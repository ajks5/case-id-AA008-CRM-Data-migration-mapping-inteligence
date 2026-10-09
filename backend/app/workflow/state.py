"""
LangGraph Workflow State Definition.
Maps the run-scoped shared workflow context (Product Bible §11 & Guide §2)
into a strongly typed LangGraph state dictionary.
"""

from typing import TypedDict, List, Dict, Any, Optional
from app.models.schemas import (
    SchemaMetadata,
    RelationshipMetadata,
    SchemaProfile,
    MappingCandidate,
    TransformationAction,
    ValidationResult,
    AgentExecutionOutput,
    MigrationRecommendation,
    Explanation,
    WorkflowContext,
    LLMEnhancementOutput,
    LLMTelemetry,
)


class WorkflowState(TypedDict, total=False):
    """
    Run-Scoped Shared Workflow Context mapped directly to LangGraph State.
    Contains strictly the fields required by Product Bible §11 and §21.
    """
    workflow_id: str
    source_schema: SchemaMetadata
    destination_schema: SchemaMetadata
    sample_rows: List[Dict[str, Any]]
    relationship_metadata: List[RelationshipMetadata]
    known_mapping_hints: Dict[str, str]

    # Populated across agent stages
    schema_profile: Optional[SchemaProfile]
    mapping_candidates: Optional[List[MappingCandidate]]
    transformation_plan: Optional[List[TransformationAction]]
    validation_results: Optional[ValidationResult]
    agent_outputs: List[AgentExecutionOutput]
    final_recommendation: Optional[MigrationRecommendation]
    explanation: Optional[Explanation]
    audit_reference: Optional[str]
    errors: List[str]

    # Traceability per Guide §9
    node_trace: List[Dict[str, Any]]

    # Phase 2.2: LangGraph Conditional Routing fields per Guide §2 & §6
    routing_status: Optional[str]
    selected_route: Optional[str]
    routing_reason: Optional[str]

    # Phase 2.3: Controlled LLM Enhancement fields per Product Bible §21
    llm_enhancement: Optional[LLMEnhancementOutput]
    llm_telemetry: Optional[LLMTelemetry]


def state_to_context(state: WorkflowState) -> WorkflowContext:
    """
    Convert LangGraph WorkflowState dictionary into the domain WorkflowContext model.
    Used by node wrappers to reuse existing domain agents unchanged.
    """
    return WorkflowContext(
        workflow_id=state.get("workflow_id", ""),
        source_schema=state.get("source_schema"),
        destination_schema=state.get("destination_schema"),
        sample_rows=state.get("sample_rows") or [],
        relationship_metadata=state.get("relationship_metadata") or [],
        known_mapping_hints=state.get("known_mapping_hints") or {},
        schema_profile=state.get("schema_profile"),
        mapping_candidates=state.get("mapping_candidates"),
        transformation_plan=state.get("transformation_plan"),
        validation_results=state.get("validation_results"),
        agent_outputs=list(state.get("agent_outputs") or []),
        final_recommendation=state.get("final_recommendation"),
        explanation=state.get("explanation"),
        audit_reference=state.get("audit_reference"),
        errors=list(state.get("errors") or []),
        node_trace=list(state.get("node_trace") or []),
        routing_status=state.get("routing_status"),
        selected_route=state.get("selected_route"),
        routing_reason=state.get("routing_reason"),
        llm_enhancement=state.get("llm_enhancement"),
        llm_telemetry=state.get("llm_telemetry"),
    )


def context_to_state(context: WorkflowContext) -> WorkflowState:
    """
    Convert domain WorkflowContext model into LangGraph WorkflowState dictionary.
    """
    return {
        "workflow_id": context.workflow_id,
        "source_schema": context.source_schema,
        "destination_schema": context.destination_schema,
        "sample_rows": context.sample_rows,
        "relationship_metadata": context.relationship_metadata,
        "known_mapping_hints": context.known_mapping_hints,
        "schema_profile": context.schema_profile,
        "mapping_candidates": context.mapping_candidates,
        "transformation_plan": context.transformation_plan,
        "validation_results": context.validation_results,
        "agent_outputs": list(context.agent_outputs),
        "final_recommendation": context.final_recommendation,
        "explanation": context.explanation,
        "audit_reference": context.audit_reference,
        "errors": list(context.errors),
        "node_trace": list(context.node_trace),
        "routing_status": context.routing_status,
        "selected_route": context.selected_route,
        "routing_reason": context.routing_reason,
        "llm_enhancement": context.llm_enhancement,
        "llm_telemetry": context.llm_telemetry,
    }

