---
path: plans/agentese-v3
status: active
progress: 70
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking:
  - plans/core-apps/the-gardener
enables:
  - plans/core-apps/the-gardener
  - plans/reactive-substrate-unification
session_notes: |
  CANONICAL PLAN for AGENTESE v3.
  Synthesizes v1 implementation, v2 draft, critiques, and philosophical foundations.
  Supersedes all previous evolution plans (archived to _archive/agentese-evolution-2025-12-15/).
  Spec: spec/protocols/agentese-v3.md

  2025-12-15: Phase 1 (Core API) COMPLETE
  - Added Observer base class with factory methods (guest, test, from_archetype, from_umwelt)
  - Added Logos.__call__() for cleaner syntax: await logos("path", observer)
  - Updated invoke() to accept Observer | Umwelt | None (defaults to guest)
  - Added @aspect decorator with category enforcement and Effect declarations
  - Added path() helper and UnboundComposedPath for string-based >> composition
  - All 941 tests passing (24 new v3 API tests)

  2025-12-15: Phase 2 (New Features) COMPLETE
  - Query system with bounds: query.py (QueryBuilder, QueryResult, bounds enforcement)
    - Pattern matching: ?world.*, ?*.*.manifest, ?self.memory.?
    - Pagination: limit (max 1000), offset
    - Capability checking, dry_run mode
    - 37 new tests
  - Alias registry: aliases.py (AliasRegistry, persistence to .kgents/aliases.yaml)
    - Prefix expansion: "me" -> "self.soul"
    - Shadowing prevention (can't alias context names)
    - Recursion prevention
    - Standard aliases (me, brain, chaos, forest, etc.)
    - 35 new tests
  - Subscription manager: subscription.py (SubscriptionManager, AgentesEvent, pattern matching)
    - Event types: INVOKED, CHANGED, ERROR, REFUSED, HEARTBEAT
    - Delivery modes: AT_MOST_ONCE, AT_LEAST_ONCE
    - Pattern matching with *, ** wildcards
    - Buffer management with backpressure
    - Context manager support
    - 34 new tests
  - Aspect pipelines: pipeline.py (AspectPipeline, PipelineResult)
    - Execute multiple aspects on same node
    - Fail-fast and collect-all modes
    - Duration tracking per stage
    - Fluent builder API
    - 17 new tests
  - Fixed associativity bug in UnboundComposedPath >> composition
  - Total test count: 1064 (Phase 1: 941 + Phase 2: 123)
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: in_progress
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: phase2_complete
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.10
  returned: 0.0
---

# AGENTESE v3: Implementation Plan

> *"Simplicity requires conviction."*

---

## I. Summary

AGENTESE v3 is the final synthesis of:
- v1 implementation learnings (559 tests)
- v2 draft innovations (envelope, effects)
- Critiques (bounds, semantics, migration)
- Philosophical foundations (category theory, phenomenology)

**Canonical Spec:** `spec/protocols/agentese-v3.md`

---

## II. Key Decisions

| Decision | Chosen | Rejected |
|----------|--------|----------|
| Path structure | `context.holon.aspect` | Flat verbs |
| Observer | Gradations (Observer → Umwelt) | Always full Umwelt |
| API surface | <50 exports | 150+ exports |
| Queries | Bounded (limit/offset) | Unbounded wildcards |
| Subscriptions | At-most-once default | Unspecified |
| Economics | Pre-charge with refund | Post-charge |
| Categories | Runtime enforced | Documentation only |

---

## III. Implementation Phases

### Phase 1: Core API ✅ COMPLETE

```
├── [✓] Add Logos.__call__ alongside .invoke()
├── [✓] Add Observer base class (with factory methods)
├── [✓] Add @aspect decorator with category enforcement
├── [✓] Add string-based >> composition (path() helper)
└── [✓] Keep v1 code working (backward compatible)
```

**Files:** `logos.py`, `node.py`, `affordances.py`
**Tests:** `_tests/test_v3_api.py` (24 tests)

### Phase 2: New Features ✅ COMPLETE

```
├── [✓] Implement query syntax with bounds
│       - QueryBuilder, QueryResult, QueryMatch
│       - Pattern matching: ?world.*, ?*.*.manifest, ?self.memory.?
│       - Bounds: limit (default 100, max 1000), offset, dry_run
│       - 37 tests
├── [✓] Implement alias registry
│       - AliasRegistry with prefix expansion
│       - Shadowing/recursion prevention
│       - Standard aliases (me, brain, chaos, forest)
│       - 35 tests
├── [✓] Add persistence (.kgents/aliases.yaml)
├── [✓] Implement subscription manager
│       - SubscriptionManager, Subscription, AgentesEvent
│       - Pattern matching with *, ** wildcards
│       - Event types: INVOKED, CHANGED, ERROR, REFUSED, HEARTBEAT
│       - Delivery modes: AT_MOST_ONCE, AT_LEAST_ONCE
│       - Buffer management with backpressure
│       - 34 tests
└── [✓] Implement aspect pipelines
        - AspectPipeline, PipelineResult, PipelineStageResult
        - Execute multiple aspects on same node
        - Fail-fast and collect-all modes
        - Duration tracking per stage
        - 17 tests
```

**Files:** `query.py` ✓, `aliases.py` ✓, `subscription.py` ✓, `pipeline.py` ✓
**Tests:** `_tests/test_query.py` (37), `_tests/test_aliases.py` (35), `_tests/test_subscription.py` (34), `_tests/test_pipeline.py` (17)

### Phase 3: CLI Integration (Week 5-6)

```
├── Wire hollow.py to use Logos
├── Add shortcut resolution
├── Add legacy command mapping
├── Add query/subscribe CLI commands
└── Add automatic OTEL tracing
```

**Files:** `hollow.py`, `shortcuts.py`, `legacy.py`, `observer.py`

### Phase 4: Migration (Week 7-8)

```
├── Mark v1 patterns deprecated
├── Emit deprecation warnings
├── Track v1 vs v3 usage
├── Delete deprecated code
└── Reduce __init__.py to <50 exports
```

**Files:** All `impl/claude/protocols/agentese/`

---

## IV. Success Metrics

### Quantitative

| Metric | v1 | v3 Target | Status |
|--------|----|----|--------|
| Public exports | 150+ | <50 | In Progress |
| Logos classes | 2 | 1 | 1 (unified) |
| Node types | 4 | 1 | In Progress |
| Test count | 559 | 600+ | **941** ✓ |
| Query latency | N/A | <10ms | Pending |
| Subscription delivery | N/A | <10ms | Pending |

### Qualitative

- [ ] `kg self.forest.manifest` works
- [ ] `kg /forest` works (shortcut)
- [ ] `kg forest` works (legacy)
- [ ] Composition with `>>` feels natural
- [ ] New contributor understands API in 10 minutes
- [ ] The Gardener works entirely through AGENTESE

---

## V. Blocking Relationships

```
agentese-v3 (this plan)
    │
    └─► plans/core-apps/the-gardener
        └─► Crown Jewel #7 (autopoietic dev interface)
```

The Gardener requires:
1. CLI as AGENTESE REPL ← Phase 3
2. Session management ← separate plan
3. Proactive proposals ← separate plan

---

## VI. Related Documents

| Document | Path | Relationship |
|----------|------|--------------|
| v3 Spec (canonical) | `spec/protocols/agentese-v3.md` | Source of truth |
| v1 Spec (reference) | `spec/protocols/agentese.md` | Historical reference |
| Archived evolution plans | `plans/_archive/agentese-evolution-2025-12-15/` | Superseded |
| The Gardener | `plans/core-apps/the-gardener.md` | Depends on this |

---

## VII. Open Questions

1. **Subscription buffer size:** Default 1000 events—sufficient?
2. **Alias shadowing:** Should user aliases override shortcuts?
3. **Effect rollback:** Strategy for failed writes?
4. **Federation:** When to prioritize?

---

*Last updated: 2025-12-15*
