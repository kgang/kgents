---
path: plans/meta
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
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
```

## Anti-Patterns

```
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
2025-12-12  ModalScope: duplicate() → git stash/branch mapping?
```

---

*Lines: 110/200 | Last pruned: 2025-12-14*
