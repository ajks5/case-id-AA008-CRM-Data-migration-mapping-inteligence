# AA018 — Purchase Request Routing Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA018` |
| Domain | Procurement Operations |
| Complexity | Easy |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Purchase Request Routing Intelligence**

## 2. Business Problem

Purchase requests need consistent routing based on category, amount band, budget status, preferred supplier availability, and exception flags.

## 3. Primary Users / Actors

- Procurement coordinator
- Budget owner
- Operations requester

## 4. MVP Objective

Recommend the correct procurement path and review level.

## 5. Business Input

Purchase request with category, amount, cost center, budget availability, preferred supplier status, urgency, and exception reason.

## 6. Expected Final Output / Recommendation

Recommended action: STANDARD_PROCUREMENT / PREFERRED_SUPPLIER / BUDGET_REVIEW / EXCEPTION_REVIEW / REQUEST_INFO.

## 7. Domain Data Required

- Category rules
- Approval amount bands
- Budget status
- Preferred supplier list
- Exception rules

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Purchase Intake Agent | Validates request and category. | `purchase_request` | `validated_request` |
| Budget Agent | Checks budget availability and amount thresholds. | `validated_request + budget` | `budget_status` |
| Supplier Path Agent | Checks preferred supplier/category route. | `validated_request + supplier_rules` | `supplier_route` |
| Exception Agent | Checks urgency and configured exception conditions. | `validated_request + exception_rules` | `exception_flags` |
| Purchase Routing Decision Agent | Chooses the correct procurement path. | `all agent outputs` | `final_recommendation` |

## 9. Agent Responsibilities

Each specialized agent must:

- perform one clear business responsibility
- consume structured input from the current workflow context
- produce a structured output
- avoid making decisions outside its boundary
- expose enough evidence for later explanation and audit

The **Decision Agent** combines prior agent outputs into the final structured recommendation.

## 10. Agent Inputs and Outputs

Use explicit structured models for:

- original business input
- validated/normalized input
- each agent output
- decision result
- explanation/evidence
- audit reference

Do not pass unstructured blobs between agents when a small structured contract is practical.

## 11. Run-Scoped Shared Workflow Context

The workflow context should contain at least:

- `workflow_id`
- `purchase_request`
- `validated_request`
- `budget_status`
- `supplier_route`
- `exception_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Missing category/amount/cost center → REQUEST_INFO.
2. Budget unavailable or threshold exceeded → BUDGET_REVIEW.
3. Preferred supplier available and no exception → PREFERRED_SUPPLIER.
4. Configured exception → EXCEPTION_REVIEW.
5. Otherwise → STANDARD_PROCUREMENT.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply data completeness, budget, supplier, and exception precedence in that order.

The final response should contain:

- `status` / recommended action
- score or priority where relevant
- short reasons
- triggered rules / evidence
- agent output references where useful
- audit reference

## 14. Execution Flow

```text
Business Input
    ↓
Input Validation / Adapter
    ↓
Context Builder
    ↓
Run-Scoped Shared Workflow Context
    ↓
Specialized Domain Agents
    ↓
Deterministic Rules / Scoring
    ↓
Decision / Recommendation Agent
    ↓
Structured Recommendation
    ↓
Explanation + Evidence
    ↓
Audit Trail
    ↓
Business UI
```

The implementation may run agents sequentially in Phase 1. Later phases will evolve orchestration using LangGraph.

## 15. Explanation and Evidence Requirements

The application must make it possible to understand:

- which agents executed
- what each agent concluded
- which rules or thresholds triggered
- why the final recommendation was selected
- what important limitations or missing data affected the result

The explanation must not invent evidence that is not present in the workflow state.

## 16. Audit Requirements

Record at minimum:

- `workflow_id`
- request/input reference
- execution timestamp
- agent execution sequence
- major agent outputs
- triggered decision rules
- final recommendation
- errors or fallback state

An in-memory audit store is acceptable for the internship MVP unless a later phase explicitly requires persistence.

## 17. Sample Scenarios

| Scenario | Input / Condition | Expected Behaviour |
|---|---|---|
| Normal request | Budget available, standard supplier route | STANDARD_PROCUREMENT |
| Preferred supplier | Approved vendor exists | PREFERRED_SUPPLIER |
| Budget issue | Amount exceeds available budget | BUDGET_REVIEW |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Purchase request
- Rule results
- Agent trace
- Routing recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No purchasing execution
- No payment authorization
- No autonomous approval

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

MISSING_DATA → request info; BUDGET_FLAG → review; EXCEPTION → exception review; CLEAN → standard/preferred path.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of free-text justification; deterministic budget and routing rules remain authoritative.

The LLM is an enhancement layer. It must not replace deterministic authority where deterministic rules already provide the business decision.

## 22. Acceptance Criteria

The case is ready for core internship progression when:

- [ ] The supplied business input can be submitted through the application.
- [ ] Input is validated and normalized.
- [ ] 3–5 meaningful agent responsibilities are implemented.
- [ ] Agents use structured inputs and outputs.
- [ ] Run-scoped shared workflow context is visible in code and/or UI.
- [ ] Deterministic rules/scoring are implemented and testable.
- [ ] A structured recommendation is produced.
- [ ] Explanation/evidence is available.
- [ ] Audit information is recorded.
- [ ] At least the three sample scenarios can be demonstrated.
- [ ] The case can later map existing agents to LangGraph nodes without redesigning the domain.
- [ ] The Product Bible remains the domain source of truth through later phases.

---

## AI Execution Reminder

When this Product Bible is given to an AI assistant together with a RealRails GitHub post and generic feeder documents:

1. Treat the **current GitHub post** as the immediate task boundary.
2. Treat this **Product Bible** as the domain/product source of truth.
3. Use the **generic RealRails feeder documents** as the engineering method.
4. Use the latest **Repomix** as the implementation truth.
5. Use **ABIP only as an architecture-learning reference**.
6. Do not invent unrelated features, agents, data, or future-phase technologies.

