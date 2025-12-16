# Gestalt Live Infrastructure: Phase 2 Continuation

**Plan**: `plans/gestalt-live-infrastructure.md`
**Current Phase**: Phase 2 - Real-Time Updates
**Date**: 2025-12-16
**Prerequisite**: Phase 1 Complete (52 tests passing)
**Status**: ✅ COMPLETE (73 total tests, 21 new streaming tests)

---

## Goal

Add real-time SSE streaming for topology updates and events, with animated entity states and efficient delta updates.

---

## Phase 1 Deliverables (Complete)

- [x] Kubernetes collector with Mock fallback
- [x] API endpoints (`/api/infra/*`)
- [x] GestaltLive.tsx page with 3D scene
- [x] Entity shapes by kind, health colors
- [x] Event feed panel, entity detail panel
- [x] Route at `/gestalt/live`
- [x] 52 tests passing

---

## Phase 2 Requirements

### 1. Topology Streaming (SSE)

**Backend: `protocols/api/infrastructure.py`**

Implement actual SSE streaming that sends incremental updates:

```python
# Current: Returns full topology each time
# Needed: Stream incremental TopologyUpdate events

class TopologyUpdateKind(str, Enum):
    FULL = "full"           # Initial full topology
    ENTITY_ADD = "add"      # New entity
    ENTITY_UPDATE = "update" # Entity changed (health, status, metrics)
    ENTITY_REMOVE = "remove" # Entity deleted
    CONNECTION_ADD = "conn_add"
    CONNECTION_REMOVE = "conn_remove"

@dataclass
class TopologyUpdate:
    kind: TopologyUpdateKind
    timestamp: datetime
    entity: InfraEntity | None = None
    connection: InfraConnection | None = None
    topology: InfraTopology | None = None  # Only for FULL
```

**Implementation checklist:**
- [ ] Add `TopologyUpdate` model to `agents/infra/models.py`
- [ ] Implement `collect_topology_diff()` in BaseCollector
- [ ] Track previous topology state for diffing
- [ ] Stream updates via `/api/infra/topology/stream`
- [ ] Send `FULL` on connection, then deltas

### 2. Event Streaming (SSE)

**Backend: Already scaffolded in `collectors/kubernetes.py`**

Connect mock event streaming to actual API:

```python
# In MockKubernetesCollector.stream_events():
# - Already generates random events
# - Need to connect to /api/infra/events/stream endpoint
# - Ensure proper SSE format: "data: {json}\n\n"
```

**Implementation checklist:**
- [ ] Wire `stream_events()` to SSE endpoint
- [ ] Add event filtering by severity/kind
- [ ] Handle client disconnect gracefully
- [ ] Add reconnection support (Last-Event-ID)

### 3. Frontend SSE Integration

**File: `pages/GestaltLive.tsx`**

Current state: Has basic EventSource setup but full reload on each message.

Needed changes:

```typescript
// 1. Apply topology updates incrementally
function applyTopologyUpdate(
  prev: InfraTopologyResponse | null,
  update: TopologyUpdate
): InfraTopologyResponse {
  if (update.kind === 'full') return update.topology!;
  if (!prev) return prev;

  switch (update.kind) {
    case 'add':
      return {
        ...prev,
        entities: [...prev.entities, update.entity!],
      };
    case 'update':
      return {
        ...prev,
        entities: prev.entities.map(e =>
          e.id === update.entity!.id ? update.entity! : e
        ),
      };
    case 'remove':
      return {
        ...prev,
        entities: prev.entities.filter(e => e.id !== update.entity!.id),
      };
    // Handle connection updates...
  }
}

// 2. Animate entity transitions
// - Fade in new entities (opacity 0→1)
// - Pulse updated entities
// - Fade out removed entities before deletion

// 3. Connection throttling
// - Debounce rapid updates (batch within 100ms window)
// - Skip intermediate states for fast-changing metrics
```

**Implementation checklist:**
- [ ] Implement `applyTopologyUpdate()` function
- [ ] Add entity transition animations (fade in/out)
- [ ] Add update pulse animation (brief glow)
- [ ] Debounce rapid updates
- [ ] Show "Connected" / "Reconnecting" status indicator

### 4. Entity State Animations

**File: `pages/GestaltLive.tsx` (InfraNode component)**

Current: Basic pulse for unhealthy, spin for pending.

Needed enhancements:

```typescript
// Transition states
interface EntityAnimationState {
  opacity: number;      // 0-1, for fade in/out
  scale: number;        // base scale
  pulseIntensity: number; // 0-1, for update flash
  isNew: boolean;       // just added
  isRemoving: boolean;  // marked for removal
}

// In useFrame():
// 1. Lerp opacity for smooth fade
// 2. Apply pulse decay (pulseIntensity *= 0.95)
// 3. Scale bounce on status change
// 4. Rotation speed based on activity level
```

**Implementation checklist:**
- [ ] Add EntityAnimationState tracking
- [ ] Implement fade-in animation (new entities)
- [ ] Implement update pulse (brief glow on change)
- [ ] Add removal animation (fade out, then remove from state)
- [ ] Smooth transitions for position changes (lerp)

### 5. Backend Topology Diff

**File: `agents/infra/collectors/base.py`**

Add efficient diffing:

```python
class BaseCollector:
    _previous_topology: InfraTopology | None = None

    async def collect_topology_diff(self) -> list[TopologyUpdate]:
        """Collect changes since last call."""
        current = await self.collect_topology()

        if self._previous_topology is None:
            self._previous_topology = current
            return [TopologyUpdate(kind="full", topology=current)]

        updates = self._diff_topologies(self._previous_topology, current)
        self._previous_topology = current
        return updates

    def _diff_topologies(
        self, old: InfraTopology, new: InfraTopology
    ) -> list[TopologyUpdate]:
        """Calculate diff between two topologies."""
        updates = []

        old_ids = {e.id for e in old.entities}
        new_ids = {e.id for e in new.entities}

        # Added entities
        for entity in new.entities:
            if entity.id not in old_ids:
                updates.append(TopologyUpdate(kind="add", entity=entity))

        # Removed entities
        for entity in old.entities:
            if entity.id not in new_ids:
                updates.append(TopologyUpdate(kind="remove", entity=entity))

        # Updated entities (changed health, status, metrics)
        for new_entity in new.entities:
            if new_entity.id in old_ids:
                old_entity = next(e for e in old.entities if e.id == new_entity.id)
                if self._entity_changed(old_entity, new_entity):
                    updates.append(TopologyUpdate(kind="update", entity=new_entity))

        # Similar for connections...
        return updates

    def _entity_changed(self, old: InfraEntity, new: InfraEntity) -> bool:
        """Check if entity has meaningful changes."""
        return (
            old.status != new.status
            or abs(old.health - new.health) > 0.05
            or abs(old.cpu_percent - new.cpu_percent) > 5
            or abs(old.memory_bytes - new.memory_bytes) > 1024 * 1024
        )
```

### 6. Tests for Streaming

**File: `agents/infra/_tests/test_streaming.py` (new)**

```python
class TestTopologyStreaming:
    """Tests for topology diff and streaming."""

    @pytest.mark.asyncio
    async def test_initial_diff_returns_full(self):
        """First diff should return full topology."""

    @pytest.mark.asyncio
    async def test_entity_add_detected(self):
        """New entities generate ADD updates."""

    @pytest.mark.asyncio
    async def test_entity_remove_detected(self):
        """Removed entities generate REMOVE updates."""

    @pytest.mark.asyncio
    async def test_entity_update_detected(self):
        """Changed entities generate UPDATE updates."""

    @pytest.mark.asyncio
    async def test_no_update_for_unchanged(self):
        """Unchanged entities don't generate updates."""

    @pytest.mark.asyncio
    async def test_small_changes_ignored(self):
        """Small metric changes below threshold are ignored."""


class TestEventStreaming:
    """Tests for event streaming."""

    @pytest.mark.asyncio
    async def test_stream_produces_events(self):
        """Event stream produces events."""

    @pytest.mark.asyncio
    async def test_event_severity_filtering(self):
        """Events can be filtered by severity."""
```

---

## Files to Create

```
impl/claude/agents/infra/
├── _tests/
│   └── test_streaming.py          # New: streaming tests

impl/claude/web/src/
├── hooks/
│   └── useInfraStream.ts          # New: SSE connection hook
├── utils/
│   └── topologyDiff.ts            # New: diff application
```

## Files to Modify

```
impl/claude/agents/infra/
├── models.py                      # Add TopologyUpdate, TopologyUpdateKind
├── collectors/base.py             # Add collect_topology_diff()
├── collectors/kubernetes.py       # Update MockKubernetesCollector

impl/claude/protocols/api/
├── infrastructure.py              # Wire actual streaming

impl/claude/web/src/
├── pages/GestaltLive.tsx          # SSE integration, animations
├── api/types.ts                   # Add TopologyUpdate types
```

---

## Implementation Order

1. **Add TopologyUpdate model** (backend)
   - `models.py`: Add `TopologyUpdateKind`, `TopologyUpdate`
   - 2 tests

2. **Implement diff algorithm** (backend)
   - `collectors/base.py`: Add `collect_topology_diff()`, `_diff_topologies()`
   - 6 tests

3. **Wire SSE endpoints** (backend)
   - `infrastructure.py`: Update `stream_topology()` to use diff
   - `infrastructure.py`: Update `stream_events()` to actually stream
   - 3 tests

4. **Add TopologyUpdate types** (frontend)
   - `api/types.ts`: Add `TopologyUpdate`, `TopologyUpdateKind`

5. **Create useInfraStream hook** (frontend)
   - Connection management
   - Reconnection with backoff
   - Status indicator state

6. **Apply incremental updates** (frontend)
   - `topologyDiff.ts`: `applyTopologyUpdate()` function
   - Handle add/update/remove

7. **Add entity animations** (frontend)
   - Fade in/out transitions
   - Update pulse effect
   - Position lerping

8. **Test end-to-end** (manual)
   - Start backend, frontend
   - Watch entities update in real-time
   - Verify smooth animations

---

## Exit Criteria for Phase 2

- [x] SSE streams topology updates (not full reload)
- [x] New entities fade in smoothly
- [x] Updated entities pulse briefly
- [x] Removed entities fade out before deletion
- [x] Event feed updates in real-time
- [x] Connection status indicator works
- [x] 15+ new tests passing (67+ total) → **21 new tests, 73 total**

---

## Testing Commands

```bash
# Run all infra tests
cd impl/claude && uv run pytest agents/infra/_tests/ -v

# Run just streaming tests
uv run pytest agents/infra/_tests/test_streaming.py -v

# Start backend for manual testing
uv run uvicorn protocols.api.app:create_app --factory --reload

# Start frontend
cd web && npm run dev
```

---

## API Testing (curl)

```bash
# Test topology endpoint
curl http://localhost:8000/api/infra/topology | jq

# Test SSE topology stream (watch for updates)
curl -N http://localhost:8000/api/infra/topology/stream

# Test SSE event stream
curl -N http://localhost:8000/api/infra/events/stream

# Test health endpoint
curl http://localhost:8000/api/infra/health | jq
```

---

## Notes from Phase 1

- MockKubernetesCollector generates realistic random data
- Health scoring already calculates grades
- Event streaming skeleton exists but not wired to SSE
- Position calculation uses force-directed layout

---

*"The infrastructure breathes. Now let's make it dance."*

---

## Phase 2 Implementation Summary (2025-12-16)

### Files Created

```
impl/claude/web/src/
├── hooks/useInfraStream.ts       # SSE hook with reconnection, debouncing
├── utils/topologyDiff.ts         # Incremental update application

impl/claude/agents/infra/_tests/
└── test_streaming.py             # 21 streaming tests
```

### Files Modified

```
impl/claude/web/src/
├── api/types.ts                  # Added TopologyUpdate types, EntityAnimationState
├── pages/GestaltLive.tsx         # Streaming integration, animations, status indicator

impl/claude/agents/infra/
└── models.py                     # (Already had TopologyUpdate from Phase 1)
└── collectors/base.py            # (Already had diff algorithm from Phase 1)
```

### Key Features Delivered

1. **SSE Streaming Integration**
   - `useInfraStream` hook manages topology and event streams
   - Automatic reconnection with exponential backoff
   - Debounced updates (100ms window) to prevent UI thrashing

2. **Incremental Updates**
   - `applyTopologyUpdate()` handles add/update/remove operations
   - `calculateAnimationChanges()` determines which entities need animation

3. **Entity Animations**
   - Fade in: New entities opacity 0→1
   - Pulse: Updated entities emit brief glow
   - Fade out: Removed entities opacity 1→0 before removal
   - Position lerping for smooth movement

4. **Connection Status Indicator**
   - Real-time status: Connected, Connecting, Reconnecting, Error, Offline
   - Visual indicator in header with color and icon

5. **Tests**
   - 21 new streaming tests covering:
     - TopologyUpdate model
     - Diff algorithm correctness
     - Change detection thresholds
     - Streaming behavior

### Test Results

```
73 passed (21 new + 52 existing)
```

### Next Phase

Phase 3 can focus on:
- Entity filtering UI (by kind, namespace, health)
- Enhanced connection visualization (animated particles for traffic)
- Historical playback (scrub through topology changes)
