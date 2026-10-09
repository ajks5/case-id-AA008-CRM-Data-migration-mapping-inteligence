# AA021 — Fleet Maintenance Prioritization Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA021` |
| Domain | Logistics Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Fleet Maintenance Prioritization Intelligence**

## 2. Business Problem

Fleet teams need to prioritize maintenance based on due service, fault severity, mileage, repeat issues, and operational availability.

## 3. Primary Users / Actors

- Fleet coordinator
- Maintenance planner
- Operations manager

## 4. MVP Objective

Recommend maintenance priority and next operational action using deterministic vehicle-health rules.

## 5. Business Input

Vehicle record with mileage, service due date, fault codes, repeat-fault count, current availability, last maintenance, and route commitment.

## 6. Expected Final Output / Recommendation

Recommended action: CONTINUE_SERVICE / SCHEDULE_MAINTENANCE / PRIORITY_INSPECTION / REMOVE_FROM_SCHEDULE / REQUEST_DATA.

## 7. Domain Data Required

- Vehicle maintenance history
- Service intervals
- Fault severity table
- Route commitments
- Availability status

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Vehicle Intake Agent | Validates maintenance and availability fields. | `vehicle_record` | `validated_vehicle` |
| Service Due Agent | Checks mileage/time-based maintenance thresholds. | `validated_vehicle + intervals` | `service_status` |
| Fault Agent | Classifies known fault severity and repeat faults. | `validated_vehicle + fault_rules` | `fault_status` |
| Operational Impact Agent | Checks route commitment and spare capacity. | `validated_vehicle + operations` | `impact_status` |
| Maintenance Decision Agent | Recommends maintenance action and priority. | `all agent outputs` | `final_recommendation` |

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
- `vehicle_record`
- `validated_vehicle`
- `service_status`
- `fault_status`
- `impact_status`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Critical known safety-related fault flag → REMOVE_FROM_SCHEDULE and human inspection.
2. Overdue service without critical fault → SCHEDULE_MAINTENANCE.
3. Repeat unresolved fault → PRIORITY_INSPECTION.
4. Incomplete maintenance data → REQUEST_DATA.
5. No autonomous repair actions.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply critical fault rules first, then service-due and repeat-fault priority with operational impact evidence.

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
| Routine due service | Service threshold reached | SCHEDULE_MAINTENANCE |
| Repeat fault | Same fault repeated | PRIORITY_INSPECTION |
| Critical flag | Configured critical fault code | REMOVE_FROM_SCHEDULE |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Vehicle summary
- Service/fault status
- Agent trace
- Maintenance recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No autonomous driving/vehicle control
- No diagnostic replacement for qualified technicians
- No repair execution

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

CRITICAL_FAULT → remove/review; REPEAT_FAULT → priority inspection; SERVICE_DUE → schedule; HEALTHY → continue.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of technician notes into non-authoritative fault context or explanation. Deterministic fault/service rules remain authoritative.

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

