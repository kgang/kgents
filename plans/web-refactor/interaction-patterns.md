---
path: plans/web-refactor/interaction-patterns
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: [web-refactor/user-flows]
parent: plans/web-refactor/webapp-refactor-master
requires: [web-refactor/elastic-primitives]
session_notes: |
  Core impulse: move agents around, build pipelines. This chunk gives
  users agency over composition—the UI becomes an operad algebra.
  COMPLETE: All 4 phases done - DnD, Pipeline Canvas, Historical Mode, Polish.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
entropy:
  planned: 0.08
  spent: 0.08
  returned: 0.0
---

# Interaction Patterns

> *"The UI is an operad algebra. Composition is primary."*

## Problem Statement

Current interactions are limited:
- Click citizen → show details
- Click play/pause → control simulation
- Input text → submit to INHABIT

Users want to **compose**:
- Drag agents into pipelines
- Connect outputs to inputs
- Replay historical simulations
- Fork and modify agent configurations

---

## Core Interaction Modes

### 1. Observe Mode (Default)

Standard viewing mode:
- Click to select
- Hover for tooltips
- Scroll to navigate
- Keyboard shortcuts available

### 2. Build Mode

Pipeline construction mode:
- Drag agents from palette
- Drop on canvas or into pipeline slots
- Connect ports with wires
- Validate compositions in real-time

### 3. Historical Mode

Replay past simulations:
- Timeline scrubber
- Step forward/backward
- All mutations disabled
- Visual differentiation (timeline UI visible)

### 4. INHABIT Mode

Existing mode for embodying agents:
- Direct agent control
- Consent mechanics
- Force/apologize actions

---

## Drag & Drop System

### DnD Provider

Use `@dnd-kit/core` for accessible, performant DnD:

```typescript
import {
  DndContext,
  DragOverlay,
  useDraggable,
  useDroppable,
} from '@dnd-kit/core';

interface DragData {
  type: 'agent' | 'pipeline-node' | 'widget';
  id: string;
  sourceZone: string;
  payload: unknown;
}

interface DropZone {
  id: string;
  accepts: DragData['type'][];
  onDrop: (data: DragData) => void;
}
```

### Draggable Agents

```typescript
interface DraggableAgentProps {
  agent: CitizenCardJSON;
  dragHandle?: 'card' | 'icon' | 'grip';
}

function DraggableAgent({ agent, dragHandle = 'grip' }: DraggableAgentProps) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: agent.citizen_id,
    data: {
      type: 'agent',
      id: agent.citizen_id,
      sourceZone: 'mesa',
      payload: agent,
    },
  });

  return (
    <ElasticCard
      ref={setNodeRef}
      {...(dragHandle === 'card' ? { ...listeners, ...attributes } : {})}
      className={isDragging ? 'opacity-50' : ''}
    >
      {dragHandle === 'grip' && (
        <GripHandle {...listeners} {...attributes} />
      )}
      <CitizenCard {...agent} />
    </ElasticCard>
  );
}
```

### Drop Zones

```typescript
interface PipelineSlotProps {
  slotId: string;
  accepts: ('agent' | 'output')[];
  onDrop: (data: DragData) => void;
  children?: React.ReactNode;
}

function PipelineSlot({ slotId, accepts, onDrop, children }: PipelineSlotProps) {
  const { isOver, setNodeRef } = useDroppable({
    id: slotId,
    data: { accepts },
  });

  return (
    <div
      ref={setNodeRef}
      className={`
        border-2 border-dashed rounded-lg p-4 transition-colors
        ${isOver ? 'border-town-highlight bg-town-highlight/10' : 'border-town-accent/30'}
        ${children ? '' : 'min-h-[100px] flex items-center justify-center'}
      `}
    >
      {children || <span className="text-gray-500">Drop agent here</span>}
    </div>
  );
}
```

---

## Pipeline Canvas

### Data Model

```typescript
interface PipelineNode {
  id: string;
  type: 'agent' | 'operation' | 'input' | 'output';
  position: { x: number; y: number };
  data: unknown;
  ports: {
    inputs: Port[];
    outputs: Port[];
  };
}

interface Port {
  id: string;
  label: string;
  type: string; // Type hint for validation
  connected?: string; // Port ID of connection
}

interface PipelineEdge {
  id: string;
  source: { nodeId: string; portId: string };
  target: { nodeId: string; portId: string };
}

interface Pipeline {
  id: string;
  name: string;
  nodes: PipelineNode[];
  edges: PipelineEdge[];
}
```

### Canvas Component

```typescript
interface PipelineCanvasProps {
  pipeline: Pipeline;
  mode: 'view' | 'edit';
  onNodeAdd: (node: Omit<PipelineNode, 'id'>) => void;
  onNodeMove: (id: string, position: { x: number; y: number }) => void;
  onNodeRemove: (id: string) => void;
  onEdgeAdd: (edge: Omit<PipelineEdge, 'id'>) => void;
  onEdgeRemove: (id: string) => void;
}

function PipelineCanvas(props: PipelineCanvasProps) {
  // SVG-based edge rendering
  // Draggable nodes with React Flow or custom implementation
  // Port connection handling
}
```

### Connection Validation

Connections are validated against the operad grammar:

```typescript
function canConnect(source: Port, target: Port, operad: Operad): boolean {
  // Type compatibility
  if (source.type !== target.type && target.type !== 'any') {
    return false;
  }

  // Operad law validation
  return operad.isValidComposition(source.nodeType, target.nodeType);
}
```

---

## Historical Mode

### Timeline Scrubber

```typescript
interface TimelineScrubberProps {
  totalTicks: number;
  currentTick: number;
  events: TownEvent[];
  onSeek: (tick: number) => void;
  onPlay: () => void;
  onPause: () => void;
  isPlaying: boolean;
}

function TimelineScrubber(props: TimelineScrubberProps) {
  // Horizontal timeline
  // Event markers at significant moments
  // Drag to seek
  // Keyboard: arrow keys for step, space for play/pause
}
```

### Historical State Management

```typescript
interface HistoricalState {
  mode: 'live' | 'historical';
  currentTick: number;
  maxTick: number;
  snapshots: Map<number, ColonyDashboardJSON>;
}

function useHistoricalMode(townId: string) {
  const [state, setState] = useState<HistoricalState>({
    mode: 'live',
    currentTick: 0,
    maxTick: 0,
    snapshots: new Map(),
  });

  const enterHistorical = (tick: number) => {
    setState(s => ({ ...s, mode: 'historical', currentTick: tick }));
  };

  const returnToLive = () => {
    setState(s => ({ ...s, mode: 'live', currentTick: s.maxTick }));
  };

  const seekTo = (tick: number) => {
    // Fetch snapshot from cache or API
    // Update currentTick
  };

  return { state, enterHistorical, returnToLive, seekTo };
}
```

### Visual Differentiation

Historical mode has distinct visual treatment:

```css
.historical-mode {
  /* Subtle sepia overlay */
  filter: sepia(10%);

  /* Timeline always visible */
  .timeline-scrubber {
    display: block;
    position: sticky;
    bottom: 0;
  }

  /* Disable interactive elements */
  .interactive-element {
    pointer-events: none;
    opacity: 0.7;
  }

  /* "Viewing history" badge */
  &::before {
    content: 'Viewing History';
    position: fixed;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--color-warning);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
  }
}
```

---

## Keyboard Shortcuts

Global shortcuts (always active):

| Key | Action |
|-----|--------|
| `Space` | Play/Pause simulation |
| `Escape` | Close modal/panel, exit mode |
| `?` | Show keyboard shortcuts |
| `b` | Toggle build mode |
| `h` | Toggle historical mode |
| `1-9` | Select nth agent |
| `←/→` | Step backward/forward (historical) |

Build mode shortcuts:

| Key | Action |
|-----|--------|
| `Delete/Backspace` | Remove selected node |
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` | Redo |
| `Ctrl+S` | Save pipeline |
| `Ctrl+E` | Execute pipeline |

---

## Gesture Support (Touch)

| Gesture | Action |
|---------|--------|
| Tap | Select |
| Long press | Open context menu / drag mode |
| Pinch | Zoom canvas |
| Two-finger pan | Scroll canvas |
| Swipe left (on agent) | Quick action menu |

---

## Implementation Tasks

### Phase 1: DnD Foundation
- [x] Install and configure `@dnd-kit/core`
- [x] Create `DraggableAgent` component
- [x] Create `PipelineSlot` drop zone
- [x] Build drag overlay for preview

### Phase 2: Pipeline Canvas
- [x] Design pipeline data model
- [x] Create `PipelineCanvas` component
- [x] Implement node positioning
- [x] Implement edge rendering (SVG)
- [x] Add port connection logic

### Phase 3: Historical Mode
- [x] Create `TimelineScrubber` component
- [x] Implement `useHistoricalMode` hook
- [x] Add snapshot caching
- [x] Create visual differentiation CSS
- [x] Add keyboard navigation

### Phase 4: Polish
- [x] Add keyboard shortcuts
- [x] Add touch gestures
- [x] Add undo/redo for pipeline edits
- [x] Create context menus

---

## Connection to AGENTESE

Pipelines map directly to AGENTESE compositions:

```typescript
// User builds this visually:
// [Scout] >> [Sage] >> [Spark]

// Converts to AGENTESE path:
const agentesePath = pipeline
  .nodes
  .filter(n => n.type === 'agent')
  .map(n => `world.agent.${n.data.name}`)
  .join(' >> ');

// "world.agent.Scout >> world.agent.Sage >> world.agent.Spark"
```

Validation uses the operad:

```python
# Backend validates composition
BUILDER_OPERAD.is_valid_composition([Scout, Sage, Spark])  # True/False
```

---

## Success Metrics

1. **Drag Latency**: <16ms from drag start to visual feedback
2. **Connection Accuracy**: 95% of drop attempts hit intended target
3. **Historical Seek**: <100ms to render any snapshot
4. **Keyboard Coverage**: 100% of actions accessible via keyboard

---

*"Agents are morphisms in a category; composition is primary."*
