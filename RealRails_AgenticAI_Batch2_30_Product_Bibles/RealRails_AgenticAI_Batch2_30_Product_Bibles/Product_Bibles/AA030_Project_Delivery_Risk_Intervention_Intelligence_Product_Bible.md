# AA030 — Project Delivery Risk & Intervention Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA030` |
| Domain | PMO / Delivery Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Project Delivery Risk & Intervention Intelligence**

## 2. Business Problem

Project managers need a consistent way to identify delivery risk using milestone slippage, dependency status, issue severity, resource gaps, and upcoming deadlines.

## 3. Primary Users / Actors

- Project manager
- PMO analyst
- Delivery lead

## 4. MVP Objective

Recommend project intervention priority and next coordination action using transparent deterministic rules.

## 5. Business Input

Project snapshot with milestone status, days slipped, critical dependencies, open high-severity issues, resource-gap flags, next deadline, and current status.

## 6. Expected Final Output / Recommendation

Recommended action: CONTINUE_MONITORING / RECOVERY_PLAN / DEPENDENCY_ESCALATION / RESOURCE_REVIEW / EXECUTIVE_REVIEW, with risk score.

## 7. Domain Data Required

- Milestone plan
- Dependency status
- Issue log summary
- Resource gap flags
- Configured risk thresholds

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Project Intake Agent | Validates project health fields. | `project_snapshot` | `validated_project` |
| Schedule Risk Agent | Scores milestone slippage and deadline pressure. | `validated_project` | `schedule_score` |
| Dependency Agent | Evaluates blocked/critical dependencies. | `validated_project + dependency_data` | `dependency_flags` |
| Issue & Resource Agent | Scores issue severity and declared resource gaps. | `validated_project + issue_resource_data` | `issue_resource_score` |
| Delivery Risk Decision Agent | Combines evidence into an intervention recommendation. | `all agent outputs` | `final_recommendation` |

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
- `project_snapshot`
- `validated_project`
- `schedule_score`
- `dependency_flags`
- `issue_resource_score`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Critical blocked dependency → DEPENDENCY_ESCALATION.
2. Major resource gap near deadline → RESOURCE_REVIEW.
3. High combined schedule + issue risk → RECOVERY_PLAN or EXECUTIVE_REVIEW.
4. Low risk → CONTINUE_MONITORING.
5. Do not infer employee performance from project outcomes.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Calculate fixed delivery-risk score, then apply dependency/resource hard routes and map to intervention level.

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
| Healthy project | Milestones on track, no major blockers | CONTINUE_MONITORING |
| Dependency blocker | Critical external dependency blocked | DEPENDENCY_ESCALATION |
| High delivery risk | Slippage + severe issues + near deadline | RECOVERY_PLAN |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Project health summary
- Risk breakdown
- Agent trace
- Intervention recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No employee performance scoring
- No automatic budget/staffing decisions
- No replacement for project governance

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

DEPENDENCY_BLOCK → escalation; RESOURCE_GAP → resource review; HIGH_RISK → recovery/executive review; LOW_RISK → monitor.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of project updates or issue notes into a concise non-authoritative narrative; risk scoring remains deterministic.

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

