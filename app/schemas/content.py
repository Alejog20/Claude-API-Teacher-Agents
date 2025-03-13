from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enumeraciones para valores constantes
class ContentType(str, Enum):
    """Tipos de contenido educativo"""
    LESSON = "lesson"
    EXERCISE = "exercise"
    EVALUATION = "evaluation"
    RESOURCE = "resource"

class ResourceType(str, Enum):
    """Tipos de recursos educativos"""
    VIDEO = "video"
    READING = "reading"
    INTERACTIVE = "interactive"
    PRACTICE = "practice"
    OTHER = "other"

class DifficultyLevel(int, Enum):
    """Niveles de dificultad"""
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    UPPER_INTERMEDIATE = 4
    ADVANCED = 5

class LearningStatus(str, Enum):
    """Estados de aprendizaje"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"

# Esquemas base para materiales educativos
class MaterialBase(BaseModel):
    """Esquema base para materias/materiales"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la materia")
    descripcion: Optional[str] = Field(None, description="Descripción de la materia")
    
    class Config:
        from_attributes = True

class MaterialCreate(MaterialBase):
    """Esquema para crear materias"""
    pass

class MaterialUpdate(BaseModel):
    """Esquema para actualizar materias"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la materia")
    descripcion: Optional[str] = Field(None, description="Descripción de la materia")
    
    class Config:
        from_attributes = True

class MaterialResponse(MaterialBase):
    """Esquema para respuesta de materias"""
    id: int = Field(..., description="ID de la materia")
    created_at: datetime = Field(..., description="Fecha de creación")
    
    class Config:
        from_attributes = True

# Esquemas para lecciones
class LessonBase(BaseModel):
    """Esquema base para lecciones"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la lección")
    materia_id: int = Field(..., description="ID de la materia relacionada")
    nivel: int = Field(..., ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: str = Field(..., description="Tema de la lección")
    subtema: Optional[str] = Field(None, description="Subtema específico")
    
    class Config:
        from_attributes = True

class LessonCreate(LessonBase):
    """Esquema para crear lecciones"""
    contenido: str = Field(..., description="Contenido completo de la lección")
    formato: Optional[str] = Field("texto", description="Formato del contenido")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class LessonUpdate(BaseModel):
    """Esquema para actualizar lecciones"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200, description="Título de la lección")
    nivel: Optional[int] = Field(None, ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: Optional[str] = Field(None, description="Tema de la lección")
    subtema: Optional[str] = Field(None, description="Subtema específico")
    contenido: Optional[str] = Field(None, description="Contenido completo de la lección")
    formato: Optional[str] = Field(None, description="Formato del contenido")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        from_attributes = True

class LessonResponse(LessonBase):
    """Esquema para respuesta de lecciones"""
    id: int = Field(..., description="ID de la lección")
    contenido: str = Field(..., description="Contenido completo de la lección")
    formato: str = Field(..., description="Formato del contenido")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha de última actualización")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    materia: Optional[MaterialResponse] = Field(None, description="Información de la materia")
    recursos_relacionados: Optional[List[Dict[str, Any]]] = Field(None, description="Recursos relacionados")
    
    class Config:
        from_attributes = True

# Esquemas para ejercicios
class ExerciseBase(BaseModel):
    """Esquema base para ejercicios"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título del ejercicio")
    materia_id: int = Field(..., description="ID de la materia relacionada")
    nivel: int = Field(..., ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: str = Field(..., description="Tema del ejercicio")
    
    class Config:
        from_attributes = True

class ExerciseCreate(ExerciseBase):
    """Esquema para crear ejercicios"""
    enunciado: str = Field(..., description="Enunciado del ejercicio")
    instrucciones: Optional[str] = Field(None, description="Instrucciones adicionales")
    pistas: Optional[List[str]] = Field(None, description="Pistas para la resolución")
    solucion: str = Field(..., description="Solución completa del ejercicio")
    tipo: Optional[str] = Field("práctica", description="Tipo de ejercicio")

class ExerciseUpdate(BaseModel):
    """Esquema para actualizar ejercicios"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200, description="Título del ejercicio")
    nivel: Optional[int] = Field(None, ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: Optional[str] = Field(None, description="Tema del ejercicio")
    enunciado: Optional[str] = Field(None, description="Enunciado del ejercicio")
    instrucciones: Optional[str] = Field(None, description="Instrucciones adicionales")
    pistas: Optional[List[str]] = Field(None, description="Pistas para la resolución")
    solucion: Optional[str] = Field(None, description="Solución completa del ejercicio")
    tipo: Optional[str] = Field(None, description="Tipo de ejercicio")
    
    class Config:
        from_attributes = True

class ExerciseResponse(ExerciseBase):
    """Esquema para respuesta de ejercicios"""
    id: int = Field(..., description="ID del ejercicio")
    enunciado: str = Field(..., description="Enunciado del ejercicio")
    instrucciones: Optional[str] = Field(None, description="Instrucciones adicionales")
    pistas: Optional[List[str]] = Field(None, description="Pistas para la resolución")
    solucion: str = Field(..., description="Solución completa del ejercicio")
    tipo: str = Field(..., description="Tipo de ejercicio")
    created_at: datetime = Field(..., description="Fecha de creación")
    materia: Optional[MaterialResponse] = Field(None, description="Información de la materia")
    
    class Config:
        from_attributes = True

# Esquemas para preguntas de evaluación
class QuestionBase(BaseModel):
    """Esquema base para preguntas de evaluación"""
    texto: str = Field(..., description="Texto de la pregunta")
    tipo: str = Field(..., description="Tipo de pregunta (selección múltiple, verdadero/falso, etc.)")
    
    class Config:
        from_attributes = True

class QuestionCreate(QuestionBase):
    """Esquema para crear preguntas"""
    opciones: Optional[List[str]] = Field(None, description="Opciones de respuesta (para selección múltiple)")
    respuesta_correcta: str = Field(..., description="Respuesta correcta")
    explicacion: Optional[str] = Field(None, description="Explicación de la respuesta")
    puntos: Optional[int] = Field(1, description="Puntos asignados a la pregunta")

class QuestionUpdate(BaseModel):
    """Esquema para actualizar preguntas"""
    texto: Optional[str] = Field(None, description="Texto de la pregunta")
    tipo: Optional[str] = Field(None, description="Tipo de pregunta")
    opciones: Optional[List[str]] = Field(None, description="Opciones de respuesta")
    respuesta_correcta: Optional[str] = Field(None, description="Respuesta correcta")
    explicacion: Optional[str] = Field(None, description="Explicación de la respuesta")
    puntos: Optional[int] = Field(None, description="Puntos asignados a la pregunta")
    
    class Config:
        from_attributes = True

class QuestionResponse(QuestionBase):
    """Esquema para respuesta de preguntas"""
    id: int = Field(..., description="ID de la pregunta")
    opciones: Optional[List[str]] = Field(None, description="Opciones de respuesta")
    puntos: int = Field(..., description="Puntos asignados a la pregunta")
    
    class Config:
        from_attributes = True

class QuestionWithAnswerResponse(QuestionResponse):
    """Esquema para respuesta de preguntas con respuesta incluida"""
    respuesta_correcta: str = Field(..., description="Respuesta correcta")
    explicacion: Optional[str] = Field(None, description="Explicación de la respuesta")

# Esquemas para evaluaciones
class EvaluationBase(BaseModel):
    """Esquema base para evaluaciones"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la evaluación")
    materia_id: int = Field(..., description="ID de la materia relacionada")
    nivel: int = Field(..., ge=1, le=10, description="Nivel de dificultad (1-10)")
    descripcion: Optional[str] = Field(None, description="Descripción de la evaluación")
    
    class Config:
        from_attributes = True

class EvaluationCreate(EvaluationBase):
    """Esquema para crear evaluaciones"""
    instrucciones: Optional[str] = Field(None, description="Instrucciones para la evaluación")
    tiempo_limite: Optional[int] = Field(None, description="Tiempo límite en minutos")
    preguntas: List[QuestionCreate] = Field(..., min_items=1, description="Preguntas de la evaluación")

class EvaluationUpdate(BaseModel):
    """Esquema para actualizar evaluaciones"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200, description="Título de la evaluación")
    nivel: Optional[int] = Field(None, ge=1, le=10, description="Nivel de dificultad (1-10)")
    descripcion: Optional[str] = Field(None, description="Descripción de la evaluación")
    instrucciones: Optional[str] = Field(None, description="Instrucciones para la evaluación")
    tiempo_limite: Optional[int] = Field(None, description="Tiempo límite en minutos")
    
    class Config:
        from_attributes = True

class EvaluationResponse(EvaluationBase):
    """Esquema para respuesta de evaluaciones"""
    id: int = Field(..., description="ID de la evaluación")
    instrucciones: Optional[str] = Field(None, description="Instrucciones para la evaluación")
    tiempo_limite: Optional[int] = Field(None, description="Tiempo límite en minutos")
    num_preguntas: int = Field(..., description="Número total de preguntas")
    created_at: datetime = Field(..., description="Fecha de creación")
    materia: Optional[MaterialResponse] = Field(None, description="Información de la materia")
    preguntas: Optional[List[QuestionResponse]] = Field(None, description="Preguntas de la evaluación")
    
    class Config:
        from_attributes = True

# Esquemas para recursos educativos
class ResourceBase(BaseModel):
    """Esquema base para recursos educativos"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título del recurso")
    tipo: ResourceType = Field(..., description="Tipo de recurso")
    materia_id: Optional[int] = Field(None, description="ID de la materia relacionada")
    
    class Config:
        from_attributes = True

class ResourceCreate(ResourceBase):
    """Esquema para crear recursos"""
    descripcion: Optional[str] = Field(None, description="Descripción del recurso")
    url: Optional[HttpUrl] = Field(None, description="URL del recurso (si es externo)")
    contenido: Optional[str] = Field(None, description="Contenido del recurso (si es interno)")
    nivel: Optional[int] = Field(None, ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: Optional[str] = Field(None, description="Tema relacionado")
    
    @validator('contenido')
    def validate_content_or_url(cls, v, values):
        if not v and 'url' not in values:
            raise ValueError('Debe proporcionar contenido o URL para el recurso')
        return v

class ResourceUpdate(BaseModel):
    """Esquema para actualizar recursos"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200, description="Título del recurso")
    tipo: Optional[ResourceType] = Field(None, description="Tipo de recurso")
    descripcion: Optional[str] = Field(None, description="Descripción del recurso")
    url: Optional[HttpUrl] = Field(None, description="URL del recurso")
    contenido: Optional[str] = Field(None, description="Contenido del recurso")
    nivel: Optional[int] = Field(None, ge=1, le=10, description="Nivel de dificultad (1-10)")
    tema: Optional[str] = Field(None, description="Tema relacionado")
    
    class Config:
        from_attributes = True

class ResourceResponse(ResourceBase):
    """Esquema para respuesta de recursos"""
    id: int = Field(..., description="ID del recurso")
    descripcion: Optional[str] = Field(None, description="Descripción del recurso")
    url: Optional[HttpUrl] = Field(None, description="URL del recurso (si es externo)")
    contenido: Optional[str] = Field(None, description="Contenido del recurso (si es interno)")
    nivel: Optional[int] = Field(None, description="Nivel de dificultad (1-10)")
    tema: Optional[str] = Field(None, description="Tema relacionado")
    created_at: datetime = Field(..., description="Fecha de creación")
    materia: Optional[MaterialResponse] = Field(None, description="Información de la materia")
    
    class Config:
        from_attributes = True

# Esquemas para progreso de aprendizaje
class ProgressBase(BaseModel):
    """Esquema base para progreso de aprendizaje"""
    usuario_id: int = Field(..., description="ID del usuario")
    materia_id: int = Field(..., description="ID de la materia")
    tema: str = Field(..., description="Tema estudiado")
    subtema: Optional[str] = Field(None, description="Subtema específico")
    
    class Config:
        from_attributes = True

class ProgressCreate(ProgressBase):
    """Esquema para crear registros de progreso"""
    estado: LearningStatus = Field(..., description="Estado del progreso")
    porcentaje_completado: float = Field(..., ge=0, le=100, description="Porcentaje completado (0-100)")

class ProgressUpdate(BaseModel):
    """Esquema para actualizar registros de progreso"""
    estado: Optional[LearningStatus] = Field(None, description="Estado del progreso")
    porcentaje_completado: Optional[float] = Field(None, ge=0, le=100, description="Porcentaje completado (0-100)")
    
    class Config:
        from_attributes = True

class ProgressResponse(ProgressBase):
    """Esquema para respuesta de progreso"""
    id: int = Field(..., description="ID del registro de progreso")
    estado: LearningStatus = Field(..., description="Estado del progreso")
    porcentaje_completado: float = Field(..., description="Porcentaje completado (0-100)")
    ultima_actividad: datetime = Field(..., description="Fecha de última actividad")
    
    class Config:
        from_attributes = True