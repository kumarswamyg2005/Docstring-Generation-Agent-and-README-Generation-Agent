"""FastAPI Web Application for Documentation Generator.

This module provides a REST API with Swagger UI for generating
Python docstrings and README files through file uploads.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pathlib import Path
import tempfile
import shutil
import zipfile
from io import BytesIO

from docstring_generator import DocstringGenerator
from readme_generator import READMEGenerator

app = FastAPI(
    title="Documentation Generator API",
    description="Upload Python files to automatically generate docstrings and README files",
    version="1.0.0",
    docs_url="/",  # Swagger UI at root
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Documentation Generator API is running"}


@app.post("/generate-docstrings/single",
         summary="Generate docstrings for a single Python file",
         description="Upload a Python file and get back the same file with added docstrings")
async def generate_docstrings_single(
    file: UploadFile = File(..., description="Python file to process"),
    style: str = Form("google", description="Docstring style: google, numpy, or sphinx"),
    use_ai: bool = Form(False, description="Use AI enhancement (requires API key)")
):
    """Generate docstrings for a single Python file.
    
    Args:
        file: The Python file to process
        style: Docstring format style
        use_ai: Whether to use AI for enhanced descriptions
    
    Returns:
        FileResponse: Modified Python file with docstrings
    """
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python (.py) files are supported")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_file = temp_path / file.filename
        
        # Save uploaded file
        with open(input_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        try:
            # Generate docstrings
            generator = DocstringGenerator(style=style, use_ai=use_ai)
            modified_source = generator.generate_for_file(input_file)
            
            if modified_source is None:
                raise HTTPException(
                    status_code=400, 
                    detail="Failed to process file. File may have syntax errors."
                )
            
            # Return the modified content directly
            return Response(
                content=modified_source.encode('utf-8'),
                media_type="text/x-python",
                headers={
                    "Content-Disposition": f"attachment; filename=documented_{file.filename}"
                }
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
    """Generate docstrings for multiple Python files.
    
    Args:
        files: List of Python files to process
        style: Docstring format style
        use_ai: Whether to use AI for enhanced descriptions
    
    Returns:
        FileResponse: ZIP file containing all documented files
    """
    # Validate all files are Python files
    for file in files:
        if not file.filename.endswith('.py'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.filename}. Only Python (.py) files are supported"
            )
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        input_dir.mkdir()
        
        # Save uploaded files
        for file in files:
            file_path = input_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        try:
            # Generate docstrings
            generator = DocstringGenerator(style=style, use_ai=use_ai)
            results = generator.process_directory(input_dir, output_dir=output_dir)
            
            # If no files were processed, create output copies of originals
            if results['files_processed'] == 0:
                output_dir.mkdir(parents=True, exist_ok=True)
                for file_path in input_dir.glob('*.py'):
                    shutil.copy(file_path, output_dir / file_path.name)
            
            # Ensure output directory exists and has files
            if not output_dir.exists() or not list(output_dir.glob('*.py')):
                raise HTTPException(
                    status_code=400,
                    detail="No Python files with functions/classes found to document."
                )
            
            # Create ZIP file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in output_dir.rglob('*.py'):
                    zipf.write(file_path, file_path.name)
            
            # Return the ZIP file content
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
    """Generate README for a project.
    
    Args:
        project_zip: ZIP file containing the project
        use_ai: Whether to use AI for enhanced descriptions
    
    Returns:
        FileResponse: Generated README.md file
    """
    if not project_zip.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "project.zip"
        extract_dir = temp_path / "project"
        readme_path = temp_path / "README.md"
        
        # Save and extract ZIP
        with open(zip_path, "wb") as f:
            content = await project_zip.read()
            f.write(content)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        
        try:
            # Generate README
            generator = READMEGenerator(project_root=extract_dir, use_ai=use_ai)
            generator.analyze_project()
            generator.generate_readme(readme_path)
            
            # Read the README content before temp directory is deleted
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            return Response(
                content=readme_content.encode('utf-8'),
                media_type="text/markdown",
                headers={"Content-Disposition": "attachment; filename=README.md"}
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating README: {str(e)}")


@app.get("/styles",
        summary="Get available docstring styles",
        description="Returns list of supported docstring formatting styles")
async def get_styles():
    """Get available docstring styles."""
    return {
        "styles": [
            {
                "name": "google",
                "description": "Google Style Python Docstrings"
            },
            {
                "name": "numpy",
                "description": "NumPy/SciPy Documentation Style"
            },
            {
                "name": "sphinx",
                "description": "Sphinx Documentation Style"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Starting Documentation Generator API")
    print("="*70)
    print("\n📖 Swagger UI: http://localhost:8000")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
