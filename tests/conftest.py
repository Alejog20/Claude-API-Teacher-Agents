"""
Archivo de configuración para pytest.
Definición de fixtures y configuración para todos los tests de la carpeta utils.
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile

# Añadir la raíz del proyecto al path de Python
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importaciones necesarias para fixtures
try:
    from app.utils.config import settings
except ImportError:
    print("ADVERTENCIA: No se pudo importar settings. Asegúrate de que app.utils.config esté accesible.")

# Fixture para pruebas de almacenamiento
@pytest.fixture
def temp_storage_dir():
    """Crea un directorio temporal para almacenamiento durante las pruebas."""
    temp_dir = tempfile.mkdtemp()
    with patch('app.utils.storage.STORAGE_DIR', temp_dir):
        yield temp_dir
    # Limpiar después de la prueba
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_upload_file():
    """Crea un mock de UploadFile para pruebas."""
    file = MagicMock(spec=UploadFile)
    file.filename = "test_file.txt"
    file.content_type = "text/plain"
    file.read = AsyncMock(return_value=b"Test content")
    return file

# Configuración para pruebas asíncronas
def pytest_configure(config):
    """Configuración adicional para pytest."""
    try:
        # Verificar que el plugin asyncio está disponible
        import pytest_asyncio
    except ImportError:
        print("ADVERTENCIA: pytest-asyncio no está instalado. Las pruebas asíncronas pueden fallar.")
        print("Instala con: pip install pytest-asyncio")

# Configuración para pruebas que usan settings
@pytest.fixture
def mock_settings():
    """Proporciona un mock de configuración para pruebas."""
    return MagicMock()

# Fixture para entorno configurado con variables de entorno específicas
@pytest.fixture
def env_setup():
    """Configura variables de entorno para pruebas y las restaura después."""
    original_environ = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original_environ)

# Fixture para probar funciones de logging
@pytest.fixture
def temp_log_dir():
    """Crea un directorio temporal para logs durante las pruebas."""
    temp_dir = tempfile.mkdtemp()
    log_dir = os.path.join(temp_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    with patch('app.utils.logger.os.makedirs') as mock_makedirs:
        yield log_dir, mock_makedirs
    
    # Limpiar después de la prueba
    shutil.rmtree(temp_dir)

# Marcador personalizado para pruebas de seguridad
def pytest_configure(config):
    """Añade marcadores personalizados."""
    config.addinivalue_line(
        "markers", "security: marca pruebas relacionadas con la seguridad"
    )
    config.addinivalue_line(
        "markers", "config: marca pruebas relacionadas con la configuración"
    )
    config.addinivalue_line(
        "markers", "logging: marca pruebas relacionadas con el logging"
    )
    config.addinivalue_line(
        "markers", "storage: marca pruebas relacionadas con el almacenamiento"
    )

# Fixture para probar JWT
@pytest.fixture
def test_jwt_data():
    """Proporciona datos de prueba para JWT."""
    return {
        "user_id": 1,
        "username": "testuser",
        "role": "user"
    }

@pytest.fixture
def test_secret_key():
    """Proporciona una clave secreta de prueba para JWT."""
    return "test_secret_key_for_jwt_operations"