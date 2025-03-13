"""
Tests para las funciones de base de datos.
"""
import pytest
import os
import aiosqlite
import tempfile
from pathlib import Path

from app.db import database

@pytest.mark.db
class TestDatabaseFunctions:
    """Pruebas para las funciones de la base de datos."""
    
    @pytest.mark.asyncio
    async def test_init_db(self, monkeypatch):
        """Test inicialización de la base de datos."""
        # Crear un archivo temporal para la base de datos
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Monkeypatching para usar el archivo temporal
        monkeypatch.setattr(database, 'DB_PATH', db_path)
        
        try:
            # Inicializar la base de datos
            await database.init_db()
            
            # Verificar que la base de datos existe y tiene tablas
            assert os.path.exists(db_path)
            
            # Verificar que las tablas se han creado correctamente
            async with aiosqlite.connect(db_path) as db:
                # Verificar tabla usuarios
                cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
                table = await cursor.fetchone()
                assert table is not None
                
                # Verificar otras tablas importantes
                tables_to_check = ['perfiles', 'materias', 'evaluaciones', 'progreso', 'recursos', 'interacciones']
                
                for table_name in tables_to_check:
                    cursor = await db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    table = await cursor.fetchone()
                    assert table is not None, f"La tabla {table_name} no se ha creado"
                
                # Verificar estructura de una tabla
                cursor = await db.execute("PRAGMA table_info(usuarios)")
                columns = await cursor.fetchall()
                column_names = [column[1] for column in columns]
                
                expected_columns = ['id', 'username', 'email', 'password_hash', 'is_active', 'created_at', 'updated_at']
                for col in expected_columns:
                    assert col in column_names, f"La columna {col} no existe en la tabla usuarios"
        
        finally:
            # Limpieza
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_get_db(self):
        """Test obtención de conexión a la base de datos."""
        db_gen = database.get_db()
        db = await anext(db_gen)
        
        try:
            # Verificar que tenemos una conexión válida de SQLite
            assert db is not None
            
            # Comprobar que podemos ejecutar una consulta simple
            cursor = await db.execute("SELECT 1")
            result = await cursor.fetchone()
            
            assert result[0] == 1
        
        finally:
            # Cerrar la conexión
            try:
                await db.close()
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_backup_db(self, monkeypatch):
        """Test copia de seguridad de la base de datos."""
        # Crear un directorio temporal para las copias de seguridad
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Crear un archivo temporal para la base de datos
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                db_path = tmp.name
            
            # Monkeypatching para usar archivos temporales
            monkeypatch.setattr(database, 'DB_PATH', db_path)
            monkeypatch.setattr(database, 'backup_dir', tmp_dir)
            
            try:
                # Crear un archivo de prueba
                with open(db_path, 'w') as f:
                    f.write("test data")
                
                # Ejecutar la copia de seguridad
                backup_file = await database.backup_db()
                
                # Verificar que se creó el archivo de copia de seguridad
                assert os.path.exists(backup_file)
                
                # Verificar que contiene los datos correctos
                with open(backup_file, 'r') as f:
                    content = f.read()
                    assert content == "test data"
            
            finally:
                # Limpieza
                if os.path.exists(db_path):
                    os.unlink(db_path)