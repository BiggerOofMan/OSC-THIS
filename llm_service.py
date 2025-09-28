"""
LLM Service for ingredient research using Meta Llama-3.3-70B
Supports multiple providers: Ollama, Together AI, OpenAI-compatible APIs
"""

import os
import re
import json
import logging
import requests
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    TOGETHER = "together"
    OPENAI_COMPATIBLE = "openai_compatible"
    OPENAI = "openai"

@dataclass
class LLMConfig:
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 500
    # optional: override auth header name and prefix (prefix e.g. 'Bearer ')
    auth_header: str = 'Authorization'
    auth_prefix: str = 'Bearer '

@dataclass
class IngredientResearchResult:
    ingredient_name: str
    description: str
    purpose: str
    health_concerns: str
    safety_level: str  # low, moderate, high, severe

class LLMIngredientResearcher:
    """Uses LLM to research unknown ingredients"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._get_default_config()
        self._validate_config()
        # When an auth error occurs we'll disable further calls for this process to avoid
        # spamming logs and hitting rate limits on a misconfigured key/proxy.
        self._disabled_due_to_auth = False
        # When network errors occur repeatedly, temporarily disable calls for a cooldown
        self._network_disabled_until = 0.0
    
    def _get_default_config(self) -> LLMConfig:
        # choose provider by available env
        base = os.getenv('OPENAI_BASE_URL') or os.getenv('LLM_BASE_URL')
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')
        model = os.getenv('LLM_MODEL_NAME') or os.getenv('OPENAI_MODEL_NAME') or 'llama-3.3-70b-instruct'
        provider = LLMProvider.OPENAI_COMPATIBLE
        # allow override of auth header name and prefix via env
        auth_header = os.getenv('LLM_AUTH_HEADER') or os.getenv('OPENAI_AUTH_HEADER') or 'Authorization'
        auth_prefix = os.getenv('LLM_AUTH_PREFIX') or os.getenv('OPENAI_AUTH_PREFIX') or 'Bearer '
        return LLMConfig(provider=provider, model_name=model, api_key=api_key, base_url=base, auth_header=auth_header, auth_prefix=auth_prefix)
    
    def _validate_config(self):
        if not self.config.base_url or not self.config.api_key:
            raise RuntimeError("LLM config missing base_url or api_key")
    
    def research_ingredient(self, ingredient_name: str) -> Optional[IngredientResearchResult]:
        prompt = self._create_research_prompt(ingredient_name)
        resp = self._call_openai_compatible(prompt)
        if not resp:
            return None
        parsed = self._parse_llm_response(ingredient_name, resp)
        return parsed
    
    def _create_research_prompt(self, ingredient_name: str) -> str:
        return (
            f"You are a food-ingredient expert. For the ingredient token: '{ingredient_name}' "
            "return a concise JSON object with keys: name, description, purpose, health_concerns, safety_level "
            "(one of: low, moderate, high, severe). Keep answers factual and concise."
        )
    
    def _call_openai_compatible(self, prompt: str) -> Optional[str]:
        # Short-circuit if we've previously seen an auth failure for this process
        if getattr(self, '_disabled_due_to_auth', False):
            logger.debug("LLM calls disabled due to earlier authentication failure.")
            return None
        # Short-circuit if network disabled and cooldown hasn't expired
        if time.time() < getattr(self, '_network_disabled_until', 0):
            logger.debug("LLM calls temporarily disabled due to recent network errors (cooldown active).")
            return None
        try:
            url = self.config.base_url.rstrip('/') + '/v1/chat/completions'
            # Build auth header from config (prefix + key). The header name and prefix can be overridden by env vars
            headers = {'Content-Type': 'application/json'}
            try:
                header_name = getattr(self.config, 'auth_header', 'Authorization') or 'Authorization'
                header_prefix = getattr(self.config, 'auth_prefix', 'Bearer ') or ''
                # Avoid including None
                token = self.config.api_key or ''
                headers[header_name] = f"{header_prefix}{token}"
            except Exception:
                # fallback to default Authorization: Bearer KEY
                headers['Authorization'] = f'Bearer {self.config.api_key}'
            body = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": min(self.config.max_tokens, 400),
                "temperature": self.config.temperature
            }
            # retry on transient network errors with exponential backoff
            backoff = [1, 2, 4]
            r = None
            last_exc = None
            for wait in backoff:
                try:
                    r = requests.post(url, headers=headers, json=body, timeout=20)
                    break
                except requests.exceptions.RequestException as e:
                    last_exc = e
                    logger.debug("LLM request attempt failed (will retry): %s", e)
                    time.sleep(wait)
            if r is None and last_exc is not None:
                # disable briefly to avoid log spam
                self._network_disabled_until = time.time() + 60
                logger.warning("LLM request failed due to network error: %s. Disabling LLM calls for 60s.", str(last_exc))
                return None
            # Sanitize logging: don't include potentially sensitive response bodies or keys
            if r.status_code == 401:
                # Mark disabled so subsequent calls won't spam
                self._disabled_due_to_auth = True
                try:
                    short = r.json().get('error', {}).get('message', 'authentication error')
                except Exception:
                    short = 'authentication error (401)'
                logger.warning("LLM call failed 401: %s. LLM calls disabled until config is fixed.", short)
                return None
            if r.status_code >= 400:
                logger.warning("LLM call failed %s", r.status_code)
                return None
            j = r.json()
            # Common response shape: choices[0].message.content
            content = None
            if isinstance(j, dict):
                if 'choices' in j and len(j['choices']) > 0:
                    c0 = j['choices'][0]
                    if isinstance(c0, dict) and 'message' in c0 and 'content' in c0['message']:
                        content = c0['message']['content']
                    elif 'text' in c0:
                        content = c0.get('text')
            if not content:
                # fallback: try to get text
                content = r.text
            return content
        except requests.exceptions.RequestException as e:
            logger.warning("LLM request network error: %s", e)
            return None
        except Exception as e:
            logger.warning("LLM request error: %s", e)
            return None
    
    def _parse_llm_response(self, ingredient_name: str, response: str) -> Optional[IngredientResearchResult]:
        # try to extract JSON from response
        try:
            m = re.search(r'(\{[\s\S]*\})', response)
            if m:
                data = json.loads(m.group(1))
                name = data.get('name') or ingredient_name
                return IngredientResearchResult(
                    ingredient_name = name,
                    description = data.get('description',''),
                    purpose = data.get('purpose',''),
                    health_concerns = data.get('health_concerns',''),
                    safety_level = data.get('safety_level','moderate')
                )
            # fallback: try to interpret plain text lines
            lines = [l.strip() for l in response.splitlines() if l.strip()]
            if lines:
                # very simple heuristic
                return IngredientResearchResult(ingredient_name=lines[0], description=' '.join(lines[1:])[:1000], purpose='', health_concerns='', safety_level='moderate')
        except Exception as e:
            logger.warning("Failed to parse LLM response: %s", e)
        return None

    def normalize_name(self, ocr_name: str) -> Optional[str]:
        prompt = (
            f"Normalize this OCR-mangled ingredient token into a canonical single ingredient name.\n"
            f"Input: {ocr_name}\n"
            "Return only the canonical name (no explanation)."
        )
        resp = self._call_openai_compatible(prompt)
        if not resp:
            return None
        # take first line and clean
        first = resp.strip().splitlines()[0]
        return re.sub(r'[^A-Za-z0-9 \-]', '', first).strip()
    
    def score_product_health(self, ingredients: List[str], brief_context: str = "") -> Optional[Dict[str, Any]]:
        prompt = (
            f"You are a food-safety expert. Given these ingredients: {', '.join(ingredients)}\n"
            "Return a JSON object with keys: product_score (0-10 float), confidence (0-1), "
            "ingredient_scores: list of {name, score (0-10), short_reason}. Return only JSON."
        )
        resp = self._call_openai_compatible(prompt)
        if not resp:
            return None
        try:
            m = re.search(r'(\{[\s\S]*\})', resp)
            if m:
                return json.loads(m.group(1))
        except Exception as e:
            logger.warning("Failed to parse score JSON: %s", e)
        return None

def create_llm_researcher() -> Optional[LLMIngredientResearcher]:
    try:
        cfg = LLMConfig(
            provider = LLMProvider.OPENAI_COMPATIBLE,
            model_name = os.getenv('LLM_MODEL_NAME') or os.getenv('OPENAI_MODEL_NAME') or 'llama-3.3-70b-instruct',
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY'),
            base_url = os.getenv('OPENAI_BASE_URL') or os.getenv('LLM_BASE_URL')
        )
        if not cfg.api_key or not cfg.base_url:
            logger.info("LLM config incomplete (no api_key/base_url)")
            return None
        return LLMIngredientResearcher(cfg)
    except Exception as e:
        logger.warning("create_llm_researcher error: %s", e)
        return None

# Example quick test disabled by default
if __name__ == "__main__":
    r = create_llm_researcher()
    print("researcher:", bool(r))