"""
Tests for Deterministic Mapping Rules (Rules 1 - 5).
Directly asserts Product Bible §12:
1. Exact normalized-name + compatible type -> DIRECT_MAP.
2. Known alias + compatible type -> DIRECT_MAP with evidence.
3. Type-convertible fields -> TRANSFORM.
4. Required target field without valid source/default -> REVIEW.
5. Never silently drop relationship or required-field conflicts.
"""

import pytest
from app.data.aliases import find_alias_match, normalize_identifier
from app.data.transformation_rules import (
    normalize_type,
    are_types_directly_compatible,
    get_transformation_rule,
    apply_sample_transformation,
)
from app.rules.mapping_rules import (
    RULE_1_ID,
    RULE_2_ID,
    RULE_3_ID,
    RULE_4_ID,
    RULE_5_ID,
    RULE_METADATA,
)
from app.models.schemas import MigrationRequest
from app.workflow.orchestrator import MigrationOrchestrator


def test_rule_metadata_exists():
    """Verify all 5 rules are registered with base confidence scores."""
    assert RULE_1_ID in RULE_METADATA
    assert RULE_2_ID in RULE_METADATA
    assert RULE_3_ID in RULE_METADATA
    assert RULE_4_ID in RULE_METADATA
    assert RULE_5_ID in RULE_METADATA

    assert RULE_METADATA[RULE_1_ID]["base_confidence"] == 100.0
    assert RULE_METADATA[RULE_2_ID]["base_confidence"] == 90.0
    assert RULE_METADATA[RULE_3_ID]["base_confidence"] == 70.0
    assert RULE_METADATA[RULE_4_ID]["base_confidence"] == 0.0
    assert RULE_METADATA[RULE_5_ID]["base_confidence"] == 0.0


def test_rule_1_exact_name_and_compatible_type():
    """Rule 1: Exact normalized name + compatible type yields DIRECT_MAP."""
    assert normalize_identifier("First_Name") == normalize_identifier("first_name")
    assert are_types_directly_compatible("varchar", "string") is True
    assert are_types_directly_compatible("integer", "int") is True


def test_rule_2_known_alias_match():
    """Rule 2: Known alias matches canonical target."""
    match = find_alias_match("email", "email_addr")
    assert match is not None
    assert "known CRM alias" in match

    match_cust = find_alias_match("customer_id", "cust_id")
    assert match_cust is not None
    assert "known CRM alias" in match_cust

    match_phone = find_alias_match("phone", "phone_num")
    assert match_phone is not None


def test_rule_3_type_convertible_transformations():
    """Rule 3: Type-convertible fields yield TRANSFORM actions."""
    # string -> datetime
    res = get_transformation_rule("string", "datetime")
    assert res is not None
    rule_name, desc = res
    assert rule_name == "PARSE_STRING_TO_DATETIME"

    # int -> string
    res_int_str = get_transformation_rule("integer", "string")
    assert res_int_str is not None
    assert res_int_str[0] == "CAST_INT_TO_STRING"

    # Sample transformation simulation
    val = apply_sample_transformation("PARSE_STRING_TO_DATETIME", "2024-05-10")
    assert val == "2024-05-10T00:00:00Z"


def test_rule_4_required_target_missing_source_flagged_for_review():
    """Rule 4: Required target field without source or default triggers REVIEW."""
    req = MigrationRequest(
        source_schema={
            "table_name": "src",
            "fields": [{"name": "col_a", "data_type": "string"}],
            "relationships": []
        },
        destination_schema={
            "table_name": "dest",
            "fields": [
                {"name": "col_a", "data_type": "string", "is_required": False},
                {"name": "required_missing_col", "data_type": "string", "is_required": True}
            ],
            "relationships": []
        },
        sample_rows=[],
        relationship_metadata=[],
        known_mapping_hints={}
    )
    orch = MigrationOrchestrator()
    ctx = orch.run(req)
    
    assert ctx.final_recommendation is not None
    assert ctx.final_recommendation.overall_status == "NEEDS_REVIEW"
    missing_rec = next(
        r for r in ctx.final_recommendation.field_recommendations
        if r.destination_field == "required_missing_col"
    )
    assert missing_rec.decision == "REVIEW"
    assert missing_rec.rule_id == RULE_4_ID
    assert missing_rec.requires_human_review is True


def test_rule_5_relationship_conflict_flagged_for_review():
    """Rule 5: Relationship conflicts are never silently dropped; triggers REVIEW."""
    req = MigrationRequest(
        source_schema={
            "table_name": "flat_src",
            "fields": [{"name": "id", "data_type": "integer"}],
            "relationships": []
        },
        destination_schema={
            "table_name": "rel_dest",
            "fields": [
                {"name": "id", "data_type": "integer", "is_required": True},
                {"name": "parent_id", "data_type": "integer", "is_required": True}
            ],
            "relationships": [
                {
                    "source_table": "rel_dest",
                    "source_field": "parent_id",
                    "target_table": "orgs",
                    "target_field": "id",
                    "is_required": True
                }
            ]
        },
        sample_rows=[],
        relationship_metadata=[],
        known_mapping_hints={}
    )
    orch = MigrationOrchestrator()
    ctx = orch.run(req)

    assert ctx.final_recommendation is not None
    assert ctx.final_recommendation.overall_status == "NEEDS_REVIEW"
    assert RULE_5_ID in ctx.final_recommendation.triggered_rules
    parent_rec = next(
        r for r in ctx.final_recommendation.field_recommendations
        if r.destination_field == "parent_id"
    )
    assert parent_rec.decision == "REVIEW"
