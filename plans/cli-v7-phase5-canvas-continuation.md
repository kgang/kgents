# Phase 5B: Collaborative Canvas — Continuation Prompt

**Status**: ✅ CORE COMPLETE (Spring Physics + NodeDetailPanel done)
**Created**: 2025-12-20
**Updated**: 2025-12-20
**Foundation**: Canvas.tsx + AgentCanvas.tsx + hooks infrastructure exists
**Goal**: Finish the Figma-like collaborative mind-map experience

## Session 2025-12-20 Accomplishments

| Work Item | Status | Files Created/Modified |
|-----------|--------|------------------------|
| AnimatedCursor with spring physics | ✅ DONE | `web/src/components/canvas/AnimatedCursor.tsx` (252 lines) |
| Behavior-driven spring settings | ✅ DONE | FOLLOWER=300/25, EXPLORER=150/15, ASSISTANT=200/20, AUTONOMOUS=100/10 |
| Circadian tempo modulation | ✅ DONE | Night (0.3) slows animations, morning (1.0) normal speed |
| CursorOverlay updated | ✅ DONE | `CursorOverlay.tsx` now uses AnimatedCursor instead of CSS transitions |
| NodeDetailPanel slide-in | ✅ DONE | `web/src/components/canvas/NodeDetailPanel.tsx` (346 lines) |
| Teaching mode overlays | ✅ DONE | Context explanations (world, self, concept, void, time) |
| Teaching mode toggle | ✅ DONE | BookOpen button in Canvas toolbar |
| Tests passing | ✅ DONE | `pytest services/conductor/_tests/` all pass |

### What's Left (Lower Priority)

| Work Item | Status | Notes |
|-----------|--------|-------|
| WebSocket upgrade | PENDING | SSE works, WebSocket is optimization |
| Share URL implementation | PENDING | `kg self.conductor.share` |
| Mobile touch | PENDING | Pan/zoom touch events |

---

## 🎯 Grounding in Kent's Voice

> *"Agents pretending to be there with their cursors moving, kinda following my cursor, kinda doing its own thing."*

> *"Tasteful > feature-complete"*

> *"The persona is a garden, not a museum"*

The canvas should feel **inhabited**, not just functional. When you're alone, it should feel like others *could* be there. When agents are active, their presence should feel organic, not mechanical.

---

## What Exists (READ FIRST)

### Files to Read

```
impl/claude/web/src/pages/Canvas.tsx              # Main page (418 lines)
impl/claude/web/src/components/canvas/            # AgentCanvas, CursorOverlay, etc.
impl/claude/web/src/hooks/usePresenceChannel.ts   # SSE cursor streaming
impl/claude/web/src/hooks/useCanvasNodes.ts       # AGENTESE node discovery
impl/claude/web/src/hooks/useCircadian.ts         # Time-of-day modulation
impl/claude/web/src/hooks/useUserFocus.ts         # Human focus tracking
impl/claude/web/src/hooks/useCanvasLayout.ts      # Force-directed + drag
impl/claude/web/src/styles/animations.css         # vine-breathe animation
services/conductor/presence.py                    # Backend presence channel
services/conductor/swarm.py                       # Agent spawning
services/conductor/flux.py                        # ConductorFlux event routing (Phase 7)
services/conductor/bus_bridge.py                  # A2A → global SynergyBus bridging
```

### What Works ✅

1. **Node Discovery**: `useCanvasNodes` fetches AGENTESE paths, builds hierarchy
2. **Radial Layout**: Force-directed positioning with drag-and-drop
3. **Organic Connections**: Cubic bezier "vine" paths with gradient + breathing animation
4. **Pan/Zoom**: Infinite canvas with mouse controls
5. **Cursor Overlay**: Basic cursor rendering for agents
6. **Presence SSE**: `usePresenceChannel` connects to `/api/presence/stream`
7. **Circadian Modulation**: Background warmth adjusts by time of day
8. **Demo Mode**: Can spawn simulated agent cursors via `self.presence:demo`
9. **Phase 7 Events**: SWARM_SPAWNED, SWARM_A2A_MESSAGE flow through SynergyBus

### What's Missing ❌

| Gap | Description | Impact |
|-----|-------------|--------|
| **Smooth Cursor Interpolation** | Cursors jump to positions, don't animate | Feels robotic |
| **Real Backend Presence** | Demo mode only; real swarm agents don't emit presence | No true collaboration |
| **Cursor Following Behavior** | `follow_strength` from CursorBehavior not applied | All cursors same |
| **WebSocket Fan-out** | SSE is polling-ish; need true WebSocket for <100ms latency | Laggy feel |
| **Teaching Mode Overlays** | No explanatory callouts on nodes | Missing for new users |
| **Node Detail Panel** | Clicking a node shows nothing | Can't explore aspects |
| **Share URL** | No `kg self.conductor.share` implementation | Can't collaborate |
| **Mobile Touch** | Pan/zoom doesn't work on touch | No mobile access |

---

## Core Work (Priority Order)

### 5.1 Smooth Cursor Interpolation (Joy-Inducing)

**Current**: Cursors teleport to new positions.
**Target**: Cursors glide with spring physics, matching their `behavior` personality.

```typescript
// impl/claude/web/src/components/canvas/AnimatedCursor.tsx
import { motion, useSpring } from 'framer-motion';
import type { AgentCursor } from '@/hooks/usePresenceChannel';
import type { CursorBehavior } from '@/hooks/usePresenceChannel';

// Behavior determines animation feel
const BEHAVIOR_SPRING: Record<CursorBehavior, { damping: number; stiffness: number }> = {
  follower: { damping: 25, stiffness: 300 },    // Quick, responsive
  explorer: { damping: 15, stiffness: 150 },    // Looser, wandering
  assistant: { damping: 20, stiffness: 200 },   // Balanced
  autonomous: { damping: 10, stiffness: 100 },  // Slow, deliberate
};

interface AnimatedCursorProps {
  cursor: AgentCursor;
  targetPosition: { x: number; y: number };
  circadianTempo: number;  // 0.0-1.0, slows at night
}

export function AnimatedCursor({ cursor, targetPosition, circadianTempo }: AnimatedCursorProps) {
  const spring = BEHAVIOR_SPRING[cursor.behavior] || BEHAVIOR_SPRING.assistant;

  // Apply circadian tempo: slower at night
  const adjustedStiffness = spring.stiffness * (0.5 + circadianTempo * 0.5);

  const x = useSpring(targetPosition.x, { ...spring, stiffness: adjustedStiffness });
  const y = useSpring(targetPosition.y, { ...spring, stiffness: adjustedStiffness });

  return (
    <motion.div
      className="absolute pointer-events-none"
      style={{ x, y, transform: 'translate(-50%, -50%)' }}
    >
      {/* Cursor glyph based on state */}
      <div className={`cursor-${cursor.state} cursor-${cursor.behavior}`}>
        {getCursorEmoji(cursor.state)}
      </div>
      {/* Name label */}
      <div className="text-xs text-white/80 mt-1 whitespace-nowrap">
        {cursor.display_name}
      </div>
    </motion.div>
  );
}
```

### 5.2 Wire Swarm Agents to Presence (Composable)

**Current**: Only demo mode emits cursors.
**Target**: When `SwarmSpawner.spawn()` creates an agent, it automatically joins `PresenceChannel`.

This is already partially done! The `spawn()` method calls `channel.join(cursor)`. What's missing:
- Emitting the Phase 7 synergy event (`create_swarm_spawned_event`)
- Ensuring the SSE/WebSocket picks up new cursors immediately

```python
# services/conductor/swarm.py - Verify spawn() emits synergy event

from protocols.synergy import create_swarm_spawned_event, get_synergy_bus

async def spawn(...) -> AgentCursor | None:
    # ... existing code ...

    # Emit synergy event for global visibility (Phase 7 integration)
    event = create_swarm_spawned_event(
        agent_id=agent_id,
        task=task,
        behavior=decision.role.behavior.name,
        autonomy_level=decision.role.trust.value,
    )
    await get_synergy_bus().emit(event)

    # ConductorFlux will route this to subscribers (including WebSocket fan-out)
```

### 5.3 Node Detail Panel (Tasteful)

**Current**: Clicking node just selects it.
**Target**: Slide-in panel showing node aspects, recent invocations, and teaching info.

```typescript
// impl/claude/web/src/components/canvas/NodeDetailPanel.tsx
interface NodeDetailPanelProps {
  node: CanvasNode | null;
  onClose: () => void;
  onInvoke: (path: string, aspect: string) => void;
}

export function NodeDetailPanel({ node, onClose, onInvoke }: NodeDetailPanelProps) {
  const { enabled: teachingEnabled } = useTeachingMode();

  if (!node) return null;

  return (
    <motion.aside
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      className="w-80 bg-gray-900 border-l border-gray-800 p-4"
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="font-medium text-white">{node.label}</h2>
          <code className="text-xs text-blue-400">{node.path}</code>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white">×</button>
      </div>

      {/* Description */}
      {node.description && (
        <p className="text-sm text-gray-400 mb-4">{node.description}</p>
      )}

      {/* Aspects (fetch from registry or hardcode common ones) */}
      <div className="space-y-2">
        <h3 className="text-xs text-gray-500 uppercase">Aspects</h3>
        <div className="flex flex-wrap gap-1">
          {['manifest', 'witness', 'refine'].map((aspect) => (
            <button
              key={aspect}
              onClick={() => onInvoke(node.path, aspect)}
              className="px-2 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded"
            >
              {aspect}
            </button>
          ))}
        </div>
      </div>

      {/* Teaching callout */}
      {teachingEnabled && (
        <TeachingCallout category="conceptual" className="mt-4">
          This node is part of the <strong>{node.context}</strong> context.
          {getContextExplanation(node.context)}
        </TeachingCallout>
      )}
    </motion.aside>
  );
}

function getContextExplanation(context: string): string {
  const explanations: Record<string, string> = {
    world: 'Nodes in world.* represent external entities, environments, and tools.',
    self: 'Nodes in self.* represent the agent\'s internal state, memory, and capabilities.',
    concept: 'Nodes in concept.* represent abstract ideas, definitions, and platonic forms.',
    void: 'Nodes in void.* represent entropy, serendipity, and the accursed share.',
    time: 'Nodes in time.* represent temporal traces, forecasts, and schedules.',
  };
  return explanations[context] || '';
}
```

### 5.4 WebSocket Upgrade for Presence (Performance)

**Current**: SSE polling has ~500ms latency.
**Target**: WebSocket with <100ms latency, smooth cursor interpolation.

```python
# protocols/api/conductor_websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from services.conductor.flux import get_conductor_flux, ConductorEvent

CONDUCTOR_EVENT_TYPES = {
    "conductor.cursor.moved",
    "conductor.agent.joined",
    "conductor.agent.left",
    "conductor.swarm.activity",
    "conductor.file.changed",
}

async def conductor_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time conductor updates.

    Subscribes to ConductorFlux and pushes events to connected clients.
    """
    await websocket.accept()

    flux = get_conductor_flux()

    async def on_event(event: ConductorEvent):
        if event.event_type.value in CONDUCTOR_EVENT_TYPES:
            try:
                await websocket.send_json(event.to_dict())
            except:
                pass  # Client disconnected

    unsubscribe = flux.subscribe(on_event)

    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            # Handle focus broadcasts from client
            if data.startswith("focus:"):
                path = data[6:]
                # Could broadcast human focus to agents here
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe()
```

```typescript
// impl/claude/web/src/hooks/usePresenceWebSocket.ts
export function usePresenceWebSocket(sessionId: string) {
  const [cursors, setCursors] = useState<Map<string, AgentCursor>>(new Map());
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/conductor/${sessionId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'conductor.cursor.moved' || 
          data.type === 'conductor.agent.joined') {
        setCursors((prev) => {
          const next = new Map(prev);
          next.set(data.source_event.source_id, data.source_event.payload);
          return next;
        });
      }
    };

    wsRef.current = ws;
    return () => ws.close();
  }, [sessionId]);

  return { cursors: Array.from(cursors.values()) };
}
```

### 5.5 Share URL Implementation (sshx-Inspired)

**Current**: No share functionality.
**Target**: `kg self.conductor.share` generates a shareable URL.

```python
# protocols/agentese/contexts/self_conductor.py - Add share aspect

@aspect(
    category=AspectCategory.MUTATION,
    effects=[Effect.CREATES("share_session")],
    help="Generate a shareable URL for this session (sshx-inspired)",
)
async def share(
    self, observer: "Umwelt[Any, Any]", **kwargs: Any
) -> dict[str, Any]:
    """Generate a shareable URL for real-time collaboration."""
    import secrets
    from datetime import datetime, timedelta

    share_token = secrets.token_urlsafe(16)
    session_id = self._session_id or "unknown"

    # Get active agent names from presence channel
    presence = get_presence_channel()
    active_names = [c.display_name for c in presence.get_all()]

    expires_at = datetime.now() + timedelta(hours=24)

    return {
        "url": f"https://kgents.io/share/{share_token}",
        "session_id": session_id,
        "agents_active": active_names,
        "expires_at": expires_at.isoformat(),
        "share_token": share_token,
    }
```

---

## Test Strategy

| Type | Count | Focus |
|------|-------|-------|
| **Type I (Unit)** | 10 | AnimatedCursor spring calculations, NodeDetailPanel rendering |
| **Type II (Integration)** | 10 | WebSocket connection lifecycle, presence event flow |
| **Type III (Visual)** | 5 | Cursor interpolation feels right, circadian warmth visible |
| **Type IV (E2E)** | 5 | Full flow: spawn agent → cursor appears → follows human |

### Key E2E Test

```python
# services/conductor/_tests/test_canvas_e2e.py

@pytest.mark.asyncio
async def test_swarm_spawn_appears_on_canvas(reset_all):
    """
    E2E: Spawning a swarm agent creates a visible cursor on canvas.

    Flow:
    1. SwarmSpawner.spawn() creates agent
    2. Agent joins PresenceChannel
    3. SynergyEvent emitted (SWARM_SPAWNED)
    4. ConductorFlux routes to subscribers
    5. WebSocket pushes to frontend
    6. Cursor appears with correct behavior animation
    """
    spawner = SwarmSpawner(max_agents=5)

    # Spawn a researcher
    cursor = await spawner.spawn(
        "researcher-1",
        "Research the authentication patterns",
        context={"role_hint": "researcher"},
    )

    assert cursor is not None
    assert cursor.behavior == CursorBehavior.EXPLORER

    # Verify presence channel has cursor
    channel = get_presence_channel()
    all_cursors = channel.get_all()
    assert any(c.agent_id == "researcher-1" for c in all_cursors)

    # Verify synergy event was emitted
    # (Would need event capture fixture)
```

---

## Exit Condition

**When Phase 5 feels complete**:

1. ✅ Agent cursors glide smoothly (not teleport)
2. ✅ Cursor behavior visible (FOLLOWER is snappy, EXPLORER is loose)
3. ✅ Spawning a swarm agent → cursor appears on canvas
4. ✅ Clicking node → detail panel shows aspects
5. ✅ Teaching mode → explanatory overlays visible
6. ✅ `kg self.conductor.share` → shareable URL generated
7. ✅ Canvas feels inhabited, not empty

**The Companion Test**: When you're working alone on the canvas, does it feel like agents *could* appear at any moment? When they do appear, does their presence feel organic, not mechanical?

---

## Principle Alignment

| Principle | How Applied |
|-----------|-------------|
| **Tasteful** | Node detail panel is information-dense without overwhelming |
| **Joy-Inducing** | Smooth cursor interpolation, circadian warmth make it feel alive |
| **Composable** | Swarm spawn → synergy event → presence channel → WebSocket → UI |
| **Heterarchical** | Cursors have different behaviors (follower vs explorer) |
| **Generative** | Teaching mode explains the AGENTESE ontology |

---

## Reading Order

1. `impl/claude/web/src/hooks/usePresenceChannel.ts` — Understand current SSE flow
2. `impl/claude/web/src/components/canvas/CursorOverlay.tsx` — See current cursor rendering
3. `services/conductor/presence.py` — Backend presence source of truth
4. `services/conductor/swarm.py` — How agents are spawned
5. `services/conductor/flux.py` — ConductorFlux event routing (Phase 7)
6. `plans/cli-v7-implementation.md` Phase 5 section — Original spec

---

## Quick Start

```bash
# Start backend
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Start frontend
cd impl/claude/web && npm run dev

# Visit http://localhost:3000/canvas
# Click "Demo" to spawn simulated agent cursors
```

---

*"Your cursor and mine, dancing through the garden together."*

---

**Ready for Implementation**: This continuation picks up where the existing Canvas.tsx left off and delivers the polish needed for the companion test.
