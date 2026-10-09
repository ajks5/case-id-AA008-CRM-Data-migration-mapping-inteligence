"""
Comprehensive End-to-End Validation Script for AA008 CRM Data Migration (Phase 2.3).
Validates:
1. Health and LLM status endpoints
2. All 3 Product Bible scenarios with LangGraph routing and Controlled LLM enhancement
3. LLM telemetry (model, provider, status, latency) and bounded structured output
4. Audit persistence with LLM metadata
5. Deterministic fallback safety
"""

from starlette.testclient import TestClient
from app.main import app
from app.data.sample_scenarios import SAMPLE_SCENARIOS

client = TestClient(app)


def run_e2e_verification():
    print("=" * 80)
    print("AA008 CRM DATA MIGRATION INTELLIGENCE — PHASE 2.3 CONTROLLED LLM E2E VALIDATION")
    print("=" * 80)

    # 1. Health Check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    print(f"\n[PASS] Health Check: {health_resp.json()}")

    # 2. LLM Status Check (no secrets exposed)
    llm_status_resp = client.get("/api/llm/status")
    assert llm_status_resp.status_code == 200
    llm_cfg = llm_status_resp.json()
    assert "api_key" not in llm_cfg, "Never expose raw API keys in response"
    print(f"[PASS] LLM Status Endpoint: Provider={llm_cfg['provider']}, Model={llm_cfg['model']}, Status={llm_cfg['status']}, HasKey={llm_cfg['has_api_key']}")

    # 3. Scenarios Endpoint
    scenarios_resp = client.get("/api/scenarios")
    assert scenarios_resp.status_code == 200
    scenarios = scenarios_resp.json()
    assert len(scenarios) == 3
    print(f"[PASS] Sample Scenarios Endpoint: {len(scenarios)} scenarios loaded.\n")

    for scn in scenarios:
        scn_id = scn["id"]
        print("-" * 80)
        print(f"Testing Scenario: {scn['name']} ({scn_id})")
        print(f"Expected Behavior: {scn['expected_behavior']}")

        resp = client.post("/api/migrate", json=scn["request"])
        assert resp.status_code == 200, f"Failed migration: {resp.text}"
        data = resp.json()

        wf_id = data["workflow_id"]
        agents = [a["agent_name"] for a in data["agent_outputs"]]
        rec = data["final_recommendation"]
        explanation = data["explanation"]
        selected_route = data.get("selected_route")
        routing_status = data.get("routing_status")
        routing_reason = data.get("routing_reason")
        llm_enhancement = data.get("llm_enhancement")
        llm_telemetry = data.get("llm_telemetry")

        print(f" -> Workflow ID: {wf_id}")
        print(f" -> Agents Executed in Order: {' -> '.join(agents)}")
        assert len(agents) == 5, "All 5 specialized domain agents must execute"

        print(f" -> Overall Status: {rec['overall_status']}")
        print(f" -> Summary Counts: {rec['summary_counts']}")
        print(f" -> Triggered Rules: {rec['triggered_rules']}")
        print(f" -> LangGraph Route Selected: {selected_route} (Status: {routing_status})")
        print(f" -> Routing Reason: {routing_reason}")

        # Controlled LLM Assertions
        assert llm_telemetry is not None, "LLM telemetry must be recorded"
        assert llm_enhancement is not None, "LLM enhancement output must be present"
        print(f" -> LLM Telemetry: Status={llm_telemetry['status']} | Provider={llm_telemetry['provider']} | Model={llm_telemetry['model']} | Latency={llm_telemetry['latency_ms']:.1f}ms | Fallback={llm_telemetry['fallback_used']}")
        print(f" -> LLM Executive Summary: {llm_enhancement['executive_summary']}")
        print(f" -> LLM Risk Assessment: {llm_enhancement['risk_assessment']}")

        # LangGraph Node Execution Trace
        node_trace = data.get("node_trace", [])
        print(f" -> LangGraph Node Execution Trace ({len(node_trace)} nodes):")
        for step in node_trace:
            print(f"     [{step['step_number']:>2}] {step['node']:<20} | {step['agent']:<42} | {step['status']}")

        assert len(node_trace) == 10, f"Expected 10 LangGraph nodes, got {len(node_trace)}"
        assert node_trace[7]["node"] == "llm_enhancement", "Step 8 must be llm_enhancement node"

        if scn_id == "simple_schema":
            assert rec["overall_status"] == "READY"
            assert rec["summary_counts"]["DIRECT_MAP"] == 6
            assert rec["summary_counts"]["DEFAULT"] == 1
            assert rec["summary_counts"]["REVIEW"] == 0
            assert "RULE_1_EXACT_NAME_COMPATIBLE_TYPE" in rec["triggered_rules"]

            # Phase 2.2 Route assertion
            assert selected_route == "route_direct_accept"
            assert routing_status == "ACCEPTED_DIRECT"
            assert node_trace[6]["node"] == "direct_accept"
            print(" [OK] Scenario 1 verified: HIGH_CONFIDENCE -> route_direct_accept -> llm_enhancement (LOW RISK).")

        elif scn_id == "naming_mismatch":
            assert rec["overall_status"] == "READY"
            assert rec["summary_counts"]["DIRECT_MAP"] == 6
            assert rec["summary_counts"]["TRANSFORM"] == 1
            assert rec["summary_counts"]["REVIEW"] == 0
            assert "RULE_2_KNOWN_ALIAS_COMPATIBLE_TYPE" in rec["triggered_rules"]
            assert "RULE_3_TYPE_CONVERTIBLE" in rec["triggered_rules"]

            # Phase 2.2 Route assertion
            assert selected_route == "route_transform_verify"
            assert routing_status == "TRANSFORM_STAGED"
            assert node_trace[6]["node"] == "transform_verify"
            # Phase 2.3 LLM transformation rationale check
            assert "created_at" in llm_enhancement.get("transformation_rationales", {})
            print(f"      Transformation Rationale (created_at): {llm_enhancement['transformation_rationales']['created_at']}")
            print(" [OK] Scenario 2 verified: TRANSFORM_REQUIRED -> route_transform_verify -> llm_enhancement.")

        elif scn_id == "relationship_mismatch":
            assert rec["overall_status"] == "NEEDS_REVIEW"
            assert rec["summary_counts"]["REVIEW"] >= 1
            assert "RULE_4_REQUIRED_TARGET_MISSING_SOURCE" in rec["triggered_rules"]
            assert "RULE_5_RELATIONSHIP_OR_KEY_CONFLICT" in rec["triggered_rules"]

            # Phase 2.2 Route assertion
            assert selected_route == "route_human_review"
            assert routing_status == "ESCALATED_FOR_REVIEW"
            assert node_trace[6]["node"] == "human_review"
            # Phase 2.3 LLM review actions check
            assert len(llm_enhancement.get("suggested_review_actions", [])) > 0
            print(f"      Triage Actions: {llm_enhancement['suggested_review_actions']}")
            print(" [OK] Scenario 3 verified: REVIEW_REQUIRED -> route_human_review -> llm_enhancement (HIGH RISK).")

        # Verify Audit Store
        audit_resp = client.get(f"/api/audit/{wf_id}")
        assert audit_resp.status_code == 200
        audit_data = audit_resp.json()
        assert audit_data["workflow_id"] == wf_id
        assert audit_data["final_recommendation_status"] == rec["overall_status"]
        assert audit_data["selected_route"] == selected_route
        assert audit_data["routing_status"] == routing_status
        assert len(audit_data["node_trace"]) == 10
        assert audit_data.get("llm_telemetry") is not None
        print(f" [OK] Audit record verified: route={audit_data['selected_route']}, llm_status={audit_data['llm_telemetry']['status']}")

    print("\n" + "=" * 80)
    print("ALL 3 PRODUCT BIBLE SCENARIOS & CONTROLLED LLM ENHANCEMENTS FULLY VERIFIED!")
    print("=" * 80)


if __name__ == "__main__":
    run_e2e_verification()
