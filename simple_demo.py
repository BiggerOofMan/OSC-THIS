#!/usr/bin/env python3
"""
Simple THIS Demo - Shows ingredient analysis without OCR dependencies
"""

def demo_ingredient_analysis():
    """Demo the core ingredient analysis functionality"""
    
    print("🍎 THIS - The Hell Is This? - SIMPLE DEMO")
    print("=" * 60)
    
    # Sample ingredients (including glucuronolactone!)
    test_cases = [
        {
            'name': '🥤 Energy Drink',
            'ingredients': 'Water, High Fructose Corn Syrup, Citric Acid, Natural Flavors, Sodium Benzoate, Caffeine, Glucuronolactone, Aspartame (contains Phenylalanine), Yellow 5',
            'allergies': []
        },
        {
            'name': '🍪 Chocolate Cookies',
            'ingredients': 'Wheat Flour, Sugar, Eggs, Milk, Butter, Chocolate Chips, Vanilla, Baking Powder, Salt, Almonds',
            'allergies': ['milk', 'eggs', 'wheat']
        },
        {
            'name': '🥛 Spanish Juice (Translated)',
            'ingredients': 'Organic Apple Juice, Organic Orange Juice, Natural Flavors, Vitamin C, Citric Acid',
            'allergies': []
        }
    ]
    
    # Simple ingredient database (subset of the full one)
    ingredient_db = {
        'glucuronolactone': {
            'name': 'Glucuronolactone',
            'description': 'A naturally occurring chemical compound produced in the liver, commonly added to energy drinks',
            'health_concern': 'low',
            'allergens': [],
            'safety_info': 'Generally recognized as safe (GRAS) by FDA. Naturally produced in human liver.',
            'natural': True
        },
        'aspartame': {
            'name': 'Aspartame',
            'description': 'Artificial sweetener approximately 200 times sweeter than sugar',
            'health_concern': 'moderate',
            'allergens': [],
            'safety_info': 'FDA approved but contains phenylalanine - warning required for phenylketonuria sufferers',
            'natural': False
        },
        'high fructose corn syrup': {
            'name': 'High Fructose Corn Syrup',
            'description': 'Sweetener made from corn starch, higher fructose content than regular corn syrup',
            'health_concern': 'moderate',
            'allergens': [],
            'safety_info': 'Linked to obesity and metabolic issues when consumed in excess',
            'natural': False
        },
        'wheat': {
            'name': 'Wheat',
            'description': 'Cereal grain containing gluten proteins',
            'health_concern': 'low',
            'allergens': ['gluten'],
            'safety_info': 'Contains gluten - avoid if celiac disease or gluten sensitivity',
            'natural': True
        },
        'milk': {
            'name': 'Milk',
            'description': 'Dairy product from mammals, contains lactose and casein',
            'health_concern': 'low',
            'allergens': ['dairy'],
            'safety_info': 'Contains lactose - may cause issues for lactose intolerant individuals',
            'natural': True
        },
        'eggs': {
            'name': 'Eggs',
            'description': 'Protein-rich ingredient from chicken eggs',
            'health_concern': 'low',
            'allergens': ['eggs'],
            'safety_info': 'Common allergen, especially in children',
            'natural': True
        }
    }
    
    def analyze_simple(ingredients_text, user_allergies=None):
        """Simple analysis function"""
        # Parse ingredients
        ingredients = [ing.strip() for ing in ingredients_text.split(',')]
        
        found_allergens = []
        health_scores = []
        warnings = []
        detailed_info = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Check if we know this ingredient
            info = None
            for db_key, db_info in ingredient_db.items():
                if db_key in ingredient_lower or ingredient_lower in db_key:
                    info = db_info
                    break
            
            if info:
                detailed_info.append(info)
                found_allergens.extend(info['allergens'])
                
                # Health score mapping
                score_map = {'low': 8, 'moderate': 6, 'high': 3, 'severe': 1}
                health_scores.append(score_map[info['health_concern']])
                
                # Check user allergies
                if user_allergies:
                    for allergen in info['allergens']:
                        if allergen.lower() in [a.lower() for a in user_allergies]:
                            warnings.append(f"⚠️ ALLERGEN ALERT: Contains {allergen.title()}")
                    
                    if any(allergy.lower() in ingredient_lower for allergy in user_allergies):
                        warnings.append(f"⚠️ INGREDIENT ALERT: Contains {ingredient}")
            else:
                health_scores.append(5)  # Neutral score for unknown
        
        # Calculate overall health score
        overall_score = sum(health_scores) / len(health_scores) if health_scores else 5
        
        return {
            'ingredients': ingredients,
            'health_score': round(overall_score, 1),
            'allergens': list(set(found_allergens)),
            'warnings': warnings,
            'detailed_info': detailed_info
        }
    
    # Run demos
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'-'*20} DEMO {i}: {case['name']} {'-'*20}")
        print(f"📄 Ingredients: {case['ingredients']}")
        
        if case['allergies']:
            print(f"👤 User Allergies: {', '.join(case['allergies'])}")
        
        # Analyze
        result = analyze_simple(case['ingredients'], case['allergies'])
        
        print(f"\n📊 Results:")
        print(f"   Health Score: {result['health_score']}/10")
        print(f"   Ingredients Found: {len(result['ingredients'])}")
        
        if result['allergens']:
            print(f"   Allergens Detected: {', '.join(result['allergens'])}")
        
        if result['warnings']:
            print(f"\n🚨 WARNINGS:")
            for warning in result['warnings']:
                print(f"   {warning}")
        
        if result['detailed_info']:
            print(f"\n🧪 Ingredient Details:")
            for info in result['detailed_info']:  # Show all ingredients
                concern_emoji = {'low': '✅', 'moderate': '⚠️', 'high': '🚨'}.get(info['health_concern'], '❓')
                print(f"   {concern_emoji} {info['name']}: {info['description']}")
    
    # Special highlight for glucuronolactone
    print(f"\n🎯 SPECIAL HIGHLIGHT - About Glucuronolactone:")
    if 'glucuronolactone' in ingredient_db:
        info = ingredient_db['glucuronolactone']
        print(f"   ✨ {info['name']}")
        print(f"   📚 Description: {info['description']}")
        print(f"   🔬 Safety: {info['safety_info']}")
        print(f"   🌱 Natural: {'Yes' if info['natural'] else 'No'}")
    
    print(f"\n{'='*60}")
    print("✅ Simple Demo Complete!")
    print("\n🚀 To use the full system:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Install Tesseract OCR for image processing")
    print("   3. Run: python app.py")
    print("   4. Visit: http://localhost:5000")

if __name__ == "__main__":
    demo_ingredient_analysis()