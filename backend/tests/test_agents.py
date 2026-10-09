"""
Tests for Individual Specialized Domain Agents.
Verifies each agent's contract per Product Bible §8 and §9:
- Schema Analyzer Agent: profiles tables, columns, types, keys, relationships.
- Field Mapping Agent: matches candidate source and target fields.
- Transformation Agent: determines casts, defaults, normalizations.
- Validation Agent: checks required target coverage, types, relationships.
- Migration Decision Agent: produces approved mappings and review items.
"""

import pytest
from app.models.schemas import MigrationRequest
from app.context.context_builder import ContextBuilder
from app.agents.schema_analyzer_agent import SchemaAnalyzerAgent
from app.agents.field_mapping_agent import FieldMappingAgent
from app.agents.transformation_agent import TransformationAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.migration_decision_agent import MigrationDecisionAgent


@pytest.fixture
def sample_request():
    return MigrationRequest(
        source_schema={
            "table_name": "legacy_accounts",
            "fields": [
                {"name": "acc_id", "data_type": "integer", "is_primary_key": True},
                {"name": "company_name", "data_type": "varchar"},
                {"name": "created_date", "data_type": "varchar"},
            ],
            "relationships": []
        },
        destination_schema={
            "table_name": "crm_accounts",
            "fields": [
                {"name": "id", "data_type": "integer", "is_primary_key": True, "is_required": True},
                {"name": "account_name", "data_type": "string", "is_required": True},
                {"name": "created_at", "data_type": "datetime", "is_required": True},
                {"name": "tier", "data_type": "string", "is_required": False, "default_value": "STANDARD"},
            ],
            "relationships": []
        },
        sample_rows=[
            {"acc_id": 1, "company_name": "Acme Corp", "created_date": "2024-01-01"}
        ],
        relationship_metadata=[],
        known_mapping_hints={"acc_id": "id"}
    )


def test_agent_1_schema_analyzer(sample_request):
    ctx = ContextBuilder.build(sample_request)
    agent = SchemaAnalyzerAgent()
    ctx = agent.execute(ctx)

    assert ctx.schema_profile is not None
    assert ctx.schema_profile.source_table == "legacy_accounts"
    assert ctx.schema_profile.destination_table == "crm_accounts"
    assert len(ctx.schema_profile.source_fields) == 3
    assert len(ctx.schema_profile.destination_fields) == 4
    assert len(ctx.agent_outputs) == 1
    assert ctx.agent_outputs[0].agent_name == "Schema Analyzer Agent"


def test_agent_2_field_mapping(sample_request):
    ctx = ContextBuilder.build(sample_request)
    ctx = SchemaAnalyzerAgent().execute(ctx)
    ctx = FieldMappingAgent().execute(ctx)

    assert ctx.mapping_candidates is not None
    assert len(ctx.mapping_candidates) == 4
    
    # Check hint match
    id_cand = next(c for c in ctx.mapping_candidates if c.destination_field == "id")
    assert id_cand.candidate_type == "HINT"
    assert id_cand.source_field == "acc_id"

    # Check alias match
    acc_name_cand = next(c for c in ctx.mapping_candidates if c.destination_field == "account_name")
    assert acc_name_cand.candidate_type == "ALIAS"
    assert acc_name_cand.source_field == "company_name"

    # Check alias + type mismatch
    created_cand = next(c for c in ctx.mapping_candidates if c.destination_field == "created_at")
    assert "MISMATCH" in created_cand.candidate_type

    assert len(ctx.agent_outputs) == 2


def test_agent_3_transformation(sample_request):
    ctx = ContextBuilder.build(sample_request)
    ctx = SchemaAnalyzerAgent().execute(ctx)
    ctx = FieldMappingAgent().execute(ctx)
    ctx = TransformationAgent().execute(ctx)

    assert ctx.transformation_plan is not None
    assert len(ctx.transformation_plan) == 4

    created_tf = next(t for t in ctx.transformation_plan if t.destination_field == "created_at")
    assert created_tf.action_type == "TYPE_CAST"
    assert created_tf.transformation_rule == "PARSE_STRING_TO_DATETIME"
    assert created_tf.sample_after == "2024-01-01T00:00:00Z"

    tier_tf = next(t for t in ctx.transformation_plan if t.destination_field == "tier")
    assert tier_tf.action_type == "DEFAULT_VALUE"
    assert tier_tf.sample_after == "STANDARD"

    assert len(ctx.agent_outputs) == 3


def test_agent_4_validation(sample_request):
    ctx = ContextBuilder.build(sample_request)
    ctx = SchemaAnalyzerAgent().execute(ctx)
    ctx = FieldMappingAgent().execute(ctx)
    ctx = TransformationAgent().execute(ctx)
    ctx = ValidationAgent().execute(ctx)

    assert ctx.validation_results is not None
    assert ctx.validation_results.all_valid is True
    assert len(ctx.validation_results.blocking_issues) == 0
    assert len(ctx.agent_outputs) == 4


def test_agent_5_migration_decision(sample_request):
    ctx = ContextBuilder.build(sample_request)
    ctx = SchemaAnalyzerAgent().execute(ctx)
    ctx = FieldMappingAgent().execute(ctx)
    ctx = TransformationAgent().execute(ctx)
    ctx = ValidationAgent().execute(ctx)
    ctx = MigrationDecisionAgent().execute(ctx)

    assert ctx.final_recommendation is not None
    assert ctx.final_recommendation.overall_status == "READY"
    assert ctx.final_recommendation.summary_counts["DIRECT_MAP"] == 2  # id (hint), account_name (alias)
    assert ctx.final_recommendation.summary_counts["TRANSFORM"] == 1   # created_at
    assert ctx.final_recommendation.summary_counts["DEFAULT"] == 1     # tier
    assert len(ctx.agent_outputs) == 5
