"""
Transformation rule library and type compatibility definitions for CRM Data Migration.
Implements Rule 3 (Type-convertible fields -> TRANSFORM) and canonical type normalization.
"""

from typing import Tuple, Optional, Any
from datetime import datetime

# Canonical types: string, integer, float, boolean, datetime, date, json
TYPE_CANONICAL_MAP = {
    "str": "string",
    "string": "string",
    "text": "string",
    "varchar": "string",
    "char": "string",
    "nvarchar": "string",
    "int": "integer",
    "integer": "integer",
    "bigint": "integer",
    "smallint": "integer",
    "tinyint": "integer",
    "float": "float",
    "double": "float",
    "decimal": "float",
    "numeric": "float",
    "real": "float",
    "bool": "boolean",
    "boolean": "boolean",
    "datetime": "datetime",
    "timestamp": "datetime",
    "timestamptz": "datetime",
    "date": "date",
    "json": "json",
    "jsonb": "json",
}


def normalize_type(type_name: str) -> str:
    """Normalize raw SQL / CRM type to canonical representation."""
    cleaned = type_name.lower().split("(")[0].strip()
    return TYPE_CANONICAL_MAP.get(cleaned, cleaned)


def are_types_directly_compatible(src_type: str, dest_type: str) -> bool:
    """Check if two data types are directly compatible without transformation."""
    norm_src = normalize_type(src_type)
    norm_dest = normalize_type(dest_type)
    return norm_src == norm_dest


def get_transformation_rule(src_type: str, dest_type: str) -> Optional[Tuple[str, str]]:
    """
    Check if a type conversion is supported.
    Returns (rule_name, explanation) or None if incompatible.
    """
    norm_src = normalize_type(src_type)
    norm_dest = normalize_type(dest_type)

    if norm_src == norm_dest:
        return None

    # (src, dest) conversions
    conversions = {
        ("integer", "string"): (
            "CAST_INT_TO_STRING",
            "Cast integer numeric values to string format"
        ),
        ("float", "string"): (
            "CAST_FLOAT_TO_STRING",
            "Cast float decimal values to standard string format"
        ),
        ("string", "integer"): (
            "PARSE_STRING_TO_INT",
            "Parse and validate numeric string into integer"
        ),
        ("string", "float"): (
            "PARSE_STRING_TO_FLOAT",
            "Parse numeric string into floating-point value"
        ),
        ("string", "datetime"): (
            "PARSE_STRING_TO_DATETIME",
            "Parse ISO / standard date string into ISO-8601 UTC datetime"
        ),
        ("string", "date"): (
            "PARSE_STRING_TO_DATE",
            "Parse date string into standard YYYY-MM-DD date"
        ),
        ("date", "datetime"): (
            "DATE_TO_DATETIME",
            "Promote date to midnight ISO-8601 UTC timestamp"
        ),
        ("datetime", "date"): (
            "DATETIME_TO_DATE",
            "Extract date component (YYYY-MM-DD) from timestamp"
        ),
        ("integer", "boolean"): (
            "INT_TO_BOOLEAN",
            "Convert binary int (0/1) to boolean (false/true)"
        ),
        ("string", "boolean"): (
            "PARSE_STRING_TO_BOOLEAN",
            "Convert boolean string ('true'/'false'/'yes'/'no') to boolean"
        ),
    }

    return conversions.get((norm_src, norm_dest))


def apply_sample_transformation(rule_name: str, sample_value: Any) -> Any:
    """Simulate sample transformation for preview in UI."""
    if sample_value is None:
        return None
    try:
        val_str = str(sample_value).strip()
        if rule_name == "CAST_INT_TO_STRING" or rule_name == "CAST_FLOAT_TO_STRING":
            return str(sample_value)
        elif rule_name == "PARSE_STRING_TO_INT":
            return int(float(val_str))
        elif rule_name == "PARSE_STRING_TO_FLOAT":
            return float(val_str)
        elif rule_name in ("PARSE_STRING_TO_DATETIME", "DATE_TO_DATETIME"):
            # Simple simulation for sample preview
            if "T" in val_str:
                return val_str
            return f"{val_str}T00:00:00Z"
        elif rule_name in ("PARSE_STRING_TO_DATE", "DATETIME_TO_DATE"):
            return val_str.split("T")[0].split(" ")[0]
        elif rule_name == "INT_TO_BOOLEAN":
            return bool(int(sample_value))
        elif rule_name == "PARSE_STRING_TO_BOOLEAN":
            return val_str.lower() in ("true", "1", "yes", "t", "y")
    except Exception:
        return f"[Transform error for {sample_value}]"
    return sample_value
