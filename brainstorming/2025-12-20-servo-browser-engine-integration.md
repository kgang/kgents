# Servo + Rust for kgents: Transformative Integration v2 (WARP-Synergy)

> *"The noun is a lie. There is only the rate of change."*
> *"The persona is a garden, not a museum."* — Kent's standing intent

**Date**: 2025-12-20
**Context**: Brainstorming integration opportunities with Mozilla's Servo browser engine
**Goal**: Make Servo + Rust foundational across ALL of kgents, not just UI, and cross-synergize with WARP primitives and category-theory architecture

---

## 0. Constitutional Alignment (Immutable)

All proposed integrations must satisfy `spec/principles/CONSTITUTION.md`:

- Tasteful: every Rust or Servo component must earn existence
- Curated: choose a few high-leverage primitives, not a sprawl of bindings
- Ethical: privacy-first, explicit gates, visible provenance
- Joy-Inducing: tools feel alive and opinionated, not corporate chrome
- Composable: Rust components must preserve categorical laws
- Heterarchical: no hard-coded master; orchestration is contextual
- Generative: SpecGraph + N-Phase compiler remain authoritative

---

## 1. WARP -> kgents -> Servo Cross-Synergy (Core Mapping)

Servo and Rust should *instantiate* WARP-inspired kgents primitives, not merely host a UI.

| WARP-inspired kgents primitive | Servo/Rust leverage | Transformative impact |
| --- | --- | --- |
| TraceNode (`time.trace.node.*`) | Rust log + zero-copy event buffers | Trace-first history becomes real-time, replayable, auditable |
| Walk (`time.walk.*`) | Servo session surface + playback UI | Conversations become cinematic, not scrollback |
| Ritual (`self.ritual.*`) | Rust workflow kernel + Sentinel gates | Agent Mode with lawful composition + covenant negotiation |
| Offering (`concept.offering.*`) | Rust capability enforcement + budget caps | Context becomes priced and contract-bound |
| IntentTree (`concept.intent.*`) | Rust graph engine + Servo visualization | Task graphs are typed and explorable |
| Covenant (`self.covenant.*`) | Rust permission engine + UI overlays | Human approvals become explicit, visible, explainable |
| Terrace (`brain.terrace.*`) | Rust-indexed knowledge layers + Servo UI | Drive becomes curated, versioned, local-first |
| VoiceGate (`self.voice.gate.*`) | Rust classifier + Anti-Sausage rules | Voice preserved at every entrypoint |
| TerrariumView (`world.terrarium.view.*`) | Servo multi-webview + compositional lenses | Multi-pane heterarchy becomes first-class |

Servo supplies the surface; Rust supplies the laws.

---

## 2. Servo as the Projection Substrate (Not a WebView)

Servo is not "a browser" inside kgents. It is the **projection substrate** that renders the ontology.

### 2.1 Servo Projection Target (Spec-First)

- Register a `servo` target in the Projection Protocol
- Projectors emit a ServoScene graph, not raw HTML
- WebGPU is used where it adds semantic clarity (Town, Sheaf, Memory)

### 2.2 TerrariumView = Multi-Webview Heterarchy

Servo's multi-webview becomes `world.terrarium.view.*`:

- Each jewel can render independently
- Views are compositional lenses over the same TraceNode stream
- Fault isolation: a crashed view doesn't collapse the system

### 2.3 Servo as the Native Host for CLI v7 Canvas

- CLI v7 Collaborative Canvas runs in Servo
- Cursor presence is a projection of IntentTree + TraceNode focus
- Walk playback becomes a first-class cinematic UI

---

## 3. Webapp Strategy Re-Write (Servo Primitives Replace the Webapp)

We can kill the current webapp as a primary surface. The "main website" becomes a **Servo host** that only composes projection outputs.

### 3.1 Replace the Container Functor with a Servo Shell

From `docs/skills/metaphysical-fullstack.md`, the main website is a shallow container functor. Re-interpret it as:

- **ServoShell** = minimal host process (windowing + projection registry + routing)
- **Projection outputs** = first-class surfaces (ServoScene, TraceNode playback, Terrace views)
- **No bespoke webapp logic** beyond composition, navigation, and covenant-gated entry

The webapp is not the UI. The webapp is the **composition boundary**.

### 3.2 Servo Target = Primary Projection Target

Per `docs/skills/projection-target.md`, register a `servo` projection target:

- Projectors emit `ServoScene` graphs, not HTML/React
- Fidelity should be **MAXIMUM (0.9-1.0)** by default
- Fallbacks: CLI → TUI → JSON remain intact, but Servo is default

This keeps the metaphysical fullstack promise: completeness of definition gives completeness of projection, and Servo is the top projection.

### 3.3 Servo Primitives Superset the "Webapp"

Replace webapp primitives with Servo-native primitives:

| Old Webapp Layer | Servo Primitive Replacement | Notes |
| --- | --- | --- |
| Router + SPA pages | IntentTree navigation | Navigation is a projection of intent, not a URL |
| React components | ServoScene nodes | UI is a graph, not a DOM |
| CSS layouts | Servo layout primitives | Density-aware layouts live in Rust |
| Frontend state | TraceNode / Walk streams | State is in the ledger, not the component |

### 3.4 Elastic UI Patterns Move to Servo

`docs/skills/elastic-ui-patterns.md` still applies; implement it in Servo primitives:

- Compact/Comfortable/Spacious as **Servo layout modes**
- ElasticSplit, FloatingSidebar, BottomDrawer become **Servo widgets**
- Density constants live in the Rust layer to enforce consistency

Servo primitives are now the **single source of layout truth**.

### 3.5 Webapp Residuals (Allowed, but Non-Primary)

Keep a minimal web presence only for:

- Docs, specs, and onboarding
- Static marketing or read-only dashboards
- Deep-linking into Servo sessions (covenant-gated)

All operational UI is Servo-first, or it does not exist.

---

## 4. Crown Jewel UX Refinement (B → A-Grade)

Current Crown Jewels feel like a **3.75/5 (B)**: solid foundations, but not yet inevitable, alive, or teaching-dense. The Servo rewrite is the moment to push them into **A-grade** presence by aligning with the mood board and design references in `creative/crown-jewels-genesis-moodboard.md`.

### 4.1 Design References to Inherit (Explicit)

Use the references already curated in the mood board (online, but canonized in kgents):

- Studio Ghibli UI principles (warm, breathing machinery)
- Matsu theme (watercolor textures, hand-made softness)
- Organic Matter trend (fluid shapes, living materials)
- Sleep No More / Punchdrunk (participant-as-actor immersion)
- Ethical AI patterns (visible consent, human override)

These are not optional aesthetics; they are **structural cues** for Servo primitives.

### 4.2 Servo Primitive Requirements (Mood Board Translated)

Make the following Servo-level primitives non-negotiable:

- **Breathing Surface**: idle pulse on living panels (3–4s, 2–3% amplitude)
- **Unfurling Panels**: drawers open like leaves, not mechanical slides
- **Flow Traces**: data moves like water through vine paths
- **Texture Layer**: subtle paper or grain (not flat glass)
- **Teaching Overlay**: dense teacher callouts with opt-in visibility

Servo is the material; these are the motions that make it feel alive.

### 4.3 Crown Jewel Visual Contracts (Per Jewel)

Each jewel needs a servo-scene contract that preserves identity:

- **Atelier (Copper / Creative Forge)**: workshop glow, spectator bids as living tokens, creation canvas with breathing frame
- **Park (Sage / Immersive Inhabit)**: first-person theater, consent balance as a living gauge, character nodes as orbiting masks
- **Domain (Wood / Integration Hub)**: garden of connectors, flow lines as living vines, sync health as pulse not bar
- **Coalition (Amber / Collaboration)**: warm, communal glow; turn-taking visible; contracts appear as ritual tablets

### 4.4 Typography + Palette Lock-In (Servo Style Sheet)

From the mood board:

- **Headings**: Nunito (friendly, hand-made feel)
- **Body**: Inter (clean, readable)
- **Code**: JetBrains Mono (technical clarity)
- **Palette**: Living Earth (warm soil, living greens, amber glow)

Servo should render with the same typographic and color intent across all projections. This is how we prevent drift.

### 4.5 Crown Jewel Outcome Target

By making Servo the substrate, the Crown Jewels should feel:

- **Alive** (breathing surfaces, organic motion)
- **Teaching-dense** (dense teacher overlays, explicit laws visible)
- **Immersive** (participant-as-actor, ritual theater)
- **Grounded** (warm earth palette, tangible textures)

This is what takes the jewels from B to A.

---

## 5. Rust as the Categorical Kernel (Not a Sidecar)

Rust should underpin kgents' law-critical paths, not just performance hot spots.

### 5.1 The Categorical Core (PolyAgent + Operad + Sheaf)

Make the categorical foundation a Rust crate (`kgents-core`) with PyO3 bindings:

- PolyAgent transition engine
- Operad composition + law checking
- Sheaf gluing and compatibility

### 5.2 SpecGraph + N-Phase Compiler as Rust-Accelerated

SpecGraph, N-Phase compiler, and drift detection should get Rust support for reliability and speed:

- YAML parse + frontmatter validation
- Graph diff and drift detection
- Spec -> Impl scaffolding

This keeps the **Generative** principle enforced at scale.

### 5.3 Event Bus + TraceNode Capture

Rust event bus + trace buffer unlocks WARP-style blocks:

- Every AGENTESE invocation emits a TraceNode
- TraceNodes are time-indexed, replayable, and queryable
- Witness becomes a real-time historian, not a log sink

---

## 6. Servo + Rust Across ALL of kgents (Transformative Iterations)

Below are system-wide, not just UI-level, applications.

### 6.1 AGENTESE Runtime and Gateway

- Rust router for AGENTESE path dispatch
- Typed envelopes with strict validation
- Covenant and Offering enforcement in Rust

**Effect**: AGENTESE becomes a lawful runtime, not just a routing layer.

### 6.2 Brain + Terrace Indexing

- Rust memory indexing for Brain terraces
- Fast embedding search, curated memory views
- Servo surfaces: memory lattices + trace heatmaps

**Effect**: Brain becomes a Drive-like knowledge system with real time coherence.

### 6.3 Witness + TraceNode Ledger

- Rust trace buffer + append-only ledger
- Servo playback of Walks, ritual state, intent resolution
- Provenance becomes visual and inspectable

**Effect**: Trace-first history becomes the default user experience.

### 6.4 Gardener + Forest Protocol Integration

- Rust plan parser for Forest files
- Servo visuals for plan trees, phase maps, and N-Phase status
- Walks anchored directly to plan leaves

**Effect**: The Forest becomes navigable and alive, not just markdown.

### 6.5 Town + Park: WebGPU as Ontological Space

- Town simulations in WebGPU
- Park consent flows rendered as spatial theaters
- K-gent persona sliders become actual state spaces

**Effect**: Category theory becomes visible, not just textual.

### 6.6 CLI v7 Conductor as Ritual Engine

- Rust Conductor for ritual orchestration
- Covenant gates visible in Servo UI
- Conversation Window becomes TraceNode + Walk view

**Effect**: CLI v7 becomes WARP-grade while preserving kgents laws.

---

## 7. Category Theory Architecture: Servo + Rust as Functors

Servo and Rust should align with the categorical stack:

- **Polynomial**: Rust state machines for agents
- **Operad**: Rust law-checked composition
- **Sheaf**: Rust coherence validation
- **SpecGraph**: Rust spec graph transformations

This makes Servo and Rust into functorial implementations, not ad-hoc integrations.

---

## 8. WARP-Style Workflow: How It Feels

WARP's brilliance is not just features; it is the **feeling of flow**. Servo + Rust should deliver that across kgents:

- Every action is a TraceNode
- Every session is a Walk
- Every workflow is a Ritual
- Every context is an Offering
- Every permission is a Covenant
- Every memory set is a Terrace

Servo makes it visible. Rust makes it safe.

---

## 9. Implementation Arc (N-Phase Skeleton)

- PLAN: Forest plans for Servo projection target + Rust core
- RESEARCH: Servo embedding API maturity, Rust binding strategy
- DEVELOP: SpecGraph nodes for TraceNode, Walk, Ritual, Offering
- STRATEGIZE: Map Rust kernel integration into services + AGENTESE
- CROSS-SYNERGIZE: Wire to CLI v7, Witness, Brain, Gardener
- IMPLEMENT: Servo target + Rust core crates
- QA: Covenant/Offering enforcement audits
- TEST: SpecGraph drift checks + operad law tests
- EDUCATE: Skills for Servo projection + Rust core usage
- MEASURE: Trace coverage, ritual completion, voice gate hits
- REFLECT: Anti-Sausage check + Constitution review

---

## 10. Anti-Sausage Check (Servo Edition)

- Did I smooth anything that should remain sharp? No. This is trace-first, spec-first, law-first.
- Did I add safe corporate tone? No. It stays opinionated and categorical.
- Did I downgrade heterarchy? No. Multi-webview + compositional orchestration is heterarchical.
- Is this still daring? Yes. It commits to Servo as substrate and Rust as law engine.

---

## 11. Transformative Iterations (Priority Set)

| Priority | Iteration | Transformative Claim |
| --- | --- | --- |
| P0 | Servo shell + webapp deprecation | The "webapp" becomes a projection compositor |
| P1 | Servo primitives mapped to Crown Jewel contracts | The jewels move from B to A-grade presence |
| P2 | Servo projection target + TraceNode playback | Trace-first UI replaces scrollback |
| P3 | Rust TraceNode ledger + Witness integration | Auditability becomes default |
| P4 | Rust Covenant/Offering enforcement | Permissions become explicit, not implied |
| P5 | Rust PolyAgent + Operad kernel | Category laws become enforced in core |
| P6 | TerrariumView multi-webview | Heterarchical UI becomes real |
| P7 | Town/Sheaf WebGPU | Category theory becomes visible |

---

## 10. Sources

- [Servo GitHub Repository](https://github.com/servo/servo)
- [Servo Official Website](https://servo.org/)
- [Servo 2025 Roadmap](https://www.phoronix.com/news/Servo-Roadmap-2025)
- [Tauri Embedding Prototype Update](https://servo.org/blog/2024/01/19/embedding-update/)
- [Servo in 2024 Review](https://servo.org/blog/2025/01/31/servo-in-2024/)
- [This Month in Servo (March 2025)](https://servo.org/blog/2025/03/10/this-month-in-servo/)
- [Building a Browser Using Servo](https://servo.org/blog/2024/09/11/building-browser/)

---

*"The persona is a garden, not a museum."*
*A Servo + Rust kgents would let that garden grow as a living, law-abiding substrate.*
