"""
Context Builder for AA008 CRM Data Migration.
Prepares the Run-Scoped Shared Workflow Context per Product Bible §11 and Feeder Guide 02 §2.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.models.schemas import (
    MigrationRequest,
    WorkflowContext,
    SchemaMetadata,
    RelationshipMetadata,
    AgentExecutionOutput,
)


class ContextBuilder:
    """Builds and initializes the run-scoped shared workflow context."""

    @staticmethod
    def build(request: MigrationRequest) -> WorkflowContext:
        """
        Validates business input, generates workflow ID, and constructs
        the initial shared workflow context.
        """
        # Generate unique workflow ID
        workflow_id = f"wf_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        errors: List[str] = []

        # Validate basic schema presence
        if not request.source_schema.table_name:
            errors.append("Source schema table name is missing.")
        if not request.source_schema.fields:
            errors.append("Source schema contains no fields.")
        if not request.destination_schema.table_name:
            errors.append("Destination schema table name is missing.")
        if not request.destination_schema.fields:
            errors.append("Destination schema contains no fields.")

        # Combine and deduplicate relationships from schemas and top-level request
        combined_relationships: List[RelationshipMetadata] = []
        seen_rel = set()
        all_rels = (
            (request.relationship_metadata or [])
            + (request.source_schema.relationships or [])
            + (request.destination_schema.relationships or [])
        )
        for r in all_rels:
            rel_key = (r.source_table, r.source_field, r.target_table, r.target_field)
            if rel_key not in seen_rel:
                seen_rel.add(rel_key)
                combined_relationships.append(r)

        context = WorkflowContext(
            workflow_id=workflow_id,
            source_schema=request.source_schema,
            destination_schema=request.destination_schema,
            sample_rows=request.sample_rows,
            relationship_metadata=combined_relationships,
            known_mapping_hints=request.known_mapping_hints or {},
            schema_profile=None,
            mapping_candidates=None,
            transformation_plan=None,
            validation_results=None,
            agent_outputs=[],
            final_recommendation=None,
            explanation=None,
            audit_reference=None,
            errors=errors,
        )

        return context
