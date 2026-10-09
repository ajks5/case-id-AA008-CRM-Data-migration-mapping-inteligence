# AA010 — Service Ticket Resolution Prioritization
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA010` |
| Domain | IT Service Management |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Service Ticket Resolution Prioritization**

## 2. Business Problem

Support teams need to prioritize incoming tickets and recommend the next operational handling path using severity, service impact, SLA, known category, and available ownership.

## 3. Primary Users / Actors

- Service desk analyst
- Operations support lead
- Queue manager

## 4. MVP Objective

Recommend ticket priority and next handling action using deterministic service-management rules.

## 5. Business Input

Ticket with service, category, impact, urgency, description, age, SLA target, ownership, and known error indicators.

## 6. Expected Final Output / Recommendation

Recommended action: ASSIGN / PRIORITIZE / REQUEST_INFO / KNOWN_FIX_PATH / ESCALATE, with priority and reasons.

## 7. Domain Data Required

- Ticket queue
- Service criticality rules
- SLA thresholds
- Known category rules
- Support ownership map

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Ticket Intake Agent | Validates and normalizes ticket metadata. | `ticket` | `validated_ticket` |
| Impact & SLA Agent | Calculates operational impact and SLA pressure. | `validated_ticket + service_rules` | `impact_score, sla_status` |
| Category & Known Error Agent | Matches deterministic category/error rules. | `validated_ticket + known_rules` | `category_result, known_fix_flag` |
| Ownership Agent | Finds eligible team/queue and checks ownership gaps. | `validated_ticket + ownership_map` | `routing_result` |
| Ticket Decision Agent | Produces priority and next operational action. | `all agent outputs` | `final_recommendation` |

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
- `ticket`
- `validated_ticket`
- `impact_score`
- `sla_status`
- `category_result`
- `known_fix_flag`
- `routing_result`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Critical service + high impact or imminent SLA breach → PRIORITIZE/ESCALATE.
2. Known error + valid runbook path → KNOWN_FIX_PATH.
3. Missing required reproduction/context data → REQUEST_INFO.
4. No valid owner → ESCALATE routing.
5. Do not execute destructive remediation automatically.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply severity/SLA overrides, then select routing and next action based on category and ownership evidence.

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
| Known issue | Matched known error and valid owner | KNOWN_FIX_PATH |
| SLA risk | High impact, close to breach | PRIORITIZE |
| Incomplete ticket | Missing key diagnostic fields | REQUEST_INFO |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Ticket intake
- Priority/SLA indicators
- Agent trace
- Routing recommendation
- Evidence/audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No autonomous production changes
- No credential handling
- No replacement for incident/problem management processes

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

KNOWN_FIX → known path; HIGH_IMPACT/SLA → escalation; MISSING_INFO → request data; NORMAL → assign.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional classification/summarization of free-text ticket descriptions or explanation generation, with deterministic routing and SLA logic preserved.

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

