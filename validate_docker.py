"""
Containerized Validation Script for Phase 1.3.
Verifies the running Docker containers over live HTTP requests.
Tests:
1. Backend Health Check (GET http://localhost:8000/health)
2. Frontend HTTP Root (GET http://localhost:3000/)
3. Product Bible Scenarios Endpoint (GET http://localhost:8000/api/scenarios)
4. Full Execution of Scenarios 1, 2, and 3 (POST http://localhost:8000/api/migrate)
5. Deterministic Rules Verification (Rules 1-5)
6. Shared Workflow Context & 5-Agent Execution Chain
7. Audit Log Retrieval (GET http://localhost:8000/api/audit/{workflow_id})
"""

import time
import sys
import httpx

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def test_containerized_workflow():
    print("=" * 75)
    print("AA008 CRM DATA MIGRATION — PHASE 1.3 DOCKER CONTAINER VALIDATION")
    print("=" * 75)

    client = httpx.Client(timeout=10.0)

    # 1. Backend Health Check
    print("\n[Step 1] Checking Backend Health Endpoint...")
    try:
        res = client.get(f"{BACKEND_URL}/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        health_data = res.json()
        assert health_data["status"] == "healthy"
        assert health_data["case_id"] == "AA008"
        print(f" -> Backend Healthy: {health_data}")
    except Exception as e:
        print(f" [FAIL] Backend health check failed: {e}")
        sys.exit(1)

    # 2. Frontend Accessibility Check
    print("\n[Step 2] Checking Frontend Nginx Web Server...")
    try:
        res = client.get(f"{FRONTEND_URL}/")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert "<div id=\"root\"></div>" in res.text or "<!DOCTYPE html>" in res.text or "<!doctype html>" in res.text
        print(f" -> Frontend Accessible at {FRONTEND_URL} (HTTP 200 OK)")
    except Exception as e:
        print(f" [FAIL] Frontend check failed: {e}")
        sys.exit(1)

    # 3. Sample Scenarios Retrieval
    print("\n[Step 3] Fetching Pre-seeded Product Bible Scenarios...")
    try:
        res = client.get(f"{BACKEND_URL}/api/scenarios")
        assert res.status_code == 200
        scenarios = res.json()
        assert len(scenarios) == 3, f"Expected 3 scenarios, found {len(scenarios)}"
        print(f" -> Successfully loaded {len(scenarios)} seeded scenarios from containerized backend.")
    except Exception as e:
        print(f" [FAIL] Scenarios endpoint check failed: {e}")
        sys.exit(1)

    # 4. Run End-to-End Migration Workflows
    for scn in scenarios:
        scn_id = scn["id"]
        scn_name = scn["name"]
        print("-" * 75)
        print(f"Executing Workflow: {scn_name} ({scn_id})")

        start_time = time.time()
        res = client.post(f"{BACKEND_URL}/api/migrate", json=scn["request"])
        elapsed = time.time() - start_time
        assert res.status_code == 200, f"Migration failed: {res.text}"
        data = res.json()

        wf_id = data["workflow_id"]
        agents = [a["agent_name"] for a in data["agent_outputs"]]
        rec = data["final_recommendation"]
        explanation = data["explanation"]

        print(f" -> Workflow ID: {wf_id}")
        print(f" -> 5-Agent Chain: {' -> '.join(agents)}")
        assert len(agents) == 5, f"Expected 5 agents, executed {len(agents)}"
        assert agents == [
            "Schema Analyzer Agent",
            "Field Mapping Agent",
            "Transformation Agent",
            "Validation Agent",
            "Migration Decision Agent"
        ]

        print(f" -> Overall Status: {rec['overall_status']}")
        print(f" -> Summary Counts: {rec['summary_counts']}")
        print(f" -> Triggered Rules: {rec['triggered_rules']}")
        print(f" -> Explanation: {explanation['summary']}")
        print(f" -> Response Time: {elapsed:.3f}s")

        if scn_id == "simple_schema":
            assert rec["overall_status"] == "READY"
            assert rec["summary_counts"]["DIRECT_MAP"] == 6
            assert rec["summary_counts"]["DEFAULT"] == 1
            assert rec["summary_counts"]["REVIEW"] == 0
            assert "RULE_1_EXACT_NAME_COMPATIBLE_TYPE" in rec["triggered_rules"]
            print(" [PASS] Scenario 1 (Simple Schema): 100% direct mapping verified!")

        elif scn_id == "naming_mismatch":
            assert rec["overall_status"] == "READY"
            assert rec["summary_counts"]["DIRECT_MAP"] == 6
            assert rec["summary_counts"]["TRANSFORM"] == 1
            assert rec["summary_counts"]["REVIEW"] == 0
            assert "RULE_2_KNOWN_ALIAS_COMPATIBLE_TYPE" in rec["triggered_rules"]
            assert "RULE_3_TYPE_CONVERTIBLE" in rec["triggered_rules"]
            print(" [PASS] Scenario 2 (Naming Mismatch): Alias resolution & type transform verified!")

        elif scn_id == "relationship_mismatch":
            assert rec["overall_status"] == "NEEDS_REVIEW"
            assert rec["summary_counts"]["REVIEW"] >= 1
            assert "RULE_4_REQUIRED_TARGET_MISSING_SOURCE" in rec["triggered_rules"]
            assert "RULE_5_RELATIONSHIP_OR_KEY_CONFLICT" in rec["triggered_rules"]
            print(" [PASS] Scenario 3 (Relationship Mismatch): Missing relational link flagged for REVIEW!")

        # 5. Verify In-Memory Audit Trail
        audit_res = client.get(f"{BACKEND_URL}/api/audit/{wf_id}")
        assert audit_res.status_code == 200, f"Failed to retrieve audit: {audit_res.text}"
        audit_data = audit_res.json()
        assert audit_data["workflow_id"] == wf_id
        assert audit_data["final_recommendation_status"] == rec["overall_status"]
        print(f" [PASS] In-memory audit entry confirmed (ID: {wf_id})")

    print("\n" + "=" * 75)
    print("ALL DOCKER CONTAINER VALIDATION CHECKS PASSED PERFECTLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_containerized_workflow()
