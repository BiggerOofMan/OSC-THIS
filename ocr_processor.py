import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import List, Tuple, Optional
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file (if present) so environment variables like TESSERACT_CMD are available
try:
    load_dotenv()
    logger.debug("Loaded .env file (if present)")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

class ImagePreprocessor:
    """Handles image preprocessing to improve OCR accuracy."""
    
    @staticmethod
    def preprocess_image(image_path: str) -> Image.Image:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise

class OCRProcessor:
    """Handles OCR operations to extract text from food labels."""
    
    def __init__(self):
        # Configure Tesseract binary path. Priority order:
        # 1. TESSERACT_CMD environment variable (full path to tesseract executable)
        # 2. TESSERACT_PATH environment variable (directory containing tesseract.exe)
        # 3. Common Windows install location
        # If none exist, we leave pytesseract to rely on PATH.
        env_cmd = os.getenv('TESSERACT_CMD')
        env_path = os.getenv('TESSERACT_PATH')

        cmd = None
        if env_cmd:
            cmd = env_cmd
        elif env_path:
            # allow user to point to folder instead of full exe
            cmd = os.path.join(env_path, 'tesseract.exe') if os.name == 'nt' else os.path.join(env_path, 'tesseract')
        else:
            # Common Windows path
            common_win = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(common_win):
                cmd = common_win

        if cmd:
            try:
                pytesseract.pytesseract.tesseract_cmd = cmd
                logging.getLogger(__name__).info(f"Using tesseract executable: {cmd}")
            except Exception:
                logging.getLogger(__name__).warning(f"Failed to set pytesseract.tesseract_cmd to {cmd}")
        else:
            logging.getLogger(__name__).info("No explicit tesseract path configured; relying on system PATH")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from food label image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        try:
            # Preprocess image
            preprocessor = ImagePreprocessor()
            processed_image = preprocessor.preprocess_image(image_path)
            
            # Configure OCR settings for better ingredient detection
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,()[]-%/:; '
            
            # Extract text
            extracted_text = pytesseract.image_to_string(
                processed_image,
                config=custom_config,
                lang='eng'
            )
            
            logger.info(f"Successfully extracted text from image: {len(extracted_text)} characters")
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def extract_text_multilang(self, image_path: str, languages: List[str] = ['eng']) -> str:
        """
        Extract text supporting multiple languages.
        
        Args:
            image_path: Path to the image file
            languages: List of language codes (e.g., ['eng', 'spa', 'fra'])
            
        Returns:
            Extracted text as string
        """
        try:
            preprocessor = ImagePreprocessor()
            processed_image = preprocessor.preprocess_image(image_path)
            
            # Join languages with +
            lang_string = '+'.join(languages)
            
            extracted_text = pytesseract.image_to_string(
                processed_image,
                lang=lang_string
            )
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting multilingual text: {e}")
            raise
    
    def extract_ingredients_section(self, text: str) -> str:
        """
        Extract the ingredients section from the full OCR text.
        
        Args:
            text: Full OCR extracted text
            
        Returns:
            Ingredients section text
        """
        import re
        
        # Common ingredient section keywords in multiple languages
        ingredient_keywords = [
            r'ingredients?:',
            r'ingredientes?:',
            r'ingrédients?:',
            r'zutaten:',
            r'成分:',
            r'原材料:',
        ]
        
        text_lower = text.lower()
        
        for keyword in ingredient_keywords:
            match = re.search(keyword, text_lower)
            if match:
                # Extract text after the keyword
                start_pos = match.end()
                
                # Look for end markers (nutritional info, etc.)
                end_markers = [
                    r'nutrition',
                    r'nutritional',
                    r'calories',
                    r'energy',
                    r'allergen',
                    r'storage',
                    r'best before',
                    r'expiry',
                ]
                
                end_pos = len(text)
                for marker in end_markers:
                    end_match = re.search(marker, text_lower[start_pos:])
                    if end_match:
                        end_pos = start_pos + end_match.start()
                        break
                
                ingredients_text = text[start_pos:end_pos].strip()
                return ingredients_text
        
        # If no specific ingredients section found, return full text
        logger.warning("No ingredients section found, returning full text")
        return text

if __name__ == "__main__":
    # Test the OCR processor
    ocr = OCRProcessor()
    
    # Example usage (you'll need to provide an actual image file)
    # text = ocr.extract_text_from_image("sample_food_label.jpg")
    # ingredients = ocr.extract_ingredients_section(text)
    # print(f"Extracted ingredients: {ingredients}")
    
    print("OCR Processor initialized successfully!")