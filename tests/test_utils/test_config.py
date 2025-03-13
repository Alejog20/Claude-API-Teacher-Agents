"""
Tests para el módulo de configuración.
"""
import os
import pytest
from unittest.mock import patch
from app.utils.config import Settings

def test_settings_default_values():
    """Prueba que los valores por defecto de la configuración son correctos."""
    # Crear una instancia de Settings sin variables de entorno
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
    
    # Verificar valores por defecto
    assert settings.APP_NAME == "Plataforma de Aprendizaje Personalizado"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DATABASE_URL == "sqlite:///./app.db"
    assert settings.CLAUDE_API_KEY == ""
    assert settings.CLAUDE_MODEL == "claude-3-7-sonnet-20250219"
    assert settings.SECRET_KEY == "supersecretkey"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24
    assert settings.LOG_LEVEL == "INFO"
    assert settings.QUEUE_SYSTEM == "memory"
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.DEBUG is False

def test_settings_from_env_variables():
    """Prueba que las variables de entorno sobreescriben los valores por defecto."""
    # Definir variables de entorno para la prueba
    test_env = {
        "DATABASE_URL": "sqlite:///./test.db",
        "CLAUDE_API_KEY": "test-api-key",
        "CLAUDE_MODEL": "claude-test-model",
        "SECRET_KEY": "test-secret-key",
        "LOG_LEVEL": "DEBUG",
        "QUEUE_SYSTEM": "redis",
        "REDIS_URL": "redis://testhost:6379/1",
        "DEBUG": "true"
    }
    
    # Crear una instancia de Settings con las variables de entorno
    with patch.dict(os.environ, test_env):
        settings = Settings()
    
    # Verificar que las variables de entorno tienen efecto
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    assert settings.CLAUDE_API_KEY == "test-api-key"
    assert settings.CLAUDE_MODEL == "claude-test-model"
    assert settings.SECRET_KEY == "test-secret-key"
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.QUEUE_SYSTEM == "redis"
    assert settings.REDIS_URL == "redis://testhost:6379/1"
    assert settings.DEBUG is True

def test_settings_immutability():
    """Prueba que los ajustes son inmutables una vez creados."""
    settings = Settings()
    
    # Intentar modificar un valor
    with pytest.raises(Exception):
        settings.SECRET_KEY = "new-secret-key"