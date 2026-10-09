"""
Controlled Prompt Contracts for Migration Explainer.
Follows Feeder Guide §6:
- Clear role: Migration rationale & transformation explanation
- Allowed input: Structured deterministic outputs only
- Strict bounds: Do NOT invent fields or change decisions
- Expected structured output format: JSON
"""

import json
from typing import Dict, Any, List


SYSTEM_PROMPT = """You are an enterprise CRM Data Migration Explainer.
Your sole responsibility is to generate clear, executive-grade explanations and transformation rationales
grounded strictly in the deterministic decisions and rule outputs already produced by domain agents.

MANDATORY BOUNDARIES:
1. NEVER alter, override, or contradict any deterministic decision, routing status, or field mapping.
2. NEVER invent non-existent database fields, foreign keys, or tables that were not supplied in the input.
3. In transformation_rationales, ONLY include keys corresponding to destination fields that actually require transformation in the input.
4. If no transformations are planned, transformation_rationales MUST be an empty JSON object {}.
5. In suggested_review_actions, provide concrete, practical triage steps for flagged review items or blocking issues. If there are no review items or blocking issues, return an empty list [].
6. Respond with pure JSON conforming strictly to the requested schema. Do NOT include markdown code blocks (e.g. ```json) or conversational text.
"""


def build_user_prompt(
    source_table: str,
    dest_table: str,
    overall_status: str,
    selected_route: str,
    routing_status: str,
    summary_counts: Dict[str, int],
    triggered_rules: List[str],
    transformations: List[Dict[str, Any]],
    review_items: List[str],
    blocking_issues: List[str],
    unmapped_fields: List[str],
) -> str:
    """Constructs the bounded input prompt for the LLM."""
    payload = {
        "source_table": source_table,
        "destination_table": dest_table,
        "overall_status": overall_status,
        "selected_route": selected_route,
        "routing_status": routing_status,
        "summary_counts": summary_counts,
        "triggered_rules": triggered_rules,
        "transformations": transformations,
        "review_items": review_items,
        "blocking_issues": blocking_issues,
        "unmapped_source_fields": unmapped_fields,
    }

    schema_example = {
        "executive_summary": "2-3 sentence executive explanation of the migration plan, routing decision, and field coverage.",
        "transformation_rationales": {
            "destination_field_name": "Technical explanation of why the transformation or data type cast is required."
        },
        "risk_assessment": "Assessment of migration risk (LOW, MODERATE, or HIGH) based strictly on review items and constraints.",
        "suggested_review_actions": [
            "Actionable step 1 for migration analysts to triage review items."
        ]
    }

    return (
        f"DETERMINISTIC MIGRATION EVIDENCE:\n"
        f"{json.dumps(payload, indent=2)}\n\n"
        f"INSTRUCTIONS:\n"
        f"Synthesize the evidence above into the following JSON schema:\n"
        f"{json.dumps(schema_example, indent=2)}\n\n"
        f"Return ONLY valid JSON."
    )
