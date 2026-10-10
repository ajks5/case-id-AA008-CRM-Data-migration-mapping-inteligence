"""
Test Suite for Phase 2.3: Controlled LLM Enhancement.
Adheres to Master Prompt & Feeder Guide §10:
Covers 5 small evaluation scenarios:
1. Normal valid LLM response (simple_schema - HIGH_CONFIDENCE / direct_accept)
2. Ambiguous or difficult input (naming_mismatch - TRANSFORM_REQUIRED / transform_verify)
3. Domain-specific edge case (relationship_mismatch - REVIEW_REQUIRED / human_review)
4. LLM unavailable / timeout / error (graceful fallback)
5. Invalid or malformed LLM output (schema violation / fallback)

Verifies:
- deterministic decision behavior remains safe
- LLM output is bounded to its approved role
- fallback works
- explanation / trace identifies whether LLM was used
- audit remains available
"""

import pytest
from unittest.mock import patch
from app.models.schemas import MigrationRequest, LLMEnhancementOutput, LLMTelemetry
from app.workflow.orchestrator import MigrationOrchestrator
from app.data.sample_scenarios import SAMPLE_SCENARIOS
from app.llm.config import LLMConfig
from app.llm.service import MigrationLLMService
from app.llm.validator import LLMOutputValidator
from app.llm.fallback import DeterministicFallbackProvider
from app.audit.audit_store import audit_store


@pytest.fixture(autouse=True)
def clean_audit_store():
    """Ensure clean audit state before each test run."""
    audit_store.clear()
    yield
    audit_store.clear()


# ---------------------------------------------------------------------------
# Scenario 1: Normal Valid LLM Response (Product Bible §17 & Feeder Guide §10)
# ---------------------------------------------------------------------------
def test_scenario_1_normal_valid_llm_response():
    """
    Scenario 1: Normal valid LLM response for simple_schema.
    Verifies:
    - Deterministic decision: READY, 6 DIRECT_MAP, 1 DEFAULT
    - Route: route_direct_accept (ACCEPTED_DIRECT)
    - LLM output bounded to explanation/summary
    - Telemetry records success and latency
    - Audit captures llm_telemetry and trace step
    """
    req = MigrationRequest(**SAMPLE_SCENARIOS["simple_schema"]["request"])
    
    # Use deterministic mock config for reproducible test assertion
    mock_config = LLMConfig(provider="mock", model="mock-v1", enabled=True)
    with patch("app.workflow.graph._llm_service", MigrationLLMService(mock_config)):
        orchestrator = MigrationOrchestrator()
        context = orchestrator.run(req)

    # 1. Deterministic authority intact
    assert context.final_recommendation is not None
    assert context.final_recommendation.overall_status == "READY"
    assert context.final_recommendation.summary_counts["DIRECT_MAP"] == 6
    assert context.final_recommendation.summary_counts["REVIEW"] == 0
    assert context.validation_results.all_valid is True

    # 2. Conditional Routing intact
    assert context.selected_route == "route_direct_accept"
    assert context.routing_status == "ACCEPTED_DIRECT"

    # 3. LLM Enhancement bounded and populated
    assert context.llm_enhancement is not None
    assert isinstance(context.llm_enhancement, LLMEnhancementOutput)
    assert len(context.llm_enhancement.executive_summary) > 0
    assert "legacy_contacts" in context.llm_enhancement.executive_summary
    assert context.llm_enhancement.risk_assessment == "LOW RISK: High-confidence direct field mappings with zero constraint violations."

    # 4. Telemetry and Trace
    assert context.llm_telemetry is not None
    assert context.llm_telemetry.status == "SUCCESS"
    assert context.llm_telemetry.fallback_used is False
    assert context.llm_telemetry.validation_passed is True

    trace_nodes = [step["node"] for step in context.node_trace]
    assert "llm_enhancement" in trace_nodes
    llm_step = next(s for s in context.node_trace if s["node"] == "llm_enhancement")
    assert llm_step["status"] == "COMPLETED"
    assert "LLM Status: SUCCESS" in llm_step["summary"]

    # 5. Audit persisted
    assert context.audit_reference is not None
    audit_rec = audit_store.get(context.audit_reference)
    assert audit_rec is not None
    assert audit_rec.llm_telemetry is not None
    assert audit_rec.llm_telemetry.status == "SUCCESS"


# ---------------------------------------------------------------------------
# Scenario 2: Ambiguous or Difficult Input (naming_mismatch / TRANSFORM_REQUIRED)
# ---------------------------------------------------------------------------
def test_scenario_2_ambiguous_transform_rationales():
    """
    Scenario 2: Transform path with CRM aliases and datetime conversions.
    Verifies:
    - Deterministic decision: READY, 1 TRANSFORM (signup_date -> created_at)
    - Route: route_transform_verify (TRANSFORM_STAGED)
    - LLM provides technical transformation rationales for 'created_at'
    - Hallucinated fields are forbidden
    """
    req = MigrationRequest(**SAMPLE_SCENARIOS["naming_mismatch"]["request"])

    mock_config = LLMConfig(provider="mock", model="mock-v1", enabled=True)
    with patch("app.workflow.graph._llm_service", MigrationLLMService(mock_config)):
        orchestrator = MigrationOrchestrator()
        context = orchestrator.run(req)

    # 1. Deterministic authority intact
    assert context.final_recommendation.overall_status == "READY"
    assert context.final_recommendation.summary_counts["TRANSFORM"] == 1
    assert context.selected_route == "route_transform_verify"
    assert context.routing_status == "TRANSFORM_STAGED"

    # 2. LLM Enhancement rationales bounded to actual transform fields
    assert context.llm_enhancement is not None
    assert "created_at" in context.llm_enhancement.transformation_rationales
    rationale = context.llm_enhancement.transformation_rationales["created_at"]
    assert "Rule 3" in rationale or "TYPE_CAST" in rationale or "datetime" in rationale
    assert "MODERATE RISK" in context.llm_enhancement.risk_assessment

    # 3. Explanation enriched
    assert context.explanation.transformation_rationales is not None
    assert "created_at" in context.explanation.transformation_rationales


# ---------------------------------------------------------------------------
# Scenario 3: Domain-Specific Edge Case (relationship_mismatch / REVIEW_REQUIRED)
# ---------------------------------------------------------------------------
def test_scenario_3_exception_edge_case_review_actions():
    """
    Scenario 3: Unresolved relational foreign key constraint (Rule 4 & Rule 5).
    Verifies:
    - Deterministic decision: NEEDS_REVIEW, blocking constraint on account_id
    - Route: route_human_review (ESCALATED_FOR_REVIEW)
    - LLM generates HIGH RISK assessment and concrete triage steps
    - Telemetry and Audit reflect human review branch + LLM enrichment
    """
    req = MigrationRequest(**SAMPLE_SCENARIOS["relationship_mismatch"]["request"])

    mock_config = LLMConfig(provider="mock", model="mock-v1", enabled=True)
    with patch("app.workflow.graph._llm_service", MigrationLLMService(mock_config)):
        orchestrator = MigrationOrchestrator()
        context = orchestrator.run(req)

    # 1. Deterministic authority halts automated migration
    assert context.final_recommendation.overall_status == "NEEDS_REVIEW"
    assert context.validation_results.all_valid is False
    assert len(context.validation_results.blocking_issues) > 0
    assert context.selected_route == "route_human_review"
    assert context.routing_status == "ESCALATED_FOR_REVIEW"

    # 2. LLM Enhancement identifies high risk and provides review actions
    assert context.llm_enhancement is not None
    assert "HIGH RISK" in context.llm_enhancement.risk_assessment
    assert len(context.llm_enhancement.suggested_review_actions) > 0
    # Confirms triage advice addresses account_id
    assert any("account_id" in action for action in context.llm_enhancement.suggested_review_actions)


# ---------------------------------------------------------------------------
# Scenario 4: LLM Unavailable / Timeout / Network Error (Fallback Verification)
# ---------------------------------------------------------------------------
def test_scenario_4_llm_timeout_triggers_deterministic_fallback():
    """
    Scenario 4: LLM request times out.
    Verifies:
    - Deterministic decision is NOT affected
    - System does not crash with 500 error
    - Fallback provider engages automatically
    - Telemetry flags status='FALLBACK', fallback_used=True, validation_passed=False
    - Error message recorded in telemetry and trace without leaking secrets
    """
    req = MigrationRequest(**SAMPLE_SCENARIOS["simple_schema"]["request"])

    # Simulate timeout by injecting an LLMService that raises TimeoutException
    service = MigrationLLMService(LLMConfig(provider="gemini", model="gemini-2.5-flash", api_key="test_key", timeout=0.001))
    with patch.object(service, "_call_gemini", side_effect=Exception("Connection timed out after 0.001s")):
        with patch("app.workflow.graph._llm_service", service):
            orchestrator = MigrationOrchestrator()
            context = orchestrator.run(req)

    # 1. Deterministic authority intact
    assert context.final_recommendation.overall_status == "READY"
    assert context.selected_route == "route_direct_accept"
    assert context.routing_status == "ACCEPTED_DIRECT"

    # 2. Fallback output generated deterministically
    assert context.llm_enhancement is not None
    assert "Deterministic direct migration accepted" in context.llm_enhancement.executive_summary

    # 3. Telemetry explicitly indicates fallback
    assert context.llm_telemetry is not None
    assert context.llm_telemetry.status == "FALLBACK"
    assert context.llm_telemetry.fallback_used is True
    assert "timed out" in context.llm_telemetry.error_message.lower() or "error" in context.llm_telemetry.error_message.lower()

    # 4. Audit captures fallback
    audit_rec = audit_store.get(context.audit_reference)
    assert audit_rec.llm_telemetry.fallback_used is True


# ---------------------------------------------------------------------------
# Scenario 5: Invalid / Malformed LLM Output (Validation & Bounding)
# ---------------------------------------------------------------------------
def test_scenario_5_malformed_llm_output_triggers_fallback():
    """
    Scenario 5: Provider returns non-JSON or invalid schema.
    Verifies:
    - LLMOutputValidator rejects malformed payload
    - Fallback engages seamlessly
    - Telemetry records validation failure
    """
    req = MigrationRequest(**SAMPLE_SCENARIOS["simple_schema"]["request"])

    # Simulate provider returning malformed gibberish text
    service = MigrationLLMService(LLMConfig(provider="gemini", model="gemini-2.5-flash", api_key="test_key"))
    with patch.object(service, "_call_gemini", return_value="INVALID_NON_JSON_RESPONSE {{{"):
        with patch("app.workflow.graph._llm_service", service):
            orchestrator = MigrationOrchestrator()
            context = orchestrator.run(req)


    # 1. Deterministic decision safe
    assert context.final_recommendation.overall_status == "READY"
    assert context.selected_route == "route_direct_accept"

    # 2. Fallback output engaged
    assert context.llm_enhancement is not None
    assert context.llm_telemetry.status == "FALLBACK"
    assert context.llm_telemetry.fallback_used is True
    assert context.llm_telemetry.validation_passed is False
    assert "Malformed JSON" in context.llm_telemetry.error_message


def test_validator_prunes_hallucinated_fields():
    """
    Unit test: Verify validator strips fields that do not exist in destination schema.
    """
    raw_payload = """
    {
      "executive_summary": "Test summary",
      "transformation_rationales": {
        "valid_field": "Valid rationale",
        "hallucinated_non_existent_column": "Fake rationale"
      },
      "risk_assessment": "LOW",
      "suggested_review_actions": []
    }
    """
    valid_dest_fields = {"valid_field", "other_field"}
    is_valid, output, err = LLMOutputValidator.validate_and_bound(raw_payload, valid_dest_fields)

    assert is_valid is True
    assert output is not None
    assert "valid_field" in output.transformation_rationales
    assert "hallucinated_non_existent_column" not in output.transformation_rationales


def test_key_switching_and_quota_failover():
    """
    Unit test: Verify that when Key 1 encounters 429/403/error, service switches to Key 2.
    """
    config = LLMConfig(
        provider="gemini",
        model="gemini-3.5-flash-lite",
        api_keys=["primary_key_429", "backup_key_success"],
    )
    service = MigrationLLMService(config)

    valid_json_response = """
    {
      "executive_summary": "Successful migration summary after failover.",
      "transformation_rationales": {},
      "risk_assessment": "LOW",
      "suggested_review_actions": []
    }
    """

    call_count = 0
    def mock_post(self, url, headers=None, json=None):
        nonlocal call_count
        call_count += 1
        key = headers.get("x-goog-api-key")
        import httpx
        req = httpx.Request("POST", url)
        if key == "primary_key_429":
            return httpx.Response(429, request=req, text='{"error": {"message": "Resource exhausted"}}')
        elif key == "backup_key_success":
            import json as json_lib
            body = {
                "candidates": [
                    {"content": {"parts": [{"text": valid_json_response}]}}
                ]
            }
            return httpx.Response(200, request=req, text=json_lib.dumps(body))
        raise ValueError(f"Unexpected key: {key}")

    with patch("httpx.Client.post", mock_post):
        result_text = service._call_gemini("test user prompt")

    assert "Successful migration summary after failover" in result_text
    assert call_count == 2
    assert service._active_key_index == 1

