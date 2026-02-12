# DocuMate Web UI

A beautiful, modern web interface for the DocuMate documentation generator.

## Features

- 🎨 Modern, responsive design with gradient backgrounds
- 📁 Three modes: Single file, Multiple files, and README generation
- 🤖 Optional AI enhancement toggle
- 🎯 Drag-and-drop file upload
- 📥 Direct download of generated files
- ⚡ Real-time processing with loading indicators
- 🎭 Smooth animations and transitions

## How to Use

### 1. Start the API Server

First, make sure the FastAPI server is running:

```bash
PYTHONPATH=. python3 src/main.py
```

The server will start on `http://localhost:8000`

### 2. Open the UI

Simply open `ui.html` in your web browser:

```bash
# macOS
open ui.html

# Linux
xdg-open ui.html

# Windows
start ui.html
```

Or navigate to the file in your file explorer and double-click it.

### 3. Use the Interface

**Single File Mode:**

1. Click "Single File" tab
2. Upload a Python file (.py)
3. Select docstring style (Google/NumPy/Sphinx)
4. Optionally enable AI enhancement
5. Click "Generate Docstrings"
6. Download your documented file

**Multiple Files Mode:**

1. Click "Multiple Files" tab
2. Select multiple Python files
3. Choose your preferred style
4. Generate and download as ZIP

**README Generation:**

1. Click "Generate README" tab
2. Upload a ZIP of your project
3. Optionally enable AI
4. Download the generated README.md

## Technologies Used

- Pure HTML5/CSS3/JavaScript (no frameworks)
- Modern CSS Grid and Flexbox
- Fetch API for REST calls
- Blob API for file downloads
- CSS animations and transitions

## Browser Compatibility

Works on all modern browsers:

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

## Screenshots

The UI features:

- Gradient purple theme
- Tab-based navigation
- File upload zones with hover effects
- Loading spinners during processing
- Success/error messages
- Direct download buttons

## Troubleshooting

**Issue:** Cannot connect to API

- **Solution:** Make sure the server is running on port 8000

**Issue:** CORS errors

- **Solution:** The FastAPI server has CORS enabled, but make sure you're accessing from the same machine

**Issue:** File won't download

- **Solution:** Check your browser's download settings and allow downloads

## API Endpoints Used

- `POST /generate-docstrings/single` - Single file processing
- `POST /generate-docstrings/multiple` - Multiple files processing
- `POST /generate-readme` - README generation
- `GET /health` - Health check

## Customization

You can easily customize the UI by editing `ui.html`:

- **Colors:** Modify the gradient in the `body` background
- **Fonts:** Change the `font-family` in the universal selector
- **Button styles:** Edit the `.btn` class
- **API URL:** Update the `API_BASE` constant in JavaScript

## Production Deployment

For production use:

1. Deploy the FastAPI backend to a cloud service
2. Update the `API_BASE` URL in ui.html
3. Serve ui.html through a web server (Nginx, Apache, etc.)
4. Enable HTTPS for security

Enjoy using DocuMate! 🚀
