---
path: self.forest.plan.derivation-dag-integration
mood: triumphant
momentum: 0.95
trajectory: ascending
season: BLOOMING
last_gardened: 2025-12-23
gardener: claude-opus-4
---

# Derivation DAG Integration

> *"Specs form a derivation DAG: CONSTITUTION → Meta-Principles → Operational → ADs → Domain"*

**Origin**: Emerged from spec metabolization session (2025-12-23). Research revealed the derivation infrastructure already exists but lacks explicit wiring to navigation and visualization layers.

**Goal**: Make the derivation DAG visible, navigable, and self-healing.

---

## Phase 1 Complete! ✓

**Session**: 2025-12-23
**Tests**: 255 passing (36 new CONSTITUTION tests)

### What Was Done

1. **Added `DerivationTier.AXIOM`** — New tier above BOOTSTRAP (rank=-1, ceiling=1.0)
2. **Created `bootstrap.py`** — CONSTITUTION derivation with all 7 principles as categorical draws
3. **Updated registry** — Seeds CONSTITUTION first, bootstrap agents derive from it
4. **Added `is_axiom` and `is_indefeasible` properties** — Clean API for tier checking
5. **Comprehensive tests** — 11 new tests for CONSTITUTION as root

### Key Design Decisions

- **Q1 (Principles as nodes vs draws)**: Implemented as draws on CONSTITUTION ✓
  - Principles are not agents, they're properties of agents
  - CONSTITUTION carries all 7 with categorical evidence (draw_strength=1.0)

- **Q2 (Meta-Principles)**: Deferred to Phase 2
  - Can be added as FUNCTOR-tier nodes when needed

### Verification

```bash
# All tests pass
uv run pytest protocols/derivation/_tests/ -v  # 255 passed

# Type checks pass
uv run mypy protocols/derivation/{types,registry,bootstrap}.py --strict  # Success
```

---

## Executive Summary

The derivation framework (`impl/claude/protocols/derivation/`) now implements:
- **CONSTITUTION as axiomatic root** (Phase 1 ✓)
- Confidence propagation (inherited × tier_ceiling + empirical + stigmergic)
- DAG structure with cycle detection
- ASHC → derivation bridge
- Witness → stigmergic confidence bridge
- Hypergraph edge resolvers

**What's remaining**:
1. ~~CONSTITUTION as explicit root~~ ✓ COMPLETE
2. Confidence-aware navigation in Hypergraph Emacs
3. Evidence attached to EDGES (WitnessedDerivation)
4. Continuous health monitoring
5. Derivation crystal compression

---

## Phase 1: CONSTITUTION as Explicit Root ✓ COMPLETE

**Estimated Effort**: 1 session (2-3 hours)
**Actual Effort**: ~1.5 hours
**Status**: COMPLETE
**Priority**: HIGH (foundational)
**Risk**: LOW

### What

Make CONSTITUTION the axiomatic root of the derivation DAG, with all bootstrap agents deriving from it.

### Why

Currently the DAG has 7 implicit roots (Id, Compose, Judge, Ground, Contradict, Sublate, Fix). This obscures the true hierarchy. With CONSTITUTION as root:
- Visualization shows complete hierarchy from first principles
- Confidence propagation starts from a single axiom
- The seven principles become explicit nodes in the graph

### Implementation

```python
# impl/claude/protocols/derivation/bootstrap.py (NEW FILE)

from .types import Derivation, DerivationTier, PrincipleDraw, EvidenceType

SEVEN_PRINCIPLES = (
    "Tasteful", "Curated", "Ethical", "Joy-Inducing",
    "Composable", "Heterarchical", "Generative",
)

CONSTITUTION_DERIVATION = Derivation(
    agent_name="CONSTITUTION",
    tier=DerivationTier.AXIOM,  # New tier, ceiling=1.0
    derives_from=(),  # True root
    principle_draws=tuple(
        PrincipleDraw(
            principle=p,
            draw_strength=1.0,
            evidence_type=EvidenceType.CATEGORICAL,
            evidence_sources=("axiom",),
        )
        for p in SEVEN_PRINCIPLES
    ),
    inherited_confidence=1.0,
    empirical_confidence=1.0,
    stigmergic_confidence=1.0,
)

BOOTSTRAP_AGENTS = {
    "Id": ("CONSTITUTION",),
    "Compose": ("CONSTITUTION",),
    "Judge": ("CONSTITUTION",),
    "Ground": ("CONSTITUTION",),
    "Contradict": ("CONSTITUTION",),
    "Sublate": ("CONSTITUTION",),
    "Fix": ("CONSTITUTION",),
}
```

### Changes Required

1. **Add `DerivationTier.AXIOM`** (types.py) — ceiling 1.0, above BOOTSTRAP
2. **Create bootstrap.py** — CONSTITUTION derivation + bootstrap agent mappings
3. **Update registry initialization** — Register CONSTITUTION first
4. **Update existing bootstrap agent derivations** — `derives_from=("CONSTITUTION",)`

### Tests

- [x] CONSTITUTION is retrievable from registry
- [x] Bootstrap agents derive from CONSTITUTION
- [x] Confidence propagation works from CONSTITUTION down
- [x] DAG has single root (CONSTITUTION)
- [x] Any agent can trace ancestry to CONSTITUTION
- [x] CONSTITUTION is indefeasible (Law 3)

### Open Questions (Resolved)

- **Q1**: Should each of the seven principles be a separate node, or just draws on CONSTITUTION?
  - **Decision**: Draws on CONSTITUTION ✓
  - **Rationale**: Principles are not agents. They're categorical properties that agents draw upon.

- **Q2**: Should Meta-Principles (Accursed Share, etc.) also be derivation nodes?
  - **Decision**: Deferred to Phase 2
  - **Rationale**: Can add as FUNCTOR-tier nodes when navigation requires them

---

## Phase 2 Complete! ✓ (Radical AGENTESE Approach)

**Session**: 2025-12-23
**Estimated Effort**: 2-3 sessions
**Actual Effort**: ~1 session (COMPRESSED!)
**Status**: COMPLETE
**Priority**: HIGH (user-facing)
**Risk**: MEDIUM (frontend + backend coordination)

### Design Decision: Radical Compression

The original plan called for 4 separate files (routes, hook, component, keybindings).
We chose the **radical AGENTESE approach** instead:

- ❌ New `derivation_routes.py` — AGENTESE IS the API
- ✓ Extended existing `concept.derivation` node with `for_path` and `ancestors` aspects
- ✓ Extended existing `StatusLine` component with confidence indicator
- ✓ Extended existing `useKeyHandler` with gD/gc keybindings

**Principle Alignment**: Tasteful ✓, Composable ✓, Generative ✓

### What Was Done

1. **Extended `concept.derivation` node** (concept_derivation.py):
   - Added `for_path` aspect — Query derivation by spec path (AGENTESE native)
   - Added `ancestors` aspect — Get full ancestor chain for navigation
   - Updated affordances list and `_invoke_aspect` routing

2. **Added confidence indicator to StatusLine** (StatusLine.tsx + .css):
   - New `confidence?: number` and `derivationTier?: string` props
   - Visual bar display: `████░░░░ 75%`
   - Color-coded by health level (healthy/degraded/warning/critical)
   - Tooltip with tier info and keybinding hints

3. **Added derivation keybindings** (useKeyHandler.ts):
   - `gD` → GO_DERIVATION_PARENT — Navigate to derives_from
   - `gc` → SHOW_CONFIDENCE — Show confidence breakdown
   - Optional callbacks in UseKeyHandlerOptions

### Verification

```bash
# Backend tests pass (255 tests)
uv run pytest protocols/derivation/_tests/ -v

# Frontend typecheck passes
cd web && npm run typecheck

# Frontend lint passes
cd web && npm run lint

# Mypy passes
uv run mypy protocols/agentese/contexts/concept_derivation.py
```

### What Was NOT Done (Intentionally)

- No new `derivation_routes.py` — Follows "AGENTESE IS the API"
- No new `useDerivationNav.ts` — Extended existing hooks instead
- No new `ConfidenceIndicator.tsx` — Integrated into StatusLine

---

## Phase 2 Original Design (SUPERSEDED)

<details>
<summary>Original plan for reference</summary>

### What

Add derivation-aware navigation to Hypergraph Emacs with confidence visualization.

### Why

The editor currently navigates by file structure. Users can't see:
- What a spec derives from
- How confident the derivation is
- Where evidence is weak

With confidence-aware navigation:
- Visual distinction for low-confidence specs (color gradient)
- Navigate by derivation chain (`gd` for parent, `gD` for dependents)
- Confidence breakdown in status line

### Implementation

#### Backend: Derivation Query Endpoints

```python
# impl/claude/protocols/api/derivation_routes.py (NEW)

@router.get("/derivation/{spec_path:path}")
async def get_derivation(spec_path: str) -> DerivationResponse:
    """Get derivation info for a spec."""
    derivation = registry.get(spec_path)
    return DerivationResponse(
        spec_path=spec_path,
        tier=derivation.tier.name,
        confidence=derivation.total_confidence,
        confidence_breakdown={
            "inherited": derivation.inherited_confidence,
            "empirical": derivation.empirical_confidence,
            "stigmergic": derivation.stigmergic_confidence,
        },
        derives_from=derivation.derives_from,
        dependents=registry.dependents(spec_path),
        principle_draws=[
            {"principle": d.principle, "strength": d.draw_strength}
            for d in derivation.principle_draws
        ],
    )

@router.get("/derivation/{spec_path:path}/ancestors")
async def get_ancestors(spec_path: str) -> list[str]:
    """Get full ancestry chain to CONSTITUTION."""
    return registry.ancestors(spec_path)
```

</details>

---

## Phase 3: WitnessedDerivation (Evidence on Edges)

**Estimated Effort**: 3-4 sessions (9-12 hours)
**Priority**: MEDIUM (deep infrastructure)
**Risk**: MEDIUM (new data model)

### What

Attach witness evidence (marks, tests, proofs) to derivation EDGES, not just nodes.

### Why

Currently evidence is node-centric. You know "witness.md has 3 marks" but not "the derivation from CONSTITUTION to witness.md has evidence X, Y, Z."

With edge-centric evidence:
- Can answer "why do we trust this derivation?"
- Can identify weak links in the chain
- Can crystallize patterns about specific derivations

### Implementation

```python
# impl/claude/protocols/derivation/witnessed.py (NEW FILE)

@dataclass(frozen=True)
class WitnessedDerivation:
    """A derivation edge enriched with witness evidence."""

    # Edge identity
    source_spec: str
    target_spec: str
    derivation_type: str  # "derives_from", "implements", "extends"

    # Core derivation (from DerivationRegistry)
    derivation: Derivation

    # Attached evidence (by level)
    marks: tuple[MarkId, ...]        # L0: Human attention
    tests: tuple[TestId, ...]        # L1: Automated tests
    proofs: tuple[ProofId, ...]      # L2: ASHC/formal proofs

    # Crystallized insights about this edge
    crystals: tuple[CrystalId, ...]

    # Edge-specific confidence (distinct from node confidence)
    edge_confidence: float
    last_verified: datetime

    @property
    def evidence_ladder(self) -> dict[str, int]:
        """Count evidence at each level."""
        return {
            "L0_marks": len(self.marks),
            "L1_tests": len(self.tests),
            "L2_proofs": len(self.proofs),
            "crystals": len(self.crystals),
        }

    @property
    def is_well_evidenced(self) -> bool:
        """Heuristic: at least L1 evidence exists."""
        return len(self.tests) > 0 or len(self.proofs) > 0


class WitnessedDerivationRegistry:
    """
    Registry of witnessed derivations.

    Wraps DerivationRegistry with evidence attachment.
    """

    def __init__(self, derivation_registry: DerivationRegistry):
        self._derivations = derivation_registry
        self._evidence: dict[tuple[str, str], EdgeEvidence] = {}

    async def attach_mark(
        self,
        source: str,
        target: str,
        mark_id: MarkId,
    ) -> WitnessedDerivation:
        """Attach a witness mark to a derivation edge."""
        key = (source, target)
        evidence = self._evidence.get(key, EdgeEvidence.empty())
        self._evidence[key] = evidence.with_mark(mark_id)
        return self._build_witnessed(source, target)

    async def attach_test(
        self,
        source: str,
        target: str,
        test_id: TestId,
        passed: bool,
    ) -> WitnessedDerivation:
        """Attach a test result to a derivation edge."""
        # ...

    async def attach_proof(
        self,
        source: str,
        target: str,
        proof_id: ProofId,
        checker: str,  # "dafny", "lean4", "verus"
    ) -> WitnessedDerivation:
        """Attach a formal proof to a derivation edge."""
        # ...
```

### Database Schema

```sql
-- New table for edge evidence
CREATE TABLE derivation_edge_evidence (
    id UUID PRIMARY KEY,
    source_spec TEXT NOT NULL,
    target_spec TEXT NOT NULL,
    derivation_type TEXT NOT NULL,

    -- Evidence references (arrays of IDs)
    mark_ids UUID[] DEFAULT '{}',
    test_ids UUID[] DEFAULT '{}',
    proof_ids UUID[] DEFAULT '{}',
    crystal_ids UUID[] DEFAULT '{}',

    -- Computed fields
    edge_confidence FLOAT DEFAULT 0.0,
    last_verified TIMESTAMP,

    -- Constraints
    UNIQUE(source_spec, target_spec, derivation_type)
);

CREATE INDEX idx_edge_evidence_source ON derivation_edge_evidence(source_spec);
CREATE INDEX idx_edge_evidence_target ON derivation_edge_evidence(target_spec);
```

### Changes Required

1. **Create `witnessed.py`** — WitnessedDerivation + registry
2. **Add database migration** — `derivation_edge_evidence` table
3. **Update mark creation** — Option to attach to edge
4. **Update ASHC bridge** — Attach proofs to edges
5. **API endpoints** — Query edge evidence
6. **Frontend** — Show edge evidence in navigation

### Tests

- [ ] Can attach mark to edge
- [ ] Can attach test result to edge
- [ ] Can attach proof to edge
- [ ] Edge confidence updates correctly
- [ ] Evidence ladder counts are accurate

### Open Questions

- **Q6**: How to identify which edge a mark belongs to?
  - **Options**:
    - Explicit `--edge source:target` flag on `km` command
    - Infer from mark context (current file = target)
    - Tag-based: `--tag edge:principles.md:witness.md`
  - **Lean toward**: Infer from context, with explicit override

- **Q7**: Should edge evidence affect node confidence?
  - **Options**:
    - Edge confidence is independent
    - Edge confidence contributes to target node's stigmergic
  - **Lean toward**: Contribute to stigmergic (evidence of derivation = evidence of use)

- **Q8**: What's the relationship between edge crystals and node crystals?
  - **Weak area**: Need to design crystal hierarchy for edges
  - **Proposal**: Edge crystals are separate, can reference node crystals

---

## Phase 4: ASHC Continuous Health Monitoring

**Estimated Effort**: 2 sessions (4-6 hours)
**Priority**: MEDIUM (automation)
**Risk**: LOW (additive)

### What

Background monitoring of derivation DAG health with auto-refresh of stale evidence.

### Why

Currently ASHC runs on-demand. Specs can become stale (evidence > 7 days old) without anyone noticing. With continuous monitoring:
- Dashboard shows DAG health at a glance
- Stale specs auto-refresh in background
- Confidence trends visible over time

### Implementation

```python
# impl/claude/protocols/ashc/health.py (NEW FILE)

@dataclass(frozen=True)
class DerivationHealth:
    """Health status of the derivation DAG."""

    total_specs: int
    healthy_count: int      # Evidence fresh, confidence >= ceiling - 0.1
    stale_count: int        # Evidence > 7 days old
    low_confidence_count: int  # Confidence < ceiling - 0.2
    orphan_count: int       # No derives_from (except CONSTITUTION)

    @property
    def health_score(self) -> float:
        """0.0-1.0 overall health."""
        if self.total_specs == 0:
            return 1.0
        return self.healthy_count / self.total_specs


class DerivationHealthMonitor:
    """
    Background health monitoring for derivation DAG.

    Runs periodically (configurable, default 1 hour).
    Auto-refreshes critically stale specs.
    Emits events for dashboard consumption.
    """

    def __init__(
        self,
        registry: DerivationRegistry,
        ashc: ASHCCompiler,
        event_bus: EventBus,
        refresh_interval: timedelta = timedelta(hours=1),
        staleness_threshold: timedelta = timedelta(days=7),
        auto_refresh_limit: int = 5,  # Max specs to refresh per cycle
    ):
        self._registry = registry
        self._ashc = ashc
        self._bus = event_bus
        self._interval = refresh_interval
        self._staleness = staleness_threshold
        self._limit = auto_refresh_limit

    async def check_health(self) -> DerivationHealth:
        """Run health check, emit events, optionally auto-refresh."""

        all_derivations = list(self._registry.all())
        now = datetime.utcnow()

        stale = [
            d for d in all_derivations
            if d.last_verified < now - self._staleness
        ]

        low_conf = [
            d for d in all_derivations
            if d.total_confidence < d.tier.ceiling - 0.2
        ]

        orphans = [
            d for d in all_derivations
            if not d.derives_from and d.agent_name != "CONSTITUTION"
        ]

        health = DerivationHealth(
            total_specs=len(all_derivations),
            healthy_count=len(all_derivations) - len(stale) - len(low_conf),
            stale_count=len(stale),
            low_confidence_count=len(low_conf),
            orphan_count=len(orphans),
        )

        # Emit health event
        await self._bus.emit(DerivationHealthEvent(health=health))

        # Auto-refresh critically stale
        critical = [d for d in stale if d.total_confidence < 0.5][:self._limit]
        for derivation in critical:
            await self._refresh(derivation)

        return health

    async def _refresh(self, derivation: Derivation) -> None:
        """Refresh a single derivation via ASHC."""
        spec_path = self._registry.spec_path_for(derivation.agent_name)
        if spec_path:
            output = await self._ashc.compile(spec_path, n_variations=10)
            await update_derivation_from_ashc(
                self._registry,
                derivation.agent_name,
                output,
            )
            await self._bus.emit(DerivationRefreshedEvent(
                agent_name=derivation.agent_name,
                old_confidence=derivation.total_confidence,
                new_confidence=self._registry.get(derivation.agent_name).total_confidence,
            ))
```

### CLI Integration

```bash
# Manual health check
kg derivation health

# Output:
# Derivation DAG Health
# ═══════════════════════════════════════════
# Total Specs:    193
# Healthy:        178 (92%)
# Stale:          10 (5%)
# Low Confidence: 5 (3%)
# Orphans:        0
#
# Health Score: 0.92
#
# Critically Stale (auto-refresh candidates):
#   - spec/services/forge.md (14 days, confidence 0.42)
#   - spec/agents/q-gent.md (21 days, confidence 0.38)

# Manual refresh
kg derivation refresh spec/services/forge.md
```

### Changes Required

1. **Create `health.py`** — Monitor + health check
2. **Add CLI commands** — `kg derivation health`, `kg derivation refresh`
3. **Add background task** — Scheduled health checks
4. **Add dashboard endpoint** — `/api/derivation/health`
5. **Frontend widget** — Health indicator in status bar

### Tests

- [ ] Health check correctly identifies stale specs
- [ ] Auto-refresh triggers ASHC compilation
- [ ] Health events emitted correctly
- [ ] CLI output is accurate

### Open Questions

- **Q9**: What's the right auto-refresh limit?
  - **Concern**: ASHC is expensive (LLM calls), don't want runaway costs
  - **Lean toward**: 5 per cycle, configurable, with cost tracking

- **Q10**: Should auto-refresh require confirmation?
  - **Options**:
    - Fully automatic (fire-and-forget)
    - Require confirmation for expensive refreshes
    - Dry-run mode by default
  - **Lean toward**: Automatic for stale, confirmation for low-confidence (might need manual fix)

---

## Phase 5: Derivation Crystal Compression

**Estimated Effort**: 3-4 sessions (9-12 hours)
**Priority**: LOW (advanced feature)
**Risk**: MEDIUM (new concept)

### What

Compress evidence about derivation edges into crystals, enabling pattern recognition over time.

### Why

Individual marks about derivations are noisy. Over weeks/months, patterns emerge:
- "The CONSTITUTION → Brain derivation is always stable"
- "The AD-009 → services/* derivations need frequent refresh"
- "Principle X is the most-drawn-upon"

With derivation crystals:
- Compressed insights about derivation patterns
- Trend detection (improving vs degrading)
- Historical confidence visualization

### Implementation

```python
# impl/claude/services/witness/derivation_crystal.py (NEW FILE)

@dataclass(frozen=True)
class DerivationCrystal:
    """
    Compressed evidence about a derivation edge or subgraph.

    Analogous to Crystal (marks → session → day → week → epoch)
    but for derivation evidence.
    """

    id: CrystalId
    level: CrystalLevel  # EDGE=0, CHAIN=1, SUBGRAPH=2, EPOCH=3

    # What this crystal covers
    derivation_edges: tuple[tuple[str, str], ...]
    time_range: tuple[datetime, datetime]

    # Compressed insights
    insight: str
    significance: str

    # Confidence analysis
    confidence_trend: float  # -1.0 (degrading) to +1.0 (improving)
    average_confidence: float
    min_confidence: float
    max_confidence: float

    # Evidence summary
    total_marks: int
    total_tests: int
    total_proofs: int

    # Principle patterns
    dominant_principles: tuple[str, ...]

    # Mood vector (affective signature)
    mood: MoodVector

    # Provenance
    source_crystals: tuple[CrystalId, ...]  # Level 1+ only
    crystallized_at: datetime


class DerivationCrystallizer:
    """
    Compress derivation evidence into crystals.

    Levels:
    - EDGE (L0): Single edge, from marks/tests/proofs
    - CHAIN (L1): Derivation chain (A → B → C)
    - SUBGRAPH (L2): Related edges (all edges touching spec X)
    - EPOCH (L3): Long-term patterns (monthly/quarterly)
    """

    async def crystallize_edge(
        self,
        source: str,
        target: str,
        evidence: WitnessedDerivation,
    ) -> DerivationCrystal:
        """Create L0 crystal from edge evidence."""
        # Use LLM to generate insight and significance
        prompt = self._build_edge_prompt(source, target, evidence)
        response = await self._llm.generate(prompt)

        return DerivationCrystal(
            id=generate_crystal_id(),
            level=CrystalLevel.EDGE,
            derivation_edges=((source, target),),
            time_range=evidence.time_range,
            insight=response.insight,
            significance=response.significance,
            confidence_trend=self._compute_trend(evidence),
            # ...
        )

    async def crystallize_chain(
        self,
        chain: list[str],  # [A, B, C] means A → B → C
        edge_crystals: list[DerivationCrystal],
    ) -> DerivationCrystal:
        """Create L1 crystal from chain of edge crystals."""
        # ...
```

### Visualization

```
Derivation Crystal Timeline:
════════════════════════════════════════════════════════════════════

Dec 2025                                                          Now
    │                                                               │
    ├──[EDGE]───[EDGE]───[CHAIN]───────────────────[SUBGRAPH]──────┤
    │  witness   brain    Core→Brain                Full DAG       │
    │  0.82      0.78     "Stable"                   "Healthy"      │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

Trend: ↑ +0.05 (improving over 30 days)
```

### Changes Required

1. **Create `derivation_crystal.py`** — DerivationCrystal + Crystallizer
2. **Add database tables** — `derivation_crystals`
3. **Add crystallization triggers** — On health check, on threshold
4. **API endpoints** — Query derivation crystals
5. **Visualization component** — Timeline, trend charts

### Tests

- [ ] Edge crystal created from evidence
- [ ] Chain crystal aggregates edge crystals
- [ ] Confidence trend computed correctly
- [ ] LLM generates meaningful insights

### Open Questions

- **Q11**: What triggers crystallization?
  - **Options**:
    - Time-based (daily, weekly)
    - Evidence-count threshold (N marks → crystal)
    - Confidence-change threshold (Δ > 0.1)
  - **Lean toward**: Combination (weekly + threshold)

- **Q12**: How to handle conflicting crystals?
  - **Weak area**: Two crystals about same edge might have different insights
  - **Proposal**: Later crystal supersedes, with reference to earlier

- **Q13**: What's the LLM prompt structure for crystallization?
  - **Weak area**: Need to design prompts that produce useful insights
  - **Needs research**: Review existing crystal prompts, adapt for derivation

---

## Weak Areas & Risks

### Weak Area 1: Frontend Complexity

**Risk**: Phases 2 and 5 require significant frontend work (React components, state management, visualization).

**Mitigation**:
- Phase 2 can start with status line only (simpler)
- Reuse existing components (ConfidenceBar from SpecView)
- Consider gradual rollout (CLI first, then frontend)

### Weak Area 2: LLM Costs for Crystallization

**Risk**: Phase 5 uses LLM to generate insights. With 193 specs and weekly crystallization, costs could add up.

**Mitigation**:
- Use smaller model (Claude Haiku) for crystallization
- Batch crystallization (process 10 edges in one call)
- Cache similar insights (embedding-based dedup)

### Weak Area 3: Edge Evidence Attribution

**Risk**: It's unclear how to automatically attribute marks/tests to specific edges.

**Mitigation**:
- Start with explicit attribution (`km --edge source:target`)
- Add heuristics later (current file = target, recent navigation = source)
- Allow retroactive attribution (mark exists, then link to edge)

### Weak Area 4: Database Migration

**Risk**: Phase 3 adds new tables. Migration could affect production.

**Mitigation**:
- Use additive migrations only (no schema changes to existing tables)
- Test with production-like data before deploy
- Have rollback plan

### Weak Area 5: Circular Dependencies in Derivation

**Risk**: The DAG allows multiple parents (`derives_from: (A, B)`). Confidence propagation could have edge cases.

**Mitigation**:
- Existing cycle detection prevents true cycles
- Product-of-ancestors formula already handles multiple parents
- Add tests for complex DAG structures (diamond patterns)

---

## Open Questions Summary

| # | Question | Leaning | Status |
|---|----------|---------|--------|
| Q1 | Principles as nodes or draws? | Draws on CONSTITUTION | Decided |
| Q2 | Meta-Principles as derivation nodes? | Yes, FUNCTOR tier | Decided |
| Q3 | Confidence as % or decimal? | Percentage | Decided |
| Q4 | Unregistered specs handling? | Auto-register ORPHAN | Decided |
| Q5 | UX for shared principle navigation? | Infer from current | Decided |
| Q6 | Edge attribution for marks? | Infer + explicit override | Open |
| Q7 | Edge confidence → node confidence? | Contribute to stigmergic | Open |
| Q8 | Edge crystals vs node crystals? | Separate hierarchies | Open |
| Q9 | Auto-refresh limit? | 5 per cycle | Decided |
| Q10 | Auto-refresh confirmation? | Auto for stale, confirm for low-conf | Open |
| Q11 | Crystallization triggers? | Weekly + threshold | Open |
| Q12 | Conflicting crystals? | Later supersedes | Open |
| Q13 | LLM prompt for derivation crystal? | Needs research | Open |

---

## Implementation Order

```
Phase 1 (CONSTITUTION) ──────┐
                             ├──► Phase 2 (Navigation)
Phase 3 (Witnessed) ─────────┤
                             ├──► Phase 4 (Health)
                             │
                             └──► Phase 5 (Crystals)
```

**Recommended sequence**:
1. **Phase 1** first (foundation, unlocks visualization)
2. **Phase 2** second (user-facing value)
3. **Phase 3** third (deepens evidence model)
4. **Phase 4** fourth (automation, depends on 1-3)
5. **Phase 5** fifth (advanced, depends on 3)

**Parallel opportunities**:
- Phase 1 + Phase 3 database work can run in parallel
- Phase 2 frontend + Phase 4 backend can run in parallel

---

## Success Criteria

### Phase 1 Success
- [ ] `kg derivation show CONSTITUTION` returns root derivation
- [ ] All 7 bootstrap agents show `derives_from: CONSTITUTION`
- [ ] DAG visualization shows single root

### Phase 2 Success
- [ ] `gd` navigates to parent in derivation chain
- [ ] Status line shows tier and confidence
- [ ] Low-confidence specs are visually distinct (color)

### Phase 3 Success
- [ ] Marks can be attached to edges
- [ ] Edge evidence visible in navigation
- [ ] Edge confidence distinct from node confidence

### Phase 4 Success
- [ ] `kg derivation health` shows accurate stats
- [ ] Stale specs auto-refresh in background
- [ ] Health events visible in dashboard

### Phase 5 Success
- [ ] Derivation crystals generated from edge evidence
- [ ] Confidence trends visible over time
- [ ] Chain-level crystals aggregate edge crystals

---

## References

**Existing Infrastructure**:
- `impl/claude/protocols/derivation/` — DerivationRegistry, DAG, types
- `impl/claude/protocols/derivation/ashc_bridge.py` — ASHC → Derivation
- `impl/claude/protocols/derivation/witness_bridge.py` — Witness → Stigmergic
- `impl/claude/protocols/derivation/hypergraph_bridge.py` — Hyperedge resolvers

**Specifications**:
- `spec/protocols/derivation-framework.md` — Full derivation theory
- `spec/meta.md` — Derivation DAG navigation hub
- `spec/principles/decisions/AD-014-self-hosting-spec.md` — Self-hosting vision

**Today's Work**:
- `plans/meta.md` — Session learnings
- Witness marks: mark-9dc, mark-e44, mark-2fc, mark-058
- Decision: fuse-3065d144 (Hub pattern)

---

*"The proof IS the decision. The derivation IS the trust."*

**Created**: 2025-12-23
**Status**: PLANNING
**Next Action**: Phase 1 implementation (CONSTITUTION as root)
