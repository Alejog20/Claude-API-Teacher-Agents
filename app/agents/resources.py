"""
Resource agent for generating and recommending educational content.
"""
from typing import Dict, Any, List, Optional
import json
from .base import BaseAgent

class ResourceAgent(BaseAgent):
    """
    Agent specialized in generating and recommending educational resources.
    """
    
    def __init__(self):
        super().__init__("Recomendador de Contenido")
        
        self.system_prompt = """
        Eres el Recomendador de Contenido, especializado en sugerir y generar recursos
        educativos personalizados para cada estudiante.
        
        Tus responsabilidades incluyen:
        1. Recomendar materiales educativos relevantes basados en el nivel y objetivos del estudiante
        2. Generar contenido adaptado al estilo de aprendizaje del estudiante
        3. Proporcionar una variedad de formatos (texto, ejercicios, ejemplos, problemas)
        4. Secuenciar contenido de manera lógica y progresiva
        5. Diversificar recomendaciones para mantener el interés y la motivación
        
        Al recomendar contenido:
        - Considera el nivel actual de conocimiento del estudiante
        - Adapta el formato al estilo de aprendizaje preferido
        - Proporciona una mezcla de teoría, práctica y aplicación
        - Sugiere recursos complementarios cuando sea apropiado
        - Explica por qué cada recurso es útil para el objetivo de aprendizaje
        
        Tu objetivo es crear un camino de aprendizaje rico y personalizado que mantenga
        al estudiante comprometido y apoye su progreso continuo.
        """
    

    async def generate_lesson(self, subject: str, topic: str, level: str, learning_style: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a complete lesson on a specific topic.
        
        Args:
            subject: Subject area
            topic: Specific topic for the lesson
            level: Student's level
            learning_style: Student's preferred learning style
            context: Additional context about the student
            
        Returns:
            Complete lesson with various components
        """
        learning_style_str = f", adaptado al estilo de aprendizaje {learning_style}" if learning_style else ""
        
        prompt = f"""
        Crea una lección completa sobre "{topic}" en la materia de {subject} para un estudiante de nivel {level}{learning_style_str}.
        
        La lección debe incluir:
        1. Introducción al tema (objetivos de aprendizaje, relevancia)
        2. Conceptos clave explicados claramente
        3. Ejemplos y aplicaciones prácticas
        4. Visualizaciones o analogías para facilitar la comprensión
        5. Ejercicios de práctica con soluciones
        6. Resumen de los puntos principales
        7. Recursos adicionales recomendados
        
        Utiliza un lenguaje claro y adecuado al nivel del estudiante.
        """
        
        response = await self.process_message(prompt, context)
        
        # Extract the main components
        sections = self._extract_lesson_sections(response)
        
        return {
            "subject": subject,
            "topic": topic,
            "level": level,
            "learning_style": learning_style,
            "full_content": response,
            "sections": sections,
            "exercises": self._extract_exercises(response)
        }
    
    async def recommend_resources(self, subject: str, topics: List[str], level: str, resource_types: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recommend educational resources for specific topics.
        
        Args:
            subject: Subject area
            topics: List of topics
            level: Student's level
            resource_types: Types of resources to recommend
            context: Additional context about the student
            
        Returns:
            List of recommended resources
        """
        topics_str = ", ".join(topics)
        resource_types_str = ", ".join(resource_types) if resource_types else "libros, videos, artículos, ejercicios, aplicaciones"
        
        prompt = f"""
        Recomienda recursos educativos para estudiar los siguientes temas de {subject}: {topics_str}.
        
        Detalles:
        - Nivel del estudiante: {level}
        - Tipos de recursos a recomendar: {resource_types_str}
        
        Para cada recurso, proporciona:
        1. Título/nombre
        2. Tipo de recurso
        3. Breve descripción
        4. Por qué es útil para el estudiante
        5. Nivel de dificultad
        
        Organiza las recomendaciones por tema y tipo de recurso.
        """
        
        response = await self.process_message(prompt, context)
        
        # Parse the response to extract structured resources
        resources = self._parse_resources(response)
        
        return {
            "subject": subject,
            "topics": topics,
            "resource_types": resource_types,
            "resources": resources,
            "raw_recommendations": response
        }
    
    async def create_practice_material(self, subject: str, topic: str, level: str, material_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create practice material such as exercises, quizzes, etc.
        
        Args:
            subject: Subject area
            topic: Specific topic
            level: Student's level
            material_type: Type of material to create
            context: Additional context about the student
            
        Returns:
            Practice material
        """
        prompt = f"""
        Crea material de práctica tipo "{material_type}" sobre el tema "{topic}" de {subject} para un estudiante de nivel {level}.
        
        El material debe:
        1. Ser apropiado para el nivel del estudiante
        2. Cubrir los conceptos clave del tema
        3. Incluir instrucciones claras
        4. Proporcionar soluciones o respuestas
        5. Variar en dificultad (de más sencillo a más complejo)
        
        Estructura el material claramente con secciones bien definidas.
        """
        
        response = await self.process_message(prompt, context)
        
        return {
            "subject": subject,
            "topic": topic,
            "level": level,
            "material_type": material_type,
            "content": response,
            "structured_content": self._structure_practice_material(response, material_type)
        }
    
    async def adapt_content(self, content: str, target_level: str, target_style: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Adapt existing content to a different level or learning style.
        
        Args:
            content: Original content
            target_level: Target difficulty level
            target_style: Target learning style
            context: Additional context about the student
            
        Returns:
            Adapted content
        """
        prompt = f"""
        Adapta el siguiente contenido educativo a un nivel {target_level} y estilo de aprendizaje {target_style}:
        
        {content}
        
        Al adaptar el contenido:
        1. Ajusta el vocabulario y complejidad al nivel indicado
        2. Modifica el formato y presentación según el estilo de aprendizaje
        3. Añade o simplifica ejemplos según sea necesario
        4. Mantén los conceptos clave intactos
        5. Asegúrate de que el contenido siga siendo preciso y educativo
        """
        
        return await self.process_message(prompt, context)
    
    def _extract_lesson_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from lesson text."""
        sections = {
            "introduction": "",
            "key_concepts": "",
            "examples": "",
            "practice": "",
            "summary": "",
            "additional_resources": ""
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            lower_line = line.lower()
            
            # Detect section headers
            if "introduc" in lower_line or "objetivos" in lower_line:
                current_section = "introduction"
                sections[current_section] += line + "\n"
            elif any(phrase in lower_line for phrase in ["conceptos clave", "conceptos fundamentales", "conceptos principales"]):
                current_section = "key_concepts"
                sections[current_section] += line + "\n"
            elif "ejemplo" in lower_line or "aplicaci" in lower_line or "caso" in lower_line:
                current_section = "examples"
                sections[current_section] += line + "\n"
            elif "ejercicio" in lower_line or "práctica" in lower_line or "problema" in lower_line:
                current_section = "practice"
                sections[current_section] += line + "\n"
            elif "resumen" in lower_line or "conclusi" in lower_line:
                current_section = "summary"
                sections[current_section] += line + "\n"
            elif "recurso" in lower_line or "adicional" in lower_line or "lectura" in lower_line:
                current_section = "additional_resources"
                sections[current_section] += line + "\n"
            elif current_section:
                sections[current_section] += line + "\n"
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def _extract_exercises(self, text: str) -> List[Dict[str, Any]]:
        """Extract exercises from lesson text."""
        exercises = []
        exercise_section = False
        current_exercise = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
            
            # Detect exercise section
            if "ejercicio" in lower_line and not exercise_section:
                exercise_section = True
                continue
                
            if not exercise_section:
                continue
                
            # Detect new exercise
            if (line[0].isdigit() and line[1] in ['.', ')', ':']) or "ejercicio" in lower_line:
                if current_exercise:
                    exercises.append(current_exercise)
                
                current_exercise = {
                    "question": line,
                    "answer": ""
                }
            elif current_exercise:
                # Check for solution indicators
                if any(word in lower_line for word in ["solución", "respuesta", "solution", "answer"]):
                    current_exercise["answer"] = ""
                    continue
                    
                # Default to adding to question unless we've seen a solution indicator
                if "answer" in current_exercise and current_exercise["answer"]:
                    current_exercise["answer"] += line + "\n"
                else:
                    current_exercise["question"] += "\n" + line
        
        # Add the last exercise
        if current_exercise:
            exercises.append(current_exercise)
            
        # Clean up
        for exercise in exercises:
            exercise["question"] = exercise["question"].strip()
            exercise["answer"] = exercise["answer"].strip()
            
        return exercises
    
    def _parse_resources(self, text: str) -> List[Dict[str, Any]]:
        """Parse recommended resources into structured format."""
        resources = []
        current_resource = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for new resource (bullet points or numbered items)
            if line.startswith(('- ', '* ', '• ')) or (line[0].isdigit() and line[1] in ['.', ')', ':']):
                if current_resource and "title" in current_resource:
                    resources.append(current_resource)
                    
                current_resource = {
                    "title": line.lstrip('- *•0123456789.) '),
                    "type": "",
                    "description": "",
                    "relevance": "",
                    "difficulty": ""
                }
            elif current_resource:
                lower_line = line.lower()
                
                # Try to detect what kind of information this line contains
                if any(word in lower_line for word in ["tipo:", "type:", "recurso:"]):
                    current_resource["type"] = line.split(":", 1)[1].strip()
                elif any(word in lower_line for word in ["descripción:", "description:", "acerca de:"]):
                    current_resource["description"] = line.split(":", 1)[1].strip()
                elif any(word in lower_line for word in ["utilidad:", "relevancia:", "por qué:"]):
                    current_resource["relevance"] = line.split(":", 1)[1].strip()
                elif any(word in lower_line for word in ["dificultad:", "nivel:", "difficulty:"]):
                    current_resource["difficulty"] = line.split(":", 1)[1].strip()
                else:
                    # If we can't determine the type, add to description
                    current_resource["description"] += " " + line
        
        # Add the last resource
        if current_resource and "title" in current_resource:
            resources.append(current_resource)
            
        # Clean up
        for resource in resources:
            for key in resource:
                if isinstance(resource[key], str):
                    resource[key] = resource[key].strip()
                    
        return resources
    
    def _structure_practice_material(self, text: str, material_type: str) -> Dict[str, Any]:
        """Structure practice material based on its type."""
        if material_type.lower() in ["quiz", "cuestionario"]:
            return self._structure_quiz(text)
        elif material_type.lower() in ["worksheet", "hoja de trabajo", "ejercicios"]:
            return self._structure_worksheet(text)
        else:
            # Default generic structure
            return {
                "instructions": self._extract_section_by_header(text, ["instrucciones", "instructions"]),
                "content": text,
                "solutions": self._extract_section_by_header(text, ["soluciones", "solutions", "respuestas"])
            }
    
    def _structure_quiz(self, text: str) -> Dict[str, Any]:
        """Structure quiz content."""
        questions = []
        current_question = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect new question
            if (line[0].isdigit() and line[1] in ['.', ')', ':']) or line.lower().startswith("pregunta"):
                if current_question:
                    questions.append(current_question)
                    
                current_question = {
                    "question": line,
                    "options": [],
                    "answer": ""
                }
            elif current_question:
                lower_line = line.lower()
                
                # Detect options (typically a, b, c, d)
                if line[0].isalpha() and len(line) > 1 and line[1] in ['.', ')', ':']:
                    current_question["options"].append(line)
                
                # Detect answer
                elif "respuesta" in lower_line or "answer" in lower_line:
                    current_question["answer"] = line.split(":", 1)[1].strip() if ":" in line else ""
        
        # Add the last question
        if current_question:
            questions.append(current_question)
            
        return {
            "instructions": self._extract_section_by_header(text, ["instrucciones", "instructions"]),
            "questions": questions
        }
    
    def _structure_worksheet(self, text: str) -> Dict[str, Any]:
        """Structure worksheet content."""
        problems = []
        current_problem = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect new problem
            if (line[0].isdigit() and line[1] in ['.', ')', ':']) or line.lower().startswith(("problema", "ejercicio")):
                if current_problem:
                    problems.append(current_problem)
                    
                current_problem = {
                    "problem": line,
                    "solution": ""
                }
            elif current_problem:
                lower_line = line.lower()
                
                # Detect solution
                if "solución" in lower_line or "solution" in lower_line:
                    current_problem["solution"] = ""
                elif "solution" in current_problem and current_problem["solution"]:
                    current_problem["solution"] += line + "\n"
                else:
                    current_problem["problem"] += "\n" + line
        
        # Add the last problem
        if current_problem:
            problems.append(current_problem)
            
        # Clean up
        for problem in problems:
            problem["problem"] = problem["problem"].strip()
            problem["solution"] = problem["solution"].strip()
            
        return {
            "instructions": self._extract_section_by_header(text, ["instrucciones", "instructions"]),
            "problems": problems
        }
    
    def _extract_section_by_header(self, text: str, possible_headers: List[str]) -> str:
        """Extract a section from text based on possible header names."""
        lines = text.split('\n')
        section_content = ""
        in_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            lower_line = line.lower()
            
            # Check if this line contains a section header
            if any(header in lower_line for header in possible_headers) and not in_section:
                in_section = True
                if ":" in line:
                    section_content = line.split(":", 1)[1].strip() + "\n"
                continue
                
            # Check for next section header
            if in_section and i < len(lines) - 1:
                next_line = lines[i+1].strip().lower()
                if next_line and any(next_line.startswith(header) for header in ["instruc", "question", "problem", "ejercicio", "pregunta"]):
                    break
                    
            # Add content if in section
            if in_section:
                section_content += line + "\n"
                
        return section_content.strip()