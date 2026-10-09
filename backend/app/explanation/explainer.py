"""
Explainability layer for AA008 CRM Data Migration Mapping Intelligence.
Follows Product Bible §15 and Feeder Guide 04.
Strict rule: Does not invent evidence; only cites facts present in workflow state.
"""

from typing import List, Dict, Any
from app.models.schemas import WorkflowContext, Explanation
from app.rules.mapping_rules import RULE_METADATA


class MigrationExplainer:
    """Generates structured, audited explanations directly from shared workflow context."""

    @staticmethod
    def explain(context: WorkflowContext) -> WorkflowContext:
        """Derive explanation from the executed agents and triggered rules."""
        if not context.final_recommendation:
            context.errors.append("Final recommendation missing for Explainer.")
            return context

        rule_citations: List[Dict[str, str]] = []
        for r_id in context.final_recommendation.triggered_rules:
            meta = RULE_METADATA.get(r_id)
            if meta:
                rule_citations.append({
                    "rule_id": r_id,
                    "rule_name": f"Rule {meta['rule_number']}: {meta['name']}",
                    "description": meta["description"],
                    "target_decision": meta["target_decision"],
                    "confidence": f"{meta['base_confidence']}%",
                })
            else:
                rule_citations.append({
                    "rule_id": r_id,
                    "rule_name": r_id,
                    "description": "Deterministic rule triggered by field condition.",
                    "target_decision": "CUSTOM",
                    "confidence": "N/A",
                })

        agent_conclusions: List[Dict[str, str]] = []
        for out in context.agent_outputs:
            agent_conclusions.append({
                "agent": out.agent_name,
                "responsibility": out.responsibility,
                "status": out.status,
                "conclusion": out.output_summary,
            })

        limitations: List[str] = []
        if context.final_recommendation.unmapped_source_fields:
            limitations.append(
                f"Unmapped source fields: {', '.join(context.final_recommendation.unmapped_source_fields)} "
                "exist in the source schema but have no corresponding target destination."
            )
        if context.final_recommendation.review_items:
            for item in context.final_recommendation.review_items:
                limitations.append(f"Review required: {item}")
        if not context.sample_rows:
            limitations.append("No sample data rows provided; type compatibility was evaluated via schema types only.")

        summary = (
            f"Migration plan evaluated {len(context.destination_schema.fields)} destination fields across "
            f"{len(context.agent_outputs)} specialized stages. "
            f"Resulted in overall status '{context.final_recommendation.overall_status}' "
            f"with {len(rule_citations)} distinct deterministic rule categories applied."
        )
        if context.selected_route:
            summary += (
                f" LangGraph conditional route: '{context.selected_route}' "
                f"({context.routing_status})."
            )

        llm_exec_summary = None
        transformation_rationales = None
        risk_assessment = None
        suggested_review_actions = None
        llm_used = False
        fallback_used = False

        if context.llm_enhancement:
            llm_exec_summary = context.llm_enhancement.executive_summary
            transformation_rationales = context.llm_enhancement.transformation_rationales
            risk_assessment = context.llm_enhancement.risk_assessment
            suggested_review_actions = context.llm_enhancement.suggested_review_actions

        if context.llm_telemetry:
            llm_used = context.llm_telemetry.llm_used
            fallback_used = context.llm_telemetry.fallback_used

        explanation = Explanation(
            summary=summary,
            rule_citations=rule_citations,
            agent_conclusions=agent_conclusions,
            limitations_or_warnings=limitations,
            llm_executive_summary=llm_exec_summary,
            transformation_rationales=transformation_rationales,
            risk_assessment=risk_assessment,
            suggested_review_actions=suggested_review_actions,
            llm_used=llm_used,
            fallback_used=fallback_used,
        )

        context.explanation = explanation
        return context

