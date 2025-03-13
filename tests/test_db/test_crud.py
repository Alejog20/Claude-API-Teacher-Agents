"""
Tests para las operaciones CRUD de la base de datos.
"""
import pytest
from pydantic import BaseModel
import asyncio
from datetime import date

from app.db import crud
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.learning import EvaluationCreate, ProgressUpdate

@pytest.mark.db
class TestUserCRUD:
    """Pruebas para operaciones CRUD de usuarios."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_db):
        """Test crear un nuevo usuario."""
        # Crear datos de prueba
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="Password123"
        )
        
        # Ejecutar la operación
        created_user = await crud.create_user(test_db, user_data)
        
        # Verificar resultados
        assert created_user is not None
        assert created_user["username"] == "newuser"
        assert created_user["email"] == "new@example.com"
        assert "password_hash" in created_user
        assert created_user["is_active"] == 1
    
    @pytest.mark.asyncio
    async def test_get_user(self, test_db):
        """Test obtener un usuario por ID."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="getuser",
            email="get@example.com",
            password="Password123"
        )
        created_user = await crud.create_user(test_db, user_data)
        user_id = created_user["id"]
        
        # Obtener el usuario
        user = await crud.get_user(test_db, user_id)
        
        # Verificar resultados
        assert user is not None
        assert user["id"] == user_id
        assert user["username"] == "getuser"
        assert user["email"] == "get@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, test_db):
        """Test obtener un usuario por nombre de usuario."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="uniqueuser",
            email="unique@example.com",
            password="Password123"
        )
        await crud.create_user(test_db, user_data)
        
        # Obtener el usuario por username
        user = await crud.get_user_by_username(test_db, "uniqueuser")
        
        # Verificar resultados
        assert user is not None
        assert user["username"] == "uniqueuser"
        assert user["email"] == "unique@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user(self, test_db):
        """Test actualizar un usuario."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="updateuser",
            email="update@example.com",
            password="Password123"
        )
        created_user = await crud.create_user(test_db, user_data)
        user_id = created_user["id"]
        
        # Actualizar el usuario
        update_data = UserUpdate(
            username="updateduser",
            email="updated@example.com"
        )
        updated_user = await crud.update_user(test_db, user_id, update_data)
        
        # Verificar resultados
        assert updated_user is not None
        assert updated_user["id"] == user_id
        assert updated_user["username"] == "updateduser"
        assert updated_user["email"] == "updated@example.com"

@pytest.mark.db
class TestProfileCRUD:
    """Pruebas para operaciones CRUD de perfiles."""
    
    @pytest.mark.asyncio
    async def test_create_profile(self, test_db):
        """Test crear un perfil de usuario."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="profileuser",
            email="profile@example.com",
            password="Password123"
        )
        created_user = await crud.create_user(test_db, user_data)
        user_id = created_user["id"]
        
        # Crear el perfil
        profile_data = ProfileCreate(
            usuario_id=user_id,
            nombre="Nombre",
            apellido="Apellido",
            fecha_nacimiento=date(2000, 1, 1),
            estilo_aprendizaje="visual",
            nivel_educativo="universitario"
        )
        
        created_profile = await crud.create_profile(test_db, profile_data)
        
        # Verificar resultados
        assert created_profile is not None
        assert created_profile["usuario_id"] == user_id
        assert created_profile["nombre"] == "Nombre"
        assert created_profile["apellido"] == "Apellido"
        assert "fecha_nacimiento" in created_profile
    
    @pytest.mark.asyncio
    async def test_get_profile_by_user_id(self, test_db):
        """Test obtener perfil por ID de usuario."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="profilegetuser",
            email="profileget@example.com",
            password="Password123"
        )
        created_user = await crud.create_user(test_db, user_data)
        user_id = created_user["id"]
        
        # Crear el perfil
        profile_data = ProfileCreate(
            usuario_id=user_id,
            nombre="Nombre",
            apellido="Apellido",
            fecha_nacimiento=date(2000, 1, 1),
            estilo_aprendizaje="visual",
            nivel_educativo="universitario"
        )
        
        await crud.create_profile(test_db, profile_data)
        
        # Obtener el perfil
        profile = await crud.get_profile_by_user_id(test_db, user_id)
        
        # Verificar resultados
        assert profile is not None
        assert profile["usuario_id"] == user_id
        assert profile["nombre"] == "Nombre"
        assert profile["apellido"] == "Apellido"
    
    @pytest.mark.asyncio
    async def test_update_profile(self, test_db):
        """Test actualizar perfil de usuario."""
        # Primero creamos un usuario para la prueba
        user_data = UserCreate(
            username="profileupdateuser",
            email="profileupdate@example.com",
            password="Password123"
        )
        created_user = await crud.create_user(test_db, user_data)
        user_id = created_user["id"]
        
        # Crear el perfil
        profile_data = ProfileCreate(
            usuario_id=user_id,
            nombre="Nombre",
            apellido="Apellido",
            fecha_nacimiento=date(2000, 1, 1),
            estilo_aprendizaje="visual",
            nivel_educativo="universitario"
        )
        
        await crud.create_profile(test_db, profile_data)
        
        # Actualizar el perfil
        update_data = ProfileUpdate(
            nombre="NombreActualizado",
            apellido="ApellidoActualizado",
            nivel_educativo="maestría"
        )
        
        updated_profile = await crud.update_profile(test_db, user_id, update_data)
        
        # Verificar resultados
        assert updated_profile is not None
        assert updated_profile["usuario_id"] == user_id
        assert updated_profile["nombre"] == "NombreActualizado"
        assert updated_profile["apellido"] == "ApellidoActualizado"
        assert updated_profile["nivel_educativo"] == "maestría"

@pytest.mark.db
class TestLearningCRUD:
    """Pruebas para operaciones CRUD relacionadas con el aprendizaje."""
    
    @pytest.mark.asyncio
    async def test_create_evaluation(self, test_db):
        """Test crear una evaluación."""
        # Crear una evaluación
        eval_data = EvaluationCreate(
            usuario_id=1,  # Usuario existente en los datos de prueba
            materia_id=1,  # Materia existente en los datos de prueba
            nivel=3,
            puntaje=92.5
        )
        
        created_eval = await crud.create_evaluation(test_db, eval_data)
        
        # Verificar resultados
        assert created_eval is not None
        assert created_eval["usuario_id"] == 1
        assert created_eval["materia_id"] == 1
        assert created_eval["nivel"] == 3
        assert created_eval["puntaje"] == 92.5
    
    @pytest.mark.asyncio
    async def test_get_user_evaluations(self, test_db):
        """Test obtener evaluaciones de un usuario."""
        # Crear algunas evaluaciones adicionales
        eval_data1 = EvaluationCreate(
            usuario_id=1,
            materia_id=1,
            nivel=2,
            puntaje=88.0
        )
        
        eval_data2 = EvaluationCreate(
            usuario_id=1,
            materia_id=2,
            nivel=1,
            puntaje=75.0
        )
        
        await crud.create_evaluation(test_db, eval_data1)
        await crud.create_evaluation(test_db, eval_data2)
        
        # Obtener todas las evaluaciones del usuario
        evaluations = await crud.get_user_evaluations(test_db, 1)
        
        # Verificar resultados
        assert len(evaluations) >= 3  # Al menos las 3 evaluaciones que hemos creado
        
        # Obtener evaluaciones filtradas por materia
        evaluations_filtered = await crud.get_user_evaluations(test_db, 1, materia_id=2)
        
        # Verificar resultados filtrados
        assert len(evaluations_filtered) >= 1
        assert all(e["materia_id"] == 2 for e in evaluations_filtered)
    
    @pytest.mark.asyncio
    async def test_update_progress(self, test_db):
        """Test actualizar progreso de aprendizaje."""
        # Crear datos de progreso
        progress_data = ProgressUpdate(
            usuario_id=1,
            materia_id=1,
            tema="Geometría",
            subtema="Triángulos",
            estado="in_progress",
            porcentaje_completado=50.0
        )
        
        # Actualizar progreso (crea nuevo registro)
        updated_progress = await crud.update_progress(test_db, progress_data)
        
        # Verificar resultados
        assert updated_progress is not None
        assert updated_progress["usuario_id"] == 1
        assert updated_progress["materia_id"] == 1
        assert updated_progress["tema"] == "Geometría"
        assert updated_progress["subtema"] == "Triángulos"
        assert updated_progress["estado"] == "in_progress"
        assert updated_progress["porcentaje_completado"] == 50.0
        
        # Actualizar progreso existente
        progress_data.porcentaje_completado = 75.0
        progress_data.estado = "completed"
        
        updated_progress_again = await crud.update_progress(test_db, progress_data)
        
        # Verificar actualización
        assert updated_progress_again is not None
        assert updated_progress_again["porcentaje_completado"] == 75.0
        assert updated_progress_again["estado"] == "completed"