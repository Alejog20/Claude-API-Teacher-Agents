# Importaciones para facilitar el acceso a los modelos
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.schemas.learning import EvaluationCreate, ProgressUpdate, ResourceCreate

__all__ = [
    'UserCreate', 'UserLogin', 'UserResponse', 'Token', 'TokenData',
    'ProfileCreate', 'ProfileUpdate', 'ProfileResponse',
    'EvaluationCreate', 'ProgressUpdate', 'ResourceCreate'
]