# HYDRATE.md - kgents Session Context

**Status**: ~6,122 tests passing | Branch: `main`

## Recent: New Agent Batch Refactoring (Complete)

Comprehensive review and refactoring of seven proposed agents (Q, S, U, V, X, Y, Z) against design principles and bootstrap derivability. **All changes executed.**

### Assessment Summary

| Agent | Status | Verdict | Key Issue |
|-------|--------|---------|-----------|
| **Q-gent** | ✅ Clean | KEEP | Cleanly derived (Ground + Contradict) |
| **S-gent** | ✅ Clean | KEEP | Cleanly derived (Ground + Compose) |
| **V-gent** | ✅ Clean | KEEP | Extends Judge bootstrap with user principles |
| **U-gent** | ⚠️ Heavy | SIMPLIFY | Complex machinery, could be infrastructure |
| **X-gent** | ⚠️ Infrastructure | RECONSIDER | MCP/OpenAPI is protocol, not agent genus |
| **Y-gent** | ⚠️ Overlap | MERGE | Graph composition overlaps C-gent + Fix |
| **Z-gent** | ⚠️ Overlap | MERGE | Context mgmt overlaps Cooled Functor + Lethe |

### Detailed Analysis

#### Agents That Pass (Clean Derivation)

**Q-gent v2.0 (Questioner)** ✅
- **Derivation**: `Ground + Contradict` → surfaces what could contradict plans
- **Morphism**: `Context → Questions`
- **Unique Value**: Pre-execution inquiry fills a gap no other agent owns
- **Verdict**: KEEP AS-IS

**S-gent v2.0 (Scribe)** ✅
- **Derivation**: `Ground + Compose` → records events into structured context
- **Morphism**: `Event → SessionContext`
- **Unique Value**: Session-scoped working memory distinct from M-gent (long-term) and D-gent (raw)
- **Verdict**: KEEP AS-IS

**V-gent (Validator)** ✅
- **Derivation**: Extends `Judge` bootstrap with user/domain principles
- **Morphism**: `(Output, Constitution) → Verdict`
- **Unique Value**: Constitutional AI pattern for ethical/semantic validation
- **Integration**: Clean separation from T-gent (functional) and P-gent (parsing)
- **Verdict**: KEEP AS-IS

#### Agents Requiring Simplification

**U-gent (Understudy)** ⚠️
- **Issue 1**: Heavy machinery (ShadowObserver, StudentTrainer, StudentRouter, DriftDetector)
- **Issue 2**: Knowledge distillation is infrastructure, not agent genus
- **Issue 3**: Overlaps with B-gent (economics) and E-gent (evolution)
- **Bootstrap Gap**: No clean derivation from seven bootstrap agents
- **Recommendation**: Refactor as **B-gent Extension** ("Budget through Distillation")
  - Move ShadowObserver → O-gent telemetry integration
  - Move StudentRouter → C-gent conditional composition
  - Move DriftDetector → existing O-gent + V-gent pattern
  - Keep only "distill this agent to cheaper model" as B-gent operation

**X-gent (Xenolinguist)** ⚠️
- **Issue 1**: MCP/OpenAPI are protocols, not reasoning patterns
- **Issue 2**: "Protocol adapter" is infrastructure, not cognitive capability
- **Issue 3**: Already covered: L-gent (catalog), P-gent (parsing), W-gent (middleware)
- **Bootstrap Gap**: No derivation from bootstrap agents
- **Recommendation**: Refactor as **Infrastructure Layer**
  - MCP Client → `protocols/mcp/` (not agent genus)
  - Puppet Factory → L-gent's registration mechanism
  - External data → D-gent backends
  - **Delete X-gent as genus**; promote patterns to infrastructure docs

**Y-gent (Y-Combinator)** ⚠️
- **Issue 1**: Graph composition is C-gent extended, not new primitive
- **Issue 2**: Y-combinator IS Fix bootstrap with explicit recursion
- **Issue 3**: Branch/merge patterns exist in C-gent parallel.md
- **Bootstrap Gap**: `Y = Fix + Compose + Branch` - all exist
- **Recommendation**: Merge into **C-gent Extensions**
  - ThoughtGraph → `spec/c-gents/graph_composition.md`
  - YCombinator → Already is Fix with `max_depth`
  - Branch/Merge → Extend `spec/c-gents/parallel.md`
  - **Delete Y-gent as genus**; this is C-gent feature, not new letter

**Z-gent (Zero)** ⚠️
- **Issue 1**: Sliding window IS Cooled Functor (bootstrap idiom 3.2)
- **Issue 2**: Strategic forgetting IS Lethe (D-gent Phase 4)
- **Issue 3**: Unask/Mu operator is Judge + Contradict (premise checking)
- **Bootstrap Gap**: `Z = Cooled + Lethe + Judge` - all exist
- **Recommendation**: Merge into **Existing Components**
  - SlidingWindow → Cooled Functor formalization
  - SalienceScorer → M-gent's cartographer scoring
  - Forgetting cycles → Lethe integration in D-gent
  - Mu operator → V-gent premise validation
  - **Delete Z-gent as genus**; distribute to existing owners

### Generativity Assessment (Inter-Agent Compatibility)

| Combination | Current | After Simplification |
|-------------|---------|----------------------|
| Q + V | ✅ Q surfaces questions, V validates answers | Same |
| Q + S | ✅ Q reads session context from S | Same |
| U + B | ⚠️ Heavy overlap | ✅ B owns economics including distillation |
| X + L | ⚠️ Both register agents | ✅ L is sole registrar, X is infra |
| Y + C | ⚠️ Both compose agents | ✅ C owns all composition including graphs |
| Z + Lethe | ⚠️ Both manage forgetting | ✅ Lethe owns forgetting |

### Derivation Cleanliness Score

Post-simplification derivation map:

| Agent | Bootstrap Derivation | Clean? |
|-------|---------------------|--------|
| Q-gent | Ground + Contradict | ✅ |
| S-gent | Ground + Compose | ✅ |
| V-gent | Judge + Ground (extension) | ✅ |
| U→B extension | Compose + Judge (already exists) | ✅ |
| X→infra | N/A (infrastructure) | ✅ |
| Y→C extension | Fix + Compose (already exists) | ✅ |
| Z→distributed | Cooled + Lethe (already exist) | ✅ |

### Actions Completed

| Action | Status | Output |
|--------|--------|--------|
| KEEP Q-gent | ✅ | `spec/q-gents/README.md` |
| KEEP S-gent | ✅ | `spec/s-gents/README.md` |
| KEEP V-gent | ✅ | `spec/v-gents/README.md` |
| REFACTOR U-gent → B-gent | ✅ | `spec/b-gents/distillation.md` |
| DELETE X-gent → Infrastructure | ✅ | `docs/infrastructure/mcp-integration.md` |
| MERGE Y-gent → C-gent | ✅ | `spec/c-gents/graph-composition.md` |
| DISTRIBUTE Z-gent | ✅ | `spec/c-gents/context-management.md` |

Full summary: `docs/agent-refactoring-summary.md`

### Principle Alignment Rationale

- **Tasteful**: 3 agents pass, 4 fail "does this need to exist as distinct genus?"
- **Curated**: 7 genera bloats the alphabet; 3 additions is curated
- **Composable**: Merging Y→C improves composition, not adds complexity
- **Generative**: Clean derivation = regenerable from bootstrap
- **Heterarchical**: Distributed Z avoids "entropy god-agent" pattern

---

## Previous: DevEx Bootstrap Plan v2 (📋 PLANNING)

See `docs/devex-bootstrap-plan.md` - MCP sidecar architecture for developer-system metacognition.

**Key Points**:
- MCP sidecar (not middleware) - Claude *perceives* kgents via `kgents://` resources
- Pre-computed context via background daemons (<50ms latency)
- K-gent Mirror + Coach modes (prevents echo chamber)
- `kgents wake` / `kgents sleep` rituals

**Next**: Kent reviews plan → Phase 1 MCP implementation.

---

## Previous: Q-gent and S-gent v2.0 Revisions (Complete)

Revised Q-gent and S-gent specifications for pragmatism and harmony with design principles.

| Agent | V1.0 | V2.0 | Key Change |
|-------|------|------|------------|
| **Q-gent** | Quartermaster (gadgets) | Questioner (inquiry) | Removed W-gent overlap; now surfaces questions before action |
| **S-gent** | Sentinel (security) | Scribe (session memory) | Removed god-agent pattern; now provides structured session context |

### Why the Revisions?

**Q-gent v1.0 (Quartermaster) Issues:**
- Gadgets heavily overlapped with W-gent interceptors
- Laboratory duplicated W-gent registry patterns
- Not cleanly derivable from bootstrap

**S-gent v1.0 (Sentinel) Issues:**
- Overlapped with T-gent, V-gent, P-gent
- God-agent anti-pattern (wanted to wrap all agents)
- Security is a cross-cutting concern, not a genus

### Security Note
Security concerns from S-gent v1.0 should be distributed:
- Input sanitization → P-gent
- Sandboxing → J-gent/W-gent
- Monitoring → O-gent
- Ethics → V-gent

Proposed addition to `spec/principles.md`: "Defense in Depth" operational principle.

---

## Completed Systems

### Instance DB - Bicameral Engine (532 tests)

| Phase | Component | Key Files |
|-------|-----------|-----------|
| 1-2 | Core + Synapse + Hippocampus | `instance_db/{synapse,hippocampus}.py` |
| 3 | D-gent Adapters + Bicameral | `agents/d/{bicameral,infra_backends}.py` |
| 4 | Composting + Lethe | `instance_db/{compost,lethe}.py` |
| 5 | Lucid Dreaming + Neurogenesis | `instance_db/{dreamer,neurogenesis}.py` |
| 6 | Observability + Dashboard | `agents/o/cortex_observer.py`, `agents/w/cortex_dashboard.py` |

**Quick Start**:
```python
# Bicameral Memory (Left=relational, Right=vector)
bicameral = create_bicameral_memory(relational, vector, embedder, auto_heal_ghosts=True)
results = await bicameral.recall("query")  # Ghost memories auto-healed

# Synapse (Active Inference)
synapse = Synapse(store, SynapseConfig(surprise_threshold=0.5, flashbulb_threshold=0.9))
await synapse.fire(signal)  # Routes: flashbulb (>0.9), fast (>0.5), batch (<0.5)

# LucidDreamer (Interruptible maintenance)
dreamer = create_lucid_dreamer(synapse, hippocampus)
report = await dreamer.rem_cycle()
```

### Semantic Field (71 tests)

Stigmergic coordination via pheromones - agents emit/sense signals without direct imports.

| Agent | Emits | Senses |
|-------|-------|--------|
| Psi | METAPHOR | - |
| F | INTENT | METAPHOR |
| J | WARNING | - |
| B | OPPORTUNITY, SCARCITY | - |
| M | MEMORY | MEMORY |
| N | NARRATIVE | NARRATIVE |
| L | CAPABILITY | CAPABILITY |
| O | - | All types |

```python
field = create_semantic_field()
emitter = create_psi_emitter(field)
emitter.emit_metaphor("source", "target", strength=0.85, position=pos)
```

### M-gent Cartography (157 tests)

Memory-as-Orientation: HoloMap, Attractors, Desire Lines, Voids, Foveation.

```python
cartographer = create_cartographer(vector_search, trace_store)
holo_map = await cartographer.invoke(context_vector, Resolution.ADAPTIVE)
# → landmarks, desire_lines, voids, horizon
```

### W-gent Interceptors (125 tests)

Pipeline: Safety(50) → Metering(100) → Telemetry(200) → Persona(300)

---

## Agent Quick Reference

| Agent | Purpose | Key File |
|-------|---------|----------|
| B | Token economics | `agents/b/metered_functor.py` |
| D | State/Memory | `agents/d/bicameral.py` |
| E | Thermodynamic evolution | `agents/e/cycle.py` |
| I | Interface/TUI | `agents/i/semantic_field.py` |
| K | Kent simulacra | `agents/k/persona.py` |
| L | Semantic search | `agents/l/semantic_registry.py` |
| M | Context cartography | `agents/m/cartographer.py` |
| N | Narrative traces | `agents/n/chronicle.py` |
| O | Observation | `agents/o/observer.py` |
| Psi | Metaphor solving | `agents/psi/engine.py` |
| W | Wire protocol | `agents/w/bus.py` |

---

## Commands

```bash
pytest -m "not slow" -q              # Fast tests, quiet
pytest impl/claude/agents/d/ -v      # Specific agent
kgents check .                       # Validate
```

---

## Coding Gotchas

| Issue | Fix |
|-------|-----|
| Python 3.12 syntax | Use `Generic[A]` + `TypeVar`, not `class Foo[A]:` |
| Cross-agent imports | Use `*_integration.py` files or SemanticField |
| Forward refs | `from __future__ import annotations` + `TYPE_CHECKING` |

**Foundational agents** (can be imported anywhere): `shared`, `a`, `d`, `l`, `c`
