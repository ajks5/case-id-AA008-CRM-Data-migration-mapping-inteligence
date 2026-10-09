"""
Deterministic rules and scoring definitions for CRM Data Migration.
Directly implements Product Bible §12:
1. Exact normalized-name + compatible type -> DIRECT_MAP (Confidence 100)
2. Known alias + compatible type -> DIRECT_MAP with evidence (Confidence 90)
3. Type-convertible fields -> TRANSFORM (Confidence 70)
4. Required target field without valid source/default -> REVIEW (Confidence 0)
5. Never silently drop relationship or required-field conflicts -> REVIEW (Confidence 0)
"""

from typing import Dict, Any

RULE_1_ID = "RULE_1_EXACT_NAME_COMPATIBLE_TYPE"
RULE_2_ID = "RULE_2_KNOWN_ALIAS_COMPATIBLE_TYPE"
RULE_3_ID = "RULE_3_TYPE_CONVERTIBLE"
RULE_4_ID = "RULE_4_REQUIRED_TARGET_MISSING_SOURCE"
RULE_5_ID = "RULE_5_RELATIONSHIP_OR_KEY_CONFLICT"

RULE_METADATA: Dict[str, Dict[str, Any]] = {
    RULE_1_ID: {
        "rule_number": 1,
        "name": "Exact Name & Compatible Type",
        "description": "Exact normalized column name and compatible data type produces a direct mapping.",
        "target_decision": "DIRECT_MAP",
        "base_confidence": 100.0,
    },
    RULE_2_ID: {
        "rule_number": 2,
        "name": "Known CRM Alias & Compatible Type",
        "description": "Column matched via deterministic CRM alias dictionary with compatible type.",
        "target_decision": "DIRECT_MAP",
        "base_confidence": 90.0,
    },
    RULE_3_ID: {
        "rule_number": 3,
        "name": "Type-Convertible Transformation",
        "description": "Field names match or alias match, but data types require an explicit cast or parser transform.",
        "target_decision": "TRANSFORM",
        "base_confidence": 70.0,
    },
    RULE_4_ID: {
        "rule_number": 4,
        "name": "Required Target Field Missing Source/Default",
        "description": "Target field is mandatory (required=True) but lacks a candidate source field or default value.",
        "target_decision": "REVIEW",
        "base_confidence": 0.0,
    },
    RULE_5_ID: {
        "rule_number": 5,
        "name": "Relationship / Foreign Key Conflict",
        "description": "Target field is part of a required relational constraint or foreign key that cannot be resolved safely.",
        "target_decision": "REVIEW",
        "base_confidence": 0.0,
    },
}
