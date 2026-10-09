# AA014 — Cloud Cost Anomaly Review Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA014` |
| Domain | Cloud FinOps |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Cloud Cost Anomaly Review Intelligence**

## 2. Business Problem

Cloud cost spikes and unusual resource usage need consistent review so teams can distinguish expected changes from anomalies requiring owner action.

## 3. Primary Users / Actors

- FinOps analyst
- Cloud operations lead
- Application owner

## 4. MVP Objective

Classify cost anomalies and recommend an investigation path using deterministic thresholds and ownership data.

## 5. Business Input

Resource/subscription cost snapshot with baseline, current spend, percentage change, resource type, tags, owner, recent change indicator, and budget threshold.

## 6. Expected Final Output / Recommendation

Recommended action: NO_ACTION / OWNER_REVIEW / INVESTIGATE_SPIKE / TAGGING_FIX / BUDGET_ESCALATION, with evidence.

## 7. Domain Data Required

- Historical cost baseline
- Current cost
- Budget thresholds
- Resource tags/ownership
- Known planned-change flags

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Cost Intake Agent | Validates cost period, owner, and baseline fields. | `cost_event` | `validated_event` |
| Variance Agent | Calculates absolute and percentage variance. | `validated_event + baseline` | `variance_metrics` |
| Ownership & Tagging Agent | Checks required ownership and cost-allocation metadata. | `validated_event + tags` | `ownership_status` |
| Budget & Change Agent | Checks budget threshold and known planned-change indicators. | `validated_event + budget + change_flags` | `budget_flags, change_context` |
| FinOps Decision Agent | Recommends the review route. | `all agent outputs` | `final_recommendation` |

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
- `cost_event`
- `validated_event`
- `variance_metrics`
- `ownership_status`
- `budget_flags`
- `change_context`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Missing owner/tag → TAGGING_FIX.
2. Budget threshold breach → BUDGET_ESCALATION.
3. Large unexplained variance → INVESTIGATE_SPIKE.
4. Variance explained by approved planned change → OWNER_REVIEW or NO_ACTION.
5. Do not automatically shut down resources.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply metadata and budget hard rules first, then classify anomaly severity using configured variance bands.

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
| Expected growth | Moderate increase with approved change | OWNER_REVIEW |
| Unexplained spike | Large variance, no planned change | INVESTIGATE_SPIKE |
| Budget breach | Spend crosses configured budget | BUDGET_ESCALATION |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Cost anomaly list
- Variance chart/table
- Ownership panel
- Agent trace
- Recommended action
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No automated resource shutdown
- No billing-system modifications
- No financial commitment authority

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

TAG_GAP → tagging path; BUDGET_BREACH → escalation; LARGE_UNEXPLAINED → investigation; EXPLAINED → normal review.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of change notes or generation of investigation explanation; variance and budget decisions stay deterministic.

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

