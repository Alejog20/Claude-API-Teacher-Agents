from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.learning import EvaluationCreate, EvaluationResponse, ProgressUpdate, ProgressResponse
from app.api.routes.auth import get_current_user
from app.db.database import get_db
from app.services.queue import queue
from app.utils.logger import setup_logger

router = APIRouter(prefix="/progress", tags=["Progreso"])
logger = setup_logger("progress")

@router.post("/evaluate", status_code=status.HTTP_202_ACCEPTED)
async def request_evaluation(
    materia_id: int,
    nivel: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Solicita una evaluación para una materia específica"""
    
    # Verificar que la materia existe
    async with db:
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Obtener información del perfil para personalización
        cursor = await db.execute(
            "SELECT * FROM perfiles WHERE usuario_id = ?", 
            (current_user["id"],)
        )
        profile = await cursor.fetchone()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe completar su perfil antes de realizar evaluaciones"
            )
    
    # Si no se especifica nivel, intentar determinar el último nivel evaluado
    if nivel is None:
        async with db:
            cursor = await db.execute(
                """
                SELECT nivel FROM evaluaciones 
                WHERE usuario_id = ? AND materia_id = ? 
                ORDER BY fecha DESC LIMIT 1
                """,
                (current_user["id"], materia_id)
            )
            last_eval = await cursor.fetchone()
            
            if last_eval:
                nivel = dict(last_eval)["nivel"] + 1
            else:
                nivel = 1
    
    # Crear contexto para la evaluación
    context = {
        "usuario_id": current_user["id"],
        "materia": dict(materia)["nombre"],
        "materia_id": materia_id,
        "nivel": nivel,
        "estilo_aprendizaje": dict(profile)["estilo_aprendizaje"],
        "nivel_educativo": dict(profile)["nivel_educativo"]
    }
    
    # Encolar la tarea de evaluación
    task_id = await queue.enqueue("evaluacion_inicial", context)
    
    return {"task_id": task_id, "message": "Generación de evaluación iniciada", "nivel": nivel}

@router.post("/evaluations", response_model=EvaluationResponse)
async def register_evaluation(
    evaluation: EvaluationCreate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Registra el resultado de una evaluación"""
    
    # Verificar que la materia existe
    async with db:
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (evaluation.materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Registrar la evaluación
        cursor = await db.execute(
            """
            INSERT INTO evaluaciones (usuario_id, materia_id, nivel, puntaje)
            VALUES (?, ?, ?, ?)
            """,
            (current_user["id"], evaluation.materia_id, evaluation.nivel, evaluation.puntaje)
        )
        await db.commit()
        
        # Obtener la evaluación registrada
        eval_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM evaluaciones WHERE id = ?", (eval_id,))
        registered_eval = await cursor.fetchone()
    
    # Convertir Row a diccionario
    eval_dict = dict(registered_eval)
    return EvaluationResponse(**eval_dict)

@router.get("/evaluations", response_model=List[EvaluationResponse])
async def get_evaluations(
    materia_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Obtiene el historial de evaluaciones del estudiante"""
    
    query = "SELECT * FROM evaluaciones WHERE usuario_id = ?"
    params = [current_user["id"]]
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    query += " ORDER BY fecha DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        evaluations = await cursor.fetchall()
    
    # Convertir lista de Row a lista de diccionarios
    return [EvaluationResponse(**dict(eval)) for eval in evaluations]

@router.post("/update", response_model=ProgressResponse)
async def update_progress(
    progress: ProgressUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Actualiza el progreso del estudiante en un tema específico"""
    
    # Verificar que la materia existe
    async with db:
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (progress.materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Verificar si ya existe un registro de progreso para este tema
        cursor = await db.execute(
            """
            SELECT * FROM progreso 
            WHERE usuario_id = ? AND materia_id = ? AND tema = ? AND (subtema = ? OR (subtema IS NULL AND ? IS NULL))
            """,
            (current_user["id"], progress.materia_id, progress.tema, progress.subtema, progress.subtema)
        )
        existing_progress = await cursor.fetchone()
        
        if existing_progress:
            # Actualizar el progreso existente
            await db.execute(
                """
                UPDATE progreso 
                SET estado = ?, porcentaje_completado = ?, ultima_actividad = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (progress.estado, progress.porcentaje_completado, dict(existing_progress)["id"])
            )
            await db.commit()
            
            # Obtener el progreso actualizado
            cursor = await db.execute("SELECT * FROM progreso WHERE id = ?", (dict(existing_progress)["id"],))
            updated_progress = await cursor.fetchone()
        else:
            # Crear un nuevo registro de progreso
            cursor = await db.execute(
                """
                INSERT INTO progreso (usuario_id, materia_id, tema, subtema, estado, porcentaje_completado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    current_user["id"], 
                    progress.materia_id, 
                    progress.tema, 
                    progress.subtema, 
                    progress.estado, 
                    progress.porcentaje_completado
                )
            )
            await db.commit()
            
            # Obtener el progreso creado
            progress_id = cursor.lastrowid
            cursor = await db.execute("SELECT * FROM progreso WHERE id = ?", (progress_id,))
            updated_progress = await cursor.fetchone()
    
    # Convertir Row a diccionario
    progress_dict = dict(updated_progress)
    return ProgressResponse(**progress_dict)

@router.get("/status", response_model=List[ProgressResponse])
async def get_progress_status(
    materia_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Obtiene el estado de progreso del estudiante"""
    
    query = "SELECT * FROM progreso WHERE usuario_id = ?"
    params = [current_user["id"]]
    
    if materia_id is not None:
        query += " AND materia_id = ?"
        params.append(materia_id)
    
    query += " ORDER BY ultima_actividad DESC"
    
    async with db:
        cursor = await db.execute(query, params)
        progress_items = await cursor.fetchall()
    
    # Convertir lista de Row a lista de diccionarios
    return [ProgressResponse(**dict(item)) for item in progress_items]

@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_progress(
    materia_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Solicita un análisis del progreso del estudiante en una materia"""
    
    # Verificar que la materia existe
    async with db:
        cursor = await db.execute("SELECT * FROM materias WHERE id = ?", (materia_id,))
        materia = await cursor.fetchone()
        
        if not materia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Obtener evaluaciones y progreso para contexto
        cursor = await db.execute(
            """
            SELECT * FROM evaluaciones 
            WHERE usuario_id = ? AND materia_id = ? 
            ORDER BY fecha DESC LIMIT 5
            """,
            (current_user["id"], materia_id)
        )
        evaluations = await cursor.fetchall()
        
        cursor = await db.execute(
            """
            SELECT * FROM progreso 
            WHERE usuario_id = ? AND materia_id = ? 
            ORDER BY ultima_actividad DESC
            """,
            (current_user["id"], materia_id)
        )
        progress_items = await cursor.fetchall()
    
    # Convertir resultados a diccionarios
    eval_list = [dict(eval) for eval in evaluations]
    progress_list = [dict(item) for item in progress_items]
    
    # Crear contexto para el análisis
    context = {
        "usuario_id": current_user["id"],
        "materia": dict(materia)["nombre"],
        "materia_id": materia_id,
        "evaluaciones": eval_list,
        "progreso": progress_list
    }
    
    # Encolar la tarea de análisis
    task_id = await queue.enqueue("analisis_progreso", context)
    
    return {"task_id": task_id, "message": "Análisis de progreso iniciado"}