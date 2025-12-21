# Interactive Text Gallery Page

> *"The text IS the interface."*

---

## Session Prompt

```
/hydrate

Create an Interactive Text Gallery page at `/_/gallery/interactive-text`.

## Context

The Interactive Text × Servo bridge is complete. Three systems are now unified:

1. **Interactive Text** (`services/interactive_text/`) — parses markdown → MeaningTokens
2. **tokens_to_scene bridge** (`protocols/agentese/projection/tokens_to_scene.py`) — MeaningTokens → SceneGraph
3. **Servo** (`web/src/components/servo/`) — renders SceneGraph to React

The bridge works (18 tests passing) but there's no UI to showcase it. Your mission: build a gallery page.

## The Existing Pattern

Study these files to understand gallery page architecture:

1. `web/src/App.tsx` — Routes at lines 58-65, `/_/` prefix for developer galleries
2. `web/src/pages/GalleryPage.tsx` — Full gallery with category filtering
3. `web/src/pages/LayoutGallery.tsx` — Simpler gallery with "pilot" pattern

Key patterns:
- Lazy loading via `lazy(() => import(...))`
- Living Earth theme colors
- PilotContainer pattern for showcasing components
- Joy components for loading/error states

## Your Mission

### 1. Create the Gallery Page

Create `web/src/pages/InteractiveTextGallery.tsx`:

```typescript
/**
 * InteractiveTextGallery: Demonstrates the Interactive Text × Servo bridge.
 *
 * Pilots:
 * 1. Token Parser Demo - Parse markdown, show token breakdown
 * 2. AGENTESE Portal - Show interactive path tokens with hover/click
 * 3. Task Toggle - Show checkbox tokens with toggle interaction
 * 4. Code Region - Show code block tokens with syntax highlighting
 * 5. Full Document - Render a complete markdown file as SceneGraph
 * 6. Token Comparison - Show same content in different density modes
 *
 * @see protocols/agentese/projection/tokens_to_scene.py - Bridge
 * @see components/servo/MeaningTokenRenderer.tsx - Token renderer
 */
```

### 2. Add the Route

In `web/src/App.tsx`, add:

```typescript
const InteractiveTextGallery = lazy(() => import('./pages/InteractiveTextGallery'));

// In routes (around line 59):
<Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />
```

### 3. Create API Endpoint (Optional but Nice)

If you want live parsing, add an endpoint in `protocols/api/routes/document.py`:

```python
@router.post("/document/parse")
async def parse_document(text: str) -> dict:
    """Parse markdown and return SceneGraph."""
    from protocols.agentese.projection.tokens_to_scene import markdown_to_scene_graph
    scene = await markdown_to_scene_graph(text)
    return scene.to_dict()
```

### 4. Key Components to Use

Already built, just wire up:

```typescript
// Token rendering
import { MeaningTokenRenderer } from '@/components/servo/MeaningTokenRenderer';
import { ServoSceneRenderer } from '@/components/servo/ServoSceneRenderer';

// Joy components
import { PersonalityLoading, EmpathyError } from '@/components/joy';

// Theme
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from '@/components/servo/theme';
```

### 5. Demo Data

Use the sample markdown from `demos/interactive_text_demo.py`:

```typescript
const SAMPLE_MARKDOWN = `
# Interactive Text Demo

Check \`self.brain.capture\` for memory operations.
Navigate to \`world.town.citizen\` to see agent simulation.

## Tasks

- [x] Create tokens_to_scene_graph bridge
- [ ] Wire up AGENTESE navigation

## Code Example

\`\`\`python
pipeline = AgentA >> AgentB >> AgentC
\`\`\`

See [P1] (Tasteful) and [R2.1] for design rationale.
`;
```

### 6. Pilot Ideas

| Pilot | What It Shows |
|-------|---------------|
| **Token Parser** | Input textarea + live parse → show token breakdown |
| **AGENTESE Portal** | Render `self.brain.capture` with hover state display |
| **Task Toggle** | Render checkboxes, click to toggle, show state change |
| **Code Region** | Render code block with language badge |
| **Mixed Document** | Full markdown → ServoSceneRenderer |
| **Density Comparison** | Same content at COMPACT vs SPACIOUS |

### 7. Interaction Wiring (Stretch Goal)

If time permits, wire up actual interactions:

```typescript
// AGENTESE path click → navigate
const handleNodeSelect = (node: SceneNode) => {
  const path = node.content?.token_data?.path;
  if (path) {
    navigate(`/${path}`);  // AGENTESE-as-route
  }
};

// Task toggle → state update
const handleTaskToggle = async (node: SceneNode) => {
  // Call backend to toggle task in source file
};
```

## Files to Read First

1. `protocols/agentese/projection/tokens_to_scene.py` — The bridge (understand the types)
2. `web/src/components/servo/MeaningTokenRenderer.tsx` — Token renderers
3. `web/src/components/servo/ServoSceneRenderer.tsx` — Scene renderer
4. `demos/interactive_text_demo.py` — Working demo with sample data
5. `web/src/pages/LayoutGallery.tsx` — Gallery page pattern

## Success Criteria

1. **Page loads** at `/_/gallery/interactive-text`
2. **Tokens render** — MeaningTokenRenderer shows styled tokens
3. **Live parse** — Typing in textarea updates token display
4. **Multiple pilots** — At least 4 of the 6 pilots implemented
5. **Joy-inducing** — Breathing containers, Living Earth colors

## Voice Anchors

"Daring, bold, creative, opinionated but not gaudy"
"Tasteful > feature-complete"
"The text IS the interface"
"Joy-inducing > merely functional"

## Anti-Patterns to Avoid

- Don't create a new API pattern — use existing bridge
- Don't duplicate MeaningTokenRenderer logic — reuse it
- Don't skip typecheck — `npm run typecheck` before done
```

---

## Architecture Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  InteractiveTextGallery.tsx (NEW)                                           │
│  - Textarea for input                                                        │
│  - Pilots showcasing tokens                                                  │
│  - ServoSceneRenderer for full documents                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  MeaningTokenRenderer.tsx (EXISTS)                                          │
│  - AGENTESEPortal, TaskToggle, CodeRegion, etc.                             │
│  - Handles all 6 token types + plain text                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ServoSceneRenderer.tsx (EXISTS)                                            │
│  - Renders SceneGraph to React                                              │
│  - Handles layout, selection, edges                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  tokens_to_scene.py (EXISTS)                                                │
│  - markdown_to_scene_graph() convenience function                           │
│  - MeaningTokenContent dataclass                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Wins by Time

### < 30 min: Minimal Gallery
- Create page with hardcoded sample data
- Render tokens via MeaningTokenRenderer
- Add route to App.tsx

### < 1 hour: Live Parsing
- Add textarea input
- Client-side parse (import parser logic)
- Update tokens on input change

### < 2 hours: Full Pilots
- Implement all 6 pilots
- Add density toggle
- Polish with animations

---

*Created: 2025-12-21 | Bridge complete, gallery needed*
*Voice: "The text IS the interface"*
