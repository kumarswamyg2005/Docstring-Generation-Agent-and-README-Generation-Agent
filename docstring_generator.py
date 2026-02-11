"""Docstring Generator Agent - PEP-257 Compliant Documentation Generator.

This module implements an intelligent agent that automatically generates
high-quality docstrings for Python functions, classes, and methods following
PEP-257 standards and industry best practices.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils import (
    read_python_file,
    parse_python_code,
    extract_function_info,
    extract_class_info,
    calculate_complexity_score,
    is_special_method,
    format_type_annotation
)
from ai_provider import enhance_description_with_ai
from config import config


class DocstringGenerator:
    """Main agent for generating Python docstrings.
    
    This agent analyzes Python source code using AST parsing and generates
    comprehensive docstrings following PEP-257 standards. It supports multiple
    docstring styles (Google, NumPy, Sphinx) and can optionally use AI to
    enhance descriptions.
    
    Attributes:
        style (str): Docstring style to use ('google', 'numpy', 'sphinx').
        use_ai (bool): Whether to use AI enhancement for descriptions.
        stats (Dict[str, int]): Statistics about generation process.
    """
    
    def __init__(self, style: str = 'google', use_ai: bool = True):
        """Initialize the docstring generator.
        
        Args:
            style (str): Docstring style ('google', 'numpy', or 'sphinx').
            use_ai (bool): Enable AI-powered description enhancement.
            
        Raises:
            ValueError: If style is not supported.
        """
        if style not in ['google', 'numpy', 'sphinx']:
            raise ValueError(f"Unsupported docstring style: {style}")
        
        self.style = style
        self.use_ai = use_ai
        self.stats = {
            'functions_processed': 0,
            'classes_processed': 0,
            'methods_processed': 0,
            'errors': 0
        }
    
    def generate_for_file(self, file_path: Path) -> Optional[str]:
        """Generate docstrings for all elements in a Python file.
        
        This method reads a Python file, parses it, and generates docstrings
        for all functions, classes, and methods that don't already have adequate
        documentation.
        
        Args:
            file_path (Path): Path to the Python source file.
        
        Returns:
            Optional[str]: Modified source code with generated docstrings,
                or None if file cannot be processed.
        
        Raises:
            IOError: If file cannot be read.
            SyntaxError: If Python code has syntax errors.
        """
        print(f"\n📄 Processing: {file_path.name}")
        
        source_code = read_python_file(file_path)
        if source_code is None:
            self.stats['errors'] += 1
            return None
        
        # Check for empty file
        if not source_code.strip():
            print("   ⚠️  Empty file, skipping...")
            return source_code
        
        tree = parse_python_code(source_code)
        if tree is None:
            print("   ❌ Syntax error, attempting best-effort processing...")
            self.stats['errors'] += 1
            return source_code
        
        # Process all top-level definitions
        modified_source = source_code
        
        # Collect all nodes to process (with their line numbers)
        nodes_to_process = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_nested(node, tree):
                    nodes_to_process.append(('function', node, node.lineno))
            
            elif isinstance(node, ast.ClassDef):
                nodes_to_process.append(('class', node, node.lineno))
                
                # Collect methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        nodes_to_process.append(('method', item, item.lineno))
        
        # Sort by line number in REVERSE order (bottom to top)
        # This ensures insertions don't affect line numbers of nodes we haven't processed
        nodes_to_process.sort(key=lambda x: x[2], reverse=True)
        
        # Process nodes from bottom to top
        for node_type, node, _ in nodes_to_process:
            if node_type == 'function':
                modified_source = self._add_function_docstring(
                    modified_source, node, source_code
                )
                self.stats['functions_processed'] += 1
            
            elif node_type == 'class':
                modified_source = self._add_class_docstring(
                    modified_source, node, source_code
                )
                self.stats['classes_processed'] += 1
            
            elif node_type == 'method':
                modified_source = self._add_function_docstring(
                    modified_source, node, source_code, is_method=True
                )
                self.stats['methods_processed'] += 1
        
        return modified_source
    
    def _is_nested(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if a function is nested inside another function or class.
        
        Args:
            node (ast.FunctionDef): Function node to check.
            tree (ast.Module): Full AST tree.
        
        Returns:
            bool: True if function is nested (inside another function or class), False if top-level.
        """
        for parent in ast.walk(tree):
            # Check if inside another function
            if isinstance(parent, ast.FunctionDef) and parent != node:
                if node in ast.walk(parent):
                    return True
            # Check if inside a class (i.e., it's a method)
            if isinstance(parent, ast.ClassDef):
                if node in ast.walk(parent):
                    return True
        return False
    
    def _add_function_docstring(self, source: str, node: ast.FunctionDef, 
                                original_source: str, is_method: bool = False) -> str:
        """Add or update docstring for a function.
        
        Args:
            source (str): Current source code.
            node (ast.FunctionDef): Function AST node.
            original_source (str): Original unmodified source.
            is_method (bool): Whether this is a class method.
        
        Returns:
            str: Modified source code with docstring added.
        """
        # Check if docstring already exists
        existing_docstring = ast.get_docstring(node)
        if existing_docstring and len(existing_docstring) > 20:
            print(f"   ✓ {node.name} - already documented")
            return source
        
        # Extract function info
        func_info = extract_function_info(node)
        
        # Generate docstring
        docstring = self._generate_function_docstring(func_info, is_method, original_source)
        
        # Insert docstring into source
        lines = source.split('\n')
        
        # node.lineno is 1-indexed, but list is 0-indexed
        # We want to insert AFTER the def line (which is at node.lineno - 1 in 0-indexed array)
        def_line_index = node.lineno - 1
        
        # Find the line that ends with ':' (could be multi-line function def)
        insert_index = def_line_index
        while insert_index < len(lines) and ':' not in lines[insert_index]:
            insert_index += 1
        
        # Insert after the ':' line
        insert_index += 1
        
        # Get indentation from the def line
        base_indent = self._get_indentation(lines[def_line_index])
        
        # Add proper indentation to docstring (one level deeper than def)
        docstring_lines = docstring.split('\n')
        indented_docstring = '\n'.join(
            [f"{base_indent}    {line}" if line.strip() else "" 
             for line in docstring_lines]
        )
        
        # Insert the docstring
        lines.insert(insert_index, indented_docstring)
        
        print(f"   ✅ Generated docstring for: {node.name}")
        return '\n'.join(lines)
    
    def _add_class_docstring(self, source: str, node: ast.ClassDef, 
                            original_source: str) -> str:
        """Add or update docstring for a class.
        
        Args:
            source (str): Current source code.
            node (ast.ClassDef): Class AST node.
            original_source (str): Original unmodified source.
        
        Returns:
            str: Modified source code with docstring added.
        """
        existing_docstring = ast.get_docstring(node)
        if existing_docstring and len(existing_docstring) > 20:
            print(f"   ✓ {node.name} - already documented")
            return source
        
        class_info = extract_class_info(node)
        docstring = self._generate_class_docstring(class_info, original_source)
        
        lines = source.split('\n')
        
        # node.lineno is 1-indexed, convert to 0-indexed
        class_line_index = node.lineno - 1
        
        # Find the line that ends with ':' (class definition)
        insert_index = class_line_index
        while insert_index < len(lines) and ':' not in lines[insert_index]:
            insert_index += 1
        
        # Insert after the ':' line
        insert_index += 1
        
        # Get base indentation
        base_indent = self._get_indentation(lines[class_line_index])
        
        # Add proper indentation to docstring
        docstring_lines = docstring.split('\n')
        indented_docstring = '\n'.join(
            [f"{base_indent}    {line}" if line.strip() else ""
             for line in docstring_lines]
        )
        
        # Insert the docstring
        lines.insert(insert_index, indented_docstring)
        
        print(f"   ✅ Generated docstring for class: {node.name}")
        return '\n'.join(lines)
    
    def _generate_function_docstring(self, func_info: Dict[str, Any], 
                                    is_method: bool, source: str) -> str:
        """Generate docstring content for a function.
        
        Args:
            func_info (Dict[str, Any]): Function metadata from AST.
            is_method (bool): Whether this is a class method.
            source (str): Original source code for AI enhancement.
        
        Returns:
            str: Generated docstring in the specified style.
        """
        if self.style == 'google':
            return self._generate_google_style(func_info, is_method, source)
        elif self.style == 'numpy':
            return self._generate_numpy_style(func_info, is_method, source)
        else:
            return self._generate_sphinx_style(func_info, is_method, source)
    
    def _generate_class_docstring(self, class_info: Dict[str, Any], source: str) -> str:
        """Generate docstring content for a class.
        
        Args:
            class_info (Dict[str, Any]): Class metadata from AST.
            source (str): Original source code for AI enhancement.
        
        Returns:
            str: Generated docstring in the specified style.
        """
        name = class_info['name']
        bases = class_info['bases']
        attributes = class_info['attributes']
        
        # Generate base description
        base_desc = f"{name} class"
        if bases:
            base_desc += f" extending {', '.join(bases)}"
        base_desc += "."
        
        # Enhance with AI if enabled
        if self.use_ai:
            class_snippet = f"class {name}({', '.join(bases)}):"
            base_desc = enhance_description_with_ai(class_snippet, base_desc, 'class')
        
        if self.style == 'google':
            doc = f'"""{base_desc}\n'
            
            if attributes:
                doc += '\n    Attributes:\n'
                for attr in attributes:
                    attr_type = format_type_annotation(attr['annotation'])
                    doc += f"        {attr['name']} ({attr_type}): Description of {attr['name']}.\n"
            
            doc += '    """'
            return doc
        
        # Similar logic for numpy and sphinx styles
        return f'"""{base_desc}"""'
    
    def _generate_google_style(self, func_info: Dict[str, Any], 
                               is_method: bool, source: str) -> str:
        """Generate Google-style docstring.
        
        Args:
            func_info (Dict[str, Any]): Function metadata.
            is_method (bool): Whether this is a method.
            source (str): Source code for context.
        
        Returns:
            str: Google-style formatted docstring.
        """
        name = func_info['name']
        args = func_info['args']
        returns = func_info['returns']
        
        # Generate brief description
        if is_special_method(name):
            brief = self._get_special_method_description(name)
        else:
            brief = f"{name.replace('_', ' ').capitalize()}."
            
            if self.use_ai:
                func_snippet = f"def {name}({', '.join([a['name'] for a in args])}):"
                brief = enhance_description_with_ai(func_snippet, brief, 'function')
        
        doc = f'"""{brief}\n'
        
        # Add arguments section
        if args:
            # Filter out 'self' and 'cls' for methods
            filtered_args = [arg for arg in args 
                            if arg['name'] not in ['self', 'cls']]
            
            if filtered_args:
                doc += '\n    Args:\n'
                for arg in filtered_args:
                    arg_type = format_type_annotation(arg['annotation'])
                    doc += f"        {arg['name']} ({arg_type}): Description of {arg['name']}.\n"
        
        # Add returns section
        if returns:
            doc += '\n    Returns:\n'
            doc += f"        {returns}: Description of return value.\n"
        
        doc += '    """'
        return doc
    
    def _generate_numpy_style(self, func_info: Dict[str, Any], 
                             is_method: bool, source: str) -> str:
        """Generate NumPy-style docstring.
        
        Args:
            func_info (Dict[str, Any]): Function metadata.
            is_method (bool): Whether this is a method.
            source (str): Source code for context.
        
        Returns:
            str: NumPy-style formatted docstring.
        """
        name = func_info['name']
        args = func_info['args']
        returns = func_info['returns']
        
        brief = f"{name.replace('_', ' ').capitalize()}."
        
        doc = f'"""{brief}\n\n'
        
        if args:
            filtered_args = [arg for arg in args if arg['name'] not in ['self', 'cls']]
            if filtered_args:
                doc += '    Parameters\n'
                doc += '    ----------\n'
                for arg in filtered_args:
                    doc += f"    {arg['name']} : {format_type_annotation(arg['annotation'])}\n"
                    doc += f"        Description of {arg['name']}\n"
        
        if returns:
            doc += '\n    Returns\n'
            doc += '    -------\n'
            doc += f"    {returns}\n"
            doc += '        Description of return value\n'
        
        doc += '    """'
        return doc
    
    def _generate_sphinx_style(self, func_info: Dict[str, Any], 
                               is_method: bool, source: str) -> str:
        """Generate Sphinx-style docstring.
        
        Args:
            func_info (Dict[str, Any]): Function metadata.
            is_method (bool): Whether this is a method.
           source (str): Source code for context.
        
        Returns:
            str: Sphinx-style formatted docstring.
        """
        name = func_info['name']
        args = func_info['args']
        returns = func_info['returns']
        
        brief = f"{name.replace('_', ' ').capitalize()}."
        
        doc = f'"""{brief}\n'
        
        if args:
            filtered_args = [arg for arg in args if arg['name'] not in ['self', 'cls']]
            for arg in filtered_args:
                doc += f'\n    :param {arg["name"]}: Description of {arg["name"]}'
                if arg.get('annotation'):
                    doc += f'\n    :type {arg["name"]}: {format_type_annotation(arg["annotation"])}'
        
        if returns:
            doc += f'\n    :return: Description of return value'
            doc += f'\n    :rtype: {returns}'
        
        doc += '\n    """'
        return doc
    
    def _get_special_method_description(self, method_name: str) -> str:
        """Get standard description for Python special methods.
        
        Args:
            method_name (str): Name of the special method.
        
        Returns:
            str: Standard description for the method.
        """
        descriptions = {
            '__init__': 'Initialize a new instance.',
            '__str__': 'Return a string representation.',
            '__repr__': 'Return a detailed string representation for debugging.',
            '__len__': 'Return the length.',
            '__getitem__': 'Get an item by key or index.',
            '__setitem__': 'Set an item by key or index.',
            '__delitem__': 'Delete an item by key or index.',
            '__iter__': 'Return an iterator.',
            '__next__': 'Get the next item from the iterator.',
            '__enter__': 'Enter the context manager.',
            '__exit__': 'Exit the context manager.',
            '__call__': 'Make the instance callable.',
            '__eq__': 'Check equality with another object.',
            '__lt__': 'Check if less than another object.',
            '__gt__': 'Check if greater than another object.',
        }
        return descriptions.get(method_name, f'{method_name} special method.')
    
    def _get_indentation(self, line: str) -> str:
        """Extract indentation from a line of code.
        
        Args:
            line (str): Line of code.
        
        Returns:
            str: Whitespace indentation string.
        """
        return line[:len(line) - len(line.lstrip())]
    
    def process_directory(self, directory: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Process all Python files in a directory recursively.
        
        Args:
            directory (Path): Root directory to process.
            output_dir (Optional[Path]): Directory to save modified files.
                If None, overwrites original files.
        
        Returns:
            Dict[str, Any]: Processing statistics and results.
        """
        from utils import get_all_python_files
        
        python_files = get_all_python_files(directory)
        
        if not python_files:
            print("No Python files found.")
            return {'files_processed': 0}
        
        print(f"\n🔍 Found {len(python_files)} Python files\n")
        
        results = []
        
        for file_path in python_files:
            modified_source = self.generate_for_file(file_path)
            
            if modified_source:
                if output_dir:
                    # Maintain directory structure in output
                    relative_path = file_path.relative_to(directory)
                    output_path = output_dir / relative_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = file_path
                
                # Write modified source
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(modified_source)
                
                results.append({
                    'file': str(file_path),
                    'output': str(output_path),
                    'success': True
                })
        
        return {
            'files_processed': len(results),
            'statistics': self.stats,
            'results': results
        }
    
    def print_statistics(self):
        """Print generation statistics to console."""
        print("\n" + "="*50)
        print("📊 DOCSTRING GENERATION STATISTICS")
        print("="*50)
        print(f"Functions processed: {self.stats['functions_processed']}")
        print(f"Classes processed:   {self.stats['classes_processed']}")
        print(f"Methods processed:   {self.stats['methods_processed']}")
        print(f"Errors encountered:  {self.stats['errors']}")
        print("="*50 + "\n")
