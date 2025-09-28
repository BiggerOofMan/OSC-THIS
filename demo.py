#!/usr/bin/env python3

"""
THIS (The Hell Is This?) - Demo Script
Demonstrates the capabilities of the THIS system with sample data.
"""

import os
import json
from pathlib import Path
from this_processor import THISProcessor


def print_separator(title=""):
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")
        

def print_results(results, show_details=True):
    """Print analysis results in a formatted way."""
    analysis = results['analysis']
    
    # Basic info
    print(f"🕒 Processing Time: {results['processing_time_seconds']:.2f} seconds")
    print(f"📊 Health Score: {analysis['health_score']}/10")
    print(f"📝 Ingredients Found: {analysis['total_ingredients']}")
    print(f"🔍 Known Ingredients: {analysis['known_ingredients']}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"   {results['summary']}")
    
    # Personal allergen warnings
    if results.get('personal_allergen_warnings'):
        print(f"\n🚨 ALLERGEN ALERTS:")
        for warning in results['personal_allergen_warnings']:
            print(f"   {warning['message']}")
    
    # Recommendations
    if results.get('recommendations'):
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    
    if show_details and analysis['ingredient_details']:
        print(f"\n🧪 Ingredient Details:")
        for ingredient in analysis['ingredient_details']:
            concern_emoji = {
                'low': '✅',
                'moderate': '⚠️',
                'high': '🚨',
                'severe': '💀'
            }.get(ingredient['health_concern'], '❓')
            
            print(f"\n   {concern_emoji} {ingredient['name']}")
            print(f"      Purpose: {ingredient['purpose']}")
            print(f"      Health Concern: {ingredient['health_concern'].title()}")
            if ingredient['allergens']:
                print(f"      Allergens: {', '.join(ingredient['allergens'])}")
            print(f"      Info: {ingredient['safety_info'][:80]}...")

def demo_energy_drink():
    """Demo analysis of a typical energy drink."""
    print_separator("DEMO 1: ENERGY DRINK ANALYSIS")
    
    # Typical energy drink ingredients (including your glucuronolactone!)
    energy_drink_ingredients = """
    Ingredients: Carbonated Water, Sucrose, Glucose, Citric Acid, 
    Taurine, Sodium Citrate, Caffeine, Inositol, Niacinamide, 
    Calcium Pantothenate, Pyridoxine HCl, Vitamin B12, Natural 
    and Artificial Flavors, Colors (Caramel Color, Red 40), 
    Glucuronolactone
    """
    
    print("🥤 Analyzing: Energy Drink")
    print(f"📄 Ingredients: {energy_drink_ingredients.strip()}")
    
    this = THISProcessor()
    results = this.analyze_text_directly(energy_drink_ingredients)
    
    print_results(results)
    
    # Special highlight for glucuronolactone
    glucurono_found = any(
        'glucuronolactone' in ingredient['name'].lower() 
        for ingredient in results['analysis']['ingredient_details']
    )
    
    if glucurono_found:
        print(f"\n🎯 SPECIAL HIGHLIGHT - Glucuronolactone Found!")
        for ingredient in results['analysis']['ingredient_details']:
            if 'glucuronolactone' in ingredient['name'].lower():
                print(f"   ✨ {ingredient['name']}: {ingredient['description']}")
                print(f"   📚 Safety Info: {ingredient['safety_info']}")
                break

def demo_allergen_warnings():
    """Demo personal allergen warnings."""
    print_separator("DEMO 2: PERSONAL ALLERGEN WARNINGS")
    
    # Food with common allergens
    cookie_ingredients = """
    Ingredients: Enriched Wheat Flour (Wheat Flour, Niacin, Reduced Iron, 
    Thiamine Mononitrate, Riboflavin, Folic Acid), Sugar, Vegetable Oil 
    (Palm, Soybean), Cocoa Powder, Eggs, Milk, Salt, Baking Soda, 
    Natural Vanilla Flavor, Almonds, May Contain: Peanuts, Tree Nuts
    """
    
    # Simulate user with allergies
    user_allergies = ["milk", "eggs", "nuts", "wheat"]
    
    print("🍪 Analyzing: Chocolate Chip Cookies")
    print(f"👤 User Allergies: {', '.join(user_allergies)}")
    print(f"📄 Ingredients: {cookie_ingredients.strip()}")
    
    this = THISProcessor()
    results = this.analyze_text_directly(cookie_ingredients, user_allergies=user_allergies)
    
    print_results(results, show_details=False)

def demo_multilingual():
    """Demo multi-language support."""
    print_separator("DEMO 3: MULTI-LANGUAGE SUPPORT")
    
    # Spanish ingredients
    spanish_ingredients = """
    Ingredientes: Agua, azúcar, ácido cítrico, sabores naturales, 
    conservante (benzoato de sodio), colorante amarillo 5, 
    edulcorante artificial (aspartamo)
    """
    
    print("🌍 Analyzing: Spanish Food Label")
    print(f"📄 Original: {spanish_ingredients.strip()}")
    
    this = THISProcessor()
    results = this.analyze_text_directly(spanish_ingredients)
    
    # Show translation info
    if results.get('translation'):
        trans = results['translation']
        print(f"\n🔤 Language Detection: {trans['detected_language'].upper()}")
        print(f"📝 Translated: {trans['translated']}")
    
    print_results(results, show_details=False)

def demo_health_comparison():
    """Demo health score comparison between different products."""
    print_separator("DEMO 4: HEALTH SCORE COMPARISON")
    
    products = [
        {
            'name': '🥤 Soda',
            'ingredients': 'Carbonated Water, High Fructose Corn Syrup, Caramel Color, Phosphoric Acid, Natural Flavors, Caffeine, Aspartame, Potassium Benzoate'
        },
        {
            'name': '🥛 Organic Juice', 
            'ingredients': 'Organic Apple Juice, Organic Orange Juice, Natural Flavors, Vitamin C, Citric Acid'
        },
        {
            'name': '💊 Energy Bar',
            'ingredients': 'Dates, Almonds, Cashews, Organic Cocoa Powder, Sea Salt, Natural Vanilla Extract'
        }
    ]
    
    this = THISProcessor()
    scores = []
    
    for product in products:
        print(f"\n{product['name']}")
        print(f"📄 Ingredients: {product['ingredients']}")

        results = this.analyze_text_directly(product['ingredients'])
        score = results['analysis']['health_score']
        scores.append((product['name'], score))

        print(f"📊 Health Score: {score}/10")
        print(f"📝 Summary: {results['summary']}")
    
    # Show ranking
    print(f"\n🏆 HEALTH RANKING:")
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(sorted_scores, 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
        print(f"   {medal} {name}: {score}/10")

def demo_unknown_ingredients():
    """Demo handling of unknown ingredients."""
    print_separator("DEMO 5: UNKNOWN INGREDIENTS HANDLING")
    
    # Mix of known and unknown ingredients
    mystery_ingredients = """
    Ingredients: Water, Xylitol, Erythritol, Natural Flavors, 
    Monk Fruit Extract, Stevia Leaf Extract, Potassium Sorbate, 
    Methylcobalamin, Pterostilbene, Resveratrol, Quercetin
    """
    
    print("❓ Analyzing: Product with Unknown Ingredients")
    print(f"📄 Ingredients: {mystery_ingredients.strip()}")
    
    this = THISProcessor()
    results = this.analyze_text_directly(mystery_ingredients)
    
    print_results(results, show_details=False)
    
    # Highlight unknown ingredients
    unknown_count = results['analysis']['total_ingredients'] - results['analysis']['known_ingredients']
    if unknown_count > 0:
        print(f"\n❓ Unknown Ingredients Found: {unknown_count}")
        print("💡 The system flags unknown ingredients for your research")

def main():
    """Run all demos."""
    print("🍎 THIS - The Hell Is This? - DEMO")
    print("Demonstrating AI-powered ingredient analysis capabilities")
    
    try:
        demo_energy_drink()
        demo_allergen_warnings()
        demo_multilingual()
        demo_health_comparison()
        demo_unknown_ingredients()
        
        print_separator("DEMO COMPLETE")
        print("✅ All demos completed successfully!")
        print("\n🚀 Next Steps:")
        print("   1. Run 'python app.py' for the web interface")
        print("   2. Visit http://localhost:5000")
        print("   3. Upload your own food label images")
        print("   4. Add your personal allergies for custom warnings")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()