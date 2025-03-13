from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar, Union
from datetime import datetime

# Definir tipo genérico para respuestas paginadas
T = TypeVar('T')

class StandardResponse(BaseModel):
    """Esquema estándar para respuestas exitosas de la API"""
    status: str = Field("success", description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Any] = Field(None, description="Datos de la respuesta")

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error de la API"""
    status: str = Field("error", description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje de error")
    error_code: Optional[str] = Field(None, description="Código de error")
    details: Optional[Any] = Field(None, description="Detalles adicionales del error")

class PageResponse(Generic[T]):
    """Esquema para respuestas paginadas"""
    items: List[T] = Field(..., description="Lista de elementos")
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    pages: int = Field(..., description="Total de páginas")
    
    class Config:
        from_attributes = True

class ProgressSummary(BaseModel):
    """Esquema para resumen de progreso"""
    materia_id: int = Field(..., description="ID de la materia")
    materia_nombre: str = Field(..., description="Nombre de la materia")
    temas_totales: int = Field(..., description="Total de temas en la materia")
    temas_completados: int = Field(..., description="Temas completados")
    porcentaje_total: float = Field(..., description="Porcentaje total de progreso")
    ultima_actividad: datetime = Field(..., description="Fecha de última actividad")
    
    class Config:
        from_attributes = True

class EvaluationSummary(BaseModel):
    """Esquema para resumen de evaluaciones"""
    materia_id: int = Field(..., description="ID de la materia")
    materia_nombre: str = Field(..., description="Nombre de la materia")
    evaluaciones_totales: int = Field(..., description="Total de evaluaciones realizadas")
    puntaje_promedio: float = Field(..., description="Puntaje promedio obtenido")
    nivel_actual: int = Field(..., description="Nivel actual en la materia")
    ultima_evaluacion: datetime = Field(..., description="Fecha de última evaluación")
    
    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    """Esquema para respuesta de progreso general"""
    progreso_general: float = Field(..., description="Porcentaje de progreso general")
    materias: List[ProgressSummary] = Field(..., description="Progreso por materia")
    evaluaciones: List[EvaluationSummary] = Field(..., description="Resumen de evaluaciones")
    ultimo_contenido: Optional[Any] = Field(None, description="Último contenido estudiado")
    recomendaciones: Optional[List[Any]] = Field(None, description="Recomendaciones personalizadas")
    
    class Config:
        from_attributes = True

class PathItem(BaseModel):
    """Esquema para un ítem en la ruta de aprendizaje"""
    id: int = Field(..., description="ID del ítem")
    tipo: str = Field(..., description="Tipo de ítem (lección, ejercicio, evaluación)")
    titulo: str = Field(..., description="Título del ítem")
    descripcion: Optional[str] = Field(None, description="Descripción breve")
    nivel: int = Field(..., description="Nivel de dificultad")
    estado: Optional[str] = Field(None, description="Estado actual (para el usuario)")
    fecha_completado: Optional[datetime] = Field(None, description="Fecha de completado (si aplica)")
    
    class Config:
        from_attributes = True

class LearningPathResponse(BaseModel):
    """Esquema para respuesta de ruta de aprendizaje"""
    materia_id: int = Field(..., description="ID de la materia")
    materia_nombre: str = Field(..., description="Nombre de la materia")
    nivel_actual: int = Field(..., description="Nivel actual del estudiante")
    progreso_total: float = Field(..., description="Progreso total en la ruta")
    path_items: List[PathItem] = Field(..., description="Ítems en la ruta de aprendizaje")
    proximos_pasos: List[PathItem] = Field(..., description="Próximos ítems recomendados")
    
    class Config:
        from_attributes = True

class AgentResponse(BaseModel):
    """Esquema para respuestas generadas por agentes"""
    agent_type: str = Field(..., description="Tipo de agente que generó la respuesta")
    content: str = Field(..., description="Contenido de la respuesta")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Contexto utilizado para generar la respuesta")
    generated_at: datetime = Field(..., description="Fecha de generación")
    
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    """Esquema para respuestas de tareas asíncronas"""
    task_id: str = Field(..., description="ID de la tarea")
    status: str = Field(..., description="Estado de la tarea (pending, processing, completed, failed)")
    message: str = Field(..., description="Mensaje descriptivo")
    result: Optional[Any] = Field(None, description="Resultado de la tarea (si está completa)")
    created_at: datetime = Field(..., description="Fecha de creación de la tarea")
    completed_at: Optional[datetime] = Field(None, description="Fecha de finalización de la tarea")
    error: Optional[str] = Field(None, description="Error (si la tarea falló)")
    
    class Config:
        from_attributes = True