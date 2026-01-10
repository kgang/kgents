---
path: self.forest.plan.meta
mood: pruned
momentum: 0.8
trajectory: steady
season: BLOOMING
last_gardened: 2025-12-24
gardener: claude-opus-4.5
---

# meta.md — Mycelium

> *One insight per line. If it takes a paragraph, it's not distilled.*

**Protocol**: Append atomic learnings. Prune monthly. **250-line cap**.

**Transferred to CLAUDE.md** (2025-12-17): Core categorical, graceful degradation, testing, anti-patterns, and design heuristics. This file remains the append-only source; CLAUDE.md gets the curated subset.

**Pruned** (2025-12-23): Removed date-specific implementation notes, Living Docs details, Foundry specifics. Kept universal patterns. Dropped from 420→200 lines.

---

## The Four Pillars (Core Abstractions)

```
I.   AGENTESE          Paths ARE the API; observer-dependent projections
II.  D-gents           Categorical persistence; Universe + DataBus + verified optics
III. Galois/DP/ASHC    Value-encoded self-justification; design as optimization
IV.  Hypergraph/UX     Six-mode modal editing; K-Blocks; Trails; Marks
```

### Galois Insight
```
L(P) = d(P, C(R(P)))           # Information destroyed in restructuring
Low loss = self-justifying     # Axioms are fixed points where L ≈ 0
R_constitutional = 1 - L       # Reward = inverse of Galois loss
Seven layers from convergence  # L1-L7 emerge from restructuring depth
```

### UX Innovation
```
"The file is a lie. There is only the graph."
K-Block: monadic isolation until commit
Trail: semantic breadcrumb (not position history)
Mark: atomic witness with reasoning + principles
Six modes: NORMAL, INSERT, EDGE, VISUAL, COMMAND, WITNESS
```

---

## Documentation Roadmap (from Audit 2025-12-24)

### Priority 1: Task-to-Skill Routing (HIGH)
```
docs/skills/ROUTING.md - Decision tree + task taxonomy
Maps natural language tasks → skill combinations
```

### Priority 2: Quick-Reference Cards (HIGH)
```
docs/skills/_quickref/*.md - One per skill, <100 lines
Commands, decision trees, anti-patterns compressed
```

### Priority 3: Error Index (MEDIUM)
```
docs/ERRORS.md - Searchable error catalog
Error pattern → Skill section → Fix (one line each)
```

### Priority 4: Standardized Frontmatter (MEDIUM)
```yaml
# Every skill should have:
id: skill-name
prerequisites: [skill-a, skill-b]
enables: [skill-c]
difficulty: easy|medium|hard
```

### Priority 5: Expand Agent Skills (MEDIUM)
```
Add "For Agents" sections to: crown-jewel-patterns.md,
metaphysical-fullstack.md, test-patterns.md
JSON output formats, subprocess integration, agent workflows
```

---

## Learnings

### Categorical Foundations
```
Operads define grammar; algebras apply grammar to systems
Sheaf gluing = emergence: compatible locals → global
PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior
Turn projectors are natural transformations: preserve structure across CLI/TUI/JSON/marimo/SSE
Functor law verification proves composition: if laws pass, arbitrary nesting is safe
UI layout stability = sheaf gluing: local state (hover) → global constraint (fixed height)
```

### AGENTESE & Protocols
```
Three Phases (SENSE→ACT→REFLECT) compress 11 without loss
Turn is fundamental: single trace derives all panels (holographic)
K-gent = Governance Functor, not chatbot
Protocol > ABC: typing.Protocol enables duck typing without inheritance coupling
AD-012: Paths are PLACES (navigable), aspects are ACTIONS (invocable)—mixing causes 405 errors
Punchdrunk principle: collaboration > control; citizen refusal is core feature, not bug
@node runs at import time: If module not imported, node not registered
_invoke_aspect routes to methods: abstract in BaseLogosNode, concrete implementations in subclass
Never @property affordances(): BaseLogosNode.affordances() is a METHOD expecting (observer: AgentMeta)
_get_affordances_for_archetype() is the hook: override this, not affordances itself
```

### Reactive & Streaming
```
Flux > Loop: streams are event-driven, not timer-driven
Perturbation principle: invoke() on running flux injects, never bypasses
Streaming ≠ mutability: ephemeral chunks project immutable Turns
Signal generation monotonic: only increments on distinct value changes
>> and // operators: associative, flatten automatically, 100-widget chains in <10ms
Async generators must NOT be awaited: calling them returns generator directly
_invoke_aspect stream check: if aspect == "stream": return method() (no await)
Gateway _generate_sse wraps output: don't pre-format SSE in stream aspect—double-wrap bug
```

### Graceful Degradation
```
Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback
SSE over NATS: circuit breaker + fallback queue ensures degradation when NATS unavailable
Template fallbacks make CLI commands work without LLM
Optional dep stubs: no-op stubs for type-checking; document intent, not silent failure
Reserve space > conditional render: always render container, toggle content opacity
Maximum claim wins: if A claims 16px and B claims 24px, slot = 24px (all content must fit)
```

### Frontend Patterns
```
SSE stale closures: event handlers capture callbacks at creation; use refs for fresh handlers
Silent API failures kill UX: explicit loading/error/success states mandatory
Debug backend first: curl endpoint directly before blaming frontend
Immer MapSet: enable at app entry when Zustand stores use Map/Set—silent failures otherwise
StrictMode + WebSocket = double-mount: use refs to guard connect/disconnect
Stable body refs: JSON.stringify(body) in useMemo prevents object identity thrashing
Empty ResizeObserver mock breaks layout: callback never fires → context never updates
Global mock MUST call callback with dimensions: setup.ts mock fires synchronously with 1280x800
Test isolation via TestLayoutProvider: explicit context injection > mocked globals
Inline object props in useEffect: body={{ x }} creates new ref every render → infinite loop
```

### Testing & DevEx
```
DI > mocking: set_soul() injection pattern beats patch() for testability
Property-based tests catch edge cases: Hypothesis found boundary issues humans missed
Performance baselines as assertions: `assert elapsed < 1.0` catches regressions
Registry singleton + xdist: session-scoped fixtures in ROOT conftest.py ensure workers populated
Contract tests bridge type gaps: Python validators mirror TypeScript interfaces
Eager evaluation trap: header.get("path", fallback()) evaluates fallback even if key exists; use if/else
Test isolation via DI: _get_project_root() override > filesystem monkeypatch for temp fixture paths
PID-based database isolation: membrane_test_{pid}.db prevents SQLite lockups across agents
PYTEST_XDIST_WORKER + PYTEST_CURRENT_TEST: detect test environment, apply isolation
Session-scoped fixture resets engine singleton: each pytest session gets isolated DB
```

### Infrastructure
```
HTTP validation order: 400 before 403; record before check for rate limits
404 (not 403) for cross-tenant access: prevents tenant enumeration attack
FastAPI route order matters: specific routes must come before generic patterns
Three buses: DataBus (storage) → SynergyBus (cross-jewel) → EventBus (fan-out)
Bridge pattern: DataBus → SynergyBus via wire_data_to_synergy()
Fire-and-forget bus: asyncio.create_task for non-blocking SynergyBus events
DI Container pattern: Services dataclass wires all deps at startup—single source of truth, easy mocking
EventBus > direct calls: pub/sub decouples components, errors isolated per handler
Atomic persistence: temp file + rename is POSIX atomic—never corrupt state on crash
```

### Design Principles
```
Skills pull before doing, push after learning
Stigmergic surface: agents append, humans curate
Wiring > Creation: check if infrastructure exists before building new
Easter eggs hidden > announced: discovery is the delight
Teaching examples > reference docs: show the pattern in action
AGENTESE-first: all CLI commands route through Logos
Context.holon.aspect > flat verbs: ontological structure matters
Bounded queries: ?pattern with limit/offset prevents footguns
Pipeline fail_fast semantics: don't pass stale input to later stages after failure
Read-before-edit pattern: cache file content, reject edit if not cached
FileEditGuard singleton via DI: guards injected, never instantiated
```

### Crown Jewel Patterns
```
Container owns Workflow: Container persists, Workflows come and go
Signal Aggregation: multiple signals → confidence + reasons (transparent, composable)
Dual-Channel Output: emit(human, semantic) for humans + agents from same command
Bounded Trace: append + trim(50) = trajectory analysis without unbounded growth
Habitat Guarantee: ∀ path p: Habitat(p) ≠ ∅; no blank pages, no 404 behavior
Cache key = SHA256(normalized(intent, context)): deterministic, collision-resistant
Lazy-load dependencies: _get_classifier() pattern defers import until first use → faster startup
Frozen dataclasses for contracts: immutable boundaries between layers, enables safe composition
```

### Witness Primitives
```
Mark = atomic unit: every action auditable, replayable
Walk = session trace: anchored to Forest plans (kept for intuitive "going for a walk" feeling)
Playbook = lawful workflow: gated by Grant, verified by laws
VoiceGate = trust-gated output: L0-L3 determines expression
Law 3 at gateway: _invoke_path() emits Mark—all AGENTESE paths traced automatically
Two visions coexist: self.witness (trust agency) + time.witness (crystallization)
SILENT ≠ DORMANT: Muse actively observes in SILENT; DORMANT is cooldown
WitnessSheaf glues event sources: EventSource × LocalObservation → ExperienceCrystal
Pipeline >> Step: associative composition, category laws verified
Trust gating hierarchy: L0 read-only, L1 bounded, L2 confirm, L3 autonomous
Walk outlives Session: Walk persists after session ends for audit (Law 2)
SessionWalkBridge: CLI session can have at most one Walk (Law 1), optional binding (Law 3)
```

### Metabolic Development
```
Diversity > Count: 10 diverse runs > 100 identical runs for evidence confidence
DiversityScore = unique_inputs / total_runs: prevents confidence inflation
InputSignature hashes (file_content, test_focus, context): deduplication across runs
BackgroundEvidencing fire-and-forget: asyncio.create_task for non-blocking verification
Critical failure = >50% test failure rate: only surface regressions, not minor issues
Stratigraphy layers: SURFACE (0-1d), SHALLOW (2-14d), FOSSIL (>14d)—age determines wisdom value
Circadian resonance: same weekday > adjacent day for morning matching (Monday Kent ≠ Friday Kent)
Serendipity from FOSSIL only: >14 days old = unexpected, not familiar
10% serendipity trigger: random.random() > 0.9 for accursed share wisdom
```

### ASHC (Automated Self-Healing Code)
```
Behavioral isomorphism > textual: compare behavior (laws, tests), not code text
check_isomorphism must be async: instance.invoke() is async, can't use run_until_complete()
Post-process > pytest plugin: simpler, testable, decoupled
Bounded context (5 lines max): prevents obligation bloat, faster proof search
Pattern-based variable extraction: readable properties > AST dumps
LemmaDatabase protocol > concrete class: DI for testing, D-gent persistence later
Failed tactics as stigmergic anti-pheromone: track separately, inform future attempts
Temperature as hyper-parameter: in config, not hardcoded
Heritage hints from spec: polynomial, composition, identity patterns as LLM guidance
Three Gatekeepers: Dafny (imperative/Z3), Lean4 (mathematical), Verus (Rust/linear types)
Protocol > ABC for checkers: duck typing enables polymorphic ProofSearcher injection
Lazy registry instantiation: register(name, class), instantiate on first get()—startup cost avoided
Dafny stderr on success: parse exit code, not output presence
Z3 timeout unreliable: --resource-limit more reliable than --verification-time-limit
Verus verus! impl gotcha: blocks inside impl sections SILENTLY IGNORED—wrap entire impl
Zombie reaping essential: await proc.wait() after proc.kill() or process table fills
sorry = incomplete: Lean4 proofs with sorry treated as FAILED (not just warning)
Stigmergic decay ≠ evidence decay: different mechanisms, run together in decay cycle
Half-life formula for stigmergic: confidence' = confidence * 0.5^(days / halflife)
```

### AD-015 Radical Unification
```
LedgerCache → ProxyHandleStore: Delete ad-hoc caches, unify via singleton proxy store
ensure_scanned() → get_or_raise(): Explicit data requirement, NoProxyHandleError if missing
analyze_now() → compute(): Explicit computation with TTL, provenance, event transparency
Reactive invalidation via ProxyReactor: Spec deprecation events auto-invalidate handles
One truth, one store: All Crown Jewels can share ProxyHandleStore for computed data
```

---

## Anti-Patterns

```
Silent catch blocks: swallowing errors shows blank UI; always surface
Generator Trap: pickle can't serialize stack frames
Timer-driven loops create zombies
Bypassing running loops causes state schizophrenia
Context dumping: large payloads tax every turn
Full ouroboros (feedback=1.0) → solipsism
Bypassing cache check: classification is expensive; always check cache FIRST
Caching by intent alone: context affects behavior; hash (intent, context) together
Force LOCAL for CHAOTIC: security violation; CHAOTIC → WASM unconditionally
Mutable contracts: Request/Response should be frozen dataclasses; prevents cross-layer mutation
Shadowing with @property affordances: causes 'tuple not callable' error
```

---

### Unified Data Spine (2025-12-25)
```
Crystal→K-Block: Crystals ARE K-Blocks with isolation=SEALED; unify storage
Upload→Layer: Always assign layer on ingest; editable suggestion pattern
Edge dual storage: Normalized + JSONB for performance; EdgeSyncService maintains consistency
Mark→K-Block linkage: target_kblock_id field enables join queries
Feed/Meta layer-aware: Layers optional filter; Meta reads galois_loss from K-Block
Single source of truth: K-Block table is spine; all systems project from it
```

---

### Constitutional Decision OS (2025-12-26)
```
Amendment A: ETHICAL as floor constraint (≥0.6), not weighted principle
Literature: L(P) = d(P, C(R(P))) is NOT novel formula — novel APPLICATION
Pilot-first: Every week validates infrastructure THROUGH a pilot, not in isolation
Joy calibration: FLOW (productivity), WARMTH (consumer), SURPRISE (creative)
5 pilots: trail-to-crystal (wedge), wasm-survivors, disney-portal, rap-coach, sprite-procedural
Consumer-first: Ship trail-to-crystal before Galois API; enterprise deferred until design partner
Super-additivity: L(A∪B) > L(A) + L(B) + τ signals contradiction
Ghost preservation: Unchosen paths remain inspectable for audit
Compression honesty: Crystal must disclose what was dropped
```

### Coherence Synthesis Integration (2025-01-10)
```
R = 1 - L: Design axiom (reward = 1 - Galois loss), validated ρ = 0.8346
Kent-calibrated tiers: CATEGORICAL (L<0.10), EMPIRICAL (L<0.38), AESTHETIC (L<0.45), SOMATIC (L<0.65), CHAOTIC (≥0.65)
Content layers: AXIOM → VALUE → SPEC → TUNING mapped from tiers
PilotBootstrapper: From axioms to laws in hours, not weeks
validate_axiom_candidate(): Galois loss < 0.10 = axiom
classify_content_layer(): Deterministic layer from loss
HoTT conceptual model: Python classes for paths, not machine-verified proofs
LeanExporter: Generates Lean 4 with `sorry` stubs for future formal proofs
CategoricalLawVerifier: Tests associativity, identity laws via HoTT path construction
Evidence.galois_loss: Now integrated into ASHC equivalence_score
galois_coherence property: 1 - galois_loss (the unifying equation)
15 coherence tests: Cross-system verification R = 1 - L holds
```

### Aggressive Cleanup Protocol (2025-12-26)
```
One truth source: plans/enlightened-synthesis/ replaces 20+ scattered docs
Archive don't delete: _archive/2025-12-26-cleanup/ preserves history
NOW.md ceiling: 200 lines max (was 425)
HYDRATE.md ceiling: 150 lines max
Redundant doc detection: If absorbed into synthesis, archive immediately
```

---

## Unanswered

```
DensityField animation: 30fps always or only when focused?
Servo embedding vs Electron: which path for desktop app?
```

---

*Lines: 240/250 | Last updated: 2025-12-26 | Constitutional Decision OS + Cleanup Protocol added*
