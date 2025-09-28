#!/usr/bin/env python3
"""
Test UF API endpoint for more information
"""

import os
import requests
from dotenv import load_dotenv

def explore_uf_api():
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    print("🔍 Exploring UF AI API Endpoint")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:15] if api_key else 'None'}...")
    
    endpoints_to_try = [
        "/v1/models",
        "/models", 
        "/health",
        "/v1/health",
        "",
        "/docs"
    ]
    
    for endpoint in endpoints_to_try:
        url = base_url.rstrip('/') + endpoint
        print(f"\n🌐 Testing: {url}")
        
        # Try without authentication first
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status (no auth): {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error (no auth): {e}")
        
        # Try with authentication
        if api_key:
            try:
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.get(url, headers=headers, timeout=10)
                print(f"   Status (with auth): {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.text[:200]}...")
                elif response.status_code == 401:
                    error_info = response.text[:300] if response.text else "No error details"
                    print(f"   Auth Error: {error_info}")
            except Exception as e:
                print(f"   Error (with auth): {e}")

def check_litellm_format():
    """Check if this needs LiteLLM specific format"""
    print(f"\n🤖 LiteLLM Authentication Tips:")
    print("=" * 50)
    print("Some LiteLLM proxies require:")
    print("1. Different header: 'X-API-Key' instead of 'Authorization'")
    print("2. No 'Bearer ' prefix")
    print("3. Model names in specific format")
    print("4. User/team authentication")
    print()
    print("Try setting these environment variables:")
    print("$env:LLM_AUTH_HEADER=\"X-API-Key\"")
    print("$env:LLM_AUTH_PREFIX=\"\"")

if __name__ == "__main__":
    explore_uf_api()
    check_litellm_format()