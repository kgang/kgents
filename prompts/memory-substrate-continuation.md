# Memory Phase 5: Substrate Implementation Sprint

> *"The substrate is the commons; the crystal is the garden."*

## Context

RESEARCH phase complete. Types validated with 23 tests. Now ship.

**Completed**:
- `substrate.py` — SharedSubstrate, Allocation, CrystalPolicy (380 lines, mypy strict)
- Research questions answered: room size (1K default), promotion (dual-path), debris (human_label required)

**Validated Category Laws**:
- `promote >> demote ≅ id` (up to resolution loss)
- `usage ⊣ promotion` (adjunction)

## Sprint Directive

Execute phases **DEVELOP → IMPLEMENT → QA → TEST** in one session. Target: 60+ tests, full integration.

### DEVELOP: Sharpen Remaining Types

1. **Ghost Lifecycle Metadata** — Wire `LifecyclePolicy` into `GlassCacheManager`
2. **Auto-Consolidation** — Connect `CompactionTrigger` to `InferenceGuidedCrystal.consolidate()`
3. **Categorical Routing** — Wire `CategoricalRouter` to live `PheromoneField`

### IMPLEMENT: File Plan

```
impl/claude/agents/m/substrate.py        ✓ EXISTS
impl/claude/agents/m/routing.py          NEW — CategoricalRouter + Task type
impl/claude/agents/m/compaction.py       NEW — Compactor, AutoCompactionDaemon
impl/claude/infra/ghost/lifecycle.py     NEW — LifecycleAwareCache
impl/claude/agents/m/_tests/test_routing.py
impl/claude/agents/m/_tests/test_compaction.py
impl/claude/infra/ghost/_tests/test_lifecycle.py
```

### QA Checklist

- [ ] All types have docstrings with categorical insights
- [ ] LifecyclePolicy.human_label enforced everywhere
- [ ] No orphaned allocations (cleanup on agent removal)
- [ ] CrystalPolicy logs promotion decisions
- [ ] Mypy strict: 0 errors
- [ ] Ruff: 0 warnings

### TEST: Targets

| Category | Target | Focus |
|----------|--------|-------|
| Unit: Routing | 15 | gradient following, adjoint property |
| Unit: Compaction | 10 | triggers, auto-consolidation |
| Unit: Lifecycle | 10 | TTL, expiration, ghost integration |
| Integration | 15 | allocate → use → compact → route |
| Property | 10 | categorical laws, naturality |

### Property Tests (Required)

```python
def test_routing_naturality():
    """route(f(task)) = f(route(task)) for morphism f"""

def test_deposit_route_adjunction():
    """deposit ⊣ route: gradients created = routes followed"""

def test_compaction_preserves_resolution_ordering():
    """hot patterns stay hotter than cold after compaction"""
```

## Entropy Budget

- **Sip**: 0.07 for exploration (serendipitous naming, poetic identifiers)
- **Pourback**: Unused exploration → next phase
- **Tithe**: If blocked, pay gratitude and pivot

## Exit Criteria

- [ ] 60+ new tests passing
- [ ] CategoricalRouter routes via live PheromoneField
- [ ] Ghost cache has lifecycle metadata
- [ ] Auto-compaction fires on pressure threshold
- [ ] `m/__init__.py` exports all new types

## Invocation

```
/hydrate

Continue Memory Phase 5. RESEARCH complete. Execute DEVELOP → TEST.
Ship the substrate. Be ambitious. 60+ tests. Full integration.
```

---

*"The river that knows its course flows without thinking."*
