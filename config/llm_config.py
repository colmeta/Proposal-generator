"""
Multi-LLM Configuration System
Supports OpenAI, Anthropic, Google Gemini, and Groq with automatic fallback
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum
import openai
from anthropic import Anthropic
import google.generativeai as genai
from groq import Groq


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"


class LLMConfig:
    """Configuration for multi-LLM support with fallback"""
    
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        # Anthropic Configuration
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        
        # Google Gemini Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        # Groq Configuration
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        
        # Provider priority order (fallback chain)
        self.provider_priority = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.GEMINI,
            LLMProvider.GROQ
        ]
        
        # Task-specific provider preferences
        self.task_providers = {
            "writing": LLMProvider.OPENAI,
            "strategy": LLMProvider.ANTHROPIC,
            "research": LLMProvider.GEMINI,
            "fast": LLMProvider.GROQ,
            "quality": LLMProvider.ANTHROPIC,
            "compliance": LLMProvider.ANTHROPIC,
        }
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self):
        """Initialize LLM client connections"""
        self.clients = {}
        
        if self.openai_api_key:
            self.clients[LLMProvider.OPENAI] = openai.OpenAI(api_key=self.openai_api_key)
        
        if self.anthropic_api_key:
            self.clients[LLMProvider.ANTHROPIC] = Anthropic(api_key=self.anthropic_api_key)
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.clients[LLMProvider.GEMINI] = genai
        
        if self.groq_api_key:
            self.clients[LLMProvider.GROQ] = Groq(api_key=self.groq_api_key)
    
    def get_provider_for_task(self, task_type: str) -> Optional[LLMProvider]:
        """Get preferred provider for a specific task type"""
        preferred = self.task_providers.get(task_type)
        
        if preferred and preferred in self.clients:
            return preferred
        
        # Fallback to first available provider
        for provider in self.provider_priority:
            if provider in self.clients:
                return provider
        
        return None
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers"""
        return list(self.clients.keys())
    
    def call_llm(
        self,
        prompt: str,
        task_type: str = "general",
        provider: Optional[LLMProvider] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call LLM with automatic fallback
        
        Args:
            prompt: The prompt to send
            task_type: Type of task (writing, strategy, research, etc.)
            provider: Specific provider to use (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Dict with 'content', 'provider', 'model', 'usage'
        """
        # Determine provider
        if provider is None:
            provider = self.get_provider_for_task(task_type)
        
        if provider is None:
            raise ValueError("No LLM provider available. Check API keys.")
        
        # Try primary provider, fallback on error
        for attempt_provider in [provider] + [p for p in self.provider_priority if p != provider]:
            if attempt_provider not in self.clients:
                continue
            
            try:
                return self._call_provider(
                    attempt_provider,
                    prompt,
                    temperature,
                    max_tokens,
                    **kwargs
                )
            except Exception as e:
                print(f"Error with {attempt_provider}: {e}")
                continue
        
        raise RuntimeError("All LLM providers failed")
    
    def _call_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Call specific provider"""
        client = self.clients[provider]
        
        if provider == LLMProvider.OPENAI:
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "provider": provider.value,
                "model": self.openai_model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        elif provider == LLMProvider.ANTHROPIC:
            response = client.messages.create(
                model=self.anthropic_model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return {
                "content": response.content[0].text,
                "provider": provider.value,
                "model": self.anthropic_model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        
        elif provider == LLMProvider.GEMINI:
            model = client.GenerativeModel(self.gemini_model)
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                **kwargs
            )
            return {
                "content": response.text,
                "provider": provider.value,
                "model": self.gemini_model,
                "usage": {}
            }
        
        elif provider == LLMProvider.GROQ:
            response = client.chat.completions.create(
                model=self.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "provider": provider.value,
                "model": self.groq_model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Global instance
llm_config = LLMConfig()

