# AA023 — Retail Stock Transfer Recommendation Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA023` |
| Domain | Retail Operations |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Retail Stock Transfer Recommendation Intelligence**

## 2. Business Problem

Multi-store retailers need consistent recommendations for transferring stock between locations when one store is overstocked and another is at risk of stockout.

## 3. Primary Users / Actors

- Retail operations planner
- Store manager
- Inventory coordinator

## 4. MVP Objective

Recommend internal stock-transfer actions using deterministic stock, demand, distance band, and minimum-stock rules.

## 5. Business Input

SKU-by-store snapshot with on-hand, safety stock, recent demand rate, open inbound quantity, transfer eligibility, and inter-store distance band.

## 6. Expected Final Output / Recommendation

Recommended action: NO_TRANSFER / TRANSFER / REPLENISH_EXTERNALLY / REVIEW_DATA, with source store, destination store, and quantity.

## 7. Domain Data Required

- Store inventory
- Demand rates
- Safety stock
- Inbound POs
- Transfer eligibility/distance bands

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Stock Intake Agent | Validates SKU/store inventory fields. | `store_stock` | `validated_stock` |
| Deficit Agent | Identifies destination stores below projected minimum. | `validated_stock + demand` | `deficit_stores` |
| Surplus Agent | Identifies source stores with transferable surplus above safety stock. | `validated_stock` | `surplus_stores` |
| Transfer Feasibility Agent | Matches eligible source/destination pairs and quantity limits. | `deficit + surplus + distance` | `transfer_options` |
| Transfer Decision Agent | Ranks transfer options and recommends action. | `all agent outputs` | `final_recommendation` |

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
- `store_stock`
- `validated_stock`
- `deficit_stores`
- `surplus_stores`
- `transfer_options`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Never reduce source below safety stock.
2. Account for open inbound quantity before creating deficit.
3. Only allow approved transfer pairs/distance bands.
4. If no safe internal source exists → REPLENISH_EXTERNALLY.
5. Invalid stock data → REVIEW_DATA.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Calculate deficits and safe surpluses, generate feasible pairs, then rank by quantity coverage and distance band.

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
| Internal balance | One surplus store can cover deficit | TRANSFER |
| No source surplus | All stores near minimum | REPLENISH_EXTERNALLY |
| Bad data | Missing safety-stock value | REVIEW_DATA |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Store/SKU matrix
- Deficit/surplus panels
- Transfer options
- Agent trace
- Recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No automatic inventory transfer posting
- No supplier purchasing
- No demand forecasting beyond provided rates

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

DATA_ERROR → review; FEASIBLE_TRANSFER → transfer path; NO_SOURCE → external replenishment; NO_DEFICIT → no transfer.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional explanation generation or interpretation of non-critical store notes. Transfer feasibility remains deterministic.

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

