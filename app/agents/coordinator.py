"""
Coordinator agent implementation for the learning platform.
"""
from typing import Dict, Any, Optional, List
import json
from .base import BaseAgent

class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that manages the learning experience.
    
    This agent serves as the main entry point and router to specialized agents.
    """
    
    def __init__(self):
        super().__init__("Coordinador de Aprendizaje")
        
        self.system_prompt = """
        Eres el Coordinador de Aprendizaje, el agente principal que gestiona la experiencia educativa.
        
        Tus responsabilidades incluyen:
        1. Evaluar el nivel de conocimiento del estudiante
        2. Comprender sus objetivos y necesidades de aprendizaje
        3. Derivar consultas específicas a agentes especializados cuando sea apropiado
        4. Proporcionar una visión general del progreso del estudiante
        5. Recomendar caminos de aprendizaje personalizados
        
        Cuando te presenten una consulta, primero determina si debes:
        - Responder directamente si es una pregunta general sobre la plataforma o el proceso de aprendizaje
        - Sugerir un agente especializado si la consulta requiere conocimiento profundo en una materia específica
        - Solicitar más información si la consulta es ambigua
        
        Mantén un tono motivador y centrado en el estudiante, destacando siempre su progreso y potencial.
        """
    
    async def evaluate_student_level(self, subject: str, student_responses: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a student's level in a specific subject based on their responses.
        
        Args:
            subject: The subject being evaluated
            student_responses: List of student responses to assessment questions
            context: Additional context about the student
            
        Returns:
            Evaluation results with level assessment and recommendations
        """
        # Format prompt for evaluation
        prompt = f"""
        Evalúa el nivel de conocimiento del estudiante en {subject} basado en sus respuestas.
        
        Respuestas del estudiante:
        {json.dumps(student_responses, ensure_ascii=False, indent=2)}
        
        Por favor, proporciona:
        1. Una evaluación del nivel actual (principiante, intermedio, avanzado)
        2. Fortalezas identificadas
        3. Áreas específicas que necesitan mejora
        4. Recomendaciones personalizadas para avanzar
        5. Próximos temas sugeridos
        """
        
        response = await self.process_message(prompt, context)
        
        # Extract structured information from response
        # This is a simplified implementation - in a real system you might use more robust parsing
        level = "principiante"
        if "intermedio" in response.lower():
            level = "intermedio"
        elif "avanzado" in response.lower():
            level = "avanzado"
        
        # Extract recommendations (look for numbered items or bullet points)
        recommendations = []
        for line in response.split('\n'):
            if any(line.strip().startswith(prefix) for prefix in ['- ', '* ', '• ', '1. ', '2. ', '3. ']):
                clean_line = line.strip().lstrip('- *•123456789. ')
                if clean_line and len(clean_line) > 5:  # Minimal validation
                    recommendations.append(clean_line)
        
        return {
            "subject": subject,
            "level": level,
            "full_assessment": response,
            "recommendations": recommendations[:5],  # Limit to 5 recommendations
            "next_steps": self._extract_next_steps(response)
        }
    
    async def create_learning_path(self, subject: str, level: str, goals: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a personalized learning path for a student.
        
        Args:
            subject: The subject for the learning path
            level: Student's current level in the subject
            goals: List of student's learning goals
            context: Additional context about the student
            
        Returns:
            Structured learning path with topics and resources
        """
        # Format prompt for learning path creation
        prompt = f"""
        Crea una ruta de aprendizaje personalizada para un estudiante de nivel {level} en {subject}.
        
        Objetivos del estudiante:
        {json.dumps(goals, ensure_ascii=False, indent=2)}
        
        La ruta de aprendizaje debe incluir:
        1. Secuencia lógica de temas (5-7 temas)
        2. Para cada tema, proporciona:
           - Breve descripción
           - Conceptos clave que deben dominarse
           - Recursos recomendados (lecturas, videos, ejercicios)
           - Un hito de evaluación para verificar el aprendizaje
        3. Tiempo estimado para completar cada etapa
        
        Adapta la ruta a las preferencias y nivel del estudiante.
        """
        
        response = await self.process_message(prompt, context)
        
        # Parse the response to extract structured data
        # This is simplified - a real implementation would have more robust parsing
        topics = self._extract_topics_from_learning_path(response)
        
        return {
            "subject": subject,
            "student_level": level,
            "full_path": response,
            "topics": topics,
            "estimated_completion_time": self._extract_time_estimate(response)
        }
    
    def _extract_next_steps(self, text: str) -> List[str]:
        """Extract next steps recommendations from text."""
        next_steps = []
        in_next_steps_section = False
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check if we've reached the next steps section
            if any(phrase in line.lower() for phrase in ['próximos temas', 'próximos pasos', 'siguientes pasos']):
                in_next_steps_section = True
                continue
                
            # If we're in the next steps section and find a list item, add it
            if in_next_steps_section and line and any(line.startswith(prefix) for prefix in ['- ', '* ', '• ', '1. ', '2. ']):
                clean_line = line.lstrip('- *•123456789. ')
                next_steps.append(clean_line)
                
            # If we find a new section heading, stop collecting next steps
            if in_next_steps_section and line and line.endswith(':') and not any(line.startswith(prefix) for prefix in ['- ', '* ', '• ']):
                in_next_steps_section = False
        
        return next_steps
    
    def _extract_topics_from_learning_path(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured topics from learning path text."""
        topics = []
        current_topic = None
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for new topic (typically numbered or with a heading pattern)
            if line[0].isdigit() and line[1] in ['.', ')', ':'] or line.startswith('Tema '):
                if current_topic:
                    topics.append(current_topic)
                
                current_topic = {
                    "title": line.lstrip('0123456789.) Tema:'),
                    "description": "",
                    "key_concepts": [],
                    "resources": [],
                    "evaluation": ""
                }
                current_section = "description"
                
            elif current_topic:
                # Check for section headers
                lower_line = line.lower()
                if any(phrase in lower_line for phrase in ['conceptos clave', 'conceptos fundamentales']):
                    current_section = "key_concepts"
                elif any(phrase in lower_line for phrase in ['recursos', 'materiales', 'lecturas']):
                    current_section = "resources"
                elif any(phrase in lower_line for phrase in ['evaluación', 'hito', 'verificación']):
                    current_section = "evaluation"
                # Add content to the current section
                elif current_section == "description":
                    current_topic["description"] += line + " "
                elif current_section == "key_concepts" and line.startswith(('- ', '* ', '• ')):
                    current_topic["key_concepts"].append(line.lstrip('- *•'))
                elif current_section == "resources" and line.startswith(('- ', '* ', '• ')):
                    current_topic["resources"].append(line.lstrip('- *•'))
                elif current_section == "evaluation":
                    current_topic["evaluation"] += line + " "
        
        # Add the last topic if there is one
        if current_topic:
            topics.append(current_topic)
            
        return topics
    
    def _extract_time_estimate(self, text: str) -> str:
        """Extract time estimate from learning path text."""
        for line in text.split('\n'):
            line = line.lower().strip()
            if any(phrase in line for phrase in ['tiempo estimado', 'duración', 'completar en']):
                return line
        return "Tiempo estimado no especificado"