import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from app.utils.config import settings

def setup_logger(name='app'):
    """Configurar el logger con formato personalizado y nivel según configuración"""
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Configurar el logger
    logger = logging.getLogger(name)
    
    # Establecer nivel según configuración
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    logger.setLevel(log_level)
    
    # Evitar duplicación de handlers
    if not logger.handlers:
        # Formato para los logs
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler para archivo con rotación
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger