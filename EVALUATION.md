# Project Evaluation (Short)

## What this project is

DocuMate is a documentation generator for Python code. It can create docstrings (Google/NumPy/Sphinx styles) and generate a README from a project.

## How it works (high level)

- **Web API**: FastAPI app with Swagger UI for file uploads.
- **Core logic**: Uses Python AST parsing to analyze code and produce docstrings/README content.
- **Optional AI**: Can enhance outputs with OpenAI/Anthropic if keys are configured.

## Main features

- Upload a single Python file → returns docstring-inserted file.
- Upload multiple files → returns a ZIP with updated files.
- Upload a project ZIP → returns a generated README.
- Health and styles endpoints for easy checks.

## How to run

- Run locally: `python3 src/main.py`
- Swagger UI: http://localhost:8000/docs

## Project layout

- `app/` FastAPI app and API models
- `src/` runtime entry + Docker files
- Root: generators and utilities
