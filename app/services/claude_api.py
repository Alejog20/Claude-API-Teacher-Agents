"""
Client for interacting with Claude's API.
"""
import anthropic
from typing import Dict, Any, List, Optional
import json
import asyncio

from app.utils.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("claude_api")

class ClaudeClient:
    """
    Client for interacting with Claude's API.
    """
    
    def __init__(self, api_key=None, model=None):
        """
        Initialize the Claude client.
        
        Args:
            api_key: API key for Claude (default: from settings)
            model: Model to use (default: from settings)
        """
        self.api_key = api_key or settings.CLAUDE_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        
        logger.info(f"Claude client initialized with model {self.model}")
    
    async def generate_response(
        self, 
        message: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        previous_messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response using Claude's API.
        
        Args:
            message: The user's message
            system_prompt: System prompt for Claude
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            previous_messages: Previous conversation messages
            
        Returns:
            Claude's response
        """
        try:
            # Prepare messages
            messages = previous_messages or []
            if not previous_messages:
                messages.append({"role": "user", "content": message})
            
            # Use default system prompt if none provided
            system = system_prompt or "You are a helpful, harmless, and honest AI assistant."
            
            # Call the API
            response = await self.client.messages.create(
                model=self.model,
                system=system,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            logger.info(f"Generated response with {response.usage.output_tokens} tokens")
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def batch_process(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[str]:
        """
        Process multiple prompts concurrently.
        
        Args:
            prompts: List of prompts to process
            system_prompt: System prompt to use for all requests
            max_concurrent: Maximum number of concurrent requests
            
        Returns:
            List of responses
        """
        # Create a semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_prompt(prompt):
            async with semaphore:
                return await self.generate_response(prompt, system_prompt)
        
        # Process all prompts concurrently
        tasks = [process_prompt(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Error processing prompt {i}: {str(response)}")
                processed_responses.append(f"Error: {str(response)}")
            else:
                processed_responses.append(response)
        
        return processed_responses
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text using Claude.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis (e.g., "sentiment", "topics", "complexity")
            criteria: Specific criteria to analyze
            
        Returns:
            Analysis results
        """
        criteria_str = "\n".join([f"- {criterion}" for criterion in criteria]) if criteria else ""
        
        prompt = f"""
        Please analyze the following text for {analysis_type}.
        
        {f"Analyze based on these criteria:\n{criteria_str}" if criteria else ""}
        
        Text to analyze:
        ---
        {text}
        ---
        
        Provide a structured analysis with clear sections and numerical ratings where applicable.
        """
        
        response = await self.generate_response(
            message=prompt,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500
        )
        
        return {
            "analysis_type": analysis_type,
            "text_analyzed": text[:100] + "..." if len(text) > 100 else text,
            "full_analysis": response,
            "criteria": criteria
        }