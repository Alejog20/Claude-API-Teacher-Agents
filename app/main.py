# app/main.py
import os
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import auth, students, content, progress
from app.services.queue import QueueService
from app.services.coordination import AgentCoordinator
from app.db.database import engine, Base
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Plataforma de Aprendizaje Personalizado con Agentes de Claude",
    description="Sistema adaptativo de aprendizaje con agentes de IA interconectados",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a dominio específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Variables globales para servicios
queue_service = None
agent_coordinator = None

@app.on_event("startup")
async def startup_event():
    """Inicializa los servicios al arrancar la aplicación"""
    global queue_service, agent_coordinator
    
    try:
        # Inicializar servicio de colas
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        queue_service = QueueService(redis_url=redis_url)
        await queue_service.connect()
        
        # Inicializar coordinador de agentes
        agent_coordinator = AgentCoordinator(queue_service)
        await agent_coordinator.initialize()
        
        logger.info("Servicios iniciados correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar servicios: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Detiene los servicios al apagar la aplicación"""
    global queue_service, agent_coordinator
    
    try:
        if agent_coordinator:
            await agent_coordinator.shutdown()
        
        if queue_service:
            await queue_service.stop()
        
        logger.info("Servicios detenidos correctamente")
    except Exception as e:
        logger.error(f"Error al detener servicios: {str(e)}")

# Incluir rutas de la API
app.include_router(auth.router, prefix="/api", tags=["Autenticación"])
app.include_router(students.router, prefix="/api/students", tags=["Estudiantes"])
app.include_router(content.router, prefix="/api/content", tags=["Contenido"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progreso"])

# Endpoints para verificar estado
@app.get("/")
async def root():
    return {"status": "online", "message": "Plataforma de Aprendizaje Personalizado"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"db": True, "queue": queue_service is not None}}

# Ejecutar aplicación directamente si se llama al script
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)