from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional, Dict, Any

from app.db.database import get_db
from app.api.routes.auth import get_current_user
from app.utils.config import settings
from app.utils.logger import setup_logger
from app.agents import create_agent

logger = setup_logger("dependencies")

# Reutiliza el esquema OAuth2 definido en auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Verifica que el usuario actual esté activo.
    
    Args:
        current_user: Usuario autenticado actual
    
    Returns:
        El usuario actual si está activo
        
    Raises:
        HTTPException: Si el usuario no está activo
    """
    if not current_user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user

async def get_student_profile(current_user = Depends(get_current_user), db = Depends(get_db)):
    """
    Obtiene el perfil del estudiante para el usuario actual.
    
    Args:
        current_user: Usuario autenticado actual
        db: Conexión a la base de datos
        
    Returns:
        El perfil del estudiante
        
    Raises:
        HTTPException: Si el perfil no existe
    """
    async with db:
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        profile = await cursor.fetchone()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de estudiante no encontrado"
            )
    
    return dict(profile)

async def get_subject_by_id(materia_id: int, db = Depends(get_db)):
    """
    Obtiene una materia por su ID.
    
    Args:
        materia_id: ID de la materia
        db: Conexión a la base de datos
        
    Returns:
        La materia encontrada
        
    Raises:
        HTTPException: Si la materia no existe
    """
    async with db:
        cursor = await db.execute(
            "SELECT * FROM materias WHERE id = ?", 
            (materia_id,)
        )
        subject = await cursor.fetchone()
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
    
    return dict(subject)

async def get_agent_with_context(
    agent_type: str, 
    current_user = Depends(get_current_user),
    db = Depends(get_db),
    subject_id: Optional[int] = None
):
    """
    Crea un agente con contexto del estudiante.
    
    Args:
        agent_type: Tipo de agente a crear
        current_user: Usuario autenticado actual
        db: Conexión a la base de datos
        subject_id: ID de la materia (opcional)
        
    Returns:
        Un agente inicializado con el contexto del estudiante
    """
    # Obtener el perfil para contexto
    async with db:
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        profile = await cursor.fetchone()
    
    # Preparar argumentos para el agente
    agent_args = {}
    if subject_id is not None and agent_type == "subject":
        # Si es un agente de materia, buscar la materia
        cursor = await db.execute("SELECT nombre FROM materias WHERE id = ?", (subject_id,))
        subject = await cursor.fetchone()
        if subject:
            agent_args["subject"] = dict(subject)["nombre"]
    
    # Crear el agente
    agent = create_agent(agent_type, **agent_args)
    
    # Añadir contexto del estudiante si hay perfil
    if profile:
        profile_dict = dict(profile)
        await agent.set_student_context(profile_dict)
    
    return agent

def check_permissions(required_permissions: list):
    """
    Dependencia para verificar permisos.
    Por ahora es un placeholder, pero permitirá implementar un sistema de permisos
    más avanzado en el futuro.
    
    Args:
        required_permissions: Lista de permisos requeridos
        
    Returns:
        Función de dependencia que verifica permisos
    """
    async def _check_permissions(current_user = Depends(get_current_user)):
        # Para una versión inicial, simplemente verificamos que el usuario esté autenticado
        # En futuras versiones, se puede implementar un sistema más complejo
        return current_user
        
    return _check_permissions

async def get_user_progress_context(
    materia_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Obtiene el contexto completo del progreso del estudiante para una materia.
    Útil para proporcionar contexto a los agentes.
    
    Args:
        materia_id: ID de la materia
        current_user: Usuario autenticado actual
        db: Conexión a la base de datos
        
    Returns:
        Diccionario con el contexto del progreso del estudiante
    """
    usuario_id = current_user["id"]
    
    async with db:
        # Obtener información de la materia
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Obtener perfil del estudiante
        cursor = await db.execute("SELECT * FROM perfiles WHERE usuario_id = ?", (usuario_id,))
        profile = await cursor.fetchone()
        
        # Obtener evaluaciones recientes
        cursor = await db.execute(
            """
            SELECT * FROM evaluaciones 
            WHERE usuario_id = ? AND materia_id = ? 
            ORDER BY fecha DESC LIMIT 5
            """,
            (usuario_id, materia_id)
        )
        evaluations = await cursor.fetchall()
        
        # Obtener progreso actual
        cursor = await db.execute(
            """
            SELECT * FROM progreso 
            WHERE usuario_id = ? AND materia_id = ? 
            ORDER BY ultima_actividad DESC
            """,
            (usuario_id, materia_id)
        )
        progress_items = await cursor.fetchall()
    
    # Construir el contexto
    context = {
        "usuario_id": usuario_id,
        "materia": dict(materia),
        "perfil": dict(profile) if profile else None,
        "evaluaciones": [dict(eval) for eval in evaluations],
        "progreso": [dict(item) for item in progress_items],
    }
    
    # Calcular nivel actual basado en las evaluaciones
    if evaluations:
        max_nivel = max([dict(eval)["nivel"] for eval in evaluations])
        avg_puntaje = sum([dict(eval)["puntaje"] for eval in evaluations]) / len(evaluations)
        context["nivel_actual"] = max_nivel
        context["puntaje_promedio"] = avg_puntaje
    
    # Calcular temas completados
    if progress_items:
        temas_completados = sum(1 for item in progress_items if dict(item)["estado"] == "completado")
        porcentaje_total = sum(dict(item)["porcentaje_completado"] for item in progress_items) / len(progress_items) if progress_items else 0
        context["temas_completados"] = temas_completados
        context["porcentaje_total"] = porcentaje_total
    
    return context