# AA008 — 2–3 Minute Demo Script & Presentation Flow

> **Case ID:** AA008 — CRM Data Migration Mapping Intelligence  
> **Target Audience:** Technical & Business Reviewers, Hiring Managers, Product Leads  
> **Environment:** Local Phase 3 UI (`http://localhost:5173`) running against Local FastAPI backend (`http://localhost:8000`) with mock or Gemini LLM provider.

---

## Timed Walkthrough (Total: ~2 Minutes 35 Seconds)

### Step 1: Business Problem (~15–20s)
- **Visual:** Open browser to the AA008 application dashboard header.
- **Narrative:**
  > *"When enterprises migrate CRM platforms—such as legacy customer databases to a modern CRM—schema fields rarely align 1:1. Migration teams struggle with inconsistent field names, type conversions like string-to-datetime, and foreign-key breakages. Manual spreadsheet mapping is slow and prone to errors. AA008 is an agentic decision-support engine that analyzes schemas and produces an explainable, auditable mapping blueprint before migration planning. Crucially, the application never writes to CRM systems or production databases."*

### Step 2: Business Input (~20s)
- **Visual:** Highlight the **Schema Input & Scenario Selector** panel. Click on `Scenario 1: Simple Schema`.
- **Narrative:**
  > *"The application takes structured source and destination schema definitions, including field types, nullability, keys, relationship constraints, and data samples. Analysts can choose from preloaded real-world scenarios or paste custom schema JSON directly into the editor."*

### Step 3: Implemented Business Workflow (~25–30s)
- **Visual:** Click **Run 5-Agent Migration Pipeline**. Scroll to the **LangGraph Orchestration Trace**.
- **Narrative:**
  > *"When we trigger the pipeline, LangGraph coordinates five specialized agents: Schema Analyzer Agent, Field Mapping Agent, Transformation Agent, Validation Agent, and Migration Decision Agent. All state is maintained in a run-scoped context. Deterministic rules evaluate name aliases and data types, and a deterministic conditional router determines the execution branch based on validation results, executing 10 nodes per run."*

### Step 4: Authoritative Recommendation (~20s)
- **Visual:** Scroll to the **Migration Readiness Banner** and **Field Mapping Matrix**.
- **Narrative:**
  > *"Here is the authoritative recommendation: the system assigns an overall status of 'READY' with an 'ACCEPTED_DIRECT' route. All 6 destination fields are directly mapped with 100% confidence under Rule 1, standard default values are applied, and zero manual reviews are required."*

### Step 5: Explainability & Audit Evidence (~20s)
- **Visual:** Click **Explainability & Audit** (or open the drawer titled **Explainability, Audit & Technical Details**). Show the 10-node step execution trace and rule citations.
- **Narrative:**
  > *"Notice the explainability: every recommendation links to triggered deterministic rules and agent outputs. The drawer logs the full 10-node LangGraph trace with timestamps and execution status. Analysts can also click 'Download mapping worksheet' to export a complete CSV worksheet named mapping-worksheet-<workflow_id>.csv for offline human review."*

### Step 6: Alternate / Conditional Route Demonstration (~25s)
- **Visual:** Close drawer. Select `Scenario 3: Relationship Mismatch` and click **Run 5-Agent Migration Pipeline**.
- **Narrative:**
  > *"Now let's demonstrate conditional routing under an exception. In this scenario, a flat web leads table lacks the mandatory foreign key 'account_id' referencing 'crm_accounts'. The router detects blocking constraint violations under Rules 4 and 5, halting automated approval and taking the 'route_human_review' branch. The status updates to 'NEEDS_REVIEW' with explicit blocking constraint evidence."*

### Step 7: Controlled LLM Contribution & Fallback (~20s)
- **Visual:** Point to the **Controlled LLM Advisory Panel** with risk rating and triage checklist.
- **Narrative:**
  > *"Notice how the LLM is bounded. It generates executive summaries, risk classifications, and plain-language triage checklists, but has zero authority to alter mappings or override decisions. If the LLM is disabled or fails, our deterministic fallback instantly serves rule-based wording without interrupting the workflow, ensuring predictable behavior."*

### Step 8: Business Value & Boundaries Close (~15s)
- **Visual:** Return to the top overview summary.
- **Narrative:**
  > *"To summarize: AA008 turns complex schema reconciliation into a fast, repeatable, and fully audited process. It provides analysts with high confidence while keeping human reviewers firmly in control. Because the application never writes to CRM systems or databases, migration planning is safe, transparent, and auditable."*

---

## Live Demo Reproduction Checklist

Before starting your live presentation or recording:

- [ ] **Backend running:** `uvicorn app.main:app --port 8000` with `$env:LLM_PROVIDER="mock"` and `$env:LLM_ENABLED="true"`.
- [ ] **Frontend running:** Vite running on `http://localhost:5173` pointing to `http://localhost:8000`.
- [ ] **Verify Scenario 1:** Select `simple_schema` → click **Run 5-Agent Migration Pipeline** → confirm `READY` (`ACCEPTED_DIRECT`), 6 direct maps.
- [ ] **Verify Scenario 2:** Select `naming_mismatch` → click **Run 5-Agent Migration Pipeline** → confirm `READY` (`TRANSFORM_STAGED`), 1 transform, Rules 2 & 3.
- [ ] **Verify Scenario 3:** Select `relationship_mismatch` → click **Run 5-Agent Migration Pipeline** → confirm `NEEDS_REVIEW` (`ESCALATED_FOR_REVIEW`), blocking constraint evidence under Rules 4 & 5.
- [ ] **Verify Fallback:** Set `$env:LLM_ENABLED="false"`, restart backend, run assessment to show `SKIPPED` status with deterministic narrative.
- [ ] **Verify Worksheet Download:** Click **Download mapping worksheet** and verify `mapping-worksheet-<workflow_id>.csv` generates properly.
- [ ] **Verify Audit Drawer:** Click **Explainability & Audit** and verify 10-node execution timeline and telemetry.
