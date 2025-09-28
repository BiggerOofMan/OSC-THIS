#!/usr/bin/env python3
"""
Test API connection to the configured endpoint
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_api_connection():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    model_name = os.getenv('LLM_MODEL_NAME')
    
    print("🔗 Testing API Connection")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Model: {model_name}")
    print(f"API Key: {api_key[:10] if api_key else 'Not set'}...")
    
    if not api_key or not base_url:
        print("❌ Missing API key or base URL in .env file")
        return False
    
    # Test the connection
    url = base_url.rstrip('/') + '/v1/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    body = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hello, are you working?"}],
        "max_tokens": 50,
        "temperature": 0.3
    }
    
    try:
        print(f"\n🌐 Testing connection to: {url}")
        print("📤 Sending test request...")
        
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            try:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    print(f"🤖 Model response: {content}")
                return True
            except Exception as e:
                print(f"⚠️ Response parsing error: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return True  # Connection worked even if parsing failed
        
        elif response.status_code == 401:
            print("❌ Authentication failed (401)")
            print("🔑 Check your API key in the .env file")
            return False
        
        elif response.status_code == 404:
            print("❌ Endpoint not found (404)")
            print("🌐 Check your base URL and model name")
            print(f"Attempted URL: {url}")
            return False
        
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("🌐 Check if the API endpoint is reachable")
        print("🔧 Possible issues:")
        print("   - VPN required to access UF AI API")
        print("   - Network firewall blocking the connection")
        print("   - API endpoint is down")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        print("⏱️ The API took too long to respond")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    print("\n" + "=" * 50)
    if success:
        print("✅ API connection is working!")
    else:
        print("❌ API connection failed!")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if you're connected to UF VPN")
        print("2. Verify API key is correct")
        print("3. Confirm the API endpoint is accessible")
        print("4. Try accessing the API URL in a browser")