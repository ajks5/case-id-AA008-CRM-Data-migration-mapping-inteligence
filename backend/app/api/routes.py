"""
FastAPI Routes for AA008 CRM Data Migration Mapping Intelligence.
Endpoints:
- GET /health
- GET /api/scenarios
- POST /api/migrate
- GET /api/audit
- GET /api/audit/{workflow_id}
- GET /api/rules
- GET /api/aliases
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.schemas import MigrationRequest, WorkflowContext, AuditRecord
from app.workflow.orchestrator import MigrationOrchestrator
from app.audit.audit_store import audit_store
from app.data.sample_scenarios import SAMPLE_SCENARIOS
from app.data.aliases import CRM_FIELD_ALIASES
from app.rules.mapping_rules import RULE_METADATA

router = APIRouter()
orchestrator = MigrationOrchestrator()


@router.get("/health")
def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "AA008 CRM Data Migration Mapping Intelligence",
        "version": "1.0.0",
        "case_id": "AA008",
    }


@router.get("/api/scenarios")
def get_sample_scenarios():
    """Retrieve pre-seeded Product Bible scenarios."""
    return list(SAMPLE_SCENARIOS.values())


@router.get("/api/scenarios/{scenario_id}")
def get_scenario_by_id(scenario_id: str):
    """Retrieve single scenario by ID."""
    if scenario_id not in SAMPLE_SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return SAMPLE_SCENARIOS[scenario_id]


@router.post("/api/migrate", response_model=WorkflowContext)
def run_migration_pipeline(request: MigrationRequest):
    """
    Executes the 5-agent migration intelligence workflow sequentially.
    Returns complete run-scoped shared workflow context.
    """
    try:
        context = orchestrator.run(request)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration execution failed: {str(e)}")


@router.get("/api/audit", response_model=List[AuditRecord])
def get_all_audit_records():
    """Retrieve all recorded audit events."""
    return audit_store.list_all()


@router.get("/api/audit/{workflow_id}", response_model=AuditRecord)
def get_audit_record(workflow_id: str):
    """Retrieve audit record by workflow ID."""
    record = audit_store.get(workflow_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit record '{workflow_id}' not found")
    return record


@router.get("/api/rules")
def get_rules_metadata():
    """Retrieve deterministic rules definition and confidence scores."""
    return RULE_METADATA


@router.get("/api/aliases")
def get_crm_aliases():
    """Retrieve CRM synonym and alias dictionary."""
    return CRM_FIELD_ALIASES


@router.get("/api/llm/status")
def get_llm_status():
    """
    Retrieve non-secret LLM configuration status for UI and observability.
    Guarantees no API keys or credentials are ever exposed.
    """
    from app.llm.config import LLMConfig
    cfg = LLMConfig.from_env()
    return {
        "provider": cfg.provider,
        "model": cfg.model,
        "enabled": cfg.enabled,
        "timeout": cfg.timeout,
        "has_api_key": bool(cfg.api_key),
        "status": "ready" if (cfg.enabled and (cfg.provider == "mock" or bool(cfg.api_key))) else "fallback_only",
    }

