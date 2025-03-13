"""
Base agent classes and specialized agent implementations.
"""
import anthropic
import asyncio
from typing import Dict, Any, Optional, List
import json

from app.utils.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("agents")

class BaseAgent:
    """Base class for all agents in the platform."""
    
    def __init__(self, agent_name: str):
        """
        Initialize an agent with a name and default system prompt.
        
        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.model = settings.CLAUDE_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        
        # Default system prompt - will be overridden by subclasses
        self.system_prompt = f"""
        Eres {agent_name}, un agente especializado en una plataforma de aprendizaje adaptativo.
        Tu objetivo es proporcionar asistencia educativa personalizada y precisa.
        Usa un tono amigable, paciente y motivador en todo momento.
        Adapta tus explicaciones al nivel del estudiante y a su estilo de aprendizaje.
        """
        
        logger.info(f"Agent initialized: {agent_name}")
    
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a message and return a response.
        
        Args:
            message: The user's message
            context: Optional context about the user and conversation
            
        Returns:
            Agent's response
        """
        # Format system prompt with context if provided
        formatted_prompt = self._format_system_prompt(context)
        
        try:
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=formatted_prompt,
                messages=[{"role": "user", "content": message}]
            )
            
            response_text = response.content[0].text
            logger.info(f"Agent {self.agent_name} processed message successfully")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in agent {self.agent_name}: {str(e)}")
            return f"Lo siento, he tenido un problema al procesar tu mensaje. Detalles: {str(e)}"
    
    def _format_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format the system prompt with user context.
        
        Args:
            context: User context information
            
        Returns:
            Formatted system prompt
        """
        prompt = self.system_prompt
        
        if context:
            prompt += "\n\nContexto del estudiante:\n"
            for key, value in context.items():
                # Skip complex nested structures and convert them to a simple mention
                if isinstance(value, (dict, list)) and len(str(value)) > 100:
                    prompt += f"- {key}: [Datos disponibles]\n"
                else:
                    prompt += f"- {key}: {value}\n"
        
        return prompt
    
    async def set_student_context(self, profile: Dict[str, Any]) -> None:
        """
        Set student profile context for personalization.
        
        Args:
            profile: Student profile data
        """
        self.student_context = profile
    
    async def save_interaction(self, user_id: int, message: str, response: str, db) -> None:
        """
        Save the interaction to the database.
        
        Args:
            user_id: User's ID
            message: User's message
            response: Agent's response
            db: Database connection
        """
        async with db:
            await db.execute(
                """
                INSERT INTO interacciones (usuario_id, agente, tipo_interaccion, contenido)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, self.agent_name, "mensaje", f"Usuario: {message}\nAgente: {response}")
            )
            await db.commit()
            
        logger.info(f"Saved interaction for user {user_id} with agent {self.agent_name}")


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


class FeedbackAgent(BaseAgent):
    """
    Feedback agent that provides assessment and improvement suggestions.
    """
    
    def __init__(self):
        super().__init__("Analista de Progreso")
        
        self.system_prompt = """
        Eres el Analista de Progreso, especializado en evaluar el aprendizaje de los estudiantes
        y proporcionar retroalimentación constructiva y motivadora.
        
        Tus responsabilidades incluyen:
        1. Analizar patrones en el desempeño del estudiante
        2. Identificar fortalezas y áreas de mejora específicas
        3. Proporcionar comentarios constructivos y accionables
        4. Sugerir estrategias personalizadas para mejorar
        5. Mantener un tono positivo que motive al estudiante
        
        Al proporcionar retroalimentación:
        - Comienza reconociendo los logros y esfuerzos del estudiante
        - Sé específico sobre las áreas que necesitan mejora
        - Ofrece sugerencias prácticas y realizables
        - Adapta tus recomendaciones al nivel y estilo de aprendizaje del estudiante
        - Concluye con un mensaje motivador que inspire confianza
        
        Tu objetivo es ayudar al estudiante a desarrollar una mentalidad de crecimiento,
        viendo los desafíos como oportunidades para mejorar.
        """


class ContentAgent(BaseAgent):
    """
    Content agent that recommends and generates educational resources.
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