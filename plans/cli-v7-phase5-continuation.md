# CLI v7 Phase 5: Collaborative Canvas — Continuation Prompt

**For**: Next session agent
**From**: Session 2025-12-20 (Phase 4 completion)
**Principle**: *"The canvas is where we meet. Your cursor and mine, dancing through the garden together."*

---

## 🎯 GROUND IN KENT'S INTENT FIRST

> *"The Mirror Test: Does K-gent feel like me on my best day?"*
> *"Daring, bold, creative, opinionated but not gaudy"*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

---

## Context: Where We Are

**Phases 0-4 COMPLETE** (382 conductor + REPL tests passing):

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 0 | ✅ | Ground Truth (CLI v6) |
| Phase 1 | ✅ | File I/O: `world.file.read`, `world.file.edit`, FileEditGuard |
| Phase 2 | ✅ | Deep Conversation: ConversationWindow (35-turn), Summarizer |
| Phase 3 | ✅ | Agent Presence: CursorState, AgentCursor, PresenceChannel, CircadianPhase |
| Phase 4 | ✅ | REPL: `/memory`, `/presence`, presence footer after invocations |

**Test health**: `uv run pytest services/conductor/ protocols/cli/_tests/test_repl.py -q` → 382 passed

---

## Phase 5: Collaborative Canvas (Web)

> *"A shared mind-map surface where humans and agents have visible presence."*

### Vision

The full Figma-like experience: infinite canvas, agent cursors, AGENTESE nodes as navigable space, real-time collaboration. Inspired by:

- **[Miro](https://miro.com/mind-map/)**: Infinite canvas with AI-powered branching
- **[FigJam](https://www.figma.com/figjam/)**: Real-time cursor presence, smooth interpolation
- **sshx**: Browser-accessible terminal sharing (already have `kg self.conductor.share`)

### Crown Jewel Patterns to Apply

| Pattern | Application |
|---------|-------------|
| **#11 Circadian Modulation** | Canvas warmth/brightness adjusts by time of day |
| **#13 Contract-First Types** | Canvas components use generated types from BE |
| **#14 Teaching Mode Toggle** | Explanatory overlays on AGENTESE nodes |

---

## Deliverables

### 5.1 Canvas as Projection Target (Fidelity 0.9)

**Location**: `agents/i/reactive/projection/targets.py`

```python
@ProjectionRegistry.register("canvas", fidelity=0.9)
def canvas_projector(widget) -> dict:
    """HIGH fidelity - full visual, interactive, animated."""
    return {
        "type": "canvas_node",
        "position": widget.state.position,
        "content": widget.to_json(),
        "connections": widget.state.connections,
        "animation": widget.state.animation_speed,
    }
```

### 5.2 React Components

**Location**: `impl/claude/web/src/components/canvas/` (or `services/conductor/web/`)

| Component | Purpose |
|-----------|---------|
| `CollaborativeCanvas.tsx` | Infinite canvas with pan/zoom |
| `AgentNode.tsx` | Render AGENTESE node with teaching overlays |
| `AnimatedCursor.tsx` | Agent cursor with circadian tempo |
| `ConnectionLayer.tsx` | Lines between connected nodes |

### 5.3 WebSocket Presence Hook

**Location**: `impl/claude/web/src/hooks/usePresenceChannel.ts`

Already exists! Check current implementation:
```typescript
// Connect to presence SSE/WebSocket
// Render cursors from PresenceChannel
```

### 5.4 Agent Cursor Behaviors

**Location**: `services/conductor/behaviors.py` (NEW)

```python
class CursorBehavior(Enum):
    FOLLOWER = "follower"     # Follows human with slight delay
    EXPLORER = "explorer"     # Independent exploration
    ASSISTANT = "assistant"   # Follows but occasionally suggests
    AUTONOMOUS = "autonomous" # Does its own thing entirely
```

### 5.5 AI-Powered Branch Suggestions

**Location**: `protocols/agentese/contexts/self_conductor.py` (extend existing)

```python
@node(path="self.conductor.canvas.suggest")
async def suggest_branches(observer, focus_path: str) -> list[SuggestionResponse]:
    """Miro-inspired: suggest related AGENTESE nodes."""
```

---

## Existing Infrastructure to Build On

### Already Implemented

| Component | Location | Notes |
|-----------|----------|-------|
| **PresenceChannel** | `services/conductor/presence.py` | Async pub/sub for cursor updates |
| **AgentCursor** | `services/conductor/presence.py` | Has `to_cli()`, `to_dict()`, state transitions |
| **CursorState** | `services/conductor/presence.py` | Enum with emoji, color, animation_speed |
| **CircadianPhase** | `services/conductor/presence.py` | Time-of-day modulation |
| **render_presence_footer** | `services/conductor/presence.py` | CLI projection (adapt for canvas) |
| **usePresenceChannel** | `impl/claude/web/src/hooks/` | May need enhancement |

### Check These Files First

```bash
# Presence infrastructure
impl/claude/services/conductor/presence.py

# Existing hooks
impl/claude/web/src/hooks/usePresenceChannel.ts
impl/claude/web/src/hooks/useCanvasNodes.ts

# Canvas page (may exist)
impl/claude/web/src/pages/Canvas.tsx
```

---

## Entry Points

### Option A: Canvas Component First (Recommended)

1. Create `CollaborativeCanvas.tsx` with basic pan/zoom (use react-zoom-pan-pinch or similar)
2. Render static AGENTESE nodes from registry
3. Add `usePresenceChannel` hook for cursor updates
4. Render `AnimatedCursor` for each agent

### Option B: Backend Projection First

1. Add canvas projection target to `ProjectionRegistry`
2. Create `self.conductor.canvas.state` node for canvas state
3. Wire to React via SSE endpoint

### Option C: Cursor Animation First

1. Create `CursorAnimator` class with behavior patterns
2. Add `AnimatedCursor.tsx` component
3. Test with mock cursor data
4. Integrate with live PresenceChannel

---

## Exit Condition

**Phase 5 is complete when**:

1. Opening `/canvas` feels like entering a shared space
2. Agent cursors move with personality (follower, explorer behaviors)
3. AGENTESE nodes are navigable (click to invoke)
4. Circadian modulation makes evening sessions feel warmer
5. Teaching mode explains the ontology with overlays

**Quality Benchmark**: *"The coworking test: Does it feel like working alongside someone?"*

---

## Test Strategy

| Type | Target | Focus |
|------|--------|-------|
| Type I (Unit) | 15 | Canvas state, cursor animation math |
| Type II (Integration) | 8 | Presence hook + canvas rendering |
| Type III (Property) | 5 | Animation interpolation bounds |
| Type IV (E2E) | 8 | Full canvas interaction flow |
| **Total** | **36** | |

**Performance baseline**: Canvas render (100 nodes) < 16ms (60fps)

---

## Commands to Verify

```bash
# Backend tests
cd impl/claude && uv run pytest services/conductor/ -q

# Frontend typecheck
cd impl/claude/web && npm run typecheck

# Full verification
cd impl/claude && uv run pytest -q && uv run mypy .
```

---

## Voice Anchors (Keep These Close)

| Anchor | When to Use |
|--------|-------------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making canvas aesthetic decisions |
| *"The persona is a garden, not a museum"* | Canvas should feel alive, not static |
| *"Tasteful > feature-complete"* | Don't over-engineer the first pass |
| *"Joy-inducing"* | Cursor animations should delight |

---

## Anti-Sausage Check Before Ending

- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Did I add words Kent wouldn't use?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*

---

*Created: 2025-12-20 | Phase 4 Complete → Phase 5 Ready*
*"The canvas is where we meet."*
