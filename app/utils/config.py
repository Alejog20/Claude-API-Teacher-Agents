# Crea el archivo app/utils/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///./teachassistant.db"
    
    # Configuración de la API de Claude
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"
    
    # Configuración del logging
    LOG_LEVEL: str = "INFO"
    
    # Otras configuraciones
    APP_NAME: str = "TeachAssistant"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
