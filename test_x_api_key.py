#!/usr/bin/env python3
"""
Test X-API-Key authentication format specifically
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_x_api_key_format():
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model_name = os.getenv('LLM_MODEL_NAME')
    
    print("🔑 Testing X-API-Key Authentication Format")
    print("=" * 50)
    
    url = base_url.rstrip('/') + '/v1/chat/completions'
    
    # Try X-API-Key format (common for LiteLLM)
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key  # No Bearer prefix
    }
    
    body = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        print(f"🌐 Testing: {url}")
        print(f"🔑 Header: X-API-Key: {api_key[:15]}...")
        print(f"🤖 Model: {model_name}")
        
        response = requests.post(url, headers=headers, json=body, timeout=20)
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! X-API-Key format works!")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_x_api_key_format()
    if success:
        print(f"\n🎯 X-API-Key format works! Your environment is correctly configured.")
    else:
        print(f"\n❌ X-API-Key format also failed. The issue might be:")
        print("1. Your API key is not valid/expired")
        print("2. You need to be on UF VPN")
        print("3. The key isn't registered in their LiteLLM database")
        print("4. Contact UF IT for API access verification")