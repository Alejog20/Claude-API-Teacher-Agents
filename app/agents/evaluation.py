"""
Evaluation agent for assessing student learning.
"""
from typing import Dict, Any, List, Optional
import json
from .base import BaseAgent

class EvaluationAgent(BaseAgent):
    """
    Agent specialized in creating assessments and evaluating student performance.
    """
    
    def __init__(self):
        super().__init__("Evaluador")
        
        self.system_prompt = """
        Eres el Evaluador, especializado en crear evaluaciones educativas y analizar el desempeño de los estudiantes.
        
        Tus responsabilidades incluyen:
        1. Crear evaluaciones personalizadas adaptadas al nivel del estudiante
        2. Generar preguntas claras y relevantes para medir la comprensión
        3. Evaluar respuestas con objetividad y precisión
        4. Proporcionar retroalimentación constructiva y específica
        5. Identificar conceptos erróneos y áreas que necesitan atención
        
        Al crear evaluaciones:
        - Asegúrate de cubrir conceptos fundamentales y aplicaciones prácticas
        - Varía el tipo de preguntas (selección múltiple, respuesta corta, problemas)
        - Equilibra la dificultad para evaluar diferentes niveles de dominio
        - Proporciona instrucciones claras y sin ambigüedades
        
        Tu objetivo es ayudar a medir con precisión el conocimiento de los estudiantes,
        identificando tanto sus fortalezas como sus áreas de mejora.
        """
    
    async def create_assessment(self, subject: str, topics: List[str], level: str, num_questions: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an assessment for given topics.
        
        Args:
            subject: Subject of the assessment
            topics: List of topics to cover
            level: Difficulty level
            num_questions: Number of questions to generate
            context: Additional context about the student
            
        Returns:
            Complete assessment with questions and answers
        """
        topics_str = ", ".join(topics)
        
        prompt = f"""
        Crea una evaluación sobre {subject}, enfocada en los siguientes temas: {topics_str}.
        
        Detalles:
        - Nivel de dificultad: {level}
        - Número de preguntas: {num_questions}
        - Incluye una mezcla de tipos de preguntas (selección múltiple, respuesta corta, problemas)
        
        Para cada pregunta proporciona:
        1. El enunciado claro de la pregunta
        2. Opciones (si es selección múltiple)
        3. La respuesta correcta
        4. Una breve explicación de por qué es la respuesta correcta
        
        Enumera las preguntas claramente y separa las secciones.
        """
        
        response = await self.process_message(prompt, context)
        
        # Parse the response to extract structured questions
        questions = self._parse_questions(response)
        
        return {
            "subject": subject,
            "topics": topics,
            "level": level,
            "questions": questions,
            "raw_assessment": response
        }
    
    async def evaluate_response(self, question: str, student_answer: str, correct_answer: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate a student's response to a question.
        
        Args:
            question: The question that was asked
            student_answer: Student's answer
            correct_answer: The correct answer
            context: Additional context about the student
            
        Returns:
            Evaluation with feedback
        """
        prompt = f"""
        Evalúa la siguiente respuesta de un estudiante:
        
        Pregunta: {question}
        
        Respuesta correcta: {correct_answer}
        
        Respuesta del estudiante: {student_answer}
        
        Por favor, proporciona:
        1. ¿Es correcta la respuesta? (Sí/No/Parcialmente)
        2. Puntuación (0-100)
        3. Retroalimentación específica sobre qué hizo bien el estudiante
        4. Identificación de errores o conceptos erróneos
        5. Sugerencias para mejorar
        """
        
        response = await self.process_message(prompt, context)
        
        # Parse the evaluation
        is_correct = "no"
        if "sí" in response.lower() or "correcta" in response.lower():
            is_correct = "yes"
        elif "parcialmente" in response.lower():
            is_correct = "partially"
        
        # Extract score - look for numbers followed by % or /100
        score = 0
        import re
        score_matches = re.findall(r'(\d+)(?:%|\/100)', response)
        if score_matches:
            score = int(score_matches[0])
        
        return {
            "is_correct": is_correct,
            "score": score,
            "feedback": response,
            "question": question,
            "student_answer": student_answer,
            "correct_answer": correct_answer
        }
    
    async def analyze_assessment_results(self, assessment_results: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze the results of a complete assessment.
        
        Args:
            assessment_results: List of question/answer/evaluation results
            context: Additional context about the student
            
        Returns:
            Comprehensive analysis of the assessment
        """
        results_str = json.dumps(assessment_results, ensure_ascii=False, indent=2)
        
        prompt = f"""
        Analiza los siguientes resultados de evaluación:
        
        {results_str}
        
        Proporciona:
        1. Puntuación total y porcentaje de aciertos
        2. Fortalezas demostradas
        3. Áreas que necesitan mejora
        4. Conceptos específicos que el estudiante parece no entender
        5. Recomendaciones concretas para mejorar
        6. Sugerencias para el próximo tema de estudio
        """
        
        response = await self.process_message(prompt, context)
        
        # Calculate overall score
        if assessment_results:
            total_score = sum(result.get("score", 0) for result in assessment_results)
            average_score = total_score / len(assessment_results)
        else:
            average_score = 0
        
        return {
            "overall_score": average_score,
            "full_analysis": response,
            "strengths": self._extract_section(response, "Fortalezas"),
            "areas_for_improvement": self._extract_section(response, "Áreas"),
            "recommendations": self._extract_section(response, "Recomendaciones")
        }
    
    def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
        """Parse questions from assessment text."""
        questions = []
        current_question = None
        current_section = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for new question (typically numbered)
            if (line[0].isdigit() and line[1] in ['.', ')', ':']) or line.lower().startswith('pregunta'):
                if current_question:
                    questions.append(current_question)
                
                current_question = {
                    "text": line,
                    "options": [],
                    "correct_answer": "",
                    "explanation": ""
                }
                current_section = "text"
            
            elif current_question:
                # Check for options/answers/explanation sections
                lower_line = line.lower()
                
                # Option lines typically start with a letter followed by a delimiter
                if line and line[0].isalpha() and len(line) > 1 and line[1] in ['.', ')', ':']: 
                    current_question["options"].append(line)
                    current_section = "options"
                    
                elif any(phrase in lower_line for phrase in ['respuesta correcta:', 'correct answer:', 'respuesta:']):
                    current_section = "correct_answer"
                    continue
                    
                elif any(phrase in lower_line for phrase in ['explicación:', 'explanation:', 'justificación:']):
                    current_section = "explanation"
                    continue
                
                # Add content to the current section
                elif current_section == "text" and not current_question["options"]:
                    current_question["text"] += "\n" + line
                elif current_section == "correct_answer":
                    current_question["correct_answer"] += line + " "
                elif current_section == "explanation":
                    current_question["explanation"] += line + " "
        
        # Add the last question
        if current_question:
            questions.append(current_question)
            
        # Clean up the data
        for question in questions:
            question["text"] = question["text"].strip()
            question["correct_answer"] = question["correct_answer"].strip()
            question["explanation"] = question["explanation"].strip()
        
        return questions
    
    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """Extract a section from the analysis text."""
        lines = text.split('\n')
        section_content = []
        in_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section header
            if section_name.lower() in line.lower() and ":" in line:
                in_section = True
                continue
            
            # Check for next section header
            if in_section and ":" in line and any(char.isupper() for char in line[0:2]):
                break
                
            # Add content if in the target section
            if in_section and line.startswith(("- ", "* ", "• ", "1. ", "2. ")):
                section_content.append(line.lstrip("- *•123456789. "))
        
        return section_content