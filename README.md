# THIS (The Hell Is This?) - Installation Guide

## Prerequisites

### 1. Install Python 3.8 or higher
- Download from https://python.org
- Make sure to check "Add Python to PATH" during installation

### 2. Install Tesseract OCR
#### Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (usually `C:\Program Files\Tesseract-OCR\`)
3. Add to system PATH or update `ocr_processor.py` with the correct path

#### macOS:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

## Installation Steps

### 1. Clone or Download the Project
```bash
cd C:\Users\Anirudh\Desktop\MiniHackProject\OSC2
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv this_env
```

### 3. Activate Virtual Environment
#### Windows:
```powershell
this_env\Scripts\Activate.ps1  # or Activate for cmd.exe
```

#### macOS/Linux:
```bash
source waye_env/bin/activate
```

### 4. Install Required Packages
```bash
pip install -r requirements.txt
```

### 5. Test Installation
```bash
python this_processor.py
```

## 🤖 NEW: AI-Powered Ingredient Research

THIS now includes **Meta Llama-3.3-70B** integration for researching unknown ingredients! 

### Quick Setup:
1. **Ollama (Local)**: Install from https://ollama.ai/, run `ollama pull llama3.3:70b`
2. **Together AI (Cloud)**: Get API key from https://api.together.xyz/
3. **Configure**: Copy `config.env.example` to `.env` and add your settings

### Benefits:
- 🔍 **Automatic research** of unknown ingredients
- 🎯 **Detailed information**: purpose, health concerns, allergens
- 📊 **Confidence scores** for reliability assessment  
- 🔒 **Privacy options**: Use local Ollama or cloud APIs

See `LLM_SETUP.md` for detailed configuration instructions.

### Demo the LLM Feature:
```bash
python llm_demo.py
```

## Running the Application

### Option 1: Web Interface (Recommended)
```bash
python app.py
```
Then open: http://localhost:5000

### Option 2: Command Line Testing
```bash
python this_processor.py
```

## Usage Examples

### Web Interface
1. Open http://localhost:5000
2. Upload a food label image OR paste ingredients text
3. Optionally add your known allergies
4. Click "Analyze" to get results

### Python API
```python
from this_processor import THISProcessor

# Initialize
this = THISProcessor()

# Analyze text directly
result = waye.analyze_text_directly(
    "Water, Sugar, Citric Acid, Natural Flavors, Preservatives",
    user_allergies=["gluten", "nuts"]
)

# Analyze image (requires image file)
# result = this.process_food_label("path/to/food_label.jpg")

print(f"Health Score: {result['analysis']['health_score']}/10")
print(f"Summary: {result['summary']}")
```

## Troubleshooting

### Common Issues

1. **Tesseract not found error**
   - Make sure Tesseract is installed and in PATH
   - Or update the path in `ocr_processor.py`

2. **Import errors**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again

3. **OCR accuracy issues**
   - Ensure good lighting when taking photos
   - Try to capture just the ingredients section
   - Text should be clear and readable

4. **Translation issues**
   - Check internet connection (Google Translate API)
   - Some languages may have limited support

### Performance Tips
- Use well-lit, clear images
- Crop to just the ingredients section
- Ensure text is horizontal and readable
- Use high-resolution images when possible

## Features

✅ **OCR Processing** - Extract text from food label images  
✅ **Multi-language Support** - Detect and translate 12+ languages  
✅ **Ingredient Analysis** - Comprehensive database of food additives  
✅ **Allergen Detection** - Identify common allergens  
✅ **Personal Allergy Alerts** - Custom warnings based on your allergies  
✅ **Health Scoring** - 1-10 scale based on ingredient safety  
✅ **Web Interface** - Mobile-friendly web app  
✅ **API Endpoints** - For integration with other apps  

## Supported Languages
- English, Spanish, French, German, Italian, Portuguese
- Japanese, Chinese, Korean, Arabic, Hindi, Russian

## File Structure
```
OSC2/
├── requirements.txt          # Python dependencies
├── app.py                   # Flask web application
├── this_processor.py        # Main processing orchestrator  
├── ocr_processor.py         # OCR and image processing
├── ingredient_analyzer.py   # Ingredient database and analysis
├── language_processor.py    # Multi-language translation
├── uploads/                 # Temporary image storage
├── results/                 # Analysis results (JSON files)
└── README.md               # This file
```

## Next Steps
1. Expand ingredient database
2. Add more languages
3. Implement user accounts
4. Add mobile app
5. Integrate with nutrition APIs
6. Add barcode scanning