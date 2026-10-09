"""
End-to-End Tests for the 3 Product Bible Scenarios & FastAPI Endpoints.
Implements Product Bible §17 & Acceptance Criteria §22:
- Scenario 1: Simple schema -> High direct-map coverage
- Scenario 2: Naming mismatch -> Alias-based DIRECT_MAP + transform
- Scenario 3: Relationship mismatch -> REVIEW
"""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.data.sample_scenarios import SAMPLE_SCENARIOS
from app.rules.mapping_rules import RULE_1_ID, RULE_2_ID, RULE_3_ID, RULE_4_ID, RULE_5_ID

client = TestClient(app)


def test_health_endpoint():
    """Verify /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["case_id"] == "AA008"


def test_get_scenarios_endpoint():
    """Verify /api/scenarios lists all 3 Product Bible scenarios."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) == 3
    ids = [s["id"] for s in scenarios]
    assert "simple_schema" in ids
    assert "naming_mismatch" in ids
    assert "relationship_mismatch" in ids


def test_scenario_1_simple_schema():
    """
    Scenario 1: Simple schema
    Mostly matching names/types -> High direct-map coverage.
    """
    req_data = SAMPLE_SCENARIOS["simple_schema"]["request"]
    response = client.post("/api/migrate", json=req_data)
    assert response.status_code == 200
    res = response.json()

    assert res["workflow_id"].startswith("wf_")
    assert res["final_recommendation"]["overall_status"] == "READY"
    assert res["final_recommendation"]["summary_counts"]["DIRECT_MAP"] >= 5
    assert res["final_recommendation"]["summary_counts"]["REVIEW"] == 0
    assert RULE_1_ID in res["final_recommendation"]["triggered_rules"]

    # Verify agent timeline
    agent_names = [a["agent_name"] for a in res["agent_outputs"]]
    assert agent_names == [
        "Schema Analyzer Agent",
        "Field Mapping Agent",
        "Transformation Agent",
        "Validation Agent",
        "Migration Decision Agent"
    ]

    # Phase 2.2: Verify LangGraph conditional routing
    assert res["selected_route"] == "route_direct_accept"
    assert res["routing_status"] == "ACCEPTED_DIRECT"

    # Verify audit record created
    audit_res = client.get(f"/api/audit/{res['workflow_id']}")
    assert audit_res.status_code == 200
    assert audit_res.json()["final_recommendation_status"] == "READY"
    assert audit_res.json()["selected_route"] == "route_direct_accept"


def test_scenario_2_naming_mismatch():
    """
    Scenario 2: Naming mismatch
    Alias-based mappings required -> DIRECT_MAP + evidence + TRANSFORM.
    """
    req_data = SAMPLE_SCENARIOS["naming_mismatch"]["request"]
    response = client.post("/api/migrate", json=req_data)
    assert response.status_code == 200
    res = response.json()

    assert res["final_recommendation"]["overall_status"] == "READY"
    assert res["final_recommendation"]["summary_counts"]["DIRECT_MAP"] == 6
    assert res["final_recommendation"]["summary_counts"]["TRANSFORM"] == 1
    assert res["final_recommendation"]["summary_counts"]["REVIEW"] == 0
    assert RULE_2_ID in res["final_recommendation"]["triggered_rules"]
    assert RULE_3_ID in res["final_recommendation"]["triggered_rules"]

    # Phase 2.2: Verify LangGraph conditional routing
    assert res["selected_route"] == "route_transform_verify"
    assert res["routing_status"] == "TRANSFORM_STAGED"

    # Verify signup_date was transformed to created_at
    created_rec = next(
        r for r in res["final_recommendation"]["field_recommendations"]
        if r["destination_field"] == "created_at"
    )
    assert created_rec["decision"] == "TRANSFORM"
    assert created_rec["source_field"] == "signup_date"
    assert created_rec["transformation"] == "PARSE_STRING_TO_DATETIME"


def test_scenario_3_relationship_mismatch():
    """
    Scenario 3: Relationship mismatch
    Target relationship cannot be safely derived -> REVIEW.
    """
    req_data = SAMPLE_SCENARIOS["relationship_mismatch"]["request"]
    response = client.post("/api/migrate", json=req_data)
    assert response.status_code == 200
    res = response.json()

    assert res["final_recommendation"]["overall_status"] == "NEEDS_REVIEW"
    assert res["final_recommendation"]["summary_counts"]["REVIEW"] >= 1
    assert RULE_4_ID in res["final_recommendation"]["triggered_rules"]
    assert RULE_5_ID in res["final_recommendation"]["triggered_rules"]

    # Phase 2.2: Verify LangGraph conditional routing
    assert res["selected_route"] == "route_human_review"
    assert res["routing_status"] == "ESCALATED_FOR_REVIEW"

    # Verify account_id flagged for review with relationship conflict explanation
    acc_rec = next(
        r for r in res["final_recommendation"]["field_recommendations"]
        if r["destination_field"] == "account_id"
    )
    assert acc_rec["decision"] == "REVIEW"
    assert acc_rec["requires_human_review"] is True
    assert "crm_accounts" in acc_rec["evidence"]
