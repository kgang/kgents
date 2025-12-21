# Interactive Text × Servo × Meaning Tokens: The Unified Projection Surface

> *"Servo is not 'a browser' inside kgents. It is the projection substrate that renders the ontology."*

---

## The Synthesis Insight

Three systems. One vision. **Documents that breathe.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MEANING TOKENS (Atoms)                                                      │
│  - Parser extracts 6 token types from markdown                               │
│  - Each token has affordances (hover, click, drag)                           │
│  - 211 tests, roundtrip fidelity guaranteed                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  SCENE GRAPH (Composition)                                                   │
│  - Nodes + Edges + Layout                                                    │
│  - From protocols/agentese/projection/scene.py                               │
│  - Density-aware (COMPACT/COMFORTABLE/SPACIOUS)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  TERRARIUM VIEW (Observer Lens)                                              │
│  - Selection query (what to show)                                            │
│  - Lens config (how to transform)                                            │
│  - Same content + different observer = different scene                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  SERVO (Projection Substrate)                                                │
│  - ServoSceneRenderer.tsx renders SceneGraph                                 │
│  - Living Earth theme + animations                                           │
│  - Selection + interaction handling                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The Unification**:
```
MeaningToken[] ──compose──▶ SceneGraph ──lens──▶ TerrariumView ──render──▶ Servo
```

A markdown document becomes a **living SceneGraph** where:
- AGENTESE paths are **navigable nodes**
- Task checkboxes are **stateful nodes with toggle affordance**
- Code blocks are **executable nodes**
- The whole document is a **traversable graph**

---

## Session Prompt

```
/hydrate

Synthesize Interactive Text, Servo, and Meaning Tokens into a unified frontend.

## The Three Systems

### 1. Meaning Tokens (services/interactive_text/)
- Parser with 6 token types, 211 tests passing
- Web projector outputs ReactElement specs
- Gap: NO React components consume this yet

### 2. Servo (web/src/components/servo/)
- ServoSceneRenderer renders SceneGraph to React
- ServoNodeRenderer, ServoEdgeRenderer for primitives
- Living Earth theme with animations
- Already handles selection, interaction, density

### 3. TerrariumView (protocols/agentese/projection/terrarium_view.py)
- Observer-dependent lens over data streams
- Selection query + lens config + projection target
- Law 2: Same content + different lens = different scene

## The Synthesis Question

Can we make MeaningTokens compose into SceneGraph, rendered by Servo?

```python
# Current: Separate paths
tokens = parse_markdown(text)           # → MeaningToken[]
react_elements = web_projector(tokens)  # → ReactElement[]  # NO consumer!

scene = create_scene_graph(walk)        # → SceneGraph
rendered = ServoSceneRenderer(scene)    # → React components

# Unified: Tokens AS nodes
tokens = parse_markdown(text)
scene = tokens_to_scene_graph(tokens)   # NEW: MeaningToken[] → SceneGraph
rendered = ServoSceneRenderer(scene)    # Existing: SceneGraph → React
```

## Your Mission

1. **UNDERSTAND**: Read these files in order:
   - services/interactive_text/projectors/web.py (ReactElement output)
   - protocols/agentese/projection/scene.py (SceneGraph definition)
   - web/src/components/servo/ServoSceneRenderer.tsx (React renderer)
   - web/src/components/servo/ServoNodeRenderer.tsx (Node primitives)

2. **DESIGN**: Sketch the bridge
   - How does MeaningToken map to SceneNode?
   - What's the edge structure? (Token adjacency? AGENTESE path links?)
   - How do affordances become interaction handlers?

3. **PROTOTYPE**: Build the minimal bridge
   - Option A: New `tokens_to_scene_graph.py` converter
   - Option B: New SceneNodeKind for each token type
   - Option C: Reuse existing ServoNodeRenderer with token-specific styling

4. **DEMO**: Render one document
   - Parse CLAUDE.md or NOW.md
   - Convert to SceneGraph
   - Render with ServoSceneRenderer
   - See tokens as interactive nodes

## Key Files

### Interactive Text (Backend Complete)
- services/interactive_text/__init__.py — Public API
- services/interactive_text/parser.py — MarkdownParser
- services/interactive_text/projectors/web.py — ReactElement output
- services/interactive_text/tokens/*.py — 6 token implementations

### Scene Graph (Bridge Layer)
- protocols/agentese/projection/scene.py — SceneGraph, SceneNode, SceneEdge
- protocols/agentese/projection/warp_converters.py — Existing converters

### Servo (Frontend Complete)
- web/src/components/servo/ServoSceneRenderer.tsx — Top-level renderer
- web/src/components/servo/ServoNodeRenderer.tsx — Node primitives
- web/src/components/servo/theme.ts — Living Earth palette

### Existing React Infrastructure
- web/src/components/projection/*.tsx — TextWidget, TableWidget, etc.
- web/src/components/genesis/*.tsx — Animation primitives
- web/src/components/joy/*.tsx — Breathe, Shimmer, Pop effects

## Design Constraints

1. **Reuse Servo** — Don't create parallel rendering path
2. **Preserve Affordances** — Token interactions must survive conversion
3. **Observer Dependence** — Different observers see different scenes
4. **Density Awareness** — COMPACT/COMFORTABLE/SPACIOUS from LayoutDirective

## The Dream Demo

Open NOW.md in the web UI:
- Document renders as a SceneGraph
- AGENTESE paths (`self.brain.capture`) are nodes that navigate on click
- Task checkboxes are toggleable nodes with trace witness
- Code blocks have "Run" button affordance
- Hovering shows polynomial state
- The Living Earth theme makes it breathe

## Voice Anchors

"Daring, bold, creative, opinionated but not gaudy"
"Tasteful > feature-complete"
"The persona is a garden, not a museum"
"The webapp is not the UI. The webapp is the composition boundary."
```

---

## Architecture Sketch

```
                          ┌─────────────────────┐
                          │     CLAUDE.md       │
                          │  (Plain Markdown)   │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   MarkdownParser    │
                          │  services/inter...  │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   MeaningToken[]    │
                          │  6 types, affordan. │
                          └──────────┬──────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌───────────┐    ┌───────────┐    ┌───────────┐
            │    CLI    │    │   JSON    │    │    WEB    │
            │ Projector │    │ Projector │    │ Projector │
            └───────────┘    └───────────┘    └─────┬─────┘
                                                    │
                                    ┌───────────────┘
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │  tokens_to_scene()  │ ◀── NEW BRIDGE
                          │   Token → SceneNode │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │     SceneGraph      │
                          │  nodes, edges, lay. │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │  TerrariumView      │
                          │  (Observer Lens)    │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ ServoSceneRenderer  │
                          │  Living Earth Theme │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   React Components  │
                          │  (Interactive DOM)  │
                          └─────────────────────┘
```

---

## Token → SceneNode Mapping (Draft)

| MeaningToken | SceneNodeKind | Visual | Affordances |
|--------------|---------------|--------|-------------|
| AGENTESEPath | `AGENTESE_PORTAL` | Glowing link | Click→navigate, Hover→state |
| TaskCheckbox | `TASK_TOGGLE` | Checkbox icon | Click→toggle, Hover→trace |
| Image | `IMAGE_EMBED` | Thumbnail | Click→expand, Hover→analysis |
| CodeBlock | `CODE_REGION` | Syntax box | Click→edit, DoubleClick→run |
| PrincipleRef | `PRINCIPLE_ANCHOR` | Badge | Hover→tooltip, Click→navigate |
| RequirementRef | `REQUIREMENT_TRACE` | Badge | Hover→status, Click→verification |

Each SceneNode carries:
```typescript
interface TokenSceneNode extends SceneNode {
  kind: 'AGENTESE_PORTAL' | 'TASK_TOGGLE' | ...;
  token: MeaningToken;        // Original token data
  affordances: Affordance[];  // From token definition
  sourcePosition: { start: number; end: number; };
}
```

---

## Quick Wins by Difficulty

### Tier 1: Prove the Bridge (< 1 hour)
- [ ] Write `tokens_to_scene_graph()` converter
- [ ] Test with simple markdown: "Check `self.test`"
- [ ] Log SceneGraph output, verify structure

### Tier 2: Servo Integration (< 2 hours)
- [ ] Add `MEANING_TOKEN` to SceneNodeKind
- [ ] Extend ServoNodeRenderer to handle token nodes
- [ ] Render parsed markdown as SceneGraph

### Tier 3: Interaction Wiring (< 3 hours)
- [ ] Wire click on AGENTESE node → React Router navigation
- [ ] Wire hover → affordance tooltip display
- [ ] Wire task toggle → file mutation + trace

### Tier 4: Full Document View (session goal)
- [ ] Create `InteractiveDocumentView.tsx` page
- [ ] Load markdown file via API
- [ ] Render as ServoSceneRenderer scene
- [ ] Connect to AGENTESE navigation

---

## Success Criteria

By end of session, demonstrate ONE of:
1. **Bridge Working**: `tokens_to_scene_graph()` produces valid SceneGraph
2. **Servo Renders Tokens**: ServoSceneRenderer shows token nodes
3. **Click Works**: AGENTESE path click triggers navigation
4. **Full Demo**: NOW.md renders as interactive scene

*"Joy-inducing > merely functional"* — pick what sparks joy.

---

## The Meta-Vision

This isn't just about rendering markdown nicely. It's about:

**Specs become interfaces.**
**Plans become dashboards.**
**Documentation becomes navigation.**

The Interactive Text Protocol, unified with Servo, makes the entire kgents codebase browsable as a living graph. Every AGENTESE path is a portal. Every task checkbox is a verifiable action. Every code block is executable.

The text IS the interface.

---

*Created: 2025-12-21 | Synthesizing: Interactive Text + Servo + Meaning Tokens*
*Voice: "Daring, bold, creative, opinionated but not gaudy"*
