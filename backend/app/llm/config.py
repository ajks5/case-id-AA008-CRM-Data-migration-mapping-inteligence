"""
Configuration loader for Controlled LLM Enhancement.
Adheres to Feeder Guide §5:
- Uses environment variables
- Never commits or leaks API keys
- Supports provider, model, timeout, and master enable switch
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class LLMConfig(BaseModel):
    """Configuration for LLM Service Adapter with multi-key switching."""
    provider: str = "mock"       # "gemini" | "openai" | "mock"
    model: str = "gemini-3.5-flash-lite"
    api_key: Optional[str] = None
    api_keys: List[str] = Field(default_factory=list)
    timeout: float = 10.0
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load LLM configuration strictly from environment variables."""
        # Support comma-separated multiple keys or single keys
        gemini_keys_raw = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY")
        openai_keys_raw = os.getenv("OPENAI_API_KEYS") or os.getenv("OPENAI_API_KEY")
        generic_keys_raw = os.getenv("LLM_API_KEYS") or os.getenv("LLM_API_KEY")

        provider_env = os.getenv("LLM_PROVIDER", "").strip().lower()
        if provider_env:
            provider = provider_env
        elif gemini_keys_raw or generic_keys_raw:
            provider = "gemini"
        elif openai_keys_raw:
            provider = "openai"
        else:
            provider = "mock"

        # Resolve raw key string
        raw_keys_str: Optional[str] = None
        if provider == "gemini":
            raw_keys_str = gemini_keys_raw or generic_keys_raw
        elif provider == "openai":
            raw_keys_str = openai_keys_raw or generic_keys_raw

        # Parse comma-separated keys into list
        api_keys: List[str] = []
        if raw_keys_str:
            for k in raw_keys_str.split(","):
                cleaned = k.strip()
                if cleaned and cleaned not in api_keys:
                    api_keys.append(cleaned)

        primary_api_key = api_keys[0] if api_keys else None

        # Resolve model name
        default_model = "gemini-3.5-flash-lite" if provider == "gemini" else ("gpt-4o-mini" if provider == "openai" else "mock-v1")
        model = os.getenv("LLM_MODEL", default_model).strip()

        # Resolve timeout
        try:
            timeout = float(os.getenv("LLM_TIMEOUT", "10.0"))
        except ValueError:
            timeout = 10.0

        # Master enable switch
        enabled_str = os.getenv("LLM_ENABLED", "true").strip().lower()
        enabled = enabled_str not in ("0", "false", "no", "off")

        return cls(
            provider=provider,
            model=model,
            api_key=primary_api_key,
            api_keys=api_keys,
            timeout=timeout,
            enabled=enabled,
        )
