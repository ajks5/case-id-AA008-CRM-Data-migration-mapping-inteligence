"""
Pytest configuration for AA008 CRM Data Migration Intelligence.
Defaults LLM_PROVIDER to 'mock' for hermetic, fast, and offline test execution
unless a live integration test explicitly configures otherwise.
"""

import os
import pytest
from app.audit.audit_store import audit_store


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set default test environment variables."""
    # Ensure hermetic testing by default
    if "LLM_PROVIDER" not in os.environ:
        monkeypatch.setenv("LLM_PROVIDER", "mock")
    audit_store.clear()
    yield
    audit_store.clear()
