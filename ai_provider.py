"""AI integration module for enhanced documentation generation.

This module provides interfaces to various AI providers (OpenAI, Anthropic, GitHub Models)
to generate high-quality documentation descriptions and improve docstring content.
"""

import os
from typing import Optional, Dict, Any
from config import config


class AIProvider:
    """Base class for AI provider integrations.
    
    This abstract base class defines the interface that all AI provider
    implementations must follow, ensuring consistent behavior across different
    AI services.
    """
    
    def generate_description(self, code_context: str, prompt: str) -> str:
        """Generate a description using AI based on code context.
        
        Args:
            code_context (str): The code snippet to analyze.
            prompt (str): The specific prompt for generation.
        
        Returns:
            str: Generated description.
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_description")


class OpenAIProvider(AIProvider):
    """OpenAI API integration for documentation generation.
    
    This class handles communication with OpenAI's API to generate
    intelligent documentation descriptions using GPT models.
    
    Attributes:
        api_key (str): OpenAI API key.
        model (str): Model identifier (e.g., 'gpt-4-turbo-preview').
        client: OpenAI client instance.
    """
    
    def __init__(self):
        """Initialize OpenAI provider with API key and model configuration.
        
        Raises:
            ValueError: If OPENAI_API_KEY is not set.
        """
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.openai_api_key)
            self.model = config.openai_model
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    def generate_description(self, code_context: str, prompt: str) -> str:
        """Generate description using OpenAI's API.
        
        Args:
            code_context (str): Source code to analyze.
            prompt (str): Instruction prompt for the AI.
        
        Returns:
            str: AI-generated description.
            
        Raises:
            Exception: If API call fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python documentation engineer. Generate clear, concise, and accurate docstring descriptions."},
                    {"role": "user", "content": f"{prompt}\n\nCode:\n{code_context}"}
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""


class AnthropicProvider(AIProvider):
    """Anthropic Claude API integration for documentation generation.
    
    This class handles communication with Anthropic's Claude API to generate
    intelligent documentation descriptions.
    
    Attributes:
        api_key (str): Anthropic API key.
        model (str): Model identifier (e.g., 'claude-3-sonnet-20240229').
        client: Anthropic client instance.
    """
    
    def __init__(self):
        """Initialize Anthropic provider with API key and model configuration.
        
        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set.
        """
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.anthropic_api_key)
            self.model = config.anthropic_model
        except ImportError:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    def generate_description(self, code_context: str, prompt: str) -> str:
        """Generate description using Anthropic's Claude API.
        
        Args:
            code_context (str): Source code to analyze.
            prompt (str): Instruction prompt for the AI.
        
        Returns:
            str: AI-generated description.
            
        Raises:
            Exception: If API call fails.
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nCode:\n{code_context}"
                    }
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return ""


class GitHubModelsProvider(AIProvider):
    """GitHub Models API integration for documentation generation.
    
    This class provides access to AI models hosted on GitHub Models,
    offering a free alternative for documentation generation.
    
    Attributes:
        token (str): GitHub personal access token.
        endpoint (str): API endpoint for GitHub Models.
    """
    
    def __init__(self):
        """Initialize GitHub Models provider with authentication token.
        
        Raises:
            ValueError: If GITHUB_TOKEN is not set.
        """
        if not config.github_token:
            raise ValueError("GITHUB_TOKEN not set in environment")
        
        self.token = config.github_token
        self.endpoint = "https://models.inference.ai.azure.com"
        
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.endpoint,
                api_key=self.token
            )
        except ImportError:
            raise ImportError("OpenAI library required for GitHub Models")
    
    def generate_description(self, code_context: str, prompt: str) -> str:
        """Generate description using GitHub Models API.
        
        Args:
            code_context (str): Source code to analyze.
            prompt (str): Instruction prompt for the AI.
        
        Returns:
            str: AI-generated description.
            
        Raises:
            Exception: If API call fails.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # GitHub Models default
                messages=[
                    {"role": "system", "content": "You are an expert Python documentation engineer."},
                    {"role": "user", "content": f"{prompt}\n\nCode:\n{code_context}"}
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"GitHub Models API error: {e}")
            return ""


def get_ai_provider() -> Optional[AIProvider]:
    """Factory function to get the appropriate AI provider based on configuration.
    
    Returns:
        Optional[AIProvider]: Initialized AI provider instance, or None if AI is disabled
            or no valid provider is configured.
    
    Raises:
        Exception: If provider initialization fails.
    """
    if not config.enable_ai:
        return None
    
    provider_name = config.get_available_provider()
    
    if provider_name == 'openai':
        return OpenAIProvider()
    elif provider_name == 'anthropic':
        return AnthropicProvider()
    elif provider_name == 'github':
        return GitHubModelsProvider()
    else:
        print("Warning: No AI provider configured. Using rule-based generation.")
        return None


def enhance_description_with_ai(code_snippet: str, base_description: str, 
                                 element_type: str) -> str:
    """Enhance a basic description using AI to make it more professional.
    
    This function takes a rule-based description and uses AI to improve
    its clarity, completeness, and professional tone.
    
    Args:
        code_snippet (str): The actual code being documented.
        base_description (str): Initial rule-based description.
        element_type (str): Type of code element ('function', 'class', 'method').
    
    Returns:
        str: Enhanced description, or original if AI enhancement fails.
    """
    provider = get_ai_provider()
    
    if not provider:
        return base_description
    
    prompt = f"""Improve this {element_type} description to be more clear and professional.
Keep it concise (1-2 sentences). Focus on WHAT it does and WHY it exists.

Current description: {base_description}

Provide only the improved description, nothing else."""
    
    enhanced = provider.generate_description(code_snippet, prompt)
    
    return enhanced if enhanced else base_description
