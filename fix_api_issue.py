#!/usr/bin/env python3
"""
Fix network/authentication issues with LLM API
This script provides multiple solutions for the authentication error.
"""

import os
from pathlib import Path

def show_solutions():
    print("🔧 THIS PROJECT - API CONNECTION TROUBLESHOOTING")
    print("=" * 60)
    print()
    print("❌ PROBLEM: Getting 401 Authentication Error from UF AI API")
    print("   This means your API key is invalid or has expired.")
    print()
    
    print("✅ SOLUTION OPTIONS:")
    print()
    
    print("🎯 OPTION 1: Disable LLM Research (Quickest Fix)")
    print("   The app will work without AI ingredient research")
    print("   It will still analyze known ingredients from the database")
    print()
    
    print("🎯 OPTION 2: Use Ollama (Local AI - Free)")
    print("   Install Ollama locally for private AI research")
    print("   No API keys needed, runs entirely on your computer")
    print()
    
    print("🎯 OPTION 3: Use Together AI (Cloud - Paid)")
    print("   Use Together AI's cloud API for ingredient research")
    print("   Requires signing up and getting an API key")
    print()
    
    print("🎯 OPTION 4: Use OpenAI (Cloud - Paid)")
    print("   Use OpenAI's GPT models for ingredient research")
    print("   Requires OpenAI API key")
    print()
    
    print("🎯 OPTION 5: Fix UF API Key")
    print("   Contact UF IT or whoever provided your API key")
    print()

def apply_option_1():
    """Disable LLM research"""
    print("🔧 APPLYING OPTION 1: Disable LLM Research")
    print("=" * 50)
    
    # Create a new .env that disables LLM
    env_content = """# Local environment overrides for THIS project
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
SAVE_RESULTS=True
RESULTS_DIR=results
LOG_LEVEL=INFO
LOG_FILE=this.log

# LLM Research disabled to avoid authentication errors
# OPENAI_API_KEY=
# OPENAI_BASE_URL=
# LLM_MODEL_NAME=
"""
    
    # Backup current .env
    if os.path.exists('.env'):
        os.rename('.env', '.env.backup')
        print("✅ Backed up current .env to .env.backup")
    
    # Write new .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created new .env with LLM research disabled")
    print("✅ The app will now work without API calls")
    print()
    print("🧪 Test the fix:")
    print("   python test_llm.py")
    print("   python app.py")
    print()

def apply_option_2():
    """Setup Ollama"""
    print("🔧 APPLYING OPTION 2: Setup Ollama (Local AI)")
    print("=" * 50)
    
    print("📋 STEPS TO INSTALL OLLAMA:")
    print()
    print("1. Download Ollama from: https://ollama.ai/")
    print("2. Install Ollama on your computer")
    print("3. Open Command Prompt and run:")
    print("   ollama pull llama3.2:3b")
    print("4. Wait for download to complete (may take a while)")
    print()
    
    # Create .env for Ollama
    env_content = """# Local environment overrides for THIS project
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
SAVE_RESULTS=True
RESULTS_DIR=results
LOG_LEVEL=INFO
LOG_FILE=this.log

# Ollama configuration (Local AI)
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL_NAME=llama3.2:3b
"""
    
    print("🔧 CREATING OLLAMA .ENV CONFIGURATION...")
    
    # Backup current .env
    if os.path.exists('.env'):
        os.rename('.env', '.env.backup')
        print("✅ Backed up current .env to .env.backup")
    
    # Write new .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env configured for Ollama")
    print()
    print("🧪 After installing Ollama, test with:")
    print("   python test_api_connection.py")
    print()

def apply_option_3():
    """Setup Together AI"""
    print("🔧 APPLYING OPTION 3: Setup Together AI")
    print("=" * 50)
    
    print("📋 STEPS TO USE TOGETHER AI:")
    print()
    print("1. Go to: https://api.together.xyz/")
    print("2. Sign up for an account")
    print("3. Get your API key from the dashboard")
    print("4. Replace 'YOUR_TOGETHER_API_KEY' in the .env below")
    print()
    
    # Create .env for Together AI
    env_content = """# Local environment overrides for THIS project
TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
SAVE_RESULTS=True
RESULTS_DIR=results
LOG_LEVEL=INFO
LOG_FILE=this.log

# Together AI configuration
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=YOUR_TOGETHER_API_KEY
LLM_MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct-Turbo
"""
    
    print("🔧 CREATING TOGETHER AI .ENV TEMPLATE...")
    
    # Backup current .env
    if os.path.exists('.env'):
        os.rename('.env', '.env.backup')
        print("✅ Backed up current .env to .env.backup")
    
    # Write new .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env template for Together AI")
    print("⚠️ REMEMBER: Replace 'YOUR_TOGETHER_API_KEY' with your actual key!")
    print()

def main():
    show_solutions()
    
    print("🤔 Which option would you like to try?")
    print()
    print("Enter:")
    print("  1 - Disable LLM Research (Quick fix)")
    print("  2 - Setup Ollama (Free, local)")
    print("  3 - Setup Together AI (Paid, cloud)")
    print("  4 - Show OpenAI setup")
    print("  0 - Just show info, don't change anything")
    print()
    
    try:
        choice = input("Your choice (0-4): ").strip()
        print()
        
        if choice == '1':
            apply_option_1()
        elif choice == '2':
            apply_option_2()
        elif choice == '3':
            apply_option_3()
        elif choice == '4':
            print("🔧 OPTION 4: OpenAI Setup")
            print("1. Get API key from: https://platform.openai.com/")
            print("2. Replace OPENAI_API_KEY in .env with your key")
            print("3. Set OPENAI_BASE_URL=https://api.openai.com/v1")
            print("4. Set LLM_MODEL_NAME=gpt-3.5-turbo")
        elif choice == '0':
            print("ℹ️ No changes made. You can run this script again anytime.")
        else:
            print("❌ Invalid choice. No changes made.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled. No changes made.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()