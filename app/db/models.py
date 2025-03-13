"""
Database models and schema declarations.

Note: Since we're using SQLite with raw SQL queries instead of an ORM like SQLAlchemy,
this file primarily serves to document the database schema.
"""

# Users and Authentication
"""
usuarios
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE
- email: TEXT UNIQUE
- password_hash: TEXT
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

perfiles
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER (FOREIGN KEY -> usuarios.id)
- nombre: TEXT
- apellido: TEXT
- fecha_nacimiento: DATE
- estilo_aprendizaje: TEXT
- nivel_educativo: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
"""

# Educational Content
"""
materias
- id: INTEGER PRIMARY KEY
- nombre: TEXT
- descripcion: TEXT
- created_at: TIMESTAMP

evaluaciones
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER (FOREIGN KEY -> usuarios.id)
- materia_id: INTEGER (FOREIGN KEY -> materias.id)
- nivel: INTEGER
- puntaje: REAL
- fecha: TIMESTAMP

progreso
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER (FOREIGN KEY -> usuarios.id)
- materia_id: INTEGER (FOREIGN KEY -> materias.id)
- tema: TEXT
- subtema: TEXT
- estado: TEXT ('not_started', 'in_progress', 'completed')
- porcentaje_completado: REAL
- ultima_actividad: TIMESTAMP

recursos
- id: INTEGER PRIMARY KEY
- titulo: TEXT
- tipo: TEXT ('video', 'reading', 'interactive', 'practice', 'other')
- url: TEXT
- contenido: TEXT
- materia_id: INTEGER (FOREIGN KEY -> materias.id)
- nivel: INTEGER
- created_at: TIMESTAMP
"""

# Interactions and Analytics
"""
interacciones
- id: INTEGER PRIMARY KEY
- usuario_id: INTEGER (FOREIGN KEY -> usuarios.id)
- agente: TEXT
- tipo_interaccion: TEXT
- contenido: TEXT
- timestamp: TIMESTAMP
"""

class Tables:
    """Table names for easier reference."""
    USUARIOS = "usuarios"
    PERFILES = "perfiles"
    MATERIAS = "materias"
    EVALUACIONES = "evaluaciones"
    PROGRESO = "progreso"
    RECURSOS = "recursos"
    INTERACCIONES = "interacciones"
    MIGRATIONS = "migrations"

class Columns:
    """Column names by table for easier reference."""
    USUARIOS = ["id", "username", "email", "password_hash", "is_active", "created_at", "updated_at"]
    PERFILES = ["id", "usuario_id", "nombre", "apellido", "fecha_nacimiento", "estilo_aprendizaje", "nivel_educativo", "created_at", "updated_at"]
    MATERIAS = ["id", "nombre", "descripcion", "created_at"]
    EVALUACIONES = ["id", "usuario_id", "materia_id", "nivel", "puntaje", "fecha"]
    PROGRESO = ["id", "usuario_id", "materia_id", "tema", "subtema", "estado", "porcentaje_completado", "ultima_actividad"]
    RECURSOS = ["id", "titulo", "tipo", "url", "contenido", "materia_id", "nivel", "created_at"]
    INTERACCIONES = ["id", "usuario_id", "agente", "tipo_interaccion", "contenido", "timestamp"]