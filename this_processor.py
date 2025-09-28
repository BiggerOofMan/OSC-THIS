import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Replace eager imports with safe optional imports
try:
    from ocr_processor import OCRProcessor
except Exception:
    OCRProcessor = None

try:
    from ingredient_analyzer import IngredientAnalyzer, AnalysisResult
except Exception:
    IngredientAnalyzer = None
    AnalysisResult = None

try:
    from language_processor import LanguageProcessor
except Exception:
    LanguageProcessor = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class THISProcessor:
    """
    Main THIS (The Hell Is This) processor that orchestrates OCR, translation, and analysis.
    """
    
    def __init__(self, save_results: bool = True, results_dir: str = "results"):
        """
        Initialize the THIS processor.
        """
        # instantiate components but tolerate missing modules
        if OCRProcessor:
            try:
                self.ocr_processor = OCRProcessor()
            except Exception as e:
                logger.warning("OCRProcessor init failed: %s", e)
                self.ocr_processor = None
        else:
            self.ocr_processor = None

        if IngredientAnalyzer:
            try:
                # enable LLM research only if available in analyzer (its constructor guards LLM)
                self.ingredient_analyzer = IngredientAnalyzer()
            except Exception as e:
                logger.warning("IngredientAnalyzer init failed: %s", e)
                self.ingredient_analyzer = None
        else:
            self.ingredient_analyzer = None

        if LanguageProcessor:
            try:
                self.language_processor = LanguageProcessor()
            except Exception as e:
                logger.warning("LanguageProcessor init failed: %s", e)
                self.language_processor = None
        else:
            self.language_processor = None
        
        self.save_results = save_results
        self.results_dir = Path(results_dir)
        
        if self.save_results:
            self.results_dir.mkdir(exist_ok=True)
        
        logger.info("THIS Processor initialized (OCR=%s, Analyzer=%s, Lang=%s)",
                    bool(self.ocr_processor), bool(self.ingredient_analyzer), bool(self.language_processor))
    
    def process_food_label(self, 
                          image_path: str, 
                          languages: Optional[List[str]] = None,
                          user_allergies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Complete processing pipeline for a food label image.
        """
        if not self.ingredient_analyzer:
            raise RuntimeError("IngredientAnalyzer not available. Check ingredient_analyzer.py imports or initialization.")

        try:
            start_time = datetime.now()
            logger.info(f"Starting analysis of image: {image_path}")
            
            # Step 1: OCR Processing
            logger.info("Step 1: Extracting text from image...")
            if languages:
                extracted_text = self.ocr_processor.extract_text_multilang(image_path, languages)
            else:
                extracted_text = self.ocr_processor.extract_text_from_image(image_path)
            
            if not extracted_text.strip():
                raise ValueError("No text could be extracted from the image")
            
            logger.info(f"Extracted {len(extracted_text)} characters from image")
            
            # Step 2: Extract ingredients section
            logger.info("Step 2: Identifying ingredients section...")
            ingredients_text = self.ocr_processor.extract_ingredients_section(extracted_text)
            
            # Step 3: Language detection and translation
            logger.info("Step 3: Processing language and translation...")
            translation_result = self.language_processor.translate_ingredient_list(ingredients_text)
            
            # Use translated text for analysis
            text_for_analysis = translation_result['translated']
            
            # Step 4: Ingredient analysis
            logger.info("Step 4: Analyzing ingredients...")
            analysis_result = self.ingredient_analyzer.analyze_ingredients(text_for_analysis)
            
            # Step 5: Personal allergy check
            logger.info("Step 5: Checking for personal allergens...")
            personal_warnings = self._check_personal_allergies(analysis_result, user_allergies)
            
            # Step 6: Compile comprehensive results
            processing_time = (datetime.now() - start_time).total_seconds()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'image_path': image_path,
                'ocr_results': {
                    'full_text': extracted_text,
                    'ingredients_section': ingredients_text,
                    'text_length': len(extracted_text)
                },
                'translation': translation_result,
                'analysis': self._serialize_analysis_result(analysis_result),
                'personal_allergen_warnings': personal_warnings,
                'llm_research_info': self._get_llm_research_summary(analysis_result),
                'summary': self._generate_comprehensive_summary(analysis_result, personal_warnings, translation_result),
                'recommendations': self._generate_recommendations(analysis_result, personal_warnings)
            }
            
            # Save results if requested
            if self.save_results:
                self._save_results(results, image_path)
            
            logger.info(f"Analysis completed successfully in {processing_time:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Error processing food label: {e}")
            raise
    
    def _check_personal_allergies(self, 
                                analysis_result: Any, 
                                user_allergies: Optional[List[str]]) -> List[Dict[str, str]]:
        """Check for user's specific allergies in the ingredients."""
        if not user_allergies:
            return []
        want = [a.lower().strip() for a in user_allergies]
        warnings = []
        # analysis_result.ingredient_details is a list of dicts (from ingredient_analyzer)
        details = getattr(analysis_result, 'ingredient_details', None) or analysis_result.get('ingredient_details', None) if isinstance(analysis_result, dict) else analysis_result.ingredient_details
        if not details:
            return []
        for ing in details:
            # allergens may be a list
            algs = ing.get('allergens', []) if isinstance(ing, dict) else getattr(ing, 'allergens', [])
            for alg in algs:
                if alg and alg.lower() in want:
                    warnings.append({"ingredient": ing.get('name') if isinstance(ing, dict) else ing.name, "message": f"Contains: {alg}"})
            # also check name text against user allergies
            name = (ing.get('name') if isinstance(ing, dict) else getattr(ing, 'name', '')).lower()
            for a in want:
                if a and (a in name or name in a):
                    warnings.append({"ingredient": ing.get('name') if isinstance(ing, dict) else ing.name, "message": f"Matches allergy: {a}"})
        # dedupe
        unique = []
        seen = set()
        for w in warnings:
            key = (w.get('ingredient'), w.get('message'))
            if key not in seen:
                seen.add(key)
                unique.append(w)
        return unique

    def _get_field(self, obj: Any, name: str, default=None):
        """Safe getter that works with dicts and objects."""
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    def _serialize_analysis_result(self, analysis_result: Any) -> Dict[str, Any]:
        """Convert AnalysisResult (object or dict) to serializable dictionary."""
        # support both AnalysisResult object and previously expected dict shape
        if isinstance(analysis_result, dict):
            return analysis_result

        details = []
        for d in self._get_field(analysis_result, 'ingredient_details', []):
            name = self._get_field(d, 'name')
            details.append({
                'name': name,
                'aliases': self._get_field(d, 'aliases', []),
                'description': self._get_field(d, 'safety_info', self._get_field(d, 'description', '')),
                'purpose': self._get_field(d, 'purpose', ''),
                'allergens': self._get_field(d, 'allergens', []),
                'health_concern': self._get_field(d, 'health_concern', 'moderate'),
                'natural': self._get_field(d, 'natural', False),
                'common_uses': self._get_field(d, 'common_uses', ''),
                'safety_info': self._get_field(d, 'safety_info', ''),
                'source': self._get_field(d, 'source', 'database'),
                'llm_confidence': self._get_field(d, 'llm_confidence', None),
                'score': self._get_field(d, 'score', None)
            })

        health_score = self._get_field(analysis_result, 'health_score', None)
        total = self._get_field(analysis_result, 'total_ingredients', None) or len(self._get_field(analysis_result, 'ingredients', []))
        known = self._get_field(analysis_result, 'known_ingredients', None) or len([i for i in details if i.get('score') is not None])

        return {
            'ingredients': self._get_field(analysis_result, 'ingredients', []),
            'ingredient_details': details,
            'allergens_found': self._get_field(analysis_result, 'allergens_found', []),
            'health_score': round(float(health_score) if health_score is not None else 0.0, 1),
            'summary': self._get_field(analysis_result, 'summary', ''),
            'warnings': self._get_field(analysis_result, 'warnings', []),
            'total_ingredients': int(total),
            'known_ingredients': int(known)
        }

    def _get_llm_research_summary(self, analysis_result: Any) -> Dict[str, Any]:
        """Return a minimal llm research summary that matches frontend expectations."""
        # analysis_result.llm_researched is a simple list of names (ingredient_analyzer)
        researched = getattr(analysis_result, 'llm_researched', None)
        if researched is None and isinstance(analysis_result, dict):
            researched = analysis_result.get('llm_researched', [])
        researched = researched or []
        # produce compact summary
        return {
            'research_enabled': bool(self.ingredient_analyzer and getattr(self.ingredient_analyzer, 'enable_llm_research', False)),
            'total_researched': len(researched),
            'high_confidence_results': None,
            'low_confidence_results': None,
            'researched_ingredients': [{'name': n, 'confidence': None, 'safety_level': None, 'natural': None, 'purpose': None} for n in researched]
        }
    
    def _generate_comprehensive_summary(self, 
                                      analysis_result: Any, 
                                      personal_warnings: List[Dict[str, str]],
                                      translation_result: Dict[str, str]) -> str:
        """Generate a comprehensive, user-friendly summary (handles dicts and objects)."""
        summary_parts = []

        detected_lang = translation_result.get('detected_language') if isinstance(translation_result, dict) else getattr(translation_result, 'detected_language', None)
        if detected_lang and detected_lang != 'en':
            summary_parts.append(f"🌍 Detected {detected_lang.upper()} text and translated to English.")

        # Basic analysis summary
        base_summary = self._get_field(analysis_result, 'summary', '')
        if base_summary:
            summary_parts.append(base_summary)

        # Personal allergen alerts (warnings may not include severity)
        if personal_warnings:
            high_severity = [w for w in personal_warnings if w.get('severity') == 'high']
            if high_severity:
                summary_parts.append(f"🚨 {len(high_severity)} PERSONAL ALLERGEN ALERT(S) - Please review carefully!")

        # Detailed breakdown (handle dict/object ingredient entries)
        details = self._get_field(analysis_result, 'ingredient_details', []) or []
        def get_desc(item):
            return (self._get_field(item, 'description', '') or self._get_field(item, 'safety_info', '')).strip()

        known_count = len([info for info in details if get_desc(info) and get_desc(info) != "Unknown ingredient - information not available"])
        total_count = len(self._get_field(analysis_result, 'ingredients', []) or [])

        if total_count == 0:
            summary_parts.append("No ingredients found.")
        else:
            if known_count < total_count:
                unknown_count = total_count - known_count
                summary_parts.append(f"📊 Analysis: {known_count}/{total_count} ingredients identified ({unknown_count} unknown).")
            else:
                summary_parts.append(f"📊 Analysis: All {total_count} ingredients identified.")

        return " ".join(summary_parts)

    def _generate_recommendations(self, 
                                analysis_result: Any, 
                                personal_warnings: List[Dict[str, str]]) -> List[str]:
        """Generate actionable recommendations; tolerant to dicts/objects."""
        recommendations = []

        health_score = float(self._get_field(analysis_result, 'health_score', 0.0) or 0.0)

        if health_score >= 8:
            recommendations.append("✅ This product appears to have a good ingredient profile.")
        elif health_score >= 6:
            recommendations.append("⚠️ This product has some ingredients that warrant caution.")
        else:
            recommendations.append("🚨 Consider alternatives - this product contains several concerning ingredients.")

        if personal_warnings:
            recommendations.append("🚫 DO NOT CONSUME - Contains ingredients you're allergic to.")

        details = self._get_field(analysis_result, 'ingredient_details', []) or []

        concerning = [d for d in details if (self._get_field(d, 'health_concern', '').lower() in ['high', 'severe'])]
        if concerning:
            names = [self._get_field(d, 'name', '') for d in concerning[:3]]
            recommendations.append(f"📋 Research these ingredients further: {', '.join(names)}")

        # LLM-researched detection (description may be empty)
        llm_researched = [d for d in details if (self._get_field(d, 'description', '') or '').startswith('LLM Research')]
        if llm_researched:
            recommendations.append(f"🤖 AI researched {len(llm_researched)} unknown ingredient(s) using configured LLM")

        # Low confidence LLM results
        low_conf = []
        for d in llm_researched:
            conf = self._get_field(d, 'llm_confidence', None)
            if conf is None:
                conf = self._get_field(d, 'confidence', 0.5)
            try:
                if float(conf) < 0.7:
                    low_conf.append(self._get_field(d, 'name', 'unknown'))
            except Exception:
                pass
        if low_conf:
            recommendations.append(f"⚠️ Verify these AI-researched ingredients independently (low confidence): {', '.join(low_conf[:3])}")

        # Unknown ingredients still unresolved
        unknowns = [d for d in details if (self._get_field(d, 'description', '') or '') == "Unknown ingredient - information not available"]
        if unknowns:
            recommendations.append(f"🔍 Look up these unknown ingredients: {', '.join([self._get_field(d, 'name', '') for d in unknowns[:3]])}")

        if self._get_field(analysis_result, 'allergens_found', []):
            recommendations.append("💡 Always double-check with manufacturer if you have severe allergies.")

        return recommendations
    
    def _save_results(self, results: Dict[str, Any], image_path: str):
        """Save analysis results to JSON file."""
        
        try:
            # Generate filename based on image name and timestamp
            image_name = Path(image_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{image_name}_{timestamp}.json"
            
            results_file = self.results_dir / filename
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def analyze_text_directly(self, 
                             ingredients_text: str,
                             user_allergies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze ingredients text directly without OCR.
        Useful for testing or when you already have the text.
        """
        if not self.ingredient_analyzer:
            raise RuntimeError("IngredientAnalyzer not available. Cannot analyze text. Fix imports or instantiate analyzer.")
        
        try:
            start_time = datetime.now()
            
            # Language processing
            translation_result = self.language_processor.translate_ingredient_list(ingredients_text)
            text_for_analysis = translation_result['translated']
            
            # Analysis
            analysis_result = self.ingredient_analyzer.analyze_ingredients(text_for_analysis)
            
            # Personal allergy check
            personal_warnings = self._check_personal_allergies(analysis_result, user_allergies)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'input_type': 'direct_text',
                'translation': translation_result,
                'analysis': self._serialize_analysis_result(analysis_result),
                'personal_allergen_warnings': personal_warnings,
                'llm_research_info': self._get_llm_research_summary(analysis_result),
                'summary': self._generate_comprehensive_summary(analysis_result, personal_warnings, translation_result),
                'recommendations': self._generate_recommendations(analysis_result, personal_warnings)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing text directly: {e}")
            raise

def main():
    """Example usage of the THIS processor."""
    
    print("🍎 THIS - The Hell Is This? 🍎")
    print("=" * 50)
    
    # Initialize processor
    this = THISProcessor()
    
    # Example 1: Direct text analysis
    print("\n📝 Example 1: Direct Text Analysis")
    test_ingredients = """
    Ingredients: Water, High Fructose Corn Syrup, Citric Acid, Natural Flavors, 
    Sodium Benzoate (Preservative), Caffeine, Glucuronolactone, Aspartame 
    (Contains Phenylalanine), Yellow 5, Milk, Peanuts
    """
    
    user_allergies = ["milk", "peanuts"]  # Example user allergies
    
    results = this.analyze_text_directly(test_ingredients, user_allergies)
    
    print(f"\n📊 Results:")
    print(f"Health Score: {results['analysis']['health_score']}/10")
    print(f"Summary: {results['summary']}")
    
    # LLM Research Info
    llm_info = results['llm_research_info']
    if llm_info['research_enabled'] and llm_info['total_researched'] > 0:
        print(f"\n🤖 LLM Research (Llama-3.3-70B):")
        print(f"  Researched {llm_info['total_researched']} unknown ingredient(s)")
        print(f"  High confidence: {llm_info['high_confidence_results']}, Low confidence: {llm_info['low_confidence_results']}")
    elif llm_info['research_enabled']:
        print(f"\n🤖 LLM Research: Ready (no unknown ingredients found)")
    else:
        print(f"\n🤖 LLM Research: Disabled (see config.env.example to enable)")
    
    if results['personal_allergen_warnings']:
        print(f"\n🚨 ALLERGEN ALERTS:")
        for warning in results['personal_allergen_warnings']:
            print(f"  {warning['message']}")
    
    print(f"\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"  {rec}")
    
    # Example 2: Show ingredient details
    print(f"\n🔍 Ingredient Details ({results['analysis']['total_ingredients']} total):")
    for ingredient in results['analysis']['ingredient_details']:  # Show all ingredients
        # Check if this was LLM researched
        is_llm_research = ingredient['description'].startswith('LLM Research')
        source_indicator = "🤖 AI" if is_llm_research else "📚 DB"
        
        print(f"\n  • {ingredient['name']} ({source_indicator})")
        print(f"    Purpose: {ingredient['purpose']}")
        print(f"    Health Concern: {ingredient['health_concern'].title()}")
        if ingredient['allergens']:
            print(f"    Allergens: {', '.join(ingredient['allergens'])}")
        print(f"    Info: {ingredient['safety_info'][:100]}...")

if __name__ == "__main__":
    main()
