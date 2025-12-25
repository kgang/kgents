# D-Gent Crystal Unification Plan

> *"Every agent that persists does so through D-gent. The proof IS the decision. The Crystal IS the witness."*

**Status**: Ready for Execution
**Date**: 2025-12-24
**Author**: Claude (Anthropic) via Analysis Operad audit
**Executor**: Agent with sub-agents

---

## Executive Summary

This plan consolidates kgents' backend data model under **versioned schema'd D-gent Crystal** as the universal persistence substrate. The audit revealed D-gent is architecturally sound (Constitutional score: 80%, Galois coherence: 0.95) but needs wire-up to achieve the vision of self-justifying decisions.

**The Brave Future**:
- Decisions are self-justifying (carry their own Toulmin proofs)
- Backend radically consolidated under D-gent Crystal
- AGENTESE Universal Protocol as the bus (`self.data.*`)
- Category theory basis (composition laws verified)
- Galois/DP integration (loss = difficulty, coherence = 1 - loss)

**Key Insight**: This is NOT a rebuild but a wire-up—connecting excellent existing components.

---

## Prerequisites

Before executing, the agent MUST read:

| Document | Purpose | Path |
|----------|---------|------|
| D-gent Spec | Understand Layer 0 | `spec/agents/d-gent.md` |
| Zero Seed Protocol | Seven-layer holarchy | `spec/protocols/zero-seed.md` |
| Analysis Operad | Four-mode analysis | `spec/theory/analysis-operad.md` |
| Galois Theory | Loss computation | `spec/theory/galois-modularization.md` |
| Constitution | 7+7 principles | `spec/principles/CONSTITUTION.md` |
| AGENTESE Skill | Node registration | `docs/skills/agentese-node-registration.md` |

---

## Phase 1: AGENTESE Registration (Priority: HIGH)

### Goal
Register D-gent components as AGENTESE nodes under `self.data.*` namespace.

### Context
Currently D-gent has no AGENTESE paths. The Universe and DgentRouter should be accessible via the universal protocol.

### Tasks

#### 1.1 Create D-gent AGENTESE Node Module
**Assignee**: Sub-agent (Explore + Code)
**Estimated Time**: 2 hours

```
File: impl/claude/agents/d/node.py

Tasks:
1. Read existing node patterns in impl/claude/services/*/node.py
2. Create @node decorators for:
   - self.data.store (Universe.store)
   - self.data.query (Universe.query)
   - self.data.get (Universe.get)
   - self.data.delete (Universe.delete)
   - self.data.stats (Universe.stats)
   - self.data.schema.register (Universe.register_type)
   - self.data.datum.put (DgentRouter.put)
   - self.data.datum.get (DgentRouter.get)
   - self.data.datum.list (DgentRouter.list)
   - self.data.datum.chain (DgentRouter.causal_chain)

Success Criteria:
- [ ] All nodes registered and discoverable
- [ ] logos.invoke("self.data.stats", observer) returns UniverseStats
- [ ] Tests pass: impl/claude/agents/d/_tests/test_node.py
```

#### 1.2 Register in Providers
**Assignee**: Sub-agent (Code)
**Estimated Time**: 30 minutes

```
File: impl/claude/services/providers.py

Tasks:
1. Add get_universe() provider function
2. Register: container.register("universe", get_universe, singleton=True)
3. Add get_dgent_router() if needed

Success Criteria:
- [ ] Universe injectable via DI
- [ ] No DependencyNotFoundError for universe
```

#### 1.3 Import in Gateway
**Assignee**: Sub-agent (Code)
**Estimated Time**: 15 minutes

```
File: impl/claude/protocols/agentese/gateway.py

Tasks:
1. Add agents.d.node to _import_node_modules()
2. Verify nodes appear in discovery

Success Criteria:
- [ ] kg agentese list shows self.data.* paths
```

### Phase 1 Verification
```bash
# Run after all Phase 1 tasks
cd impl/claude
uv run pytest agents/d/_tests/test_node.py -v
uv run python -c "from protocols.agentese.gateway import Logos; print([p for p in Logos().list_paths() if 'data' in p])"
```

---

## Phase 2: Galois Loss Integration (Priority: HIGH)

### Goal
Add `galois_loss()` computation to Universe for coherence tracking.

### Context
Galois loss measures information lost during restructuring. For D-gent:
- `L(Crystal) = d(Crystal, deserialize(serialize(Crystal)))`
- Low loss = high coherence = self-justifying

### Tasks

#### 2.1 Create Galois Loss Module
**Assignee**: Sub-agent (Research + Code)
**Estimated Time**: 4 hours

```
File: impl/claude/agents/d/galois.py

Tasks:
1. Read spec/theory/galois-modularization.md for theory
2. Implement semantic distance metrics:
   - cosine_embedding_distance (fast, deterministic)
   - bertscore_distance (balanced)
   - llm_judge_distance (accurate, expensive)
3. Implement GaloisLossComputer class:
   - compute(content: str) -> float
   - restructure(content: str) -> ModularContent
   - reconstitute(modular: ModularContent) -> str
4. Add compute_crystal_loss(crystal: Crystal) -> float

Success Criteria:
- [ ] galois_loss("Earth is round") < 0.1 (axiomatic)
- [ ] galois_loss("Complex multi-part claim...") > 0.3
- [ ] Tests pass: impl/claude/agents/d/_tests/test_galois.py
```

#### 2.2 Integrate into Universe
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1 hour

```
File: impl/claude/agents/d/universe/universe.py

Tasks:
1. Add galois: GaloisLossComputer | None to Universe.__init__
2. Add async def compute_loss(self, id: str) -> float method
3. Add loss to store() return (optional, for expensive tracking)
4. Emit loss in DataBus events if configured

Success Criteria:
- [ ] universe.compute_loss(crystal_id) returns float in [0, 1]
- [ ] Loss computation is optional (not required for basic use)
```

#### 2.3 Add Loss to UniverseStats
**Assignee**: Sub-agent (Code)
**Estimated Time**: 30 minutes

```
File: impl/claude/agents/d/universe/universe.py

Tasks:
1. Add average_loss: float | None to UniverseStats
2. Compute lazily when galois is available
3. Add per-schema loss breakdown

Success Criteria:
- [ ] stats.average_loss shows system health
```

### Phase 2 Verification
```bash
cd impl/claude
uv run pytest agents/d/_tests/test_galois.py -v
uv run python -c "
from agents.d.galois import GaloisLossComputer
g = GaloisLossComputer()
print(f'Axiom loss: {g.compute(\"Everything composes\"):.3f}')
print(f'Complex loss: {g.compute(\"Multi-step reasoning with dependencies\"):.3f}')
"
```

---

## Phase 3: Witness → D-gent Crystal Migration (Priority: HIGH)

### Goal
Migrate WitnessMark storage from SQL models to D-gent Crystal.

### Context
Currently WitnessMark is defined in both:
- `impl/claude/agents/d/schemas/witness.py` (Crystal schema)
- `impl/claude/models/witness.py` (SQLAlchemy model)

The Crystal schema exists but isn't wired. This phase completes the wire-up.

### Tasks

#### 3.1 Create Witness Crystal Adapter
**Assignee**: Sub-agent (Code)
**Estimated Time**: 3 hours

```
File: impl/claude/services/witness/crystal_adapter.py

Tasks:
1. Read existing persistence.py for current patterns
2. Create WitnessCrystalAdapter class:
   - Uses Universe with WITNESS_MARK_SCHEMA
   - Provides same interface as current MarkStore
   - Adds galois_loss tracking
3. Implement methods:
   - create_mark(action, reasoning, ...) -> Crystal[WitnessMark]
   - get_mark(id) -> Crystal[WitnessMark] | None
   - query_marks(tags, after, limit) -> list[Crystal[WitnessMark]]
   - get_causal_chain(id) -> list[Crystal[WitnessMark]]

Success Criteria:
- [ ] Same interface as current MarkStore
- [ ] Marks stored as D-gent Crystal
- [ ] Causal lineage preserved via datum.causal_parent
```

#### 3.2 Add Feature Flag for Migration
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1 hour

```
File: impl/claude/services/witness/__init__.py

Tasks:
1. Add USE_CRYSTAL_STORAGE env var check
2. Create get_mark_store() that returns appropriate impl:
   - If USE_CRYSTAL_STORAGE: return WitnessCrystalAdapter
   - Else: return current MarkStore
3. Update WitnessService to use get_mark_store()

Success Criteria:
- [ ] Can toggle between SQL and Crystal storage
- [ ] All existing tests pass with both modes
- [ ] No behavior change for users
```

#### 3.3 Migration Script
**Assignee**: Sub-agent (Code)
**Estimated Time**: 2 hours

```
File: impl/claude/scripts/migrate_witness_to_crystal.py

Tasks:
1. Read all marks from SQL storage
2. Convert to Crystal[WitnessMark]
3. Store in Universe
4. Verify count matches
5. Provide rollback option

Success Criteria:
- [ ] All existing marks migrated
- [ ] Causal chains preserved
- [ ] Can rollback if needed
```

### Phase 3 Verification
```bash
cd impl/claude
# Run with SQL storage
uv run pytest services/witness/_tests/ -v

# Run with Crystal storage
USE_CRYSTAL_STORAGE=1 uv run pytest services/witness/_tests/ -v

# Compare results
```

---

## Phase 4: Zero Seed Layer Tracking (Priority: MEDIUM)

### Goal
Add Zero Seed layer classification to CrystalMeta.

### Context
Zero Seed defines 7 epistemic layers (L1-L7). Each Crystal should know its layer for:
- Proof requirements (L3+ need Toulmin proofs)
- Galois loss interpretation (layer affects expected loss)
- Navigation (loss gradients by layer)

### Tasks

#### 4.1 Extend CrystalMeta
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1 hour

```
File: impl/claude/agents/d/crystal/crystal.py

Tasks:
1. Add to CrystalMeta:
   - layer: int | None (1-7, None if unclassified)
   - galois_loss: float | None
   - proof_id: str | None (reference to proof Crystal)
2. Add layer validation (must be 1-7 if set)
3. Add convenience property: requires_proof -> bool (layer >= 3)

Success Criteria:
- [ ] CrystalMeta includes layer, galois_loss, proof_id
- [ ] Existing Crystals work with layer=None
- [ ] Schema upgrade path defined
```

#### 4.2 Layer Classification Service
**Assignee**: Sub-agent (Research + Code)
**Estimated Time**: 3 hours

```
File: impl/claude/services/zero_seed/layer_classifier.py

Tasks:
1. Read spec/protocols/zero-seed.md for layer definitions
2. Implement classify_layer(content: str) -> int:
   - Use Galois loss convergence depth
   - L1-L2: loss < 0.15 after 0-1 restructurings
   - L3-L4: loss < 0.45 after 2-3 restructurings
   - L5-L6: loss < 0.75 after 4-5 restructurings
   - L7: doesn't converge quickly
3. Add classify_crystal(crystal: Crystal) -> int
4. Add batch classification for efficiency

Success Criteria:
- [ ] Constitution axioms classify as L1
- [ ] Specs classify as L3-L4
- [ ] Actions classify as L5
- [ ] Tests in _tests/test_layer_classifier.py
```

#### 4.3 Auto-Classification on Store
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1 hour

```
File: impl/claude/agents/d/universe/universe.py

Tasks:
1. Add auto_classify: bool = False to Universe.__init__
2. If auto_classify, compute layer on store()
3. Store layer in CrystalMeta
4. Make classification optional (performance concern)

Success Criteria:
- [ ] universe.store(obj, auto_classify=True) sets layer
- [ ] Layer stored in CrystalMeta
- [ ] Default is off (explicit opt-in)
```

### Phase 4 Verification
```bash
cd impl/claude
uv run pytest services/zero_seed/_tests/test_layer_classifier.py -v
uv run python -c "
from services.zero_seed.layer_classifier import classify_layer
print(f'Axiom layer: {classify_layer(\"Everything composes\")}')  # Should be 1-2
print(f'Spec layer: {classify_layer(\"The system SHALL...\")}')"  # Should be 3-4
```

---

## Phase 5: Self-Justifying Crystal (Priority: MEDIUM)

### Goal
Create the unified SelfJustifyingCrystal that carries its own proof.

### Context
This is the culmination—every Crystal can justify its own existence via embedded Toulmin proof with Galois coherence.

### Tasks

#### 5.1 Define SelfJustifyingCrystal
**Assignee**: Sub-agent (Code)
**Estimated Time**: 2 hours

```
File: impl/claude/agents/d/crystal/self_justifying.py

Tasks:
1. Create SelfJustifyingCrystal[T] extending Crystal[T]:
   - proof: GaloisWitnessedProof (required for L3+)
   - layer: int (required)
   - path: str (AGENTESE path)
2. Add properties:
   - coherence -> float (1 - galois_loss)
   - is_grounded -> bool (L1-2 or proof.coherence > 0.7)
   - tier -> EvidenceTier (from loss)
3. Add async witness() -> MarkId method
4. Add validate() that checks all requirements

Success Criteria:
- [ ] L1-L2 Crystals valid without proof
- [ ] L3+ Crystals require proof
- [ ] coherence property works
- [ ] witness() creates mark in Witness system
```

#### 5.2 Proof Storage Schema
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1 hour

```
File: impl/claude/agents/d/schemas/proof.py

Tasks:
1. Define GaloisWitnessedProof as frozen dataclass:
   - data, warrant, claim, backing, qualifier, rebuttals (Toulmin)
   - galois_loss, loss_decomposition (Galois)
   - tier, principles (Evidence)
2. Create PROOF_SCHEMA with versioning
3. Register in Universe

Success Criteria:
- [ ] Proofs storable as Crystals
- [ ] Schema versioned for evolution
```

#### 5.3 Proof ↔ Crystal Linkage
**Assignee**: Sub-agent (Code)
**Estimated Time**: 1.5 hours

```
File: impl/claude/agents/d/crystal/self_justifying.py

Tasks:
1. Add link_proof(crystal_id, proof_id) function
2. Add get_proof(crystal: SelfJustifyingCrystal) -> Crystal[Proof]
3. Use causal_parent for lineage: Crystal.datum.causal_parent = Proof.datum.id
4. Add proof validation on create

Success Criteria:
- [ ] Crystal → Proof linkage works
- [ ] Can trace Crystal to its justification
- [ ] Proof coherence affects Crystal validity
```

### Phase 5 Verification
```bash
cd impl/claude
uv run pytest agents/d/_tests/test_self_justifying.py -v
uv run python -c "
from agents.d.crystal.self_justifying import SelfJustifyingCrystal
# Create L1 crystal (no proof needed)
c1 = SelfJustifyingCrystal.create_axiom('Everything composes')
print(f'Axiom grounded: {c1.is_grounded}')  # True

# Create L4 crystal (needs proof)
c4 = SelfJustifyingCrystal.create_with_proof(
    value=MySpec(...),
    proof=my_proof,
    layer=4
)
print(f'Spec coherence: {c4.coherence:.2f}')
"
```

---

## Phase 6: Integration & Hardening (Priority: LOW)

### Goal
Full system integration, performance optimization, documentation.

### Tasks

#### 6.1 Brain → Crystal Migration
**Assignee**: Sub-agent (Code)
**Estimated Time**: 4 hours

```
Tasks:
1. Apply same pattern as Phase 3 to Brain service
2. Migrate BrainCrystal to SelfJustifyingCrystal
3. Add feature flag
4. Create migration script

Success Criteria:
- [ ] Brain uses D-gent Crystal
- [ ] All Brain tests pass
- [ ] Migration reversible
```

#### 6.2 Performance Optimization
**Assignee**: Sub-agent (Research + Code)
**Estimated Time**: 3 hours

```
Tasks:
1. Profile galois_loss computation
2. Add caching for repeated loss checks
3. Implement lazy layer classification
4. Add batch operations for migrations

Success Criteria:
- [ ] galois_loss < 100ms @ p95
- [ ] store() overhead < 10% with auto_classify=True
- [ ] Batch operations 10x faster than sequential
```

#### 6.3 Documentation
**Assignee**: Sub-agent (Write)
**Estimated Time**: 2 hours

```
Files:
- docs/skills/self-justifying-crystal.md
- Update docs/skills/unified-storage.md
- Update spec/agents/d-gent.md with new features

Success Criteria:
- [ ] Skills document the new patterns
- [ ] Examples for common use cases
- [ ] Migration guide included
```

#### 6.4 Final Verification
**Assignee**: Orchestrating agent
**Estimated Time**: 1 hour

```bash
# Full test suite
cd impl/claude
uv run pytest -q

# Type checking
uv run mypy .

# Frontend (if D-gent exposed via API)
cd web && npm run typecheck && npm run lint

# Integration test
uv run python -c "
from agents.d.crystal.self_justifying import SelfJustifyingCrystal
from agents.d.universe import init_universe

async def test():
    universe = await init_universe()

    # Create self-justifying spec crystal
    crystal = await SelfJustifyingCrystal.create_spec(
        content='System SHALL persist all decisions',
        proof=my_proof,
    )

    # Store
    id = await universe.store(crystal)

    # Retrieve
    retrieved = await universe.get(id)

    # Verify
    assert retrieved.is_grounded
    assert retrieved.coherence > 0.7
    print(f'Success! Crystal coherence: {retrieved.coherence:.2f}')

import asyncio
asyncio.run(test())
"
```

---

## Execution Guidelines

### For the Orchestrating Agent

1. **Execute phases sequentially** - Each phase depends on prior phases
2. **Spawn sub-agents for parallelizable tasks** within each phase
3. **Run verification after each phase** before proceeding
4. **Create marks for significant decisions** using `km`
5. **Update this plan** if discoveries change requirements

### For Sub-Agents

1. **Read prerequisites** before starting any task
2. **Follow gotcha patterns** in existing code
3. **Run tests before and after** changes
4. **Use --json flag** for machine-readable output
5. **Report blockers** to orchestrating agent

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| All tests pass | 100% | `pytest` exit code |
| Type check clean | 0 errors | `mypy` exit code |
| Constitutional alignment | > 80% | Manual review |
| Galois coherence | > 0.9 | `universe.stats().average_loss < 0.1` |
| Migration completeness | 100% | Count comparison |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Performance regression | Profile before/after, add benchmarks |
| Data loss during migration | Feature flags, rollback scripts |
| Breaking existing tests | Run full suite after each phase |
| Galois loss computation expensive | Make optional, add caching |
| Scope creep | Stick to plan, defer enhancements |

---

## Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| Phase 1: AGENTESE Registration | 3 hours | None |
| Phase 2: Galois Loss | 6 hours | Phase 1 |
| Phase 3: Witness Migration | 6 hours | Phase 1, 2 |
| Phase 4: Layer Tracking | 5 hours | Phase 2 |
| Phase 5: Self-Justifying Crystal | 5 hours | Phase 2, 4 |
| Phase 6: Integration | 10 hours | All prior |

**Total**: ~35 hours of focused work

---

*"The brave future is not a rebuild but a wire-up."*

**Filed**: 2025-12-24
**Status**: Ready for Execution
