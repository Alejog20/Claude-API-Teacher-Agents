"""
Coordination service for managing interactions between agents.
"""
from typing import Dict, Any, List, Optional
import asyncio
import json

from app.agents import create_agent
from app.services.claude_api import ClaudeClient
from app.utils.logger import setup_logger

logger = setup_logger("coordination")

class CoordinationService:
    """
    Service for coordinating interactions between different agents.
    
    This service manages the flow of information between the coordinator agent
    and specialized agents to provide a cohesive learning experience.
    """
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.session_context = {}
        
    async def process_user_query(self, 
                                query: str, 
                                user_context: Dict[str, Any],
                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query using the appropriate agents.
        
        Args:
            query: The user's query text
            user_context: Context about the user (profile, progress, etc.)
            session_id: Optional session identifier for continuing conversations
            
        Returns:
            Response with agent output and metadata
        """
        # Initialize or retrieve session context
        context = self.session_context.get(session_id, {}) if session_id else {}
        context.update(user_context)
        
        # First, have the coordinator agent assess the query
        coordinator = create_agent("coordinator")
        assessment = await coordinator.process_message(
            f"Analyze this query and determine which specialized agent should handle it: {query}",
            context
        )
        
        # Parse the assessment to determine which agent to use
        agent_type = self._determine_agent_type(assessment, query)
        logger.info(f"Selected agent: {agent_type} for query: {query[:50]}...")
        
        # Get the specialized agent
        agent = create_agent(agent_type)
        
        # Process the query with the specialized agent
        response = await agent.process_message(query, context)
        
        # Update session context if session_id provided
        if session_id:
            context["last_query"] = query
            context["last_response"] = response
            context["last_agent"] = agent_type
            self.session_context[session_id] = context
        
        return {
            "response": response,
            "agent": agent_type,
            "assessment": assessment,
            "session_id": session_id
        }
    
    def _determine_agent_type(self, assessment: str, query: str) -> str:
        """
        Determine which agent type to use based on coordinator assessment.
        
        This uses keyword matching as a simple heuristic. In a production system,
        this could be replaced with a more sophisticated classifier.
        """
        assessment_lower = assessment.lower()
        query_lower = query.lower()
        
        # Check for explicit agent recommendations in the assessment
        if "matemática" in assessment_lower or "cálculo" in assessment_lower or "algebra" in assessment_lower:
            return "mathematics"
        elif "ciencia" in assessment_lower or "física" in assessment_lower or "química" in assessment_lower or "biología" in assessment_lower:
            return "science"
        elif "lenguaje" in assessment_lower or "gramática" in assessment_lower or "literatura" in assessment_lower or "escritura" in assessment_lower:
            return "language"
        elif "progreso" in assessment_lower or "avance" in assessment_lower or "rendimiento" in assessment_lower:
            return "feedback"
        
        # Fallback to checking the query itself
        if any(term in query_lower for term in ["matemática", "ecuación", "problema", "cálculo", "geometría", "estadística"]):
            return "mathematics"
        elif any(term in query_lower for term in ["ciencia", "física", "química", "biología", "experimento"]):
            return "science"
        elif any(term in query_lower for term in ["lenguaje", "gramática", "literatura", "escribir", "redacción"]):
            return "language"
        elif any(term in query_lower for term in ["progreso", "avance", "evaluación", "mejorar"]):
            return "feedback"
        
        # Default to coordinator if no specific agent is determined
        return "coordinator"
    
    async def get_learning_path(self, user_id: int, materia_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized learning path for a subject.
        
        Args:
            user_id: The user's ID
            materia_id: The subject ID
            context: Additional context (progress, evaluations, etc.)
            
        Returns:
            A structured learning path with recommendations
        """
        agent = create_agent("coordinator")
        
        prompt = f"""
        Genera una ruta de aprendizaje personalizada para la materia id={materia_id}.
        Considera el nivel actual del estudiante y su progreso existente.
        La ruta debe incluir:
        1. Una secuencia lógica de temas
        2. Recursos recomendados para cada tema
        3. Puntos de evaluación a lo largo del camino
        """
        
        response = await agent.process_message(prompt, context)
        
        # In a real implementation, we'd parse this into a structured format
        # For now, we'll return a simple structure
        return {
            "materia_id": materia_id,
            "user_id": user_id,
            "path": response,
            "raw_response": response
        }
    
    async def provide_feedback(self, 
                              evaluation_data: Dict[str, Any], 
                              user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide personalized feedback based on evaluation results.
        
        Args:
            evaluation_data: Data from a user's evaluation
            user_context: Context about the user
            
        Returns:
            Structured feedback with areas of improvement and recommendations
        """
        agent = create_agent("feedback")
        
        prompt = f"""
        Analiza los resultados de esta evaluación y proporciona retroalimentación personalizada.
        Identifica:
        1. Fortalezas demostradas
        2. Áreas específicas que necesitan mejora
        3. Recomendaciones concretas para mejorar
        4. Siguiente paso recomendado en el camino de aprendizaje
        
        Datos de la evaluación:
        {json.dumps(evaluation_data, ensure_ascii=False, indent=2)}
        """
        
        response = await agent.process_message(prompt, user_context)
        
        # Parse the response to extract structured feedback
        # In a real implementation, this would use a more robust parsing method
        strengths = []
        areas_improvement = []
        recommendations = []
        
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith(("Fortaleza", "Fortalezas", "Punto fuerte")):
                strengths.append(line)
            elif line.startswith(("Área", "Areas", "Aspecto a mejorar")):
                areas_improvement.append(line)
            elif line.startswith(("Recomendación", "Recomendamos", "Sugerencia")):
                recommendations.append(line)
        
        return {
            "evaluation_id": evaluation_data.get("id"),
            "full_feedback": response,
            "strengths": strengths,
            "areas_improvement": areas_improvement,
            "recommendations": recommendations
        }