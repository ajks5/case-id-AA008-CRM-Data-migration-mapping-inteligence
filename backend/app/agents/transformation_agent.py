"""
Transformation Agent.
Product Bible §8:
- Responsibility: Determines required casts, defaults, normalizations, or derived transforms.
- Main Input: mapping_candidates + samples
- Main Output: transformation_plan
"""

from typing import List, Dict, Any, Optional
from app.models.schemas import (
    WorkflowContext,
    TransformationAction,
    AgentExecutionOutput,
)
from app.data.transformation_rules import (
    get_transformation_rule,
    apply_sample_transformation,
)
from app.rules.mapping_rules import RULE_3_ID


class TransformationAgent:
    """Specialized domain agent for determining field transformations and casts."""

    AGENT_NAME = "Transformation Agent"
    RESPONSIBILITY = "Determines required casts, defaults, normalizations, or derived transforms."

    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Evaluate mapping candidates and build transformation plan."""
        if not context.mapping_candidates:
            context.errors.append("Mapping candidates missing for Transformation Agent.")
            return context

        source_field_map = {
            f.get("name"): f for f in context.source_schema.fields if f.get("name")
        }
        dest_field_map = {
            f.get("name"): f for f in context.destination_schema.fields if f.get("name")
        }

        # Sample rows lookup helper
        sample_row = context.sample_rows[0] if context.sample_rows else {}

        actions: List[TransformationAction] = []

        for candidate in context.mapping_candidates:
            dest_name = candidate.destination_field
            src_name = candidate.source_field
            dest_def = dest_field_map.get(dest_name, {})
            src_def = source_field_map.get(src_name, {}) if src_name else {}

            dest_type = dest_def.get("data_type", "string")
            src_type = src_def.get("data_type", "string")

            # Case 1: Default value fill
            if candidate.candidate_type == "DEFAULT_VALUE":
                default_val = dest_def.get("default_value")
                actions.append(
                    TransformationAction(
                        destination_field=dest_name,
                        source_field=None,
                        action_type="DEFAULT_VALUE",
                        transformation_rule="DEFAULT_FILL",
                        confidence_score=100.0,
                        details=f"Populate target field with schema default: '{default_val}'",
                        sample_before=None,
                        sample_after=default_val,
                    )
                )
                continue

            # Case 2: Unmapped field
            if candidate.candidate_type == "UNMAPPED" or not src_name:
                actions.append(
                    TransformationAction(
                        destination_field=dest_name,
                        source_field=None,
                        action_type="NONE",
                        transformation_rule=None,
                        confidence_score=0.0,
                        details="No transformation applicable (unmapped target field).",
                        sample_before=None,
                        sample_after=None,
                    )
                )
                continue

            # Case 3: Type mismatch requiring transformation (Rule 3)
            if "MISMATCH" in candidate.candidate_type:
                rule_info = get_transformation_rule(src_type, dest_type)
                sample_val = sample_row.get(src_name)

                if rule_info:
                    rule_name, rule_desc = rule_info
                    sample_after = apply_sample_transformation(rule_name, sample_val)
                    actions.append(
                        TransformationAction(
                            destination_field=dest_name,
                            source_field=src_name,
                            action_type="TYPE_CAST",
                            transformation_rule=rule_name,
                            confidence_score=70.0,
                            details=f"Rule 3 ({rule_name}): {rule_desc}",
                            sample_before=sample_val,
                            sample_after=sample_after,
                        )
                    )
                else:
                    # Incompatible type
                    actions.append(
                        TransformationAction(
                            destination_field=dest_name,
                            source_field=src_name,
                            action_type="INCOMPATIBLE_TYPE",
                            transformation_rule=None,
                            confidence_score=20.0,
                            details=f"Cannot transform source type '{src_type}' to target type '{dest_type}'.",
                            sample_before=sample_val,
                            sample_after=None,
                        )
                    )
                continue

            # Case 4: Direct compatible mapping
            sample_val = sample_row.get(src_name)
            actions.append(
                TransformationAction(
                    destination_field=dest_name,
                    source_field=src_name,
                    action_type="NO_OP",
                    transformation_rule="DIRECT_COPY",
                    confidence_score=100.0,
                    details=f"Direct 1:1 copy from source '{src_name}' ({src_type}) to target '{dest_name}' ({dest_type}).",
                    sample_before=sample_val,
                    sample_after=sample_val,
                )
            )

        context.transformation_plan = actions

        # Execution Telemetry
        transforms_count = sum(1 for a in actions if a.action_type == "TYPE_CAST")
        defaults_count = sum(1 for a in actions if a.action_type == "DEFAULT_VALUE")
        noop_count = sum(1 for a in actions if a.action_type == "NO_OP")

        context.agent_outputs.append(
            AgentExecutionOutput(
                agent_name=self.AGENT_NAME,
                responsibility=self.RESPONSIBILITY,
                status="SUCCESS",
                input_summary=f"Processed {len(context.mapping_candidates)} candidates with {len(context.sample_rows)} sample rows.",
                output_summary=f"Planned transformations: {noop_count} direct copy, {transforms_count} type conversions, {defaults_count} default fills.",
                details={
                    "type_casts": transforms_count,
                    "default_fills": defaults_count,
                    "direct_copies": noop_count,
                },
            )
        )

        return context
