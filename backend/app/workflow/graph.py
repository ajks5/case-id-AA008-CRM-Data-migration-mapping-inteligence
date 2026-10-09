"""
LangGraph Conditional Workflow Definition for AA008 CRM Data Migration Intelligence.
Follows Product Bible §14, §20 and 01_LangGraph_Evolution_Guide.md §6, §7, §8, §9.

Conditional Topology:
START
  ↓
context_validation (Context / Validation Node)
  ↓
schema_analyzer    (Agent 1 Node)
  ↓
field_mapper       (Agent 2 Node)
  ↓
transformer        (Agent 3 Node)
  ↓
validator          (Agent 4 Node)
  ↓
decision           (Decision Node)
  ↓
[conditional_router: route_after_decision]
  ├── "route_direct_accept"   ──> direct_accept   (Branch Node A: HIGH_CONFIDENCE)   ──┐
  ├── "route_transform_verify" ──> transform_verify (Branch Node B: TRANSFORM_REQUIRED) ──┤
  └── "route_human_review"    ──> human_review    (Branch Node C: REVIEW_REQUIRED)    ──┘
                                                                                        ↓
                                                                                    explainer (Explanation Node)
                                                                                        ↓
                                                                                      audit   (Audit Node)
                                                                                        ↓
                                                                                       END
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from langgraph.graph import StateGraph, START, END

from app.models.schemas import (
    MigrationRequest,
    WorkflowContext,
    AgentExecutionOutput,
)
from app.context.context_builder import ContextBuilder
from app.agents.schema_analyzer_agent import SchemaAnalyzerAgent
from app.agents.field_mapping_agent import FieldMappingAgent
from app.agents.transformation_agent import TransformationAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.migration_decision_agent import MigrationDecisionAgent
from app.explanation.explainer import MigrationExplainer
from app.audit.audit_store import audit_store
from app.llm.service import MigrationLLMService
from app.workflow.state import WorkflowState, state_to_context


# Instantiate domain agents and services (preserved unchanged)
_schema_analyzer = SchemaAnalyzerAgent()
_field_mapper = FieldMappingAgent()
_transformer = TransformationAgent()
_validator = ValidationAgent()
_decision_agent = MigrationDecisionAgent()
_explainer = MigrationExplainer()
_llm_service = MigrationLLMService()


def _append_trace(
    current_trace: List[Dict[str, Any]],
    node_name: str,
    agent_name: str,
    summary: str,
    status: str = "COMPLETED",
) -> List[Dict[str, Any]]:
    """Helper to append structured node trace telemetry."""
    trace_list = list(current_trace or [])
    trace_list.append({
        "step_number": len(trace_list) + 1,
        "node": node_name,
        "agent": agent_name,
        "status": status,
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return trace_list


# -------------------------------------------------------------------------
# Node Implementations
# -------------------------------------------------------------------------

def context_validation_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 1: Context Builder & Input Validation Node.
    Validates business input schemas and initializes run-scoped context.
    """
    source_schema = state.get("source_schema")
    dest_schema = state.get("destination_schema")
    
    # Construct MigrationRequest to reuse deterministic ContextBuilder logic
    req = MigrationRequest(
        source_schema=source_schema,
        destination_schema=dest_schema,
        sample_rows=state.get("sample_rows") or [],
        relationship_metadata=state.get("relationship_metadata") or [],
        known_mapping_hints=state.get("known_mapping_hints") or {},
    )
    context = ContextBuilder.build(req)

    # Preserve explicit workflow_id if pre-assigned
    if state.get("workflow_id"):
        context.workflow_id = state["workflow_id"]

    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="context_validation",
        agent_name="Context Builder & Input Validator",
        summary=(
            f"Initialized workflow {context.workflow_id} "
            f"({len(context.relationship_metadata)} relationships, {len(context.sample_rows)} sample rows)."
        ),
    )

    return {
        "workflow_id": context.workflow_id,
        "source_schema": context.source_schema,
        "destination_schema": context.destination_schema,
        "sample_rows": context.sample_rows,
        "relationship_metadata": context.relationship_metadata,
        "known_mapping_hints": context.known_mapping_hints,
        "agent_outputs": [],
        "errors": context.errors,
        "node_trace": new_trace,
    }


def schema_analyzer_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 2: Schema Analyzer Agent Node.
    Profiles source and destination tables, columns, types, and primary keys.
    """
    context = state_to_context(state)
    context = _schema_analyzer.execute(context)

    summary = (
        context.agent_outputs[-1].output_summary
        if context.agent_outputs
        else "Schema profiling completed."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="schema_analyzer",
        agent_name=_schema_analyzer.AGENT_NAME,
        summary=summary,
    )

    return {
        "schema_profile": context.schema_profile,
        "agent_outputs": context.agent_outputs,
        "errors": context.errors,
        "node_trace": new_trace,
    }


def field_mapper_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 3: Field Mapping Agent Node.
    Matches candidate source and target fields via exact name and CRM aliases.
    """
    context = state_to_context(state)
    context = _field_mapper.execute(context)

    summary = (
        context.agent_outputs[-1].output_summary
        if context.agent_outputs
        else "Field candidate mapping completed."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="field_mapper",
        agent_name=_field_mapper.AGENT_NAME,
        summary=summary,
    )

    return {
        "mapping_candidates": context.mapping_candidates,
        "agent_outputs": context.agent_outputs,
        "errors": context.errors,
        "node_trace": new_trace,
    }


def transformer_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 4: Transformation Agent Node.
    Determines type casting, date normalization, or default value applications.
    """
    context = state_to_context(state)
    context = _transformer.execute(context)

    summary = (
        context.agent_outputs[-1].output_summary
        if context.agent_outputs
        else "Transformation planning completed."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="transformer",
        agent_name=_transformer.AGENT_NAME,
        summary=summary,
    )

    return {
        "transformation_plan": context.transformation_plan,
        "agent_outputs": context.agent_outputs,
        "errors": context.errors,
        "node_trace": new_trace,
    }


def validator_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 5: Validation Agent Node.
    Verifies required target field coverage and relationship integrity constraints.
    """
    context = state_to_context(state)
    context = _validator.execute(context)

    summary = (
        context.agent_outputs[-1].output_summary
        if context.agent_outputs
        else "Constraint validation completed."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="validator",
        agent_name=_validator.AGENT_NAME,
        summary=summary,
    )

    return {
        "validation_results": context.validation_results,
        "agent_outputs": context.agent_outputs,
        "errors": context.errors,
        "node_trace": new_trace,
    }


def decision_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 6: Migration Decision Agent Node.
    Synthesizes prior agent findings into final per-field actions and overall status.
    """
    context = state_to_context(state)
    context = _decision_agent.execute(context)

    summary = (
        context.agent_outputs[-1].output_summary
        if context.agent_outputs
        else "Final migration recommendation generated."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="decision",
        agent_name=_decision_agent.AGENT_NAME,
        summary=summary,
    )

    return {
        "final_recommendation": context.final_recommendation,
        "agent_outputs": context.agent_outputs,
        "errors": context.errors,
        "node_trace": new_trace,
    }



# -------------------------------------------------------------------------
# Phase 2.2: Conditional Routing Function & Branch Destination Nodes
# Product Bible §20:
# HIGH_CONFIDENCE -> accept mapping (route_direct_accept)
# TRANSFORM_REQUIRED -> transform branch (route_transform_verify)
# LOW_CONFIDENCE / REQUIRED_FIELD_MISSING -> review / escalate (route_human_review)
# -------------------------------------------------------------------------

def route_after_decision(state: WorkflowState) -> str:
    """
    Deterministic LangGraph Conditional Router.
    Implements Product Bible §20 and Guide §6, §7, §8:
    Reads state:
    - final_recommendation.overall_status
    - final_recommendation.summary_counts
    - validation_results.all_valid
    - validation_results.blocking_issues
    Returns route key:
    - 'route_human_review' if constraints violated or review items present (Rule 4 / Rule 5)
    - 'route_transform_verify' if type conversions are required (Rule 3)
    - 'route_direct_accept' if 100% direct-compatible matches (Rules 1 & 2)
    """
    rec = state.get("final_recommendation")
    val = state.get("validation_results")

    # Priority 1: Exception / Constraint / Validation Failure -> Human Review Branch
    # Product Bible §20: "LOW_CONFIDENCE → review; REQUIRED_FIELD_MISSING → block/resolve"
    if (
        not val
        or not val.all_valid
        or (rec and rec.overall_status == "NEEDS_REVIEW")
        or (rec and rec.summary_counts.get("REVIEW", 0) > 0)
    ):
        return "route_human_review"

    # Priority 2: Transformation Required -> Transform Branch
    # Product Bible §20: "TRANSFORM_REQUIRED → transform branch"
    if rec and rec.summary_counts.get("TRANSFORM", 0) > 0:
        return "route_transform_verify"

    # Priority 3: High Confidence Direct Mapping -> Accept Mapping Branch
    # Product Bible §20: "HIGH_CONFIDENCE → accept mapping"
    return "route_direct_accept"


def direct_accept_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Branch Node A: Direct Mapping Acceptance Gateway.
    Product Bible §20: 'HIGH_CONFIDENCE → accept mapping'.
    Executed when 100% of fields are direct compatible matches or defaults (Scenario 1).
    """
    selected_route = "route_direct_accept"
    routing_status = "ACCEPTED_DIRECT"
    routing_reason = (
        "High confidence direct mapping: all target fields mapped with compatible types (Rules 1 & 2), "
        "0 type casts, and 0 constraint violations."
    )

    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="direct_accept",
        agent_name="Direct Acceptance Gateway",
        summary=f"Branch '{selected_route}' taken: {routing_reason}",
        status="COMPLETED",
    )

    return {
        "selected_route": selected_route,
        "routing_status": routing_status,
        "routing_reason": routing_reason,
        "node_trace": new_trace,
    }


def transform_verify_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Branch Node B: Transformation Staging & Verification Gateway.
    Product Bible §20: 'TRANSFORM_REQUIRED → transform branch'.
    Executed when fields require type conversions or date normalizations (Scenario 2).
    """
    selected_route = "route_transform_verify"
    routing_status = "TRANSFORM_STAGED"
    transform_count = 0
    if state.get("final_recommendation"):
        transform_count = state["final_recommendation"].summary_counts.get("TRANSFORM", 0)

    routing_reason = (
        f"Transform branch activated: {transform_count} field(s) require type casting or formatting "
        "(Rule 3). Staged for automated transformation pipeline verification."
    )

    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="transform_verify",
        agent_name="Transformation Verification Gateway",
        summary=f"Branch '{selected_route}' taken: {routing_reason}",
        status="COMPLETED",
    )

    return {
        "selected_route": selected_route,
        "routing_status": routing_status,
        "routing_reason": routing_reason,
        "node_trace": new_trace,
    }


def human_review_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Branch Node C: Human Review & Exception Triage Gateway.
    Product Bible §20: 'LOW_CONFIDENCE → review; REQUIRED_FIELD_MISSING → block/resolve'.
    Executed when missing required fields, unresolvable relationships, or constraint failures occur (Scenario 3).
    """
    selected_route = "route_human_review"
    routing_status = "ESCALATED_FOR_REVIEW"
    review_count = 0
    if state.get("final_recommendation"):
        review_count = len(state["final_recommendation"].review_items)
    blocking_count = 0
    if state.get("validation_results"):
        blocking_count = len(state["validation_results"].blocking_issues)

    routing_reason = (
        f"Exception branch activated: {review_count} item(s) flagged for human review and "
        f"{blocking_count} blocking constraint violation(s) (Rules 4 & 5). Automated execution halted."
    )

    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="human_review",
        agent_name="Human Review & Triage Gateway",
        summary=f"Branch '{selected_route}' taken: {routing_reason}",
        status="COMPLETED",
    )

    return {
        "selected_route": selected_route,
        "routing_status": routing_status,
        "routing_reason": routing_reason,
        "node_trace": new_trace,
    }


def llm_enhancement_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 7: Controlled LLM Enhancement Node.
    Implements Product Bible §21 and Feeder Guide §3, §4, §6, §7, §8:
    - Bounded purpose: Migration rationale and transformation explanation
    - Authoritative inputs: Deterministic outputs only (never modifies decisions)
    - Validated structured output adhering to LLMEnhancementOutput
    - Automatic deterministic fallback on error, timeout, or schema failure
    """
    rec = state.get("final_recommendation")
    val = state.get("validation_results")
    src_schema = state.get("source_schema")
    dest_schema = state.get("destination_schema")

    src_table = src_schema.table_name if src_schema else "unknown_source"
    dest_table = dest_schema.table_name if dest_schema else "unknown_destination"

    # Extract planned transformations
    transformations: List[Dict[str, Any]] = []
    if state.get("transformation_plan"):
        for t in state["transformation_plan"]:
            transformations.append(t.model_dump())

    # Extract valid destination fields to guard against hallucinated keys
    valid_dest_fields = set()
    if dest_schema:
        for f in dest_schema.fields:
            if isinstance(f, dict):
                valid_dest_fields.add(f.get("name", ""))
            elif hasattr(f, "name"):
                valid_dest_fields.add(getattr(f, "name"))

    enhancement_output, telemetry = _llm_service.enhance(
        source_table=src_table,
        dest_table=dest_table,
        overall_status=rec.overall_status if rec else "NEEDS_REVIEW",
        selected_route=state.get("selected_route") or "route_human_review",
        routing_status=state.get("routing_status") or "ESCALATED_FOR_REVIEW",
        summary_counts=rec.summary_counts if rec else {},
        triggered_rules=rec.triggered_rules if rec else [],
        transformations=transformations,
        review_items=rec.review_items if rec else [],
        blocking_issues=val.blocking_issues if val else [],
        unmapped_fields=rec.unmapped_source_fields if rec else [],
        valid_dest_fields=valid_dest_fields,
    )

    summary_msg = (
        f"LLM Status: {telemetry.status} | Provider: {telemetry.provider} | Model: {telemetry.model} | "
        f"Fallback: {telemetry.fallback_used} | Latency: {telemetry.latency_ms:.1f}ms"
    )

    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="llm_enhancement",
        agent_name="Controlled LLM Enhancement (Product Bible §21)",
        summary=summary_msg,
        status="COMPLETED",
    )

    return {
        "llm_enhancement": enhancement_output,
        "llm_telemetry": telemetry,
        "node_trace": new_trace,
    }


def explainer_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 8: Explanation Node.
    Extracts factual rule citations, limitations, routing outcome, and summary directly from state.
    """
    context = state_to_context(state)
    context = _explainer.explain(context)

    summary = (
        context.explanation.summary
        if context.explanation
        else "Explanation derived from executed rules."
    )
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="explainer",
        agent_name="Migration Explainer",
        summary=summary,
    )

    return {
        "explanation": context.explanation,
        "errors": context.errors,
        "node_trace": new_trace,
    }


def audit_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Node 9: Audit Trail Node.
    Records the completed workflow, routing decisions, and execution trace into the immutable audit store.
    """
    # Append final audit trace step first so it is included in the recorded audit record
    new_trace = _append_trace(
        state.get("node_trace", []),
        node_name="audit",
        agent_name="Audit Store",
        summary="Workflow execution, routing decision, and telemetry logged into in-memory audit store.",
    )

    context = state_to_context(state)
    context.node_trace = new_trace
    audit_record = audit_store.record_workflow(context)

    return {
        "audit_reference": audit_record.workflow_id,
        "node_trace": new_trace,
    }


# -------------------------------------------------------------------------
# Graph Construction & Compilation
# -------------------------------------------------------------------------

def build_workflow_graph() -> StateGraph:
    """Constructs the LangGraph StateGraph with conditional routing and controlled LLM enhancement."""
    builder = StateGraph(WorkflowState)

    # 1. Register Core Deterministic Nodes (Nodes 1-6)
    builder.add_node("context_validation", context_validation_node)
    builder.add_node("schema_analyzer", schema_analyzer_node)
    builder.add_node("field_mapper", field_mapper_node)
    builder.add_node("transformer", transformer_node)
    builder.add_node("validator", validator_node)
    builder.add_node("decision", decision_node)

    # 2. Register Phase 2.2 Conditional Destination Branch Nodes
    builder.add_node("direct_accept", direct_accept_node)
    builder.add_node("transform_verify", transform_verify_node)
    builder.add_node("human_review", human_review_node)

    # 3. Register Phase 2.3 Controlled LLM Enhancement Node
    builder.add_node("llm_enhancement", llm_enhancement_node)

    # 4. Register Post-LLM Downstream Nodes
    builder.add_node("explainer", explainer_node)
    builder.add_node("audit", audit_node)

    # 5. Linear Edges leading up to Decision
    builder.add_edge(START, "context_validation")
    builder.add_edge("context_validation", "schema_analyzer")
    builder.add_edge("schema_analyzer", "field_mapper")
    builder.add_edge("field_mapper", "transformer")
    builder.add_edge("transformer", "validator")
    builder.add_edge("validator", "decision")

    # 6. Phase 2.2: Conditional Edges from Decision to Destination Branch Nodes
    builder.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "route_direct_accept": "direct_accept",
            "route_transform_verify": "transform_verify",
            "route_human_review": "human_review",
        },
    )

    # 7. Phase 2.3: Branch Nodes converge into Controlled LLM Enhancement Node
    builder.add_edge("direct_accept", "llm_enhancement")
    builder.add_edge("transform_verify", "llm_enhancement")
    builder.add_edge("human_review", "llm_enhancement")

    # 8. Post-LLM Convergence to Explanation and Audit
    builder.add_edge("llm_enhancement", "explainer")
    builder.add_edge("explainer", "audit")
    builder.add_edge("audit", END)

    return builder


# Pre-compiled singleton workflow graph
workflow_graph = build_workflow_graph().compile()

