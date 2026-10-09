# AA001 — Appointment Operations Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA001` |
| Domain | Healthcare Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Appointment Operations Intelligence**

## 2. Business Problem

Appointment teams need a consistent way to evaluate patient appointment requests against slot availability, queue load, service priority, and resource constraints without relying on ad-hoc manual judgement.

## 3. Primary Users / Actors

- Appointment coordinator
- Clinic operations lead
- Service desk reviewer

## 4. MVP Objective

Recommend the most suitable appointment action for a request using deterministic operational rules and visible evidence. This MVP is operational decision support only; it does not diagnose, prescribe, or replace clinical judgement.

## 5. Business Input

Appointment request containing service/specialty, requested date range, urgency class, location preference, patient constraints, and optional preferred clinician.

## 6. Expected Final Output / Recommendation

Recommended appointment action: BOOK / OFFER_ALTERNATIVE / PRIORITIZE_REVIEW / REQUEST_MORE_INFO, with candidate slot, priority score, reasons, and evidence.

## 7. Domain Data Required

- Seeded appointment slots and capacity
- Queue length by specialty/date
- Resource/clinician availability
- Operational priority rules
- Request constraints

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Request Validation Agent | Validates required request fields and normalizes the appointment intent. | `appointment_request` | `validated_request, missing_fields` |
| Availability Agent | Finds eligible slots that satisfy date, specialty, location, and resource constraints. | `validated_request + slot_data` | `candidate_slots` |
| Queue Load Agent | Measures queue pressure and identifies overloaded or underutilized periods. | `validated_request + queue_data` | `queue_status, queue_score` |
| Priority & Resource Agent | Applies operational priority and resource constraints to the valid candidates. | `validated_request + candidate_slots + resource_data` | `priority_score, resource_flags` |
| Appointment Decision Agent | Combines agent outputs into one structured operational recommendation. | `all agent outputs` | `final_recommendation` |

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
- `appointment_request`
- `validated_request`
- `candidate_slots`
- `queue_status`
- `priority_score`
- `resource_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Reject execution when required specialty or date window is missing.
2. Remove slots outside the requested date window or with unavailable required resources.
3. Increase priority score for approved urgency classes; never infer clinical urgency from free text.
4. If no eligible slot exists, return OFFER_ALTERNATIVE or PRIORITIZE_REVIEW rather than inventing capacity.
5. If multiple slots are eligible, rank by priority, queue pressure, and request fit using fixed weights.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Choose the highest-ranked valid slot when all mandatory constraints pass. Route to human review when urgency is high, required information is incomplete, or no candidate meets minimum suitability.

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
| Normal request | Standard priority, multiple matching slots | BOOK with top-ranked slot and reasons |
| Capacity conflict | No slot meets the required window | OFFER_ALTERNATIVE with nearest valid options |
| High-priority review | Approved urgency class + constrained capacity | PRIORITIZE_REVIEW with evidence |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Appointment request form
- Candidate slots / ranking panel
- Agent workflow trace
- Shared context viewer
- Final recommendation card
- Audit/evidence panel

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No diagnosis or clinical decision-making
- No real hospital scheduling integration
- No autonomous booking into production systems
- No inference of sensitive medical facts beyond provided operational fields

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

LangGraph routing can branch after validation/priority scoring: NORMAL → decision, MISSING_DATA → request more information, HIGH_PRIORITY → human review, NO_CAPACITY → alternative-slot path.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional controlled use for converting free-text appointment notes into structured non-clinical constraints or generating a human-readable explanation. Deterministic priority and capacity rules remain authoritative.

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

