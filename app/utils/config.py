import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Settings(BaseSettings):
    # Información de la aplicación
    APP_NAME: str = "Plataforma de Aprendizaje Personalizado"
    APP_VERSION: str = "1.0.0"
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # API de Claude
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Configuración de logs
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Sistema de colas
    QUEUE_SYSTEM: str = os.getenv("QUEUE_SYSTEM", "memory")  # memory, redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()