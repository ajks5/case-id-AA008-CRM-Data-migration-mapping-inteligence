# AA009 — Customer Renewal Action Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA009` |
| Domain | Customer Success |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Customer Renewal Action Intelligence**

## 2. Business Problem

Customer-success teams need a transparent way to identify which renewals require immediate attention based on contract timing, usage, support load, and open commitments.

## 3. Primary Users / Actors

- Customer success manager
- Renewal coordinator
- Account operations lead

## 4. MVP Objective

Recommend the next renewal-support action using operational signals, not autonomous commercial decisions.

## 5. Business Input

Account renewal record with renewal date, usage trend, support issues, open actions, contract status, and engagement history.

## 6. Expected Final Output / Recommendation

Recommended action: STANDARD_RENEWAL / PROACTIVE_OUTREACH / SERVICE_REVIEW / ESCALATE_ACCOUNT / REQUEST_DATA.

## 7. Domain Data Required

- Contract dates
- Usage summaries
- Support-ticket counts
- Open commitments
- Engagement activity

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Renewal Intake Agent | Validates renewal timing and account status. | `renewal_record` | `validated_account` |
| Usage Trend Agent | Classifies usage trend using fixed thresholds. | `validated_account + usage` | `usage_status` |
| Support Health Agent | Measures unresolved support load and severity. | `validated_account + tickets` | `support_health` |
| Commitment & Timing Agent | Checks open commitments and renewal-window SLA. | `validated_account + commitments` | `timing_flags, commitment_flags` |
| Renewal Action Decision Agent | Combines evidence into a customer-success action. | `all agent outputs` | `final_recommendation` |

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
- `renewal_record`
- `validated_account`
- `usage_status`
- `support_health`
- `timing_flags`
- `commitment_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Renewal due soon + unresolved critical issue → ESCALATE_ACCOUNT.
2. Declining usage + moderate support issues → PROACTIVE_OUTREACH.
3. Healthy usage + no major issues → STANDARD_RENEWAL.
4. Missing contract/usage data → REQUEST_DATA.
5. No autonomous price, discount, or contract decision.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply renewal-window overrides, then combine usage/support/commitment scores into an operational next action.

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
| Healthy renewal | Stable usage, no open critical issues | STANDARD_RENEWAL |
| At-risk operations | Declining usage + open support issues | PROACTIVE_OUTREACH |
| Critical blocker | Renewal near + critical unresolved issue | ESCALATE_ACCOUNT |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Account renewal summary
- Health indicators
- Agent trace
- Recommended action
- Evidence/audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No autonomous commercial negotiation
- No pricing/discount approval
- No sensitive customer profiling

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

HEALTHY → standard path; DECLINING → outreach; CRITICAL_BLOCKER → escalation; MISSING_DATA → request data.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of account notes or support history into a concise explanation; deterministic renewal action remains rule-driven.

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

