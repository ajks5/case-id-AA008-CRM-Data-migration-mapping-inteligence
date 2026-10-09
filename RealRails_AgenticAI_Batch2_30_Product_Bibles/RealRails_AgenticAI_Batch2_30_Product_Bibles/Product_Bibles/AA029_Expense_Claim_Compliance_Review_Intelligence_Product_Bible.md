# AA029 — Expense Claim Compliance Review Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA029` |
| Domain | Finance Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Expense Claim Compliance Review Intelligence**

## 2. Business Problem

Expense teams need a transparent pre-review of claims against category limits, receipt requirements, date rules, duplicates, and policy exceptions.

## 3. Primary Users / Actors

- Expense operations analyst
- Finance reviewer
- Employee support desk

## 4. MVP Objective

Recommend a policy-review route without approving reimbursement or making employment decisions.

## 5. Business Input

Expense claim with category, amount, date, receipt status, merchant reference, project/cost center, duplicate key, and exception justification status.

## 6. Expected Final Output / Recommendation

Recommended action: READY_FOR_REVIEW / RECEIPT_REQUIRED / LIMIT_REVIEW / DUPLICATE_REVIEW / POLICY_EXCEPTION / REQUEST_INFO.

## 7. Domain Data Required

- Expense policy limits
- Receipt thresholds
- Date rules
- Historical claim keys
- Allowed categories

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Expense Intake Agent | Validates category, amount, date, and required metadata. | `expense_claim` | `validated_claim` |
| Receipt Agent | Checks receipt requirements by amount/category. | `validated_claim + policy` | `receipt_status` |
| Limit & Date Agent | Checks configured policy limits and allowed date windows. | `validated_claim + policy` | `limit_flags, date_flags` |
| Duplicate & Exception Agent | Checks duplicate indicators and declared exception path. | `validated_claim + history` | `duplicate_flags, exception_status` |
| Expense Review Decision Agent | Routes the claim for human review. | `all agent outputs` | `final_recommendation` |

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
- `expense_claim`
- `validated_claim`
- `receipt_status`
- `limit_flags`
- `date_flags`
- `duplicate_flags`
- `exception_status`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Potential duplicate → DUPLICATE_REVIEW.
2. Required receipt missing → RECEIPT_REQUIRED.
3. Amount/date outside policy → LIMIT_REVIEW or POLICY_EXCEPTION.
4. Missing category/cost center → REQUEST_INFO.
5. Policy-compliant claim → READY_FOR_REVIEW.
6. No automated reimbursement approval.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply duplicate/receipt blockers first, then policy limits and exception route.

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
| Compliant claim | Within limit, receipt present | READY_FOR_REVIEW |
| Missing receipt | Receipt required but absent | RECEIPT_REQUIRED |
| Policy exception | Declared exception + out-of-policy amount | POLICY_EXCEPTION |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Expense claim
- Policy checks
- Agent trace
- Review route
- Evidence/audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No reimbursement approval
- No payroll action
- No employee performance or disciplinary scoring

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

DUPLICATE → duplicate review; RECEIPT_MISSING → receipt path; POLICY_EXCEPTION → exception review; CLEAN → ready.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of exception justification for reviewers. Deterministic policy checks remain authoritative.

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

