"""
Output Validator for Controlled LLM Responses.
Follows Feeder Guide §7:
- Validates expected fields and data types
- Prevents hallucinated target fields in transformation rationales
- Bounded output checks
- Gracefully signals validation rejection for fallback activation
"""

import json
import re
from typing import Optional, Set, Tuple
from app.models.schemas import LLMEnhancementOutput


class LLMOutputValidator:
    """Validates and bounds LLM output strictly to the domain contract."""

    @staticmethod
    def clean_json_string(raw: str) -> str:
        """Strip markdown code fence blocks if returned by provider."""
        text = raw.strip()
        # Remove ```json ... ``` or ``` ... ```
        pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
        return text

    @classmethod
    def validate_and_bound(
        cls,
        raw_content: str,
        valid_dest_fields: Set[str],
    ) -> Tuple[bool, Optional[LLMEnhancementOutput], Optional[str]]:
        """
        Validates LLM JSON output against schema and domain bounds.
        Returns: (success, parsed_output, error_message)
        """
        if not raw_content or not raw_content.strip():
            return False, None, "LLM returned empty response."

        cleaned = cls.clean_json_string(raw_content)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as err:
            return False, None, f"Malformed JSON: {str(err)}"

        if not isinstance(data, dict):
            return False, None, "LLM response is not a JSON object dictionary."

        # Validate through Pydantic
        try:
            output = LLMEnhancementOutput.model_validate(data)
        except Exception as pydantic_err:
            return False, None, f"Schema validation error: {str(pydantic_err)}"

        # Domain bounds check:
        # 1. Executive summary bounds
        if not output.executive_summary.strip():
            return False, None, "Executive summary must not be empty."
        if len(output.executive_summary) > 2500:
            output.executive_summary = output.executive_summary[:2497] + "..."

        # 2. Risk assessment bounds
        if not output.risk_assessment.strip():
            return False, None, "Risk assessment must not be empty."

        # 3. Guard against hallucinated destination fields in transformation rationales
        bounded_rationales = {}
        for dest_field, rationale in output.transformation_rationales.items():
            if dest_field in valid_dest_fields:
                bounded_rationales[dest_field] = str(rationale).strip()
            # Non-existent/hallucinated fields are pruned silently to maintain domain fidelity

        output.transformation_rationales = bounded_rationales

        return True, output, None
