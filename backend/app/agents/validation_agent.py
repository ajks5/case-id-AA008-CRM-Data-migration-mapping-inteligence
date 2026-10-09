"""
Validation Agent.
Product Bible §8:
- Responsibility: Checks required target coverage, type compatibility, and relationship integrity.
- Main Input: mapping_plan + target_constraints
- Main Output: validation_results
Implements Rule 4 & Rule 5.
"""

from typing import List, Dict, Any
from app.models.schemas import (
    WorkflowContext,
    ValidationResult,
    ValidationItem,
    AgentExecutionOutput,
)
from app.rules.mapping_rules import (
    RULE_4_ID,
    RULE_5_ID,
)


class ValidationAgent:
    """Specialized domain agent for validating coverage, constraints, and relationships."""

    AGENT_NAME = "Validation Agent"
    RESPONSIBILITY = "Checks required target coverage, type compatibility, and relationship integrity."

    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Run validation rules against current plan."""
        items: List[ValidationItem] = []
        blocking_issues: List[str] = []
        warning_issues: List[str] = []

        # Lookup tables
        dest_fields = {f.get("name"): f for f in context.destination_schema.fields if f.get("name")}
        candidates = {c.destination_field: c for c in (context.mapping_candidates or [])}
        transforms = {t.destination_field: t for t in (context.transformation_plan or [])}

        # 1. Required Target Coverage Validation (Rule 4)
        for dest_name, dest_def in dest_fields.items():
            is_required = bool(dest_def.get("is_required", False))
            has_default = dest_def.get("default_value") is not None
            candidate = candidates.get(dest_name)
            is_mapped = candidate and candidate.source_field is not None

            if is_required and not is_mapped and not has_default:
                msg = f"Mandatory target field '{dest_name}' has no mapped source field and no default value."
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="REQUIRED_COVERAGE",
                        status="FAIL",
                        message=msg,
                        rule_applied=RULE_4_ID,
                    )
                )
                blocking_issues.append(msg)
            elif is_required and not is_mapped and has_default:
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="REQUIRED_COVERAGE",
                        status="PASS",
                        message=f"Mandatory target field '{dest_name}' fulfilled via schema default value.",
                        rule_applied="DEFAULT_VALUE_COVERAGE",
                    )
                )
            elif not is_required and not is_mapped:
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="REQUIRED_COVERAGE",
                        status="WARNING",
                        message=f"Optional target field '{dest_name}' is unmapped. Will receive NULL.",
                        rule_applied="OPTIONAL_UNMAPPED",
                    )
                )
                warning_issues.append(f"Optional field '{dest_name}' will be null.")
            else:
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="REQUIRED_COVERAGE",
                        status="PASS",
                        message=f"Target field '{dest_name}' covered by source field '{candidate.source_field}'.",
                        rule_applied="MAPPED_COVERAGE",
                    )
                )

        # 2. Type Compatibility Validation
        for dest_name, transform in transforms.items():
            if transform.action_type == "INCOMPATIBLE_TYPE":
                msg = f"Target field '{dest_name}' has incompatible type conversion: {transform.details}"
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="TYPE_COMPATIBILITY",
                        status="FAIL",
                        message=msg,
                        rule_applied="INCOMPATIBLE_TYPE_RULE",
                    )
                )
                blocking_issues.append(msg)
            elif transform.action_type == "TYPE_CAST":
                items.append(
                    ValidationItem(
                        field_name=dest_name,
                        check_type="TYPE_COMPATIBILITY",
                        status="PASS",
                        message=f"Type cast verified: {transform.details}",
                        rule_applied="TYPE_CONVERSION_VERIFIED",
                    )
                )

        # 3. Relationship & Foreign Key Integrity (Rule 5)
        # "Never silently drop relationship or required-field conflicts"
        source_fields = {f.get("name") for f in context.source_schema.fields if f.get("name")}
        
        for rel in context.relationship_metadata:
            # Check if relationship applies to our destination table
            if rel.source_table == context.destination_schema.table_name:
                rel_field = rel.source_field
                is_rel_required = rel.is_required
                candidate = candidates.get(rel_field)
                
                # Check if the relationship field is mapped from source
                if is_rel_required:
                    if not candidate or not candidate.source_field:
                        msg = (
                            f"Mandatory relational link '{rel.source_table}.{rel.source_field} -> "
                            f"{rel.target_table}.{rel.target_field}' cannot be derived from source schema."
                        )
                        items.append(
                            ValidationItem(
                                field_name=rel_field,
                                check_type="RELATIONSHIP_INTEGRITY",
                                status="FAIL",
                                message=msg,
                                rule_applied=RULE_5_ID,
                            )
                        )
                        blocking_issues.append(msg)
                    else:
                        items.append(
                            ValidationItem(
                                field_name=rel_field,
                                check_type="RELATIONSHIP_INTEGRITY",
                                status="PASS",
                                message=f"Foreign key '{rel_field}' mapped from source field '{candidate.source_field}'.",
                                rule_applied="RELATIONSHIP_PRESERVED",
                            )
                        )

        all_valid = len(blocking_issues) == 0

        val_result = ValidationResult(
            all_valid=all_valid,
            items=items,
            blocking_issues=blocking_issues,
            warning_issues=warning_issues,
        )

        context.validation_results = val_result

        # Execution Telemetry
        passed_count = sum(1 for i in items if i.status == "PASS")
        failed_count = sum(1 for i in items if i.status == "FAIL")
        warn_count = sum(1 for i in items if i.status == "WARNING")

        context.agent_outputs.append(
            AgentExecutionOutput(
                agent_name=self.AGENT_NAME,
                responsibility=self.RESPONSIBILITY,
                status="SUCCESS" if all_valid else "WARNING",
                input_summary=f"Evaluated {len(dest_fields)} fields and {len(context.relationship_metadata)} relationships.",
                output_summary=f"Validation result: {'PASSED' if all_valid else 'FAILED with conflicts'} ({passed_count} pass, {failed_count} fail, {warn_count} warning).",
                details={
                    "all_valid": all_valid,
                    "blocking_issues_count": len(blocking_issues),
                    "warning_issues_count": len(warning_issues),
                    "blocking_issues": blocking_issues,
                },
            )
        )

        return context
