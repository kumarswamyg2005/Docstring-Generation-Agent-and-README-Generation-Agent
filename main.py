"""Main entry point for the Documentation Generator System.

This module provides the command-line interface for running both the
Docstring Generator and README Generator agents.
"""

import sys
from pathlib import Path
from typing import Optional
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from docstring_generator import DocstringGenerator
from readme_generator import READMEGenerator
from config import config

console = Console()


def print_banner():
    """Display application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🏆 HACKATHON DOCUMENTATION GENERATOR 🏆               ║
║                                                               ║
║     Automated Docstring + README Generation System           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def validate_configuration() -> bool:
    """Validate that configuration is properly set up.
    
    Returns:
        bool: True if configuration is valid, False otherwise.
    """
    if not config.validate():
        console.print("❌ Configuration Error", style="bold red")
        console.print("\nPlease set up your configuration:")
        console.print("1. Copy .env.example to .env")
        console.print("2. Add your API key for AI enhancement")
        console.print("\nOr disable AI enhancement with --no-ai flag\n")
        return False
    return True


def generate_docstrings(directory: Path, style: str, use_ai: bool, 
                       output_dir: Optional[Path] = None) -> bool:
    """Run the docstring generation agent.
    
    Args:
        directory (Path): Project directory to process.
        style (str): Docstring style (google/numpy/sphinx).
        use_ai (bool): Whether to use AI enhancement.
        output_dir (Optional[Path]): Output directory for modified files.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    console.print(f"\n📚 Starting Docstring Generation", style="bold yellow")
    console.print(f"   Directory: {directory}")
    console.print(f"   Style: {style}")
    console.print(f"   AI Enhancement: {'Enabled' if use_ai else 'Disabled'}\n")
    
    try:
        generator = DocstringGenerator(style=style, use_ai=use_ai)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing files...", total=None)
            
            results = generator.process_directory(directory, output_dir)
            
            progress.update(task, completed=True)
        
        # Print statistics
        generator.print_statistics()
        
        console.print("✅ Docstring generation completed successfully!\n", style="bold green")
        return True
        
    except Exception as e:
        console.print(f"❌ Error during docstring generation: {e}", style="bold red")
        return False


def generate_readme(directory: Path, use_ai: bool, 
                   output_path: Optional[Path] = None) -> bool:
    """Run the README generation agent.
    
    Args:
        directory (Path): Project directory to analyze.
        use_ai (bool): Whether to use AI enhancement.
        output_path (Optional[Path]): Path for output README.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    console.print(f"\n📄 Starting README Generation", style="bold yellow")
    console.print(f"   Directory: {directory}")
    console.print(f"   AI Enhancement: {'Enabled' if use_ai else 'Disabled'}\n")
    
    try:
        generator = READMEGenerator(project_root=directory, use_ai=use_ai)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing project...", total=None)
            generator.analyze_project()
            progress.update(task, description="Generating README...")
            
            if output_path is None:
                output_path = directory / "README.md"
            
            generator.generate_readme(output_path)
            
            progress.update(task, completed=True)
        
        console.print(f"\n✅ README generated successfully: {output_path}\n", style="bold green")
        return True
        
    except Exception as e:
        console.print(f"❌ Error during README generation: {e}", style="bold red")
        return False


def run_full_pipeline(directory: Path, style: str, use_ai: bool) -> bool:
    """Run both agents in sequence.
    
    Args:
        directory (Path): Project directory.
        style (str): Docstring style.
        use_ai (bool): Whether to use AI enhancement.
    
    Returns:
        bool: True if both agents succeeded, False otherwise.
    """
    console.print("\n🚀 Running Full Documentation Pipeline\n", style="bold magenta")
    
    # Step 1: Generate docstrings
    success_docstrings = generate_docstrings(directory, style, use_ai)
    
    if not success_docstrings:
        console.print("⚠️  Docstring generation failed, continuing with README...\n", 
                     style="yellow")
    
    # Step 2: Generate README
    success_readme = generate_readme(directory, use_ai)
    
    # Summary
    console.print("\n" + "="*60, style="bold")
    console.print("📊 PIPELINE SUMMARY", style="bold cyan")
    console.print("="*60, style="bold")
    
    status_docstrings = "✅ Success" if success_docstrings else "❌ Failed"
    status_readme = "✅ Success" if success_readme else "❌ Failed"
    
    console.print(f"Docstring Generation: {status_docstrings}")
    console.print(f"README Generation:    {status_readme}")
    console.print("="*60 + "\n", style="bold")
    
    return success_docstrings and success_readme


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="🏆 Hackathon Documentation Generator - Automated Docstring + README Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate both docstrings and README for current directory
  python main.py --all
  
  # Generate only docstrings in Google style
  python main.py --docstrings --style google
  
  # Generate only README
  python main.py --readme
  
  # Process specific directory without AI
  python main.py --all --directory /path/to/project --no-ai
  
  # Use NumPy style docstrings with AI enhancement
  python main.py --docstrings --style numpy --ai
        """
    )
    
    # Mode selection
    parser.add_argument('--all', action='store_true',
                       help='Run both docstring and README generation (default)')
    parser.add_argument('--docstrings', action='store_true',
                       help='Generate docstrings only')
    parser.add_argument('--readme', action='store_true',
                       help='Generate README only')
    
    # Common options
    parser.add_argument('--directory', '-d', type=str, default='.',
                       help='Project directory to process (default: current directory)')
    parser.add_argument('--no-ai', action='store_true',
                       help='Disable AI enhancement (use rule-based generation)')
    parser.add_argument('--ai', action='store_true',
                       help='Enable AI enhancement (requires API key in .env)')
    
    # Docstring-specific options
    parser.add_argument('--style', '-s', type=str, 
                       choices=['google', 'numpy', 'sphinx'],
                       default='google',
                       help='Docstring style (default: google)')
    parser.add_argument('--output', '-o', type=str,
                       help='Output directory for modified files (default: overwrite)')
    
    # README-specific options
    parser.add_argument('--readme-output', type=str,
                       help='Output path for README.md (default: <directory>/README.md)')
    
    args = parser.parse_args()
    
    # Display banner
    print_banner()
    
    # Determine mode
    if not any([args.all, args.docstrings, args.readme]):
        args.all = True  # Default to running all
    
    # Setup paths
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        console.print(f"❌ Error: Directory not found: {directory}", style="bold red")
        sys.exit(1)
    
    # Determine AI usage
    use_ai = not args.no_ai
    if args.ai:
        use_ai = True
    
    # Validate configuration if AI is enabled
    if use_ai:
        if not validate_configuration():
            console.print("\n💡 Tip: You can still use the tool without AI by adding --no-ai flag\n", 
                         style="yellow")
            sys.exit(1)
    
    # Setup output paths
    output_dir = Path(args.output) if args.output else None
    readme_output = Path(args.readme_output) if args.readme_output else None
    
    # Run requested operations
    success = True
    
    if args.all:
        success = run_full_pipeline(directory, args.style, use_ai)
    else:
        if args.docstrings:
            success = generate_docstrings(directory, args.style, use_ai, output_dir) and success
        
        if args.readme:
            success = generate_readme(directory, use_ai, readme_output) and success
    
    # Exit with appropriate code
    if success:
        console.print("🎉 All operations completed successfully!", style="bold green")
        sys.exit(0)
    else:
        console.print("⚠️  Some operations failed. Check output above for details.", 
                     style="bold yellow")
        sys.exit(1)


if __name__ == '__main__':
    main()
