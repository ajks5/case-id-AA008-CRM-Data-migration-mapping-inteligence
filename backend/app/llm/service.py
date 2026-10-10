"""
Migration LLM Service Adapter.
Follows Feeder Guide §4:
Single service boundary encapsulating:
- build_prompt()
- invoke()
- validate_output()
- fallback()

Guarantees:
- Zero secrets committed or exposed in logs
- Strict timeout handling
- Automatic deterministic fallback on any error, timeout, or schema failure
"""

import socket
import time
import httpx
from typing import Dict, Any, List, Set, Optional, Tuple

# Ensure IPv4 addresses are tried first to prevent dual-stack IPv6 timeout hangs on Windows
_orig_getaddrinfo = socket.getaddrinfo
def _prefer_ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig_getaddrinfo(host, port, family, type, proto, flags)
    return sorted(res, key=lambda x: 0 if x[0] == socket.AF_INET else 1)
socket.getaddrinfo = _prefer_ipv4_getaddrinfo

from app.models.schemas import LLMEnhancementOutput, LLMTelemetry
from app.llm.config import LLMConfig
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm.validator import LLMOutputValidator
from app.llm.fallback import DeterministicFallbackProvider



class MigrationLLMService:
    """Service adapter managing LLM prompt construction, invocation, validation, and fallback."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()
        self._active_key_index: int = 0

    def build_prompt(
        self,
        source_table: str,
        dest_table: str,
        overall_status: str,
        selected_route: str,
        routing_status: str,
        summary_counts: Dict[str, int],
        triggered_rules: List[str],
        transformations: List[Dict[str, Any]],
        review_items: List[str],
        blocking_issues: List[str],
        unmapped_fields: List[str],
    ) -> str:
        """Constructs prompt for the LLM."""
        return build_user_prompt(
            source_table=source_table,
            dest_table=dest_table,
            overall_status=overall_status,
            selected_route=selected_route,
            routing_status=routing_status,
            summary_counts=summary_counts,
            triggered_rules=triggered_rules,
            transformations=transformations,
            review_items=review_items,
            blocking_issues=blocking_issues,
            unmapped_fields=unmapped_fields,
        )

    @staticmethod
    def _sanitize_error_message(message: str) -> str:
        """Strip API keys, query params, and credentials from error strings."""
        if not message:
            return ""
        import re
        clean = re.sub(r"key=[a-zA-Z0-9_\-]+", "key=[REDACTED]", message)
        clean = re.sub(r"Bearer\s+[a-zA-Z0-9_\-]+", "Bearer [REDACTED]", clean)
        clean = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", clean)
        clean = re.sub(r"AQ\.[0-9A-Za-z-_]{30,}", "[REDACTED_API_KEY]", clean)
        clean = re.sub(r"sk-[a-zA-Z0-9-_]{20,}", "[REDACTED_API_KEY]", clean)
        return clean

    def _call_gemini(self, user_prompt: str) -> str:
        """Invokes Gemini REST API with automatic key switching / failover."""
        keys_pool = self.config.api_keys if self.config.api_keys else ([self.config.api_key] if self.config.api_key else [])
        if not keys_pool:
            raise ValueError("No Gemini API keys configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent"
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }

        last_error = None
        num_keys = len(keys_pool)
        start_index = self._active_key_index

        for attempt in range(num_keys):
            key_index = (start_index + attempt) % num_keys
            current_key = keys_pool[key_index]
            headers = {
                "x-goog-api-key": current_key,
                "Content-Type": "application/json",
            }

            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.post(url, headers=headers, json=payload)

                    # Auto-switch to next key on quota, rate limit, forbidden, or invalid key
                    if resp.status_code in (400, 401, 403, 429) and num_keys > 1:
                        last_error = ValueError(f"Gemini API returned {resp.status_code} on key #{key_index + 1}: {resp.text[:150]}")
                        self._active_key_index = (key_index + 1) % num_keys
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError("Gemini returned zero candidates.")
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise ValueError("Gemini returned empty parts.")

                # Retain this active key index for next requests
                self._active_key_index = key_index
                return parts[0].get("text", "")

            except (httpx.HTTPStatusError, httpx.RequestError) as http_err:
                last_error = http_err
                if num_keys > 1 and attempt < num_keys - 1:
                    self._active_key_index = (key_index + 1) % num_keys
                    continue
                raise

        if last_error:
            raise last_error
        raise ValueError("All configured Gemini API keys failed.")

    def _call_openai(self, user_prompt: str) -> str:
        """Invokes OpenAI REST API with automatic key switching / failover."""
        keys_pool = self.config.api_keys if self.config.api_keys else ([self.config.api_key] if self.config.api_key else [])
        if not keys_pool:
            raise ValueError("No OpenAI API keys configured.")

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        last_error = None
        num_keys = len(keys_pool)
        start_index = self._active_key_index

        for attempt in range(num_keys):
            key_index = (start_index + attempt) % num_keys
            current_key = keys_pool[key_index]
            headers = {
                "Authorization": f"Bearer {current_key}",
                "Content-Type": "application/json",
            }

            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code in (400, 401, 403, 429) and num_keys > 1:
                        last_error = ValueError(f"OpenAI API returned {resp.status_code} on key #{key_index + 1}")
                        self._active_key_index = (key_index + 1) % num_keys
                        continue

                    resp.raise_for_status()
                    data = resp.json()

                choices = data.get("choices", [])
                if not choices:
                    raise ValueError("OpenAI returned zero choices.")
                self._active_key_index = key_index
                return choices[0].get("message", {}).get("content", "")

            except (httpx.HTTPStatusError, httpx.RequestError) as http_err:
                last_error = http_err
                if num_keys > 1 and attempt < num_keys - 1:
                    self._active_key_index = (key_index + 1) % num_keys
                    continue
                raise

        if last_error:
            raise last_error
        raise ValueError("All configured OpenAI API keys failed.")

    def _call_mock(
        self,
        source_table: str,
        dest_table: str,
        overall_status: str,
        selected_route: str,
        routing_status: str,
        summary_counts: Dict[str, int],
        transformations: List[Dict[str, Any]],
        review_items: List[str],
        blocking_issues: List[str],
        unmapped_fields: List[str],
    ) -> str:
        """Simulates LLM response for test environments."""
        fb = DeterministicFallbackProvider.generate(
            source_table=source_table,
            dest_table=dest_table,
            overall_status=overall_status,
            selected_route=selected_route,
            routing_status=routing_status,
            summary_counts=summary_counts,
            transformations=transformations,
            review_items=review_items,
            blocking_issues=blocking_issues,
            unmapped_fields=unmapped_fields,
        )
        return fb.model_dump_json()

    def enhance(
        self,
        source_table: str,
        dest_table: str,
        overall_status: str,
        selected_route: str,
        routing_status: str,
        summary_counts: Dict[str, int],
        triggered_rules: List[str],
        transformations: List[Dict[str, Any]],
        review_items: List[str],
        blocking_issues: List[str],
        unmapped_fields: List[str],
        valid_dest_fields: Set[str],
    ) -> Tuple[LLMEnhancementOutput, LLMTelemetry]:
        """
        Executes controlled LLM enhancement with bounded validation and deterministic fallback.
        Returns: (output, telemetry)
        """
        # Check if disabled
        if not self.config.enabled:
            fallback_res = DeterministicFallbackProvider.generate(
                source_table, dest_table, overall_status, selected_route,
                routing_status, summary_counts, transformations,
                review_items, blocking_issues, unmapped_fields
            )
            telemetry = LLMTelemetry(
                llm_used=False,
                provider=self.config.provider,
                model=self.config.model,
                status="SKIPPED",
                fallback_used=True,
                validation_passed=True,
                latency_ms=0.0,
                error_message="LLM enhancement disabled by configuration.",
            )
            return fallback_res, telemetry

        # Check if API key is missing for live providers
        if self.config.provider in ("gemini", "openai") and not (self.config.api_key or self.config.api_keys):
            fallback_res = DeterministicFallbackProvider.generate(
                source_table, dest_table, overall_status, selected_route,
                routing_status, summary_counts, transformations,
                review_items, blocking_issues, unmapped_fields
            )
            telemetry = LLMTelemetry(
                llm_used=False,
                provider=self.config.provider,
                model=self.config.model,
                status="FALLBACK",
                fallback_used=True,
                validation_passed=False,
                latency_ms=0.0,
                error_message=f"Missing API key for provider '{self.config.provider}'. Deterministic fallback triggered.",

            )
            return fallback_res, telemetry

        start_time = time.perf_counter()
        raw_text = ""
        user_prompt = self.build_prompt(
            source_table=source_table,
            dest_table=dest_table,
            overall_status=overall_status,
            selected_route=selected_route,
            routing_status=routing_status,
            summary_counts=summary_counts,
            triggered_rules=triggered_rules,
            transformations=transformations,
            review_items=review_items,
            blocking_issues=blocking_issues,
            unmapped_fields=unmapped_fields,
        )

        try:
            if self.config.provider == "gemini":
                raw_text = self._call_gemini(user_prompt)
            elif self.config.provider == "openai":
                raw_text = self._call_openai(user_prompt)
            else:
                raw_text = self._call_mock(
                    source_table, dest_table, overall_status, selected_route,
                    routing_status, summary_counts, transformations,
                    review_items, blocking_issues, unmapped_fields
                )

            latency_ms = (time.perf_counter() - start_time) * 1000.0

            # Validate LLM output
            is_valid, validated_output, val_err = LLMOutputValidator.validate_and_bound(
                raw_text, valid_dest_fields
            )

            if is_valid and validated_output:
                telemetry = LLMTelemetry(
                    llm_used=True,
                    provider=self.config.provider,
                    model=self.config.model,
                    status="SUCCESS",
                    fallback_used=False,
                    validation_passed=True,
                    latency_ms=round(latency_ms, 2),
                    error_message=None,
                )
                return validated_output, telemetry
            else:
                # Validation failed -> deterministic fallback
                fallback_res = DeterministicFallbackProvider.generate(
                    source_table, dest_table, overall_status, selected_route,
                    routing_status, summary_counts, transformations,
                    review_items, blocking_issues, unmapped_fields
                )
                telemetry = LLMTelemetry(
                    llm_used=True,
                    provider=self.config.provider,
                    model=self.config.model,
                    status="FALLBACK",
                    fallback_used=True,
                    validation_passed=False,
                    latency_ms=round(latency_ms, 2),
                    error_message=f"Output validation failed: {val_err}",
                )
                return fallback_res, telemetry

        except httpx.TimeoutException:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            fallback_res = DeterministicFallbackProvider.generate(
                source_table, dest_table, overall_status, selected_route,
                routing_status, summary_counts, transformations,
                review_items, blocking_issues, unmapped_fields
            )
            telemetry = LLMTelemetry(
                llm_used=False,
                provider=self.config.provider,
                model=self.config.model,
                status="FALLBACK",
                fallback_used=True,
                validation_passed=False,
                latency_ms=round(latency_ms, 2),
                error_message=f"LLM request timed out after {self.config.timeout}s.",
            )
            return fallback_res, telemetry

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            fallback_res = DeterministicFallbackProvider.generate(
                source_table, dest_table, overall_status, selected_route,
                routing_status, summary_counts, transformations,
                review_items, blocking_issues, unmapped_fields
            )
            telemetry = LLMTelemetry(
                llm_used=False,
                provider=self.config.provider,
                model=self.config.model,
                status="FALLBACK",
                fallback_used=True,
                validation_passed=False,
                latency_ms=round(latency_ms, 2),
                error_message=f"LLM invocation error: {self._sanitize_error_message(str(exc))}",
            )

            return fallback_res, telemetry
