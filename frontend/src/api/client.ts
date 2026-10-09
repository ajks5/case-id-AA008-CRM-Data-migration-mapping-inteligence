/**
 * API client and TypeScript definitions for AA008 CRM Data Migration Intelligence.
 */

export interface RelationshipMetadata {
  source_table: string;
  source_field: string;
  target_table: string;
  target_field: string;
  relationship_type: string;
  is_required: boolean;
  description?: string;
}

export interface SchemaField {
  name: string;
  data_type: string;
  is_nullable?: boolean;
  is_required?: boolean;
  is_primary_key?: boolean;
  default_value?: any;
  description?: string;
}

export interface SchemaMetadata {
  table_name: string;
  fields: SchemaField[];
  relationships?: RelationshipMetadata[];
}

export interface MigrationRequest {
  source_schema: SchemaMetadata;
  destination_schema: SchemaMetadata;
  sample_rows?: Record<string, any>[];
  relationship_metadata?: RelationshipMetadata[];
  known_mapping_hints?: Record<string, string>;
}

export interface ScenarioItem {
  id: string;
  name: string;
  description: string;
  expected_behavior: string;
  request: MigrationRequest;
}

export interface FieldProfile {
  name: string;
  normalized_name: string;
  data_type: string;
  normalized_type: string;
  is_required: boolean;
  is_nullable: boolean;
  is_primary_key: boolean;
  sample_values: any[];
}

export interface SchemaProfile {
  source_table: string;
  destination_table: string;
  source_fields: FieldProfile[];
  destination_fields: FieldProfile[];
  source_primary_keys: string[];
  destination_primary_keys: string[];
  relationships: RelationshipMetadata[];
  field_count_source: number;
  field_count_destination: number;
}

export interface MappingCandidate {
  destination_field: string;
  source_field?: string;
  candidate_type: string;
  confidence_score: number;
  evidence: string;
  rule_applied: string;
}

export interface TransformationAction {
  destination_field: string;
  source_field?: string;
  action_type: string;
  transformation_rule?: string;
  confidence_score: number;
  details: string;
  sample_before?: any;
  sample_after?: any;
}

export interface ValidationItem {
  field_name: string;
  check_type: string;
  status: 'PASS' | 'FAIL' | 'WARNING';
  message: string;
  rule_applied: string;
}

export interface ValidationResult {
  all_valid: boolean;
  items: ValidationItem[];
  blocking_issues: string[];
  warning_issues: string[];
}

export interface FieldRecommendation {
  destination_field: string;
  source_field?: string;
  decision: 'DIRECT_MAP' | 'TRANSFORM' | 'DEFAULT' | 'UNMAPPED' | 'REVIEW';
  confidence_score: number;
  rule_id: string;
  evidence: string;
  transformation?: string;
  validation_notes?: string;
  requires_human_review: boolean;
}

export interface MigrationRecommendation {
  overall_status: 'READY' | 'NEEDS_REVIEW' | 'BLOCKED';
  summary_counts: {
    DIRECT_MAP: number;
    TRANSFORM: number;
    DEFAULT: number;
    UNMAPPED: number;
    REVIEW: number;
  };
  field_recommendations: FieldRecommendation[];
  triggered_rules: string[];
  unmapped_source_fields: string[];
  review_items: string[];
  explanation_narrative: string;
}

export interface AgentExecutionOutput {
  agent_name: string;
  responsibility: string;
  status: 'SUCCESS' | 'WARNING' | 'ERROR';
  input_summary: string;
  output_summary: string;
  timestamp: string;
  details: Record<string, any>;
}

export interface LLMEnhancementOutput {
  executive_summary: string;
  transformation_rationales: Record<string, string>;
  risk_assessment: string;
  suggested_review_actions: string[];
}

export interface LLMTelemetry {
  llm_used: boolean;
  provider: string;
  model: string;
  status: 'SUCCESS' | 'FALLBACK' | 'SKIPPED' | 'ERROR';
  fallback_used: boolean;
  validation_passed: boolean;
  latency_ms: number;
  error_message?: string;
}

export interface Explanation {
  summary: string;
  rule_citations: Array<{
    rule_id: string;
    rule_name: string;
    description: string;
    target_decision: string;
    confidence: string;
  }>;
  agent_conclusions: Array<{
    agent: string;
    responsibility: string;
    status: string;
    conclusion: string;
  }>;
  limitations_or_warnings: string[];
  llm_executive_summary?: string;
  transformation_rationales?: Record<string, string>;
  risk_assessment?: string;
  suggested_review_actions?: string[];
  llm_used?: boolean;
  fallback_used?: boolean;
}

export interface NodeTraceEntry {
  step_number: number;
  node: string;
  agent: string;
  status: string;
  summary: string;
  timestamp: string;
}

export interface AuditRecord {
  workflow_id: string;
  request_reference: string;
  timestamp: string;
  agent_execution_order: string[];
  major_outputs: Record<string, any>;
  triggered_rules: string[];
  final_recommendation_status: string;
  errors: string[];
  node_trace?: NodeTraceEntry[];
  selected_route?: string;
  routing_status?: string;
  llm_telemetry?: LLMTelemetry;
}

export interface WorkflowContext {
  workflow_id: string;
  source_schema: SchemaMetadata;
  destination_schema: SchemaMetadata;
  sample_rows: Record<string, any>[];
  relationship_metadata: RelationshipMetadata[];
  known_mapping_hints: Record<string, string>;
  schema_profile?: SchemaProfile;
  mapping_candidates?: MappingCandidate[];
  transformation_plan?: TransformationAction[];
  validation_results?: ValidationResult;
  agent_outputs: AgentExecutionOutput[];
  final_recommendation?: MigrationRecommendation;
  explanation?: Explanation;
  audit_reference?: string;
  errors: string[];
  node_trace?: NodeTraceEntry[];
  selected_route?: string;
  routing_status?: string;
  routing_reason?: string;
  llm_enhancement?: LLMEnhancementOutput;
  llm_telemetry?: LLMTelemetry;
}

export interface LLMStatus {
  provider: string;
  model: string;
  enabled: boolean;
  timeout: number;
  has_api_key: boolean;
  status: string;
}

const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = RAW_API_BASE_URL.replace(/\/+$/, '');

export async function fetchScenarios(): Promise<ScenarioItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/scenarios`);
  if (!res.ok) throw new Error(`Failed to fetch scenarios: ${res.statusText}`);
  return res.json();
}

export async function runMigration(request: MigrationRequest): Promise<WorkflowContext> {
  const res = await fetch(`${API_BASE_URL}/api/migrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Migration execution failed (${res.status}): ${errorBody}`);
  }
  return res.json();
}

export async function fetchAuditRecords(): Promise<AuditRecord[]> {
  const res = await fetch(`${API_BASE_URL}/api/audit`);
  if (!res.ok) throw new Error(`Failed to fetch audit records: ${res.statusText}`);
  return res.json();
}

export async function fetchHealth(): Promise<{ status: string; case_id: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchLLMStatus(): Promise<LLMStatus> {
  const res = await fetch(`${API_BASE_URL}/api/llm/status`);
  if (!res.ok) throw new Error(`LLM status check failed: ${res.statusText}`);
  return res.json();
}

