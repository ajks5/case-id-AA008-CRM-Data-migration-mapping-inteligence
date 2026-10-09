# AA026 — Facility Work Order Prioritization Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA026` |
| Domain | Facilities Management |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Facility Work Order Prioritization Intelligence**

## 2. Business Problem

Facilities teams need to prioritize maintenance work orders using asset criticality, safety flag, service impact, repeat history, and SLA.

## 3. Primary Users / Actors

- Facility coordinator
- Maintenance supervisor
- Site operations lead

## 4. MVP Objective

Recommend work-order priority and routing using deterministic facilities rules.

## 5. Business Input

Work order with asset, site, issue category, safety flag, service impact, age, SLA, repeat count, and technician skill requirement.

## 6. Expected Final Output / Recommendation

Recommended action: SCHEDULE / PRIORITIZE / SAFETY_REVIEW / SPECIALIST_ASSIGNMENT / REQUEST_INFO, with priority score.

## 7. Domain Data Required

- Asset criticality
- Issue categories
- SLA thresholds
- Repeat history
- Technician skill map

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Work Order Intake Agent | Validates asset and issue fields. | `work_order` | `validated_order` |
| Criticality & Impact Agent | Scores asset/service impact. | `validated_order + asset_data` | `impact_score` |
| Safety & Repeat Agent | Checks approved safety flags and repeat issue count. | `validated_order + history` | `safety_flags, repeat_flags` |
| Skill & SLA Agent | Checks SLA pressure and specialist requirement. | `validated_order + skills` | `sla_status, skill_route` |
| Work Order Decision Agent | Produces priority and routing recommendation. | `all agent outputs` | `final_recommendation` |

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
- `work_order`
- `validated_order`
- `impact_score`
- `safety_flags`
- `repeat_flags`
- `sla_status`
- `skill_route`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Configured safety flag → SAFETY_REVIEW.
2. Critical asset + high service impact or imminent SLA breach → PRIORITIZE.
3. Specialist-required issue → SPECIALIST_ASSIGNMENT.
4. Missing asset/issue details → REQUEST_INFO.
5. Repeat issue increases priority using fixed rule.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply safety/specialist hard routes, then compute priority from asset impact, repeat history, and SLA.

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
| Routine repair | Low impact, normal SLA | SCHEDULE |
| Safety flag | Approved safety category present | SAFETY_REVIEW |
| Critical repeat issue | Critical asset + repeat fault | PRIORITIZE |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Work order
- Impact/safety cards
- Agent trace
- Priority/routing
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No autonomous machinery control
- No technician performance scoring
- No replacement for qualified safety review

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

SAFETY_FLAG → safety review; SPECIALIST → specialist route; HIGH_PRIORITY → prioritize; MISSING_DATA → request info.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of free-text work-order descriptions into issue categories, with deterministic routing preserved.

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

