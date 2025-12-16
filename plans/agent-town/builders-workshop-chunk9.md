---
path: agent-town/builders-workshop-chunk9
status: fruiting
progress: 85
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
session_notes: |
  CONTINUATION from Chunk 8 (Web Projection complete, 124 tests).

  SESSION 2025-12-15:
  - Backend: WorkshopHistoryStore with pagination, filtering, aggregate metrics
  - Backend: 6 new API endpoints (history, metrics/aggregate, metrics/builder, metrics/flow)
  - Backend: Auto-recording to history on task complete/interrupt
  - Frontend: Extended workshopStore with history, metrics, replay state
  - Frontend: MetricsDashboard.tsx - sparklines, builder bars, flow viz
  - Frontend: TaskHistory.tsx - pagination, filtering, builder sequence
  - Frontend: TaskReplay.tsx - scrubber, playback controls, event log
  - Tests: 14 new backend tests for history module (all passing)
  - TypeScript compiles clean
phase_ledger:
  PLAN: touched
  RESEARCH: done
  DEVELOP: done
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: done  # Used Dashboard.tsx patterns, reactive primitives
  IMPLEMENT: done
  QA: done
  TEST: done
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: pending
entropy:
  planned: 0.12
  spent: 0.10
  remaining: 0.02
---

# Builder's Workshop: Chunk 9 - Metrics & History

> *"Every task leaves a trace. Every builder accumulates wisdom. The dashboard reveals the workshop's memory."*

**AGENTESE Context**: `world.workshop.witness`, `world.workshop.metrics`, `time.workshop.*`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**:
- `impl/claude/web/src/pages/Workshop.tsx` (Workshop page - Chunk 8)
- `impl/claude/web/src/pages/Dashboard.tsx` (Existing dashboard patterns)
- `impl/claude/web/src/components/town/Mesa.tsx` (Visualization patterns)
- `impl/claude/agents/town/workshop.py` (WorkshopMetrics, task history)
- `impl/claude/protocols/api/workshop.py` (Existing workshop API)
- `impl/claude/agents/i/reactive/primitives/` (Sparkline, Bar for metrics)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunks 4-8)

**Completed**:
- Chunk 4: `BUILDER_POLYNOMIAL` with 6 phases (71 tests)
- Chunk 5: 5 Builder classes extending Citizen (132 tests)
- Chunk 6: `WorkshopEnvironment` with task routing (93 tests)
- Chunk 7: `WorkshopFlux` streaming execution (65 tests)
- Chunk 8: Web Projection - Workshop.tsx, WorkshopMesa, BuilderPanel (124 tests)

**Total backend + frontend tests**: 485

**Web Infrastructure Ready**:
```typescript
// From Chunk 8
Workshop.tsx          // Main page
WorkshopMesa.tsx      // PixiJS canvas
BuilderPanel.tsx      // Builder detail sidebar
TaskProgress.tsx      // Phase progress bar
ArtifactFeed.tsx      // Event stream
useWorkshopStream.ts  // SSE hook
workshopStore.ts      // Zustand store

// API Endpoints
GET  /v1/workshop
POST /v1/workshop/task
GET  /v1/workshop/stream
GET  /v1/workshop/status
GET  /v1/workshop/builders
GET  /v1/workshop/builder/{archetype}
POST /v1/workshop/perturb
POST /v1/workshop/reset
GET  /v1/workshop/artifacts
```

---

## This Session: Metrics & History (Chunk 9)

### Goal

Add observability to the workshop: metrics dashboard showing builder performance, task history with replay capability, and aggregate statistics. Users should understand workshop patterns over time.

### Core Concepts

| Concept | Description | Implementation |
|---------|-------------|----------------|
| **MetricsDashboard** | Workshop-wide metrics visualization | `components/workshop/MetricsDashboard.tsx` |
| **BuilderStats** | Per-builder performance stats | `components/workshop/BuilderStats.tsx` |
| **TaskHistory** | List of completed tasks | `components/workshop/TaskHistory.tsx` |
| **TaskReplay** | Scrub through task execution | `components/workshop/TaskReplay.tsx` |
| **AggregateMetrics** | Cumulative workshop statistics | Backend aggregate endpoints |

### Research Questions

1. What metrics does `WorkshopMetrics` already track?
2. How does the existing `Dashboard.tsx` visualize data?
3. Can we reuse reactive primitives (Sparkline, Bar) for metrics?
4. How should task history be persisted? (in-memory vs store)
5. What's the replay UX? (scrubber slider, step buttons, playback speed)

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `MetricsDashboard.tsx` | `web/src/components/workshop/` | 10+ |
| `BuilderStats.tsx` | `web/src/components/workshop/` | 8+ |
| `TaskHistory.tsx` | `web/src/components/workshop/` | 8+ |
| `TaskReplay.tsx` | `web/src/components/workshop/` | 10+ |
| History API endpoints | `protocols/api/workshop.py` | 10+ |
| Aggregate metrics API | `protocols/api/workshop.py` | 6+ |
| Store extensions | `stores/workshopStore.ts` | 8+ |

**Total target: 60+ new tests**

---

## Visual Design

### MetricsDashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Workshop Metrics                                    [24h] [7d] [All]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Tasks        │  │ Artifacts    │  │ Tokens       │               │
│  │     42       │  │    156       │  │   12.4k      │               │
│  │ ▁▂▃▅▆▇█▆▅▃▂ │  │ ▁▂▃▄▅▆▇▆▅▄▃ │  │ ▁▁▂▃▅▇▆▄▃▂▁ │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  Builder Performance                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Scout   ████████████████░░░░░░░░░░  68%  │  12 tasks  │  2.1s   ││
│  │ Sage    ██████████████████████░░░░  82%  │  15 tasks  │  3.4s   ││
│  │ Spark   ████████████░░░░░░░░░░░░░░  45%  │   8 tasks  │  1.8s   ││
│  │ Steady  █████████████████████████░  95%  │  18 tasks  │  4.2s   ││
│  │ Sync    ██████████████████░░░░░░░░  72%  │  14 tasks  │  2.9s   ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Handoff Flow                                                        │
│  Scout ──(23)──▶ Sage ──(18)──▶ Spark ──(15)──▶ Steady ──(12)──▶ Sync│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### TaskHistory Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Task History                                    [Filter] [Search]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ ✓ "Add dark mode toggle"                         Dec 15, 2:34pm ││
│  │   Scout → Sage → Spark → Steady → Sync           Duration: 45s  ││
│  │   Artifacts: 5  │  Tokens: 1,234  │  Handoffs: 4                ││
│  │   [View Details] [Replay]                                       ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ ✓ "Fix login button styling"                     Dec 15, 2:12pm ││
│  │   Scout → Sage → Spark                           Duration: 28s  ││
│  │   Artifacts: 3  │  Tokens: 892   │  Handoffs: 2                 ││
│  │   [View Details] [Replay]                                       ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ ⚠ "Implement OAuth2"                             Dec 15, 1:45pm ││
│  │   Scout → Sage → [INTERRUPTED]                   Duration: 12s  ││
│  │   Artifacts: 1  │  Tokens: 456   │  Handoffs: 1                 ││
│  │   [View Details] [Resume]                                       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Page 1 of 3                                      [◀] [1] [2] [3] [▶]│
└─────────────────────────────────────────────────────────────────────┘
```

### TaskReplay Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Replay: "Add dark mode toggle"                              [Close]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────┐  ┌────────────────────┐│
│  │                                         │  │  Event Log         ││
│  │         [WorkshopMesa replay]           │  │                    ││
│  │                                         │  │  00:12 Scout start ││
│  │    Scout      Sage        Spark         │  │  00:15 Research    ││
│  │      ●━━━━━━━━○━━━━━━━━━━○             │  │  00:18 Handoff     ││
│  │    (done)   (replay)   (waiting)        │  │  00:22 Sage start  ││
│  │                                         │  │  00:28 Design v1   ││
│  │              Steady      Sync           │  │  00:35 Handoff     ││
│  │                ○          ○             │  │  ...               ││
│  │                                         │  │                    ││
│  └─────────────────────────────────────────┘  └────────────────────┘│
│                                                                      │
│  Timeline                                                            │
│  [|◀] [◀] [▶] [▶|]    [0.5x] [1x] [2x] [4x]                        │
│  ═══════●═══════════════════════════════════════════════════════════│
│  00:22 / 00:45                                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Needed

### New Endpoints

```python
# GET /v1/workshop/history
# List completed tasks with pagination
@router.get("/history")
async def get_task_history(
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,  # completed, interrupted, all
) -> TaskHistoryResponse:
    """Get paginated task history."""
    ...

# GET /v1/workshop/history/{task_id}
# Get detailed task record
@router.get("/history/{task_id}")
async def get_task_detail(task_id: str) -> TaskDetailResponse:
    """Get detailed task execution record including all events."""
    ...

# GET /v1/workshop/history/{task_id}/events
# Get task events for replay
@router.get("/history/{task_id}/events")
async def get_task_events(task_id: str) -> TaskEventsResponse:
    """Get all events for task replay."""
    ...

# GET /v1/workshop/metrics/aggregate
# Get aggregate metrics
@router.get("/metrics/aggregate")
async def get_aggregate_metrics(
    period: str = "24h",  # 24h, 7d, 30d, all
) -> AggregateMetricsResponse:
    """Get aggregate workshop metrics for period."""
    ...

# GET /v1/workshop/metrics/builder/{archetype}
# Get builder-specific metrics
@router.get("/metrics/builder/{archetype}")
async def get_builder_metrics(
    archetype: str,
    period: str = "24h",
) -> BuilderMetricsResponse:
    """Get metrics for specific builder."""
    ...

# GET /v1/workshop/metrics/flow
# Get handoff flow metrics
@router.get("/metrics/flow")
async def get_flow_metrics() -> FlowMetricsResponse:
    """Get handoff flow between builders."""
    ...
```

### Response Types

```python
@dataclass
class TaskHistoryItem:
    id: str
    description: str
    status: str  # completed, interrupted
    lead_builder: str
    builder_sequence: list[str]
    artifacts_count: int
    tokens_used: int
    handoffs: int
    duration_seconds: float
    created_at: datetime
    completed_at: datetime | None

@dataclass
class TaskHistoryResponse:
    tasks: list[TaskHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

@dataclass
class TaskDetailResponse:
    task: TaskHistoryItem
    artifacts: list[WorkshopArtifact]
    events: list[WorkshopEvent]
    builder_contributions: dict[str, BuilderContribution]

@dataclass
class BuilderContribution:
    archetype: str
    phases_worked: list[str]
    artifacts_produced: int
    tokens_used: int
    duration_seconds: float

@dataclass
class AggregateMetricsResponse:
    period: str
    total_tasks: int
    completed_tasks: int
    interrupted_tasks: int
    total_artifacts: int
    total_tokens: int
    total_handoffs: int
    avg_duration_seconds: float
    tasks_by_day: list[DayMetric]
    artifacts_by_day: list[DayMetric]
    tokens_by_day: list[DayMetric]

@dataclass
class DayMetric:
    date: str
    value: int

@dataclass
class BuilderMetricsResponse:
    archetype: str
    period: str
    tasks_participated: int
    tasks_led: int
    artifacts_produced: int
    tokens_used: int
    avg_duration_seconds: float
    specialty_efficiency: float  # % time in specialty phase
    handoffs_initiated: int
    handoffs_received: int

@dataclass
class FlowMetricsResponse:
    flows: list[HandoffFlow]
    total_handoffs: int

@dataclass
class HandoffFlow:
    from_builder: str
    to_builder: str
    count: int
    avg_artifact_quality: float  # Future: quality scoring
```

---

## TypeScript Types Needed

Add to `web/src/api/types.ts`:

```typescript
// =============================================================================
// Workshop History & Metrics
// =============================================================================

export interface TaskHistoryItem {
  id: string;
  description: string;
  status: 'completed' | 'interrupted';
  lead_builder: string;
  builder_sequence: string[];
  artifacts_count: number;
  tokens_used: number;
  handoffs: number;
  duration_seconds: number;
  created_at: string;
  completed_at: string | null;
}

export interface TaskHistoryResponse {
  tasks: TaskHistoryItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface BuilderContribution {
  archetype: string;
  phases_worked: string[];
  artifacts_produced: number;
  tokens_used: number;
  duration_seconds: number;
}

export interface TaskDetailResponse {
  task: TaskHistoryItem;
  artifacts: WorkshopArtifact[];
  events: WorkshopEvent[];
  builder_contributions: Record<string, BuilderContribution>;
}

export interface DayMetric {
  date: string;
  value: number;
}

export interface AggregateMetrics {
  period: string;
  total_tasks: number;
  completed_tasks: number;
  interrupted_tasks: number;
  total_artifacts: number;
  total_tokens: number;
  total_handoffs: number;
  avg_duration_seconds: number;
  tasks_by_day: DayMetric[];
  artifacts_by_day: DayMetric[];
  tokens_by_day: DayMetric[];
}

export interface BuilderMetrics {
  archetype: string;
  period: string;
  tasks_participated: number;
  tasks_led: number;
  artifacts_produced: number;
  tokens_used: number;
  avg_duration_seconds: number;
  specialty_efficiency: number;
  handoffs_initiated: number;
  handoffs_received: number;
}

export interface HandoffFlow {
  from_builder: string;
  to_builder: string;
  count: number;
}

export interface FlowMetrics {
  flows: HandoffFlow[];
  total_handoffs: number;
}

// Replay state
export interface ReplayState {
  taskId: string;
  events: WorkshopEvent[];
  currentIndex: number;
  isPlaying: boolean;
  playbackSpeed: number;
  duration: number;
  elapsed: number;
}
```

---

## Component Specifications

### 1. MetricsDashboard.tsx

```typescript
interface MetricsDashboardProps {
  period?: '24h' | '7d' | '30d' | 'all';
  onPeriodChange?: (period: string) => void;
}

// Features:
// - Period selector (24h, 7d, 30d, all)
// - Summary cards (tasks, artifacts, tokens) with sparklines
// - Builder performance bars
// - Handoff flow visualization
// - Auto-refresh every 30s when visible
```

### 2. BuilderStats.tsx

```typescript
interface BuilderStatsProps {
  archetype: BuilderArchetype;
  metrics: BuilderMetrics;
  showDetails?: boolean;
}

// Features:
// - Builder icon and name
// - Key metrics (tasks, artifacts, efficiency)
// - Progress bar for specialty efficiency
// - Expandable detail section
// - Comparison to average
```

### 3. TaskHistory.tsx

```typescript
interface TaskHistoryProps {
  pageSize?: number;
  onSelectTask?: (taskId: string) => void;
  onReplayTask?: (taskId: string) => void;
}

// Features:
// - Paginated list of tasks
// - Status icons (✓ completed, ⚠ interrupted)
// - Builder sequence visualization
// - Quick stats (artifacts, tokens, duration)
// - Filter by status
// - Search by description
// - Click to view details
// - Replay button
```

### 4. TaskReplay.tsx

```typescript
interface TaskReplayProps {
  taskId: string;
  onClose: () => void;
}

// Features:
// - Mini WorkshopMesa showing replay state
// - Event log synced to timeline
// - Scrubber slider
// - Playback controls (play, pause, step, speed)
// - Current event highlight
// - Jump to event on click
```

---

## Store Extensions

Extend `workshopStore.ts`:

```typescript
interface WorkshopState {
  // ... existing state ...

  // History
  taskHistory: TaskHistoryItem[];
  historyPage: number;
  historyTotal: number;
  selectedTaskId: string | null;
  taskDetail: TaskDetailResponse | null;

  // Metrics
  aggregateMetrics: AggregateMetrics | null;
  builderMetrics: Record<string, BuilderMetrics>;
  flowMetrics: FlowMetrics | null;
  metricsPeriod: '24h' | '7d' | '30d' | 'all';

  // Replay
  replay: ReplayState | null;

  // Actions
  setTaskHistory: (tasks: TaskHistoryItem[], total: number, page: number) => void;
  setTaskDetail: (detail: TaskDetailResponse | null) => void;
  setAggregateMetrics: (metrics: AggregateMetrics) => void;
  setBuilderMetrics: (archetype: string, metrics: BuilderMetrics) => void;
  setFlowMetrics: (metrics: FlowMetrics) => void;
  setMetricsPeriod: (period: string) => void;
  startReplay: (taskId: string, events: WorkshopEvent[]) => void;
  stepReplay: (direction: 1 | -1) => void;
  seekReplay: (index: number) => void;
  setReplaySpeed: (speed: number) => void;
  toggleReplayPlaying: () => void;
  stopReplay: () => void;
}
```

---

## API Client Extensions

Add to `api/client.ts`:

```typescript
export const workshopApi = {
  // ... existing methods ...

  // History
  getHistory: (page?: number, pageSize?: number, status?: string) =>
    apiClient.get<TaskHistoryResponse>('/v1/workshop/history', {
      params: { page, page_size: pageSize, status },
    }),

  getTaskDetail: (taskId: string) =>
    apiClient.get<TaskDetailResponse>(`/v1/workshop/history/${taskId}`),

  getTaskEvents: (taskId: string) =>
    apiClient.get<{ events: WorkshopEvent[] }>(`/v1/workshop/history/${taskId}/events`),

  // Metrics
  getAggregateMetrics: (period?: string) =>
    apiClient.get<AggregateMetrics>('/v1/workshop/metrics/aggregate', {
      params: { period },
    }),

  getBuilderMetrics: (archetype: string, period?: string) =>
    apiClient.get<BuilderMetrics>(`/v1/workshop/metrics/builder/${archetype}`, {
      params: { period },
    }),

  getFlowMetrics: () =>
    apiClient.get<FlowMetrics>('/v1/workshop/metrics/flow'),
};
```

---

## Backend Storage

### In-Memory History Store

For MVP, store task history in memory. Production would use database.

```python
# In workshop.py or new history.py

@dataclass
class TaskRecord:
    """Complete record of a task execution."""
    id: str
    description: str
    priority: int
    status: str  # completed, interrupted
    lead_builder: str
    builder_sequence: list[str]
    events: list[WorkshopEvent]
    artifacts: list[WorkshopArtifact]
    metrics: WorkshopMetrics
    created_at: datetime
    completed_at: datetime | None


class WorkshopHistoryStore:
    """In-memory store for task history."""

    def __init__(self, max_records: int = 100):
        self._records: dict[str, TaskRecord] = {}
        self._max_records = max_records

    def record_task(self, task: TaskRecord) -> None:
        """Store a completed task record."""
        if len(self._records) >= self._max_records:
            # Remove oldest
            oldest = min(self._records.values(), key=lambda r: r.created_at)
            del self._records[oldest.id]
        self._records[task.id] = task

    def get_task(self, task_id: str) -> TaskRecord | None:
        return self._records.get(task_id)

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
    ) -> tuple[list[TaskRecord], int]:
        """List tasks with pagination."""
        tasks = list(self._records.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        total = len(tasks)
        start = (page - 1) * page_size
        end = start + page_size
        return tasks[start:end], total

    def get_aggregate_metrics(self, period: str) -> dict:
        """Compute aggregate metrics for period."""
        # Filter by period
        # Aggregate counts
        # Return metrics dict
        ...
```

---

## Test Categories

1. **MetricsDashboard tests**: Period selection, data loading, sparklines
2. **BuilderStats tests**: Metric display, efficiency calculation
3. **TaskHistory tests**: Pagination, filtering, search, selection
4. **TaskReplay tests**: Playback controls, scrubber, event sync
5. **History API tests**: CRUD, pagination, filtering
6. **Metrics API tests**: Aggregate computation, period filtering
7. **Store tests**: History state, replay state
8. **Integration tests**: Dashboard with API, replay with events

---

## Exit Criteria

- [ ] `MetricsDashboard.tsx` shows aggregate metrics with sparklines
- [ ] `BuilderStats.tsx` displays per-builder performance
- [ ] `TaskHistory.tsx` lists tasks with pagination and filtering
- [ ] `TaskReplay.tsx` replays task execution with scrubber
- [ ] History API endpoints working
- [ ] Metrics API endpoints working
- [ ] Store extensions for history and replay
- [ ] 60+ tests passing
- [ ] Metrics tab accessible from Workshop page
- [ ] Replay launches from task history
- [ ] Auto-refresh for live metrics

---

## Implementation Order

1. **Backend First**:
   - Add `WorkshopHistoryStore` class
   - Wire history recording into `WorkshopFlux`
   - Add history API endpoints
   - Add metrics API endpoints
   - Write backend tests

2. **Store & Types**:
   - Add TypeScript types
   - Extend `workshopStore.ts`
   - Add API client methods

3. **Components**:
   - `MetricsDashboard.tsx` (uses existing Sparkline, Bar)
   - `BuilderStats.tsx` (simple display)
   - `TaskHistory.tsx` (list with pagination)
   - `TaskReplay.tsx` (most complex - scrubber + mesa)

4. **Integration**:
   - Add Metrics tab to Workshop page
   - Wire replay modal
   - Add auto-refresh

---

## Synergies

| Source | Pattern | Application |
|--------|---------|-------------|
| `Dashboard.tsx` | Metrics card layout | MetricsDashboard |
| `Sparkline.tsx` | Time series visualization | Metrics sparklines |
| `Bar.tsx` | Progress visualization | Builder efficiency bars |
| `WorkshopMesa.tsx` | Builder visualization | Replay mini-mesa |
| `useTownStream.ts` | Auto-refresh pattern | Metrics polling |

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand existing metrics and dashboard patterns before implementing.

### Actions
1. Read `WorkshopMetrics` dataclass in `workshop.py`
2. Read `Dashboard.tsx` for layout patterns
3. Read `Sparkline.tsx` and `Bar.tsx` reactive primitives
4. Check if any history storage exists
5. Study pagination patterns in existing API

### Exit Criteria
- [ ] Metrics dataclass understood
- [ ] Dashboard patterns clear
- [ ] Reactive primitives reviewed
- [ ] Storage gaps identified

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
Design APIs, types, and component interfaces.

### Actions
1. Define TypeScript types for history/metrics
2. Design API endpoint signatures
3. Design store extensions
4. Design component props interfaces
5. Create file stubs

### Exit Criteria
- [ ] All types defined
- [ ] API designed
- [ ] Store designed
- [ ] Component interfaces designed

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
Implement all metrics and history features.

### Actions
1. Implement `WorkshopHistoryStore`
2. Wire history recording in flux
3. Add history API endpoints
4. Add metrics API endpoints
5. Extend workshopStore
6. Create `MetricsDashboard.tsx`
7. Create `BuilderStats.tsx`
8. Create `TaskHistory.tsx`
9. Create `TaskReplay.tsx`
10. Add Metrics tab to Workshop

### Exit Criteria
- [ ] All code written
- [ ] TypeScript compiles
- [ ] Features accessible
- [ ] Basic functionality works

### Minimum Artifact
Working metrics dashboard.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Test all metrics and history features.

### Actions
1. Backend API tests
2. Store tests
3. Component unit tests
4. Integration tests
5. Manual testing

### Exit Criteria
- [ ] 60+ tests passing
- [ ] All features tested
- [ ] Replay works end-to-end

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
Document learnings and wrap up Builder's Workshop.

### Actions
1. Update parent plan progress
2. Add learnings to `plans/meta.md`
3. Update chunk9 status to complete
4. Write workshop epilogue

### Exit Criteria
- [ ] Parent plan updated
- [ ] Learnings captured
- [ ] Workshop complete

### Minimum Artifact
Updated session_notes + epilogue.

### Continuation
`[COMPLETE]` - Builder's Workshop done!

</details>

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | done | This document |
| RESEARCH | done | Studied WorkshopMetrics, Dashboard.tsx patterns, reactive primitives |
| DEVELOP | done | TypeScript types in api/types.ts, store extensions |
| STRATEGIZE | skipped | Strategy set in parent plan |
| CROSS-SYNERGIZE | done | Used Dashboard.tsx layout, Sparkline pattern (SVG), immer patterns |
| IMPLEMENT | done | history.py, API endpoints, MetricsDashboard/TaskHistory/TaskReplay |
| QA | done | TypeScript compiles clean |
| TEST | done | 14 backend tests (all passing) |
| EDUCATE | skipped | Doc-only deferred |
| MEASURE | deferred | - |
| REFLECT | done | Updated session_notes, meta.md learnings |

---

## Completion Preview

After Chunk 9, the Builder's Workshop will have:

1. **Backend** (Chunks 4-7): 361 tests
   - BUILDER_POLYNOMIAL
   - 5 Builder classes
   - WorkshopEnvironment
   - WorkshopFlux

2. **Frontend** (Chunks 8-9): ~184 tests
   - Workshop page with mesa, sidebar, progress
   - SSE streaming
   - Metrics dashboard
   - Task history with replay

3. **Total**: ~545 tests across full workshop implementation

---

*"The workshop remembers. Every task, every handoff, every spark of creativity—witnessed and preserved."*
