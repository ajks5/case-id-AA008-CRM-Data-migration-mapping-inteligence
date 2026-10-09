"""
Configuration loader for Controlled LLM Enhancement.
Adheres to Feeder Guide §5:
- Uses environment variables
- Never commits or leaks API keys
- Supports provider, model, timeout, and master enable switch
"""

import os
from typing import Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuration for LLM Service Adapter."""
    provider: str = "mock"       # "gemini" | "openai" | "mock"
    model: str = "gemini-2.5-flash-lite"
    api_key: Optional[str] = None
    timeout: float = 10.0
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load LLM configuration strictly from environment variables."""
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        generic_key = os.getenv("LLM_API_KEY")

        provider_env = os.getenv("LLM_PROVIDER", "").strip().lower()
        if provider_env:
            provider = provider_env
        elif gemini_key or generic_key:
            provider = "gemini"
        elif openai_key:
            provider = "openai"
        else:
            provider = "mock"

        # Resolve API key based on selected provider
        api_key: Optional[str] = None
        if provider == "gemini":
            api_key = gemini_key or generic_key
        elif provider == "openai":
            api_key = openai_key or generic_key
        else:
            api_key = None

        # Resolve model name
        default_model = "gemini-2.5-flash-lite" if provider == "gemini" else ("gpt-4o-mini" if provider == "openai" else "mock-v1")
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
            api_key=api_key,
            timeout=timeout,
            enabled=enabled,
        )
