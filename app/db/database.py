import sqlite3
import aiosqlite
import os
from app.utils.logger import setup_logger
from app.utils.config import settings

logger = setup_logger("database")

# Extrae el nombre de archivo de la URL de la base de datos
DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "")

async def init_db():
    """Inicializa la base de datos y crea las tablas si no existen"""
    # Asegúrate de que el directorio exista
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        logger.info(f"Conectado a la base de datos: {DB_PATH}")
        
        # Habilitar claves foráneas
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Crear tablas usando los scripts SQL
        await _create_tables(db)
        
        # Optimizar configuración de SQLite
        await db.execute("PRAGMA journal_mode = WAL")  # Modo Write-Ahead Logging
        await db.execute("PRAGMA synchronous = NORMAL")  # Balance entre rendimiento y seguridad
        
        logger.info("Base de datos inicializada correctamente")

async def _create_tables(db):
    """Crea las tablas necesarias en la base de datos"""
    # Tabla de usuarios
    await db.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de perfiles de estudiantes
    await db.execute('''
    CREATE TABLE IF NOT EXISTS perfiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        fecha_nacimiento DATE,
        estilo_aprendizaje TEXT,
        nivel_educativo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    ''')
    
    # Tabla de materias
    await db.execute('''
    CREATE TABLE IF NOT EXISTS materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabla de evaluaciones
    await db.execute('''
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        nivel INTEGER NOT NULL,
        puntaje REAL NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    )
    ''')
    
    # Tabla de progreso
    await db.execute('''
    CREATE TABLE IF NOT EXISTS progreso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        materia_id INTEGER NOT NULL,
        tema TEXT NOT NULL,
        subtema TEXT,
        estado TEXT NOT NULL,
        porcentaje_completado REAL DEFAULT 0,
        ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    )
    ''')
    
    # Tabla de recursos
    await db.execute('''
    CREATE TABLE IF NOT EXISTS recursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        tipo TEXT NOT NULL,
        url TEXT,
        contenido TEXT,
        materia_id INTEGER,
        nivel INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    )
    ''')
    
    # Tabla de interacciones
    await db.execute('''
    CREATE TABLE IF NOT EXISTS interacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        agente TEXT NOT NULL,
        tipo_interaccion TEXT NOT NULL,
        contenido TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    ''')
    
    await db.commit()
    logger.info("Tablas creadas correctamente")

async def get_db():
    """Devuelve una conexión a la base de datos para usar como dependencia"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = sqlite3.Row  # Para que los resultados sean como diccionarios
    
    try:
        yield db
    finally:
        await db.close()

async def backup_db():
    """Crea una copia de seguridad de la base de datos"""
    import shutil
    from datetime import datetime
    
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/backup_{timestamp}.db"
    
    # Cerrar todas las conexiones antes de hacer la copia
    # En producción, esto podría requerir más gestión
    shutil.copy2(DB_PATH, backup_file)
    
    logger.info(f"Copia de seguridad creada: {backup_file}")
    return backup_file