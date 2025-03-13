"""
CRUD operations for database entities.
"""
import aiosqlite
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.learning import EvaluationCreate, ProgressUpdate, ResourceCreate
from app.utils.security import get_password_hash

# User CRUD operations
async def create_user(db, user_data: UserCreate) -> Dict[str, Any]:
    """Create a new user."""
    hashed_password = get_password_hash(user_data.password)
    
    async with db:
        cursor = await db.execute(
            """
            INSERT INTO usuarios (username, email, password_hash, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (user_data.username, user_data.email, hashed_password, True)
        )
        await db.commit()
        
        user_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
        
    return dict(user)

async def get_user(db, user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    async with db:
        cursor = await db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
    
    return dict(user) if user else None

async def get_user_by_username(db, username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username."""
    async with db:
        cursor = await db.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = await cursor.fetchone()
    
    return dict(user) if user else None

async def get_user_by_email(db, email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email."""
    async with db:
        cursor = await db.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        user = await cursor.fetchone()
    
    return dict(user) if user else None

async def update_user(db, user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
    """Update a user's information."""
    async with db:
        # Check if user exists
        cursor = await db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        existing_user = await cursor.fetchone()
        
        if not existing_user:
            return None
        
        # Build update query
        update_data = {}
        if user_data.username is not None:
            update_data["username"] = user_data.username
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.password is not None:
            update_data["password_hash"] = get_password_hash(user_data.password)
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        
        if update_data:
            # Update user
            update_data["updated_at"] = datetime.now().isoformat()
            set_statements = ", ".join(f"{key} = ?" for key in update_data.keys())
            values = list(update_data.values())
            
            await db.execute(
                f"UPDATE usuarios SET {set_statements} WHERE id = ?",
                (*values, user_id)
            )
            await db.commit()
        
        # Get updated user
        cursor = await db.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        updated_user = await cursor.fetchone()
    
    return dict(updated_user) if updated_user else None

# Profile CRUD operations
async def create_profile(db, profile_data: ProfileCreate) -> Dict[str, Any]:
    """Create a user profile."""
    async with db:
        cursor = await db.execute(
            """
            INSERT INTO perfiles (usuario_id, nombre, apellido, fecha_nacimiento, estilo_aprendizaje, nivel_educativo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile_data.usuario_id, 
                profile_data.nombre, 
                profile_data.apellido, 
                profile_data.fecha_nacimiento, 
                profile_data.estilo_aprendizaje, 
                profile_data.nivel_educativo
            )
        )
        await db.commit()
        
        profile_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM perfiles WHERE id = ?", (profile_id,))
        profile = await cursor.fetchone()
    
    return dict(profile)

async def get_profile(db, profile_id: int) -> Optional[Dict[str, Any]]:
    """Get a profile by ID."""
    async with db:
        cursor = await db.execute("SELECT * FROM perfiles WHERE id = ?", (profile_id,))
        profile = await cursor.fetchone()
    
    return dict(profile) if profile else None

async def get_profile_by_user_id(db, user_id: int) -> Optional[Dict[str, Any]]:
    """Get a profile by user ID."""
    async with db:
        cursor = await db.execute("SELECT * FROM perfiles WHERE usuario_id = ?", (user_id,))
        profile = await cursor.fetchone()
    
    return dict(profile) if profile else None

async def update_profile(db, user_id: int, profile_data: ProfileUpdate) -> Optional[Dict[str, Any]]:
    """Update a user's profile."""
    async with db:
        # Check if profile exists
        cursor = await db.execute("SELECT * FROM perfiles WHERE usuario_id = ?", (user_id,))
        existing_profile = await cursor.fetchone()
        
        if not existing_profile:
            return None
        
        # Build update query
        update_data = {}
        if profile_data.nombre is not None:
            update_data["nombre"] = profile_data.nombre
        if profile_data.apellido is not None:
            update_data["apellido"] = profile_data.apellido
        if profile_data.fecha_nacimiento is not None:
            update_data["fecha_nacimiento"] = profile_data.fecha_nacimiento
        if profile_data.estilo_aprendizaje is not None:
            update_data["estilo_aprendizaje"] = profile_data.estilo_aprendizaje
        if profile_data.nivel_educativo is not None:
            update_data["nivel_educativo"] = profile_data.nivel_educativo
        
        if update_data:
            # Update profile
            update_data["updated_at"] = datetime.now().isoformat()
            set_statements = ", ".join(f"{key} = ?" for key in update_data.keys())
            values = list(update_data.values())
            
            await db.execute(
                f"UPDATE perfiles SET {set_statements} WHERE usuario_id = ?",
                (*values, user_id)
            )
            await db.commit()
        
        # Get updated profile
        cursor = await db.execute("SELECT * FROM perfiles WHERE usuario_id = ?", (user_id,))
        updated_profile = await cursor.fetchone()
    
    return dict(updated_profile) if updated_profile else None

# Evaluation CRUD operations
async def create_evaluation(db, evaluation_data: EvaluationCreate) -> Dict[str, Any]:
    """Create a new evaluation record."""
    async with db:
        cursor = await db.execute(
            """
            INSERT INTO evaluaciones (usuario_id, materia_id, nivel, puntaje)
            VALUES (?, ?, ?, ?)
            """,
            (
                evaluation_data.usuario_id,
                evaluation_data.materia_id,
                evaluation_data.nivel,
                evaluation_data.puntaje
            )
        )
        await db.commit()
        
        eval_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM evaluaciones WHERE id = ?", (eval_id,))
        evaluation = await cursor.fetchone()
    
    return dict(evaluation)

async def get_user_evaluations(db, user_id: int, materia_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get evaluations for a user, optionally filtered by subject."""
    query = "SELECT * FROM evaluaciones WHERE usuario_id = ?"
    params = [user_id]
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    query += " ORDER BY fecha DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        evaluations = await cursor.fetchall()
    
    return [dict(eval) for eval in evaluations]

# Progress CRUD operations
async def update_progress(db, progress_data: ProgressUpdate) -> Dict[str, Any]:
    """Create or update a progress record."""
    async with db:
        # Check if progress record exists
        cursor = await db.execute(
            """
            SELECT * FROM progreso 
            WHERE usuario_id = ? AND materia_id = ? AND tema = ? 
            AND (subtema = ? OR (subtema IS NULL AND ? IS NULL))
            """,
            (
                progress_data.usuario_id,
                progress_data.materia_id,
                progress_data.tema,
                progress_data.subtema,
                progress_data.subtema
            )
        )
        existing_progress = await cursor.fetchone()
        
        if existing_progress:
            # Update existing record
            await db.execute(
                """
                UPDATE progreso 
                SET estado = ?, porcentaje_completado = ?, ultima_actividad = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    progress_data.estado,
                    progress_data.porcentaje_completado,
                    dict(existing_progress)["id"]
                )
            )
            await db.commit()
            
            cursor = await db.execute("SELECT * FROM progreso WHERE id = ?", (dict(existing_progress)["id"],))
            updated_progress = await cursor.fetchone()
            return dict(updated_progress)
        else:
            # Create new record
            cursor = await db.execute(
                """
                INSERT INTO progreso (usuario_id, materia_id, tema, subtema, estado, porcentaje_completado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    progress_data.usuario_id,
                    progress_data.materia_id,
                    progress_data.tema,
                    progress_data.subtema,
                    progress_data.estado,
                    progress_data.porcentaje_completado
                )
            )
            await db.commit()
            
            progress_id = cursor.lastrowid
            cursor = await db.execute("SELECT * FROM progreso WHERE id = ?", (progress_id,))
            new_progress = await cursor.fetchone()
            return dict(new_progress)

async def get_user_progress(db, user_id: int, materia_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get progress records for a user, optionally filtered by subject."""
    query = "SELECT * FROM progreso WHERE usuario_id = ?"
    params = [user_id]
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    query += " ORDER BY ultima_actividad DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        progress_items = await cursor.fetchall()
    
    return [dict(item) for item in progress_items]

# Resource CRUD operations
async def create_resource(db, resource_data: ResourceCreate) -> Dict[str, Any]:
    """Create a new educational resource."""
    async with db:
        cursor = await db.execute(
            """
            INSERT INTO recursos (titulo, tipo, url, contenido, materia_id, nivel)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resource_data.titulo,
                resource_data.tipo,
                resource_data.url,
                resource_data.contenido,
                resource_data.materia_id,
                resource_data.nivel
            )
        )
        await db.commit()
        
        resource_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM recursos WHERE id = ?", (resource_id,))
        resource = await cursor.fetchone()
    
    return dict(resource)

async def get_resources(db, materia_id: Optional[int] = None, nivel: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get resources, optionally filtered by subject and level."""
    query = "SELECT * FROM recursos WHERE 1=1"
    params = []
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    if nivel is not None:
        query += " AND nivel <= ?"
        params.append(nivel)
    
    query += " ORDER BY created_at DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        resources = await cursor.fetchall()
    
    return [dict(resource) for resource in resources]

# Interactions CRUD operations
async def log_interaction(db, user_id: int, agent: str, interaction_type: str, content: str) -> Dict[str, Any]:
    """Log an interaction with an agent."""
    async with db:
        cursor = await db.execute(
            """
            INSERT INTO interacciones (usuario_id, agente, tipo_interaccion, contenido)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, agent, interaction_type, content)
        )
        await db.commit()
        
        interaction_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM interacciones WHERE id = ?", (interaction_id,))
        interaction = await cursor.fetchone()
    
    return dict(interaction)

async def get_user_interactions(db, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent interactions for a user."""
    async with db:
        cursor = await db.execute(
            """
            SELECT * FROM interacciones 
            WHERE usuario_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (user_id, limit)
        )
        interactions = await cursor.fetchall()
    
    return [dict(interaction) for interaction in interactions]