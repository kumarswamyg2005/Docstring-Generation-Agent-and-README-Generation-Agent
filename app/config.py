"""Configuration management for the documentation generator."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Configuration
USE_AI_DEFAULT = os.getenv("USE_AI_DEFAULT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Application Configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
