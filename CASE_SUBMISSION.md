# Case Submission — AA008 (Phase 2.3: Add a Controlled LLM Enhancement)

### Case Submission Information
- **Case ID:** AA008
- **Case Study Name:** CRM Data Migration Mapping Intelligence
- **Repository:** https://github.com/ajks5/case-id-AA08-CRM-Data-migration-mapping-inteligence
- **Cloud Platform:** Render (Backend API) + Vercel (Frontend UI)
- **Application URL:** https://frontend-ten-ebon-33.vercel.app
- **Backend / Health URL:** https://case-id-aa008-crm-data-migration-mapping.onrender.com/health
- **Phase:** 2.3 — Add a Controlled LLM Enhancement
- **Status:** Complete, Fallback-Safe & Fully Verified

---

### Executive Summary: What Changed from Phase 2.2
1. **Product Bible §21 Controlled LLM Enhancement:** Added ONE focused, bounded LLM capability strictly permitted by Product Bible §21 (`Future Controlled LLM Opportunity`): **Semantic Transformation & Migration Rationale Explainer** (`MigrationLLMService`).
2. **Deterministic Authority Preserved Unchanged (§12):** All 5 domain agents (Schema Analyzer, Field Mapper, Transformer, Validator, Decision Agent), all 5 deterministic business rules (Rules 1–5), and LangGraph conditional routing (`route_after_decision`) remain 100% authoritative. The LLM never overrides mapping decisions, never alters statuses, and never invents database fields.
3. **Graph Topology Evolution:** Added Node 7 (`llm_enhancement`) into the compiled LangGraph `StateGraph(WorkflowState)`. All 3 conditional branches (`direct_accept`, `transform_verify`, `human_review`) converge into `llm_enhancement`, which validates structured output, applies deterministic fallback if needed, and flows into `explainer` and `audit`.
4. **Dedicated Adapter / Service Boundary:** Encapsulated LLM operations in `app.llm` with clean separation:
   - `config.py`: Environment-driven configuration (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_TIMEOUT`, `LLM_ENABLED`, `GEMINI_API_KEY`, `OPENAI_API_KEY`).
   - `prompts.py`: Bounded system prompt & input prompt contract per Feeder Guide §6.
   - `validator.py`: Pydantic schema validation, text bounding, and destination-field hallucination pruning (`LLMOutputValidator`).
   - `fallback.py`: Guaranteed deterministic template explanation provider (`DeterministicFallbackProvider`).
   - `service.py`: Provider invocation (`gemini` via header-secured REST, `openai`, `mock`) with strict error sanitization.
5. **Double-Layer Secret Guardrail:** 
   - Never exposes API keys in source control (`.env*` gitignored, placeholder `.env.example`).
   - Gemini API uses `x-goog-api-key` request header (never exposed in query strings).
   - Regex-based error sanitization strips keys, tokens, and credentials from all exception strings before recording in trace or audit.
6. **Full Traceability & Audit Logging:** Non-secret telemetry (`llm_telemetry`: provider, model, status, latency_ms, fallback_used, validation_passed) is recorded in `WorkflowState`, step 8 of `node_trace`, and persisted in `AuditRecord`.
7. **Interactive UI Enhancement:** Added `LLMEnhancementPanel.tsx` in frontend, updating the pipeline visualizer to 10 stages and rendering executive summaries, transformation rationales, risk assessments, and triage steps with fallback alerts.

---

### LangGraph Architecture & Flow

```text
START
  ↓
1. context_validation (Context Builder & Input Validator)
  ↓
2. schema_analyzer    (Agent 1: Schema Profiling & Normalization)
  ↓
3. field_mapper       (Agent 2: Candidate Matching via Rules 1 & 2)
  ↓
4. transformer        (Agent 3: Transformation Planning via Rule 3)
  ↓
5. validator          (Agent 4: Target Coverage & Relational Integrity via Rules 4 & 5)
  ↓
6. decision           (Agent 5: Migration Decision Synthesis)
  ↓
[conditional_router: route_after_decision]
  ├── "route_direct_accept"   ──> direct_accept   (Branch A: HIGH_CONFIDENCE)        ──┐
  ├── "route_transform_verify" ──> transform_verify (Branch B: TRANSFORM_REQUIRED)    ──┤
  └── "route_human_review"    ──> human_review    (Branch C: EXCEPTION / REVIEW)     ──┘
                                                                                         ↓
                                                                                     7. llm_enhancement (Product Bible §21 Adapter)
                                                                                         ↓
                                                                                     8. explainer       (Rule Citations & Narrative)
                                                                                         ↓
                                                                                     9. audit           (Immutable Audit Store)
                                                                                         ↓
                                                                                        END
```

---

### Exact Controlled LLM Role & Boundaries (Product Bible §21)

| Aspect | Specification |
|---|---|
| **Role Name** | Semantic Transformation & Migration Rationale Explainer |
| **Product Bible Permission** | §21: *"Optional semantic assistance for ambiguous field-name matching or transformation explanation. Deterministic type/constraint validation remains authoritative."* |
| **Where it Sits in Graph** | Step 8 in `node_trace` (`llm_enhancement`), immediately after conditional branch nodes (`direct_accept`, `transform_verify`, `human_review`) and before `explainer` and `audit`. |
| **Required Input Fields** | `source_table`, `destination_table`, `overall_status`, `selected_route`, `routing_status`, `summary_counts`, `triggered_rules`, `transformations`, `review_items`, `blocking_issues`, `unmapped_fields`. |
| **Expected Structured Output** | Strongly typed JSON conforming to `LLMEnhancementOutput`: <br>• `executive_summary` (concise plain-English migration summary)<br>• `transformation_rationales` (dict of `destination_field` -> technical explanation for why conversion is needed)<br>• `risk_assessment` (factual risk level: LOW / MODERATE / HIGH)<br>• `suggested_review_actions` (actionable triage steps for migration analysts). |
| **Deterministic Business Authority** | 100% UNCHANGED. Rules 1–5, field mappings, decisions, type casts, and route selections remain entirely deterministic. |
| **Forbidden Behaviors** | Cannot override mapping decisions, cannot change overall status, cannot hallucinate non-existent fields (pruned by validator), cannot claim facts not present in state. |
| **Fallback Behavior** | If LLM times out, provider fails (429, 500, network error), API key is missing, or output is malformed, `DeterministicFallbackProvider` engages instantly, populating template rationales, marking `status="FALLBACK"`, `fallback_used=True`. |
| **Traceability / Audit** | Non-secret telemetry logged in `WorkflowContext.llm_telemetry`, `node_trace`, and `AuditRecord.llm_telemetry` (`provider`, `model`, `status`, `fallback_used`, `validation_passed`, `latency_ms`, sanitized `error_message`). |

---

### Evaluation Results (5 Required Scenarios)

| # | Evaluation Scenario | Deterministic Outcome | Route & Branch | LLM Role & Behavior | LLM Status | Fallback Used? | Result Safe? |
|---|---|---|---|---|---|---|---|
| **1** | **Normal Valid LLM Response** (`simple_schema`) | Status: `READY`<br>6 `DIRECT_MAP`<br>1 `DEFAULT`<br>0 `REVIEW` | `route_direct_accept`<br>→ `direct_accept` | Explains high compatibility, confirms 100% coverage, evaluates `LOW RISK`, 0 transform rationales. | `SUCCESS` | No (`False`) | **Yes** |
| **2** | **Ambiguous / Transform Input** (`naming_mismatch`) | Status: `READY`<br>6 `DIRECT_MAP`<br>1 `TRANSFORM`<br>0 `REVIEW` | `route_transform_verify`<br>→ `transform_verify` | Explains technical necessity of ISO-8601 string-to-datetime parsing for `created_at` (from `signup_date`), evaluates `MODERATE RISK`. | `SUCCESS` | No (`False`) | **Yes** |
| **3** | **Domain Edge Case / Exception** (`relationship_mismatch`) | Status: `NEEDS_REVIEW`<br>4 `DIRECT_MAP`<br>1 `REVIEW`<br>2 blocking issues | `route_human_review`<br>→ `human_review` | Evaluates `HIGH RISK`, outputs concrete step-by-step triage actions for analyst to remediate missing `account_id` foreign key. | `SUCCESS` | No (`False`) | **Yes** |
| **4** | **LLM Unavailable / Timeout / Rate Limit (429)** | Status: Preserved (`READY` or `NEEDS_REVIEW`) | Route: Preserved | LLM call fails or times out. `DeterministicFallbackProvider` generates template explanation. Telemetry flags `status="FALLBACK"`. | `FALLBACK` | **Yes (`True`)** | **Yes** |
| **5** | **Invalid / Malformed Output** (Broken JSON / Schema) | Status: Preserved | Route: Preserved | Provider outputs invalid JSON or hallucinated fields. `LLMOutputValidator` rejects payload or prunes fake keys, triggering deterministic fallback. | `FALLBACK` | **Yes (`True`)** | **Yes** |

---

### Test Suite & Verification Results
- **Full Pytest Suite (`backend/tests/`):** 28 of 28 tests passing:
  - `tests/test_agents.py` (5 tests): Deterministic agents profiling, mapping, transform, validation, decision.
  - `tests/test_rules.py` (6 tests): Rules 1–5 deterministic verification and scoring.
  - `tests/test_scenarios.py` (5 tests): Canonical Product Bible scenarios.
  - `tests/test_langgraph.py` (6 tests): Graph compilation, 12-node topology, conditional branching, 10-step trace.
  - `tests/test_llm_enhancement.py` (6 tests): All 5 evaluation scenarios (normal, transform rationales, review actions, timeout fallback, malformed output fallback, hallucination pruning).
- **End-to-End Verification (`backend/validate_e2e.py`):** 100% pass across health check, LLM status endpoint, all 3 migration scenarios, LangGraph node traces, and audit persistence.
- **Frontend UI & Build:** React 19 + TypeScript + Vite compiles in 575ms with zero errors (`tsc -b && vite build`). Interactive UI visualizes LLM badges, executive summary, transformation rationales, risk assessment, and fallback status.

---

### Run & Deployment Steps

#### 1. Backend Setup & Run
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configure environment (copy template)
copy ..\.env.example .env

# Run test suite (hermetic & reproducible)
python -m pytest

# Run end-to-end verification
python validate_e2e.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup & Run
```bash
cd frontend
npm install
npm run build
npm run dev
```

#### 3. Verification Endpoints
- API Health: `GET http://localhost:8000/health`
- LLM Status (non-secret): `GET http://localhost:8000/api/llm/status`
- Pre-seeded Scenarios: `GET http://localhost:8000/api/scenarios`
- Run Migration: `POST http://localhost:8000/api/migrate`
- Audit Trail: `GET http://localhost:8000/api/audit`
- Frontend UI: `http://localhost:5173`
