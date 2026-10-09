"""
LangGraph Migration Workflow Orchestrator.
Evolved from Phase 1 sequential orchestrator to LangGraph Linear Orchestration (Phase 2.1).
Follows Product Bible §14 & 01_LangGraph_Evolution_Guide.md §1, §4, §5.
"""

from typing import Optional
from app.models.schemas import MigrationRequest, WorkflowContext
from app.workflow.state import WorkflowState, state_to_context
from app.workflow.graph import workflow_graph, build_workflow_graph


class MigrationOrchestrator:
    """
    Orchestrates the migration pipeline using a compiled LangGraph Linear StateGraph.
    Preserves exact deterministic business rules, agent responsibilities, and API contract.
    """

    def __init__(self, graph=None):
        self.graph = graph or workflow_graph

    def run(self, request: MigrationRequest) -> WorkflowContext:
        """
        Run complete end-to-end migration pipeline using LangGraph.
        
        Maps:
        MigrationRequest -> Initial WorkflowState -> LangGraph Execution -> WorkflowContext
        """
        initial_state: WorkflowState = {
            "source_schema": request.source_schema,
            "destination_schema": request.destination_schema,
            "sample_rows": request.sample_rows,
            "relationship_metadata": request.relationship_metadata,
            "known_mapping_hints": request.known_mapping_hints or {},
            "agent_outputs": [],
            "errors": [],
            "node_trace": [],
        }

        # Execute through LangGraph Linear StateGraph
        final_state = self.graph.invoke(initial_state)

        # Convert back to WorkflowContext to preserve domain contract
        context = state_to_context(final_state)
        return context

    def get_graph(self):
        """Retrieve compiled LangGraph instance."""
        return self.graph
