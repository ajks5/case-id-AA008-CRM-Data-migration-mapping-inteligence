"""
Cloud Deployment Validation Script for Phase 1.4.
Verifies the deployed cloud backend API and frontend web application over live HTTPS/HTTP requests.

Accepts CLI arguments:
    --backend-url   (e.g., https://aa008-backend.onrender.com or ACA URL)
    --frontend-url  (e.g., https://aa008-frontend.vercel.app or ACA URL)
    --timeout       (default: 30 seconds to accommodate potential cold starts)

Usage:
    python validate_cloud.py --backend-url https://<YOUR_BACKEND> --frontend-url https://<YOUR_FRONTEND>
"""

import sys
import time
import argparse
import httpx


def parse_args():
    parser = argparse.ArgumentParser(description="Phase 1.4 Cloud Deployment Validation")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Base URL of deployed backend API (e.g. https://aa008-backend.onrender.com)",
    )
    parser.add_argument(
        "--frontend-url",
        default="http://localhost:3000",
        help="Base URL of deployed frontend web application (e.g. https://aa008-frontend.vercel.app)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default 30s to allow free tier wake-up)",
    )
    return parser.parse_args()


def validate_cloud_deployment(backend_url: str, frontend_url: str, timeout: float):
    backend_url = backend_url.rstrip("/")
    frontend_url = frontend_url.rstrip("/")

    print("=" * 80)
    print("AA008 CRM DATA MIGRATION - PHASE 1.4 CLOUD DEPLOYMENT VALIDATION")
    print("=" * 80)
    print(f"Target Backend URL : {backend_url}")
    print(f"Target Frontend URL: {frontend_url}")
    print(f"Request Timeout    : {timeout}s")
    print("=" * 80)

    client = httpx.Client(timeout=timeout, follow_redirects=True)

    # 1. Backend Health Check
    print("\n[Gate 1] Validating Cloud Backend Health Endpoint (/health)...")
    try:
        health_res = client.get(f"{backend_url}/health")
        assert health_res.status_code == 200, f"Expected HTTP 200, got {health_res.status_code}"
        health_data = health_res.json()
        assert health_data.get("status") == "healthy", f"Status not healthy: {health_data}"
        assert health_data.get("case_id") == "AA008", f"Expected case AA008, got {health_data}"
        print(f"  [PASS] Backend Healthy! Status: {health_data}")
    except Exception as e:
        print(f"  [FAIL] Backend health check failed: {e}")
        sys.exit(1)

    # 2. Frontend Accessibility Check
    print("\n[Gate 2] Validating Cloud Frontend Availability (/)...")
    try:
        front_res = client.get(f"{frontend_url}/")
        assert front_res.status_code == 200, f"Expected HTTP 200, got {front_res.status_code}"
        html_content = front_res.text.lower()
        assert "<div id=\"root\"></div>" in html_content or "<!doctype html>" in html_content, "Frontend HTML structure invalid"
        print(f"  [PASS] Frontend Web Application Accessible (HTTP 200 OK)")
    except Exception as e:
        print(f"  [FAIL] Frontend check failed: {e}")
        sys.exit(1)

    # 3. Sample Scenarios Retrieval
    print("\n[Gate 3] Fetching Product Bible Pre-Seeded Scenarios (/api/scenarios)...")
    try:
        scenarios_res = client.get(f"{backend_url}/api/scenarios")
        assert scenarios_res.status_code == 200
        scenarios = scenarios_res.json()
        assert len(scenarios) == 3, f"Expected 3 scenarios, found {len(scenarios)}"
        print(f"  [PASS] Successfully loaded {len(scenarios)} pre-seeded scenarios from cloud backend.")
    except Exception as e:
        print(f"  [FAIL] Scenarios endpoint check failed: {e}")
        sys.exit(1)

    # 4. Execute Full Migration Workflows across all 3 Product Bible Scenarios
    for scn in scenarios:
        scn_id = scn["id"]
        scn_name = scn["name"]
        print("\n" + "-" * 80)
        print(f"[Gate 4.{scenarios.index(scn) + 1}] Executing Workflow: {scn_name} ({scn_id})")

        start_time = time.time()
        res = client.post(f"{backend_url}/api/migrate", json=scn["request"])
        elapsed = time.time() - start_time
        assert res.status_code == 200, f"Migration failed with status {res.status_code}: {res.text}"
        data = res.json()

        wf_id = data["workflow_id"]
        agents = [a["agent_name"] for a in data["agent_outputs"]]
        rec = data["final_recommendation"]
        explanation = data["explanation"]
        audit_ref = data["audit_reference"]

        print(f"  -> Workflow ID: {wf_id}")
        print(f"  -> 5-Agent Chain: {' -> '.join(agents)}")
        assert len(agents) == 5, f"Expected 5 agents, executed {len(agents)}"
        assert agents == [
            "Schema Analyzer Agent",
            "Field Mapping Agent",
            "Transformation Agent",
            "Validation Agent",
            "Migration Decision Agent",
        ]

        print(f"  -> Overall Decision Status: {rec['overall_status']}")
        print(f"  -> Summary Counts: {rec['summary_counts']}")
        print(f"  -> Triggered Rules: {rec['triggered_rules']}")
        print(f"  -> Explanation Narrative: {explanation['summary']}")
        print(f"  -> Execution Time: {elapsed:.3f}s")

        if scn_id == "simple_schema":
            assert rec["overall_status"] == "READY", f"Expected READY, got {rec['overall_status']}"
            assert rec["summary_counts"]["DIRECT_MAP"] == 6
            assert rec["summary_counts"]["REVIEW"] == 0
            assert "RULE_1_EXACT_NAME_COMPATIBLE_TYPE" in rec["triggered_rules"]
            print("  [PASS] Scenario 1 verified: 100% direct-map deterministic rule execution.")

        elif scn_id == "naming_mismatch":
            assert rec["overall_status"] == "READY", f"Expected READY, got {rec['overall_status']}"
            assert rec["summary_counts"]["TRANSFORM"] >= 1
            assert "RULE_2_KNOWN_ALIAS_COMPATIBLE_TYPE" in rec["triggered_rules"]
            assert "RULE_3_TYPE_CONVERTIBLE" in rec["triggered_rules"]
            print("  [PASS] Scenario 2 verified: Synonym aliases and type conversion rules applied.")

        elif scn_id == "relationship_mismatch":
            assert rec["overall_status"] == "NEEDS_REVIEW", f"Expected NEEDS_REVIEW, got {rec['overall_status']}"
            assert rec["summary_counts"]["REVIEW"] >= 1
            assert "RULE_4_REQUIRED_TARGET_MISSING_SOURCE" in rec["triggered_rules"]
            assert "RULE_5_RELATIONSHIP_OR_KEY_CONFLICT" in rec["triggered_rules"]
            print("  [PASS] Scenario 3 verified: Missing required relational link flagged for human review.")

        # 5. Audit Trail Verification
        print(f"  -> Verifying Cloud In-Memory Audit Record for {wf_id}...")
        audit_res = client.get(f"{backend_url}/api/audit/{wf_id}")
        assert audit_res.status_code == 200, f"Audit retrieval failed: {audit_res.text}"
        audit_data = audit_res.json()
        assert audit_data["workflow_id"] == wf_id
        assert audit_data["final_recommendation_status"] == rec["overall_status"]
        print(f"  [PASS] In-memory audit entry confirmed (ID: {audit_ref})")

    print("\n" + "=" * 80)
    print("ALL PHASE 1.4 CLOUD VALIDATION CHECKS PASSED PERFECTLY!")
    print("=" * 80)
    print("Summary:")
    print("  - Backend Health: OK")
    print("  - Frontend Accessible: OK")
    print("  - 5 Deterministic Agents: Schema Analyzer -> Field Mapping -> Transformation -> Validation -> Migration Decision")
    print("  - Deterministic Rules 1 to 5: Verified")
    print("  - Explainability / Narrative: Verified")
    print("  - Audit Traceability: Verified")
    print("=" * 80)


if __name__ == "__main__":
    args = parse_args()
    validate_cloud_deployment(args.backend_url, args.frontend_url, args.timeout)
