"""
Security utilities for authentication, encryption and token handling.
"""
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, status
import re
import secrets
import string

from app.utils.logger import setup_logger
from app.utils.config import settings

# Configurar logger
logger = setup_logger("security")

# Contexto de encriptación para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Genera un hash seguro para una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash almacenado de la contraseña
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)

def generate_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None
) -> str:
    """
    Genera un token JWT con los datos proporcionados.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración (opcional)
        secret_key: Clave secreta para firmar el token (usa la de configuración por defecto)
        
    Returns:
        Token JWT generado
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Usar clave secreta de configuración si no se proporciona
    secret = secret_key or settings.SECRET_KEY
    
    try:
        # Generar token
        encoded_jwt = jwt.encode(
            to_encode, 
            secret, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error al generar token: {str(e)}")
        raise

def verify_token(
    token: str, 
    secret_key: Optional[str] = None,
    token_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        secret_key: Clave secreta para verificar el token (usa la de configuración por defecto)
        token_type: Tipo de token esperado (opcional)
        
    Returns:
        Contenido decodificado del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    # Usar clave secreta de configuración si no se proporciona
    secret = secret_key or settings.SECRET_KEY
    
    try:
        # Decodificar token
        payload = jwt.decode(
            token, 
            secret, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar tipo de token si se especifica
        if token_type and payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Tipo de token incorrecto. Se esperaba {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        logger.warning("Token inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error al verificar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

def generate_random_key(length: int = 32) -> str:
    """
    Genera una clave secreta aleatoria.
    
    Args:
        length: Longitud de la clave en bytes
        
    Returns:
        Clave codificada en hexadecimal
    """
    return secrets.token_hex(length)

def generate_strong_password(length: int = 12) -> str:
    """
    Genera una contraseña fuerte aleatoria.
    
    Args:
        length: Longitud de la contraseña
        
    Returns:
        Contraseña aleatoria
    """
    # Definir los caracteres a utilizar
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    numbers = string.digits
    symbols = string.punctuation
    
    # Asegurar que haya al menos uno de cada tipo
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(numbers),
        secrets.choice(symbols)
    ]
    
    # Completar con caracteres aleatorios
    for _ in range(length - 4):
        password.append(secrets.choice(lowercase + uppercase + numbers + symbols))
    
    # Mezclar la contraseña
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def is_valid_password(password: str) -> bool:
    """
    Verifica si una contraseña cumple con los requisitos mínimos de seguridad.
    
    Args:
        password: Contraseña a verificar
        
    Returns:
        True si la contraseña es válida, False en caso contrario
    """
    # Verificar longitud mínima
    if len(password) < 8:
        return False
    
    # Verificar que contenga al menos una letra minúscula
    if not re.search(r'[a-z]', password):
        return False
    
    # Verificar que contenga al menos una letra mayúscula
    if not re.search(r'[A-Z]', password):
        return False
    
    # Verificar que contenga al menos un número
    if not re.search(r'\d', password):
        return False
    
    # Verificar que contenga al menos un carácter especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def is_valid_token_format(token: str) -> bool:
    """
    Verifica si un token tiene el formato JWT válido (sin verificar la firma).
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        True si el token tiene formato válido, False en caso contrario
    """
    if not isinstance(token, str):
        return False
        
    # Un token JWT válido tiene 3 partes separadas por puntos
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    try:
        # Intentar decodificar la cabecera (header) y payload
        # Sin verificar la firma
        jwt.get_unverified_header(token)
        jwt.decode(token, options={"verify_signature": False})
        return True
    except (jwt.PyJWTError, ValueError, TypeError):
        return False

def sanitize_input(input_str: str) -> str:
    """
    Sanitiza entrada para prevenir inyección de código.
    
    Args:
        input_str: Cadena a sanitizar
        
    Returns:
        Cadena sanitizada
    """
    # Reemplazar caracteres potencialmente peligrosos
    sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
    
    # Eliminar caracteres de control
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\n\r\t')
    
    return sanitized