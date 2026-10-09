"""
Main FastAPI Application Entrypoint.
AA008 CRM Data Migration Mapping Intelligence.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="AA008 CRM Data Migration Mapping Intelligence",
    description="RealRails Agentic AI Batch 2 — Deterministic 5-Agent CRM Schema Migration Engine",
    version="1.0.0",
)

# Configure CORS for local development and frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "case_id": "AA008",
        "name": "CRM Data Migration Mapping Intelligence",
        "description": "Standard RealRails deterministic 5-agent migration engine.",
        "endpoints": {
            "health": "/health",
            "scenarios": "/api/scenarios",
            "migrate": "POST /api/migrate",
            "audit": "/api/audit",
            "rules": "/api/rules",
            "aliases": "/api/aliases",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
