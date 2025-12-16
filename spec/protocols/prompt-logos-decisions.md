# Prompt Logos: Architectural Decision Record

> *Decisions made during the critical revision of prompt-logos.md (v0.1 → v0.2)*

**Date:** 2025-12-16
**Status:** Accepted
**Context:** spec/protocols/prompt-logos.md revision
**Supersedes:** N/A

---

## ADR-PL-001: Context Namespace (`concept.prompt.*` over `prompt.*`)

### Status
**ACCEPTED**

### Context
The original v0.1 spec proposed adding a sixth AGENTESE context (`prompt.*`). This would be the first context addition since the protocol's inception and violates the explicit 5-context limit in `spec/principles.md`.

### Decision
Prompt Logos uses `concept.prompt.*` within the existing `concept.*` context.

### Rationale
1. **Principle alignment**: The Tasteful principle explicitly limits contexts to five
2. **Conceptual fit**: Prompts are abstract structures (concepts) that can be instantiated
3. **Precedent**: Evergreen already uses `concept.prompt.*` paths
4. **Parsimony**: Adding contexts sets precedent for future proliferation

### Consequences
- **Positive**: Maintains protocol integrity; no AGENTESE spec change required
- **Negative**: Longer paths (`concept.prompt.task.X` vs `prompt.task.X`)
- **Mitigation**: Slash command shortcuts (`/prompt` → `concept.prompt.*`)

---

## ADR-PL-002: Phase-Gated Implementation

### Status
**ACCEPTED**

### Context
The v0.1 spec presented all features (registry, self-improvement, meta-prompts, observer-dependent rendering) as a single vision without implementation ordering.

### Decision
Implement Prompt Logos in four phases with increasing complexity:

| Phase | Scope | Dependency |
|-------|-------|------------|
| 1 (MVP) | Registry + basic types | None |
| 2 | TextGRAD + rigidity | Phase 1 |
| 3 | Meta-prompts + halting | Phase 2 |
| 4 | Observer-dependent + composition | Phase 3 |

### Rationale
1. **Risk mitigation**: Earlier phases prove value before investing in complexity
2. **Tasteful scoping**: "Say 'no' more than 'yes'" applies to features too
3. **Incremental value**: Each phase is useful independently

### Consequences
- **Positive**: Clear implementation roadmap; defer speculative features
- **Negative**: Some v0.1 features delayed
- **Mitigation**: Phase boundaries can be adjusted based on learnings

---

## ADR-PL-003: Rigidity is Earned, Not Declared

### Status
**ACCEPTED**

### Context
The Evergreen spec defines rigidity (0.0-1.0) as a parameter controlling how much a prompt resists change. The question: who sets these values?

### Decision
Rigidity is **computed from provenance**, not manually declared:

```python
rigidity = f(age, authority, stability, explicit_lock)
```

Factors:
- **Age**: Older prompts resist change more (0-0.2)
- **Authority**: Core team prompts are more rigid (0-0.2)
- **Stability**: High success rate → more rigid (0-0.1)
- **Lock**: Explicit human override (→1.0)

### Rationale
1. **Ethical principle**: Avoids arbitrary authority; decisions are traceable
2. **Self-correcting**: Poorly-performing prompts naturally become more mutable
3. **Transparent**: Formula is documented and auditable

### Consequences
- **Positive**: Democratic governance; data-driven decisions
- **Negative**: New prompts start with moderate rigidity (0.5)
- **Mitigation**: Explicit `lock()` for prompts requiring immediate stability

---

## ADR-PL-004: Meta-Prompt Halting Safeguards

### Status
**ACCEPTED**

### Context
Meta-prompts can improve themselves. Without safeguards, this creates potential for infinite recursion or runaway drift.

### Decision
Four safeguards:

1. **Recursion limit**: MAX_META_RECURSION = 3
2. **Cooldown**: Same prompt cannot improve twice within 1 hour
3. **Convergence detection**: Halt if <5% change
4. **Human-in-loop**: Meta-meta changes require approval

### Rationale
1. **Ethical principle**: Preserve human oversight over self-modification
2. **Practical**: Prevents resource exhaustion
3. **Testable**: Each safeguard has clear acceptance criteria

### Consequences
- **Positive**: Safe self-improvement within bounds
- **Negative**: Limits potential for radical self-improvement
- **Mitigation**: Safeguard parameters can be tuned with experience

---

## ADR-PL-005: Differentiation from Evergreen

### Status
**ACCEPTED**

### Context
The v0.1 spec didn't clearly articulate why Prompt Logos is needed when Evergreen already exists.

### Decision
Explicit value proposition:

> **Evergreen cultivates ONE garden (CLAUDE.md). Prompt Logos cultivates a FOREST of prompts with the same categorical guarantees.**

Key differentiators:
- Agent prompts
- Task templates
- Cross-prompt inheritance
- Semantic registry/search
- Meta-prompts

### Rationale
1. **Tasteful principle**: Every agent must answer "why does this need to exist?"
2. **Clarity**: Prevents confusion about system boundaries
3. **Composition**: Evergreen becomes a special case, not replaced

### Consequences
- **Positive**: Clear mental model; Evergreen preserved
- **Negative**: Two systems to maintain (though unified)
- **Mitigation**: Shared PromptM monad, TextGRAD, rollback infrastructure

---

## ADR-PL-006: Observer-Dependent Prompts Deferred to Phase 4

### Status
**ACCEPTED**

### Context
The v0.1 spec proposed prompts that render differently based on observer (junior vs senior developer). This is the AGENTESE principle applied to prompts.

### Decision
Defer observer-dependent prompt rendering to Phase 4.

### Rationale
1. **Unclear semantics**: What does "junior developer perceives a different code review prompt" actually mean?
2. **Infrastructure ready**: Umwelt, affordances exist; semantics don't
3. **Risk mitigation**: Prove core value (Phase 1-3) before adding complexity

### Consequences
- **Positive**: Focus on well-understood features first
- **Negative**: Delays potentially powerful capability
- **Mitigation**: Phase 4 can be accelerated if demand emerges

---

## Summary

| ADR | Decision | Principle |
|-----|----------|-----------|
| PL-001 | `concept.prompt.*` | Tasteful |
| PL-002 | Phase-gated rollout | Curated |
| PL-003 | Earned rigidity | Ethical |
| PL-004 | Halting safeguards | Ethical |
| PL-005 | Forest vs Garden | Tasteful |
| PL-006 | Observer semantics deferred | Curated |

---

*Created during spec/protocols/prompt-logos.md revision: v0.1 → v0.2*
