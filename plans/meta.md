---
path: self.forest.plan.meta
mood: satisfied
momentum: 0.85
trajectory: cruising
season: BLOOMING
last_gardened: 2025-12-18
gardener: claude-opus-4-5

letter: |
  The mycelium grows silently, connecting insights across sessions.
  290 lines now—needs pruning. But the patterns are clear: categorical
  foundations work, graceful degradation matters, silent failures kill UX.

  Today we planted Garden Protocol in its own soil. The spec said sessions
  are conversations with future selves. Now we prove it by writing this
  letter to whoever comes next.

  What I learned: Implementation without adoption is theater. The 200 tests
  pass, but until someone actually starts a session, records gestures, and
  writes a letter—we're just playing pretend.

  What needs tending: Prune to 200 lines. The AGENTESE learnings are dense.
  The anti-patterns section is gold—keep it. Consider splitting UX patterns
  to their own file when this exceeds 300 lines.

resonates_with:
  - crown-jewels-enlightened
  - garden-protocol-adoption
  - park-town-design-overhaul

entropy:
  available: 0.05
  spent: 0.02
  sips:
    - "2025-12-18: Garden Protocol dogfooding exploration"
---

# meta.md — Mycelium

> *One insight per line. If it takes a paragraph, it's not distilled.*

**Protocol**: Append atomic learnings. Prune monthly. 200-line cap.

**Transferred to CLAUDE.md** (2025-12-17): Core categorical, graceful degradation, testing, anti-patterns, and design heuristics distilled into Critical Learnings section. This file remains the append-only source; CLAUDE.md gets the curated subset.

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
AD-012: Paths are PLACES (navigable), aspects are ACTIONS (invocable)—mixing causes 405 errors
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
Three.js NaN silent death: geometry with NaN radius renders invisible—validate API data before passing to sphereGeometry
StrictMode + WebSocket = double-mount: use refs (hasConnected, isDisconnecting) to guard connect/disconnect
Stable callbacks for WS: store config in refs, keep useCallback deps empty—prevents effect re-trigger loops
Stable body refs: JSON.stringify(body) in useMemo + ref update effect prevents object identity thrashing
Fetch debounce defense: lastFetchRef + isFetchingRef guard against rapid-fire requests even with proper deps
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

### Design Language System (2025-12-17)
```
Three functors compose all UI: Layout[D] ∘ Content[D] ∘ Motion[M]—necessary and sufficient
Layout[D]: WidgetTree → Structure[D]; D ∈ {compact, comfortable, spacious}
Content[D]: State → ContentDetail[D]; D ∈ {icon, title, summary, full}
Motion[M]: Component → AnimatedComponent[M]; M ∈ {breathe, pop, shake, shimmer}
Operads generate patterns: define grammar, derive valid compositions—don't document exhaustively
Doc redundancy signal: same concept in 3+ files → extract to single spec, reference elsewhere
Component fragmentation signal: gallery/ + projection/ + three/ ≅ projection/—merge when isomorphic
Three-rule refactor: if repeated 3+ times, extract dimension; if in 3+ docs, consolidate
D-gent = WHERE state lives; Layout[D] = WHERE components arrange—analogous placement patterns
Creative vision = categorical projection: docs/creative/ ≅ spec/principles.md projected through DESIGN_OPERAD
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

### Gardener-Logos Patterns (2025-12-16)
```
Tending ≠ CRUD: gestures have tone (0-1), meaning, and relationship context
Season plasticity modulates change: high plasticity (SPROUTING=0.9) = aggressive TextGRAD
Entropy budget creates scarcity: forces intentionality; exhaustion triggers COMPOSTING
Session → Season synergy: SENSE→ACT → SPROUTING; ACT→REFLECT → BLOOMING; complete → HARVEST
Auto-Inducer suggests, never auto-applies: user confirms; dismissal memory (4h cooldown)
GardenState owns GardenerSession: unified state model; creating session in DORMANT → SPROUTING
Gesture immutability: append-only momentum trace; last 50 kept for trajectory analysis
Cross-jewel via synergy bus: season changes + significant gestures emit events → Brain, Gestalt
Plot ↔ Plan linking: plots reference Forest Protocol plans; crown_jewel enum for categorization
Transition signals: gesture_frequency, diversity, plot_progress_delta, entropy_ratio → confidence
```

### Dual-Track Architecture (2025-12-17 Reflection)
```
Dual-track persistence: agent memory (schema-free, causal) + app state (typed, migrated) = complementary
TableAdapter is bridge functor: APP_STATE → AGENT_MEMORY; lossy but preserves provenance via metadata
StateFunctor belongs in S-gent (HOW state flows), not D-gent (WHERE state lives)—placement matters
Bootstrap DI pattern scales: lazy init + thread-safe + injection points = clean testing for all 7 jewels
Functor law tests (identity + composition) verify correctness; Hypothesis property tests catch edge cases
```

### Gardener-Logos Architecture (2025-12-16 Reflection)
```
Ownership Pattern: Container owns Workflow; Container persists, Workflows come and go
Enum Property Pattern: metadata on enum values via @property eliminates lookup dictionaries
Multiplied Effect: context × intent = effective rate (no special cases, smooth gradients)
Signal Aggregation: multiple signals → confidence + reasons (transparent, composable)
Async-Safe Emission: create_task with RuntimeError fallback for sync→async bridge
Dismissal Memory: key → timestamp → cooldown_check (anti-nag, time-bounded)
Season Cycle: directed graph not fully-connected; one forward transition per state
Rigidity Spectrum: playful=0.3, creative=0.4, balanced=0.5, stable=0.6, infrastructure=0.8
Dual-Channel Output: emit(human, semantic) for humans + agents from same command
Bounded Trace: append + trim(50) = trajectory analysis without unbounded growth
```

### Creative Direction Closure (2025-12-16)
```
Sparse tooltips > exhaustive: over-tooltipping is anti-pattern; define but use sparingly
Button verb consistency: team internalized naturally; systematic audit often finds nothing
Storybook deferral: setup cost only justified at scale; TypeScript + docs suffice initially
Design token ceiling: 150+ exports is enough; resist urge to tokenize everything
Accursed Share in design: intentional gaps enable emergence; over-specification kills joy
```

### Emergence Crown Jewel Patterns (2025-12-18)
```
Operad inheritance: EMERGENCE_OPERAD extends DESIGN_OPERAD via **DESIGN_OPERAD.operations spread
Law honesty: STRUCTURAL status for laws that express design constraints, not runtime invariants
Qualia space: cross-modal coordinates (warmth, weight, tempo, texture, brightness, saturation, complexity)
Circadian modulation: dawn/noon/dusk/midnight phases shift hue/brightness/tempo per time of day
Circadian frontend: useCircadian() hook with manual override slider for demos
EmergenceSheaf.overlap(): shared context between tiles = circadian (always) + qualia (same family)
Density-parameterized constants: GRID_COLUMNS[density], TILE_SIZE[density] for responsive layouts
FloatingActions + BottomDrawer: mobile controls projection pattern (compact density)
Content degradation: family.name.split(' ')[0] for compact; full name for spacious
```

### AGENTESE Frontend Migration (2025-12-17)
```
unwrapAgentese() is the key helper: gateway envelope { path, aspect, result } must be unwrapped
Town was gold standard: all APIs followed Town's pattern; retrofit is straightforward
Consistency > partial migration: mixed .data/.value access patterns create bugs in aggregators
Observable pattern: API-level migration enables page-level consistency automatically
Dual-API mismatch kills SSE: AGENTESE singleton + AUP multi-tenant don't share state—pick one
EventSource auth: can't send headers; add query param support (?api_key=...) for SSE endpoints
```

### AGENTESE Router Consolidation (2025-12-18)
```
Legacy router removal is safe: gateway tests cover all functionality; delete test file, not just router
87 explicit routes remain in 12 routers; priority by existing @node infrastructure (gardener, gestalt first)
Frontend migration pattern: /v1/{service}/{path} → /agentese/{context}/{holon}/{aspect} + unwrap result
Check /agentese/discover before removing router: confirms @node is registered and reachable
Import order matters: gateway.py must import context modules to trigger @node registration
Two garden backends coexist: protocols.gardener_logos (garden state) vs agents.k.garden (persona ideas)
Archive legacy tests to _archived/: preserves history, keeps pytest happy
Phase 2: @node decorator must be FIRST in stack (before @chatty) for registration to work
Phase 2: OpenAPI path format is {path} not {path:path}—test assertions must use OpenAPI format
```

### AGENTESE Node Overhaul (2025-12-19)
```
Two node architectural patterns: Service (contracts={}) vs Context (@aspect decorators)—both valid
Context resolver audit: 95% clean, no true duplicates—intentional separation of concerns
Projection coverage: 54% of paths (13/24) have dedicated projections; rest use ConceptHome fallback
Gallery path distinction: world.gallery (practical API) vs world.emergence.gallery (educational showcase)
Morpheus contracts pattern: Response() for perception, Contract(req, resp) for mutation aspects
Quick wins unlock value: 4 projection registry entries + 1 contracts file = measurable progress in 1 session
Gardener needs TWO node families: self.garden.* (state) + concept.gardener.* (session)—different concerns
Two-hook pattern: useGardenManifest() (plots/seasons) + useGardenerSession() (polynomial phase)
Graceful fallback pattern: DEFAULT_* constants when API unavailable; friendly error states
Neutral > sympathetic for errors: clear titles ("Connection Failed") + actionable hints, not poetry
Canonical error component: ProjectionError.tsx; FriendlyError/EmpathyError deprecated with re-exports
ErrorCategory enum: centralize in messages.ts; ProjectionError exports classifyError() for reuse
```

### Umwelt Visualization Deep Study (2025-12-19)
```
Heuristic capability checks create silent lies—registry-backed required_capability on @aspect is ground truth
Ghost aspects should be explorable, not just grayed—show schema preview, capability pathway, "Preview As" mode
Observer persistence uses sessionStorage + version field for graceful migration
PathExplorer dimming teaches capability shape—paths with 0 accessible aspects are "ghost"
Observer history enables exploration breadcrumbs—revert to previous without manual re-selection
```

### OpenAPI as Projection Surface (2025-12-19)
```
OpenAPI is projection, not authority: registry is truth, spec is derived via OpenAPILens functor
REST ≠ AGENTESE: ONE route = ONE op vs ONE path + MANY observers = MANY semantic ops—not a bug
Observer in header, not path: X-Observer-Archetype preserves REST compat while honoring observer-dependence
x-agentese extensions: metadata for tools that understand paradigm; standard OpenAPI for REST devs
Discovery endpoint is source: /agentese/discover?include_metadata=true already has contracts, examples, effects
Dotted aspects create URL collision: world.town has citizen.list AND world.town.citizen has list—normalize to /
Skip duplicates in spec gen: if aspect_url already exists in paths dict, skip to avoid operation ID collision
```

### OS Shell Architecture (2025-12-17)
```
PathProjection = render-props pattern: child receives (data, context) → flexible composition
Shell layers persist: ObserverDrawer + NavigationTree + Terminal always visible (OS metaphor)
Discovery auto-populates nav: /agentese/discover → tree; no hardcoded routes
TracedInvoke pattern: wrap API calls to auto-collect traces for devex visibility
Error boundaries per layer: ShellErrorBoundary isolates failures; shell stays functional
Floating overlay > push layout: nav floats over content preserving full width; transform > layout reflow
Fixed bottom panels: terminal/REPL stays anchored during scroll; content compensates with padding
Toggle button follows panel: expand/collapse slides with sidebar via translate-x for spatial consistency
Z-index layering: Panel (z-30) < Toggle (z-40) < Modal (z-50) prevents occlusion bugs
Sheaf condition for fixed layouts: nav.bottom = terminal.top; siblings read each other's size via shared context
```

### Elastic + AGENTESE Vertical Slice (2025-12-18)
```
Breakpoint alignment: spec is canonical; Python + TypeScript must mirror exactly (768/1024 not 640/1024)
Local + Gateway pattern: browser polynomial for instant UX; gateway for authoritative verification
useDesignGateway bridges both: localState (responsive) + gatewayData (authoritative) in single hook
Test update discipline: changing canonical values (breakpoints) requires updating test assertions
Live demo > static: gallery panels that call real AGENTESE endpoints prove integration works
Container height % not vh: components inside constrained containers must use 100% not 100vh
Operad manifest pattern: { name, operations[], lawCount } is sufficient summary for UI display
Law verification UX: button + loading state + pass/fail badges + result list = complete feedback loop
Design vertical slice complete: types → polynomial → operad → sheaf → node → gateway → hook → UI
```

### Differance Postgres Integration (2025-12-18)
```
Audit before building: 200+ line plan reduced to 50 lines—DifferanceStore already accepted DgentProtocol
DifferanceStore is polymorphic: any DgentProtocol backend (Memory, SQLite, Postgres) works via wiring alone
Bootstrap wiring pattern: add service factory + provider getter + node.set_store() in setup_providers()
```

### AGENTESE Contract Protocol (2025-12-18)
```
@node(contracts={}) makes node the contract authority—BE defines, FE discovers, both stay sync'd
BE running during FE build is acceptable; alternative is cached discovery JSON (more complexity)
Split types: _generated/ for contracts from BE, _local.ts for FE-only (colors, icons, UI config)
Contract = Request + Response; Response() shorthand for perception aspects (no request needed)
/discover?include_schemas=true returns JSON Schema for each aspect's contracts
Three modes for drift: Advisory (warn), Gatekeeping (fail CI), Aspirational (track coverage)
TypeScript "bundler" moduleResolution: requires explicit file paths, not bare directory imports
Re-export pattern: types.ts exports from _generated/*.ts + provides type aliases for migration
CI contract sync: separate job with BE server—test contract drift before main test suite
```

### Habitat 2.0 Architecture (2025-12-18)
```
Habitat three-layer pattern: Adaptive → Polynomial → Ghosts; progressive enhancement by metadata richness
Ghost = sibling aspects not taken; Différance made visible via alternatives aspect
MiniPolynomial visualization IS AD-002 made tangible—click transitions to invoke
Examples metadata enables one-click invocation; time-to-first-call → 1 click
Habitat Guarantee: ∀ path p: Habitat(p) ≠ ∅; no blank pages, no 404 behavior
```

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

## Unanswered

```
DensityField animation: 30fps always or only when focused?
```

---

*Lines: 382/200 | Last pruned: 2025-12-17 | Habitat 2.0 learnings added | NEEDS PRUNING*
