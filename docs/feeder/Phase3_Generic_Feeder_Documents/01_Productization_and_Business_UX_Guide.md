# RealRails Batch 2 — Productization & Business UX Guide
## Purpose

Use this guide for Phase 3.1.

The Agentic AI is already complete.

This phase improves how the **business user experiences the application**.

---

# 1. Productization Principle

Move from:

```text
Technical Demo
→ Internal Agent Details
→ Raw Recommendation
```

to:

```text
Business Workflow
→ Clear Input
→ Clear Recommendation
→ Evidence
→ Next Action
```

Keep the technical internals available, but not as the primary experience.

---

# 2. Product Bible Still Controls the Domain

The Product Bible defines:

- product purpose
- users
- business input
- business output
- agents
- rules
- expected UI
- boundaries

Productization must not change the domain.

---

# 3. Primary Business Experience

The main workflow should answer:

1. What can I do here?
2. What information do I need to provide?
3. What happened?
4. What is the recommendation?
5. Why?
6. What should I do next?

---

# 4. Recommended Product Pages

Choose only what fits the Product Bible:

- Home / Dashboard
- New Request / New Case
- Recommendation / Result
- Review / Action
- History / Recent Cases
- Explainability / Advanced View
- Audit / Trace
- Configuration

Do not build every page for every project.

---

# 5. Hide Technical Complexity from Normal Users

Normal users should not be forced to understand:

- graph state
- node implementation
- LLM provider
- raw JSON
- Python class names
- internal route names

These can appear in an optional advanced view.

---

# 6. Preserve Explainability

Do not remove:

- agent contribution
- triggered rules
- evidence
- recommendation reasoning
- audit reference

Instead, present them more clearly.

Example:

```text
Recommendation: PRIORITY_REVIEW

Why:
- SLA threshold breached
- High service impact
- Repeated exception

Advanced Details:
- Agent trace
- Graph route
- Shared context
- Audit ID
```

---

# 7. UX Quality

Prefer:

- clear labels
- concise text
- visible status
- useful empty states
- useful validation messages
- consistent navigation
- readable result cards
- domain-specific terminology
- responsive layout

Avoid:

- decorative complexity
- large animations
- generic AI-chat interface
- excessive technical dashboards

---

# 8. Persistence

Add simple persistence only if it improves the product.

Examples:

- recent cases
- review history
- configuration
- audit lookup

SQLite or the existing simple database is sufficient for the internship.

Do not introduce heavy infrastructure just for Phase 3.

---

# 9. Role-Based Views

Add roles only when the Product Bible benefits from them.

Simple examples:

```text
Operator → Submit / View Result
Reviewer → Review / Approve / Escalate
Admin → Configuration / Audit
```

Do not build enterprise IAM unless explicitly required.

---

# 10. Completion Check

- [ ] primary business workflow is obvious
- [ ] forms use domain language
- [ ] recommendation is clear
- [ ] next action is clear
- [ ] explanation/evidence remains available
- [ ] technical trace remains accessible
- [ ] no important Phase 2 behavior was broken
- [ ] UI is reasonably responsive
- [ ] no unnecessary feature expansion
