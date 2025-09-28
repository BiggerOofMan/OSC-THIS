from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from this_processor import THISProcessor

# Load local .env file into environment for development
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# Allow overriding the upload folder (e.g. to point to a mounted volume in production)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize THIS processor lazily to avoid startup crashes
this_processor = None

def get_processor():
    global this_processor
    if this_processor is None:
        try:
            this_processor = THISProcessor()
        except Exception as e:
            logger.error("Failed to initialize THISProcessor: %s", e)
            raise
    return this_processor

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THIS - The Hell Is This?</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .main-content {
            padding: 40px;
        }

        .upload-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            border: 2px dashed #ddd;
            transition: all 0.3s ease;
        }

        .upload-section:hover {
            border-color: #4CAF50;
            background: #f0f8f0;
        }

        .upload-section h2 {
            margin-bottom: 20px;
            color: #333;
        }

        .file-input-wrapper {
            position: relative;
            display: inline-block;
            margin: 20px 0;
        }

        .file-input {
            display: none;
        }

        .file-input-label {
            display: inline-block;
            padding: 12px 24px;
            background: #4CAF50;
            color: white;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }

        .file-input-label:hover {
            background: #45a049;
            transform: translateY(-2px);
        }

        .allergies-section {
            margin: 20px 0;
        }

        .allergies-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            margin-top: 10px;
        }

        .analyze-btn {
            background: linear-gradient(135deg, #FF6B6B 0%, #EE5A52 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }

        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255,107,107,0.3);
        }

        .analyze-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .results {
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            display: none;
        }

        .health-score {
            text-align: center;
            margin: 20px 0;
        }

        .score-circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 0 auto;
        }

        .score-good { background: #4CAF50; }
        .score-moderate { background: #FF9800; }
        .score-poor { background: #F44336; }

        .allergen-alerts {
            background: #ffebee;
            border: 2px solid #f44336;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }

        .allergen-alert {
            color: #d32f2f;
            font-weight: bold;
            margin: 5px 0;
        }

        .recommendations {
            background: #e3f2fd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }

        .recommendation {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #2196F3;
        }

        .ingredients-list {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }

        .ingredient {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }

        .ingredient.moderate { border-left-color: #FF9800; }
        .ingredient.high { border-left-color: #F44336; }

        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4CAF50;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #ffebee;
            color: #d32f2f;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }

        .text-analysis-section {
            background: #fff3e0;
            border-radius: 10px;
            padding: 30px;
            margin-top: 30px;
        }

        .text-input {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
        }

        @media (max-width: 768px) {
            .main-content {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍎 THIS</h1>
            <p>The Hell Is This? - Your Smart Ingredient Analyzer</p>
        </div>

        <div class="main-content">
            <!-- Image Upload Section -->
            <div class="upload-section">
                <h2>📸 Upload Food Label Image</h2>
                <p>Take a photo of the ingredients list on your food packaging</p>
                
                <div class="file-input-wrapper">
                    <input type="file" id="imageInput" class="file-input" accept="image/*" capture="camera">
                    <label for="imageInput" class="file-input-label">
                        📱 Choose Image or Take Photo
                    </label>
                </div>

                <div class="allergies-section">
                    <label for="allergiesInput"><strong>Your Known Allergies (optional):</strong></label>
                    <input type="text" id="allergiesInput" class="allergies-input" 
                           placeholder="e.g., milk, peanuts, gluten, soy (separate with commas)">
                </div>

                <button id="analyzeImageBtn" class="analyze-btn" disabled>
                    🔍 Analyze Food Label
                </button>
            </div>

            <!-- Text Analysis Section -->
            <div class="text-analysis-section">
                <h2>📝 Or Paste Ingredients Text</h2>
                <p>Copy and paste the ingredients list directly</p>
                
                <textarea id="ingredientsText" class="text-input" 
                          placeholder="Paste ingredients list here...
Example: Water, High Fructose Corn Syrup, Citric Acid, Natural Flavors, Sodium Benzoate, Caffeine..."></textarea>

                <button id="analyzeTextBtn" class="analyze-btn">
                    🔍 Analyze Ingredients Text
                </button>
            </div>

            <!-- Loading Indicator -->
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Analyzing your food label... This may take a moment.</p>
            </div>

            <!-- Error Display -->
            <div id="error" class="error"></div>

            <!-- Results Section -->
            <div id="results" class="results">
                <h2>📊 Analysis Results</h2>
                <div id="resultsContent"></div>
            </div>
        </div>
    </div>

    <script>
        // Elements
        const imageInput = document.getElementById('imageInput');
        const analyzeImageBtn = document.getElementById('analyzeImageBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const ingredientsText = document.getElementById('ingredientsText');
        const allergiesInput = document.getElementById('allergiesInput');
        const loading = document.getElementById('loading');
        const error = document.getElementById('error');
        const results = document.getElementById('results');
        const resultsContent = document.getElementById('resultsContent');

        // Enable analyze button when image is selected
        imageInput.addEventListener('change', function() {
            analyzeImageBtn.disabled = !this.files[0];
        });

        // Image analysis
        analyzeImageBtn.addEventListener('click', async function() {
            const file = imageInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);
            
            const allergies = allergiesInput.value.trim();
            if (allergies) {
                formData.append('allergies', allergies);
            }

            await analyzeData('/api/analyze-image', formData);
        });

        // Text analysis
        analyzeTextBtn.addEventListener('click', async function() {
            const text = ingredientsText.value.trim();
            if (!text) {
                showError('Please enter some ingredients text to analyze.');
                return;
            }

            const data = {
                ingredients_text: text,
                allergies: allergiesInput.value.trim()
            };

            await analyzeData('/api/analyze-text', JSON.stringify(data), {
                'Content-Type': 'application/json'
            });
        });

        async function analyzeData(url, data, headers = {}) {
            try {
                showLoading();
                hideError();
                hideResults();

                const response = await fetch(url, {
                    method: 'POST',
                    body: data,
                    headers: headers
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Analysis failed');
                }

                displayResults(result);

            } catch (err) {
                showError('Error: ' + err.message);
                console.error('Analysis error:', err);
            } finally {
                hideLoading();
            }
        }

        function displayResults(data) {
            const analysis = data.analysis;
            let html = '';

            // Health Score
            html += `
                <div class="health-score">
                    <h3>Health Score</h3>
                    <div class="score-circle ${getScoreClass(analysis.health_score)}">
                        ${analysis.health_score}/10
                    </div>
                    <p>${analysis.summary}</p>
                </div>
            `;

            // Personal Allergen Alerts
            if (data.personal_allergen_warnings && data.personal_allergen_warnings.length > 0) {
                html += '<div class="allergen-alerts"><h3>🚨 ALLERGEN ALERTS</h3>';
                data.personal_allergen_warnings.forEach(warning => {
                    html += `<div class="allergen-alert">${warning.message}</div>`;
                });
                html += '</div>';
            }

            // Summary
            if (data.summary) {
                html += `<div class="summary"><h3>📋 Summary</h3><p>${data.summary}</p></div>`;
            }

            // Recommendations
            if (data.recommendations && data.recommendations.length > 0) {
                html += '<div class="recommendations"><h3>💡 Recommendations</h3>';
                data.recommendations.forEach(rec => {
                    html += `<div class="recommendation">${rec}</div>`;
                });
                html += '</div>';
            }

            // Ingredients Details
            if (analysis.ingredient_details && analysis.ingredient_details.length > 0) {
                html += '<div class="ingredients-list"><h3>🧪 Ingredient Details</h3>';
                analysis.ingredient_details.forEach(ingredient => {
                    const concernClass = ingredient.health_concern === 'high' ? 'high' : 
                                       ingredient.health_concern === 'moderate' ? 'moderate' : '';
                    
                    html += `
                        <div class="ingredient ${concernClass}">
                            <h4>${ingredient.name}</h4>
                            <p><strong>Purpose:</strong> ${ingredient.purpose}</p>
                            <p><strong>Health Concern:</strong> ${ingredient.health_concern}</p>
                            ${ingredient.allergens.length > 0 ? 
                                `<p><strong>Allergens:</strong> ${ingredient.allergens.join(', ')}</p>` : ''}
                            <p><strong>Info:</strong> ${ingredient.safety_info}</p>
                        </div>
                    `;
                });
                
                html += '</div>';
            }

            resultsContent.innerHTML = html;
            showResults();
        }

        function getScoreClass(score) {
            if (score >= 7) return 'score-good';
            if (score >= 4) return 'score-moderate';
            return 'score-poor';
        }

        function showLoading() {
            loading.style.display = 'block';
        }

        function hideLoading() {
            loading.style.display = 'none';
        }

        function showError(message) {
            error.textContent = message;
            error.style.display = 'block';
        }

        function hideError() {
            error.style.display = 'none';
        }

        function showResults() {
            results.style.display = 'block';
        }

        function hideResults() {
            results.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """API endpoint for analyzing food label images."""
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get user allergies if provided
        allergies = None
        if 'allergies' in request.form and request.form['allergies'].strip():
            allergies = [allergy.strip() for allergy in request.form['allergies'].split(',')]
        
        # Process the image
        results = get_processor().process_food_label(filepath, user_allergies=allergies)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in analyze_image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """API endpoint for analyzing ingredients text directly."""
    try:
        data = request.get_json()
        
        if not data or 'ingredients_text' not in data:
            return jsonify({'error': 'No ingredients text provided'}), 400
        
        ingredients_text = data['ingredients_text'].strip()
        if not ingredients_text:
            return jsonify({'error': 'Ingredients text is empty'}), 400
        
        # Get user allergies if provided
        allergies = None
        if 'allergies' in data and data['allergies'].strip():
            allergies = [allergy.strip() for allergy in data['allergies'].split(',')]
        
        # Process the text
        results = get_processor().analyze_text_directly(ingredients_text, user_allergies=allergies)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in analyze_text: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

if __name__ == '__main__':
    print("🍎 Starting THIS - The Hell Is This? Server...")
    print("🌐 Access the web interface at: http://localhost:5000")
    print("📱 Mobile-friendly interface available")
    print("🔗 API endpoints:")
    print("   POST /api/analyze-image - Upload image for analysis")
    print("   POST /api/analyze-text - Analyze text directly")
    print("   GET /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)