from googletrans import Translator
from langdetect import detect
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageProcessor:
    """Handles multi-language support for ingredient translation and detection"""
    
    def __init__(self):
        self.translator = Translator()
        
        # Common ingredient translations for faster lookup
        self.ingredient_translations = {
            'es': {  # Spanish
                'azúcar': 'sugar',
                'sal': 'salt',
                'agua': 'water',
                'harina': 'flour',
                'huevos': 'eggs',
                'leche': 'milk',
                'mantequilla': 'butter',
                'aceite': 'oil',
                'conservantes': 'preservatives',
                'colorantes': 'colorings',
                'edulcorantes': 'sweeteners',
                'ingredientes': 'ingredients',
                'contiene': 'contains',
                'puede contener': 'may contain'
            },
            'fr': {  # French
                'sucre': 'sugar',
                'sel': 'salt',
                'eau': 'water',
                'farine': 'flour',
                'œufs': 'eggs',
                'lait': 'milk',
                'beurre': 'butter',
                'huile': 'oil',
                'conservateurs': 'preservatives',
                'colorants': 'colorings',
                'édulcorants': 'sweeteners',
                'ingrédients': 'ingredients',
                'contient': 'contains',
                'peut contenir': 'may contain'
            },
            'de': {  # German
                'zucker': 'sugar',
                'salz': 'salt',
                'wasser': 'water',
                'mehl': 'flour',
                'eier': 'eggs',
                'milch': 'milk',
                'butter': 'butter',
                'öl': 'oil',
                'konservierungsstoffe': 'preservatives',
                'farbstoffe': 'colorings',
                'süßungsmittel': 'sweeteners',
                'zutaten': 'ingredients',
                'enthält': 'contains',
                'kann enthalten': 'may contain'
            },
            'it': {  # Italian
                'zucchero': 'sugar',
                'sale': 'salt',
                'acqua': 'water',
                'farina': 'flour',
                'uova': 'eggs',
                'latte': 'milk',
                'burro': 'butter',
                'olio': 'oil',
                'conservanti': 'preservatives',
                'coloranti': 'colorings',
                'dolcificanti': 'sweeteners',
                'ingredienti': 'ingredients',
                'contiene': 'contains',
                'può contenere': 'may contain'
            },
            'pt': {  # Portuguese
                'açúcar': 'sugar',
                'sal': 'salt',
                'água': 'water',
                'farinha': 'flour',
                'ovos': 'eggs',
                'leite': 'milk',
                'manteiga': 'butter',
                'óleo': 'oil',
                'conservantes': 'preservatives',
                'corantes': 'colorings',
                'adoçantes': 'sweeteners',
                'ingredientes': 'ingredients',
                'contém': 'contains',
                'pode conter': 'may contain'
            },
            'ja': {  # Japanese
                '砂糖': 'sugar',
                '塩': 'salt',
                '水': 'water',
                '小麦粉': 'flour',
                '卵': 'eggs',
                '牛乳': 'milk',
                'バター': 'butter',
                '油': 'oil',
                '保存料': 'preservatives',
                '着色料': 'colorings',
                '甘味料': 'sweeteners',
                '原材料': 'ingredients',
                '含む': 'contains'
            },
            'zh': {  # Chinese (Simplified)
                '糖': 'sugar',
                '盐': 'salt',
                '水': 'water',
                '面粉': 'flour',
                '鸡蛋': 'eggs',
                '牛奶': 'milk',
                '黄油': 'butter',
                '油': 'oil',
                '防腐剂': 'preservatives',
                '色素': 'colorings',
                '甜味剂': 'sweeteners',
                '配料': 'ingredients',
                '含有': 'contains'
            }
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            detected_lang = detect(text)
            logger.info(f"Detected language: {detected_lang}")
            return detected_lang
        except Exception as e:
            logger.warning(f"Language detection failed: {e}, defaulting to English")
            return 'en'
    
    def translate_to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to English.
        
        Args:
            text: Text to translate
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            Translated text in English
        """
        try:
            # If already in English, return as-is
            if source_lang == 'en':
                return text
            
            # Auto-detect language if not provided
            if source_lang is None:
                source_lang = self.detect_language(text)
                if source_lang == 'en':
                    return text
            
            # Try fast translation using our dictionary first
            if source_lang in self.ingredient_translations:
                translated_text = self._fast_translate(text, source_lang)
                if translated_text != text:  # If translation occurred
                    return translated_text
            
            # Fall back to Google Translate for unknown terms
            result = self.translator.translate(text, src=source_lang, dest='en')
            logger.info(f"Translated '{text[:50]}...' from {source_lang} to English")
            return result.text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def _fast_translate(self, text: str, source_lang: str) -> str:
        """
        Fast translation using local dictionary.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            Translated text (or original if no translation found)
        """
        if source_lang not in self.ingredient_translations:
            return text
        
        translation_dict = self.ingredient_translations[source_lang]
        text_lower = text.lower()
        
        # Try exact matches first
        for foreign_word, english_word in translation_dict.items():
            if foreign_word in text_lower:
                text = text.replace(foreign_word, english_word)
                text = text.replace(foreign_word.capitalize(), english_word.capitalize())
        
        return text
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages for translation.
        
        Returns:
            List of language codes
        """
        return ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'zh', 'ko', 'ar', 'hi', 'ru']
    
    def translate_ingredient_list(self, ingredients_text: str, source_lang: Optional[str] = None) -> Dict[str, str]:
        """
        Translate ingredients list and return both original and translated versions.
        
        Args:
            ingredients_text: Original ingredients text
            source_lang: Source language (auto-detect if None)
            
        Returns:
            Dictionary with 'original', 'translated', and 'detected_language' keys
        """
        try:
            detected_lang = source_lang or self.detect_language(ingredients_text)
            translated_text = self.translate_to_english(ingredients_text, detected_lang)
            
            return {
                'original': ingredients_text,
                'translated': translated_text,
                'detected_language': detected_lang,
                'confidence': 'high' if detected_lang != 'en' else 'n/a'
            }
            
        except Exception as e:
            logger.error(f"Error in ingredient translation: {e}")
            return {
                'original': ingredients_text,
                'translated': ingredients_text,
                'detected_language': 'unknown',
                'confidence': 'low'
            }

# Language-specific OCR configurations
OCR_LANGUAGE_CONFIGS = {
    'en': 'eng',
    'es': 'spa',
    'fr': 'fra', 
    'de': 'deu',
    'it': 'ita',
    'pt': 'por',
    'ja': 'jpn',
    'zh': 'chi_sim',
    'ko': 'kor',
    'ar': 'ara',
    'hi': 'hin',
    'ru': 'rus'
}

def get_ocr_language_code(language_code: str) -> str:
    """
    Convert language code to Tesseract OCR language code.
    
    Args:
        language_code: Standard language code (e.g., 'en', 'es')
        
    Returns:
        Tesseract language code
    """
    return OCR_LANGUAGE_CONFIGS.get(language_code, 'eng')

if __name__ == "__main__":
    # Test the language processor
    processor = LanguageProcessor()
    
    # Test translations
    test_cases = [
        ("Ingredientes: azúcar, sal, agua, conservantes", "es"),
        ("Ingrédients: sucre, sel, eau, conservateurs", "fr"),
        ("Zutaten: Zucker, Salz, Wasser, Konservierungsstoffe", "de")
    ]
    
    for text, lang in test_cases:
        print(f"\nOriginal ({lang}): {text}")
        
        result = processor.translate_ingredient_list(text, lang)
        print(f"Translated: {result['translated']}")
        print(f"Detected language: {result['detected_language']}")
    
    # Test auto-detection
    print(f"\nSupported languages: {processor.get_supported_languages()}")