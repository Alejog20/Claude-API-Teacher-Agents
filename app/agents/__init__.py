"""
Agent modules for the learning platform.
"""
from app.agents.base import (
    BaseAgent,
    CoordinatorAgent,
    SubjectAgent,
    FeedbackAgent,
    ContentAgent
)

def create_agent(agent_type, **kwargs):
    """
    Creates an instance of the specified agent type.
    
    Args:
        agent_type: Type of agent to create ('coordinator', 'subject', 'feedback', 'content')
        **kwargs: Additional arguments for the agent constructor
    
    Returns:
        An instance of the requested agent
    
    Raises:
        ValueError: If the agent type is not recognized
    """
    if agent_type == "coordinator":
        return CoordinatorAgent()
    elif agent_type == "mathematics" or agent_type == "science" or agent_type == "language":
        # These are all subject agents with different specialties
        return SubjectAgent(agent_type)
    elif agent_type == "feedback":
        return FeedbackAgent()
    elif agent_type == "content":
        return ContentAgent()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

__all__ = [
    'BaseAgent',
    'CoordinatorAgent',
    'SubjectAgent',
    'FeedbackAgent',
    'ContentAgent',
    'create_agent'
]