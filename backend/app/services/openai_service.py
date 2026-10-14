import os
import time
import logging
from typing import List, Dict, Any, Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
GENERATION_MODEL = os.getenv("OPENAI_GENERATION_MODEL", "gpt-4o-mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

_openrouter_client = None
_ollama_client = None


def is_insufficient_quota(error: Exception) -> bool:
    """Return whether an OpenAI error specifically reports an exhausted quota."""
    if getattr(error, "code", None) in {"insufficient_quota", "credit_balance_exhausted"}:
        return True

    body = getattr(error, "body", None)
    if isinstance(body, dict):
        details = body.get("error", body)
        if isinstance(details, dict):
            return details.get("code") in {"insufficient_quota", "credit_balance_exhausted"}
    return False


def _get_openrouter_client():
    global _openrouter_client
    if _openrouter_client is None:
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        if not api_key:
            return None
        
        base_url = os.getenv("OPENAI_BASE_URL")
        if not base_url and api_key.startswith("sk-or-"):
            base_url = "https://openrouter.ai/api/v1"
            
        client_kwargs = {"api_key": api_key, "timeout": 35.0}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        _openrouter_client = OpenAI(**client_kwargs)
    return _openrouter_client


def _get_ollama_client():
    global _ollama_client
    if _ollama_client is None:
        if OpenAI is None:
            return None
        base_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        _ollama_client = OpenAI(base_url=base_url, api_key="ollama", timeout=60.0)
    return _ollama_client


def get_embeddings(texts: List[str], model: str | None = None) -> List[List[float]]:
    client = _get_openrouter_client()
    if client:
        model = model or os.getenv("OPENAI_EMBEDDING_MODEL") or EMBEDDING_MODEL
        try:
            resp = client.embeddings.create(input=texts, model=model)
            return [d.embedding for d in resp.data]
        except Exception as e:
            logger.warning(f"[Embeddings] OpenRouter embedding failed: {e}. Falling back to local embeddings.")
    
    # Deterministic local fallback embeddings
    from .rag_service import _approx_embedding
    return [_approx_embedding(t) for t in texts]


def chat_completion(
    messages: List[Dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int | None = None,
    response_format: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute chat completion with automatic failover between Ollama and OpenRouter."""
    preferred_provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    
    providers_to_try = []
    if preferred_provider == "ollama":
        providers_to_try = ["ollama", "openrouter"]
    elif preferred_provider in {"openrouter", "openai"}:
        providers_to_try = ["openrouter", "ollama"]
    else:  # "auto": check OpenRouter first for speed, with Ollama fallback
        providers_to_try = ["openrouter", "ollama"]
        
    last_error = None
    
    for provider in providers_to_try:
        try:
            if provider == "ollama":
                ollama_client = _get_ollama_client()
                if not ollama_client:
                    continue
                target_model = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)
                logger.info(f"[LLM] Trying Ollama local model {target_model}...")
                
                kwargs = {
                    "model": target_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens or 1500,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                    
                resp = ollama_client.chat.completions.create(**kwargs)
                content = resp.choices[0].message.content
                logger.info(f"[LLM] Ollama response received ({len(content)} chars)")
                return {"choices": [{"message": {"content": content}}]}
                
            elif provider == "openrouter":
                openrouter_client = _get_openrouter_client()
                if not openrouter_client:
                    continue
                target_model = model or os.getenv("OPENAI_GENERATION_MODEL") or GENERATION_MODEL
                logger.info(f"[LLM] Trying OpenRouter model {target_model}...")
                
                kwargs = {
                    "model": target_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens or 1500,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                    
                resp = openrouter_client.chat.completions.create(**kwargs)
                content = resp.choices[0].message.content
                logger.info(f"[LLM] OpenRouter response received ({len(content)} chars)")
                return {"choices": [{"message": {"content": content}}]}
                
        except Exception as err:
            logger.warning(f"[LLM] Provider {provider} failed: {err}")
            last_error = err
            continue

    if last_error:
        raise last_error
    raise RuntimeError("No LLM provider available (both Ollama and OpenRouter failed).")
