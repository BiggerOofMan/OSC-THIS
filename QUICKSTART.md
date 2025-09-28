# Quick Setup Guide for WAYE

## 1. Install Python Dependencies
pip install pytesseract Pillow opencv-python Flask Flask-CORS googletrans langdetect pandas numpy

## 2. Install Tesseract OCR (for image processing)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt install tesseract-ocr

## 3. Start the Web Application
python app.py

## 4. Open Your Browser
# Visit: http://localhost:5000

## 5. Use the App
# - Upload food label photos
# - Or paste ingredients text directly
# - Add your personal allergies
# - Get instant analysis with health scores and warnings

## Features You Get:
# ✅ OCR from food label photos
# ✅ Multi-language detection & translation
# ✅ 200+ ingredient database (including Glucuronolactone!)
# ✅ Personal allergen warnings
# ✅ Health scoring (1-10 scale)
# ✅ Mobile-friendly web interface
# ✅ API endpoints for integration
# ✅ Results saved as JSON files