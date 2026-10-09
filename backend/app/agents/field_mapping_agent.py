"""
Field Mapping Agent.
Product Bible §8:
- Responsibility: Matches candidate source and target fields using deterministic aliases/type rules.
- Main Input: schema_profile + aliases
- Main Output: mapping_candidates
"""

from typing import List, Optional
from app.models.schemas import (
    WorkflowContext,
    MappingCandidate,
    AgentExecutionOutput,
)
from app.data.aliases import find_alias_match
from app.data.transformation_rules import are_types_directly_compatible
from app.rules.mapping_rules import (
    RULE_1_ID,
    RULE_2_ID,
)


class FieldMappingAgent:
    """Specialized domain agent for deterministic field candidate matching."""

    AGENT_NAME = "Field Mapping Agent"
    RESPONSIBILITY = "Matches candidate source and target fields using deterministic aliases/type rules."

    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Find candidate source fields for each destination field."""
        if not context.schema_profile:
            context.errors.append("Schema profile missing for Field Mapping Agent.")
            return context

        candidates: List[MappingCandidate] = []
        source_fields = {f.name: f for f in context.schema_profile.source_fields}
        source_by_norm = {f.normalized_name: f for f in context.schema_profile.source_fields}

        for dest in context.schema_profile.destination_fields:
            matched_candidate: Optional[MappingCandidate] = None

            # Priority 0: Known mapping hints supplied in request
            for src_name, target_name in context.known_mapping_hints.items():
                if target_name.lower() == dest.name.lower() and src_name in source_fields:
                    matched_candidate = MappingCandidate(
                        destination_field=dest.name,
                        source_field=src_name,
                        candidate_type="HINT",
                        confidence_score=95.0,
                        evidence=f"Explicit mapping hint specified: '{src_name}' -> '{dest.name}'",
                        rule_applied="HINT_MAPPING",
                    )
                    break

            if matched_candidate:
                candidates.append(matched_candidate)
                continue

            # Priority 1 (Rule 1): Exact normalized name match
            if dest.normalized_name in source_by_norm:
                src_match = source_by_norm[dest.normalized_name]
                is_compat = are_types_directly_compatible(src_match.data_type, dest.data_type)
                if is_compat:
                    matched_candidate = MappingCandidate(
                        destination_field=dest.name,
                        source_field=src_match.name,
                        candidate_type="EXACT",
                        confidence_score=100.0,
                        evidence=f"Exact normalized name match ('{src_match.name}' == '{dest.name}') with compatible type '{dest.normalized_type}'.",
                        rule_applied=RULE_1_ID,
                    )
                else:
                    matched_candidate = MappingCandidate(
                        destination_field=dest.name,
                        source_field=src_match.name,
                        candidate_type="EXACT_TYPE_MISMATCH",
                        confidence_score=85.0,
                        evidence=f"Exact name match ('{src_match.name}') but data type differs: source '{src_match.data_type}' vs destination '{dest.data_type}'.",
                        rule_applied=RULE_1_ID,
                    )

            if matched_candidate:
                candidates.append(matched_candidate)
                continue

            # Priority 2 (Rule 2): Known CRM alias match
            alias_match_found = None
            alias_evidence = None
            for src_name, src_field in source_fields.items():
                evidence_text = find_alias_match(dest.name, src_name)
                if evidence_text:
                    alias_match_found = src_field
                    alias_evidence = evidence_text
                    break

            if alias_match_found:
                is_compat = are_types_directly_compatible(alias_match_found.data_type, dest.data_type)
                if is_compat:
                    matched_candidate = MappingCandidate(
                        destination_field=dest.name,
                        source_field=alias_match_found.name,
                        candidate_type="ALIAS",
                        confidence_score=90.0,
                        evidence=f"{alias_evidence} with compatible type '{dest.normalized_type}'.",
                        rule_applied=RULE_2_ID,
                    )
                else:
                    matched_candidate = MappingCandidate(
                        destination_field=dest.name,
                        source_field=alias_match_found.name,
                        candidate_type="ALIAS_TYPE_MISMATCH",
                        confidence_score=75.0,
                        evidence=f"{alias_evidence}, but data type differs: source '{alias_match_found.data_type}' vs destination '{dest.data_type}'.",
                        rule_applied=RULE_2_ID,
                    )

            if matched_candidate:
                candidates.append(matched_candidate)
                continue

            # Check if destination field has a default value defined in schema
            raw_dest_field = next(
                (f for f in context.destination_schema.fields if f.get("name") == dest.name), None
            )
            has_default = raw_dest_field and raw_dest_field.get("default_value") is not None

            if has_default:
                default_val = raw_dest_field.get("default_value")
                matched_candidate = MappingCandidate(
                    destination_field=dest.name,
                    source_field=None,
                    candidate_type="DEFAULT_VALUE",
                    confidence_score=60.0,
                    evidence=f"No source field mapped; target field specifies default value '{default_val}'.",
                    rule_applied="DEFAULT_VALUE_FALLBACK",
                )
            else:
                matched_candidate = MappingCandidate(
                    destination_field=dest.name,
                    source_field=None,
                    candidate_type="UNMAPPED",
                    confidence_score=0.0,
                    evidence="No candidate source field or recognized CRM alias found.",
                    rule_applied="UNMAPPED",
                )

            candidates.append(matched_candidate)

        context.mapping_candidates = candidates

        # Execution Telemetry
        mapped_count = sum(1 for c in candidates if c.candidate_type in ("EXACT", "ALIAS", "HINT"))
        mismatch_count = sum(1 for c in candidates if "MISMATCH" in c.candidate_type)
        unmapped_count = sum(1 for c in candidates if c.candidate_type == "UNMAPPED")

        context.agent_outputs.append(
            AgentExecutionOutput(
                agent_name=self.AGENT_NAME,
                responsibility=self.RESPONSIBILITY,
                status="SUCCESS",
                input_summary=f"Evaluated {len(context.schema_profile.destination_fields)} target fields against {len(context.schema_profile.source_fields)} source fields.",
                output_summary=f"Generated {len(candidates)} candidates: {mapped_count} direct, {mismatch_count} type convertible, {unmapped_count} unmapped.",
                details={
                    "direct_mapped": mapped_count,
                    "type_mismatch_candidates": mismatch_count,
                    "unmapped": unmapped_count,
                },
            )
        )

        return context
