"""
Tests para el módulo de logging.
"""
import logging
import os
import pytest
from unittest.mock import patch, MagicMock
from app.utils.logger import setup_logger
from app.utils.config import settings

def test_logger_creation():
    """Prueba que se crea un logger correctamente."""
    # Configurar el logger
    logger = setup_logger("test_logger")
    
    # Verificar que el logger existe y tiene el nivel correcto
    assert logger.name == "test_logger"
    assert logger.level == getattr(logging, settings.LOG_LEVEL.upper())
    
    # Verificar que tiene los handlers esperados
    assert len(logger.handlers) == 2  # Console y File
    
    # Verificar que uno es StreamHandler y otro es RotatingFileHandler
    handler_types = [type(h).__name__ for h in logger.handlers]
    assert "StreamHandler" in handler_types
    assert "RotatingFileHandler" in handler_types

def test_logger_directory_creation():
    """Prueba que se crea el directorio de logs si no existe."""
    # Simular que el directorio no existe
    with patch('os.makedirs') as mock_makedirs:
        logger = setup_logger("test_logger_dir")
        
        # Verificar que se llamó a makedirs
        mock_makedirs.assert_called_once_with('logs', exist_ok=True)

def test_logger_no_duplicate_handlers():
    """Prueba que no se añaden handlers duplicados al mismo logger."""
    # Crear el mismo logger dos veces
    logger1 = setup_logger("test_duplicate")
    handlers_count = len(logger1.handlers)
    
    # Crear el mismo logger de nuevo
    logger2 = setup_logger("test_duplicate")
    
    # Verificar que es el mismo objeto
    assert logger1 is logger2
    
    # Verificar que no se añadieron más handlers
    assert len(logger2.handlers) == handlers_count

def test_logger_formatting():
    """Prueba que el formato del logger es el esperado."""
    logger = setup_logger("test_format")
    
    # Verificar el formato en los handlers
    for handler in logger.handlers:
        assert handler.formatter is not None
        # El formato debe incluir timestamp, nombre, nivel y mensaje
        format_str = handler.formatter._fmt
        assert "%(asctime)s" in format_str
        assert "%(name)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(message)s" in format_str

def test_log_level_from_settings():
    """Prueba que el nivel de log se obtiene de la configuración."""
    # Cambiar temporalmente el nivel de log en settings
    original_level = settings.LOG_LEVEL
    
    with patch('app.utils.config.settings.LOG_LEVEL', "DEBUG"):
        logger = setup_logger("test_level")
        assert logger.level == logging.DEBUG
    
    with patch('app.utils.config.settings.LOG_LEVEL', "WARNING"):
        logger = setup_logger("test_level_warning")
        assert logger.level == logging.WARNING