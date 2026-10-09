# AA011 — Major Incident Triage & Escalation Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA011` |
| Domain | IT Operations |
| Complexity | Advanced |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Major Incident Triage & Escalation Intelligence**

## 2. Business Problem

Operations teams need to quickly classify high-impact incidents, identify service dependencies, check evidence quality, and recommend an escalation path.

## 3. Primary Users / Actors

- Major incident manager
- Operations lead
- Service owner

## 4. MVP Objective

Recommend incident handling path and escalation level using deterministic impact, service criticality, and evidence rules.

## 5. Business Input

Incident record with affected services, impact scope, start time, symptoms, dependency indicators, active alerts, and current responders.

## 6. Expected Final Output / Recommendation

Recommended action: STANDARD_INCIDENT / MAJOR_INCIDENT_REVIEW / ENGAGE_DEPENDENCY_TEAM / REQUEST_EVIDENCE / EXECUTIVE_ESCALATION, with reasons.

## 7. Domain Data Required

- Service criticality map
- Dependency map
- Impact thresholds
- Escalation rules
- Active incident/alert summaries

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Incident Intake Agent | Validates incident facts and required evidence. | `incident_record` | `validated_incident` |
| Impact Agent | Calculates affected-user/service impact from provided facts. | `validated_incident + criticality` | `impact_class` |
| Dependency Agent | Identifies relevant known service dependencies. | `validated_incident + dependency_map` | `dependency_flags` |
| Escalation Readiness Agent | Checks elapsed time, responders, and escalation thresholds. | `validated_incident + rules` | `escalation_flags` |
| Major Incident Decision Agent | Recommends incident path and escalation level. | `all agent outputs` | `final_recommendation` |

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
- `incident_record`
- `validated_incident`
- `impact_class`
- `dependency_flags`
- `escalation_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Critical-service widespread impact → MAJOR_INCIDENT_REVIEW.
2. Known dependency likely involved → ENGAGE_DEPENDENCY_TEAM.
3. Insufficient evidence for impact classification → REQUEST_EVIDENCE.
4. Configured duration/impact threshold breach → EXECUTIVE_ESCALATION.
5. Do not infer root cause without evidence.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Select highest applicable escalation path using deterministic precedence and preserve all supporting evidence.

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
| Localized incident | Limited impact and normal SLA | STANDARD_INCIDENT |
| Dependency impact | Critical dependency implicated | ENGAGE_DEPENDENCY_TEAM |
| Major outage | High impact + threshold breach | MAJOR_INCIDENT_REVIEW or EXECUTIVE_ESCALATION |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Incident summary
- Impact/dependency panels
- Agent flow
- Escalation recommendation
- Timeline/audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No automated production remediation
- No unsupported root-cause claims
- No external stakeholder communications

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

LOW_IMPACT → standard; DEPENDENCY_FLAG → engage dependency; MAJOR_THRESHOLD → major incident; INSUFFICIENT_EVIDENCE → request evidence.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of incident updates into structured facts or human-readable status explanation. It must not invent root cause or override deterministic escalation rules.

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

