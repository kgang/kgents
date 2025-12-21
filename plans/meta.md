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
```

### Foundry Phase 3: Marimo Projector (2025-12-21)
```
Marimo cell = self-contained Python: embed Agent ABC, source, and runtime in single output
mo.ui.text_area + mo.ui.run_button: minimal interactive pattern for agent exploration
Decorator stripping mandatory: @Capability.* not available in marimo runtime, strip before embed
asyncio.run() for sync marimo cells: marimo cells are sync, wrap async agent.invoke()
Capability badge pattern: stateful • streaming • observable or "minimal" for plain agents
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
```

---

## Unanswered

```
DensityField animation: 30fps always or only when focused?
Servo embedding vs Electron: which path for desktop app?
```

---

*Lines: ~250/200 | Last updated: 2025-12-21 | Foundry Phase 3 Complete*
