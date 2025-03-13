from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MateriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class MateriaCreate(MateriaBase):
    pass

class MateriaResponse(MateriaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class EvaluationBase(BaseModel):
    materia_id: int
    nivel: int = Field(..., ge=1, le=10)
    puntaje: float = Field(..., ge=0, le=100)

class EvaluationCreate(EvaluationBase):
    usuario_id: int

class EvaluationResponse(EvaluationBase):
    id: int
    fecha: datetime
    
    class Config:
        from_attributes = True

class ProgressBase(BaseModel):
    materia_id: int
    tema: str
    subtema: Optional[str] = None
    estado: str = Field(..., pattern="^(no_iniciado|en_progreso|completado)$")
    porcentaje_completado: float = Field(..., ge=0, le=100)

class ProgressUpdate(ProgressBase):
    usuario_id: int

class ProgressResponse(ProgressBase):
    id: int
    usuario_id: int
    ultima_actividad: datetime
    
    class Config:
        from_attributes = True

class ResourceBase(BaseModel):
    titulo: str
    tipo: str = Field(..., pattern="^(video|lectura|ejercicio|examen|otro)$")
    url: Optional[str] = None
    contenido: Optional[str] = None
    materia_id: Optional[int] = None
    nivel: Optional[int] = Field(None, ge=1, le=10)

class ResourceCreate(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True