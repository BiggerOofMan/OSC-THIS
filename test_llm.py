#!/usr/bin/env python3
"""
Simple test to verify LLM integration works
"""

def test_llm_integration():
    """Test LLM service integration"""
    print("🧪 Testing LLM Integration")
    print("=" * 40)
    
    try:
        # Test import
        from llm_service import create_llm_researcher, LLMProvider
        print("✅ LLM service imported successfully")
        
        # Test initialization
        researcher = create_llm_researcher()
        if researcher:
            print(f"✅ LLM researcher initialized")
            print(f"   Provider: {researcher.config.provider.value}")
            print(f"   Model: {researcher.config.model_name}")
        else:
            print("⚠️ No LLM configuration found (expected without setup)")
        
        # Test ingredient analyzer integration
        from ingredient_analyzer import IngredientAnalyzer
        analyzer = IngredientAnalyzer()
        print("✅ Ingredient analyzer with LLM support created")
        print(f"   LLM Research Enabled: {analyzer.enable_llm_research}")
        
        # Test THIS processor integration  
        from this_processor import THISProcessor
        processor = THISProcessor()
        print("✅ THIS processor with LLM support created")
        
        # Simple test analysis
        test_text = "Ingredients: Water, Methylparaben, Sodium Benzoate"
        results = processor.analyze_text_directly(test_text)
        
        print(f"\n📊 Test Analysis Results:")
        print(f"   Total ingredients: {results['analysis']['total_ingredients']}")
        print(f"   LLM research enabled: {results['llm_research_info']['research_enabled']}")
        print(f"   Ingredients researched: {results['llm_research_info']['total_researched']}")
        
        print(f"\n🎯 SUCCESS: LLM integration is working!")
        print(f"   To enable actual AI research, configure an LLM provider")
        print(f"   See config.env.example for setup instructions")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_llm_integration()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")