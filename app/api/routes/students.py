from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.api.routes.auth import get_current_user
from app.db.database import get_db
from app.utils.logger import setup_logger

router = APIRouter(prefix="/students", tags=["Estudiantes"])
logger = setup_logger("students")

@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    """Crea un perfil de estudiante para el usuario actual"""
    
    # Verificar si ya existe un perfil para este usuario
    async with db:
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        existing_profile = await cursor.fetchone()
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya tiene un perfil"
            )
        
        # Crear nuevo perfil
        cursor = await db.execute(
            """
            INSERT INTO perfiles (usuario_id, nombre, apellido, fecha_nacimiento, estilo_aprendizaje, nivel_educativo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                current_user["id"],
                profile.nombre,
                profile.apellido,
                profile.fecha_nacimiento,
                profile.estilo_aprendizaje,
                profile.nivel_educativo
            )
        )
        await db.commit()
        
        # Obtener el perfil recién creado
        profile_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM perfiles WHERE id = ?", (profile_id,))
        created_profile = await cursor.fetchone()
    
    # Convertir Row a diccionario
    profile_dict = dict(created_profile)
    return ProfileResponse(**profile_dict)

@router.get("/profiles/me", response_model=ProfileResponse)
async def get_my_profile(current_user = Depends(get_current_user), db = Depends(get_db)):
    """Obtiene el perfil del estudiante actual"""
    
    async with db:
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        profile = await cursor.fetchone()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )
    
    # Convertir Row a diccionario
    profile_dict = dict(profile)
    return ProfileResponse(**profile_dict)

@router.put("/profiles/me", response_model=ProfileResponse)
async def update_my_profile(profile_update: ProfileUpdate, current_user = Depends(get_current_user), db = Depends(get_db)):
    """Actualiza el perfil del estudiante actual"""
    
    async with db:
        # Verificar si existe el perfil
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        existing_profile = await cursor.fetchone()
        
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )
        
        # Preparar los campos a actualizar
        updates = {}
        if profile_update.nombre is not None:
            updates["nombre"] = profile_update.nombre
        if profile_update.apellido is not None:
            updates["apellido"] = profile_update.apellido
        if profile_update.fecha_nacimiento is not None:
            updates["fecha_nacimiento"] = profile_update.fecha_nacimiento
        if profile_update.estilo_aprendizaje is not None:
            updates["estilo_aprendizaje"] = profile_update.estilo_aprendizaje
        if profile_update.nivel_educativo is not None:
            updates["nivel_educativo"] = profile_update.nivel_educativo
        
        # Actualizar solo si hay campos para actualizar
        if updates:
            set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
            query = f"UPDATE perfiles SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE usuario_id = ?"
            params = list(updates.values()) + [current_user["id"]]
            
            await db.execute(query, params)
            await db.commit()
        
        # Obtener el perfil actualizado
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        updated_profile = await cursor.fetchone()
    
    # Convertir Row a diccionario
    profile_dict = dict(updated_profile)
    return ProfileResponse(**profile_dict)