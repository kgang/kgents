# Micro-Experience Factory: Agent Town × AGENTESE REPL × Reactive UI

> Theme: **Pixelated isometric foundry where agents-as-pipelines self-attach, mutate, and bloom into joyful monstrosities.**

This treatment distills the repo’s crown jewels—Agent Town (polynomial citizens + TownOperad + TownFlux), AGENTESE REPL (verb-first, five-context ontology), and the reactive/generative UI substrate (functor widgets across CLI/TUI/marimo/JSON)—into a coherent offering: a **Micro-Experience Factory**. Each concept below is compositional (category laws), flux-aware (perturbable streams + HITL), memoryful (D-gent witness/replay), and traceable (trace monoid for pipelines + world events).

---

## Grounding (Spec/Principles)
- **Composable**: Agents are morphisms; operads generate grammars (TownOperad, SoulOperad). Reactive widgets are functors (state → projection).
- **Heterarchical / Flux**: Same agent supports autonomous flow + invoked perturbation (`Flux` functor; perturbation principle).
- **Generative**: From small primitives (glyphs, slots, Town ops) to infinite valid compositions; avoid enumeration.
- **Accursed Share**: Leave room for slop/entropy; idle time self-mutates pipelines.
- **Tasteful / Curated**: Each module earns its place; joy-inducing interaction is a design goal.

---

## Core Ingredients (what we can compose)
- **Agent Town**: `CitizenPolynomial` (state cuts), `TownOperad` (greet/gossip/trade/solo + dispute/celebrate/mourn/teach), `TownFlux` (async loop, NATS/SSE), eigenvector scatter + coalition metrics.
- **AGENTESE REPL**: Five contexts (`self/world/concept/void/time`), observer archetypes, pipeline composition syntax, introspection affordances.
- **Reactive / Generative UI**: Glyph→Bar→AgentCard→Scatter widgets; functor projections (`to_cli|tui|marimo|json`); anywidget marimo bridge; SSE-ready; slot/filler operad for UI.
- **Memory / Trace**: D-gent witness/replay + graph memory; trace monoid view for pipelines + events; perturbation hooks.
- **Flux HITL**: Inject high-priority events into running flux (no bypass); DJ-pad style perturbations.

---

## Experience Directions

### 1) Isometric Foundry (Pipeline Sculptor)
- **Premise**: REPL commands (Agentese paths) render as glowing tracks in an isometric lattice. Each track segment is a morphism; nodes are citizens/holons/widgets.
- **Mechanic**: Build mode uses operad slots/fillers to auto-snap compositions; Town operations become rails; trace monoid guarantees confluent merges and replay.
- **Play**: Drop citizens onto rails; TownFlux runs; SSE feeds scatter + glyph overlays. HITL perturbations (cards/pads) inject new ops without breaking flow.
- **Emergence**: Unused slots self-bind to `void.*` entropy nodes, spawning side-loops (“slop blossoms”) that can be harvested or pruned.

### 2) Flux Carnival (Live Drama Mixer)
- **Premise**: Town plaza as voxel/isometric stage; citizens carry eigenvector colors; coalition edges pulse.
- **Mechanic**: DJ pads mapped to Town ops with metabolics (tokens, drama potential). Pads are Flux perturbations, not bypasses.
- **Feedback**: Reactive sparklines show tension/drama; metabolics bars update; gossip introduces rumor decay warnings.
- **Emergence**: “Creolize mode” routes unused outputs to void.functor to spawn shadow citizens with mutated eigenvectors.

### 3) Memory Loom (Witness/Reforge)
- **Premise**: D-gent witness streams as threads; time-scrubber replays Town days; trace monoid braids show commuting operations as glyph knots.
- **Mechanic**: Drag threads together to apply parallel/sequential operad composition; replay segments projected to different targets (CLI vs marimo) to teach functoriality.
- **Emergence**: “Sediment layers” of past pipelines reattach to present flux, enabling counterfactual runs.

### 4) Holon Bazaar (Micro-App Market)
- **Premise**: Stalls are holons from REPL (`self.status`, `world.town.step`, `concept.laws.verify`). Combining stalls generates micro-experiences.
- **Mechanic**: Slot discovery auto-attaches stalls via operad constraints; idle time triggers Accursed Share self-composition.
- **Emergence**: “Persona forge” stalls (entropy + operad + citizen) emit tiny NPCs as reactive cards, ready for Town injection.

---

## Architectural Through-Line
- **Trace Monoid**: Every REPL invocation + Town event is a trace element. Independence relations define commutation classes; braids render as isometric knots; supports replay/merge.
- **Flux Perturbation**: Invocations become prioritized events; no state bypass. HITL cards/pads implement perturbation lawfully.
- **D-gent Memory**: Witness/replay backs the Loom; graph memory feeds coalition edges + gossip accuracy decay; temporal sheaves for multi-resolution.
- **Category Laws Everywhere**: Operads (Town/Soul/UI slots), functors (widgets to targets), profunctors (logos handles), monoids (traces). Identity/associativity are verified (BootstrapWitness).
- **Projection Functor**: Same state → `to_cli|tui|marimo|json`; marimo anywidget shows live scatter; TUI adapter mirrors; CLI shows ASCII knots.

---

## AUP Alignment (AGENTESE Universal Protocol)
- **GardenState match**: Agent Town already aligns with AUP GardenState; no translation layer needed (see `plans/meta.md`, `impl/claude/protocols/api/aup.py`).
- **Envelope once, project everywhere**: Serve the isometric lattice, TownFlux streams, and REPL holon stalls through AUP HTTP/WebSocket. Clients: marimo anywidget, React, Textual TUI, CLI.
- **Channels**: `town:{id}` for flux events; `repl:{session}` for pipeline traces; `trace:{id}` for braids; all serialize via AUP serializers (`protocols/api/serializers.py`).
- **Compose API**: Use AUP `compose()` to execute Town operations and REPL pipelines remotely; mirrors operad slot snapping in the Foundry UI.
- **Observability**: AUP span metadata (span_id, timestamp) rides with SSE/WebSocket chunks; feed reactive TraceWidget overlays.
- **HITL routing**: Perturbation cards post to AUP endpoints; Flux agents consume via subscribe; guarantees no state bypass, consistent with perturbation principle.

---

## Demo Beat (Flagship Flow)
1. REPL boots in corner; user runs `world.town init` → plaza manifests; glyph rain seeds lattice.
2. Build: drag “gossip” rail between two citizens; metabolics bar shows token/drama; slots snap via operad.
3. Perturb: DJ pad injects `gossip(topic="archive")`; tension spikes; coalition edges animate; SSE updates scatter.
4. Time travel: scrub back 30s; replay to marimo pane; show functorial projection fidelity.
5. Accursed blossom: idle → Bazaar self-composes idle holons into a shadow side-show; user can harvest or quarantine.

---

## Refined User Journeys (humans, operators, agents)
- **Human composer**: Starts in REPL (explorer archetype) → builds pipeline tracks in isometric view → taps DJ pads to perturb Town → scrubs memory loom to compare branches → exports a snapshot via AUP for others to join in-browser.
- **Operator/SRE**: Watches metabolics + tension dashboards; can throttle entropy, sandbox slop blossoms, and replay incidents via trace monoid; operates entirely through AUP (headless) while TUI mirrors state.
- **Agent-as-user**: An autonomous agent connects via AUP WebSocket, requests trace braid, and proposes a new slot attachment; perturbation arrives as priority event; human can approve via HITL card—true heterarchy.
- **Educator/demo**: Uses marimo notebook (AUP client) to walk through category laws: same state projected to CLI ASCII knots, TUI lattice, and browser scatter; shows identity/associativity by swapping rail order and watching braids commute.
- **Marketplace patron**: Browses Holon Bazaar (AUP-backed) where stalls advertise slots/caps; buying (attaching) a stall emits a GardenState delta; idle time triggers slop mutations the patron can tame for bonus effects.

---

## Design Cues (internet inspiration)
- **Isometric pixel worlds**: Habbo Hotel, Crossy Road, Townscaper (cozy palettes, chunky voxels), Helltaker-esque contrast for drama spikes.
- **Factory sims**: Factorio/Dyson Sphere Program for belt/rail readability; shape language for operad slots/fillers.
- **Music pads**: Novation Launchpad, Ableton Clip Launcher for DJ-style perturbation UX.
- **Data loom**: Weaving/loom UIs (Pattern/Thread metaphors) + braid visualizations from knot theory diagrams.
- **Playful terminals**: Dwarf Fortress ASCII density, Baduk/Go influence for coalition edges; use glyph gradients, not flat grids.

---

## Next Implementation Steps (suggested)
- Prefer existing stack first: reuse reactive substrate widgets (Glyph/Bar/Sparkline/AgentCard/Scatter), marimo anywidget bridge, Textual adapter, CLI projection. Only add a thin isometric layer (SVG/Canvas) on top of the same widget state.
- Pick isometric render stack (SVG/Canvas/Three) **only** as a skin over existing reactive state; do not fork state management.
- Define trace schema (REPL command + TownEvent) with independence relations; expose to UI.
- Map HITL cards/pads to Flux perturbation API; respect metabolics budget.
- Instrument D-gent witness for replay UI; layer coalition/rumor decay overlays.
- Style: pixel/isometric palette, joyful glitches, operad slot highlights; avoid generic dark/purple defaults.

---

## Handles (for prompts)
- Context: `spec/principles.md`, `spec/town/*`, `docs/skills/agentese-repl.md`, `impl/claude/agents/town/*`, `impl/claude/agents/i/reactive/*`.
- This doc: `docs/micro-experience-factory.md`
