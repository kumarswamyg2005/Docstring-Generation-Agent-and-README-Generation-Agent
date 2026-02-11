"""README Generator Agent - Intelligent Project Documentation Generator.

This module implements an agent that analyzes entire Python projects and
generates comprehensive, professional README.md files suitable for production use.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from utils import read_python_file, parse_python_code, get_all_python_files
from ai_provider import get_ai_provider
from config import config


class READMEGenerator:
    """Agent for generating comprehensive project README files.
    
    This agent performs deep analysis of project structure, code relationships,
    dependencies, and functionality to generate informative README documentation
    that helps developers understand and use the project.
    
    Attributes:
        project_root (Path): Root directory of the project.
        use_ai (bool): Whether to use AI for enhanced descriptions.
        analysis (Dict): Stores project analysis results.
    """
    
    def __init__(self, project_root: Path, use_ai: bool = True):
        """Initialize the README generator.
        
        Args:
            project_root (Path): Path to project root directory.
            use_ai (bool): Enable AI-enhanced description generation.
        """
        self.project_root = Path(project_root)
        self.use_ai = use_ai
        self.analysis = {
            'files': [],
            'entry_points': [],
            'dependencies': set(),
            'classes': [],
            'functions': [],
            'imports': defaultdict(list),
            'file_purposes': {},
            'structure': {}
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis.
        
        This method scans all Python files, analyzes their structure,
        relationships, dependencies, and infers the project's purpose
        and architecture.
        
        Returns:
            Dict[str, Any]: Complete project analysis including file structure,
                dependencies, entry points, and component relationships.
        """
        print(f"\n🔍 Analyzing project: {self.project_root.name}\n")
        
        python_files = get_all_python_files(self.project_root)
        
        if not python_files:
            print("⚠️  No Python files found in project.")
            return self.analysis
        
        print(f"Found {len(python_files)} Python files")
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Identify entry points
        self._identify_entry_points()
        
        # Build project structure tree
        self._build_structure_tree()
        
        print("✅ Analysis complete\n")
        
        return self.analysis
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file.
        
        Extracts imports, classes, functions, and attempts to infer
        the file's purpose in the project.
        
        Args:
            file_path (Path): Path to the Python file to analyze.
        """
        source = read_python_file(file_path)
        if not source:
            return
        
        tree = parse_python_code(source)
        if not tree:
            return
        
        relative_path = file_path.relative_to(self.project_root)
        file_info = {
            'path': str(relative_path),
            'full_path': str(file_path),
            'name': file_path.name,
            'classes': [],
            'functions': [],
            'imports': [],
            'has_main': False,
            'lines': len(source.split('\n'))
        }
        
        # Analyze AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._add_dependency(alias.name)
                    file_info['imports'].append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._add_dependency(node.module)
                    file_info['imports'].append(node.module)
            
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                file_info['classes'].append(class_name)
                self.analysis['classes'].append({
                    'name': class_name,
                    'file': str(relative_path),
                    'docstring': ast.get_docstring(node)
                })
            
            elif isinstance(node, ast.FunctionDef):
                func_name = node.name
                file_info['functions'].append(func_name)
                
                # Check for main execution
                if func_name == 'main':
                    file_info['has_main'] = True
                
                self.analysis['functions'].append({
                    'name': func_name,
                    'file': str(relative_path),
                    'docstring': ast.get_docstring(node)
                })
        
        # Check for if __name__ == '__main__'
        if "if __name__ == '__main__'" in source or 'if __name__ == "__main__"' in source:
            file_info['has_main'] = True
        
        # Infer file purpose
        file_info['purpose'] = self._infer_file_purpose(file_path, file_info)
        
        self.analysis['files'].append(file_info)
        self.analysis['file_purposes'][str(relative_path)] = file_info['purpose']
    
    def _add_dependency(self, module_name: str):
        """Add a dependency to the analysis.
        
        Filters out standard library modules and extracts third-party dependencies.
        
        Args:
            module_name (str): Name of the imported module.
        """
        # Filter standard library (basic list)
        stdlib_modules = {
            'os', 'sys', 'pathlib', 'typing', 'ast', 'json', 'pickle',
            'collections', 'itertools', 'functools', 're', 'math', 'random',
            'datetime', 'time', 'logging', 'argparse', 'subprocess', 'io'
        }
        
        base_module = module_name.split('.')[0]
        
        if base_module not in stdlib_modules and not base_module.startswith('_'):
            self.analysis['dependencies'].add(base_module)
    
    def _infer_file_purpose(self, file_path: Path, file_info: Dict) -> str:
        """Infer the purpose of a file based on its name and content.
        
        Args:
            file_path (Path): Path to the file.
            file_info (Dict): Analysis information about the file.
        
        Returns:
            str: Inferred purpose description.
        """
        name = file_path.stem.lower()
        
        # Common patterns
        if name == 'main' or name == '__main__' or file_info['has_main']:
            return 'Main entry point for the application'
        elif name == 'config' or name == 'settings':
            return 'Configuration and settings management'
        elif name == 'utils' or name == 'helpers':
            return 'Utility functions and helper methods'
        elif name.endswith('_test') or name.startswith('test_'):
            return 'Test cases and unit tests'
        elif name == 'models':
            return 'Data models and class definitions'
        elif 'agent' in name:
            return 'AI agent implementation'
        elif 'generator' in name:
            return 'Code or content generation logic'
        elif 'parser' in name or 'analyzer' in name:
            return 'Code parsing and analysis'
        elif name == 'cli' or name == 'command':
            return 'Command-line interface'
        elif 'api' in name:
            return 'API endpoints and handlers'
        elif 'database' in name or 'db' in name:
            return 'Database operations and models'
        else:
            # Make a guess based on classes/functions
            if file_info['classes']:
                main_class = file_info['classes'][0]
                return f'Implementation of {main_class} and related functionality'
            elif file_info['functions']:
                return f'Core functions for {name.replace("_", " ")}'
            else:
                return 'Supporting module'
    
    def _identify_entry_points(self):
        """Identify potential entry points in the project."""
        for file_info in self.analysis['files']:
            if file_info['has_main']:
                self.analysis['entry_points'].append(file_info['path'])
    
    def _build_structure_tree(self):
        """Build a hierarchical structure representation of the project."""
        structure = {}
        
        for file_info in self.analysis['files']:
            parts = Path(file_info['path']).parts
            current = structure
            
            for i, part in enumerate(parts):
                if part not in current:
                    if i == len(parts) - 1:  # File
                        current[part] = {
                            '_type': 'file',
                            '_purpose': file_info['purpose']
                        }
                    else:  # Directory
                        current[part] = {'_type': 'directory'}
                current = current.get(part, {})
        
        self.analysis['structure'] = structure
    
    def generate_readme(self, output_path: Optional[Path] = None) -> str:
        """Generate a comprehensive README.md file.
        
        Args:
            output_path (Optional[Path]): Path where README should be saved.
                If None, returns content without saving.
        
        Returns:
            str: Generated README content in Markdown format.
        """
        # Ensure analysis is complete
        if not self.analysis['files']:
            self.analyze_project()
        
        print("📝 Generating README.md...\n")
        
        readme_content = self._build_readme_content()
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"✅ README generated: {output_path}\n")
        
        return readme_content
    
    def _build_readme_content(self) -> str:
        """Build the complete README content following the specified structure.
        
        Returns:
            str: Complete README in Markdown format.
        """
        sections = []
        
        # Title
        project_name = self.project_root.name.replace('_', ' ').replace('-', ' ').title()
        sections.append(f"# {project_name}\n")
        
        # Description
        sections.append(self._generate_description())
        
        # Project Structure
        sections.append(self._generate_structure_section())
        
        # How It Works
        sections.append(self._generate_how_it_works())
        
        # Installation
        sections.append(self._generate_installation())
        
        # Usage
        sections.append(self._generate_usage())
        
        # Key Features
        sections.append(self._generate_features())
        
        # Edge Cases & Limitations
        sections.append(self._generate_edge_cases())
        
        # Technologies Used
        sections.append(self._generate_technologies())
        
        # Future Improvements
        sections.append(self._generate_future_improvements())
        
        # License
        sections.append(self._generate_license())
        
        return '\n'.join(sections)
    
    def _generate_description(self) -> str:
        """Generate project description section.
        
        Returns:
            str: Markdown formatted description.
        """
        desc = "## 📖 Project Description\n\n"
        
        # Try to infer project purpose from entry points and main classes
        if self.analysis['entry_points']:
            desc += f"This project is a Python application with entry points at "
            desc += f"{', '.join(self.analysis['entry_points'])}. "
        
        # Use AI if available to generate better description
        if self.use_ai and self.analysis['files']:
            provider = get_ai_provider()
            if provider:
                context = f"Project: {self.project_root.name}\n"
                context += f"Files: {len(self.analysis['files'])}\n"
                context += f"Main components: {', '.join([c['name'] for c in self.analysis['classes'][:5]])}\n"
                
                prompt = """Generate a 2-3 sentence project description explaining:
1. What problem this project solves
2. Who would use it
3. Key capability

Be professional and concise."""
                
                ai_desc = provider.generate_description(context, prompt)
                if ai_desc:
                    desc += ai_desc + "\n\n"
                    return desc
        
        # Fallback description
        desc += f"This project contains {len(self.analysis['files'])} Python modules "
        desc += f"implementing {len(self.analysis['classes'])} classes and "
        desc += f"{len(self.analysis['functions'])} functions.\n\n"
        
        return desc
    
    def _generate_structure_section(self) -> str:
        """Generate project structure section.
        
        Returns:
            str: Markdown formatted structure tree.
        """
        section = "## 🗂 Project Structure\n\n"
        section += "```\n"
        section += f"{self.project_root.name}/\n"
        
        for file_info in sorted(self.analysis['files'], key=lambda x: x['path']):
            path_parts = Path(file_info['path']).parts
            indent = "│   " * (len(path_parts) - 1)
            section += f"{indent}├── {file_info['name']:<20} # {file_info['purpose']}\n"
        
        section += "```\n\n"
        return section
    
    def _generate_how_it_works(self) -> str:
        """Generate 'How It Works' section.
        
        Returns:
            str: Markdown formatted workflow description.
        """
        section = "## ⚙️ How It Works\n\n"
        
        if self.analysis['entry_points']:
            section += "### Execution Flow\n\n"
            for i, entry_point in enumerate(self.analysis['entry_points'], 1):
                section += f"{i}. **Entry Point**: `{entry_point}`\n"
                
                # Find file info
                file_info = next((f for f in self.analysis['files'] if f['path'] == entry_point), None)
                if file_info:
                    section += f"   - {file_info['purpose']}\n"
                    if file_info['classes']:
                        section += f"   - Uses classes: {', '.join(file_info['classes'])}\n"
            
            section += "\n"
        
        section += "### Component Interaction\n\n"
        section += "The project components work together as follows:\n\n"
        
        for file_info in self.analysis['files']:
            if file_info['classes'] or file_info['functions']:
                section += f"- **{file_info['name']}**: {file_info['purpose']}\n"
        
        section += "\n"
        return section
    
    def _generate_installation(self) -> str:
        """Generate installation instructions.
        
        Returns:
            str: Markdown formatted installation steps.
        """
        section = "## 🚀 Installation\n\n"
        section += "### Prerequisites\n\n"
        section += "- Python 3.8 or higher\n\n"
        
        section += "### Setup Steps\n\n"
        section += "1. Clone the repository:\n"
        section += "```bash\n"
        section += f"git clone <repository-url>\n"
        section += f"cd {self.project_root.name}\n"
        section += "```\n\n"
        
        if self.analysis['dependencies']:
            section += "2. Install dependencies:\n"
            section += "```bash\n"
            section += "pip install -r requirements.txt\n"
            section += "```\n\n"
            
            section += "   Required packages:\n"
            for dep in sorted(self.analysis['dependencies']):
                section += f"   - `{dep}`\n"
            section += "\n"
        
        # Check for .env
        env_file = self.project_root / '.env.example'
        if env_file.exists():
            section += "3. Configure environment variables:\n"
            section += "```bash\n"
            section += "cp .env.example .env\n"
            section += "# Edit .env with your configuration\n"
            section += "```\n\n"
        
        return section
    
    def _generate_usage(self) -> str:
        """Generate usage instructions.
        
        Returns:
            str: Markdown formatted usage examples.
        """
        section = "## ▶️ Usage\n\n"
        
        if self.analysis['entry_points']:
            section += "Run the application using:\n\n"
            for entry_point in self.analysis['entry_points']:
                section += "```bash\n"
                section += f"python {entry_point}\n"
                section += "```\n\n"
        else:
            section += "```bash\n"
            section += "python main.py  # Adjust based on your entry point\n"
            section += "```\n\n"
        
        return section
    
    def _generate_features(self) -> str:
        """Generate key features section.
        
        Returns:
            str: Markdown formatted feature list.
        """
        section = "## 🧠 Key Features\n\n"
        
        features = []
        
        # Infer features from classes and functions
        for class_info in self.analysis['classes'][:10]:  # Top 10 classes
            if class_info.get('docstring'):
                first_line = class_info['docstring'].split('\n')[0]
                features.append(f"- {first_line}")
            else:
                features.append(f"- {class_info['name']} implementation")
        
        if features:
            section += '\n'.join(features) + "\n\n"
        else:
            section += "- Modular Python architecture\n"
            section += "- Object-oriented design\n"
            section += "- Comprehensive functionality\n\n"
        
        return section
    
    def _generate_edge_cases(self) -> str:
        """Generate edge cases and limitations section.
        
        Returns:
            str: Markdown formatted edge cases.
        """
        section = "## ⚠️ Edge Cases & Limitations\n\n"
        
        section += "### Known Limitations\n\n"
        
        # Check for empty files
        empty_files = [f['path'] for f in self.analysis['files'] if f['lines'] < 5]
        if empty_files:
            section += f"- Some files are minimal or incomplete: {', '.join(empty_files)}\n"
        
        # Check for missing docstrings
        classes_without_docs = [c for c in self.analysis['classes'] if not c.get('docstring')]
        if classes_without_docs:
            section += f"- {len(classes_without_docs)} classes lack documentation\n"
        
        section += "\n"
        
        return section
    
    def _generate_technologies(self) -> str:
        """Generate technologies section.
        
        Returns:
            str: Markdown formatted technology list.
        """
        section = "## 🛠 Technologies Used\n\n"
        section += "- **Python 3.8+**\n"
        
        if self.analysis['dependencies']:
            section += "- **Key Libraries**:\n"
            for dep in sorted(self.analysis['dependencies']):
                section += f"  - {dep}\n"
        
        section += "\n"
        return section
    
    def _generate_future_improvements(self) -> str:
        """Generate future improvements section.
        
        Returns:
            str: Markdown formatted improvement suggestions.
        """
        section = "## 📌 Future Improvements\n\n"
        
        suggestions = []
        
        # Check for missing tests
        test_files = [f for f in self.analysis['files'] if 'test' in f['name'].lower()]
        if not test_files:
            suggestions.append("- Add comprehensive unit tests")
        
        # Check for documentation
        classes_without_docs = [c for c in self.analysis['classes'] if not c.get('docstring')]
        if classes_without_docs:
            suggestions.append("- Add docstrings to all classes and functions")
        
        # Generic suggestions
        suggestions.extend([
            "- Add error handling and logging",
            "- Implement configuration validation",
            "- Add performance optimization",
            "- Create user documentation and examples",
            "- Add CI/CD pipeline"
        ])
        
        section += '\n'.join(suggestions) + "\n\n"
        
        return section
    
    def _generate_license(self) -> str:
        """Generate license section.
        
        Returns:
            str: Markdown formatted license info.
        """
        section = "## 📄 License\n\n"
        
        # Check for LICENSE file
        license_file = self.project_root / 'LICENSE'
        if license_file.exists():
            section += "This project is licensed under the terms specified in the LICENSE file.\n\n"
        else:
            section += "No license file found. Please add appropriate licensing information.\n\n"
        
        return section
