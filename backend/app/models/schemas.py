"""
Structured data contracts and schemas for AA008 CRM Data Migration Mapping Intelligence.
Follows Product Bible §8, §10, §11, §12, §13, §16.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RelationshipMetadata(BaseModel):
    """Foreign key and relationship descriptors between tables/fields."""
    source_table: str
    source_field: str
    target_table: str
    target_field: str
    relationship_type: str = "many_to_one"
    is_required: bool = False
    description: Optional[str] = None


class SourceField(BaseModel):
    """Metadata describing a source CRM field."""
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    description: Optional[str] = None


class DestinationField(BaseModel):
    """Metadata describing a destination CRM field."""
    name: str
    data_type: str
    is_required: bool = False
    is_nullable: bool = True
    is_primary_key: bool = False
    default_value: Optional[Any] = None
    description: Optional[str] = None


class SchemaMetadata(BaseModel):
    """Metadata for a schema / table."""
    table_name: str
    fields: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of fields (conforming to SourceField or DestinationField)"
    )
    relationships: List[RelationshipMetadata] = Field(
        default_factory=list,
        description="Foreign keys and relationships associated with this table"
    )


class MigrationRequest(BaseModel):
    """
    Business Input per Product Bible §5:
    source_schema, destination_schema, sample_rows, relationship_metadata,
    optional known_mapping_hints.
    """
    source_schema: SchemaMetadata
    destination_schema: SchemaMetadata
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list)
    relationship_metadata: List[RelationshipMetadata] = Field(default_factory=list)
    known_mapping_hints: Dict[str, str] = Field(
        default_factory=dict,
        description="Optional explicit hint mappings: {source_field: destination_field}"
    )


class FieldProfile(BaseModel):
    """Profile of a single field produced by Schema Analyzer Agent."""
    name: str
    normalized_name: str
    data_type: str
    normalized_type: str
    is_required: bool = False
    is_nullable: bool = True
    is_primary_key: bool = False
    sample_values: List[Any] = Field(default_factory=list)


class SchemaProfile(BaseModel):
    """Profile produced by Schema Analyzer Agent."""
    source_table: str
    destination_table: str
    source_fields: List[FieldProfile]
    destination_fields: List[FieldProfile]
    source_primary_keys: List[str] = Field(default_factory=list)
    destination_primary_keys: List[str] = Field(default_factory=list)
    relationships: List[RelationshipMetadata] = Field(default_factory=list)
    field_count_source: int
    field_count_destination: int


class MappingCandidate(BaseModel):
    """Candidate match produced by Field Mapping Agent."""
    destination_field: str
    source_field: Optional[str] = None
    candidate_type: str  # EXACT, ALIAS, HINT, UNMAPPED
    confidence_score: float  # 100 for exact, 90 for alias, 95 for hint, 0 for none
    evidence: str
    rule_applied: str


class TransformationAction(BaseModel):
    """Action produced by Transformation Agent."""
    destination_field: str
    source_field: Optional[str] = None
    action_type: str  # NO_OP, TYPE_CAST, DATE_FORMAT, CASE_NORMALIZATION, DEFAULT_VALUE, NONE
    transformation_rule: Optional[str] = None
    confidence_score: float = 100.0
    details: str
    sample_before: Optional[Any] = None
    sample_after: Optional[Any] = None


class ValidationItem(BaseModel):
    """Item check produced by Validation Agent."""
    field_name: str
    check_type: str  # REQUIRED_COVERAGE, TYPE_COMPATIBILITY, RELATIONSHIP_INTEGRITY
    status: str  # PASS, FAIL, WARNING
    message: str
    rule_applied: str


class ValidationResult(BaseModel):
    """Aggregate result from Validation Agent."""
    all_valid: bool
    items: List[ValidationItem] = Field(default_factory=list)
    blocking_issues: List[str] = Field(default_factory=list)
    warning_issues: List[str] = Field(default_factory=list)


class FieldRecommendation(BaseModel):
    """
    Final per-field mapping recommendation per Product Bible §6:
    DIRECT_MAP / TRANSFORM / DEFAULT / UNMAPPED / REVIEW, with confidence and evidence.
    """
    destination_field: str
    source_field: Optional[str] = None
    decision: str  # DIRECT_MAP | TRANSFORM | DEFAULT | UNMAPPED | REVIEW
    confidence_score: float
    rule_id: str
    evidence: str
    transformation: Optional[str] = None
    validation_notes: Optional[str] = None
    requires_human_review: bool = False


class MigrationRecommendation(BaseModel):
    """Final decision output produced by Migration Decision Agent."""
    overall_status: str  # READY | NEEDS_REVIEW | BLOCKED
    summary_counts: Dict[str, int]
    field_recommendations: List[FieldRecommendation]
    triggered_rules: List[str]
    unmapped_source_fields: List[str] = Field(default_factory=list)
    review_items: List[str] = Field(default_factory=list)
    explanation_narrative: str


class LLMEnhancementOutput(BaseModel):
    """
    Structured output conforming to Feeder Guide §7 and Product Bible §21:
    - Executive summary of the migration plan and routing decision.
    - Transformation rationales explaining why data type casting/date normalization is necessary.
    - Risk assessment based on review items and constraint validations.
    - Suggested review actions for migration analyst triage.
    """
    executive_summary: str = Field(
        ...,
        description="Concise 2-4 sentence executive summary of the migration plan, routing decision, and field coverage."
    )
    transformation_rationales: Dict[str, str] = Field(
        default_factory=dict,
        description="Keyed by destination_field: explanation of the technical necessity and impact of each transformation."
    )
    risk_assessment: str = Field(
        ...,
        description="Factual assessment of migration risk (LOW, MODERATE, or HIGH) based strictly on constraint items."
    )
    suggested_review_actions: List[str] = Field(
        default_factory=list,
        description="Actionable triage steps for migration analysts to resolve review flags or missing relationships."
    )


class LLMTelemetry(BaseModel):
    """
    Non-secret metadata for trace and audit per Feeder Guide §9.
    Never contains API keys or raw credentials.
    """
    llm_used: bool = False
    provider: str = "none"
    model: str = "none"
    status: str = "SKIPPED"  # SUCCESS | FALLBACK | SKIPPED | ERROR
    fallback_used: bool = False
    validation_passed: bool = False
    latency_ms: float = 0.0
    error_message: Optional[str] = None


class Explanation(BaseModel):
    """Explainability model per Product Bible §15 & §21."""
    summary: str
    rule_citations: List[Dict[str, str]]
    agent_conclusions: List[Dict[str, str]]
    limitations_or_warnings: List[str]
    # Phase 2.3: Controlled LLM Enhancement fields
    llm_executive_summary: Optional[str] = None
    transformation_rationales: Optional[Dict[str, str]] = None
    risk_assessment: Optional[str] = None
    suggested_review_actions: Optional[List[str]] = None
    llm_used: bool = False
    fallback_used: bool = False


class AgentExecutionOutput(BaseModel):
    """Telemetry of single agent execution for timeline and audit."""
    agent_name: str
    responsibility: str
    status: str  # SUCCESS | ERROR
    input_summary: str
    output_summary: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)


class AuditRecord(BaseModel):
    """Audit record per Product Bible §16."""
    workflow_id: str
    request_reference: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent_execution_order: List[str]
    major_outputs: Dict[str, Any]
    triggered_rules: List[str]
    final_recommendation_status: str
    errors: List[str] = Field(default_factory=list)
    node_trace: List[Dict[str, Any]] = Field(default_factory=list, description="LangGraph node execution trace")
    selected_route: Optional[str] = Field(default=None, description="LangGraph conditional route selected")
    routing_status: Optional[str] = Field(default=None, description="Status code of the selected conditional route")
    llm_telemetry: Optional[LLMTelemetry] = Field(default=None, description="Controlled LLM execution metadata (no secrets)")


class WorkflowContext(BaseModel):
    """
    Run-Scoped Shared Workflow Context per Product Bible §11.
    """
    workflow_id: str
    source_schema: SchemaMetadata
    destination_schema: SchemaMetadata
    sample_rows: List[Dict[str, Any]] = Field(default_factory=list)
    relationship_metadata: List[RelationshipMetadata] = Field(default_factory=list)
    known_mapping_hints: Dict[str, str] = Field(default_factory=dict)
    
    # Populated across agent stages
    schema_profile: Optional[SchemaProfile] = None
    mapping_candidates: Optional[List[MappingCandidate]] = None
    transformation_plan: Optional[List[TransformationAction]] = None
    validation_results: Optional[ValidationResult] = None
    agent_outputs: List[AgentExecutionOutput] = Field(default_factory=list)
    final_recommendation: Optional[MigrationRecommendation] = None
    explanation: Optional[Explanation] = None
    audit_reference: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    node_trace: List[Dict[str, Any]] = Field(default_factory=list, description="LangGraph node execution trace")

    # Phase 2.2: LangGraph Conditional Routing fields
    routing_status: Optional[str] = Field(default=None, description="Conditional routing status outcome")
    selected_route: Optional[str] = Field(default=None, description="Name of the evaluated conditional branch")
    routing_reason: Optional[str] = Field(default=None, description="Deterministic business rationale for route")

    # Phase 2.3: Controlled LLM Enhancement fields (Product Bible §21)
    llm_enhancement: Optional[LLMEnhancementOutput] = Field(default=None, description="Validated LLM enhancement output")
    llm_telemetry: Optional[LLMTelemetry] = Field(default=None, description="LLM execution and fallback metadata")

