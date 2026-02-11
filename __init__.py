"""
Documentation Generator Package

A comprehensive tool for automated Python documentation generation.
"""

__version__ = "1.0.0"
__author__ = " Epoch Hackathon "
__description__ = "Automated Docstring and README Generator"

from .docstring_generator import DocstringGenerator
from .readme_generator import READMEGenerator
from .config import config

__all__ = [
    'DocstringGenerator',
    'READMEGenerator',
    'config'
]
