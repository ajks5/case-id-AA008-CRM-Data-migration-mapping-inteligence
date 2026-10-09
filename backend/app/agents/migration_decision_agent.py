"""
Migration Decision Agent.
Product Bible §8:
- Responsibility: Produces approved mappings and explicit review items.
- Main Input: all agent outputs
- Main Output: final_recommendation
Directly implements Bible §6 and §13.
"""

from typing import List, Dict, Any, Set
from app.models.schemas import (
    WorkflowContext,
    MigrationRecommendation,
    FieldRecommendation,
    AgentExecutionOutput,
)
from app.rules.mapping_rules import (
    RULE_1_ID,
    RULE_2_ID,
    RULE_3_ID,
    RULE_4_ID,
    RULE_5_ID,
)


class MigrationDecisionAgent:
    """Specialized domain agent for synthesizing final mapping recommendations."""

    AGENT_NAME = "Migration Decision Agent"
    RESPONSIBILITY = "Produces approved mappings and explicit review items."

    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Synthesize all prior agent outputs into a definitive migration recommendation."""
        if not context.mapping_candidates or not context.transformation_plan or not context.validation_results:
            context.errors.append("Prior agent outputs incomplete for Migration Decision Agent.")
            return context

        candidates_by_dest = {c.destination_field: c for c in context.mapping_candidates}
        transforms_by_dest = {t.destination_field: t for t in context.transformation_plan}
        val_items_by_field: Dict[str, List[Any]] = {}
        for item in context.validation_results.items:
            val_items_by_field.setdefault(item.field_name, []).append(item)

        field_recs: List[FieldRecommendation] = []
        triggered_rules: Set[str] = set()
        review_items: List[str] = []

        summary_counts = {
            "DIRECT_MAP": 0,
            "TRANSFORM": 0,
            "DEFAULT": 0,
            "UNMAPPED": 0,
            "REVIEW": 0,
        }

        # Track mapped source fields to detect unmapped sources
        mapped_sources: Set[str] = set()

        for dest in context.destination_schema.fields:
            dest_name = str(dest.get("name", ""))
            candidate = candidates_by_dest.get(dest_name)
            transform = transforms_by_dest.get(dest_name)
            val_items = val_items_by_field.get(dest_name, [])

            # Check for validation failures (Rules 4, 5, or type errors)
            failing_checks = [v for v in val_items if v.status == "FAIL"]
            
            if candidate and candidate.source_field:
                mapped_sources.add(candidate.source_field)

            # Decision Logic Priority:
            # 1. Validation Failures -> REVIEW (Rules 4 and 5)
            if failing_checks:
                triggered_rules_for_field = [v.rule_applied for v in failing_checks]
                for r in triggered_rules_for_field:
                    triggered_rules.add(r)
                
                fail_reasons = "; ".join(v.message for v in failing_checks)
                review_items.append(f"Field '{dest_name}': {fail_reasons}")

                primary_rule = triggered_rules_for_field[0]
                rec = FieldRecommendation(
                    destination_field=dest_name,
                    source_field=candidate.source_field if candidate else None,
                    decision="REVIEW",
                    confidence_score=0.0,
                    rule_id=primary_rule,
                    evidence=f"Flagged for human review due to constraints: {fail_reasons}",
                    transformation=None,
                    validation_notes=fail_reasons,
                    requires_human_review=True,
                )
                summary_counts["REVIEW"] += 1
                field_recs.append(rec)
                continue

            # 2. Type-Convertible Transformation -> TRANSFORM (Rule 3)
            if transform and transform.action_type == "TYPE_CAST":
                triggered_rules.add(RULE_3_ID)
                rec = FieldRecommendation(
                    destination_field=dest_name,
                    source_field=candidate.source_field if candidate else None,
                    decision="TRANSFORM",
                    confidence_score=70.0,
                    rule_id=RULE_3_ID,
                    evidence=f"Requires type conversion: {transform.details}. (Sample before: '{transform.sample_before}' -> after: '{transform.sample_after}')",
                    transformation=transform.transformation_rule,
                    validation_notes="Type cast verified compatible.",
                    requires_human_review=False,
                )
                summary_counts["TRANSFORM"] += 1
                field_recs.append(rec)
                continue

            # 3. Default Value -> DEFAULT
            if transform and transform.action_type == "DEFAULT_VALUE":
                rec = FieldRecommendation(
                    destination_field=dest_name,
                    source_field=None,
                    decision="DEFAULT",
                    confidence_score=100.0,
                    rule_id="DEFAULT_VALUE_RULE",
                    evidence=transform.details,
                    transformation="DEFAULT_FILL",
                    validation_notes="Optional/default value configured.",
                    requires_human_review=False,
                )
                summary_counts["DEFAULT"] += 1
                field_recs.append(rec)
                continue

            # 4. Direct Map -> DIRECT_MAP (Rules 1 & 2)
            if candidate and candidate.candidate_type in ("EXACT", "ALIAS", "HINT"):
                applied_rule = candidate.rule_applied
                triggered_rules.add(applied_rule)
                rec = FieldRecommendation(
                    destination_field=dest_name,
                    source_field=candidate.source_field,
                    decision="DIRECT_MAP",
                    confidence_score=candidate.confidence_score,
                    rule_id=applied_rule,
                    evidence=candidate.evidence,
                    transformation=None,
                    validation_notes="Deterministic match verified.",
                    requires_human_review=False,
                )
                summary_counts["DIRECT_MAP"] += 1
                field_recs.append(rec)
                continue

            # 5. Optional Unmapped -> UNMAPPED
            rec = FieldRecommendation(
                destination_field=dest_name,
                source_field=None,
                decision="UNMAPPED",
                confidence_score=0.0,
                rule_id="UNMAPPED_FIELD",
                evidence="Field is not mapped and will not receive source data.",
                transformation=None,
                validation_notes="Field will be set to NULL.",
                requires_human_review=False,
            )
            summary_counts["UNMAPPED"] += 1
            field_recs.append(rec)

        # Identify unmapped source fields
        all_sources = {f.get("name") for f in context.source_schema.fields if f.get("name")}
        unmapped_sources = sorted(list(all_sources - mapped_sources))

        # Overall Status
        if summary_counts["REVIEW"] > 0 or not context.validation_results.all_valid:
            overall_status = "NEEDS_REVIEW"
        else:
            overall_status = "READY"

        explanation_narrative = (
            f"Migration analysis completed with overall status '{overall_status}'. "
            f"Out of {len(context.destination_schema.fields)} destination fields: "
            f"{summary_counts['DIRECT_MAP']} direct mapped, "
            f"{summary_counts['TRANSFORM']} requiring transformation, "
            f"{summary_counts['DEFAULT']} filled with default values, "
            f"{summary_counts['UNMAPPED']} unmapped, and "
            f"{summary_counts['REVIEW']} requiring human review."
        )

        recommendation = MigrationRecommendation(
            overall_status=overall_status,
            summary_counts=summary_counts,
            field_recommendations=field_recs,
            triggered_rules=sorted(list(triggered_rules)),
            unmapped_source_fields=unmapped_sources,
            review_items=review_items,
            explanation_narrative=explanation_narrative,
        )

        context.final_recommendation = recommendation

        # Execution Telemetry
        context.agent_outputs.append(
            AgentExecutionOutput(
                agent_name=self.AGENT_NAME,
                responsibility=self.RESPONSIBILITY,
                status="SUCCESS",
                input_summary=f"Synthesized mapping from candidates, transformations, and validation results.",
                output_summary=f"Recommendation: {overall_status}. Summary: {summary_counts}.",
                details={
                    "overall_status": overall_status,
                    "summary_counts": summary_counts,
                    "review_count": len(review_items),
                },
            )
        )

        return context
