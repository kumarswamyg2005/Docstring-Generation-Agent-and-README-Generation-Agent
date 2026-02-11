#!/usr/bin/env python3
"""
Comprehensive test script to validate all functionality.

This script runs through various test scenarios to demonstrate
that both agents work correctly.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_imports():
    """Test that all modules can be imported."""
    console.print("\n[bold cyan]TEST 1: Module Imports[/bold cyan]")
    
    try:
        from config import config
        from utils import read_python_file, parse_python_code
        from ai_provider import AIProvider
        from docstring_generator import DocstringGenerator
        from readme_generator import READMEGenerator
        
        console.print("✅ All modules imported successfully", style="green")
        return True
    except Exception as e:
        console.print(f"❌ Import failed: {e}", style="red")
        return False


def test_configuration():
    """Test configuration loading."""
    console.print("\n[bold cyan]TEST 2: Configuration[/bold cyan]")
    
    try:
        from config import config
        
        console.print(f"   Docstring style: {config.docstring_style}")
        console.print(f"   AI enabled: {config.enable_ai}")
        console.print(f"   Max tokens: {config.max_tokens}")
        
        provider = config.get_available_provider()
        if provider:
            console.print(f"   AI provider: {provider}", style="green")
        else:
            console.print("   AI provider: None (rule-based mode)", style="yellow")
        
        console.print("✅ Configuration loaded", style="green")
        return True
    except Exception as e:
        console.print(f"❌ Configuration test failed: {e}", style="red")
        return False


def test_code_parsing():
    """Test code parsing utilities."""
    console.print("\n[bold cyan]TEST 3: Code Parsing[/bold cyan]")
    
    try:
        from utils import parse_python_code, extract_function_info, extract_class_info
        import ast
        
        # Test function parsing
        sample_code = """
def test_function(x: int, y: str) -> bool:
    return True

class TestClass:
    def method(self, value):
        pass
"""
        
        tree = parse_python_code(sample_code)
        assert tree is not None, "Failed to parse code"
        
        # Extract info
        func_count = 0
        class_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = extract_function_info(node)
                func_count += 1
            elif isinstance(node, ast.ClassDef):
                class_info = extract_class_info(node)
                class_count += 1
        
        console.print(f"   Parsed functions: {func_count}")
        console.print(f"   Parsed classes: {class_count}")
        console.print("✅ Code parsing works", style="green")
        return True
        
    except Exception as e:
        console.print(f"❌ Parsing test failed: {e}", style="red")
        return False


def test_docstring_generator():
    """Test the docstring generator."""
    console.print("\n[bold cyan]TEST 4: Docstring Generator[/bold cyan]")
    
    try:
        from docstring_generator import DocstringGenerator
        
        # Create generator (without AI for speed)
        generator = DocstringGenerator(style='google', use_ai=False)
        
        # Test on examples directory
        examples_dir = Path(__file__).parent / "examples"
        
        if not examples_dir.exists():
            console.print("⚠️  Examples directory not found, skipping test", style="yellow")
            return True
        
        # Process directory
        results = generator.process_directory(examples_dir, output_dir=None)
        
        console.print(f"   Files processed: {results['files_processed']}")
        console.print(f"   Functions: {results['statistics']['functions_processed']}")
        console.print(f"   Classes: {results['statistics']['classes_processed']}")
        console.print(f"   Methods: {results['statistics']['methods_processed']}")
        
        if results['files_processed'] > 0:
            console.print("✅ Docstring generator works", style="green")
            return True
        else:
            console.print("⚠️  No files processed", style="yellow")
            return False
            
    except Exception as e:
        console.print(f"❌ Docstring generator test failed: {e}", style="red")
        return False


def test_readme_generator():
    """Test the README generator."""
    console.print("\n[bold cyan]TEST 5: README Generator[/bold cyan]")
    
    try:
        from readme_generator import READMEGenerator
        
        # Test on current project
        project_root = Path(__file__).parent
        
        generator = READMEGenerator(project_root=project_root, use_ai=False)
        analysis = generator.analyze_project()
        
        console.print(f"   Files analyzed: {len(analysis['files'])}")
        console.print(f"   Classes found: {len(analysis['classes'])}")
        console.print(f"   Functions found: {len(analysis['functions'])}")
        console.print(f"   Dependencies: {len(analysis['dependencies'])}")
        console.print(f"   Entry points: {len(analysis['entry_points'])}")
        
        # Generate README content (don't save)
        readme_content = generator.generate_readme(output_path=None)
        
        if len(readme_content) > 100:
            console.print(f"   README length: {len(readme_content)} chars")
            console.print("✅ README generator works", style="green")
            return True
        else:
            console.print("⚠️  README too short", style="yellow")
            return False
            
    except Exception as e:
        console.print(f"❌ README generator test failed: {e}", style="red")
        return False


def test_docstring_styles():
    """Test different docstring styles."""
    console.print("\n[bold cyan]TEST 6: Docstring Styles[/bold cyan]")
    
    try:
        from docstring_generator import DocstringGenerator
        import ast
        from utils import extract_function_info
        
        # Sample function
        code = """
def sample(x: int, y: str) -> bool:
    return True
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        func_info = extract_function_info(func_node)
        
        # Test all styles
        styles_tested = []
        for style in ['google', 'numpy', 'sphinx']:
            gen = DocstringGenerator(style=style, use_ai=False)
            docstring = gen._generate_function_docstring(func_info, False, code)
            
            if docstring and len(docstring) > 20:
                styles_tested.append(style)
                console.print(f"   ✓ {style} style works")
        
        if len(styles_tested) == 3:
            console.print("✅ All docstring styles work", style="green")
            return True
        else:
            console.print(f"⚠️  Only {len(styles_tested)}/3 styles work", style="yellow")
            return False
            
    except Exception as e:
        console.print(f"❌ Style test failed: {e}", style="red")
        return False


def test_edge_cases():
    """Test edge case handling."""
    console.print("\n[bold cyan]TEST 7: Edge Case Handling[/bold cyan]")
    
    try:
        from utils import parse_python_code, read_python_file
        from pathlib import Path
        
        # Test empty code
        empty_result = parse_python_code("")
        assert empty_result is not None, "Should handle empty code"
        console.print("   ✓ Handles empty code")
        
        # Test syntax error
        bad_code = "def broken syntax here("
        error_result = parse_python_code(bad_code)
        assert error_result is None, "Should return None for bad syntax"
        console.print("   ✓ Handles syntax errors")
        
        # Test non-existent file
        fake_path = Path("/nonexistent/file.py")
        file_result = read_python_file(fake_path)
        assert file_result is None, "Should return None for missing files"
        console.print("   ✓ Handles missing files")
        
        console.print("✅ Edge case handling works", style="green")
        return True
        
    except Exception as e:
        console.print(f"❌ Edge case test failed: {e}", style="red")
        return False


def test_file_structure():
    """Test that all required files exist."""
    console.print("\n[bold cyan]TEST 8: File Structure[/bold cyan]")
    
    required_files = [
        "main.py",
        "docstring_generator.py",
        "readme_generator.py",
        "config.py",
        "utils.py",
        "ai_provider.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "QUICKSTART.md",
        "demo.py",
        "setup.py",
        "__init__.py"
    ]
    
    project_root = Path(__file__).parent
    missing_files = []
    
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
        else:
            console.print(f"   ✓ {file}")
    
    if not missing_files:
        console.print("✅ All required files present", style="green")
        return True
    else:
        console.print(f"⚠️  Missing files: {', '.join(missing_files)}", style="yellow")
        return False


def print_summary(results):
        """Print summary.
    
            Args:
                results (Any): Description of results.
            """
    """Print test summary."""
    console.print("\n" + "="*70)
    console.print("[bold cyan]TEST SUMMARY[/bold cyan]")
    console.print("="*70 + "\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test", style="cyan", width=30)
    table.add_column("Result", width=10)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        style = "green" if passed else "red"
        table.add_row(test_name, f"[{style}]{status}[/{style}]")
    
    console.print(table)
    
    # Calculate score
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    score = (passed / total) * 100
    
    console.print(f"\n[bold]Score: {passed}/{total} tests passed ({score:.1f}%)[/bold]\n")
    
    if score == 100:
        console.print("🎉 [bold green]PERFECT! All tests passed![/bold green]")
    elif score >= 80:
        console.print("✅ [bold green]EXCELLENT! System is working well.[/bold green]")
    elif score >= 60:
        console.print("⚠️  [bold yellow]GOOD. Some issues need attention.[/bold yellow]")
    else:
        console.print("❌ [bold red]NEEDS WORK. Multiple failures detected.[/bold red]")
        """Main.
            """
    
    console.print()


def main():
    """Run all tests."""
    console.print("[bold magenta]"
                 "\n╔═══════════════════════════════════════════════════════════╗\n"
                 "║       DOCUMENTATION GENERATOR - TEST SUITE               ║\n"
                 "╚═══════════════════════════════════════════════════════════╝"
                 "[/bold magenta]\n")
    
    results = {}
    
    # Run all tests
    results["Module Imports"] = test_imports()
    results["Configuration"] = test_configuration()
    results["Code Parsing"] = test_code_parsing()
    results["Docstring Generator"] = test_docstring_generator()
    results["README Generator"] = test_readme_generator()
    results["Docstring Styles"] = test_docstring_styles()
    results["Edge Cases"] = test_edge_cases()
    results["File Structure"] = test_file_structure()
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
