"""
Unit & Integration Tests for LangGraph Conditional Routing (Phase 2.2).
Validates:
1. Graph compiles successfully into an executable StateGraph with conditional edges.
2. All 11 registered nodes (6 core, 3 branch, 2 downstream) exist in the graph.
3. Scenario 1 (Normal Path - High Confidence):
   - Route selected: route_direct_accept
   - Destination node executed: direct_accept
   - Status: ACCEPTED_DIRECT / READY
4. Scenario 2 (Alternate Path - Transform Required):
   - Route selected: route_transform_verify
   - Destination node executed: transform_verify
   - Status: TRANSFORM_STAGED / READY
5. Scenario 3 (Exception Path - Missing Fields / Relationship Constraints):
   - Route selected: route_human_review
   - Destination node executed: human_review
   - Status: ESCALATED_FOR_REVIEW / NEEDS_REVIEW
6. Trace, Explanation, and Audit Store reflect routing decisions.
"""

import pytest
from app.models.schemas import MigrationRequest
from app.workflow.graph import workflow_graph, build_workflow_graph, route_after_decision
from app.workflow.orchestrator import MigrationOrchestrator
from app.workflow.state import WorkflowState, state_to_context, context_to_state
from app.data.sample_scenarios import SAMPLE_SCENARIOS
from app.audit.audit_store import audit_store
from app.rules.mapping_rules import RULE_1_ID, RULE_2_ID, RULE_3_ID, RULE_4_ID, RULE_5_ID


def test_langgraph_compilation():
    """Validate 1: The LangGraph StateGraph builds and compiles with conditional branching."""
    builder = build_workflow_graph()
    assert builder is not None

    compiled = builder.compile()
    assert compiled is not None
    assert workflow_graph is not None


def test_langgraph_conditional_node_topology():
    """Validate 2: Graph contains all 11 required nodes including conditional branch destinations."""
    builder = build_workflow_graph()
    nodes = builder.nodes
    expected_nodes = [
        "context_validation",
        "schema_analyzer",
        "field_mapper",
        "transformer",
        "validator",
        "decision",
        # Phase 2.2: Conditional branch destinations
        "direct_accept",
        "transform_verify",
        "human_review",
        # Phase 2.3: Controlled LLM enhancement
        "llm_enhancement",
        # Downstream
        "explainer",
        "audit",
    ]
    for n in expected_nodes:
        assert n in nodes, f"Expected node '{n}' missing from StateGraph."



def test_langgraph_scenario_1_normal_path():
    """
    Validate 3:
    Scenario 1 (Simple Schema) - Normal Path.
    Deterministic condition: HIGH_CONFIDENCE (all fields direct/default, 0 transforms, 0 reviews).
    Selected route: route_direct_accept -> direct_accept node.
    Business outcome: ACCEPTED_DIRECT, overall READY.
    """
    orch = MigrationOrchestrator()
    req_data = SAMPLE_SCENARIOS["simple_schema"]["request"]
    request = MigrationRequest(**req_data)

    context = orch.run(request)

    # 1. State integrity
    assert context.workflow_id.startswith("wf_")
    assert context.final_recommendation is not None
    assert context.final_recommendation.overall_status == "READY"
    assert context.final_recommendation.summary_counts["DIRECT_MAP"] == 6
    assert context.final_recommendation.summary_counts["TRANSFORM"] == 0
    assert context.final_recommendation.summary_counts["REVIEW"] == 0
    assert RULE_1_ID in context.final_recommendation.triggered_rules

    # 2. Conditional route verification
    assert context.selected_route == "route_direct_accept"
    assert context.routing_status == "ACCEPTED_DIRECT"
    assert "High confidence direct mapping" in context.routing_reason

    # 3. Dynamic node trace verification (10 nodes executed, direct_accept branch taken)
    assert len(context.node_trace) == 10
    expected_order = [
        "context_validation",
        "schema_analyzer",
        "field_mapper",
        "transformer",
        "validator",
        "decision",
        "direct_accept",
        "llm_enhancement",
        "explainer",
        "audit",
    ]
    actual_order = [entry["node"] for entry in context.node_trace]
    assert actual_order == expected_order

    # Verify direct_accept node execution telemetry
    branch_entry = context.node_trace[6]
    assert branch_entry["node"] == "direct_accept"
    assert branch_entry["status"] == "COMPLETED"
    assert "route_direct_accept" in branch_entry["summary"]


def test_langgraph_scenario_2_alternate_transform_path():
    """
    Validate 4:
    Scenario 2 (Naming Mismatch) - Alternate Path.
    Deterministic condition: TRANSFORM_REQUIRED (1 or more type casts/normalizations, 0 reviews).
    Selected route: route_transform_verify -> transform_verify node.
    Business outcome: TRANSFORM_STAGED, overall READY.
    """
    orch = MigrationOrchestrator()
    req_data = SAMPLE_SCENARIOS["naming_mismatch"]["request"]
    request = MigrationRequest(**req_data)

    context = orch.run(request)

    # 1. Recommendation verification
    assert context.final_recommendation.overall_status == "READY"
    assert context.final_recommendation.summary_counts["DIRECT_MAP"] == 6
    assert context.final_recommendation.summary_counts["TRANSFORM"] == 1
    assert context.final_recommendation.summary_counts["REVIEW"] == 0
    assert RULE_2_ID in context.final_recommendation.triggered_rules
    assert RULE_3_ID in context.final_recommendation.triggered_rules

    # 2. Conditional route verification
    assert context.selected_route == "route_transform_verify"
    assert context.routing_status == "TRANSFORM_STAGED"
    assert "Transform branch activated" in context.routing_reason

    # 3. Node trace verification (transform_verify branch taken)
    assert len(context.node_trace) == 10
    expected_order = [
        "context_validation",
        "schema_analyzer",
        "field_mapper",
        "transformer",
        "validator",
        "decision",
        "transform_verify",
        "llm_enhancement",
        "explainer",
        "audit",
    ]
    actual_order = [entry["node"] for entry in context.node_trace]
    assert actual_order == expected_order

    branch_entry = context.node_trace[6]
    assert branch_entry["node"] == "transform_verify"
    assert "route_transform_verify" in branch_entry["summary"]


def test_langgraph_scenario_3_exception_review_path():
    """
    Validate 5:
    Scenario 3 (Relationship Mismatch) - Exception / Review Path.
    Deterministic condition: REVIEW_REQUIRED / REQUIRED_FIELD_MISSING (validation constraint failures).
    Selected route: route_human_review -> human_review node.
    Business outcome: ESCALATED_FOR_REVIEW, overall NEEDS_REVIEW.
    """
    orch = MigrationOrchestrator()
    req_data = SAMPLE_SCENARIOS["relationship_mismatch"]["request"]
    request = MigrationRequest(**req_data)

    context = orch.run(request)

    # 1. Recommendation verification
    assert context.final_recommendation.overall_status == "NEEDS_REVIEW"
    assert context.final_recommendation.summary_counts["REVIEW"] >= 1
    assert context.validation_results.all_valid is False
    assert RULE_4_ID in context.final_recommendation.triggered_rules
    assert RULE_5_ID in context.final_recommendation.triggered_rules

    # 2. Conditional route verification
    assert context.selected_route == "route_human_review"
    assert context.routing_status == "ESCALATED_FOR_REVIEW"
    assert "Exception branch activated" in context.routing_reason

    # 3. Node trace verification (human_review branch taken)
    assert len(context.node_trace) == 10
    expected_order = [
        "context_validation",
        "schema_analyzer",
        "field_mapper",
        "transformer",
        "validator",
        "decision",
        "human_review",
        "llm_enhancement",
        "explainer",
        "audit",
    ]
    actual_order = [entry["node"] for entry in context.node_trace]
    assert actual_order == expected_order

    branch_entry = context.node_trace[6]
    assert branch_entry["node"] == "human_review"
    assert "route_human_review" in branch_entry["summary"]


def test_langgraph_audit_and_explanation():
    """
    Validate 6:
    Explanation and Audit nodes record routing decisions into AuditStore.
    """
    orch = MigrationOrchestrator()
    req = MigrationRequest(**SAMPLE_SCENARIOS["simple_schema"]["request"])
    ctx = orch.run(req)

    # Explanation includes conditional routing information
    assert ctx.explanation is not None
    assert "LangGraph conditional route" in ctx.explanation.summary
    assert "route_direct_accept" in ctx.explanation.summary

    # Audit record verified in store
    audit_rec = audit_store.get(ctx.workflow_id)
    assert audit_rec is not None
    assert audit_rec.workflow_id == ctx.workflow_id
    assert audit_rec.final_recommendation_status == "READY"
    assert audit_rec.selected_route == "route_direct_accept"
    assert audit_rec.routing_status == "ACCEPTED_DIRECT"
    assert len(audit_rec.node_trace) == 10
    assert audit_rec.node_trace[6]["node"] == "direct_accept"
    assert audit_rec.node_trace[7]["node"] == "llm_enhancement"
    assert audit_rec.node_trace[-1]["node"] == "audit"

