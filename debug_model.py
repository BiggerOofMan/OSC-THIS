#!/usr/bin/env python3
"""
Debug script to check what model name is being used
"""

import os
from dotenv import load_dotenv

def debug_model_name():
    # Load environment variables
    load_dotenv()
    
    print("🔍 Debugging Model Name Configuration")
    print("=" * 50)
    
    # Check all possible sources
    llm_model = os.getenv('LLM_MODEL_NAME')
    openai_model = os.getenv('OPENAI_MODEL_NAME')
    
    print(f"LLM_MODEL_NAME from env: '{llm_model}'")
    print(f"OPENAI_MODEL_NAME from env: '{openai_model}'")
    
    # Check what the LLM service would use
    from llm_service import create_llm_researcher
    
    try:
        researcher = create_llm_researcher()
        if researcher:
            print(f"LLM Service model_name: '{researcher.config.model_name}'")
            print(f"LLM Service base_url: '{researcher.config.base_url}'")
        else:
            print("❌ Could not create LLM researcher")
    except Exception as e:
        print(f"❌ Error creating researcher: {e}")

if __name__ == "__main__":
    debug_model_name()