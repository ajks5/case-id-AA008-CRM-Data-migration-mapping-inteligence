"""
Schema Analyzer Agent.
Product Bible §8:
- Responsibility: Profiles tables, columns, types, keys, and relationships.
- Main Input: source_schema + destination_schema
- Main Output: schema_profile
"""

from typing import List, Dict, Any
from app.models.schemas import (
    WorkflowContext,
    SchemaProfile,
    FieldProfile,
    AgentExecutionOutput,
)
from app.data.aliases import normalize_identifier
from app.data.transformation_rules import normalize_type


class SchemaAnalyzerAgent:
    """Specialized domain agent for profiling source and destination schemas."""

    AGENT_NAME = "Schema Analyzer Agent"
    RESPONSIBILITY = "Profiles tables, columns, types, keys, and relationships."

    def execute(self, context: WorkflowContext) -> WorkflowContext:
        """Analyze schemas in context and store SchemaProfile."""
        source_fields: List[FieldProfile] = []
        dest_fields: List[FieldProfile] = []
        source_pks: List[str] = []
        dest_pks: List[str] = []

        # Extract sample distributions from sample_rows if available
        sample_value_map: Dict[str, List[Any]] = {}
        if context.sample_rows:
            for row in context.sample_rows:
                for col, val in row.items():
                    if col not in sample_value_map:
                        sample_value_map[col] = []
                    if len(sample_value_map[col]) < 3 and val is not None:
                        sample_value_map[col].append(val)

        # Profile Source Fields
        for f in context.source_schema.fields:
            name = str(f.get("name", ""))
            data_type = str(f.get("data_type", "string"))
            is_pk = bool(f.get("is_primary_key", False))
            is_nullable = bool(f.get("is_nullable", True))
            
            if is_pk:
                source_pks.append(name)

            source_fields.append(
                FieldProfile(
                    name=name,
                    normalized_name=normalize_identifier(name),
                    data_type=data_type,
                    normalized_type=normalize_type(data_type),
                    is_required=not is_nullable,
                    is_nullable=is_nullable,
                    is_primary_key=is_pk,
                    sample_values=sample_value_map.get(name, []),
                )
            )

        # Profile Destination Fields
        for f in context.destination_schema.fields:
            name = str(f.get("name", ""))
            data_type = str(f.get("data_type", "string"))
            is_pk = bool(f.get("is_primary_key", False))
            is_req = bool(f.get("is_required", False))
            is_nullable = bool(f.get("is_nullable", not is_req))

            if is_pk:
                dest_pks.append(name)

            dest_fields.append(
                FieldProfile(
                    name=name,
                    normalized_name=normalize_identifier(name),
                    data_type=data_type,
                    normalized_type=normalize_type(data_type),
                    is_required=is_req,
                    is_nullable=is_nullable,
                    is_primary_key=is_pk,
                    sample_values=[],
                )
            )

        profile = SchemaProfile(
            source_table=context.source_schema.table_name,
            destination_table=context.destination_schema.table_name,
            source_fields=source_fields,
            destination_fields=dest_fields,
            source_primary_keys=source_pks,
            destination_primary_keys=dest_pks,
            relationships=context.relationship_metadata,
            field_count_source=len(source_fields),
            field_count_destination=len(dest_fields),
        )

        context.schema_profile = profile

        # Record execution telemetry
        context.agent_outputs.append(
            AgentExecutionOutput(
                agent_name=self.AGENT_NAME,
                responsibility=self.RESPONSIBILITY,
                status="SUCCESS",
                input_summary=(
                    f"Source: {context.source_schema.table_name} ({len(source_fields)} cols), "
                    f"Dest: {context.destination_schema.table_name} ({len(dest_fields)} cols)"
                ),
                output_summary=(
                    f"Profiled {len(source_fields)} source fields and {len(dest_fields)} target fields. "
                    f"Detected {len(context.relationship_metadata)} relationships."
                ),
                details={
                    "source_pks": source_pks,
                    "dest_pks": dest_pks,
                    "relationship_count": len(context.relationship_metadata),
                },
            )
        )

        return context
