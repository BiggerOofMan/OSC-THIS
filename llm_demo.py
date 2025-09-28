"""
Demo script showcasing LLM ingredient research with Meta Llama-3.3-70B
"""

import os
from this_processor import THISProcessor

def demo_llm_research():
    """Demonstrate LLM-powered ingredient research"""
    
    print("🤖 THIS + LLM Demo - Unknown Ingredient Research")
    print("=" * 60)
    print()
    
    # Check for LLM configuration
    llm_config_status = []
    if os.getenv('OLLAMA_HOST'):
        llm_config_status.append("✅ Ollama configured")
    if os.getenv('TOGETHER_API_KEY'):
        llm_config_status.append("✅ Together AI configured")
    if os.getenv('OPENAI_API_KEY'):
        llm_config_status.append("✅ OpenAI configured")
    
    if llm_config_status:
        print("LLM Configuration:")
        for status in llm_config_status:
            print(f"  {status}")
    else:
        print("⚠️  No LLM configuration found. Using static database only.")
        print("   To enable AI research, see config.env.example")
    
    print("\n" + "=" * 60)
    
    # Initialize processor
    processor = THISProcessor()
    
    # Test ingredients with some unknown ones
    test_ingredients = """
    Ingredients: Water, High Fructose Corn Syrup, Citric Acid, Natural Flavors, 
    Sodium Benzoate (Preservative), Caffeine, Glucuronolactone, Aspartame 
    (Contains Phenylalanine), Yellow 5, Methylparaben, Propylparaben, 
    Carrageenan, Xanthan Gum, Polysorbate 80
    """
    
    print(f"📝 Analyzing ingredients with potential LLM research:")
    print(f"Input: {test_ingredients.strip()}")
    print("\n" + "-" * 60)
    
    # Analyze
    try:
        results = processor.analyze_text_directly(test_ingredients, user_allergies=["milk"])
        
        # Display basic results
        print(f"\n📊 Analysis Results:")
        print(f"Health Score: {results['analysis']['health_score']}/10")
        print(f"Total Ingredients: {results['analysis']['total_ingredients']}")
        print(f"Known Ingredients: {results['analysis']['known_ingredients']}")
        
        # LLM Research Summary
        llm_info = results['llm_research_info']
        print(f"\n🤖 LLM Research Summary:")
        print(f"Research Enabled: {'Yes' if llm_info['research_enabled'] else 'No'}")
        print(f"Ingredients Researched: {llm_info['total_researched']}")
        print(f"High Confidence Results: {llm_info['high_confidence_results']}")
        print(f"Low Confidence Results: {llm_info['low_confidence_results']}")
        
        # Show researched ingredients details
        if llm_info['researched_ingredients']:
            print(f"\n🔍 AI-Researched Ingredients:")
            for ingredient in llm_info['researched_ingredients']:
                confidence_emoji = "✅" if ingredient['confidence'] >= 0.7 else "⚠️"
                print(f"  {confidence_emoji} {ingredient['name']}")
                print(f"     Purpose: {ingredient['purpose']}")
                print(f"     Safety: {ingredient['safety_level'].title()}")
                print(f"     Natural: {'Yes' if ingredient['natural'] else 'No'}")
                print(f"     Confidence: {ingredient['confidence']:.2f}")
                print()
        
        # Show detailed ingredient info for first few
        print(f"\n📋 Detailed Ingredient Information:")
        for i, ingredient in enumerate(results['analysis']['ingredient_details'][:5]):
            is_llm_research = ingredient['description'].startswith('LLM Research')
            source_emoji = "🤖" if is_llm_research else "📚"
            
            print(f"\n  {source_emoji} {ingredient['name']}")
            print(f"     Description: {ingredient['description'][:100]}...")
            print(f"     Purpose: {ingredient['purpose']}")
            print(f"     Health Concern: {ingredient['health_concern'].title()}")
            print(f"     Natural: {'Yes' if ingredient['natural'] else 'No'}")
            if ingredient['allergens']:
                print(f"     Allergens: {', '.join(ingredient['allergens'])}")
        
        # Summary and recommendations
        print(f"\n📝 Summary:")
        print(f"{results['summary']}")
        
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n⏱️  Processing time: {results['processing_time_seconds']:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    return True

def setup_instructions():
    """Show setup instructions for different LLM providers"""
    
    print("\n" + "=" * 60)
    print("🛠️  LLM Setup Instructions")
    print("=" * 60)
    
    print("""
📋 To enable AI-powered ingredient research with Llama-3.3-70B:

1️⃣  OLLAMA (Local - Best for privacy):
   • Install Ollama: https://ollama.ai/
   • Run: ollama pull llama3.3:70b
   • Set environment: OLLAMA_HOST=http://localhost:11434
   • Pros: Free, private, works offline
   • Cons: Requires ~40GB disk space, slower on CPU

2️⃣  TOGETHER AI (Cloud - Best for performance):
   • Sign up: https://api.together.xyz/
   • Get API key from dashboard
   • Set environment: TOGETHER_API_KEY=your_key_here
   • Pros: Fast, no local resources needed
   • Cons: Costs money, requires internet

3️⃣  OTHER PROVIDERS:
   • Many providers support Llama-3.3-70B via OpenAI-compatible APIs
   • Set: LLM_API_KEY and LLM_BASE_URL
   • Examples: Groq, Anyscale, Fireworks AI

4️⃣  FALLBACK (OpenAI):
   • Uses GPT-3.5-Turbo if no Llama access
   • Set: OPENAI_API_KEY=sk-your_key_here
   • Pros: Reliable, fast
   • Cons: Not Llama-3.3-70B, costs money

💡 Create a .env file with your chosen configuration!
""")

if __name__ == "__main__":
    # Run demo
    success = demo_llm_research()
    
    if not success:
        setup_instructions()
    
    print("\n" + "=" * 60)
    print("🎯 Demo complete! Check the results above.")
    print("💡 Tip: Run with LLM configured for best results!")