# AA008 — CRM Data Migration Mapping Intelligence
## RealRails Agentic AI Batch 2 — Phase 2.3: Add a Controlled LLM Enhancement

Evolved from Phase 2.2 conditional routing by introducing **ONE focused, controlled LLM enhancement** strictly conforming to **Product Bible §21** (`Future Controlled LLM Opportunity`) and **02_Controlled_LLM_and_Evaluation_Guide.md**.

The LLM serves as a **Semantic Transformation & Migration Rationale Explainer**, augmenting human understanding while **preserving 100% of deterministic business authority and rules**.

---

## 🎯 Phase 2.3 LangGraph Architecture & Flow

```text
START
  ↓
1. context_validation (Context Builder & Input Validator)
  ↓
2. schema_analyzer    (Agent 1: Schema Analyzer Agent)
  ↓
3. field_mapper       (Agent 2: Field Mapping Agent)
  ↓
4. transformer        (Agent 3: Transformation Agent)
  ↓
5. validator          (Agent 4: Validation Agent)
  ↓
6. decision           (Agent 5: Migration Decision Agent)
  ↓
[conditional_router: route_after_decision]
  ├── "route_direct_accept"   ──> direct_accept   (Branch A: HIGH_CONFIDENCE)        ──┐
  ├── "route_transform_verify" ──> transform_verify (Branch B: TRANSFORM_REQUIRED)    ──┤
  └── "route_human_review"    ──> human_review    (Branch C: EXCEPTION / REVIEW)     ──┘
                                                                                         ↓
                                                                                     7. llm_enhancement (Product Bible §21 Adapter)
                                                                                         ↓
                                                                                     8. explainer       (Migration Explainer)
                                                                                         ↓
                                                                                     9. audit           (Immutable Audit Store)
                                                                                         ↓
                                                                                        END
```

---

## 🤖 Controlled LLM Role & Boundaries (§21)

- **Approved Role:** Semantic transformation rationales (explaining why type conversions or date normalizations under Rule 3 are needed) and clear plain-English executive migration narrative & review triage actions.
- **Deterministic Authority Intact:** Rules 1–5, candidate matching, transformation planning, constraint validation, and routing decisions remain 100% deterministic.
- **Input Boundedness:** Consumes only deterministic structured state fields (`source_table`, `destination_table`, `overall_status`, `selected_route`, `summary_counts`, `transformations`, `review_items`, `blocking_issues`).
- **Structured Output Schema:** Pydantic `LLMEnhancementOutput` (`executive_summary`, `transformation_rationales`, `risk_assessment`, `suggested_review_actions`).
- **Strict Output Validation:** `LLMOutputValidator` validates JSON, enforces character bounds, and strips hallucinated destination field references.
- **Deterministic Fallback:** `DeterministicFallbackProvider` generates safe template reasoning whenever the LLM times out, rate limits, encounters provider errors, or receives malformed data.
- **Zero Secrets Logged:** Credentials are supplied via environment variables (`GEMINI_API_KEY`, `OPENAI_API_KEY`). Headers are used to prevent URL query leakage, and regex sanitization strips tokens from error messages.

---

## 🔀 Deterministic Route Table (Product Bible §20)

| Route Key | Condition | State Evaluated | Destination Node | Outcome & Action |
|---|---|---|---|---|
| `route_direct_accept` | **HIGH_CONFIDENCE** | `val.all_valid == True`<br>`rec.overall_status == "READY"`<br>`summary_counts["TRANSFORM"] == 0`<br>`summary_counts["REVIEW"] == 0` | `direct_accept` | **`ACCEPTED_DIRECT`**: 100% direct-compatible fields (Rules 1 & 2). Direct acceptance; LLM confirms low risk. |
| `route_transform_verify` | **TRANSFORM_REQUIRED** | `val.all_valid == True`<br>`rec.overall_status == "READY"`<br>`summary_counts["TRANSFORM"] > 0`<br>`summary_counts["REVIEW"] == 0` | `transform_verify` | **`TRANSFORM_STAGED`**: Type casts or date formatting needed (Rule 3). LLM generates technical transformation rationales. |
| `route_human_review` | **REVIEW_REQUIRED / REQUIRED_FIELD_MISSING** | `not val.all_valid`<br>`rec.overall_status == "NEEDS_REVIEW"`<br>`summary_counts["REVIEW"] > 0` | `human_review` | **`ESCALATED_FOR_REVIEW`**: Missing mandatory fields or unresolvable relationship constraints (Rules 4 & 5). LLM produces step-by-step triage actions. |

---

## 🗺️ Component Mapping: Phase 1 & 2.2 -> Phase 2.3

| Existing Component | LangGraph Component | Responsibility & Implementation |
|---|---|---|
| **Sequential Orchestrator** | **Conditional `StateGraph(WorkflowState)`** | Branching workflow routing after decision into destination nodes and converging to LLM |
| **Workflow Context** | **Graph State** (`WorkflowState`) | Strongly typed state container carrying all schema profiles, plans, LLM enhancement, telemetry, trace, and routes |
| **Domain Agents 1–5** | **Nodes 1–6** | Deterministic profiling, matching, transform planning, constraint checks, and decision synthesis |
| **Conditional Branches** | **Nodes `direct_accept`, `transform_verify`, `human_review`** | Record routing metadata for HIGH_CONFIDENCE, TRANSFORM_REQUIRED, and EXCEPTION routes |
| **Controlled LLM** | **Node `llm_enhancement`** | Service adapter executing bounded LLM prompt, output validation, and fallback handling |
| **Explanation Layer** | **Node `explainer`** | Merges deterministic rule citations and validated LLM narrative into unified explanation |
| **Audit Repository** | **Node `audit`** | Persists run record, selected route, LLM telemetry (`llm_telemetry`), and 10-node trace |
| **Traceability** | **`node_trace` Telemetry** | 10 executed steps logging step number, node name, agent/gateway, status, and summary |

---

## 🧪 Evaluation Results (5 Scenarios Verified)

1. **Scenario 1: Simple Schema (Normal Path)**
   - *Condition:* `HIGH_CONFIDENCE` → `route_direct_accept` → `direct_accept` node.
   - *Result:* `READY`, `ACCEPTED_DIRECT`, 6 `DIRECT_MAP`, 1 `DEFAULT`.
   - *LLM Behavior:* Generates executive summary confirming full field compatibility; `risk_assessment="LOW"`.
2. **Scenario 2: Naming Mismatch (Alternate Transform Path)**
   - *Condition:* `TRANSFORM_REQUIRED` → `route_transform_verify` → `transform_verify` node.
   - *Result:* `READY`, `TRANSFORM_STAGED`, 6 `DIRECT_MAP`, 1 `TRANSFORM`.
   - *LLM Behavior:* Generates technical rationale for `created_at` date string conversion; `risk_assessment="MODERATE"`.
3. **Scenario 3: Relationship Mismatch (Exception Path)**
   - *Condition:* `REVIEW_REQUIRED / REQUIRED_FIELD_MISSING` → `route_human_review` → `human_review` node.
   - *Result:* `NEEDS_REVIEW`, `ESCALATED_FOR_REVIEW`, 4 `DIRECT_MAP`, 1 `REVIEW`.
   - *LLM Behavior:* Highlights `HIGH RISK`; produces concrete triage steps to resolve `account_id` foreign key.
4. **Scenario 4: LLM Unavailable / Timeout / Rate Limit (429 Fallback)**
   - *Condition:* Network timeout or rate limit encountered.
   - *Result:* Deterministic fallback template engages automatically; `fallback_used=True`, `status="FALLBACK"`, workflow completes safely with HTTP 200.
5. **Scenario 5: Malformed / Invalid LLM Output (Validation Fallback)**
   - *Condition:* Provider returns non-JSON or invalid schema.
   - *Result:* Validator rejects payload, prunes hallucinated target fields, and activates deterministic fallback.

---

## 🚀 Exact Run Commands

### 1. Run Tests (Hermetic, Fast & Deterministic)
```bash
cd backend
python -m pytest
```
*Output: 28 passed in < 2 seconds.*

### 2. Run End-to-End Verification Script
```bash
cd backend
python validate_e2e.py
```
*Output: All 3 scenarios, LangGraph routing, and LLM telemetry 100% verified.*

### 3. Start Backend API Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Build and Run Frontend Web Client
```bash
cd frontend
npm install
npm run build
npm run dev
```
Open `http://localhost:5173` in your browser.
