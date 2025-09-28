import os
import sys
import json
import requests

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

base = os.getenv('OPENAI_BASE_URL') or os.getenv('LLM_BASE_URL')
api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')

if not base or not api_key:
    print('Missing base URL or API key in environment (.env).')
    print('OPENAI_BASE_URL:', os.getenv('OPENAI_BASE_URL'))
    print('LLM_BASE_URL:', os.getenv('LLM_BASE_URL'))
    print('OPENAI_API_KEY set:', bool(os.getenv('OPENAI_API_KEY')))
    print('LLM_API_KEY set:', bool(os.getenv('LLM_API_KEY')))
    sys.exit(2)

base = base.rstrip('/')

def try_get(path):
    url = f"{base}{path}"
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print('\nREQUEST:', url)
        print('STATUS:', resp.status_code)
        try:
            print('JSON:', json.dumps(resp.json(), indent=2))
        except Exception:
            print('TEXT:', resp.text[:200])
    except Exception as e:
        print('\nREQUEST:', url)
        print('ERROR:', e)

# Try common OpenAI-compatible model listing endpoints
try_get('/v1/models')
try_get('/models')

# Also try a simple chat call to the configured model name (if provided)
model = os.getenv('LLM_MODEL_NAME') or os.getenv('OPENAI_MODEL_NAME') or 'llama-3.3-70b-instruct'
url = f"{base}/v1/chat/completions"
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
body = {
    'model': model,
    'messages': [{'role': 'user', 'content': 'Say hi'}],
    'max_tokens': 1
}
try:
    resp = requests.post(url, headers=headers, json=body, timeout=10)
    print('\nPOST:', url)
    print('STATUS:', resp.status_code)
    try:
        print('JSON:', json.dumps(resp.json(), indent=2))
    except Exception:
        print('TEXT:', resp.text[:400])
except Exception as e:
    print('\nPOST:', url)
    print('ERROR:', e)
