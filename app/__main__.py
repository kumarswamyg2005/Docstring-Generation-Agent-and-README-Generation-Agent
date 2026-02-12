"""FastAPI Application Entry Point for Documentation Generator."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path
import tempfile
import zipfile
from io import BytesIO

from app.models import StylesResponse, HealthResponse
from app.agents import DocstringAgent, READMEAgent

app = FastAPI(
    title="Documentation Generator API",
    description="AI-powered documentation generation for Python projects",
    version="1.0.0",
    docs_url="/",
    redoc_url="/docs"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="Documentation Generator API is running")


@app.post("/generate-docstrings/single",
         summary="Generate docstrings for a single Python file",
         description="Upload a Python file and get back the same file with added docstrings")
async def generate_docstrings_single(
    file: UploadFile = File(..., description="Python file to process"),
    style: str = Form("google", description="Docstring style: google, numpy, or sphinx"),
    use_ai: bool = Form(False, description="Use AI enhancement (requires API key)")
):
    """Generate docstrings for a single Python file."""
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python (.py) files are supported")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_file = temp_path / file.filename
        
        with open(input_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        try:
            agent = DocstringAgent(style=style, use_ai=use_ai)
            modified_source = agent.process_file(input_file)
            
            if modified_source is None:
                raise HTTPException(
                    status_code=400, 
                    detail="Failed to process file. File may have syntax errors."
                )
            
            return Response(
                content=modified_source.encode('utf-8'),
                media_type="text/x-python",
                headers={"Content-Disposition": f"attachment; filename=documented_{file.filename}"}
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/generate-docstrings/multiple",
         summary="Generate docstrings for multiple Python files",
         description="Upload multiple Python files and get back a ZIP with all files documented")
async def generate_docstrings_multiple(
    files: List[UploadFile] = File(..., description="Python files to process"),
    style: str = Form("google", description="Docstring style: google, numpy, or sphinx"),
    use_ai: bool = Form(False, description="Use AI enhancement (requires API key)")
):
    """Generate docstrings for multiple Python files."""
    for file in files:
        if not file.filename.endswith('.py'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.filename}. Only Python (.py) files are supported"
            )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        input_dir.mkdir()
        
        for file in files:
            file_path = input_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        try:
            agent = DocstringAgent(style=style, use_ai=use_ai)
            agent.process_directory(input_dir, output_dir=output_dir)
            
            if not output_dir.exists() or not list(output_dir.glob('*.py')):
                raise HTTPException(
                    status_code=400,
                    detail="No Python files processed successfully."
                )
            
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in output_dir.rglob('*.py'):
                    zipf.write(file_path, file_path.name)
            
            zip_buffer.seek(0)
            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=documented_files.zip"}
            )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.post("/generate-readme",
         summary="Generate README for project (ZIP upload)",
         description="Upload a ZIP file containing Python project and get back a README.md file")
async def generate_readme(
    project_zip: UploadFile = File(..., description="ZIP file containing Python project"),
    use_ai: bool = Form(False, description="Use AI enhancement (requires API key)")
):
    """Generate README for a project."""
    if not project_zip.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "project.zip"
        extract_dir = temp_path / "project"
        readme_path = temp_path / "README.md"
        
        with open(zip_path, "wb") as f:
            content = await project_zip.read()
            f.write(content)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        
        try:
            agent = READMEAgent(project_root=extract_dir, use_ai=use_ai)
            agent.analyze_project()
            agent.generate_readme(readme_path)
            
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            return Response(
                content=readme_content.encode('utf-8'),
                media_type="text/markdown",
                headers={"Content-Disposition": "attachment; filename=README.md"}
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating README: {str(e)}")


@app.get("/styles", response_model=StylesResponse)
async def get_styles():
    """Get available docstring styles."""
    return StylesResponse(
        styles=[
            {"name": "google", "description": "Google Style Python Docstrings"},
            {"name": "numpy", "description": "NumPy/SciPy Documentation Style"},
            {"name": "sphinx", "description": "Sphinx Documentation Style"}
        ]
    )
