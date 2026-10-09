# AA016 — Access Request Policy Review Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA016` |
| Domain | Identity & Access Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Access Request Policy Review Intelligence**

## 2. Business Problem

Access requests need consistent checks against role, environment, segregation rules, expiration, and approval prerequisites before human approval.

## 3. Primary Users / Actors

- Access governance analyst
- Application owner
- IAM operations lead

## 4. MVP Objective

Recommend an access-review route using deterministic policy checks. The MVP does not grant access automatically.

## 5. Business Input

Access request with requester, target application, requested role, environment, duration, business justification status, and prerequisite approvals.

## 6. Expected Final Output / Recommendation

Recommended action: READY_FOR_APPROVAL / POLICY_REVIEW / REQUEST_INFO / CONFLICT_REVIEW / REJECT_UNSUPPORTED, with reasons.

## 7. Domain Data Required

- Role catalogue
- Environment rules
- Segregation/conflict rules
- Duration limits
- Approval prerequisites

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Access Intake Agent | Validates request fields and requested role. | `access_request` | `validated_request` |
| Role Eligibility Agent | Checks role catalogue and environment compatibility. | `validated_request + role_rules` | `eligibility_status` |
| Conflict Agent | Checks configured segregation/conflict rules. | `validated_request + conflict_rules` | `conflict_flags` |
| Approval & Duration Agent | Checks justification, prerequisite approvals, and duration policy. | `validated_request + policy` | `approval_flags` |
| Access Review Decision Agent | Recommends the human review route. | `all agent outputs` | `final_recommendation` |

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
- `access_request`
- `validated_request`
- `eligibility_status`
- `conflict_flags`
- `approval_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Unsupported role/environment → REJECT_UNSUPPORTED.
2. Configured role conflict → CONFLICT_REVIEW.
3. Missing justification/approval → REQUEST_INFO.
4. All policy checks pass → READY_FOR_APPROVAL.
5. Never grant or revoke access in the MVP.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply hard policy blockers first, then route clean requests to human approval.

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
| Valid request | Supported role, approvals present | READY_FOR_APPROVAL |
| Conflict | Role violates configured segregation rule | CONFLICT_REVIEW |
| Missing approval | Prerequisite approval absent | REQUEST_INFO |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Access request
- Policy checks
- Conflict evidence
- Agent trace
- Review recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No automatic access provisioning
- No credential processing
- No dynamic policy creation

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

POLICY_PASS → ready; CONFLICT → conflict review; MISSING_APPROVAL → request info; UNSUPPORTED → reject unsupported.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of business justification into a concise non-authoritative summary. Policy evaluation remains deterministic.

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

