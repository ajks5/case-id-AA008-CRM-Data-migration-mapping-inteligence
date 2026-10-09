# AA028 — Invoice Exception Resolution Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA028` |
| Domain | Finance Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Invoice Exception Resolution Intelligence**

## 2. Business Problem

Accounts-payable teams need to route invoice exceptions consistently based on purchase-order match, amount variance, tax fields, vendor reference, and duplicate indicators.

## 3. Primary Users / Actors

- Accounts payable analyst
- Finance operations lead
- Procurement coordinator

## 4. MVP Objective

Recommend an administrative exception-resolution path. The MVP does not authorize payment.

## 5. Business Input

Invoice record with vendor, PO reference, invoice amount, PO amount, tax fields, invoice number/date, duplicate key, and receipt status.

## 6. Expected Final Output / Recommendation

Recommended action: READY_FOR_REVIEW / PO_MISMATCH / AMOUNT_VARIANCE / TAX_REVIEW / DUPLICATE_REVIEW / REQUEST_INFO.

## 7. Domain Data Required

- Invoice records
- Purchase orders
- Receipts
- Tolerance rules
- Vendor master

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Invoice Intake Agent | Validates invoice and vendor/PO references. | `invoice` | `validated_invoice` |
| PO Match Agent | Checks PO and receipt alignment. | `validated_invoice + PO + receipts` | `match_status` |
| Variance Agent | Calculates amount/tolerance variance. | `validated_invoice + tolerance_rules` | `variance_status` |
| Tax & Duplicate Agent | Checks required tax fields and duplicate keys. | `validated_invoice + history` | `tax_flags, duplicate_flags` |
| Invoice Resolution Decision Agent | Routes the exception for human review. | `all agent outputs` | `final_recommendation` |

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
- `invoice`
- `validated_invoice`
- `match_status`
- `variance_status`
- `tax_flags`
- `duplicate_flags`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Potential duplicate → DUPLICATE_REVIEW.
2. Missing/invalid PO/receipt match → PO_MISMATCH.
3. Amount outside configured tolerance → AMOUNT_VARIANCE.
4. Tax field issue → TAX_REVIEW.
5. All checks pass → READY_FOR_REVIEW.
6. Never authorize or execute payment.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Apply duplicate and mandatory-match blockers first, then variance/tax checks, and return the primary route plus evidence.

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
| Clean invoice | Match and tolerance pass | READY_FOR_REVIEW |
| Amount mismatch | Variance exceeds tolerance | AMOUNT_VARIANCE |
| Potential duplicate | Duplicate key found | DUPLICATE_REVIEW |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Invoice summary
- Match/variance panels
- Agent trace
- Resolution recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No payment approval
- No bank integration
- No tax advice
- No autonomous accounting posting

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

DUPLICATE → duplicate review; PO_FAIL → mismatch; VARIANCE → amount review; TAX_FLAG → tax review; CLEAN → ready.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional extraction/summarization of non-authoritative invoice notes or explanation generation. Matching and tolerance logic remain deterministic.

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

