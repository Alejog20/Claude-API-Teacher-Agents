"""
Tests para el módulo de almacenamiento.
"""
import os
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException

from app.utils.storage import (
    ensure_storage_directories,
    secure_filename,
    get_content_type,
    save_file,
    get_file,
    delete_file,
    get_file_metadata,
    list_files,
    clean_temp_files,
    STORAGE_DIR
)

# Fixtures
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

# Tests
def test_ensure_storage_directories(temp_storage_dir):
    """Prueba que se crean los directorios de almacenamiento correctamente."""
    # Llama a la función
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        ensure_storage_directories()
    
    # Verifica que se crearon los directorios
    assert os.path.exists(os.path.join(temp_storage_dir, 'resources'))
    assert os.path.exists(os.path.join(temp_storage_dir, 'user_files'))
    assert os.path.exists(os.path.join(temp_storage_dir, 'temp'))

def test_secure_filename():
    """Prueba que los nombres de archivo se aseguran correctamente."""
    # Caso normal
    assert secure_filename("test_file.txt") == "test_file.txt"
    
    # Elimina caracteres no seguros
    assert secure_filename("test/file<>:|\".txt") == "testfile.txt"
    
    # Conserva espacios, puntos, guiones bajos y guiones
    assert secure_filename("test file_name-123.txt") == "test file_name-123.txt"
    
    # Elimina espacios al inicio y final
    assert secure_filename(" test.txt ") == "test.txt"

def test_get_content_type():
    """Prueba que se detecta correctamente el tipo de contenido."""
    # Tipos MIME comunes
    assert get_content_type("test.txt") == "text/plain"
    assert get_content_type("image.png") == "image/png"
    assert get_content_type("document.pdf") == "application/pdf"
    
    # Tipo desconocido
    assert get_content_type("unknown_extension") == "application/octet-stream"

@pytest.mark.asyncio
async def test_save_file(temp_storage_dir, mock_upload_file):
    """Prueba que se guardan correctamente los archivos."""
    # Guardar archivo
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        result = await save_file(
            file=mock_upload_file,
            folder='resources',
            filename='saved_file.txt'
        )
    
    # Verificar resultado
    assert result["filename"] == "saved_file.txt"
    assert result["original_filename"] == "test_file.txt"
    assert os.path.join('resources', 'saved_file.txt') in result["relative_path"]
    assert os.path.exists(os.path.join(temp_storage_dir, 'resources', 'saved_file.txt'))

@pytest.mark.asyncio
async def test_save_file_with_metadata(temp_storage_dir, mock_upload_file):
    """Prueba que se guardan correctamente los archivos con metadatos."""
    # Guardar archivo con metadatos
    metadata = {"description": "Test file", "tags": ["test", "example"]}
    
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        result = await save_file(
            file=mock_upload_file,
            folder='resources',
            filename='metadata_file.txt',
            metadata=metadata
        )
    
    # Verificar que se creó el archivo de metadatos
    assert result["metadata_path"] is not None
    assert os.path.exists(result["metadata_path"])
    
    # Verificar contenido de metadatos
    with open(result["metadata_path"], 'r') as f:
        saved_metadata = json.load(f)
    
    assert saved_metadata["description"] == "Test file"
    assert saved_metadata["tags"] == ["test", "example"]
    assert saved_metadata["original_filename"] == "test_file.txt"

@pytest.mark.asyncio
async def test_get_file(temp_storage_dir, mock_upload_file):
    """Prueba que se pueden recuperar archivos guardados."""
    # Primero guardar un archivo
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        await save_file(
            file=mock_upload_file,
            folder='resources',
            filename='get_test.txt'
        )
        
        # Luego recuperarlo
        content_type, content = await get_file(
            filename='get_test.txt',
            folder='resources'
        )
    
    # Verificar el contenido
    assert content_type == "text/plain"
    assert content == b"Test content"

@pytest.mark.asyncio
async def test_get_file_not_found(temp_storage_dir):
    """Prueba que se maneja correctamente el error de archivo no encontrado."""
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        with pytest.raises(HTTPException) as excinfo:
            await get_file(filename='nonexistent.txt')
        
        assert excinfo.value.status_code == 404
        assert "no encontrado" in excinfo.value.detail.lower()

@pytest.mark.asyncio
async def test_delete_file(temp_storage_dir, mock_upload_file):
    """Prueba que se pueden eliminar archivos."""
    # Primero guardar un archivo
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        result = await save_file(
            file=mock_upload_file,
            folder='resources',
            filename='delete_test.txt'
        )
        
        file_path = result["path"]
        assert os.path.exists(file_path)
        
        # Eliminar el archivo
        success = await delete_file(
            filename='delete_test.txt',
            folder='resources'
        )
        
        # Verificar que se eliminó
        assert success is True
        assert not os.path.exists(file_path)

@pytest.mark.asyncio
async def test_delete_nonexistent_file(temp_storage_dir):
    """Prueba que eliminar un archivo inexistente retorna False."""
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        success = await delete_file(filename='nonexistent.txt')
        assert success is False

@pytest.mark.asyncio
async def test_get_file_metadata(temp_storage_dir, mock_upload_file):
    """Prueba que se pueden recuperar los metadatos de un archivo."""
    # Guardar archivo con metadatos
    metadata = {"description": "Metadata test"}
    
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        await save_file(
            file=mock_upload_file,
            folder='resources',
            filename='metadata_test.txt',
            metadata=metadata
        )
        
        # Recuperar metadatos
        result = await get_file_metadata(
            filename='metadata_test.txt',
            folder='resources'
        )
    
    # Verificar metadatos
    assert result is not None
    assert result["description"] == "Metadata test"
    assert result["original_filename"] == "test_file.txt"

@pytest.mark.asyncio
async def test_list_files(temp_storage_dir, mock_upload_file):
    """Prueba que se listan correctamente los archivos."""
    # Guardar varios archivos
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        await save_file(file=mock_upload_file, folder='resources', filename='file1.txt')
        await save_file(file=mock_upload_file, folder='resources', filename='file2.txt')
        
        # Listar archivos
        files = await list_files(folder='resources')
    
    # Verificar lista
    assert len(files) == 2
    filenames = [f["filename"] for f in files]
    assert "file1.txt" in filenames
    assert "file2.txt" in filenames

@pytest.mark.asyncio
async def test_clean_temp_files(temp_storage_dir, mock_upload_file):
    """Prueba que se limpian correctamente los archivos temporales."""
    import time
    
    with patch('app.utils.storage.STORAGE_DIR', temp_storage_dir):
        # Guardar un archivo en temp
        await save_file(file=mock_upload_file, folder='temp', filename='old_temp.txt')
        
        # Modificar tiempo de acceso y modificación para simular un archivo antiguo
        temp_file = os.path.join(temp_storage_dir, 'temp', 'old_temp.txt')
        old_time = time.time() - (25 * 3600)  # 25 horas en el pasado
        os.utime(temp_file, (old_time, old_time))
        
        # Guardar un archivo reciente
        await save_file(file=mock_upload_file, folder='temp', filename='new_temp.txt')
        
        # Limpiar archivos temporales más antiguos que 24 horas
        deleted = await clean_temp_files(max_age_hours=24)
        
        # Verificar que solo se eliminó el archivo antiguo
        assert deleted == 1
        assert not os.path.exists(temp_file)
        assert os.path.exists(os.path.join(temp_storage_dir, 'temp', 'new_temp.txt'))