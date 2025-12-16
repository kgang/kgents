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

### Categorical Foundations
```
Operads define grammar; algebras apply grammar to systems
Sheaf gluing = emergence: compatible locals → global
PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior
Unified stack: PolyAgent (state) + Operad (grammar) + Sheaf (emergence) → any domain
Turn projectors are natural transformations: Turn → CLI/TUI/JSON/marimo/SSE preserve structure
Functor law verification proves composition: if laws pass, arbitrary nesting is safe
```

### AGENTESE & Protocols
```
Three Phases (SENSE→ACT→REFLECT) compress 11 without loss
Turn is fundamental: single trace derives all panels (holographic)
K-gent = Governance Functor, not chatbot
Symmetric lifting: every functor needs lift() AND unlift()
Protocol > ABC: typing.Protocol enables duck typing without inheritance coupling
Slash shortcuts (/cmd) map to AGENTESE paths—preserves semantics, adds ergonomics
INHABIT consent debt: continuous [0,1] beats binary—enables nuanced relationships
Punchdrunk principle: collaboration > control; citizen refusal is core feature, not bug
```

### Reactive & Streaming
```
Flux > Loop: streams are event-driven, not timer-driven
Perturbation principle: invoke() on running flux injects, never bypasses
Store Comonad > State Monad for context
Streaming ≠ mutability: ephemeral chunks project immutable Turns
Signal generation monotonic: only increments on distinct value changes
Computed lazy: only recomputes on access after invalidation
>> and // operators: associative, flatten automatically, 100-widget chains in <10ms
```

### Graceful Degradation
```
Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback
Two-tier collection: try context, fallback direct
SSE over NATS: circuit breaker + fallback queue ensures degradation when NATS unavailable
Template fallbacks make CLI commands work without LLM
Heuristic alignment fallback: keyword→eigenvector mapping enables graceful LLM degradation
```

### Frontend Patterns
```
SSE stale closures: event handlers capture callbacks at creation; use refs for fresh handlers
Silent API failures kill UX: explicit loading/error/success states mandatory
Debug backend first: curl endpoint directly before blaming frontend
Effect deps incomplete: callbacks in deps must include their own deps or use refs
Immer MapSet: enable at app entry when Zustand stores use Map/Set—silent failures otherwise
Contextual loading > spinner: rotating messages create perceived performance
Error empathy: "Lost in the Ether" > "Network Error"—friendly titles reduce frustration
```

### Testing & DevEx
```
DI > mocking: set_soul() injection pattern beats patch() for testability
Property-based tests catch edge cases: Hypothesis found boundary issues humans missed
Performance baselines as assertions: `assert elapsed < 1.0` catches regressions
Registry singleton + reset(): class-level state works with pytest fixtures via reset()
Contract tests bridge type gaps: Python validators mirror TypeScript interfaces
```

### Infrastructure
```
HTTP validation order: 400 before 403; record before check for rate limits
404 (not 403) for cross-tenant access: prevents tenant enumeration attack
FastAPI route order matters: specific routes must come before generic patterns
PDB essential: prevents all-pod eviction during node drains
Runbook URLs in alerts reduce MTTR: operator jumps directly to procedure
```

### Design Principles
```
Skills pull before doing, push after learning
Purgatory > Generator: eject state as data, not pause frames
Stigmergic surface: agents append, humans curate
Wiring > Creation: check if infrastructure exists before building new
Easter eggs hidden > announced: discovery is the delight
Teaching examples > reference docs: show the pattern in action
Counter-metrics force harm-thinking: "what makes this feature bad?" reveals blind spots
Force mechanic ethics: expensive (3x) + limited (3/session) + logged = agency by design
Six→Seven Jewel Crown: each jewel stresses one meta-framework; The Gardener stresses N-Phase (autopoiesis)
Autopoiesis = self-production; sympoiesis = making-with; Gardener enables both via N-Phase sessions
AGENTESE-first: all CLI commands route through Logos; imperative → verb-first ontology
AGENTESE v3 synthesizes: v1 learnings + v2 draft + critiques + philosophy
v3 goal: 150+ exports → <50; single Logos class; categories enforced at runtime
Context.holon.aspect > flat verbs: ontological structure matters
Observer gradations: Observer (minimal) → Umwelt (full); guest is valid observer
Bounded queries: ?pattern with limit/offset prevents footguns
Subscriptions: at-most-once default; fully specified semantics
Pre-charge economics with refund on failure: safer than post-charge
String-based >> composition: "path.a" >> "path.b" natural idiom
```

## Anti-Patterns

```
Silent catch blocks: swallowing errors shows blank UI; always surface
Generator Trap: pickle can't serialize stack frames
Timer-driven loops create zombies
Bypassing running loops causes state schizophrenia
Context dumping: large payloads tax every turn
Full ouroboros (feedback=1.0) → solipsism
```

## Unanswered

```
DensityField animation: 30fps always or only when focused?
```

---

*Lines: ~108/200 | Last pruned: 2025-12-15 | AGENTESE v3 insights added*
