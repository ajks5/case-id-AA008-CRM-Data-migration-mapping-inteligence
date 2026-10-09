# AA013 — Patch Compliance Remediation Prioritization
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA013` |
| Domain | Cloud Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Patch Compliance Remediation Prioritization**

## 2. Business Problem

Large VM fleets create many patching exceptions, and operations teams need a consistent way to prioritize remediation based on compliance state, failure reason, service criticality, and repeated misses.

## 3. Primary Users / Actors

- Cloud operations engineer
- Patch coordinator
- Service owner

## 4. MVP Objective

Recommend the next patch-remediation action for each VM using deterministic compliance and failure rules.

## 5. Business Input

VM patch record with compliance status, failed update count, last patch window, service criticality, disk status, agent health, reboot status, and exception history.

## 6. Expected Final Output / Recommendation

Recommended action: RETRY_PATCH / FIX_PREREQUISITE / SCHEDULE_REBOOT / INVESTIGATE_AGENT / ESCALATE_OWNER / NO_ACTION.

## 7. Domain Data Required

- Patch compliance snapshot
- VM health indicators
- Service criticality
- Failure-code rules
- Exception history

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Compliance Intake Agent | Normalizes VM compliance and patch status. | `vm_record` | `validated_vm` |
| Failure Classification Agent | Maps deterministic failure codes and prerequisite issues. | `validated_vm + rules` | `failure_class` |
| Health & Prerequisite Agent | Checks disk, agent, reboot, and connectivity prerequisites. | `validated_vm` | `health_flags` |
| Priority Agent | Scores remediation priority using criticality and repeated misses. | `validated_vm + history` | `priority_score` |
| Patch Remediation Decision Agent | Selects the next safe operational action. | `all agent outputs` | `final_recommendation` |

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
- `vm_record`
- `validated_vm`
- `failure_class`
- `health_flags`
- `priority_score`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Disk/prerequisite failure → FIX_PREREQUISITE.
2. Pending reboot blocking compliance → SCHEDULE_REBOOT.
3. Patch agent unhealthy → INVESTIGATE_AGENT.
4. Repeated miss on critical service → ESCALATE_OWNER.
5. Compliant VM → NO_ACTION.
6. No autonomous patch execution in the MVP.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Use failure-class precedence, then priority score for queue ordering and owner escalation.

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
| Disk issue | Insufficient disk + failed patch | FIX_PREREQUISITE |
| Repeated miss | Critical VM missed multiple cycles | ESCALATE_OWNER |
| Compliant VM | No missing updates | NO_ACTION |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- VM compliance list
- Failure classification
- Priority queue
- Agent trace
- Recommended remediation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No remote command execution
- No credentials
- No automatic reboot/patching
- No production Azure integration required

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

COMPLIANT → stop; PREREQUISITE_FAIL → fix path; AGENT_FAIL → agent investigation; REPEATED_CRITICAL → escalation.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of verbose error logs into a known failure category or explanation. Deterministic prerequisite and escalation rules control the action.

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

