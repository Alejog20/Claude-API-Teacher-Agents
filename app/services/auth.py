"""
Authentication service.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
import re

from app.utils.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("auth")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if the password matches the hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        JWT token
    """
    to_encode = data.copy()
    
 # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode the token
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        raise

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Decoded token data
        
    Raises:
        JWTError: If the token is invalid
    """
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        raise JWTError(f"Invalid token: {str(e)}")

def validate_email_password(email: str, password: str) -> Dict[str, bool]:
    """
    Validate email and password format.
    
    Args:
        email: Email to validate
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid_email": False,
        "valid_password": False,
        "email_error": None,
        "password_error": None
    }
    
    # Validate email
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        result["email_error"] = "Invalid email format"
    else:
        result["valid_email"] = True
    
    # Validate password
    if len(password) < 8:
        result["password_error"] = "Password must be at least 8 characters long"
    elif not any(c.isupper() for c in password):
        result["password_error"] = "Password must contain at least one uppercase letter"
    elif not any(c.islower() for c in password):
        result["password_error"] = "Password must contain at least one lowercase letter"
    elif not any(c.isdigit() for c in password):
        result["password_error"] = "Password must contain at least one digit"
    else:
        result["valid_password"] = True
    
    return result

def generate_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User's email
        
    Returns:
        Reset token
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "sub": email,
        "exp": expire,
        "type": "password_reset"
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: Reset token
        
    Returns:
        User's email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None