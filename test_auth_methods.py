#!/usr/bin/env python3
"""
Test different authentication methods for UF AI API
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_auth_methods():
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model_name = os.getenv('LLM_MODEL_NAME')
    
    if not api_key or not base_url:
        print("❌ Missing API key or base URL")
        return
    
    url = base_url.rstrip('/') + '/v1/chat/completions'
    
    body = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50,
        "temperature": 0.3
    }
    
    # Try different authentication methods
    auth_methods = [
        ("Authorization", f"Bearer {api_key}"),
        ("Authorization", api_key),
        ("X-API-Key", api_key),
        ("api-key", api_key),
        ("LiteLLM-Token", api_key),
        ("Token", api_key),
    ]
    
    print("🔑 Testing different authentication methods for UF AI API")
    print("=" * 60)
    
    for header_name, header_value in auth_methods:
        print(f"\n🧪 Testing: {header_name}: {header_value[:15]}...")
        
        headers = {
            'Content-Type': 'application/json',
            header_name: header_value
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! This authentication method works!")
                print(f"Use: {header_name}: {header_value}")
                return header_name, header_value
            elif response.status_code == 401:
                error_text = response.text[:200]
                print(f"❌ Auth failed: {error_text}")
            else:
                print(f"⚠️ Other error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Network error: {e}")
    
    print(f"\n❌ None of the authentication methods worked.")
    return None, None

if __name__ == "__main__":
    success_header, success_value = test_auth_methods()
    if success_header:
        print(f"\n🎯 SOLUTION FOUND!")
        print(f"Set these environment variables:")
        print(f"$env:LLM_AUTH_HEADER=\"{success_header}\"")
        if success_header != "Authorization" or not success_value.startswith("Bearer "):
            if success_value == os.getenv('OPENAI_API_KEY'):
                print(f"$env:LLM_AUTH_PREFIX=\"\"")
            else:
                print(f"$env:LLM_AUTH_PREFIX=\"{success_value.replace(os.getenv('OPENAI_API_KEY'), '')}\"")
    else:
        print(f"\n💡 Consider contacting UF IT support about the API access.")