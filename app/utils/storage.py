"""
Storage utilities for file management and upload handling.
"""
import os
import shutil
import uuid
from typing import Optional, BinaryIO, Dict, Any, List, Tuple
from pathlib import Path
import json
import aiofiles
from fastapi import UploadFile, HTTPException
import mimetypes
from datetime import datetime

from app.utils.logger import setup_logger
from app.utils.config import settings

# Configurar logger
logger = setup_logger("storage")

# Directorio base para almacenamiento
STORAGE_DIR = os.path.join(os.getcwd(), 'storage')

# Asegurar que existen los directorios necesarios
def ensure_storage_directories():
    """Crea los directorios de almacenamiento si no existen"""
    os.makedirs(STORAGE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, 'resources'), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, 'user_files'), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, 'temp'), exist_ok=True)

# Inicialización
ensure_storage_directories()

def secure_filename(filename: str) -> str:
    """
    Normaliza y asegura un nombre de archivo.
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        Nombre de archivo seguro
    """
    # Eliminar caracteres no seguros
    keepcharacters = (' ', '.', '_', '-')
    return ''.join(c for c in filename if c.isalnum() or c in keepcharacters).strip()

def get_content_type(file_path: str) -> str:
    """
    Intenta determinar el tipo de contenido de un archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Tipo de contenido MIME
    """
    # Inicializar tipos MIME si es necesario
    if not mimetypes.inited:
        mimetypes.init()
    
    # Obtener tipo MIME por extensión
    content_type, _ = mimetypes.guess_type(file_path)
    
    if not content_type:
        # Si no se puede determinar, usar un tipo genérico
        content_type = 'application/octet-stream'
    
    return content_type

async def save_file(
    file: UploadFile,
    folder: str = 'resources',
    filename: Optional[str] = None,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Guarda un archivo subido en el almacenamiento local.
    
    Args:
        file: Archivo subido
        folder: Carpeta dentro del almacenamiento (resources, user_files, temp)
        filename: Nombre para guardar el archivo (opcional, genera uno aleatorio si no se proporciona)
        user_id: ID del usuario propietario (opcional)
        metadata: Metadatos adicionales (opcional)
        
    Returns:
        Información del archivo guardado (ruta, tamaño, etc.)
    """
    # Validar carpeta
    if folder not in ['resources', 'user_files', 'temp']:
        folder = 'resources'
    
    # Crear rutas
    storage_path = os.path.join(STORAGE_DIR, folder)
    os.makedirs(storage_path, exist_ok=True)
    
    if user_id:
        # Si se proporciona user_id, crear subdirectorio para ese usuario
        storage_path = os.path.join(storage_path, str(user_id))
        os.makedirs(storage_path, exist_ok=True)
    
    # Generar nombre de archivo único si no se proporciona
    if not filename:
        ext = os.path.splitext(file.filename)[1] if file.filename else ''
        filename = f"{uuid.uuid4().hex}{ext}"
    
    # Asegurar que el nombre de archivo sea seguro
    filename = secure_filename(filename)
    
    # Ruta completa para el archivo
    file_path = os.path.join(storage_path, filename)
    
    try:
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as out_file:
            # Leer y escribir en trozos para manejar archivos grandes
            while content := await file.read(1024 * 1024):  # 1MB chunks
                await out_file.write(content)
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(file_path)
        
        # Guardar metadatos si se proporcionan
        metadata_path = None
        if metadata:
            metadata_path = f"{file_path}.meta.json"
            async with aiofiles.open(metadata_path, 'w') as meta_file:
                meta_data = {
                    "original_filename": file.filename,
                    "size": file_size,
                    "content_type": file.content_type,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    **metadata
                }
                await meta_file.write(json.dumps(meta_data))
        
        logger.info(f"Archivo guardado: {file_path} ({file_size} bytes)")
        
        return {
            "filename": filename,
            "original_filename": file.filename,
            "path": file_path,
            "relative_path": os.path.join(folder, filename) if not user_id else os.path.join(folder, str(user_id), filename),
            "size": file_size,
            "content_type": file.content_type,
            "metadata_path": metadata_path
        }
        
    except Exception as e:
        logger.error(f"Error al guardar archivo {filename}: {str(e)}")
        # Limpiar archivo parcial si existe
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error al guardar archivo: {str(e)}")

async def get_file(
    filename: str,
    folder: str = 'resources',
    user_id: Optional[int] = None
) -> Tuple[str, bytes]:
    """
    Recupera un archivo del almacenamiento.
    
    Args:
        filename: Nombre del archivo
        folder: Carpeta dentro del almacenamiento
        user_id: ID del usuario propietario (opcional)
        
    Returns:
        Tupla con el tipo de contenido y los datos del archivo
        
    Raises:
        HTTPException: Si el archivo no existe
    """
    # Validar carpeta
    if folder not in ['resources', 'user_files', 'temp']:
        folder = 'resources'
    
    # Crear ruta
    storage_path = os.path.join(STORAGE_DIR, folder)
    
    if user_id:
        storage_path = os.path.join(storage_path, str(user_id))
    
    # Asegurar que el nombre de archivo es seguro
    filename = secure_filename(filename)
    
    # Ruta completa para el archivo
    file_path = os.path.join(storage_path, filename)
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Intentar determinar el tipo de contenido
        content_type = get_content_type(file_path)
        
        # Leer archivo
        async with aiofiles.open(file_path, 'rb') as file:
            content = await file.read()
            
        return content_type, content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al leer archivo {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al leer archivo: {str(e)}")

async def delete_file(
    filename: str,
    folder: str = 'resources',
    user_id: Optional[int] = None
) -> bool:
    """
    Elimina un archivo del almacenamiento.
    
    Args:
        filename: Nombre del archivo
        folder: Carpeta dentro del almacenamiento
        user_id: ID del usuario propietario (opcional)
        
    Returns:
        True si el archivo fue eliminado, False si no existía
    """
    # Validar carpeta
    if folder not in ['resources', 'user_files', 'temp']:
        folder = 'resources'
    
    # Crear ruta
    storage_path = os.path.join(STORAGE_DIR, folder)
    
    if user_id:
        storage_path = os.path.join(storage_path, str(user_id))
    
    # Asegurar que el nombre de archivo es seguro
    filename = secure_filename(filename)
    
    # Ruta completa para el archivo
    file_path = os.path.join(storage_path, filename)
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            return False
        
        # Eliminar archivo
        os.remove(file_path)
        
        # Eliminar metadatos si existen
        meta_path = f"{file_path}.meta.json"
        if os.path.exists(meta_path):
            os.remove(meta_path)
        
        logger.info(f"Archivo eliminado: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al eliminar archivo {filename}: {str(e)}")
        return False

async def get_file_metadata(
    filename: str,
    folder: str = 'resources',
    user_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Obtiene los metadatos de un archivo.
    
    Args:
        filename: Nombre del archivo
        folder: Carpeta dentro del almacenamiento
        user_id: ID del usuario propietario (opcional)
        
    Returns:
        Metadatos del archivo o None si no existen
    """
    # Validar carpeta
    if folder not in ['resources', 'user_files', 'temp']:
        folder = 'resources'
    
    # Crear ruta
    storage_path = os.path.join(STORAGE_DIR, folder)
    
    if user_id:
        storage_path = os.path.join(storage_path, str(user_id))
    
    # Asegurar que el nombre de archivo es seguro
    filename = secure_filename(filename)
    
    # Ruta completa para el archivo de metadatos
    meta_path = os.path.join(storage_path, f"{filename}.meta.json")
    
    try:
        # Verificar que el archivo de metadatos existe
        if not os.path.exists(meta_path):
            return None
        
        # Leer metadatos
        async with aiofiles.open(meta_path, 'r') as meta_file:
            metadata = json.loads(await meta_file.read())
            
        return metadata
        
    except Exception as e:
        logger.error(f"Error al leer metadatos de {filename}: {str(e)}")
        return None

async def list_files(
    folder: str = 'resources',
    user_id: Optional[int] = None,
    with_metadata: bool = False
) -> List[Dict[str, Any]]:
    """
    Lista archivos en una carpeta.
    
    Args:
        folder: Carpeta dentro del almacenamiento
        user_id: ID del usuario propietario (opcional)
        with_metadata: Si se deben incluir metadatos
        
    Returns:
        Lista de información de archivos
    """
    # Validar carpeta
    if folder not in ['resources', 'user_files', 'temp']:
        folder = 'resources'
    
    # Crear ruta
    storage_path = os.path.join(STORAGE_DIR, folder)
    
    if user_id:
        storage_path = os.path.join(storage_path, str(user_id))
    
    # Verificar que la carpeta existe
    if not os.path.exists(storage_path):
        return []
    
    files_info = []
    
    # Listar archivos
    for entry in os.scandir(storage_path):
        if entry.is_file() and not entry.name.endswith('.meta.json'):
            file_info = {
                "filename": entry.name,
                "path": entry.path,
                "relative_path": os.path.join(folder, entry.name) if not user_id else os.path.join(folder, str(user_id), entry.name),
                "size": entry.stat().st_size,
                "created_at": datetime.fromtimestamp(entry.stat().st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(entry.stat().st_mtime).isoformat(),
                "content_type": get_content_type(entry.path)
            }
            
            # Añadir metadatos si se solicitan
            if with_metadata:
                meta_path = f"{entry.path}.meta.json"
                if os.path.exists(meta_path):
                    try:
                        async with aiofiles.open(meta_path, 'r') as meta_file:
                            metadata = json.loads(await meta_file.read())
                            file_info["metadata"] = metadata
                    except Exception as e:
                        logger.error(f"Error al leer metadatos de {entry.name}: {str(e)}")
            
            files_info.append(file_info)
    
    return files_info

async def clean_temp_files(max_age_hours: int = 24) -> int:
    """
    Limpia archivos temporales antiguos.
    
    Args:
        max_age_hours: Edad máxima de los archivos en horas
        
    Returns:
        Número de archivos eliminados
    """
    import time
    
    temp_dir = os.path.join(STORAGE_DIR, 'temp')
    if not os.path.exists(temp_dir):
        return 0
    
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    for entry in os.scandir(temp_dir):
        if entry.is_file():
            mtime = entry.stat().st_mtime
            if now - mtime > max_age_seconds:
                try:
                    os.remove(entry.path)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error al eliminar archivo temporal {entry.name}: {str(e)}")
    
    logger.info(f"Limpieza de archivos temporales completada: {deleted_count} eliminados")
    return deleted_count