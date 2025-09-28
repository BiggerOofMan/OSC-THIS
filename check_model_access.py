import os
import sys
import json
# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Minimal test to check OpenAI-compatible model access using environment variables
# Uses the new openai.OpenAI client (package 'openai')

try:
    from openai import OpenAI
except Exception as e:
    print("Missing 'openai' library. Install with: python -m pip install openai")
    sys.exit(2)

api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')
base = os.getenv('OPENAI_BASE_URL') or os.getenv('LLM_BASE_URL')
model = os.getenv('LLM_MODEL_NAME') or os.getenv('OPENAI_MODEL_NAME') or 'llama-3.3-70b-instruct'

if not api_key or not base:
    print('Missing API key or base URL. Check your .env or environment variables.')
    print('OPENAI_API_KEY:', bool(os.getenv('OPENAI_API_KEY')))
    print('LLM_API_KEY:', bool(os.getenv('LLM_API_KEY')))
    print('OPENAI_BASE_URL:', os.getenv('OPENAI_BASE_URL'))
    print('LLM_BASE_URL:', os.getenv('LLM_BASE_URL'))
    sys.exit(2)

print(f"Using base={base}, model={model}")

client = OpenAI(api_key=api_key, base_url=base)

try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Provide a one-sentence definition of methylparaben."}],
        max_tokens=60,
        temperature=0.0,
        timeout=15
    )
    # print the returned content
    text = resp.choices[0].message.content
    print('SUCCESS:')
    print(text)
    sys.exit(0)

except Exception as e:
    print('ERROR: Exception while calling model:')
    try:
        # Try to print JSON-like details if available
        err_str = str(e)
        print(err_str)
    except:
        pass
    import traceback
    traceback.print_exc()
    sys.exit(3)
