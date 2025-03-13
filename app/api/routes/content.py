from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Optional
from app.schemas.learning import ResourceCreate, ResourceResponse, MateriaResponse
from app.api.routes.auth import get_current_user
from app.db.database import get_db
from app.services.queue import queue
from app.utils.logger import setup_logger

router = APIRouter(prefix="/content", tags=["Contenido"])
logger = setup_logger("content")

@router.get("/subjects", response_model=List[MateriaResponse])
async def get_subjects(current_user = Depends(get_current_user), db = Depends(get_db)):
    """Obtiene la lista de materias disponibles"""
    
    async with db:
        cursor = await db.execute("SELECT * FROM materias ORDER BY nombre")
        subjects = await cursor.fetchall()
    
    # Convertir lista de Row a lista de diccionarios
    return [MateriaResponse(**dict(subject)) for subject in subjects]

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_content(
    materia_id: int, 
    tema: str, 
    nivel: int, 
    subtema: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user), 
    db = Depends(get_db)
):
    """Genera contenido educativo personalizado para un tema específico"""
    
    # Verificar que la materia existe
    async with db:
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Obtener información del perfil del estudiante para personalización
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        profile = await cursor.fetchone()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe completar su perfil antes de generar contenido"
            )
    
    # Crear contexto para la generación de contenido
    context = {
        "usuario_id": current_user["id"],
        "materia": dict(materia)["nombre"],
        "materia_id": materia_id,
        "tema": tema,
        "subtema": subtema,
        "nivel": nivel,
        "estilo_aprendizaje": dict(profile)["estilo_aprendizaje"],
        "nivel_educativo": dict(profile)["nivel_educativo"]
    }
    
    # Encolar la tarea de generación de contenido
    task_id = await queue.enqueue("generacion_contenido", context)
    
    # Registrar la solicitud en la base de datos
    background_tasks.add_task(
        register_content_request, 
        db, 
        current_user["id"], 
        materia_id, 
        tema, 
        subtema
    )
    
    return {"task_id": task_id, "message": "Generación de contenido iniciada"}

@router.get("/task/{task_id}")
async def get_task_status(task_id: str, current_user = Depends(get_current_user)):
    """Verifica el estado de una tarea de generación de contenido"""
    
    result = await queue.get_task_result(task_id)
    
    if result["status"] == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return result

@router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(
    materia_id: Optional[int] = None,
    nivel: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Obtiene recursos educativos filtrados por materia y nivel"""
    
    query = "SELECT * FROM recursos WHERE 1=1"
    params = []
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    if nivel is not None:
        query += " AND nivel = ?"
        params.append(nivel)
    
    query += " ORDER BY created_at DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        resources = await cursor.fetchall()
    
    # Convertir lista de Row a lista de diccionarios
    return [ResourceResponse(**dict(resource)) for resource in resources]

# Función auxiliar para registrar solicitudes de contenido
async def register_content_request(db, usuario_id, materia_id, tema, subtema):
    """Registra una solicitud de generación de contenido en la base de datos"""
    
    async with db:
        await db.execute(
            """
            INSERT INTO interacciones (usuario_id, agente, tipo_interaccion, contenido)
            VALUES (?, ?, ?, ?)
            """,
            (
                usuario_id, 
                "Generador de Contenido", 
                "solicitud_contenido",
                f"Materia: {materia_id}, Tema: {tema}, Subtema: {subtema}"
            )
        )
        await db.commit()