---
path: plans/agentese-v3-crown-synergy-audit
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/agentese-v3
  - plans/core-apps-synthesis
session_notes: |
  Created per Kent's request to audit Crown Jewel synergies with AGENTESE v3.
  To be executed AFTER agentese-v3 spec is fully implemented.
phase_ledger:
  PLAN: complete
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.02
  returned: 0.0
---

# Crown Jewels ↔ AGENTESE v3 Synergy Audit

> *"The best protocol is the one that disappears."* — AGENTESE v3 Epigraph
>
> *"Each jewel stresses a meta-framework; v3 unifies how they speak."*

This plan audits each Crown Jewel for synergies to realize when AGENTESE v3 is fully implemented. Execute this audit AFTER v3 Phase 3 (CLI Integration) is complete.

---

## I. Executive Summary

### AGENTESE v3 Capabilities to Audit

| v3 Feature | Spec Section | Crown Impact |
|------------|--------------|--------------|
| **Logos.__call__()** | §13.1 | All jewels: simpler invocation |
| **Observer gradations** | §4.2 | Punchdrunk, Domain: holographic perception |
| **Query syntax** | §8 | Brain, Gestalt: bounded discovery |
| **Subscriptions** | §9 | Atelier, Coalition: real-time streaming |
| **Path aliases** | §10 | Gardener: ergonomic shortcuts |
| **String-based >>** | §11 | Coalition, Forge: pipeline composition |
| **Aspect categories** | §7 | All jewels: runtime safety |
| **Declared effects** | §6 | Domain: audit compliance |
| **Envelope** | §5 | Enterprise: tracing + tenancy |
| **CLI as REPL** | §12 | Gardener: autopoietic dev |

### Synergy Heat Map

```
                    v3 Feature
Jewel           Call  Obs  Query  Sub  Alias  >>  Cat  Eff  Env  CLI
─────────────────────────────────────────────────────────────────────
Atelier          ●    ○     ○     ●     ○    ●    ●    ●    ●    ○
Coalition        ●    ○     ●     ●     ○    ●    ●    ●    ●    ○
Brain            ●    ●     ●     ●     ●    ○    ●    ○    ●    ●
Punchdrunk       ●    ●     ○     ●     ○    ○    ●    ●    ●    ○
Domain           ●    ●     ●     ●     ○    ●    ●    ●    ●    ○
Gestalt          ●    ●     ●     ●     ●    ○    ●    ○    ●    ●
Gardener         ●    ○     ●     ●     ●    ●    ●    ●    ●    ●
─────────────────────────────────────────────────────────────────────
● = High synergy    ○ = Moderate synergy    (blank) = Low synergy
```

---

## II. Per-Jewel Synergy Analysis

### 2.1 Atelier Experience Platform

**Current AGENTESE Usage**: `atelier.session.start`, `atelier.studio.perturb`, `atelier.artifact.acquire`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Subscriptions** | Spectators subscribe to builder stream | `logos.subscribe("world.atelier.studio.*")` |
| **String >>** | Artifact → Crystal pipeline | `"atelier.artifact.create" >> "self.memory.engram"` |
| **Effects** | Token charges declared | `@aspect(effects=[Effect.CHARGES("tokens")])` |
| **Envelope** | Per-session tracing | Trace ID correlates spectator bids to artifacts |

**Audit Checklist**:
- [ ] Wire `SpectatorPool.watch()` to v3 subscription manager
- [ ] Replace direct `TokenPool` calls with `Effect.CHARGES`
- [ ] Add `atelier.studio.flux` subscription path
- [ ] Test: spectator bids trigger subscription events
- [ ] Verify: artifact creation pipeline composes via `>>`

**Estimated Synergy Lift**: 25% reduction in custom streaming code

---

### 2.2 Coalition Forge

**Current AGENTESE Usage**: `forge.task.create`, `forge.coalition.propose`, `forge.task.execute`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Query syntax** | Discover available citizens | `logos.query("?world.town.citizen.*")` |
| **Subscriptions** | Task progress stream | `logos.subscribe("forge.task.{id}.*")` |
| **String >>** | Task chaining | `"forge.task.research" >> "forge.task.content"` |
| **Effects** | Credit charges per stage | Effects compose additively |
| **Categories** | Formation = COMPOSITION | Runtime enforcement of composition rules |

**Audit Checklist**:
- [ ] Replace custom citizen discovery with `logos.query()`
- [ ] Wire `TaskExecutor` progress to subscription manager
- [ ] Implement task chaining via v3 composition semantics
- [ ] Add `@aspect(category=AspectCategory.COMPOSITION)` to formation
- [ ] Test: effects sum correctly across pipeline stages

**Estimated Synergy Lift**: 30% reduction in orchestration code

---

### 2.3 Holographic Second Brain

**Current AGENTESE Usage**: `self.memory.capture`, `self.memory.crystal.manifest`, `self.memory.cartography.manifest`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Observer gradations** | Lightweight recall | `Observer(archetype="browser")` for quick lookups |
| **Query syntax** | Crystal discovery | `logos.query("?self.memory.crystal.*", limit=20)` |
| **Subscriptions** | Ghost surfacing | `logos.subscribe("self.memory.ghost.*")` |
| **Aliases** | Personal shortcuts | `logos.alias("brain", "self.memory")` |
| **CLI REPL** | Direct capture | `kg brain.capture "note text"` |

**Audit Checklist**:
- [ ] Implement `Observer.browser()` for minimal context lookups
- [ ] Wire `GhostNotifier` to subscription manager
- [ ] Add bounded query for cartography exploration
- [ ] Create default aliases: `brain`, `memory`, `crystals`
- [ ] Test: ghost events delivered via subscription < 10ms

**Estimated Synergy Lift**: 40% simplification of M-gent API surface

---

### 2.4 Punchdrunk Park

**Current AGENTESE Usage**: `punchdrunk.scenario.start`, `punchdrunk.inhabit`, `punchdrunk.consent.force`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Observer gradations** | Holographic perception | `Umwelt(archetype="architect")` vs `Umwelt(archetype="poet")` |
| **Subscriptions** | Consent debt stream | `logos.subscribe("punchdrunk.consent.*")` |
| **Effects + Refusal** | Force mechanic | `Effect.FORCES` + `Refusal` type |
| **Categories** | INHABIT = MUTATION | Runtime enforcement of consent checks |
| **Envelope** | Session correlation | All actions traced to scenario run |

**Audit Checklist**:
- [ ] Implement full `Umwelt` for each scenario archetype
- [ ] Wire consent ledger to subscription manager
- [ ] Replace custom force logic with `Effect.FORCES` declaration
- [ ] Add `Refusal` responses for citizen counter-proposals
- [ ] Test: different observers see different `world.town.manifest`

**Estimated Synergy Lift**: 35% reduction in consent tracking code

---

### 2.5 Domain Simulation

**Current AGENTESE Usage**: `domain.sim.start`, `domain.scenario.define`, `domain.audit.emit`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Observer gradations** | Domain expertise views | `Umwelt(archetype="crisis_commander")` |
| **Query syntax** | Scenario discovery | `logos.query("?domain.{vertical}.scenario.*")` |
| **Effects** | Audit logging | `Effect.AUDITS("decision_rationale")` |
| **Envelope** | Enterprise tracing | Tenant ID + trace ID in every invocation |
| **String >>** | Drill → Report pipeline | `"domain.drill.execute" >> "domain.report.generate"` |

**Audit Checklist**:
- [ ] Define `Umwelt` per crisis role (commander, analyst, executive)
- [ ] Wire `SpanEmitter` through v3 envelope tracing
- [ ] Add `Effect.AUDITS` to all decision aspects
- [ ] Implement bounded queries per tenant
- [ ] Test: drill completion generates correlated audit trail

**Estimated Synergy Lift**: 50% compliance code consolidation

---

### 2.6 Gestalt Architecture Visualizer

**Current AGENTESE Usage**: `world.codebase.manifest`, `self.memory.cartography`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **Observer gradations** | Security/perf/product lenses | `Observer(archetype="security_auditor")` |
| **Query syntax** | Module discovery | `logos.query("?world.codebase.module.*")` |
| **Subscriptions** | File change stream | `logos.subscribe("world.codebase.file.*")` |
| **Aliases** | Quick navigation | `logos.alias("arch", "world.codebase")` |
| **CLI REPL** | Gestalt commands | `kg arch.module[name=api].manifest` |

**Audit Checklist**:
- [ ] Define observer archetypes: security, performance, product, onboarding
- [ ] Wire file watcher to subscription manager
- [ ] Add bounded queries for large codebases
- [ ] Create `arch`, `code`, `drift` aliases
- [ ] Test: incremental updates via subscription < 2s

**Estimated Synergy Lift**: 30% reduction in custom watcher code

---

### 2.7 The Gardener

**Current AGENTESE Usage**: `concept.gardener.session.*`, `self.forest.evolve`, `concept.nphase.*`

**v3 Synergies to Realize**:

| v3 Feature | Synergy | Implementation |
|------------|---------|----------------|
| **CLI as REPL** | Core requirement | `kg self.forest.manifest` is native |
| **Aliases** | Shortcuts | `kg /forest` → `self.forest.manifest` |
| **Query syntax** | Session discovery | `logos.query("?concept.gardener.session.*")` |
| **Subscriptions** | Forest updates | `logos.subscribe("self.forest.*")` |
| **String >>** | N-Phase pipelines | `"concept.nphase.plan" >> "concept.nphase.implement"` |
| **Effects** | Session writes | `Effect.WRITES("session_store")` |

**Audit Checklist**:
- [ ] Verify v3 Phase 3 makes `kg <path>` work natively
- [ ] Add standard aliases: `/forest`, `/soul`, `/surprise`, `/continue`
- [ ] Wire session manager to subscription manager
- [ ] Implement phase composition via `>>`
- [ ] Test: bare `kg` shows proactive suggestions via query

**Estimated Synergy Lift**: The Gardener IS v3—100% alignment required

---

## III. Cross-Jewel Synergies

### 3.1 Shared Subscription Infrastructure

All jewels with real-time needs should share the v3 subscription manager:

| Jewel | Subscription Pattern | Benefit |
|-------|---------------------|---------|
| Atelier | `*.studio.*` | Spectator streams |
| Coalition | `*.task.*` | Task progress |
| Brain | `*.ghost.*` | Proactive surfacing |
| Punchdrunk | `*.consent.*` | Consent debt |
| Domain | `*.audit.*` | Compliance stream |
| Gestalt | `*.file.*` | Architecture updates |
| Gardener | `*.forest.*` | Session sync |

**Audit Action**: Ensure v3 subscription manager handles all patterns with backpressure.

### 3.2 Shared Effect Composition

Effects compose additively across jewels:

```python
# Cross-jewel pipeline
result = await (
    path("forge.task.research")          # READS, CHARGES(30)
    >> "brain.crystal.create"            # WRITES, CHARGES(10)
    >> "atelier.artifact.acquire"        # WRITES, CHARGES(50)
).run(observer, logos)

# Total effects: READS + WRITES + CHARGES(90)
```

**Audit Action**: Verify effect composition across jewel boundaries.

### 3.3 Shared Observer Archetypes

Several observer archetypes recur across jewels:

| Archetype | Jewels Using | v3 Implementation |
|-----------|--------------|-------------------|
| `developer` | Brain, Gestalt, Gardener | `Observer(archetype="developer", capabilities={"code:*"})` |
| `spectator` | Atelier, Punchdrunk | `Observer(archetype="spectator", capabilities={"read:*"})` |
| `analyst` | Domain, Gestalt | `Observer(archetype="analyst", capabilities={"audit:read"})` |
| `enterprise` | Domain, Coalition | `Umwelt(tenant_id=..., archetype="enterprise")` |

**Audit Action**: Create shared observer factory with jewel-specific extensions.

---

## IV. Implementation Sequence

### Phase 1: After v3 Phase 3 Complete

```
1. Gardener alignment (blocking)
   └── Verify CLI REPL works for all paths
   └── Add standard aliases
   └── Test session resume via v3 subscription

2. Brain integration
   └── Ghost surfacing via subscription
   └── Cartography via bounded queries
   └── Aliases for personal shortcuts
```

### Phase 2: After v3 Phase 4 Complete

```
3. Atelier + Coalition streaming
   └── Spectator subscriptions
   └── Task progress subscriptions
   └── Effect composition for credits

4. Punchdrunk consent mechanics
   └── Refusal type integration
   └── Force effects
   └── Observer-dependent perception
```

### Phase 3: Before v3 Migration Complete

```
5. Domain compliance
   └── Envelope tracing for audit
   └── Effect.AUDITS integration
   └── Per-tenant bounded queries

6. Gestalt architecture
   └── File watcher subscriptions
   └── Observer lenses
   └── CLI/Web projection from same Signal
```

---

## V. Success Criteria

### Quantitative

| Metric | Before v3 | After v3 | Target |
|--------|-----------|----------|--------|
| Custom streaming code (LOC) | ~2000 | ~500 | 75% reduction |
| Effect declaration coverage | 0% | 100% | All mutations declare effects |
| Subscription patterns shared | 0 | 7 | One per jewel |
| Observer archetypes shared | 0 | 4+ | Reuse across jewels |
| CLI commands via Logos | 30% | 100% | Full AGENTESE-first |

### Qualitative

- [ ] Developers understand one API (Logos) for all jewels
- [ ] Cross-jewel pipelines compose naturally with `>>`
- [ ] Subscription debugging uses unified tools
- [ ] Effect audit trail exports for compliance
- [ ] New jewels can be added by registering paths, not custom code

---

## VI. Open Questions for Audit

1. **Subscription cardinality**: How many concurrent subscriptions per tenant?
2. **Effect rollback**: Cross-jewel pipeline failures—partial rollback strategy?
3. **Observer inheritance**: Can jewel-specific observers extend shared archetypes?
4. **Query federation**: Can `logos.query()` span multiple jewels?
5. **Alias namespacing**: User aliases vs system aliases—conflict resolution?

---

## VII. References

- `spec/protocols/agentese-v3.md` — v3 specification
- `plans/agentese-v3.md` — v3 implementation plan
- `plans/core-apps-synthesis.md` — Crown Jewels overview
- `plans/core-apps/*.md` — Individual jewel plans

---

*"When the protocol disappears, the jewels shine."*

*Last updated: 2025-12-15*
