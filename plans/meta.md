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
Optional dep stubs: no-op stubs for type-checking; document intent, not silent failure
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
Global singletons + xdist = race: sequential OK, parallel risky—document or use markers
Contract tests bridge type gaps: Python validators mirror TypeScript interfaces
Stress test phase machines: Hypothesis with action sequences reveals invalid transitions
```

### Punchdrunk & Director Patterns
```
DirectorAgent polynomial: OBSERVING → BUILDING_TENSION → INJECTING → COOLDOWN cycle
Consent debt sensitivity: debt > 0.7 blocks injection; debt multiplies cooldown
Entropy budget: LCG sample() for deterministic testing; void.entropy for production
Injection decision algorithm: tension-based probability + debt reduction + cooldown check
ASCII projection pattern: ┌─┼└ borders + progress bars = rich CLI without deps
Cross-jewel synergies: Atelier rate limiting → injection cooldown; Forge events → injections
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
Wiring > stub: add_X_to_Y() must actually modify class, not be no-op placeholder
Subscription indexing: ** catch-all needs separate bucket from * prefix wildcards
AT_LEAST_ONCE delivery: track pending, redeliver on timeout, cap retry attempts
Pipeline fail_fast semantics: don't pass stale input to later stages after failure
TZ-aware caching: if cached_at has tzinfo, use aware now(); else use naive now()
Core-apps × AGENTESE: each jewel needs path registry + observer views + subscriptions + shortcuts + pipelines
```

### Gestalt Elastic Synthesis (2025-12-16)
```
Density-Content Isomorphism: Screen Density ≅ Observer Umwelt ≅ Content Detail Level
UI building algorithm: name dimension → define values → provide context → parameterize constants → adapt internally
Categorical stack for UI: Functor (layout), Natural Transformation (responsive), Sheaf (component coherence)
```

### UX Patterns (from Core-Apps Research)
```
Dual-currency economy: earned (watching) + purchased (premium)—never 1:1 ratio
Collective momentum: visible meter + unlock thresholds + decay creates urgency
Spectator influence gradations: cheap=plentiful, expensive=impactful
Semantic zoom: zoom level = semantic depth, not just visual scale; C4 model
Consent as continuum [0,1]: nuanced > binary; refusal is feature, not bug
Masks for threshold: anonymity enables transition from observer → participant
Memory persistence: cross-session continuity creates consequence and depth
Gap detection: show what's missing, not just what exists
Natural language → structure: "describe what you want" eliminates blank page
Dry run mode: test without execution enables safe experimentation
Timeline reconstruction: post-action replay enables objective learning
Role-based information asymmetry: different users see different data—realistic constraint
Session persistence: named sessions + `kg /continue` = work spans terminals
Context-aware completion: suggest from history + current phase, not just syntax
Decay visualization: fresh→fading opacity gradient shows temporal relevance
```

### Crown Jewel Strategy (2025-12-16)
```
Ship-ready detection: 95% code + tests > feature completeness; docs complete the last 5%
Two-leader strategy: ship best two first, validate market, fund rest
Web UI is common multiplier: single React pattern unlocks three jewels simultaneously
Gardener = force multiplier: investment in development interface accelerates all jewels
Revenue stacking: $560K = $300K enterprise + $175K SaaS + $85K economy—diverse streams
Spike completion ≠ jewel completion: spikes prove feasibility; integration proves value
Middle tier pattern: 40-60% jewels share common blocker (Web UI + API endpoints)
Enterprise sales distinct: Domain Simulation needs pilot motion, not SaaS landing page
AGENTESE path count: 58 paths = unified interface surface across all seven jewels
Test density indicates readiness: Brain 1104 > Gestalt 146 > others; correlation strong
Moat articulation: "we build substrate that generates apps" > "we build 7 apps"
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

*Lines: ~155/200 | Last pruned: 2025-12-16 | Crown Jewel Strategy added*
