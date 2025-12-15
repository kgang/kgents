---
path: agent-town/builders-workshop-chunk8
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
  - agent-town/builders-workshop-chunk9
session_notes: |
  CONTINUATION from Chunk 7 (WorkshopFlux complete, 65 tests).
  Now implementing web projection - React components for workshop visualization.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: pending  # Town.tsx, Mesa, SSE patterns
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.0
  remaining: 0.12
---

# Builder's Workshop: Chunk 8 - Web Projection

> *"The workshop made visible. Builders as personas, not dots. Tasks as journeys, not checkboxes."*

**AGENTESE Context**: `world.workshop.manifest`, `world.builder.*.manifest`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**:
- `impl/claude/web/src/pages/Town.tsx` (Town page structure - primary pattern)
- `impl/claude/web/src/components/town/Mesa.tsx` (PixiJS isometric canvas)
- `impl/claude/web/src/components/town/CitizenPanel.tsx` (Sidebar detail panel)
- `impl/claude/web/src/hooks/useTownStream.ts` (SSE event streaming)
- `impl/claude/agents/town/workshop.py` (WorkshopFlux, WorkshopEvent)
- `impl/claude/protocols/api/app.py` (FastAPI endpoints)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunks 4-7)

**Completed**:
- Chunk 4: `BUILDER_POLYNOMIAL` with 6 phases (71 tests)
- Chunk 5: 5 Builder classes (Sage, Spark, Steady, Scout, Sync) extending Citizen (132 tests)
- Chunk 6: `WorkshopEnvironment` with task routing, handoffs, events (93 tests)
- Chunk 7: `WorkshopFlux` streaming execution layer (65 tests)

**Backend Ready**:
```python
# Already implemented in workshop.py
WorkshopFlux.start(task) → WorkshopPlan
WorkshopFlux.step() → AsyncIterator[WorkshopEvent]
WorkshopFlux.run() → AsyncIterator[WorkshopEvent]
WorkshopFlux.perturb(action) → WorkshopEvent
WorkshopFlux.get_status() → dict
WorkshopFlux.get_metrics() → WorkshopMetrics

# Event types
WorkshopEventType.TASK_ASSIGNED
WorkshopEventType.PLAN_CREATED
WorkshopEventType.PHASE_STARTED
WorkshopEventType.PHASE_COMPLETED
WorkshopEventType.ARTIFACT_PRODUCED
WorkshopEventType.HANDOFF
WorkshopEventType.TASK_COMPLETED
```

**Total backend tests**: 361 (71 + 132 + 93 + 65)

---

## This Session: Web Projection (Chunk 8)

### Goal

Create React components for visualizing and interacting with the Builder's Workshop. Users should see builders as distinct personas, watch tasks progress through phases, and interact via WHISPER/INHABIT.

### Core Concepts

| Concept | Description | Implementation |
|---------|-------------|----------------|
| **Workshop Page** | Main page for workshop view | `pages/Workshop.tsx` |
| **WorkshopMesa** | Isometric canvas showing builders at their stations | `components/workshop/WorkshopMesa.tsx` |
| **BuilderPanel** | Sidebar showing builder details | `components/workshop/BuilderPanel.tsx` |
| **TaskProgress** | Visual task progress through phases | `components/workshop/TaskProgress.tsx` |
| **ArtifactFeed** | Stream of produced artifacts | `components/workshop/ArtifactFeed.tsx` |
| **useWorkshopStream** | SSE hook for workshop events | `hooks/useWorkshopStream.ts` |

### Research Questions

1. How does `Town.tsx` structure its layout? (header, mesa, sidebar, feed)
2. How does `Mesa.tsx` render citizens? (PixiJS, positions, colors)
3. How does `useTownStream` handle SSE? (EventSource, reconnection)
4. What API endpoints exist for workshops? (may need to add)
5. How should builders be positioned? (stations vs grid)

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `Workshop.tsx` page | `web/src/pages/` | 5+ |
| `WorkshopMesa.tsx` | `web/src/components/workshop/` | 10+ |
| `BuilderPanel.tsx` | `web/src/components/workshop/` | 5+ |
| `TaskProgress.tsx` | `web/src/components/workshop/` | 5+ |
| `ArtifactFeed.tsx` | `web/src/components/workshop/` | 5+ |
| `useWorkshopStream.ts` | `web/src/hooks/` | 5+ |
| API endpoints | `protocols/api/workshop.py` | 10+ |
| TypeScript types | `web/src/api/types.ts` | - |

**Total target: 45+ new tests** (frontend + backend)

---

## Visual Design

### Workshop Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Workshop: "Add Dark Mode"    Day 1    DESIGNING    ▶️ Pause  1x   │
├─────────────────────────────────────────────────────────────────────┤
│                                                    │                │
│  ┌─────────────────────────────────────────┐      │  BuilderPanel  │
│  │                                         │      │                │
│  │         WorkshopMesa (PixiJS)           │      │  [Sage] ◀      │
│  │                                         │      │  Archetype:    │
│  │    Scout      Sage        Spark         │      │  Architect     │
│  │      ○━━━━━━━━●━━━━━━━━━━○             │      │  Phase:        │
│  │    (done)   (active)   (waiting)        │      │  DESIGNING     │
│  │                                         │      │  Specialty:    │
│  │              Steady      Sync           │      │  Patterns      │
│  │                ○          ○             │      │                │
│  │             (waiting)  (waiting)        │      │  [WHISPER]     │
│  │                                         │      │  [INHABIT]     │
│  └─────────────────────────────────────────┘      │                │
│                                                    ├────────────────┤
│  TaskProgress                                      │  ArtifactFeed  │
│  ═══════●════════════════════════════════         │                │
│  EXPLORING  DESIGNING  PROTOTYPING  ...           │  📄 research   │
│                                                    │  📄 design_v1  │
└─────────────────────────────────────────────────────────────────────┘
```

### Builder Station Layout (in WorkshopMesa)

Unlike the Town mesa which uses regions, the Workshop uses **stations** arranged in a pipeline:

```
                    ┌─────────┐
                    │  Scout  │  EXPLORING
                    │    ●    │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Sage   │  DESIGNING
                    │    ●    │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Spark  │  PROTOTYPING
                    │    ○    │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Steady  │  REFINING
                    │    ○    │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Sync   │  INTEGRATING
                    │    ○    │
                    └─────────┘
```

### Builder Colors & Icons

| Builder | Color | Icon | Active State |
|---------|-------|------|--------------|
| Scout | `#22c55e` (green) | 🔍 | Pulsing ring |
| Sage | `#8b5cf6` (purple) | 📐 | Rotating glow |
| Spark | `#f59e0b` (amber) | ⚡ | Spark particles |
| Steady | `#3b82f6` (blue) | 🔧 | Steady pulse |
| Sync | `#ec4899` (pink) | 🔗 | Connected lines |

---

## API Endpoints Needed

### New Endpoints (add to `protocols/api/app.py` or `workshop.py`)

```python
# GET /workshop
# Create or get default workshop
@router.get("/workshop")
async def get_workshop() -> WorkshopResponse:
    """Get or create the default workshop."""
    ...

# POST /workshop/task
# Assign a new task
@router.post("/workshop/task")
async def assign_task(request: AssignTaskRequest) -> WorkshopPlanResponse:
    """Assign a task to the workshop."""
    ...

# GET /workshop/stream
# SSE stream of workshop events
@router.get("/workshop/stream")
async def workshop_stream() -> EventSourceResponse:
    """Stream workshop events via SSE."""
    ...

# GET /workshop/status
# Current workshop status
@router.get("/workshop/status")
async def workshop_status() -> WorkshopStatusResponse:
    """Get current workshop status including metrics."""
    ...

# GET /workshop/builders
# List all builders
@router.get("/workshop/builders")
async def list_builders() -> BuildersResponse:
    """List all builders with their current state."""
    ...

# GET /workshop/builder/{archetype}
# Get builder detail
@router.get("/workshop/builder/{archetype}")
async def get_builder(archetype: str, lod: int = 1) -> BuilderDetailResponse:
    """Get builder details at specified LOD."""
    ...

# POST /workshop/builder/{archetype}/whisper
# Send whisper to builder
@router.post("/workshop/builder/{archetype}/whisper")
async def whisper_builder(archetype: str, request: WhisperRequest) -> WhisperResponse:
    """Send a whisper to a specific builder."""
    ...

# POST /workshop/perturb
# Inject perturbation
@router.post("/workshop/perturb")
async def perturb(request: PerturbRequest) -> WorkshopEventResponse:
    """Inject a perturbation into the workshop flux."""
    ...
```

### Response Types

```python
@dataclass
class WorkshopResponse:
    id: str
    phase: str
    active_task: dict | None
    builders: list[BuilderSummary]
    metrics: dict

@dataclass
class BuilderSummary:
    archetype: str
    name: str
    phase: str  # BuilderPhase
    is_active: bool
    is_in_specialty: bool

@dataclass
class AssignTaskRequest:
    description: str
    priority: int = 1

@dataclass
class PerturbRequest:
    action: str  # "advance", "handoff", "complete", "inject_artifact"
    builder: str | None = None
    artifact: Any = None
```

---

## TypeScript Types Needed

Add to `web/src/api/types.ts`:

```typescript
// =============================================================================
// Workshop
// =============================================================================

export type WorkshopPhase =
  | 'IDLE'
  | 'EXPLORING'
  | 'DESIGNING'
  | 'PROTOTYPING'
  | 'REFINING'
  | 'INTEGRATING'
  | 'COMPLETE';

export type BuilderArchetype = 'Scout' | 'Sage' | 'Spark' | 'Steady' | 'Sync';

export type BuilderPhase =
  | 'IDLE'
  | 'EXPLORING'
  | 'DESIGNING'
  | 'PROTOTYPING'
  | 'REFINING'
  | 'INTEGRATING';

export interface BuilderSummary {
  archetype: BuilderArchetype;
  name: string;
  phase: BuilderPhase;
  is_active: boolean;
  is_in_specialty: boolean;
}

export interface WorkshopTask {
  id: string;
  description: string;
  priority: number;
  created_at: string;
}

export interface WorkshopArtifact {
  id: string;
  task_id: string;
  builder: string;
  phase: WorkshopPhase;
  content: unknown;
  created_at: string;
}

export interface WorkshopMetrics {
  total_steps: number;
  total_events: number;
  total_tokens: number;
  dialogue_tokens: number;
  artifacts_produced: number;
  phases_completed: number;
  handoffs: number;
  perturbations: number;
  duration_seconds: number;
}

export interface WorkshopStatus {
  id: string;
  phase: WorkshopPhase;
  active_task: WorkshopTask | null;
  builders: BuilderSummary[];
  artifacts: WorkshopArtifact[];
  metrics: WorkshopMetrics;
  is_running: boolean;
}

export interface WorkshopEvent {
  type: string;
  builder: string | null;
  phase: WorkshopPhase;
  message: string;
  artifact: unknown | null;
  timestamp: string;
  metadata: {
    dialogue?: string;
    perturbation?: boolean;
  };
}

export interface WorkshopPlan {
  task: WorkshopTask;
  assignments: Record<string, string[]>;
  estimated_phases: WorkshopPhase[];
  lead_builder: string;
}
```

---

## Component Specifications

### 1. Workshop.tsx (Page)

```typescript
// Similar structure to Town.tsx but for workshop
export default function Workshop() {
  // State
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [workshop, setWorkshop] = useState<WorkshopStatus | null>(null);
  const [selectedBuilder, setSelectedBuilder] = useState<string | null>(null);
  const [taskInput, setTaskInput] = useState('');

  // Hooks
  const { events, isConnected } = useWorkshopStream({ autoConnect: true });

  // Layout: Header, WorkshopMesa, BuilderPanel, TaskProgress, ArtifactFeed
}
```

### 2. WorkshopMesa.tsx (Canvas)

```typescript
// PixiJS canvas showing builders at stations
interface WorkshopMesaProps {
  builders: BuilderSummary[];
  activeBuilder: string | null;
  selectedBuilder: string | null;
  onSelectBuilder: (archetype: string | null) => void;
  width?: number;
  height?: number;
}

// Features:
// - Vertical pipeline layout (not grid)
// - Station boxes for each builder
// - Flow lines between stations
// - Active builder highlighted with animation
// - Artifact icons flowing between stations
// - Click to select builder
```

### 3. BuilderPanel.tsx (Sidebar)

```typescript
// Detail panel for selected builder
interface BuilderPanelProps {
  builder: BuilderSummary | null;
  onWhisper: (message: string) => void;
  onInhabit: () => void;
}

// Features:
// - Builder avatar/icon
// - Current phase indicator
// - Specialty badge
// - Eigenvector radar chart (reuse from CitizenPanel)
// - Recent dialogue
// - WHISPER input
// - INHABIT button (respects tier)
```

### 4. TaskProgress.tsx (Progress Bar)

```typescript
// Horizontal phase progress
interface TaskProgressProps {
  currentPhase: WorkshopPhase;
  completedPhases: WorkshopPhase[];
  task: WorkshopTask | null;
}

// Features:
// - 5 phase markers
// - Current phase highlighted
// - Completed phases filled
// - Task description
// - Time elapsed
```

### 5. ArtifactFeed.tsx (Event Log)

```typescript
// Scrolling list of artifacts
interface ArtifactFeedProps {
  artifacts: WorkshopArtifact[];
  events: WorkshopEvent[];
  maxItems?: number;
}

// Features:
// - Artifact cards with builder attribution
// - Event messages with timestamps
// - Phase badges
// - Expandable content preview
```

### 6. useWorkshopStream.ts (Hook)

```typescript
// SSE streaming hook
interface UseWorkshopStreamOptions {
  workshopId?: string;
  autoConnect?: boolean;
  onEvent?: (event: WorkshopEvent) => void;
}

interface UseWorkshopStreamResult {
  events: WorkshopEvent[];
  artifacts: WorkshopArtifact[];
  isConnected: boolean;
  error: Error | null;
  connect: () => void;
  disconnect: () => void;
}
```

---

## Zustand Store

Add to `stores/workshopStore.ts`:

```typescript
interface WorkshopState {
  // Workshop data
  workshop: WorkshopStatus | null;
  builders: BuilderSummary[];
  events: WorkshopEvent[];
  artifacts: WorkshopArtifact[];

  // UI state
  selectedBuilder: string | null;
  isRunning: boolean;

  // Actions
  setWorkshop: (workshop: WorkshopStatus) => void;
  setBuilders: (builders: BuilderSummary[]) => void;
  addEvent: (event: WorkshopEvent) => void;
  addArtifact: (artifact: WorkshopArtifact) => void;
  selectBuilder: (archetype: string | null) => void;
  setRunning: (running: boolean) => void;
  reset: () => void;
}
```

---

## Test Categories

1. **Workshop page tests**: Loading, error, render states
2. **WorkshopMesa tests**: Builder positions, selection, animations
3. **BuilderPanel tests**: Display, whisper, inhabit buttons
4. **TaskProgress tests**: Phase rendering, progress calculation
5. **ArtifactFeed tests**: Scrolling, artifact cards
6. **useWorkshopStream tests**: SSE connection, event handling
7. **API endpoint tests**: Request/response validation
8. **Integration tests**: Full page with mocked API

---

## Exit Criteria

- [ ] `Workshop.tsx` page renders with header, mesa, sidebar
- [ ] `WorkshopMesa.tsx` shows builders in pipeline layout
- [ ] `BuilderPanel.tsx` shows selected builder details
- [ ] `TaskProgress.tsx` shows phase progress
- [ ] `ArtifactFeed.tsx` streams artifacts and events
- [ ] `useWorkshopStream.ts` handles SSE connection
- [ ] API endpoints for workshop operations
- [ ] TypeScript types for workshop data
- [ ] Zustand store for workshop state
- [ ] 45+ tests passing (frontend + backend)
- [ ] Route `/workshop` accessible from nav
- [ ] Builder selection works
- [ ] WHISPER sends message (if backend supports)

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand existing patterns before implementing workshop web UI.

### Actions
1. Read `web/src/pages/Town.tsx` - page structure, loading states
2. Read `web/src/components/town/Mesa.tsx` - PixiJS rendering
3. Read `web/src/hooks/useTownStream.ts` - SSE patterns
4. Read `web/src/stores/townStore.ts` - Zustand patterns
5. Check existing API endpoints in `protocols/api/app.py`
6. Verify CORS and auth patterns

### Exit Criteria
- [ ] Town.tsx structure understood
- [ ] Mesa rendering pattern clear
- [ ] SSE hook pattern understood
- [ ] Store pattern understood
- [ ] API gaps identified

### Minimum Artifact
Design notes in session_notes.

### Continuation
On completion: `[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design component APIs and TypeScript types.

### Actions
1. Define TypeScript types in `api/types.ts`
2. Design component interfaces
3. Plan Zustand store structure
4. Define API endpoint signatures
5. Create file stubs

### Exit Criteria
- [ ] All TypeScript types defined
- [ ] Component interfaces designed
- [ ] Store structure planned
- [ ] API endpoints designed

### Minimum Artifact
TypeScript types added.

### Continuation
On completion: `[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Implement all workshop web components.

### Actions
1. Add workshop API endpoints to backend
2. Create `workshopStore.ts`
3. Create `useWorkshopStream.ts` hook
4. Create `Workshop.tsx` page
5. Create `WorkshopMesa.tsx` with PixiJS
6. Create `BuilderPanel.tsx`
7. Create `TaskProgress.tsx`
8. Create `ArtifactFeed.tsx`
9. Add route to `App.tsx`
10. Add nav link

### Exit Criteria
- [ ] All code written
- [ ] TypeScript compiles
- [ ] Route works
- [ ] Basic rendering works

### Minimum Artifact
Working Workshop page that loads.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Test all workshop web components.

### Actions
1. Add API endpoint tests
2. Add component unit tests
3. Add hook tests
4. Add integration tests
5. Manual testing in browser

### Exit Criteria
- [ ] 45+ tests passing
- [ ] All components tested
- [ ] SSE streaming works
- [ ] Selection works

### Minimum Artifact
Passing test suite.

### Continuation
On completion: `[REFLECT]`

</details>

---

## Phase: REFLECT

<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Document learnings and prepare for Chunk 9.

### Actions
1. Update `builders-workshop.md` progress
2. Add learnings to `plans/meta.md`
3. Update chunk8 status to complete
4. Identify Chunk 9 scope (public metrics dashboard)

### Exit Criteria
- [ ] Parent plan updated
- [ ] Learnings captured
- [ ] Ready for Chunk 9

### Minimum Artifact
Updated session_notes.

### Continuation
`[COMPLETE]` - Chunk 8 done.

</details>

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `web/src/pages/Town.tsx` | ~270 | Reference page structure |
| `web/src/components/town/Mesa.tsx` | ~310 | Reference PixiJS canvas |
| `web/src/components/town/CitizenPanel.tsx` | ~??? | Reference sidebar panel |
| `web/src/hooks/useTownStream.ts` | ~??? | Reference SSE hook |
| `web/src/stores/townStore.ts` | ~??? | Reference Zustand store |
| `web/src/api/types.ts` | ~260 | Add workshop types here |
| `protocols/api/app.py` | ~??? | Add workshop endpoints here |
| `agents/town/workshop.py` | ~1500 | Backend workshop implementation |

### Import Pattern (Frontend)

```typescript
// Components
import { WorkshopMesa } from '@/components/workshop/WorkshopMesa';
import { BuilderPanel } from '@/components/workshop/BuilderPanel';
import { TaskProgress } from '@/components/workshop/TaskProgress';
import { ArtifactFeed } from '@/components/workshop/ArtifactFeed';

// Hooks
import { useWorkshopStream } from '@/hooks/useWorkshopStream';

// Store
import { useWorkshopStore } from '@/stores/workshopStore';

// Types
import type { WorkshopStatus, BuilderSummary, WorkshopEvent } from '@/api/types';
```

### Import Pattern (Backend)

```python
from agents.town.workshop import (
    WorkshopEnvironment,
    WorkshopFlux,
    WorkshopEvent,
    WorkshopEventType,
    WorkshopPhase,
    WorkshopMetrics,
    create_workshop,
)
from agents.town.builders import (
    Builder,
    BuilderPhase,
    create_sage,
    create_scout,
    create_spark,
    create_steady,
    create_sync,
)
```

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | touched | This document |
| RESEARCH | pending | - |
| DEVELOP | pending | - |
| STRATEGIZE | skipped | - |
| CROSS-SYNERGIZE | pending | - |
| IMPLEMENT | pending | - |
| QA | pending | - |
| TEST | pending | - |
| EDUCATE | skipped | - |
| MEASURE | deferred | - |
| REFLECT | pending | - |

---

## Chunk 9 Preview

After Web Projection, Chunk 9 will cover:
1. **Public Metrics Dashboard**: Display workshop metrics
2. **Task History**: View completed tasks and artifacts
3. **Replay Scrubber**: Replay task execution (if time permits)

---

*"The workshop is not observed—it is inhabited. Each builder has presence, not just position."*
