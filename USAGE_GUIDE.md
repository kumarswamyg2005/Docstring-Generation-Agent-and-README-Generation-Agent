# 📖 DocuMate - Usage Guide

## 🚀 Quick Start (For Anyone Using This Tool)

### Step 1: Requirements

```bash
# Make sure Python 3.7+ is installed
python3 --version

# Install dependencies (if any are added later)
pip install -r requirements.txt
```

### Step 2: Basic Usage

#### Generate Docstrings for Your Code

```bash
# Navigate to the DocuMate folder
cd /path/to/DocuMate

# Generate docstrings for your Python project
python3 main.py --docstrings --no-ai --directory /path/to/your/code --output ./documented_output
```

#### Real Examples:

**Example 1: Document a single folder**

```bash
python3 main.py --docstrings --no-ai --directory ~/my_project/src --output ~/my_project/documented
```

**Example 2: Document entire project**

```bash
python3 main.py --docstrings --no-ai --directory ~/Desktop/my_python_app --output ~/Desktop/my_python_app_docs
```

**Example 3: Use AI enhancement (if API keys configured)**

```bash
python3 main.py --docstrings --ai --directory ~/my_code --output ~/my_code_documented
```

### Step 3: Choose Docstring Style

```bash
# Google Style (default)
python3 main.py --docstrings --no-ai --style google --directory ./code --output ./output

# NumPy Style
python3 main.py --docstrings --no-ai --style numpy --directory ./code --output ./output

# Sphinx Style
python3 main.py --docstrings --no-ai --style sphinx --directory ./code --output ./output
```

---

## 📦 How to Share This Tool with Others

### Method 1: Share the Folder (Simplest)

1. Zip the entire `epoch` folder
2. Send to others via email/drive/USB
3. They extract and run: `python3 main.py --docstrings --no-ai --directory <their_code> --output <output_folder>`

### Method 2: GitHub Repository (Recommended)

```bash
# Initialize git if not already done
cd /Users/kumaraswamy/Desktop/epoch
git init
git add .
git commit -m "Initial commit - DocuMate v1.0"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/DocuMate.git
git push -u origin main
```

Then others can clone:

```bash
git clone https://github.com/YOUR_USERNAME/DocuMate.git
cd DocuMate
python3 main.py --docstrings --no-ai --directory ~/their_code --output ~/output
```

### Method 3: Create Standalone Executable (Advanced)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile main.py

# Executable will be in dist/main
# Share the dist/ folder with others
```

---

## 🎯 Demo for Sir/Judges

### Quick Demo Script:

```bash
# 1. Show the tool
cd /Users/kumaraswamy/Desktop/epoch
ls -la

# 2. Show test code WITHOUT docstrings
cat test_input/fresh_test.py

# 3. Generate docstrings
python3 main.py --docstrings --no-ai --directory test_input --output test_output

# 4. Show the SAME code WITH docstrings
cat test_output/fresh_test.py

# 5. Prove it's valid Python (no errors)
python3 -c "import ast; ast.parse(open('test_output/fresh_test.py').read()); print('✅ Valid!')"
```

---

## 📋 What Files to Share

### Minimum Required Files:

```
DocuMate/
├── main.py                    # Main entry point
├── docstring_generator.py     # Core generator
├── readme_generator.py        # README generator
├── utils.py                   # Helper functions
├── USAGE_GUIDE.md            # This file
├── README.md                 # Project overview
└── requirements.txt          # Dependencies (if any)
```

### Optional Files for Demo:

```
├── test_input/               # Example input code
│   └── fresh_test.py
├── test_output/              # Example output
│   └── fresh_test.py
└── perfect_demo.py           # Demo script
```

---

## ⚙️ Command Reference

### All Options:

```bash
python3 main.py --help

Options:
  --all                    Generate both docstrings and README
  --docstrings            Generate docstrings only
  --readme                Generate README only
  --directory DIRECTORY   Path to Python code directory
  --output OUTPUT         Output directory for docstrings
  --readme-output OUTPUT  Output path for README
  --style {google,numpy,sphinx}  Docstring style
  --no-ai                 Disable AI enhancement
  --ai                    Enable AI enhancement
```

### Common Commands:

```bash
# Just docstrings
python3 main.py --docstrings --no-ai --directory ./code --output ./output

# Just README
python3 main.py --readme --no-ai --directory ./code --readme-output ./README.md

# Both docstrings and README
python3 main.py --all --no-ai --directory ./code --output ./docs --readme-output ./README.md
```

---

## 🎥 Live Demo Tips

1. **Prepare clean test file** - Show code without any docstrings
2. **Run the tool** - Let them see the live generation
3. **Show the output** - Display beautifully formatted docstrings
4. **Verify syntax** - Prove no errors with `python3 -m py_compile`
5. **Compare side-by-side** - Show before/after

### One-Line Demo:

```bash
echo "def test(x): return x*2" > demo.py && python3 main.py --docstrings --no-ai --directory . --output ./out --style google && cat out/demo.py
```

---

## 🐛 Troubleshooting

**Issue: "No module named 'X'"**

```bash
pip install -r requirements.txt
```

**Issue: "Permission denied"**

```bash
chmod +x main.py
python3 main.py ...
```

**Issue: "Output folder exists"**

```bash
# Delete old output first
rm -rf output_folder
python3 main.py --docstrings --no-ai --directory ./code --output ./output_folder
```

---

## 💡 Tips for Users

1. **Always backup original code** before running
2. **Use `--output` flag** to keep original code safe
3. **Review generated docstrings** - customize if needed
4. **Start with small test** before documenting entire project
5. **Use `--no-ai` flag** for fast, offline generation

---

## 📞 Support

For issues or questions, contact: [Your Email/GitHub]

---

**Made with ❤️ for Hackathon 2026**
