"""Utility functions for code analysis and documentation generation.

This module provides helper functions for parsing Python source code,
analyzing AST nodes, and extracting meaningful information for documentation.
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


def read_python_file(file_path: Path) -> Optional[str]:
    """Read a Python file and return its content.
    
    Args:
        file_path (Path): Path to the Python file.
    
    Returns:
        Optional[str]: File content as string, or None if file cannot be read.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def parse_python_code(source_code: str) -> Optional[ast.Module]:
    """Parse Python source code into an AST.
    
    Args:
        source_code (str): Python source code as string.
    
    Returns:
        Optional[ast.Module]: Parsed AST module, or None if parsing fails.
    """
    try:
        return ast.parse(source_code)
    except SyntaxError as e:
        print(f"Syntax error in code: {e}")
        return None


def extract_function_info(node: ast.FunctionDef) -> Dict[str, Any]:
    """Extract detailed information from a function AST node.
    
    Analyzes a function definition node and extracts parameters, return type,
    decorators, and other metadata useful for documentation generation.
    
    Args:
        node (ast.FunctionDef): AST node representing a function definition.
    
    Returns:
        Dict[str, Any]: Dictionary containing function metadata including:
            - name: Function name
            - args: List of argument information
            - returns: Return type annotation if present
            - decorators: List of decorator names
            - docstring: Existing docstring if present
            - lineno: Line number in source file
            - is_async: Whether function is async
    """
    info = {
        'name': node.name,
        'args': [],
        'returns': None,
        'decorators': [],
        'docstring': ast.get_docstring(node),
        'lineno': node.lineno,
        'is_async': isinstance(node, ast.AsyncFunctionDef)
    }
    
    # Extract arguments
    for arg in node.args.args:
        arg_info = {
            'name': arg.arg,
            'annotation': ast.unparse(arg.annotation) if arg.annotation else None
        }
        info['args'].append(arg_info)
    
    # Extract return type
    if node.returns:
        info['returns'] = ast.unparse(node.returns)
    
    # Extract decorators
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            info['decorators'].append(decorator.id)
        elif isinstance(decorator, ast.Call):
            info['decorators'].append(ast.unparse(decorator))
    
    return info


def extract_class_info(node: ast.ClassDef) -> Dict[str, Any]:
    """Extract detailed information from a class AST node.
    
    Args:
        node (ast.ClassDef): AST node representing a class definition.
    
    Returns:
        Dict[str, Any]: Dictionary containing class metadata including:
            - name: Class name
            - bases: List of base classes
            - methods: List of method information
            - attributes: List of class attributes
            - docstring: Existing docstring if present
            - lineno: Line number in source file
    """
    info = {
        'name': node.name,
        'bases': [],
        'methods': [],
        'attributes': [],
        'docstring': ast.get_docstring(node),
        'lineno': node.lineno
    }
    
    # Extract base classes
    for base in node.bases:
        info['bases'].append(ast.unparse(base))
    
    # Extract methods and attributes
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_info = extract_function_info(item)
            info['methods'].append(method_info)
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            attr_info = {
                'name': item.target.id,
                'annotation': ast.unparse(item.annotation) if item.annotation else None
            }
            info['attributes'].append(attr_info)
    
    return info


def get_all_python_files(directory: Path, exclude_dirs: List[str] = None) -> List[Path]:
    """Recursively find all Python files in a directory.
    
    Args:
        directory (Path): Root directory to search.
        exclude_dirs (List[str]): List of directory names to exclude (e.g., ['venv', '__pycache__']).
    
    Returns:
        List[Path]: List of paths to Python files.
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv', 'env', '__pycache__', '.git', 'node_modules', '.venv']
    
    python_files = []
    
    for item in directory.rglob('*.py'):
        # Check if any excluded directory is in the path
        if any(excluded in item.parts for excluded in exclude_dirs):
            continue
        python_files.append(item)
    
    return python_files


def infer_parameter_type(param_name: str, function_body: List[ast.stmt]) -> Optional[str]:
    """Attempt to infer parameter type from function body usage.
    
    This function performs basic static analysis to guess parameter types
    based on how they're used in the function body.
    
    Args:
        param_name (str): Name of the parameter to infer type for.
        function_body (List[ast.stmt]): List of AST statements in function body.
    
    Returns:
        Optional[str]: Inferred type as string, or None if cannot infer.
    """
    # This is a simplified implementation
    # In a production system, you'd use more sophisticated type inference
    
    for stmt in ast.walk(ast.Module(body=function_body)):
        # Check for string methods
        if isinstance(stmt, ast.Call):
            if isinstance(stmt.func, ast.Attribute):
                if isinstance(stmt.func.value, ast.Name) and stmt.func.value.id == param_name:
                    string_methods = ['split', 'strip', 'replace', 'format', 'join']
                    list_methods = ['append', 'extend', 'pop', 'remove']
                    dict_methods = ['get', 'keys', 'values', 'items']
                    
                    if stmt.func.attr in string_methods:
                        return 'str'
                    elif stmt.func.attr in list_methods:
                        return 'List'
                    elif stmt.func.attr in dict_methods:
                        return 'Dict'
    
    return None


def calculate_complexity_score(node: ast.FunctionDef) -> int:
    """Calculate a simple complexity score for a function.
    
    This helps determine if a function needs detailed documentation.
    Higher scores indicate more complex functions.
    
    Args:
        node (ast.FunctionDef): Function AST node.
    
    Returns:
        int: Complexity score (higher = more complex).
    """
    score = 0
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While)):
            score += 2
        elif isinstance(child, ast.Try):
            score += 3
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if child != node:  # Nested function
                score += 5
        elif isinstance(child, ast.ExceptHandler):
            score += 1
    
    # Consider length
    score += len(node.body)
    
    return score


def is_special_method(method_name: str) -> bool:
    """Check if a method is a Python special/magic method.
    
    Args:
        method_name (str): Name of the method.
    
    Returns:
        bool: True if method is a special method (e.g., __init__, __str__).
    """
    return method_name.startswith('__') and method_name.endswith('__')


def format_type_annotation(annotation: Optional[str]) -> str:
    """Format a type annotation for display in docstrings.
    
    Args:
        annotation (Optional[str]): Raw type annotation string.
    
    Returns:
        str: Formatted type annotation, or 'Any' if None.
    """
    if annotation is None:
        return 'Any'
    
    # Clean up common verbose annotations
    annotation = annotation.replace('typing.', '')
    
    return annotation
