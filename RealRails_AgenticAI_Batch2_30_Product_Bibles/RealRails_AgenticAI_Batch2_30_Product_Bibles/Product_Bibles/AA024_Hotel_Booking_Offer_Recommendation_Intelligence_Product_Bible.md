# AA024 — Hotel Booking Offer Recommendation Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA024` |
| Domain | Hospitality & Travel |
| Complexity | Medium |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Hotel Booking Offer Recommendation Intelligence**

## 2. Business Problem

A hotel booking platform needs to rank available property/room offers against guest requirements, policy constraints, budget, and availability.

## 3. Primary Users / Actors

- Booking customer
- Reservation support agent
- Property operations reviewer

## 4. MVP Objective

Recommend suitable booking offers using deterministic matching and scoring before optional LLM assistance.

## 5. Business Input

Stay request with destination, dates, guest count, room needs, budget band, cancellation preference, amenities, and accessibility requirements explicitly provided by the user.

## 6. Expected Final Output / Recommendation

Ranked offers: RECOMMENDED / ALTERNATE / NO_MATCH / REQUEST_INFO, with price, policy fit, reasons, and evidence.

## 7. Domain Data Required

- Seeded properties/room types
- Availability
- Price rules
- Cancellation rules
- Amenity metadata

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Stay Intent Agent | Validates and normalizes the booking request. | `stay_request` | `validated_intent` |
| Availability Agent | Finds available room/property options. | `validated_intent + inventory` | `available_offers` |
| Policy & Price Agent | Evaluates price and cancellation-policy fit. | `available_offers + preferences` | `policy_price_scores` |
| Amenity & Fit Agent | Scores room capacity and explicitly requested amenities. | `available_offers + preferences` | `fit_scores` |
| Booking Offer Decision Agent | Ranks valid offers and returns recommendation. | `all agent outputs` | `final_recommendation` |

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
- `stay_request`
- `validated_intent`
- `available_offers`
- `policy_price_scores`
- `fit_scores`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Guest count must fit room capacity.
2. Unavailable inventory is excluded.
3. Budget and cancellation preference use fixed scoring bands.
4. Explicit accessibility requirements are hard constraints when provided.
5. If no valid offer exists → NO_MATCH.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Filter hard constraints, then rank remaining offers using fixed weighted score across price, policy, and requested fit.

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
| Clear match | Several valid rooms, one best fit | RECOMMENDED |
| Budget conflict | Valid inventory but above budget | ALTERNATE |
| No availability | No room fits dates/guest count | NO_MATCH |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Search form
- Offer ranking
- Score/evidence panel
- Agent trace
- Recommendation
- Audit

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No real booking payment
- No discriminatory pricing
- No inference of sensitive guest attributes

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

VALID_OFFERS → ranking; NO_AVAILABILITY → no-match; HARD_CONSTRAINT_FAIL → alternate/no-match; MISSING_INPUT → request info.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional parsing of free-text travel preferences into structured non-sensitive fields or explanation generation. Availability and ranking rules remain deterministic.

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

