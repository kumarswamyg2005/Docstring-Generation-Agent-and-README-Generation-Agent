#!/usr/bin/env python3
"""Command-line interface for documentation generation."""

import argparse
from pathlib import Path
from docstring_generator import DocstringGenerator
from readme_generator import READMEGenerator


def main():
    """Main.
        """
    """Main.
        """
    parser = argparse.ArgumentParser(description="Generate documentation for Python projects")
    parser.add_argument('--docstrings', action='store_true', help='Generate docstrings')
    parser.add_argument('--readme', action='store_true', help='Generate README')
    parser.add_argument('--directory', type=str, default='.', help='Directory to process')
    parser.add_argument('--style', type=str, default='google', 
                       choices=['google', 'numpy', 'sphinx'], 
                       help='Docstring style')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI enhancement')
    parser.add_argument('--output', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    use_ai = not args.no_ai
    directory = Path(args.directory).resolve()
    
    if args.docstrings:
        print(f"\n🚀 Generating docstrings for: {directory}")
        print(f"Style: {args.style}")
        print(f"AI Enhancement: {'Enabled' if use_ai else 'Disabled'}\n")
        
        generator = DocstringGenerator(style=args.style, use_ai=use_ai)
        
        if args.output:
            output_dir = Path(args.output)
            generator.process_directory(directory, output_dir=output_dir)
        else:
            generator.process_directory(directory)
        
        generator.print_statistics()
    
    if args.readme:
        print(f"\n📝 Generating README for: {directory}")
        print(f"AI Enhancement: {'Enabled' if use_ai else 'Disabled'}\n")
        
        readme_gen = READMEGenerator(project_root=directory, use_ai=use_ai)
        readme_gen.analyze_project()
        
        readme_path = directory / 'README_GENERATED.md'
        readme_gen.generate_readme(readme_path)
        
        print(f"✅ README saved to: {readme_path}")
    
    if not args.docstrings and not args.readme:
        parser.print_help()
        print("\n⚠️  Please specify --docstrings or --readme")


if __name__ == '__main__':
    main()
