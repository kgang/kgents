---
path: self.forest.plan.meta
mood: pruned
momentum: 0.8
trajectory: steady
season: BLOOMING
last_gardened: 2025-12-20
gardener: claude-opus-4
---

# meta.md — Mycelium

> *One insight per line. If it takes a paragraph, it's not distilled.*

**Protocol**: Append atomic learnings. Prune monthly. **200-line cap**.

**Transferred to CLAUDE.md** (2025-12-17): Core categorical, graceful degradation, testing, anti-patterns, and design heuristics. This file remains the append-only source; CLAUDE.md gets the curated subset.

**Pruned** (2025-12-20): Removed date-specific implementation notes (Dec 16-20). Work is complete, learnings captured. Dropped from 491→200 lines.

---

## Learnings

### Categorical Foundations
```
Operads define grammar; algebras apply grammar to systems
Sheaf gluing = emergence: compatible locals → global
PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior
Turn projectors are natural transformations: preserve structure across CLI/TUI/JSON/marimo/SSE
Functor law verification proves composition: if laws pass, arbitrary nesting is safe
```

### AGENTESE & Protocols
```
Three Phases (SENSE→ACT→REFLECT) compress 11 without loss
Turn is fundamental: single trace derives all panels (holographic)
K-gent = Governance Functor, not chatbot
Protocol > ABC: typing.Protocol enables duck typing without inheritance coupling
AD-012: Paths are PLACES (navigable), aspects are ACTIONS (invocable)—mixing causes 405 errors
Punchdrunk principle: collaboration > control; citizen refusal is core feature, not bug
```

### Reactive & Streaming
```
Flux > Loop: streams are event-driven, not timer-driven
Perturbation principle: invoke() on running flux injects, never bypasses
Streaming ≠ mutability: ephemeral chunks project immutable Turns
Signal generation monotonic: only increments on distinct value changes
>> and // operators: associative, flatten automatically, 100-widget chains in <10ms
```

### Graceful Degradation
```
Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback
SSE over NATS: circuit breaker + fallback queue ensures degradation when NATS unavailable
Template fallbacks make CLI commands work without LLM
Optional dep stubs: no-op stubs for type-checking; document intent, not silent failure
```

### Frontend Patterns
```
SSE stale closures: event handlers capture callbacks at creation; use refs for fresh handlers
Silent API failures kill UX: explicit loading/error/success states mandatory
Debug backend first: curl endpoint directly before blaming frontend
Immer MapSet: enable at app entry when Zustand stores use Map/Set—silent failures otherwise
StrictMode + WebSocket = double-mount: use refs to guard connect/disconnect
Stable body refs: JSON.stringify(body) in useMemo prevents object identity thrashing
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
```

### Infrastructure
```
HTTP validation order: 400 before 403; record before check for rate limits
404 (not 403) for cross-tenant access: prevents tenant enumeration attack
FastAPI route order matters: specific routes must come before generic patterns
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
```

### Crown Jewel Patterns
```
Container owns Workflow: Container persists, Workflows come and go
Signal Aggregation: multiple signals → confidence + reasons (transparent, composable)
Dual-Channel Output: emit(human, semantic) for humans + agents from same command
Bounded Trace: append + trim(50) = trajectory analysis without unbounded growth
Habitat Guarantee: ∀ path p: Habitat(p) ≠ ∅; no blank pages, no 404 behavior
```

### Witness Primitives (2025-12-20)
```
Vocabulary: TraceNode→Mark, Walk (unchanged), Ritual→Playbook, Covenant→Grant, Offering→Scope, Terrace→Lesson
Mark = atomic unit: every action auditable, replayable
Walk = session trace: anchored to Forest plans (kept for intuitive "going for a walk" feeling)
Playbook = lawful workflow: gated by Grant, verified by laws
VoiceGate = trust-gated output: L0-L3 determines expression
Law 3 at gateway: _invoke_path() emits Mark—all AGENTESE paths traced automatically
Fire-and-forget bus: asyncio.create_task for non-blocking SynergyBus events
```

### Witness/Muse (2025-12-20)
```
Two visions coexist: self.witness (trust agency) + time.witness (crystallization)
SILENT ≠ DORMANT: Muse actively observes in SILENT; DORMANT is cooldown
WitnessSheaf glues event sources: EventSource × LocalObservation → ExperienceCrystal
Pipeline >> Step: associative composition, category laws verified
Trust gating hierarchy: L0 read-only, L1 bounded, L2 confirm, L3 autonomous
```

### CLI v7 Conductor (2025-12-20)
```
Read-before-edit pattern: cache file content, reject edit if not cached
FileEditGuard singleton via DI: guards injected, never instantiated
Synergy events for file ops: FILE_READ, FILE_EDITED enable cross-jewel awareness
Conductor ≠ kgentsd: Conductor orchestrates sessions; kgentsd watches + acts
Demo aspect pattern: self.X.demo spawns simulated behavior—validate joy before polish
CursorBehavior personality: follow_strength + exploration_tendency = heterarchical agents
BehaviorAnimator: organic noise via sin combination, not just random (feels alive)
SwarmRole = Behavior × Trust: capabilities from trust, personality from behavior
A2A via WitnessSynergyBus: messages ARE events—reuse existing infrastructure
ConductorFlux: unified cross-phase event routing, single subscription point
SessionWalkBridge: CLI session can have at most one Walk (Law 1), optional binding (Law 3)
Walk outlives Session: Walk persists after session ends for audit (Law 2)
RitualNode real stores: Look up Covenant/Offering from global stores, fallback to stubs gracefully
```

### Servo/TerrariumView (Session 7)
```
Graceful degradation: React component null-check props with ?? fallbacks
Contract tests verify Python JSON matches TypeScript interfaces—catches drift
time.walk.list returns SceneGraph directly—no intermediate transform needed
Edge case tests (unicode, empty, long content) found no bugs—converters robust
WalkStatus styling lookup: fallback to ACTIVE if status unknown
```

### Witness Spec Cleanup (2025-12-20)
```
Keep TerrariumView, LensMode: established metaphor, tests passing—don't rename unnecessarily
Walk≠Arc: spec had backwards compat alias error; Walk stays Walk per rename map
Domain laws vs Category laws: Lesson laws are domain-specific (immutability, versioning), not category laws (identity, associativity)
Rename scope: Phase 1 core = TraceNode→Mark, Ritual→Playbook, Covenant→Grant, Offering→Scope, Terrace→Lesson
```

### Layout Sheaf (2025-12-20)
```
UI layout stability = sheaf gluing: local state (hover) → global constraint (fixed height)
Reserve space > conditional render: always render container, toggle content opacity
Maximum claim wins: if A claims 16px and B claims 24px, slot = 24px (all content must fit)
Transient claims reserve on mount, not activation: prevents layout shift when content appears
```

### ASHC Phase 5: Bootstrap Regeneration (2025-12-21)
```
Behavioral isomorphism > textual: compare behavior (laws, tests), not code text
SpecParser extracts laws via pattern matching: "Laws:" headers + math symbols (= ≡)
check_isomorphism must be async: instance.invoke() is async, can't use run_until_complete()
Regeneration n_variations > 1: LLM variance means multiple samples needed for confidence
```

### ResizeObserver Mock Fix (2025-12-21)
```
Empty ResizeObserver mock breaks layout-dependent components: callback never fires → context never updates
Global mock MUST call callback with dimensions: setup.ts mock fires synchronously with 1280x800
Context-dependent rendering needs deterministic context: useLayoutContext() returns DEFAULT_CONTEXT until ResizeObserver fires
Test isolation via TestLayoutProvider: explicit context injection > mocked globals (tests/utils/testProviders.tsx)
```

### Foundry Phase 1: Projector Composition (2025-12-21)
```
Monkey-patch >> operator via setattr: avoids modifying base.py, clean separation of compose.py
DockerArtifact struct carries metadata: downstream projectors need image_name, ports, volumes
Composed projector injects upstream artifact: K8s manifest gets Docker image reference automatically
IdentityProjector satisfies composition laws: Id >> P ≡ P for testing and pipelines
```

### Living Docs Reference Generation (2025-12-21)
```
Teaching: section with gotcha: keyword enables extraction: pattern match, not section parsing
AGENTESE: path in docstrings enables navigation: cross-reference to protocol invocation
_tests/ exclusion critical: without it, test files inflate doc count 2x
Tier determination expanded: agents/ and protocols/ now RICH tier (not just services/)
_parse_docstring returns 4-tuple: (summary, examples, teaching, agentese_path)
SpecExtractor for markdown: ## headers as symbols, code blocks as examples
Anti-patterns → warning severity, Laws → critical severity: semantic mapping matters
Spec categories integrate via _extract_spec_category: separate iteration for markdown files
Combined docs: 8,243 DocNodes (7,609 code + 634 spec), 937 examples, 79 teaching moments
Phase 3 generate_to_directory: GenerationManifest tracks all files + totals
Category pages group by module: by_module dict → ## headers for each module
No-overwrite default: check filepath.exists() before writing—prevents clobbering
Phase 4-5: Iterator-based TeachingCollector > database—lightweight, composes with extractors
Evidence verification: resolve test_file.py::test_name by globbing _tests/**/<file>.py
CLI thin routing: docs.py routes to teaching.py—follows brain_thin.py pattern
Phase 6 hydrator: keyword-based matching now, semantic via Brain vectors is future work
HydrationContext.to_markdown() optimized for Claude: gotchas → modules → voice anchors
Voice anchors curated from _focus.md: don't mine from git, preserve authentic Kent voice
relevant_for_file() extracts keywords from path parts: services/brain/core → ["brain", "core"]
Doc backfill Phase 3: D-gent 6 gotchas, M-gent 6 gotchas, Sheaf 5 gotchas—17 total for categorical layer
```

### Foundry Phase 3: Marimo Projector (2025-12-21)
```
Marimo cell = self-contained Python: embed Agent ABC, source, and runtime in single output
mo.ui.text_area + mo.ui.run_button: minimal interactive pattern for agent exploration
Decorator stripping mandatory: @Capability.* not available in marimo runtime, strip before embed
asyncio.run() for sync marimo cells: marimo cells are sync, wrap async agent.invoke()
Capability badge pattern: stateful • streaming • observable or "minimal" for plain agents
```

### Foundry Phase 4: Agent Foundry Service (2025-12-21)
```
Crown Jewel Pattern: core.py (orchestrator), node.py (@node), polynomial.py (state), operad.py (grammar), contracts.py (types)
Forge pipeline: cache check → classify → generate → validate → select → project → cache → return
LRU cache with TTL: bounded memory, metrics tracking for promotion decisions
Mypy match-case quirk: unique variable names per case required (request1, request2 not request, request)
Safety forcing is unconditional: CHAOTIC reality OR unstable code → WASM (no exceptions, no overrides)
Cache key = SHA256(normalized(intent, context)): deterministic, collision-resistant, enables later inspection
Lazy-load dependencies: _get_classifier() pattern defers import until first use → faster startup
Frozen dataclasses for contracts: immutable boundaries between layers, enables safe composition
Rendering classes separate concerns: ForgeRendering.to_text() for CLI, to_dict() for JSON
Polynomial defines direction sets: _foundry_directions(state) returns valid events per state → type-safe FSM
```

### Metabolic Development (2025-12-21)
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
Pattern detection without ML: key phrase matching + occurrence counting across voices
brain_adapter.find_prior_evidence() wired to BackgroundEvidencing: stub → real implementation
MetabolismPersistence: single D-gent layer for evidence + insights + stigmergy traces
Persistence param injection: BackgroundEvidencing(persistence=...) + fallback to JSON if None
```

### ASHC Proof Generation Phase 2 (2025-12-21)
```
Post-process > pytest plugin: simpler, testable, decoupled—plugin can come in Phase 5
Bounded context (5 lines max): prevents obligation bloat, faster proof search
Pattern-based variable extraction: readable properties > AST dumps
UUID-based obligation IDs: globally unique, session-independent
```

### ASHC Proof Generation Phase 3 (2025-12-21)
```
LemmaDatabase protocol > concrete class: DI for testing, D-gent persistence later
Failed tactics as stigmergic anti-pheromone: track separately, inform future attempts
Temperature as hyper-parameter: in config, not hardcoded—per Kent's decision
Heritage hints from spec: polynomial, composition, identity patterns as LLM guidance
Prompt determinism: sorted failed_tactics, bounded hints, stable structure
```

### Doc Backfill Phase 4: Interactive Text (2025-12-21)
```
Added interactive_text + liminal to CATEGORIES: missing services = no gotcha extraction
Teaching totals: 116→165 (+49), critical: 20→31 (+11), evidence verified: 103→150
TokenRegistry ClassVar singleton: class-level state shared across instances—clear() in tests
DocumentEventBus fire-and-forget: asyncio.create_task + _safe_notify swallows exceptions
ProjectionFunctor laws: _compose() is target-specific (CLI=newlines, JSON=arrays, Web=nesting)
Ghost tokens have reduced affordances: is_ghost=True disables invoke/navigate gracefully
```

### Memory-First Docs: Crystallization (2025-12-21)
```
Deterministic ID = f"teach-{module}-{symbol}-{insight_hash[:12]}": idempotent deduplication
TeachingCrystal provenance: source_module, source_symbol, evidence, born_at for full trace
Query patterns: get_alive_teaching(), get_teaching_by_module(prefix), get_ancestral_wisdom()
TeachingCrystallizer bridges Living Docs → Brain: collector.collect_all() → brain.crystallize_teaching()
Async container.resolve() in crystallize_all_teaching(): must await, not sync call
New model tables need init_db(): UndefinedTableError → run asyncio.run(init_db()) to create
PostgreSQL asyncpg strict on timezones: DateTime column + datetime.now(UTC) → DataError; use func.now() default instead
ID length must fit String(64): hash full content, not embed readable strings—"t-{sha256[:50]}" pattern
```

### ASHC Phase 5: Checker Bridges (2025-12-21)
```
Three Gatekeepers: Dafny (imperative/Z3), Lean4 (mathematical), Verus (Rust/linear types)
Protocol > ABC for checkers: duck typing enables polymorphic ProofSearcher injection
Lazy registry instantiation: register(name, class), instantiate on first get()—startup cost avoided
Dafny stderr on success: parse exit code, not output presence
Z3 timeout unreliable: --resource-limit more reliable than --verification-time-limit for Dafny/Verus
Lean4 bare vs lake: `lake env lean` for projects, bare `lean` for standalone files
Verus verus! impl gotcha: blocks inside impl sections SILENTLY IGNORED—wrap entire impl
Zombie reaping essential: await proc.wait() after proc.kill() or process table fills
sorry = incomplete: Lean4 proofs with sorry treated as FAILED (not just warning)
Noisy error cascades (Dafny): first error is key, subsequent often red herrings
```

### Derivation Framework Phase 4: Decay & Refresh (2025-12-22)
```
Stigmergic decay ≠ evidence decay: different mechanisms, run together in decay cycle
ActivityRecord tracks last_active timestamp: decay based on inactivity, not low usage
Grace period (14 days default): recently active agents don't decay even if usage is low
ASHC refresh is optional: if no runner, skips without failing the decay cycle
run_decay_cycle is idempotent: safe to run daily via cron or scheduler
Half-life formula for stigmergic: confidence' = confidence * 0.5^(days / halflife)
DecayConfig for tunable parameters: half-life, thresholds, floors all configurable
Explicit type annotations for mypy: float annotations prevent "Returning Any" errors
```

### SSE Streaming via AGENTESE (2025-12-22)
```
Async generators must NOT be awaited: calling them returns generator directly, await fails
_invoke_aspect stream check: if aspect == "stream": return method() (no await)
Gateway _generate_sse wraps output: don't pre-format SSE in stream aspect—double-wrap bug
Stream aspects yield raw dicts: let gateway format with `data: {json}\n\n`
AGENTESE SSE URL pattern: /{context}/{holon}/{aspect} not /{aspect}/stream
Vite proxy works for SSE: no special config needed, just standard /agentese proxy
```

### Node Affordances Pattern (2025-12-22)
```
Never @property affordances(): BaseLogosNode.affordances() is a METHOD expecting (observer: AgentMeta) → list
Shadowing with @property causes 'tuple not callable': self.affordances(meta) fails
_get_affordances_for_archetype() is the hook: override this, not affordances itself
COLLABORATION_AFFORDANCES should NOT include 'manifest': it's already in _base_affordances
```

### ZenPortal Audit (2025-12-22)
```
DI Container pattern: Services dataclass wires all deps at startup—single source of truth, easy mocking
Atomic persistence: temp file + rename is POSIX atomic—never corrupt state on crash
EventBus > direct calls: pub/sub decouples components, errors isolated per handler
Vim navigation (j/k): reduces hand travel, matches terminal muscle memory
Copy confirmation: silent ops = user uncertainty; use Garden + notify() for feedback
Elastic width: truncate labels gracefully based on available space—never overflow
Status glyphs (▪/▫): scannable at glance, language-independent, compact
Notification toasts: bottom-left, 3s auto-dismiss, non-blocking feedback
Selection persistence: save selected_session_id + session_order separately from data
Human-friendly age: "3m", "1h", "2d" > ISO timestamps for daily-use UX
Async service separation: sync wrapper + asyncio.to_thread() keeps UI responsive
Graceful degradation via tuples: (result, error) never raises—caller decides
Active pane indicator: reverse video title > subtle border change (unmistakable)
SelectablePane base class: extract j/k/1-9/enter logic once, reuse everywhere
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
Inline object props in useEffect: body={{ x }} creates new ref every render → infinite loop
Bypassing cache check: classification is expensive; always check cache FIRST
Caching by intent alone: context affects behavior; hash (intent, context) together
Force LOCAL for CHAOTIC: security violation; CHAOTIC → WASM unconditionally
Mutable contracts: Request/Response should be frozen dataclasses; prevents cross-layer mutation
```

---

## Unanswered

```
DensityField animation: 30fps always or only when focused?
Servo embedding vs Electron: which path for desktop app?
```

### Git Archaeology → Witness → ASHC (2025-12-22)
```
CommitTeaching → Mark: teaching.insight → response.content, commit.sha → proof.data, category → tags
Deterministic mark IDs: arch-{sha[:8]}-{hash[:8]} for idempotent crystallization re-runs
GENEALOGICAL evidence tier: git history is evidence of past decisions (spec/protocols/witness-supersession.md)
Principle inference from category: gotcha→ethical, pattern→composable+generative, decision→tasteful
_invoke_aspect routes to methods: abstract in BaseLogosNode, concrete implementations in subclass
BasicRendering(summary=str): expects string, not dict; use custom rendering dataclasses with to_dict/to_text
Umwelt[Any, Any] > Observer for node methods: Observer is for lightweight calls, Umwelt for full invocations
concept.compiler.priors bridges archaeology→ASHC: extract priors → seed CausalLearner → 8 edges from 100 commits
Archaeological confidence discount 50%: correlational not causal; use as initial priors, let runtime evidence accumulate
```

---

*Lines: ~400/200 | Last updated: 2025-12-22 | Git Archaeology Phase 6 Complete*
