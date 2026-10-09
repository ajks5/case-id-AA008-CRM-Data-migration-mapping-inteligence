"""
In-memory Audit Store for AA008 CRM Data Migration.
Follows Product Bible §16:
Records workflow_id, request reference, execution timestamp,
agent execution sequence, major agent outputs, triggered decision rules,
final recommendation, and errors.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.models.schemas import WorkflowContext, AuditRecord


class AuditStore:
    """Thread-safe, in-memory repository for migration workflow audit trails."""

    def __init__(self):
        self._records: Dict[str, AuditRecord] = {}

    def record_workflow(self, context: WorkflowContext) -> AuditRecord:
        """Create and store an audit record from the completed workflow context."""
        agent_names = [a.agent_name for a in context.agent_outputs]
        rec_status = (
            context.final_recommendation.overall_status
            if context.final_recommendation
            else "UNKNOWN"
        )
        triggered_rules = (
            context.final_recommendation.triggered_rules
            if context.final_recommendation
            else []
        )

        major_outputs = {
            "summary_counts": (
                context.final_recommendation.summary_counts
                if context.final_recommendation
                else {}
            ),
            "review_items_count": (
                len(context.final_recommendation.review_items)
                if context.final_recommendation
                else 0
            ),
            "validation_passed": (
                context.validation_results.all_valid
                if context.validation_results
                else False
            ),
            "fields_analyzed": len(context.destination_schema.fields),
            "selected_route": context.selected_route,
            "routing_status": context.routing_status,
            "routing_reason": context.routing_reason,
            "llm_telemetry": (
                context.llm_telemetry.model_dump()
                if context.llm_telemetry
                else None
            ),
        }

        record = AuditRecord(
            workflow_id=context.workflow_id,
            request_reference=f"Migration {context.source_schema.table_name} -> {context.destination_schema.table_name}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_execution_order=agent_names,
            major_outputs=major_outputs,
            triggered_rules=triggered_rules,
            final_recommendation_status=rec_status,
            errors=context.errors,
            node_trace=list(context.node_trace),
            selected_route=context.selected_route,
            routing_status=context.routing_status,
            llm_telemetry=context.llm_telemetry,
        )


        self._records[context.workflow_id] = record
        context.audit_reference = context.workflow_id
        return record

    def get(self, workflow_id: str) -> Optional[AuditRecord]:
        """Retrieve audit record by workflow ID."""
        return self._records.get(workflow_id)

    def list_all(self) -> List[AuditRecord]:
        """List all audit records in descending order of timestamp."""
        return sorted(self._records.values(), key=lambda r: r.timestamp, reverse=True)

    def clear(self) -> None:
        """Clear audit records (useful for test isolation)."""
        self._records.clear()


# Global singleton instance for in-memory session
audit_store = AuditStore()
