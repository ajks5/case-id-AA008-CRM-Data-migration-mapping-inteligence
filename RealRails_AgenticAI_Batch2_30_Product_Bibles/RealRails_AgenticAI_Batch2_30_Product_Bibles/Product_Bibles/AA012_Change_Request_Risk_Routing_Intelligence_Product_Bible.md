# AA012 — Change Request Risk Routing Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA012` |
| Domain | IT Change Management |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Change Request Risk Routing Intelligence**

## 2. Business Problem

Change teams need consistent operational risk classification and review routing based on service criticality, blast radius, rollback readiness, maintenance window, and test evidence.

## 3. Primary Users / Actors

- Change manager
- Platform owner
- Operations reviewer

## 4. MVP Objective

Recommend change-review path using deterministic operational risk rules.

## 5. Business Input

Change request with affected service, change type, environment, implementation window, rollback plan, test evidence, dependency count, and requester-declared risk.

## 6. Expected Final Output / Recommendation

Recommended action: STANDARD_REVIEW / ENHANCED_REVIEW / REQUEST_EVIDENCE / RESCHEDULE / ESCALATE_CHANGE, with risk score and reasons.

## 7. Domain Data Required

- Service criticality
- Change-type rules
- Maintenance windows
- Dependency metadata
- Evidence checklist

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Change Intake Agent | Validates required change fields and evidence references. | `change_request` | `validated_change` |
| Service Impact Agent | Scores criticality and blast-radius indicators. | `validated_change + service_data` | `impact_score` |
| Rollback & Evidence Agent | Checks rollback readiness and mandatory evidence. | `validated_change + checklist` | `readiness_flags` |
| Window & Dependency Agent | Checks maintenance window and dependency conflicts. | `validated_change + windows + dependencies` | `window_flags, dependency_flags` |
| Change Risk Decision Agent | Combines evidence into a review route. | `all agent outputs` | `final_recommendation` |

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
- `change_request`
- `validated_change`
- `impact_score`
- `readiness_flags`
- `window_flags`
- `dependency_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Missing rollback/test evidence → REQUEST_EVIDENCE.
2. Outside approved window → RESCHEDULE unless emergency policy applies.
3. High criticality + broad dependency impact → ENHANCED_REVIEW/ESCALATE_CHANGE.
4. Normal low-risk change with complete evidence → STANDARD_REVIEW.
5. Do not execute the change.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply hard blockers first, then map fixed risk score to standard/enhanced/escalated review.

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
| Routine change | Low impact, evidence complete, valid window | STANDARD_REVIEW |
| Evidence gap | Rollback plan missing | REQUEST_EVIDENCE |
| High-risk change | Critical service + many dependencies | ENHANCED_REVIEW |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Change summary
- Risk breakdown
- Evidence checklist
- Agent trace
- Review recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No automatic production deployment
- No approval authority beyond MVP recommendation
- No emergency-change execution

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

BLOCKER → request/reschedule; LOW_RISK → standard review; HIGH_RISK → enhanced review; EXTREME → escalation.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of change description into structured implementation facts or readable risk explanation; deterministic risk rules remain authoritative.

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

