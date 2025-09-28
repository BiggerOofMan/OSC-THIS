#!/usr/bin/env python3
"""
Quick solution: Run the app without LLM research until API key is fixed
"""

import os
import subprocess
import sys

def run_app_without_llm():
    print("🚀 Starting THIS app WITHOUT LLM research")
    print("=" * 50)
    print("✅ The app will work fully except for AI ingredient research")
    print("✅ Known ingredients from database will still be analyzed")
    print("✅ All other features (OCR, translation, allergen warnings) work")
    print()
    
    # Temporarily unset LLM environment variables
    env_backup = {}
    llm_env_vars = ['OPENAI_API_KEY', 'OPENAI_BASE_URL', 'LLM_MODEL_NAME', 
                    'LLM_AUTH_HEADER', 'LLM_AUTH_PREFIX']
    
    for var in llm_env_vars:
        if var in os.environ:
            env_backup[var] = os.environ[var]
            del os.environ[var]
    
    print("🔧 Temporarily disabled LLM environment variables")
    print("🌐 Starting Flask app on http://localhost:5000...")
    print("⚠️  LLM research will be disabled until API key is fixed")
    print()
    print("🔧 TO FIX THE UF API KEY LATER:")
    print("1. Contact UF IT about your API key access")
    print("2. Verify you're on UF VPN if required")  
    print("3. Ask them to add your key to their LiteLLM verification table")
    print("4. Test with: python test_x_api_key.py")
    print()
    
    try:
        # Run the Flask app
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error running app: {e}")
    finally:
        # Restore environment variables
        for var, value in env_backup.items():
            os.environ[var] = value
        print("🔄 Restored LLM environment variables")

def show_instructions():
    print("\n📋 WHAT THIS DOES:")
    print("✅ Runs your app with LLM research temporarily disabled")
    print("✅ All other features work normally (OCR, database lookup, allergen warnings)")
    print("✅ You can still analyze food labels and get ingredient information")
    print("❌ Unknown ingredients won't be researched with AI (they'll show as 'Unknown')")
    print()
    print("🔧 TO RE-ENABLE LLM RESEARCH:")
    print("1. Fix your UF API key with IT support")
    print("2. Test: python test_x_api_key.py")
    print("3. When it works, restart normally: python app.py")
    print()
    
    choice = input("Continue? (y/n): ").strip().lower()
    return choice in ['y', 'yes', '']

if __name__ == "__main__":
    if show_instructions():
        run_app_without_llm()
    else:
        print("👋 Cancelled. No changes made.")