"""Configuration management for the documentation agents.

This module handles loading environment variables and configuration
settings for both the Docstring Generator and README Generator agents.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the documentation generation system.
    
    This class manages all configuration settings including AI model selection,
    API keys, and generation preferences. It follows the singleton pattern to
    ensure consistent configuration across the application.
    
    Attributes:
        openai_api_key (str): API key for OpenAI services.
        anthropic_api_key (str): API key for Anthropic services.
        github_token (str): GitHub token for accessing GitHub Models.
        openai_model (str): OpenAI model identifier.
        anthropic_model (str): Anthropic model identifier.
        docstring_style (str): Preferred docstring format (google/numpy/sphinx).
        enable_ai (bool): Whether to use AI enhancement for documentation.
        max_tokens (int): Maximum tokens for AI generation.
        temperature (float): Temperature parameter for AI generation.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # AI Provider Settings
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
        self.github_token: Optional[str] = os.getenv('GITHUB_TOKEN')
        
        # Model Selection
        self.openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.anthropic_model: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        # Documentation Settings
        self.docstring_style: str = os.getenv('DEFAULT_DOCSTRING_STYLE', 'google')
        self.enable_ai: bool = os.getenv('ENABLE_AI_ENHANCEMENT', 'true').lower() == 'true'
        self.max_tokens: int = int(os.getenv('MAX_TOKENS', '4000'))
        self.temperature: float = float(os.getenv('TEMPERATURE', '0.3'))
        
        # Project Paths
        self.project_root: Path = Path(__file__).parent
        self.output_dir: Path = self.project_root / 'output'
        self.output_dir.mkdir(exist_ok=True)
    
    def get_available_provider(self) -> Optional[str]:
        """Determine which AI provider is available based on API keys.
        
        Returns:
            str: Name of available provider ('openai', 'anthropic', 'github', or None).
            
        Raises:
            ValueError: If no valid API key is configured.
        """
        if self.openai_api_key:
            return 'openai'
        elif self.anthropic_api_key:
            return 'anthropic'
        elif self.github_token:
            return 'github'
        else:
            return None
    
    def validate(self) -> bool:
        """Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if self.enable_ai and not self.get_available_provider():
            return False
        
        if self.docstring_style not in ['google', 'numpy', 'sphinx']:
            return False
            
        return True


# Global configuration instance
config = Config()
