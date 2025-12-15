---
path: plans/meta
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# meta.md — Mycelium

> *One insight per line. If it takes a paragraph, it's not distilled.*

**Protocol**: Append atomic learnings. Prune monthly. 200-line cap.

---

## Learnings

```
2025-12-14  Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback
2025-12-14  Cross-agent import OK: Town→K-gent LLM; reuse > duplicate
2025-12-14  Async migration: make _execute_* async first, then update tests
2025-12-13  Three Phases (SENSE→ACT→REFLECT) compress 11 without loss
2025-12-13  Turn is fundamental: single trace derives all panels (holographic)
2025-12-13  Posture is polynomial: (phase, activity) → symbol
2025-12-13  Weather metaphors: entropy=clouds, queue=pressure, tokens=temperature
2025-12-13  Two-tier collection: try context, fallback direct; graceful degradation
2025-12-13  Operads define grammar; algebras apply grammar to systems
2025-12-13  Sheaf gluing = emergence: compatible locals → global
2025-12-13  LLM-once cheap: pre-compute, hotload forever (AD-004)
2025-12-12  Skills pull before doing, push after learning
2025-12-12  Purgatory > Generator: eject state as data, not pause frames
2025-12-12  Flux > Loop: streams are event-driven, not timer-driven
2025-12-12  Perturbation principle: invoke() on running flux injects, never bypasses
2025-12-12  Store Comonad > State Monad for context
2025-12-12  Projector ≠ lens: compression violates Get-Put
2025-12-12  K-gent = Governance Functor, not chatbot
2025-12-12  Symmetric lifting: every functor needs lift() AND unlift()
2025-12-12  Stigmergic surface: agents append, humans curate
2025-12-12  PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior
2025-12-11  T/U split: testing vs tools is categorical
2025-12-11  OCap for trust: BypassToken is unforgeable
2025-12-13  Wiring is composition: factory→factory→node forms morphism chain
2025-12-13  Mock+Real test pairs: isolation tests + integration verification
2025-12-13  Graceful degradation: return informative errors, don't crash
2025-12-14  Streaming ≠ mutability: ephemeral chunks project immutable Turns
2025-12-14  Forest handles: plans ARE handles; epilogues ARE witnesses; dormant = accursed share
2025-12-14  Phase condensation: SENSE→ACT→REFLECT allows merging (e.g., DEVELOP+IMPLEMENT)
2025-12-14  CLI dialogue: registry pattern + fallback routing keeps match statement clean
2025-12-14  Duck typing (hasattr) bridges different agent protocols (dialogue vs invoke)
2025-12-14  Re-metabolize reveals health: 0% drift when all sections present
2025-12-14  Reactive substrate: pure entropy + time-downward + projections = deterministic widgets
2025-12-14  Auto-inducer signifiers: ⟿ (continue) / ⟂ (halt) make continuation generators self-executing
2025-12-14  Enum identity breaks on reload: compare `.value`, not `is`
2025-12-14  DI > mocking: `set_soul()` injection pattern beats `patch()` for testability
2025-12-14  HTTP validation order: 400 (bad request) before 403 (forbidden); record before check for rate limits
2025-12-14  Re-metabolize reveals health: 22 skills, 5% drift, all holograms present, laws preserved
2025-12-14  REPL observer wrapper: frozen Umwelt needs mutable wrapper for cache tracking
2025-12-14  REPL architecture: Logos → CLI fallback enables graceful degradation across maturity levels
2025-12-14  REPL test categories: observer/navigation/pipeline/error/introspection/completion/rendering/degradation/state/integration
2025-12-14  Ruff autofix: import sorting + f-string cleanup accelerates QA
2025-12-14  marimo > Textual for visualization: reactive DAG maps to citizen state changes
2025-12-14  k-clique percolation: overlapping coalitions via shared k-1 nodes (k=3 for town)
2025-12-14  EigenTrust: reputation weighted by assigner's reputation solves sybil, converges
2025-12-14  LLM budget rule: evolving citizens + archetype leaders only (3-5 of 25)
2025-12-14  Redis reuse: triad-redis already available; don't deploy new when existing suffices
2025-12-14  Alerting in runbook: extract rules from docs before creating new; Phase 4 runbook had them
2025-12-14  Archetype factory pattern: create_archetype() → composable citizen creation with defaults
2025-12-14  7D eigenvector metric laws: identity, symmetry, triangle—preserved by drift() method
2025-12-14  kustomize commonLabels pollute podSelector; use labels+includeSelectors:false for network policies
2025-12-14  Easter eggs hidden > announced: discovery is the delight, not the feature list
2025-12-14  Rate limiting K-gent: 30s cooldown prevents token burn on philosophical tangents
2025-12-14  Widget functor law: scatter.map(f) ≡ scatter.with_state(f(state))—enables filter composition
2025-12-14  NATS subject schema: town.{town_id}.{phase}.{operation} supports wildcards at each level
2025-12-14  SSE over NATS: circuit breaker + fallback queue ensures graceful degradation when NATS unavailable
2025-12-14  Protocol > ABC: typing.Protocol allows duck typing without inheritance coupling
2025-12-14  Sparkline is a "sink"—composes on left only, never on right (terminal output)
2025-12-14  Soul+Shadow bridge natural: introspection → projection analysis flows semantically
2025-12-14  Pipeline presets reduce cognitive load for common composition patterns
2025-12-14  Template fallbacks make CLI commands work without LLM (graceful degradation)
2025-12-14  Slash shortcuts (/cmd) map to AGENTESE paths—preserves semantics, adds ergonomics
2025-12-14  Render sub-millisecond: 0.03ms p50 for 25-citizen scatter—measure before optimizing
2025-12-14  Meta-skill pattern: threshold=0 + empty demos → prerequisite-only mastery
2025-12-14  Mastery as meta-skill: unlock via all prerequisites mastered, not demos
2025-12-14  CROSS-SYNERGIZE is law verification: existing tests suffice; no new code needed to prove laws
2025-12-14  SLI before code: document targets before implementing metrics—drives alert threshold design
2025-12-14  marimo LogosCell pattern IS AgenteseBridge pattern—direct mapping, no adapter layer needed
2025-12-14  Sessions NATS publishing already aligns with AUP subscribe channels—zero new wire work
2025-12-14  Agent Town GardenState ≡ AUP GardenState—no translation layer needed
2025-12-14  TUI remote mode DEFERRED not BLOCKED—local TUI continues working independently
2025-12-14  Teaching examples > reference docs: show the pattern in action, not just describe it
2025-12-14  Runbook-first: write operator docs before infrastructure—surfaces edge cases early
2025-12-14  Counter-metrics force harm-thinking: "what makes this feature bad?" reveals blind spots
2025-12-14  Dashboard sketch before infra: if you can't draw it, you don't understand it
2025-12-14  SVG > Canvas for <100 elements: native click handling, CSS transitions, no hit-testing
2025-12-14  Non-blocking webhook: asyncio.create_task() for fire-and-forget ingestion
2025-12-14  Idempotency pattern: in-memory store (MVP) → Redis (production) with TTL
2025-12-14  Latency growth as memory leak proxy: simpler than direct measurement in soak tests
2025-12-14  PDB essential: prevents all-pod eviction during node drains
2025-12-14  Runbook URLs in alerts reduce MTTR: operator jumps directly to procedure
2025-12-14  404 (not 403) for cross-tenant access: prevents tenant enumeration attack
2025-12-14  Wiring > Creation: check if infrastructure exists before building new (Phase 2)
2025-12-14  Binary fallback: operations gracefully degrade to solo when only 1 participant
2025-12-14  Right to Rest: citizen polynomial RESTING phase accepts only WakeInput—uninterruptible
2025-12-14  Archetype eigenvector bias: spec → variance(0.1) → citizen; biases compound at coalition level
2025-12-14  k-clique percolation: k=3 for towns; scales to ~100 citizens before O(n²) dominates
2025-12-14  CROSS-SYNERGIZE verdict: direct import when protocol matches; pattern reuse when memory model differs
2025-12-14  Glyph grammar: middle dot (·) > period; box-drawing chars (═ ─ │) add polish
2025-12-14  Viewport windowing: render subset of grid for cleaner CLI output
2025-12-14  Bridge pattern: environment → scatter → isometric is clean functor chain
2025-12-14  QA edge cases reveal working graceful degradation: budget → cached → template cascade reliable
2025-12-14  FastAPI route order matters: specific routes (e.g., /town/{id}/init) must come before generic patterns (/{context}/{holon}/*)
2025-12-14  Kind image loading: use versioned tags (v2, v3) to force pod recreation; imagePullPolicy=IfNotPresent caches aggressively
2025-12-14  Signal generation monotonic: only increments on distinct value changes—enables change detection
2025-12-14  Snapshot captures (value, timestamp, generation): restore notifies subscribers but generation continues forward
2025-12-14  Computed lazy: only recomputes on access after invalidation—saves CPU on unused derivations
2025-12-14  Effect cleanup pattern: return cleanup fn from effect fn; called before next run and on dispose
2025-12-14  ModalScope merge strategies map to git: SUMMARIZE≈squash+message, REBASE≈replay, SQUASH≈single commit
2025-12-14  Turn projectors are natural transformations: Turn → CLI/TUI/JSON/marimo/SSE preserve structure
2025-12-14  Property-based tests catch edge cases: Hypothesis found boundary issues humans missed
2025-12-14  Performance baselines as assertions: `assert elapsed < 1.0` catches regressions automatically
2025-12-14  Wave 1 reactive: 591 tests in 4.71s; sub-10ms per test enables fast CI feedback
2025-12-15  JetStream StreamConfig: omit max_age for defaults; large nanosecond values cause "invalid JSON" (10025)
2025-12-15  NetworkPolicy cross-namespace: label target namespace with ingress selector (kgents.io/tier=gateway)
2025-12-15  Stream pre-creation: when auto-create fails, manually create minimal config then restart deployment
2025-12-15  Dev API keys built-in: kg_dev_alice (FREE/read), kg_dev_bob (PRO/rw), kg_dev_carol (ENTERPRISE/admin)
2025-12-15  NATS circuit breaker works: fallback mode serves requests while reconnecting; health endpoint shows status
2025-12-15  Composition tiering: primitives first (atomic), then composites (cards), defer 2D grids (semantic mismatch)
2025-12-15  Layout presets > manual composition: metric_row(), panel(), status_row() reduce cognitive load
2025-12-15  Projection = batteries: developers design state, not rendering; CLI/TUI/marimo/JSON/VR are targets
2025-12-15  StatefulWidget protocol: use Protocol[S] for widgets with `.state` to enable law verification without inheritance
2025-12-15  Registry singleton + reset(): class-level state works with pytest fixtures via reset() for test isolation
2025-12-15  Functor law verification proves composition: if laws pass, arbitrary nesting is safe
2025-12-15  Wave 2.1 >> and // operators: associative, flatten automatically, 100-widget chains in <10ms
2025-12-15  ComposableMixin pattern: add to existing widget class to gain >> and // without modifying base
2025-12-15  Type narrowing in tests: use `result: ComposableWidget` annotation when chaining >> to avoid mypy errors
2025-12-15  LogosCell pattern: AGENTESE paths → marimo cells via LogosCellResult(_repr_html_ for mo.Html)
2025-12-15  to_marimo() universal: check HStack/VStack first (use_anywidget param), then KgentsWidget (no param)
2025-12-15  INHABIT consent debt: continuous [0,1] variable beats binary accept/reject—enables nuanced relationships
2025-12-15  Alignment thresholds: >0.5 enact, 0.3-0.5 negotiate, <0.3 resist—negotiation band prevents frustration
2025-12-15  Heuristic alignment fallback: keyword→eigenvector mapping enables graceful LLM degradation
2025-12-15  Force mechanic ethics: expensive (3x tokens) + limited (3/session) + logged = agency by design
2025-12-15  Counter-metrics for UX: force-to-suggest ratio > 0.3 reveals alignment threshold too strict
2025-12-15  Punchdrunk principle: collaboration > control; citizen refusal is core feature, not bug
2025-12-15  16 production systems built: AGENTESE/PolyAgent/Operad/Sheaf/Flux/Town/K-gent/M-gent/Reactive/N-Phase/Terrarium/API/Billing/Licensing/Tenancy
2025-12-15  Unified categorical stack: PolyAgent (state machines) + Operad (grammar) + Sheaf (emergence) → any domain
2025-12-15  Projection Protocol: widget.to_cli()/to_marimo()/to_json()—same state, multiple targets, zero rewrites
2025-12-15  SaaS infrastructure complete: Stripe billing, OpenMeter usage, multi-tenant RLS, feature gating decorators
2025-12-15  AGENTESE 8-phase impl: parser→affordances→JIT→laws→integration→wiring→adapter—all phases shipped
2025-12-15  Memory substrate shipped: crystals, cartography, stigmergy, semantic routing, ghost sync—8 phases complete
2025-12-15  BUILDER_POLYNOMIAL: archetype→phase mapping (Scout→EXPLORING, Sage→DESIGNING, etc.) enables typed handoffs
2025-12-15  Builder extends Citizen: dual polynomials (life+work) in parallel; extend > wrap for dataclass inheritance
2025-12-15  Immer MapSet: enable at app entry when Zustand stores use Map/Set—silent failures otherwise
2025-12-15  SSE stale closures: event handlers capture callbacks at creation; use refs for fresh handlers
2025-12-15  Silent API failures kill UX: explicit loading/error/success states mandatory, not optional
2025-12-15  Debug backend first: curl endpoint directly before blaming frontend; curl through proxy second
2025-12-15  React navigate() timing: for same-component URL updates, history.replaceState() safer than navigate()
2025-12-15  Effect deps incomplete: callbacks in deps must include their own deps or use refs to avoid stale state
2025-12-15  WorkshopEnvironment is task-centric (not spatial): builders inhabit tasks, not regions
2025-12-15  Workshop phase→archetype mapping: EXPLORING→Scout, DESIGNING→Sage, PROTOTYPING→Spark, REFINING→Steady, INTEGRATING→Sync
2025-12-15  Keyword routing MVP: simple dict lookup before LLM-based semantic routing; extend later
2025-12-15  EventBus reuse: same pattern for TownEvent and WorkshopEvent—generic typing works
2025-12-15  Widget JSON bridge: TS discriminated union mirrors Python _to_json(); exhaustive switch enables type-safe dispatch
2025-12-15  React hooks ref pattern: store callbacks in ref to avoid stale closures in SSE event handlers
2025-12-15  Widget context pattern: useWidgetRenderOptional() enables layout components to work in isolation and with WidgetRenderer
2025-12-15  WorkshopFlux auto_advance: must check TASK_COMPLETED after _advance_phase() to stop running—infinite loop otherwise
```

## Anti-Patterns

```
2025-12-15  Silent catch blocks: swallowing errors shows blank UI; always surface to user or logs
2025-12-15  Missing loading states: "works on my machine" hides race conditions on slow networks
2025-12-13  Terminology sprawl: one metaphor system, not five competing
2025-12-12  Generator Trap: pickle can't serialize stack frames
2025-12-12  Timer-driven loops create zombies
2025-12-12  Bypassing running loops causes state schizophrenia
2025-12-12  Context dumping: large payloads tax every turn
2025-12-12  Keyword intercept dangerous: "delete"→"Minimalism"→auto-approve
2025-12-11  Full ouroboros (feedback=1.0) → solipsism
```

## Unanswered

```
2025-12-12  DensityField animation: 30fps always or only when focused?
2025-12-12  Flux → archetype wiring (Consolidator, Spawner)?
```

---

*Lines: 184/200 | Last pruned: 2025-12-15*
