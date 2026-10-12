# AA008 — CRM Data Migration Mapping Intelligence
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.  
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.  
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA008` |
| Domain | Data & Integration |
| Complexity | Advanced |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**CRM Data Migration Mapping Intelligence**

## 2. Business Problem

Different source CRM schemas must be mapped into a standard destination schema while handling column mismatches, data types, missing fields, and relationship differences.

## 3. Primary Users / Actors

- Migration analyst
- Data engineer
- CRM implementation lead

## 4. MVP Objective

Recommend source-to-target mappings, transformation actions, and review items using deterministic schema rules first.

## 5. Business Input

Source schema, destination schema, sample rows, relationship metadata, and optional known mapping hints.

## 6. Expected Final Output / Recommendation

Per-field mapping recommendation: DIRECT_MAP / TRANSFORM / DEFAULT / UNMAPPED / REVIEW, with confidence and evidence.

## 7. Domain Data Required

- Source schema metadata
- Destination schema metadata
- Sample data profiles
- Transformation rule library
- Known mapping aliases

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Schema Analyzer Agent | Profiles tables, columns, types, keys, and relationships. | `source_schema + destination_schema` | `schema_profile` |
| Field Mapping Agent | Matches candidate source and target fields using deterministic aliases/type rules. | `schema_profile + aliases` | `mapping_candidates` |
| Transformation Agent | Determines required casts, defaults, normalizations, or derived transforms. | `mapping_candidates + samples` | `transformation_plan` |
| Validation Agent | Checks required target coverage, type compatibility, and relationship integrity. | `mapping_plan + target_constraints` | `validation_results` |
| Migration Decision Agent | Produces approved mappings and explicit review items. | `all agent outputs` | `final_recommendation` |

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
- `source_schema`
- `destination_schema`
- `schema_profile`
- `mapping_candidates`
- `transformation_plan`
- `validation_results`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Exact normalized-name + compatible type → DIRECT_MAP.
2. Known alias + compatible type → DIRECT_MAP with evidence.
3. Type-convertible fields → TRANSFORM.
4. Required target field without valid source/default → REVIEW.
5. Never silently drop relationship or required-field conflicts.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Select highest-confidence deterministic mapping candidate, attach transformation if required, and route ambiguous/low-confidence mappings to human review.

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
| Simple schema | Mostly matching names/types | High direct-map coverage |
| Naming mismatch | Alias-based mappings required | DIRECT_MAP + evidence |
| Relationship mismatch | Target relationship cannot be safely derived | REVIEW |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Schema upload/selection
- Mapping table
- Confidence/evidence
- Transformation plan
- Validation summary
- Audit trail

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No production database writes in MVP
- No silent destructive migration
- No claim of 100% autonomous schema migration

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

HIGH_CONFIDENCE → accept mapping; TRANSFORM_REQUIRED → transform branch; LOW_CONFIDENCE → review; REQUIRED_FIELD_MISSING → block/resolve.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional semantic assistance for ambiguous field-name matching or transformation explanation. Deterministic type/constraint validation remains authoritative.

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

