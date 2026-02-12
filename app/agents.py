"""Agents for documentation generation.

This module contains agent classes that wrap the core documentation
generation functionality using the existing DocstringGenerator and
READMEGenerator classes.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import sys

# Add parent directory to path to import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from docstring_generator import DocstringGenerator
from readme_generator import READMEGenerator
from app.config import USE_AI_DEFAULT


class DocstringAgent:
    """Agent for generating Python docstrings.
    
    This agent wraps the DocstringGenerator to provide a clean interface
    for the FastAPI application.
    """
    
    def __init__(self, style: str = 'google', use_ai: bool = USE_AI_DEFAULT):
        """Initialize the docstring generation agent.
        
        Args:
            style: Docstring style ('google', 'numpy', or 'sphinx')
            use_ai: Whether to use AI enhancement
        """
        self.generator = DocstringGenerator(style=style, use_ai=use_ai)
    
    def process_file(self, file_path: Path) -> Optional[str]:
        """Process a single Python file and generate docstrings.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Modified source code with docstrings, or None if processing fails
        """
        return self.generator.generate_for_file(file_path)
    
    def process_directory(self, directory: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Process all Python files in a directory.
        
        Args:
            directory: Root directory to process
            output_dir: Directory to save modified files
            
        Returns:
            Processing statistics and results
        """
        return self.generator.process_directory(directory, output_dir)


class READMEAgent:
    """Agent for generating project README files.
    
    This agent wraps the READMEGenerator to provide a clean interface
    for the FastAPI application.
    """
    
    def __init__(self, project_root: Path, use_ai: bool = USE_AI_DEFAULT):
        """Initialize the README generation agent.
        
        Args:
            project_root: Root directory of the project
            use_ai: Whether to use AI enhancement
        """
        self.generator = READMEGenerator(project_root=project_root, use_ai=use_ai)
    
    def analyze_project(self):
        """Analyze the project structure and content."""
        self.generator.analyze_project()
    
    def generate_readme(self, output_path: Path):
        """Generate and save the README file.
        
        Args:
            output_path: Path where README.md will be saved
        """
        self.generator.generate_readme(output_path)
