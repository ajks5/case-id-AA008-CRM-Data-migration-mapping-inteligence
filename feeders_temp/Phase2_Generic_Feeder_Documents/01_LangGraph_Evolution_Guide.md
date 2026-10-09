# RealRails Batch 2 — LangGraph Evolution Guide
## Purpose

Use this guide for Phase 2.1 and 2.2.

The application already works.

LangGraph is introduced to evolve **orchestration**, not to replace the Product Bible or rewrite working domain logic.

---

# 1. Migration Principle

Use this mapping:

```text
Existing Agent / Service
        ↓
LangGraph Node

Existing Run-Scoped Shared Workflow Context
        ↓
Graph State

Existing Sequential Orchestrator
        ↓
StateGraph

Existing Decision Service
        ↓
Decision Node

Existing Explanation + Audit
        ↓
Final Node(s)
```

Preserve existing behavior first.

---

# 2. Graph State

The graph state should represent the data already required by the working application.

Typical shape:

```text
workflow_id
business_input
validated_input
shared_context
agent_outputs
routing_status
final_recommendation
explanation
audit_reference
errors
```

Case-specific fields may be added only when they already belong to the Product Bible/implementation.

Do not invent "memory" fields simply because LangGraph is being used.

---

# 3. Node Design

A LangGraph node should:

- perform one meaningful step
- read only required state
- call/reuse existing domain logic where practical
- return explicit state updates
- preserve traceability

Prefer wrapping existing agents/services rather than rewriting them.

---

# 4. Phase 2.1 — Linear Graph

Start with:

```text
START
  ↓
Context / Validation
  ↓
Agent A
  ↓
Agent B
  ↓
Agent C
  ↓
Decision
  ↓
Explanation / Audit
  ↓
END
```

The goal is to learn:

- graph state
- nodes
- state updates
- graph compilation
- graph invocation
- execution trace

Do not add branching yet.

---

# 5. Preserve API/UI

Where practical:

```text
Existing API Endpoint
        ↓
LangGraph Invocation
        ↓
Same Structured Response
```

This avoids unnecessary frontend rewrites.

---

# 6. Phase 2.2 — Conditional Routing

Only add routes that correspond to real Product Bible conditions.

A router should use deterministic state values, for example:

```python
if state["missing_fields"]:
    return "request_more_info"

if state["risk_score"] >= HIGH_RISK_THRESHOLD:
    return "human_review"

return "continue"
```

This is illustrative only.

Use case-specific fields and rules.

---

# 7. Good Routing Characteristics

A good route is:

- domain-relevant
- deterministic
- easy to explain
- easy to test
- based on existing state
- reflected in explanation/audit

Avoid a graph with many branches merely to look advanced.

---

# 8. Route Contract

For every route define:

| Field | Meaning |
|---|---|
| Route Name | Stable internal route |
| Condition | Exact deterministic test |
| Reads | Graph-state fields used |
| Destination | Next node |
| Outcome | Business effect |
| Evidence | What is logged/explained |

---

# 9. Traceability

Record enough to show:

```text
workflow_id
node entered
node completed
important output
route evaluated
route selected
final result
```

Simple application logging or a workflow trace is sufficient for the internship.

Do not introduce a separate observability platform unless genuinely useful.

---

# 10. Validation

## Linear

Validate:

- graph compiles
- nodes run in expected order
- state updates correctly
- final result matches Phase 1 behavior

## Conditional

Validate:

- normal route
- alternate route
- route condition
- destination node
- final result
- explanation/audit

---

# 11. Do Not Add Yet

During Posts 2.1 and 2.2 do not add:

- LLM calls
- RAG
- vector database
- MCP
- knowledge graph
- long-term memory

Post 2.3 will introduce one controlled LLM enhancement.
