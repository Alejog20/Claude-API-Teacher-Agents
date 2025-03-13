"""
Content generation service using Claude API.
"""
from typing import Dict, Any, List, Optional
import json
import asyncio

from app.utils.logger import setup_logger
from app.services.claude_api import ClaudeClient
from app.agents import create_agent

logger = setup_logger("content_generator")

class ContentGenerator:
    """
    Service for generating educational content.
    """
    
    def __init__(self):
        self.claude_client = ClaudeClient()
    
    async def generate_lesson(
        self,
        subject: str,
        topic: str,
        level: str,
        learning_style: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete lesson.
        
        Args:
            subject: Subject area
            topic: Topic for the lesson
            level: Difficulty level
            learning_style: Learning style preference
            context: Additional context
            
        Returns:
            Complete lesson content
        """
        # Use the appropriate agent
        agent = create_agent("content")
        
        # Create context dictionary
        full_context = {
            "subject": subject,
            "topic": topic,
            "level": level,
            "learning_style": learning_style
        }
        
        if context:
            full_context.update(context)
        
        # Generate lesson content
        prompt = f"""
        Crea una lección completa sobre el tema '{topic}' en la materia de {subject}.
        
        Nivel de dificultad: {level}
        {f"Estilo de aprendizaje: {learning_style}" if learning_style else ""}
        
        La lección debe incluir:
        1. Introducción y objetivos de aprendizaje
        2. Explicación clara de los conceptos clave
        3. Ejemplos ilustrativos
        4. Ejercicios prácticos con soluciones
        5. Resumen de los puntos principales
        6. Recursos adicionales recomendados
        
        Estructura el contenido en secciones claras y utiliza un lenguaje adecuado para el nivel indicado.
        """
        
        response = await agent.process_message(prompt, full_context)
        
        # Parse sections from the response
        sections = self._parse_lesson_sections(response)
        
        return {
            "subject": subject,
            "topic": topic,
            "level": level,
            "learning_style": learning_style,
            "content": response,
            "sections": sections
        }
    
    async def generate_exercises(
        self,
        subject: str,
        topic: str,
        level: str,
        num_exercises: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate practice exercises.
        
        Args:
            subject: Subject area
            topic: Topic for exercises
            level: Difficulty level
            num_exercises: Number of exercises to generate
            context: Additional context
            
        Returns:
            Generated exercises with solutions
        """
        # Use subject-specific agent
        agent = create_agent(self._map_subject_to_agent(subject))
        
        # Build prompt
        prompt = f"""
        Crea {num_exercises} ejercicios prácticos sobre '{topic}' en la materia de {subject}.
        
        Nivel de dificultad: {level}
        
        Para cada ejercicio, proporciona:
        1. El enunciado claro del problema
        2. La solución completa paso a paso
        
        Enumera los ejercicios claramente y separa cada uno con un título.
        """
        
        # Generate exercises
        response = await agent.process_message(prompt, context or {})
        
        # Parse exercises
        exercises = self._parse_exercises(response, num_exercises)
        
        return {
            "subject": subject,
            "topic": topic,
            "level": level,
            "exercises": exercises,
            "raw_content": response
        }
    
    async def generate_evaluation(
        self,
        subject: str,
        topics: List[str],
        level: str,
        num_questions: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an evaluation.
        
        Args:
            subject: Subject area
            topics: List of topics to cover
            level: Difficulty level
            num_questions: Number of questions
            context: Additional context
            
        Returns:
            Complete evaluation with questions and answers
        """
        # Use evaluation agent
        agent = create_agent("feedback")
        
        # Format topics
        topics_str = ", ".join(topics)
        
        # Build prompt
        prompt = f"""
        Crea una evaluación sobre {subject}, enfocada en los siguientes temas: {topics_str}.
        
        Nivel de dificultad: {level}
        Número de preguntas: {num_questions}
        
        Incluye una mezcla de tipos de preguntas (selección múltiple, respuesta corta, problemas).
        
        Para cada pregunta, proporciona:
        1. El enunciado claro
        2. Opciones de respuesta (si aplica)
        3. La respuesta correcta
        4. Una breve explicación de la respuesta
        
        Enumera las preguntas claramente.
        """
        
        # Generate evaluation
        response = await agent.process_message(prompt, context or {})
        
        # Parse questions
        questions = self._parse_questions(response)
        
        return {
            "subject": subject,
            "topics": topics,
            "level": level,
            "questions": questions,
            "raw_content": response
        }
    
    async def recommend_resources(
        self,
        subject: str,
        topic: str,
        level: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend educational resources.
        
        Args:
            subject: Subject area
            topic: Topic of interest
            level: Student's level
            context: Additional context
            
        Returns:
            Recommended resources
        """
        # Use content agent
        agent = create_agent("content")
        
        # Build prompt
        prompt = f"""
        Recomienda recursos educativos para estudiar el tema '{topic}' en la materia de {subject}.
        
        Nivel del estudiante: {level}
        
        Para cada recurso, proporciona:
        1. Título/nombre
        2. Tipo de recurso (libro, video, artículo, aplicación, etc.)
        3. Breve descripción
        4. Por qué es útil para este tema
        
        Incluye una variedad de tipos de recursos para diferentes estilos de aprendizaje.
        """
        
        # Generate recommendations
        response = await agent.process_message(prompt, context or {})
        
        # Parse resources
        resources = self._parse_resources(response)
        
        return {
            "subject": subject,
            "topic": topic,
            "level": level,
            "resources": resources,
            "raw_content": response
        }
    
    def _map_subject_to_agent(self, subject: str) -> str:
        """Map a subject to the appropriate agent type."""
        subject_lower = subject.lower()
        
        if any(term in subject_lower for term in ["matemática", "álgebra", "cálculo", "geometría"]):
            return "mathematics"
        elif any(term in subject_lower for term in ["ciencia", "física", "química", "biología"]):
            return "science"
        elif any(term in subject_lower for term in ["lenguaje", "literatura", "gramática", "comunicación"]):
            return "language"
        elif any(term in subject_lower for term in ["historia", "geografía", "civismo"]):
            return "history"
        else:
            return "coordinator"  # Default to coordinator
    
    def _parse_lesson_sections(self, text: str) -> Dict[str, str]:
        """Parse a lesson into sections."""
        sections = {
            "introduction": "",
            "concepts": "",
            "examples": "",
            "exercises": "",
            "summary": "",
            "resources": ""
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to identify section headers
            lower_line = line.lower()
            
            if any(term in lower_line for term in ["introducción", "objetivos", "introduction"]):
                current_section = "introduction"
                sections[current_section] += line + "\n"
            elif any(term in lower_line for term in ["conceptos", "explicación", "teoría", "concepts"]):
                current_section = "concepts"
                sections[current_section] += line + "\n"
            elif any(term in lower_line for term in ["ejemplo", "muestra", "examples"]):
                current_section = "examples"
                sections[current_section] += line + "\n"
            elif any(term in lower_line for term in ["ejercicio", "práctica", "exercise"]):
                current_section = "exercises"
                sections[current_section] += line + "\n"
            elif any(term in lower_line for term in ["resumen", "conclusión", "summary"]):
                current_section = "summary"
                sections[current_section] += line + "\n"
            elif any(term in lower_line for term in ["recursos", "recomendaciones", "resources"]):
                current_section = "resources"
                sections[current_section] += line + "\n"
            elif current_section:
                sections[current_section] += line + "\n"
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def _parse_exercises(self, text: str, expected_count: int) -> List[Dict[str, str]]:
        """Parse exercises from text."""
        exercises = []
        current_exercise = None
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for exercise header (numbered or with "Ejercicio" prefix)
            if line.startswith(("Ejercicio", "Exercise")) or (line[0].isdigit() and line[1] in ['.', ')', ':']):
                # Save previous exercise if exists
                if current_exercise:
                    exercises.append(current_exercise)
                
                # Start new exercise
                current_exercise = {
                    "question": line,
                    "solution": ""
                }
                current_section = "question"
                
            elif current_exercise:
                # Check for solution marker
                lower_line = line.lower()
                if any(term in lower_line for term in ["solución", "solution", "respuesta"]):
                    current_section = "solution"
                    continue
                
                # Add content to current section
                if current_section == "question" and not current_exercise["solution"]:
                    current_exercise["question"] += "\n" + line
                elif current_section == "solution":
                    current_exercise["solution"] += "\n" + line
        
        # Add the last exercise
        if current_exercise:
            exercises.append(current_exercise)
        
        # Clean up
        for exercise in exercises:
            exercise["question"] = exercise["question"].strip()
            exercise["solution"] = exercise["solution"].strip()
        
        return exercises
    
    def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Parse questions from evaluation text."""
        questions = []
        current_question = None
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for question header
            if line.startswith(("Pregunta", "Question")) or (line[0].isdigit() and line[1] in ['.', ')', ':']):
                # Save previous question if exists
                if current_question:
                    questions.append(current_question)
                
                # Start new question
                current_question = {
                    "text": line,
                    "options": [],
                    "correct_answer": "",
                    "explanation": ""
                }
                current_section = "text"
                
            elif current_question:
                lower_line = line.lower()
                
                # Check for options (typically start with a letter and delimiter)
                if line and line[0].isalpha() and len(line) > 1 and line[1] in ['.', ')', ':']:
                    current_question["options"].append(line)
                    current_section = "options"
                # Check for answer marker
                elif "respuesta" in lower_line or "answer" in lower_line:
                    current_section = "correct_answer"
                    continue
                # Check for explanation marker
                elif "explicación" in lower_line or "explanation" in lower_line:
                    current_section = "explanation"
                    continue
                # Add content to current section
                elif current_section == "text" and not current_question["options"]:
                    current_question["text"] += "\n" + line
                elif current_section == "correct_answer":
                    current_question["correct_answer"] += line + " "
                elif current_section == "explanation":
                    current_question["explanation"] += line + " "
        
        # Add the last question
        if current_question:
            questions.append(current_question)
        
        # Clean up
        for question in questions:
            question["text"] = question["text"].strip()
            question["correct_answer"] = question["correct_answer"].strip()
            question["explanation"] = question["explanation"].strip()
        
        return questions
    
    def _parse_resources(self, text: str) -> List[Dict[str, str]]:
        """Parse resources from recommendation text."""
        resources = []
        current_resource = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for resource header (bullet points or numbers)
            if line.startswith(("- ", "* ", "• ")) or (line[0].isdigit() and line[1] in ['.', ')', ':']):
                # Save previous resource if exists
                if current_resource:
                    resources.append(current_resource)
                
                # Start new resource
                current_resource = {
                    "title": line.lstrip("- *•0123456789.) "),
                    "type": "",
                    "description": ""
                }
            elif current_resource:
                lower_line = line.lower()
                
                # Check for type marker
                if "tipo:" in lower_line or "type:" in lower_line:
                    current_resource["type"] = line.split(":", 1)[1].strip()
                # Check for description marker
                elif "descripción:" in lower_line or "description:" in lower_line:
                    current_resource["description"] = line.split(":", 1)[1].strip()
                # Default to adding to description
                elif not current_resource["type"]:
                    current_resource["type"] = line
                else:
                    current_resource["description"] += " " + line
        
        # Add the last resource
        if current_resource:
            resources.append(current_resource)
        
        return resources

# Task processing function for the queue service
async def process_task(task: Dict[str, Any]) -> Any:
    """
    Process a task from the queue.
    
    Args:
        task: Task data
        
    Returns:
        Task result
    """
    task_type = task["type"]
    data = task["data"]
    generator = ContentGenerator()
    
    if task_type == "generate_lesson":
        return await generator.generate_lesson(
            subject=data.get("subject", ""),
            topic=data.get("topic", ""),
            level=data.get("level", "intermediate"),
            learning_style=data.get("learning_style"),
            context=data
        )
    
    elif task_type == "generate_exercises":
        return await generator.generate_exercises(
            subject=data.get("subject", ""),
            topic=data.get("topic", ""),
            level=data.get("level", "intermediate"),
            num_exercises=data.get("num_exercises", 5),
            context=data
        )
    
    elif task_type == "generate_evaluation":
        return await generator.generate_evaluation(
            subject=data.get("subject", ""),
            topics=data.get("topics", [data.get("topic", "")]),
            level=data.get("level", "intermediate"),
            num_questions=data.get("num_questions", 10),
            context=data
        )
    
    elif task_type == "recommend_resources":
        return await generator.recommend_resources(
            subject=data.get("subject", ""),
            topic=data.get("topic", ""),
            level=data.get("level", "intermediate"),
            context=data
        )
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")

# Helper function for the service layer
async def generate_content(
    subject: str,
    topic: str,
    level: str = "intermediate",
    content_type: str = "lesson",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate educational content of the specified type.
    
    Args:
        subject: Subject area
        topic: Topic of interest
        level: Difficulty level
        content_type: Type of content to generate
        context: Additional context
        
    Returns:
        Generated content
    """
    generator = ContentGenerator()
    
    if content_type == "lesson":
        return await generator.generate_lesson(subject, topic, level, context=context)
    
    elif content_type == "exercises":
        return await generator.generate_exercises(subject, topic, level, context=context)
    
    elif content_type == "evaluation":
        return await generator.generate_evaluation(subject, [topic], level, context=context)
    
    elif content_type == "resources":
        return await generator.recommend_resources(subject, topic, level, context=context)
    
    else:
        raise ValueError(f"Unknown content type: {content_type}")