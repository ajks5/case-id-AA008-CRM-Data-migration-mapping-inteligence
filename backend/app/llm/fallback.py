"""
Deterministic Fallback Provider for Migration Explainer.
Follows Feeder Guide §8:
- Provides a guaranteed safe deterministic template explanation
- Executes when LLM times out, fails, returns malformed output, or is disabled
- Keeps the system completely operational without unhandled exceptions
"""

from typing import Dict, Any, List
from app.models.schemas import LLMEnhancementOutput


class DeterministicFallbackProvider:
    """Generates bounded deterministic explanations from structured state when LLM is unavailable."""

    @staticmethod
    def generate(
        source_table: str,
        dest_table: str,
        overall_status: str,
        selected_route: str,
        routing_status: str,
        summary_counts: Dict[str, int],
        transformations: List[Dict[str, Any]],
        review_items: List[str],
        blocking_issues: List[str],
        unmapped_fields: List[str],
    ) -> LLMEnhancementOutput:
        """Construct deterministic fallback explanation adhering to LLMEnhancementOutput schema."""
        direct_count = summary_counts.get("DIRECT_MAP", 0)
        transform_count = summary_counts.get("TRANSFORM", 0)
        default_count = summary_counts.get("DEFAULT", 0)
        review_count = summary_counts.get("REVIEW", 0)
        total_mapped = direct_count + transform_count + default_count

        # 1. Executive Summary
        if routing_status == "ACCEPTED_DIRECT":
            summary = (
                f"Deterministic direct migration accepted for '{source_table}' -> '{dest_table}'. "
                f"All {total_mapped} fields mapped with full type compatibility under Rules 1 & 2 "
                f"with zero staging transformations and zero blocking issues."
            )
        elif routing_status == "TRANSFORM_STAGED":
            summary = (
                f"Deterministic migration staged with automated transformations for '{source_table}' -> '{dest_table}'. "
                f"{direct_count} field(s) mapped directly, while {transform_count} field(s) require data type conversion "
                f"or datetime normalization under Rule 3."
            )
        else:  # ESCALATED_FOR_REVIEW
            summary = (
                f"Deterministic migration halted for human analyst triage on '{source_table}' -> '{dest_table}'. "
                f"{review_count} field(s) flagged for review and {len(blocking_issues)} constraint violation(s) "
                f"detected under Rules 4 & 5."
            )

        # 2. Transformation Rationales
        rationales: Dict[str, str] = {}
        for action in transformations:
            dest_field = action.get("destination_field")
            if not dest_field:
                continue
            action_type = action.get("action_type", "TRANSFORMATION")
            rule = action.get("transformation_rule") or "Rule 3"
            details = action.get("details", "")
            src_field = action.get("source_field")
            source_info = f"from source field '{src_field}' " if src_field else ""
            rationales[dest_field] = (
                f"Automated {action_type} required {source_info}per {rule}. "
                f"Details: {details}."
            )

        # 3. Risk Assessment
        if review_count > 0 or len(blocking_issues) > 0:
            risk = (
                f"HIGH RISK: {review_count} unmapped or missing required field(s) and "
                f"{len(blocking_issues)} blocking constraint(s) require manual remediation."
            )
        elif transform_count > 0:
            risk = (
                f"MODERATE RISK: {transform_count} field(s) require automated transformation. "
                f"Data type conversion fidelity should be verified in staging."
            )
        else:
            risk = (
                "LOW RISK: High-confidence direct field mappings with zero constraint violations."
            )

        # 4. Suggested Review Actions
        actions: List[str] = []
        for issue in blocking_issues:
            actions.append(f"Resolve blocking constraint: {issue}")
        for item in review_items:
            actions.append(f"Review unmapped / required field: {item}")
        if unmapped_fields:
            actions.append(
                f"Review unmapped source field(s) ({', '.join(unmapped_fields)}) for potential custom attribute mapping."
            )

        return LLMEnhancementOutput(
            executive_summary=summary,
            transformation_rationales=rationales,
            risk_assessment=risk,
            suggested_review_actions=actions,
        )
