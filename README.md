# THIS (The Hell Is This?) – Installation Guide

## 1. Prerequisites
- Python 3.8+ (download from python.org, check "Add Python to PATH")  
- Tesseract OCR  
  - Windows: download from UB Mannheim Tesseract GitHub page, install, and add to PATH  
  - macOS:  
    ```bash
    brew install tesseract
    ```
  - Linux (Ubuntu/Debian):  
    ```bash
    sudo apt update
    sudo apt install tesseract-ocr libtesseract-dev
    ```

## 2. Setup
```bash
# Go to project folder
cd C:\Users\Anirudh\Desktop\MiniHackProject\OSC2

# Create virtual environment
python -m venv this_env

# Activate (Windows)
this_env\Scripts\activate

# Activate (macOS/Linux)
source this_env/bin/activate

# Install dependencies
pip install -r requirements.txt

3. Test Installation

python this_processor.py

4. AI Ingredient Research (Optional)

THIS can use Llama 3.3 (70B) for ingredient research.

    Local (Ollama): install Ollama, then run:

ollama pull llama3.3:70b

Cloud (Together AI): get an API key from Together

Copy config.env.example to .env and add your keys

Run demo:

    python llm_demo.py

5. Running the App

    Web App (Recommended):

python app.py

Open: http://localhost:5000

Command Line:

    python this_processor.py

6. Usage

Web App

    Open app in browser

    Upload food label image or paste ingredients

    Add allergies (optional)

    Click Analyze

Python API

from this_processor import THISProcessor

this = THISProcessor()
result = this.analyze_text_directly(
    "Water, Sugar, Citric Acid, Natural Flavors",
    user_allergies=["gluten", "nuts"]
)

print(result["summary"])

7. Troubleshooting

    Tesseract not found → reinstall or update path in ocr_processor.py

    Import errors → activate virtual environment and reinstall requirements

    Bad OCR → use clear, well-lit images

    Translation issues → check internet connection

8. Features

    OCR (read ingredients from images)

    Multi-language support (12+)

    Ingredient analysis + health scoring

    Allergen alerts (customizable)

    Web app + API

9. File Layout

OSC2/
├── app.py               # Flask app
├── this_processor.py    # Main logic
├── ocr_processor.py     # OCR functions
├── ingredient_analyzer.py
├── language_processor.py
├── uploads/             # Temp images
├── results/             # Analysis JSONs
└── requirements.txt
