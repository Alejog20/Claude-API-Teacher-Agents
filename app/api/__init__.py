"""
API route modules for the learning platform.
"""
from fastapi import APIRouter

# Import individual routers
from app.api.routes.auth import router as auth_router
from app.api.routes.students import router as students_router
from app.api.routes.content import router as content_router
from app.api.routes.progress import router as progress_router
from app.api.routes.chat import router as chat_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(students_router, prefix="/students", tags=["Students"])
api_router.include_router(content_router, prefix="/content", tags=["Content"])
api_router.include_router(progress_router, prefix="/progress", tags=["Progress"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])

# Export all routers individually for flexibility
__all__ = [
    'api_router',
    'auth_router',
    'students_router',
    'content_router',
    'progress_router',
    'chat_router'
]