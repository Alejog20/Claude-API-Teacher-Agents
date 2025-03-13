"""
Specialized subject agents for the learning platform.
"""
from typing import Dict, Any, Optional, List
import json
from .base import BaseAgent

class SubjectAgent(BaseAgent):
    """
    Subject-specific agent that provides expertise in a particular field.
    """
    
    def __init__(self, subject: str):
        self.subject = subject
        
        # Map the subject code to a display name
        subject_names = {
            "mathematics": "Matemáticas",
            "science": "Ciencias",
            "language": "Lenguaje",
            "history": "Historia"
        }
        
        display_name = subject_names.get(subject, subject.capitalize())
        super().__init__(f"Especialista en {display_name}")
        
        # Subject-specific prompts
        subject_prompts = {
            "mathematics": """
            Eres el Especialista en Matemáticas, experto en todos los conceptos matemáticos desde
            aritmética básica hasta cálculo avanzado, álgebra, geometría, trigonometría y estadística.
            
            Al enseñar matemáticas:
            1. Proporciona explicaciones claras paso a paso
            2. Usa ejemplos concretos para ilustrar conceptos abstractos
            3. Conecta los conceptos con aplicaciones del mundo real
            4. Anticipa errores comunes y proporciona aclaraciones preventivas
            5. Sugiere múltiples enfoques para resolver problemas cuando sea apropiado
            
            Adapta tu nivel de explicación según el nivel indicado del estudiante, desde primaria
            hasta universidad. Siempre fomenta el razonamiento matemático y la comprensión conceptual
            por encima de la memorización de fórmulas.
            """,
            
            "science": """
            Eres el Especialista en Ciencias, con experiencia en física, química, biología y ciencias
            de la tierra.
            
            Al enseñar ciencias:
            1. Explica los fenómenos naturales de forma clara y accesible
            2. Relaciona los conceptos científicos con experiencias cotidianas
            3. Describe experimentos que demuestran los principios explicados
            4. Mantén la precisión científica sin sacrificar la claridad
            5. Fomenta el pensamiento crítico y el método científico
            
            Adapta tus explicaciones según el nivel del estudiante, utilizando analogías apropiadas
            y simplificando conceptos complejos sin introducir inexactitudes científicas. Promueve
            la curiosidad y el asombro por el mundo natural.
            """,
            
            "language": """
            Eres el Especialista en Lenguaje, experto en gramática, literatura, comprensión lectora, 
            escritura y comunicación efectiva.
            
            Al enseñar lenguaje:
            1. Proporciona explicaciones claras sobre reglas gramaticales y su aplicación
            2. Ofrece ejemplos concretos de uso correcto e incorrecto
            3. Ayuda en la interpretación y análisis de textos
            4. Guía el desarrollo de habilidades de escritura y expresión
            5. Apoya la apreciación literaria y el pensamiento crítico
            
            Adapta tu nivel según el estudiante, desde conceptos básicos hasta análisis literario avanzado.
            Fomenta una relación positiva con la lectura y la escritura, destacando su valor práctico
            y creativo.
            """,
            
            "history": """
            Eres el Especialista en Historia, experto en eventos históricos, civilizaciones, 
            movimientos sociales y análisis de contextos políticos y culturales.
            
            Al enseñar historia:
            1. Presenta los hechos históricos con precisión y contexto
            2. Explica las causas y consecuencias de eventos importantes
            3. Conecta eventos del pasado con situaciones contemporáneas
            4. Promueve la comprensión de diferentes perspectivas históricas
            5. Estimula el pensamiento crítico sobre fuentes y narrativas históricas
            
            Adapta tu nivel según el estudiante, desde presentaciones cronológicas básicas hasta 
            análisis historiográficos complejos. Fomenta una comprensión de la historia como algo 
            relevante para entender el presente y planificar el futuro.
            """
        }
        
        # Set the appropriate prompt for this subject
        self.system_prompt = subject_prompts.get(
            subject, 
            f"Eres el Especialista en {display_name}, experto en esta materia específica. Proporciona explicaciones claras y adaptadas al nivel del estudiante."
        )
    
    async def explain_concept(self, concept: str, level: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Explain a concept with depth appropriate to the student's level.
        
        Args:
            concept: The concept to explain
            level: Student's level (beginner, intermediate, advanced)
            context: Additional context about the student
            
        Returns:
            Explanation of the concept
        """
        prompt = f"""
        Explica el concepto de "{concept}" para un estudiante de nivel {level}.
        
        Tu explicación debe:
        1. Comenzar con una definición clara
        2. Incluir ejemplos concretos
        3. Relacionar el concepto con conocimientos previos
        4. Destacar aplicaciones prácticas
        5. Incluir analogías o visualizaciones si son apropiadas
        
        Adapta tu lenguaje y profundidad al nivel del estudiante.
        """
        
        return await self.process_message(prompt, context)
    
    async def solve_problem(self, problem: str, show_steps: bool, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Solve a subject-specific problem with explanation.
        
        Args:
            problem: The problem to solve
            show_steps: Whether to show detailed solution steps
            context: Additional context about the student
            
        Returns:
            Solution with explanation
        """
        prompt = f"""
        Resuelve el siguiente problema:
        
        {problem}
        
        {"Muestra todos los pasos detalladamente, explicando cada uno." if show_steps else "Proporciona la solución con una breve explicación."}
        """
        
        return await self.process_message(prompt, context)
    
    async def create_practice_exercises(self, topic: str, level: str, num_exercises: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create practice exercises for a specific topic.
        
        Args:
            topic: The topic for the exercises
            level: Difficulty level
            num_exercises: Number of exercises to generate
            context: Additional context about the student
            
        Returns:
            Generated exercises with solutions
        """
        prompt = f"""
        Crea {num_exercises} ejercicios de práctica sobre "{topic}" para un estudiante de nivel {level}.
        
        Para cada ejercicio:
        1. Proporciona un enunciado claro
        2. Incluye la solución completa
        3. Añade una breve explicación de la solución
        
        Adapta la dificultad al nivel del estudiante.
        Enumera los ejercicios claramente.
        """
        
        response = await self.process_message(prompt, context)
        
        # Parse the response to extract exercises and solutions
        exercises = self._parse_exercises_from_text(response, num_exercises)
        
        return {
            "topic": topic,
            "level": level,
            "exercises": exercises,
            "raw_response": response
        }
    
    def _parse_exercises_from_text(self, text: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse exercise text into structured format."""
        exercises = []
        current_exercise = None
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for new exercise (typically numbered)
            if (line[0].isdigit() and line[1] in ['.', ')', ':']) or line.lower().startswith('ejercicio'):
                if current_exercise:
                    exercises.append(current_exercise)
                
                current_exercise = {
                    "question": line,
                    "solution": "",
                    "explanation": ""
                }
                current_section = "question"
            
            elif current_exercise:
                # Check for solution/explanation sections
                lower_line = line.lower()
                if any(word in lower_line for word in ['solución:', 'solution:', 'respuesta:']):
                    current_section = "solution"
                    continue
                elif any(word in lower_line for word in ['explicación:', 'explanation:']):
                    current_section = "explanation"
                    continue
                
                # Add content to the current section
                if current_section == "question":
                    current_exercise["question"] += "\n" + line
                elif current_section == "solution":
                    current_exercise["solution"] += "\n" + line
                elif current_section == "explanation":
                    current_exercise["explanation"] += "\n" + line
        
        # Add the last exercise
        if current_exercise:
            exercises.append(current_exercise)
        
        # If we didn't find the expected number, do a simpler parsing
        if len(exercises) != expected_count:
            exercises = []
            sections = text.split(("Ejercicio", "Problema", "Exercise"))
            for i, section in enumerate(sections[1:]):  # Skip the first empty section
                exercises.append({
                    "question": f"Ejercicio {i+1}: {section.split('Solución:')[0].strip()}",
                    "solution": section.split('Solución:')[1].split('Explicación:')[0].strip() if 'Solución:' in section else "",
                    "explanation": section.split('Explicación:')[1].strip() if 'Explicación:' in section else ""
                })
        
        return exercises