"""
Base Agent Class
All agents inherit from this base class with LLM routing and common functionality
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from config.llm_config import llm_config, LLMProvider
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Provides LLM routing, logging, and common agent functionality.
    """
    
    def __init__(self, name: str, role: str, task_type: str = "general"):
        """
        Initialize base agent
        
        Args:
            name: Agent name (e.g., "CEO Agent")
            role: Agent role/description
            task_type: Preferred task type for LLM selection
        """
        self.name = name
        self.role = role
        self.task_type = task_type
        self.logger = logging.getLogger(f"agent.{name.lower().replace(' ', '_')}")
    
    def call_llm(
        self,
        prompt: str,
        provider: Optional[LLMProvider] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """
        Call LLM with automatic provider selection and fallback
        
        Args:
            prompt: The prompt to send
            provider: Specific provider to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        
        Returns:
            Generated text content
        """
        try:
            response = llm_config.call_llm(
                prompt=prompt,
                task_type=self.task_type,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            self.logger.debug(
                f"LLM call completed: {response['provider']} "
                f"({response['model']})"
            )
            
            return response["content"]
        
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def log_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log agent action"""
        message = f"{self.name}: {action}"
        if details:
            message += f" | Details: {details}"
        self.logger.info(message)
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate input data has required fields
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
        
        Returns:
            True if valid, raises ValueError if not
        """
        missing = [field for field in required_fields if field not in data or data[field] is None]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return True
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return output
        
        Args:
            input_data: Input data dictionary
        
        Returns:
            Output data dictionary
        """
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}')>"

