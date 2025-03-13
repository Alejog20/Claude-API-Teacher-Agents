"""
Tests para el módulo de seguridad.
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.utils.security import (
    hash_password, 
    verify_password, 
    generate_token, 
    verify_token,
    generate_random_key,
    generate_strong_password,
    is_valid_password,
    sanitize_input
)

# Configuración de prueba
TEST_SECRET_KEY = "test_secret_key"
TEST_USER = {"username": "testuser", "user_id": 1}

def test_password_hashing():
    """Prueba que el hashing y verificación de contraseñas funciona correctamente."""
    # Datos de prueba
    password = "secureP@ssw0rd"
    
    # Generar hash
    hashed = hash_password(password)
    
    # Verificar que el hash no es igual a la contraseña original
    assert hashed != password
    
    # Verificar que la contraseña original es verificada correctamente
    assert verify_password(password, hashed) is True
    
    # Verificar que una contraseña incorrecta falla
    assert verify_password("wrongpassword", hashed) is False

def test_token_generation_and_verification():
    """Prueba que la generación y verificación de tokens funciona correctamente."""
    # Generar token
    token = generate_token(TEST_USER, secret_key=TEST_SECRET_KEY)
    
    # Verificar que el token no está vacío
    assert token
    
    # Verificar que el token se puede decodificar
    payload = verify_token(token, secret_key=TEST_SECRET_KEY)
    
    # Verificar que el payload contiene los datos correctos
    assert payload["username"] == TEST_USER["username"]
    assert payload["user_id"] == TEST_USER["user_id"]
    assert "exp" in payload

def test_token_expiration():
    """Prueba que los tokens expirados son rechazados."""
    # Generar token con expiración en el pasado
    expires_delta = timedelta(seconds=-1)
    token = generate_token(TEST_USER, expires_delta=expires_delta, secret_key=TEST_SECRET_KEY)
    
    # Verificar que el token es rechazado
    with pytest.raises(HTTPException) as excinfo:
        verify_token(token, secret_key=TEST_SECRET_KEY)
    
    # Verificar que el error es por token expirado
    assert excinfo.value.status_code == 401
    assert "expirado" in excinfo.value.detail.lower()

def test_token_tampering():
    """Prueba que los tokens manipulados son rechazados."""
    # Generar token
    token = generate_token(TEST_USER, secret_key=TEST_SECRET_KEY)
    
    # Manipular token (cambiar última letra)
    tampered_token = token[:-1] + ('A' if token[-1] != 'A' else 'B')
    
    # Verificar que el token es rechazado
    with pytest.raises(HTTPException) as excinfo:
        verify_token(tampered_token, secret_key=TEST_SECRET_KEY)
    
    # Verificar que el error es por token inválido
    assert excinfo.value.status_code == 401
    assert "inválido" in excinfo.value.detail.lower()

def test_random_key_generation():
    """Prueba que se generan claves aleatorias de la longitud correcta."""
    # Generar clave
    key = generate_random_key(32)
    
    # Verificar longitud (32 bytes = 64 caracteres hex)
    assert len(key) == 64
    
    # Verificar que dos claves son diferentes
    assert generate_random_key(32) != generate_random_key(32)

def test_strong_password_generation():
    """Prueba que se generan contraseñas fuertes."""
    # Generar contraseña
    password = generate_strong_password(12)
    
    # Verificar longitud
    assert len(password) == 12
    
    # Verificar que la contraseña es válida
    assert is_valid_password(password)

def test_password_validation():
    """Prueba que la validación de contraseñas funciona correctamente."""
    # Contraseñas válidas
    assert is_valid_password("SecureP@ss123")
    assert is_valid_password("Complex!234Pwd")
    
    # Contraseñas inválidas
    assert not is_valid_password("short")  # Muy corta
    assert not is_valid_password("nouppercase123!")  # Sin mayúsculas
    assert not is_valid_password("NOLOWERCASE123!")  # Sin minúsculas
    assert not is_valid_password("NoNumbers!")  # Sin números
    assert not is_valid_password("NoSpecial123")  # Sin caracteres especiales

def test_input_sanitization():
    """Prueba que la sanitización de entrada funciona correctamente."""
    # Texto con HTML
    assert sanitize_input("<script>alert('XSS')</script>") == "&lt;script&gt;alert('XSS')&lt;/script&gt;"
    
    # Texto normal
    assert sanitize_input("Normal text") == "Normal text"
    
    # Texto con caracteres de control
    control_chars = "".join(chr(i) for i in range(32) if i not in [9, 10, 13])  # Todos excepto \t, \n, \r
    sanitized = sanitize_input(f"Test{control_chars}Text")
    assert sanitized == "TestText"
