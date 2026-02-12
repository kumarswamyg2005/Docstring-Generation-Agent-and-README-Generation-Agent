# Web API Documentation Generator

## Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**

   ```bash
   python app.py
   ```

   Or for development with auto-reload:

   ```bash
   uvicorn app:app --reload
   ```

3. **Open Swagger UI:**
   Navigate to http://localhost:8000 in your browser

## API Endpoints

### 1. Generate Docstrings for Single File

**POST** `/generate-docstrings/single`

Upload a Python file and get back the documented version.

**Parameters:**

- `file`: Python file (.py)
- `style`: Docstring style (google/numpy/sphinx) - default: google
- `use_ai`: Enable AI enhancement - default: false

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/generate-docstrings/single" \
  -F "file=@mycode.py" \
  -F "style=google" \
  -F "use_ai=false" \
  --output documented_mycode.py
```

### 2. Generate Docstrings for Multiple Files

**POST** `/generate-docstrings/multiple`

Upload multiple Python files and get back a ZIP with all documented files.

**Parameters:**

- `files`: Multiple Python files
- `style`: Docstring style (google/numpy/sphinx)
- `use_ai`: Enable AI enhancement

### 3. Generate Docstrings for Entire Project

**POST** `/generate-docstrings/project`

Upload a ZIP file containing your project and get back documented version.

**Parameters:**

- `project_zip`: ZIP file containing Python project
- `style`: Docstring style (google/numpy/sphinx)
- `use_ai`: Enable AI enhancement

### 4. Generate README

**POST** `/generate-readme`

Upload a ZIP file and get back a generated README.md.

**Parameters:**

- `project_zip`: ZIP file containing Python project
- `use_ai`: Enable AI enhancement

### 5. Get Available Styles

**GET** `/styles`

Returns list of supported docstring formatting styles.

### 6. Health Check

**GET** `/health`

Check if the API is running.

## Features

- **Swagger UI**: Interactive API documentation at `/`
- **ReDoc**: Alternative documentation at `/redoc`
- **Multiple formats**: Google, NumPy, Sphinx docstring styles
- **AI Enhancement**: Optional AI-powered descriptions (requires API key in .env)
- **Batch Processing**: Handle multiple files or entire projects

## Notes

- Without AI enhancement, the system uses rule-based generation
- AI enhancement requires setting up `.env` with API keys
- All processing happens server-side - your files are processed in temporary directories

## Example Usage in Swagger

1. Go to http://localhost:8000
2. Click on **POST /generate-docstrings/single**
3. Click **Try it out**
4. Upload your Python file
5. Select docstring style
6. Click **Execute**
7. Download the documented file

That's it! Your code now has professional docstrings.
