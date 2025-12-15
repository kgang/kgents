---
path: plans/visionary-ux-flows
status: active
progress: 0
last_touched: 2025-12-14
touched_by: opus-4.5
blocking: []
enables: [agent-town-phase7, reactive-substrate-unification, k-gent-ambient]
session_notes: |
  VISIONARY UX BRAINSTORM: Kent's 4 dream interfaces
  Method: Full N-Phase Cycle with external research
  Grounding: spec/principles.md + reference papers (SIMULACRA, VOYAGER, CHATDEV, ALTERA, AGENT HOSPITAL)
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.12
  returned: 0.03
---

# Visionary UX Flows: The Four Gardens

> *"The interface is not a window to the system. The interface IS the system, made visible."*

## Executive Summary

This document synthesizes Kent's visionary UX requirements with external research, academic heritage (SIMULACRA, VOYAGER, CHATDEV, ALTERA), and deep grounding in kgents principles to produce four interconnected interface designs.

**The Four Gardens**:

| Garden | Vision | Core Metaphor |
|--------|--------|---------------|
| **I. The Messenger** | K-gent conversation interface | Conversation IS computation |
| **II. The Town** | Agent Town ASCII sandbox | Citizens on a playing field |
| **III. The Forge** | DAW/Fruity Loops workbench | Agents as instruments |
| **IV. The Traces** | Fractal decision archaeology | Dreams undreamt made visible |

Each garden is a **projection** of the same underlying AGENTESE substrate—different views into the same category-theoretic foundation.

### Critical Gaps & Risks (to address in IMPLEMENT)
- AUP alignment is implied but not explicit per garden; need channel/serializer mapping and client patterns.
- UI stack divergence risk: commit to existing reactive substrate (Glyph/Bar/Sparkline/AgentCard/Scatter) + marimo anywidget + Textual adapters; any isometric/DAW skin must be a projection, not a new state system.
- Law verification UI: none of the mockups show identity/associativity checks; add visible law badges tied to BootstrapWitness.
- Time-travel/branching: Redux-like patterns listed, but storage/backpressure and D-gent witness integration are unspecified.
- HITL/perturbation: Not yet wired to Flux perturbation principle; define card/pad pathways per garden.
- Metrics/SLOs: No operator-facing SLOs (latency, FPS, AUP error budget); add targets.

---

## I. The Messenger Garden

> *"I see the conversation log. There is a full, robust messenger-like interface rasterized through our generative UI meta-framework. It moves effortlessly from command line to marimo to a website."*

### Vision

A unified conversation interface where:
- CLI is just "messenger without decorations"
- Marimo notebook is "messenger with reactive cells"
- Website is "messenger with styling"
- All share the same underlying Turn/Message data structures

### Research Synthesis

From [Sendbird](https://sendbird.com/blog/resources-for-modern-chat-app-ui) and [UXPin](https://www.uxpin.com/studio/blog/chat-user-interface-design/):
- Message bubbles distinguish sent/received via alignment (left/right)
- Micro-interactions: editing, reactions, threading, retry
- Real-time typing indicators and smart suggestions
- Seamless time breaks and on-demand message loading

From [Ramotion](https://www.ramotion.com/messenger-application-ui-ux-design-concept/):
- User-centric categorization of messages, statuses, group interactions
- Intuitive navigation across social connections

### Architecture: The Turn Protocol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE TURN PROTOCOL                                     │
│                                                                              │
│   Turn = (speaker: Actor, content: Content, timestamp: Time, meta: Meta)    │
│                                                                              │
│   The SAME Turn projects to ANY target:                                      │
│                                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │    CLI      │  │   Marimo    │  │    Web      │  │    JSON     │        │
│   │             │  │             │  │             │  │             │        │
│   │ [K-gent]:   │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ {"speaker": │        │
│   │ "Hello,    │  │ │ K-gent  │ │  │ │ 💬 K-gent│ │  │  "kgent",  │        │
│   │  friend!"  │  │ │ Hello,  │ │  │ │ Hello,  │ │  │  "content": │        │
│   │             │  │ │ friend! │ │  │ │ friend! │ │  │  "Hello"}  │        │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│         ↑               ↑                ↑                ↑                  │
│         └───────────────┴────────────────┴────────────────┘                  │
│                              SAME TURN                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description | Kgents Mapping |
|---------|-------------|----------------|
| **Unified Turn Log** | Single source of truth for all conversation | `time.conversation.witness` |
| **Reactive Projection** | Same data, different views | `KgentsWidget.project(target)` |
| **K-gent Persona** | Personality coordinates in every message | `SOUL_POLYNOMIAL` eigenvectors |
| **Streaming** | Real-time token streaming with Turn projection | `FluxAgent` + SSE |
| **Threading** | Branching conversations as tree structure | `ModalScope.duplicate()` |
| **Reactions** | Eigenvector feedback (approve/challenge/curious) | `void.gratitude.tithe` |
| **AUP Transport** | HTTP/WebSocket envelopes, spans | `protocols/api/aup.py` channels |

### Target-Specific Projections

**CLI Projection**:
```
[2025-12-14 15:32:01] K-gent: I've been thinking about the nature of agency...
[2025-12-14 15:32:15] You: What have you concluded?
[2025-12-14 15:32:18] K-gent: That the observer and observed are inseparable.
                      [↩ reply] [👁 witness] [🔀 branch]
```

**Marimo Projection**:
```python
@app.cell
def conversation():
    return mo.ui.anywidget(MessengerWidget(turns=conversation_log))

@app.cell
def current_turn(conversation):
    # Reactive: updates when conversation changes
    return conversation.current_turn
```

**Web Projection** (via AUP JSON):
```json
{
  "handle": "self.kgent.dialogue.witness",
  "result": {
    "turns": [
      {"speaker": "kgent", "content": "...", "timestamp": 1734200001},
      {"speaker": "user", "content": "...", "timestamp": 1734200015}
    ]
  }
}
```

### Implementation Path

1. **Phase 1**: `Turn` dataclass + AUP serializer; map to `protocols/api/serializers.py`.
2. **Phase 2**: `MessengerWidget(KgentsWidget[ConversationState])` with 4 projections (CLI/TUI/marimo/JSON) using existing reactive substrate primitives.
3. **Phase 3**: SSE/WebSocket integration via AUP channels; streaming spans and spans→UI overlays.
4. **Phase 4**: Threading/branching via `ModalScope`; add law badges (identity/assoc) per branch.
5. **Phase 5**: Full marimo notebook with reactive cells and AUP client example.

---

## II. The Town Garden

> *"There is a 'small town' of agents, represented as ASCII characters, on a playing field. We limit the density of multi-way conversations as would happen in real life. I would like to select an agent, look at their thoughts, rewind the day, create branching universe, mix it up."*

### Vision

A Smallville-inspired sandbox where:
- Citizens are ASCII glyphs moving on a 2D field
- Conversations are spatially limited (proximity-based)
- Time can be paused, rewound, branched
- Any citizen's internal state is inspectable
- Haiku is used liberally for cheap NPC cognition

### Research Synthesis

From [Stanford Generative Agents](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763):
- World organized as tree: root → areas → subareas → objects
- Agents remember subgraph of world they've seen
- Users can embody agents or issue "inner voice" directives
- Emergent behavior: Valentine's Day party from single seed

From [JASSS Guidelines](https://www.jasss.org/12/2/1.html):
- Transparency for overlapping agents
- Texture to encode multiple variables
- Semantic depth of field (crispness) for focus

From [Victor Dibia's 4 UX Principles](https://newsletter.victordibia.com/p/4-ux-design-principles-for-multi):
- Capability discovery: help users understand what agents can do
- Observability and provenance: trace agent actions
- Nudge toward high-reliability tasks

### Architecture: The Town Protocol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT TOWN FIELD                                      │
│                                                                              │
│   +----------------------------------------------------------+              │
│   |                    Day 47, 14:32                         |              │
│   |                                                          |              │
│   |      B                    · · · pheromone · · ·          |              │
│   |           H         ···                                  |              │
│   |                ···       T          M                    |              │
│   |        ···                                   S           |              │
│   |   ···                            P                       |              │
│   |                        [K]  <-- selected                 |              │
│   |          W                                               |              │
│   +----------------------------------------------------------+              │
│                                                                              │
│   [Space] Pause  [←→] Rewind/FF  [Enter] Select  [B] Branch  [T] Thoughts   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ [K] K-gent (REFLECTING)                                              │   │
│   │ Warmth: ███████░░░ 0.72  | Trust: █████████░ 0.91                   │   │
│   │ Current thought: "The conversation with Builder was illuminating..." │   │
│   │ Memory: 47 engrams | Coalitions: [Philosophers, Builders]           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description | Kgents Mapping |
|---------|-------------|----------------|
| **Spatial Field** | 2D grid with citizens as glyphs | `EigenvectorScatterWidget` |
| **Proximity Conversations** | Only adjacent citizens can converse | `TOWN_OPERAD.greet` |
| **Time Control** | Pause/rewind/fast-forward simulation | Redux-style time travel |
| **Branching Universe** | Fork reality at any point | `ModalScope.duplicate()` |
| **Thought Inspector** | View any citizen's internal state | `self.soul.witness` |
| **Cheap Cognition** | Haiku for NPC thoughts, Sonnet for evolving citizens | LLM budget rule |
| **AUP Streaming** | Town flux via `town:{id}` channel | `protocols/api/aup.py` |

### Time Travel Debugging

Inspired by [Redux DevTools](https://blog.logrocket.com/redux-devtools-tips-tricks-for-faster-debugging/):

```
Timeline: ════════════════════════════════════════════════════════════════
          │ Day 1    │ Day 2    │ Day 3    │ Day 4    │ Day 5    │
          │          │          │          │    ▼     │          │
          │          │          │          │ [NOW]    │          │
          └──────────┴──────────┴──────────┴──────────┴──────────┘

Actions:  [Greet] [Trade] [Gossip] [Reflect] [Sleep] [Wake] [Greet]...

Branch Points: ★ Day 2 (Valentine proposal) ★ Day 4 (Coalition formed)

[J] Jump to action  [S] Skip action  [R] Replay from start  [B] Branch here
```

Key capabilities from [Redux DevTools patterns](https://medium.com/the-web-tub/time-travel-in-react-redux-apps-using-the-redux-devtools-5e94eba5e7c0):
- **Action List**: Every dispatched action in chronological order
- **Jump to State**: Click any action to restore state
- **Skip Actions**: Remove action from middle, rebuild state
- **Replay**: Reproduce exact sequence leading to a state
- **Export/Import**: Save timeline as file, share/reload

### Branching Universe

```python
# User sees interesting state, wants to explore alternate path
universe_a = town.snapshot()  # Current timeline

# Branch: what if Builder had rejected K-gent's proposal?
universe_b = town.branch(
    at_action="Day2_Greet_KgentToBuilder",
    alternate_outcome={"accepted": False}
)

# Both universes now evolve independently
# User can switch between them, compare outcomes
```

### LLM Budget Strategy

| Citizen Type | LLM Model | Token Budget | Frequency |
|--------------|-----------|--------------|-----------|
| Background NPC | Haiku | 100 tokens/turn | Every 10 ticks |
| Active NPC | Haiku | 500 tokens/turn | Every tick |
| Evolving Citizen | Sonnet | 2000 tokens/turn | On interaction |
| K-gent | Opus | Unlimited | Always |

From `meta.md` learning: "LLM budget rule: evolving citizens + archetype leaders only (3-5 of 25)"

### Implementation Path

1. **Phase 1**: Extend `EigenvectorScatterWidget` (existing reactive) with selection + AUP feed (`town:{id}` SSE/WebSocket).
2. **Phase 2**: Time control (pause/play/step) backed by D-gent witness and trace monoid, not ad-hoc Redux.
3. **Phase 3**: Snapshot/restore with independence relations; storage budget + backpressure policy.
4. **Phase 4**: Branching via `ModalScope` + UI handles; law badge for associativity of branch merges.
5. **Phase 5**: Thought inspector panel (reuse AgentCard state + memory stats).
6. **Phase 6**: LLM budget hooks (Haiku/Sonnet) gated by metabolics and AUP metadata.

---

## III. The Forge Garden

> *"A workbench, music DAW/Fruity Loops, forge-like interface for simulating, eval'ing, doing constructive surgery to create agents or agentic workflows."*

### Vision

A visual composition environment where:
- Agents are "instruments" that can be placed on tracks
- Workflows are "arrangements" with visual wiring
- Eval is "mixing/mastering" with real-time feedback
- Everything is drag-and-drop, node-based composition

### Research Synthesis

From [LANDR DAW Review](https://blog.landr.com/best-daw/):
- Ableton's Session View: audition/cycle different combinations
- Bitwig's modular routing: any signal to any destination
- Push controller: tactile, intuitive interaction

From [Generative Audio Workstations](https://www.audiocipher.com/post/generative-audio-workstation):
- AI VSTs: generate within existing workflow
- Google Gemini watching DAW giving realtime feedback
- LLMs generating reasoning traces + task-specific actions

From [yWorks Decision Trees](https://www.yworks.com/pages/interactive-decision-tree-diagrams):
- Hide branches not yet taken
- New elements added without disturbing mental map
- Animations for transitions

### Architecture: The Agent DAW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENT FORGE                                           │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ PALETTE                │ ARRANGEMENT                                    │ │
│ │ ┌─────────────────────┐ │ ┌───────────────────────────────────────────┐ │ │
│ │ │ PRIMITIVES          │ │ │ Track 1: [GROUND]──>[JUDGE]──>[SUBLATE]  │ │ │
│ │ │ ○ Ground            │ │ │                         ↓                 │ │ │
│ │ │ ○ Judge             │ │ │ Track 2: [MEMORY]──────────>[SYNTHESIZE]  │ │ │
│ │ │ ○ Sublate           │ │ │                                    ↓      │ │ │
│ │ │ ○ Synthesize        │ │ │ Track 3: [K-GENT]────────────>[OUTPUT]    │ │ │
│ │ │ ○ Project           │ │ │                                           │ │ │
│ │ │ ○ ...               │ │ └───────────────────────────────────────────┘ │ │
│ │ │                     │ │                                               │ │
│ │ │ POLYNOMIALS         │ │ ┌───────────────────────────────────────────┐ │ │
│ │ │ ◉ Soul              │ │ │ INSPECTOR                                  │ │
│ │ │ ◉ Memory            │ │ │ Selected: JUDGE                            │ │
│ │ │ ◉ Evolution         │ │ │ Positions: [DELIBERATING, JUDGING, DONE]  │ │
│ │ │ ◉ Citizen           │ │ │ Current: DELIBERATING                     │ │
│ │ │                     │ │ │ Directions: {Claim, Evidence, Counter}    │ │
│ │ │ COMPOSED            │ │ │ Transition: Pure function                 │ │
│ │ │ ◆ Alethic Agent     │ │ │ Laws: ✓ Identity  ✓ Associativity        │ │
│ │ │ ◆ Dialectic Agent   │ │ └───────────────────────────────────────────┘ │ │
│ │ │ ◆ Custom...         │ │                                               │ │
│ │ └─────────────────────┘ │                                               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ TRANSPORT                                                               │ │
│ │ [▶ Run] [⏸ Pause] [⏹ Stop] [⏺ Record] | Input: [         ] | Output: █ │ │
│ │                                                                         │ │
│ │ Console: Running GROUND... ✓ | Running JUDGE... thinking...            │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description | Kgents Mapping |
|---------|-------------|----------------|
| **Palette** | Drag-and-drop agent primitives | `agents/poly/primitives.py` |
| **Arrangement** | Visual wiring diagram | `WiringDiagram` composition |
| **Inspector** | View polynomial structure | `PolyAgent.positions/directions` |
| **Transport** | Run/pause/step execution | `FluxAgent` control |
| **Console** | Real-time execution trace | `time.trace.witness` |
| **Law Verification** | Visual ✓/✗ for category laws | `OperadRegistry.verify_all()` |
| **AUP Export** | Export to AUP compose payloads | `protocols/api/aup.py` |

### Eval Mode: The Mixing Console

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVAL CONSOLE                                          │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────────┐│
│   │ Test Cases          │ Results          │ Metrics                       ││
│   │ ┌─────────────────┐ │ ┌──────────────┐ │ ┌─────────────────────────┐   ││
│   │ │ [✓] Basic claim │ │ │ Pass: 47/50  │ │ │ Accuracy: 94%           │   ││
│   │ │ [✓] Edge case   │ │ │ Fail: 3/50   │ │ │ Latency p50: 1.2s       │   ││
│   │ │ [✗] Adversarial │ │ │ Skip: 0      │ │ │ Token/req: 847          │   ││
│   │ │ [~] Ambiguous   │ │ │              │ │ │ Cost: $0.034            │   ││
│   │ │ ...             │ │ │ [View Fails] │ │ │                         │   ││
│   │ └─────────────────┘ │ └──────────────┘ │ └─────────────────────────┘   ││
│   └────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│   TRACE (Failed Test: Adversarial)                                          │
│   ┌────────────────────────────────────────────────────────────────────────┐│
│   │ 1. [GROUND] Input: "The sky is always green"                           ││
│   │    → Evidence: 0 supporting, 3 contradicting                           ││
│   │    → Confidence: 0.12 (low)                                            ││
│   │                                                                         ││
│   │ 2. [JUDGE] Deliberating...                                             ││
│   │    → ⚠ Model hallucinated supporting evidence                          ││
│   │    → Verdict: TRUE (incorrect!)                                         ││
│   │                                                                         ││
│   │ 3. [SUBLATE] Synthesizing...                                           ││
│   │    → Output: "The sky is green due to atmospheric..."                  ││
│   └────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Constructive Surgery

```python
# Visual representation becomes code
forge_diagram = ForgeWidget()

# User drags and connects in UI:
# [GROUND] → [CUSTOM_FILTER] → [JUDGE] → [OUTPUT]

# Export to Python:
pipeline = forge_diagram.export_python()
# Output:
# from agents.poly import sequential
# pipeline = sequential(GROUND, custom_filter, JUDGE)

# Or export to AGENTESE:
path = forge_diagram.export_agentese()
# Output: "world.claim.ground >> concept.filter.custom >> world.claim.judge"
```

### Implementation Path

1. **Phase 1**: Palette widget using existing reactive primitives; list comes from operad registry.
2. **Phase 2**: Canvas widget using reactive layout; no new state system—Signal/Computed only.
3. **Phase 3**: Connection/wiring with type checking against PolyAgent signatures + operad slots.
4. **Phase 4**: Transport controls with FluxAgent; perturbation via HITL cards/pads.
5. **Phase 5**: Inspector panel with law badges (identity/assoc) tied to BootstrapWitness.
6. **Phase 6**: Eval mode with test case management + metabolics; export spans for AUP.
7. **Phase 7**: Export to Python/AGENTESE/AUP compose payloads.

---

## IV. The Traces Garden

> *"Richly detailed, fractal-like, mesmerizing traces on past decisions, incorporated decision points, dreams undreamt?"*

### Vision

A visualization of agent history that:
- Shows decision trees as fractal structures
- Highlights "roads not taken" (counterfactuals)
- Reveals hidden patterns through visual density
- Feels alive, organic, breathing

### Research Synthesis

From [Fractal Hierarchy Visualization](http://www.pitecan.com/presentations/DEWS98/FractalViewTree/FractalViewTree.html):
- Self-similarity allows interaction at any scale
- Width increases exponentially with depth
- Fractal approaches make huge trees navigable

From [Pythagoras Trees](https://www.researchgate.net/publication/314585619_Generalized_Pythagoras_Trees_A_Fractal_Approach_to_Hierarchy_Visualization):
- Each vertex sized by metric (importance/impact)
- Recursive structure reveals hierarchy naturally
- Interactions for zoom, browse, filter

From [LLM Observability](https://langfuse.com/docs/observability/overview):
- Traces as spans representing workflow steps
- Visual traces replace text log traversal
- Expand steps to see prompts, responses, metadata

### Architecture: The Decision Archaeology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRACE ARCHAEOLOGY                                     │
│                                                                              │
│   Session: 2025-12-14 | Agent: K-gent | Turns: 847 | Decisions: 2,341      │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────────┐│
│   │                                                                         ││
│   │                              ┌─┐                                        ││
│   │                             ╱   ╲                                       ││
│   │                            ╱     ╲                                      ││
│   │                       ┌───┴───┐   ├───────┐                             ││
│   │                      ╱   ◉    ╲ ╱   ○     ╲    ← taken / not taken     ││
│   │                     ╱  ACCEPT  ╳  REJECT   ╲                            ││
│   │                ┌───┴──┐      ╱ ╲      ┌────┴───┐                        ││
│   │               ╱  ◉    ╲    ╱   ╲    ╱    ○     ╲                        ││
│   │              ╱ EXPLORE ╲  │     │  ╱  RETREAT   ╲                       ││
│   │          ┌──┴──┐ ┌──┴──┐ │     │ ┌──┴──┐ ┌──┴──┐                       ││
│   │         ╱  ◉   ╲╱  ○   ╲│     │╱  ○   ╲╱  ○   ╲                        ││
│   │        ╱ DEEP   ╲ WIDE  │     │ FAST   ╲ SLOW  ╲                       ││
│   │       ╱    ▼     ╲      │     │         ╲       ╲                      ││
│   │      [CURRENT]    ╲     │     │ Dreams   ╲       ╲                     ││
│   │                    ╲    │     │ undreamt  ╲       ╲                    ││
│   │                     (faded paths continue fractally...)                 ││
│   │                                                                         ││
│   └────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│   ◉ = Path taken    ○ = Path not taken (counterfactual)                     │
│   Brightness = Confidence    Size = Impact    Color = Domain                 │
│                                                                              │
│   [Hover: View decision context]  [Click: Explore branch]  [Scroll: Zoom]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description | Kgents Mapping |
|---------|-------------|----------------|
| **Fractal Tree** | Self-similar at all scales | Pythagoras tree algorithm |
| **Taken Paths** | Bright, full opacity | `time.trace.witness` |
| **Counterfactuals** | Faded, "dreams undreamt" | Alternative outputs from LLM |
| **Decision Density** | Visual heat from decision clusters | Pheromone-like gradients |
| **Zoom Semantic** | Deeper zoom = more detail | LOD 0→1→2→3 navigation |
| **Time Animation** | Watch tree grow over session | CSS transitions |

### Dreams Undreamt: Counterfactual Visualization

```python
# During agent execution, capture alternatives:
@dataclass(frozen=True)
class DecisionPoint:
    """A moment where an agent chose among alternatives."""
    timestamp: float
    agent_id: str
    chosen: str           # What was selected
    alternatives: tuple[str, ...]  # What was NOT selected
    confidence: float     # How sure was the agent
    context: str          # Why this decision mattered

# The "dreams undreamt" are the alternatives
# They fade into the fractal background
# But clicking them shows "what could have been"
```

### The Breathing Fractal

Entropy makes the tree alive:

```python
def animate_trace_tree(tree: TraceTree, t: float, entropy: float) -> None:
    """
    The tree breathes with entropy.

    - Low entropy: Tree is still, focused
    - High entropy: Branches sway, counterfactuals glow
    - The Accursed Share makes dreams visible
    """
    distortion = entropy_to_distortion(entropy, tree.seed, t)

    for branch in tree.branches:
        if branch.taken:
            # Taken paths: subtle pulse
            branch.opacity = 1.0
            branch.scale = 1.0 + distortion.pulse * 0.05
        else:
            # Dreams undreamt: glow with entropy
            branch.opacity = 0.2 + entropy * 0.3
            branch.jitter = (distortion.jitter_x, distortion.jitter_y)
```

### Implementation Path

1. **Phase 1**: `TraceTree` data structure with decision points
2. **Phase 2**: Basic tree rendering (no fractal yet) using existing reactive renderer (CLI/TUI/marimo).
3. **Phase 3**: Pythagoras tree algorithm for fractal layout
4. **Phase 4**: Counterfactual capture during agent execution
5. **Phase 5**: Entropy-based animation
6. **Phase 6**: Interactive navigation (zoom, hover, click)
7. **Phase 7**: Integration with `time.trace.witness` path + AUP streaming for browser clients

---

## Cross-Synergies: The Unified Vision

### All Four Gardens Share

| Shared Element | Implementation |
|----------------|----------------|
| **Turn/Event Log** | `time.*.witness` paths |
| **Time Control** | Redux-like state snapshots |
| **Branching** | `ModalScope.duplicate()` |
| **Projection** | `KgentsWidget.project(target)` |
| **Entropy** | `entropy_to_distortion()` pure function |
| **LLM Integration** | Haiku cheap, Sonnet moderate, Opus premium |

### The Meta-Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GENERATIVE UI META-FRAMEWORK                              │
│                                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│   │  MESSENGER  │     │    TOWN     │     │   FORGE     │                   │
│   │  (Turns)    │     │  (Citizens) │     │  (Agents)   │                   │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│          │                   │                   │                           │
│          └───────────────────┼───────────────────┘                           │
│                              ▼                                               │
│                    ┌─────────────────┐                                       │
│                    │  REACTIVE       │                                       │
│                    │  SUBSTRATE      │                                       │
│                    │  (Signal[T])    │                                       │
│                    └────────┬────────┘                                       │
│                             │                                                │
│          ┌──────────────────┼──────────────────┐                            │
│          ▼                  ▼                  ▼                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│   │     CLI     │   │   Marimo    │   │    TUI      │   │    Web      │     │
│   │  (ASCII)    │   │ (anywidget) │   │  (Textual)  │   │   (JSON)    │     │
│   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│                                                                              │
│                              ↑                                               │
│                    ┌─────────────────┐                                       │
│                    │    TRACES       │                                       │
│                    │ (Decision Tree) │                                       │
│                    └─────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mapping to Existing Architecture

| Vision | Existing Code | Gap Analysis |
|--------|---------------|--------------|
| Messenger | `agents/k/dialogue.py` | Need Turn widget, streaming projection |
| Town Field | `agents/town/visualization.py` | Need time control, branching |
| Town Citizens | `agents/town/citizen.py` | Need thought inspector |
| Forge Palette | `agents/poly/primitives.py` | Need drag-and-drop widget |
| Forge Wiring | `agents/poly/wiring.py` | Need visual canvas |
| Traces | `time.trace.witness` | Need fractal visualization |
| Reactive Substrate | `agents/i/reactive/` | Good foundation; reuse for all skins |
| AUP | `protocols/api/aup.py`, serializers | Map all projections to AUP HTTP/WS |
| NATS/SSE | Town streaming | Verify AUP envelope + spans passthrough |

---

## Refined Journeys (human, operator, agent)
- **Human composer**: Starts Messenger in CLI, escalates to marimo for live widgets; drags Town/Forge slots via isometric/TUI skins; perturbations via pads; shares AUP link so friends join via browser.
- **Operator/SRE**: Lives in Textual dashboard; watches AUP endpoint SLOs, flux metabolics, and trace braids; can throttle entropy, quarantine slop blooms, replay incident timelines; uses same AUP channels, no hidden backdoors.
- **Agent-as-user**: Connects via AUP WebSocket, pulls GardenState, proposes new slot attachment; human approves via HITL card; perturbation injected lawfully into Flux; agent can subscribe to trace channel for self-debugging.
- **Educator/demo**: Runs marimo notebook; shows identity/associativity badges by swapping rails; toggles targets (CLI/TUI/Web) to prove functorial projection; uses fractal traces to reveal “dreams undreamt.”

---

## Prioritized Implementation Roadmap

### Wave 1: Foundation (Enables All Gardens)
1. Extend `Signal[T]` with state snapshots for time travel
2. Add `ModalScope.duplicate()` for branching
3. Create unified `Turn` dataclass
4. Implement `entropy_to_distortion()` as pure Python function

### Wave 2: The Messenger
1. `MessengerWidget(KgentsWidget[ConversationState])`
2. CLI, TUI, marimo, JSON projectors
3. SSE streaming integration
4. K-gent persona in every message

### Wave 3: The Town
1. Time control (pause/rewind/branch)
2. Click-to-select citizen
3. Thought inspector panel
4. Haiku integration for cheap NPC thoughts

### Wave 4: The Forge
1. Palette widget with agent primitives
2. Canvas with node placement
3. Wiring/connection system
4. Transport controls

### Wave 5: The Traces
1. `TraceTree` data structure
2. Pythagoras tree layout algorithm
3. Counterfactual capture
4. Entropy animation

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Same widget → 4 targets | ✓ | Unified substrate proof |
| Time travel state count | 1000+ | Enough history for debugging |
| Branch creation time | <100ms | Interactive feel |
| Haiku cost per NPC thought | <$0.001 | Cheap cognition budget |
| Fractal render depth | 10 levels | Sufficient decision archaeology |
| AUP endpoint latency (p95) | <400ms | Keeps browser/TUI responsive |
| SSE/WebSocket error rate | <0.1% | Reliability target |
| Kent says "amazing" | ✓ | The Mirror Test |

---

## The Enlightened Vision

> *"These four gardens are not separate applications. They are FOUR PROJECTIONS of the SAME underlying AGENTESE substrate."*

The Messenger shows conversation.
The Town shows agents.
The Forge shows composition.
The Traces show history.

But underneath, it's all:
- **Turns** flowing through **time**
- **Agents** composing via **operads**
- **State** projected to **targets**
- **Entropy** bringing **life**

The interface IS the system, made visible.

---

## Sources

- [Stanford Generative Agents (SIMULACRA)](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763)
- [Victor Dibia: 4 UX Principles for Multi-Agent Systems](https://newsletter.victordibia.com/p/4-ux-design-principles-for-multi)
- [JASSS: Agent-Based Model Visualization Guidelines](https://www.jasss.org/12/2/1.html)
- [Redux DevTools Time Travel](https://medium.com/the-web-tub/time-travel-in-react-redux-apps-using-the-redux-devtools-5e94eba5e7c0)
- [Langfuse: AI Agent Observability](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse)
- [Generative Audio Workstations](https://www.audiocipher.com/post/generative-audio-workstation)
- [Fractal Hierarchy Visualization](http://www.pitecan.com/presentations/DEWS98/FractalViewTree/FractalViewTree.html)
- [Pythagoras Trees for Hierarchy Visualization](https://www.researchgate.net/publication/314585619_Generalized_Pythagoras_Trees_A_Fractal_Approach_to_Hierarchy_Visualization)
- [Sendbird: Chat UI Resources](https://sendbird.com/blog/resources-for-modern-chat-app-ui)
- [UXPin: Chat Interface Design](https://www.uxpin.com/studio/blog/chat-user-interface-design/)
- [Nayuki: Pythagoras Tree Algorithm](https://www.nayuki.io/page/pthagoras-tree)
- [Figma Audio DAW Kits](https://www.figma.com/community/file/1027361920979577146)
- [Isometric UI Inspiration](https://dribbble.com/tags/isometric_ui)

---

## Continuation

```
⟿[IMPLEMENT]
/hydrate prompts/visionary-ux-implement.md
handles: research=complete; four_gardens=defined; substrate=mapped
mission: Begin Wave 1 Foundation implementation
exit: Signal snapshots + ModalScope branching + Turn dataclass
```

---

*"The noun is a lie. There is only the rate of change—and now, the rate of change is visible in four gardens that are one garden."*
