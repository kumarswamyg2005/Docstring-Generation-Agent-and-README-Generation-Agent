# DocuMate - Python Documentation Generator

## 📖 Overview

DocuMate is an intelligent documentation generator that automates the creation of Python docstrings and README files. Built with two powerful agents, it analyzes your codebase and generates comprehensive, PEP-257 compliant documentation in seconds.

### Why DocuMate?

- **Save Time**: Generate documentation for entire projects in minutes instead of hours
- **Maintain Consistency**: Ensure uniform documentation style across your codebase
- **Multiple Formats**: Support for Google, NumPy, and Sphinx docstring styles
- **Smart Analysis**: Uses AST parsing to understand your code structure
- **Optional AI Enhancement**: Integrate with language models for intelligent descriptions

## 🗂 Project Structure

```
documate/
├── main.py                    # CLI entry point
├── docstring_generator.py     # Docstring generation agent
├── readme_generator.py        # README generation agent
├── ai_provider.py            # AI provider integrations
├── config.py                 # Configuration management
├── utils.py                  # Utility functions
├── demo.py                   # Interactive demo
├── test_suite.py            # Test suite
├── examples/                 # Example files
│   ├── sample_code.py
│   └── edge_cases.py
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md              # This file
```

## 🏗️ Architecture

### Core Components

**Docstring Generator Agent**

- Analyzes Python code using AST (Abstract Syntax Tree)
- Extracts functions, classes, methods, and parameters
- Generates PEP-257 compliant docstrings
- Supports Google, NumPy, and Sphinx formats

**README Generator Agent**

- Scans entire project structure
- Identifies entry points and dependencies
- Generates comprehensive documentation
- Creates installation and usage instructions

**AI Provider System**

- Modular design supporting multiple AI providers
- Optional enhancement for better descriptions
- Fallback to template-based generation

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher

### Setup Steps

1. Clone the repository:

```bash
git clone <repository-url>
cd documate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies:

- `rich` - Beautiful terminal output
- `click` - CLI framework
- `python-dotenv` - Environment configuration
- `pyyaml` - YAML parsing
- `pytest` - Testing framework

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## ▶️ Usage

### Generate Docstrings

```bash
# Generate docstrings for all Python files in current directory
python main.py --docstrings

# Specify directory and style
python main.py --docstrings --directory ./src --style numpy

# Without AI enhancement
python main.py --docstrings --no-ai
```

### Generate README

```bash
# Generate README for your project
python main.py --readme

# Specify project directory
python main.py --readme --directory ./my-project
```

### Generate Everything

```bash
# Generate both docstrings and README
python main.py --all
```

### Run Demo

```bash
# See interactive demonstration
python demo.py
```

## 🧠 Key Features

### Docstring Generation

- **Multiple Formats**: Generate Google, NumPy, or Sphinx style docstrings
- **Smart Analysis**: Automatic parameter and return type detection
- **PEP-257 Compliance**: Industry-standard documentation
- **Batch Processing**: Process entire directories at once
- **Preserves Code**: Only adds docstrings, doesn't modify logic

### README Generation

- **Comprehensive Sections**: Auto-generates 11+ README sections
- **Project Analysis**: Identifies entry points and dependencies
- **Installation Instructions**: Creates setup steps automatically
- **Usage Examples**: Generates code examples from your project
- **Structure Visualization**: Creates directory tree diagrams

### Developer Experience

- **Beautiful CLI**: Rich terminal interface with progress bars
- **Flexible Configuration**: Environment-based settings
- **No AI Required**: Works offline with template-based generation
- **Fast Execution**: Processes large projects in seconds
- **Extensive Tests**: Comprehensive test suite included

## ⚠️ Limitations

- AI enhancement requires API keys and internet connection
- Large projects may take longer to analyze
- Complex dynamic code patterns may not be fully captured
- Requires Python 3.8 or higher

## 🛠 Technologies

- **Python 3.8+** - Core language
- **AST Module** - Code parsing and analysis
- **Rich** - Terminal UI and formatting
- **Click** - Command-line interface
- **PyYAML** - Configuration management

## � Roadmap

- [ ] Support for more programming languages
- [ ] Web-based UI for easier usage
- [ ] Integration with popular IDEs
- [ ] Batch processing for large codebases
- [ ] Custom template support
- [ ] Documentation quality scoring

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built for developers who value good documentation but want to save time writing it.

---

**Made with ❤️ by the DocuMate team**
