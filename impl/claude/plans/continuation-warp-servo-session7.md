# WARP + Servo: Session 7 - QA & Phase 3 Enhancement

> *"Daring, bold, creative, opinionated but not gaudy"*

**Date**: 2025-12-20
**Previous Session**: Phase 2 completed (WARP → SceneGraph converters + React Servo components)
**This Session**: QA/robustify Phase 2, then iteratively enhance Phase 3

---

## Context: What Was Built in Session 6

### Key Design Decision Made

We **reused existing SceneGraph** instead of creating new `servo_primitives.py`:

| Original Plan | Actual Implementation |
|---------------|----------------------|
| `servo_primitives.py` | Reuse `protocols/agentese/projection/scene.py` |
| New `ServoNodeKind` | Use existing `SceneNodeKind` (9 kinds) |
| Separate style system | Map to existing Living Earth palette |

**Rationale**: SceneGraph already has 47 tests with category laws verified.

### Files Created (Session 6)

**Python**:
```
protocols/agentese/projection/warp_converters.py  # 33 tests passing
```

**React**:
```
web/src/components/servo/
├── index.ts                  # Barrel export
├── theme.ts                  # Living Earth palette mapping
├── TraceNodeCard.tsx         # TRACE node renderer
├── WalkCard.tsx              # WALK node renderer
├── ServoNodeRenderer.tsx     # Kind → Component dispatch
├── ServoEdgeRenderer.tsx     # SVG vine edges
└── ServoSceneRenderer.tsx    # Full scene with layout
```

### Current Test Status

```bash
# Run these to verify baseline
cd /Users/kentgang/git/kgents/impl/claude
uv run pytest protocols/agentese/projection/_tests/ -v  # 128 tests
cd web && npm run typecheck  # Should pass
```

---

## Session 7 Goals

### Part 1: QA & Robustify Phase 2 (1-2 hours)

#### 1.1 Review Converter Edge Cases

Check `warp_converters.py` for:
- [ ] Empty content handling (null/None in TraceNode fields)
- [ ] Very long labels (beyond 40 char truncation)
- [ ] Unicode in stimulus/response content
- [ ] Walk with 0 traces
- [ ] Walk with 100+ traces (performance)

Add tests for any gaps found.

#### 1.2 React Component Robustness

Check servo components for:
- [ ] Missing/undefined props gracefully handled
- [ ] Empty SceneGraph renders empty state (not crash)
- [ ] Keyboard navigation (a11y)
- [ ] `prefers-reduced-motion` works (breathing disabled)

#### 1.3 Type Safety Audit

```bash
# Backend
cd /Users/kentgang/git/kgents/impl/claude
uv run mypy protocols/agentese/projection/warp_converters.py --strict

# Frontend
cd web && npm run typecheck
```

Fix any type issues found.

#### 1.4 Integration Test

Create a simple integration test that:
1. Creates a Walk with TraceNodes
2. Converts to SceneGraph via `walk_to_scene()`
3. Serializes to JSON (simulating API response)
4. Verify structure matches what React expects

```python
# Add to test_warp_converters.py
def test_full_pipeline_walk_to_json():
    """Walk → SceneGraph → JSON round-trip."""
    walk = Walk.create("Test pipeline")
    # Add traces...
    graph = walk_to_scene(walk)
    json_data = graph.to_dict()

    # Verify React-expected structure
    assert "nodes" in json_data
    assert "layout" in json_data
    assert json_data["nodes"][0]["kind"] == "WALK"
```

---

### Part 2: Phase 3 Enhancement (2-3 hours)

Phase 3 chunks from original plan:
1. **Chunk 3: TerrariumView** - Full trace browser
2. **Chunk 4: Playback UI** - Session replay
3. **Chunk 5: Intent Navigation** - IntentTree visualization

#### 2.1 Priority: TerrariumView Foundation

Create a simple Witness dashboard page that:
- Fetches active Walks via AGENTESE (`time.walk.list`)
- Renders them using `ServoSceneRenderer`
- Shows trace timeline when Walk is selected

**Files to create/modify**:
```
web/src/pages/Witness.tsx          # New page (or enhance existing)
web/src/hooks/useWitnessDashboard.ts  # Data fetching hook
```

**Approach**:
```typescript
// useWitnessDashboard.ts
export function useWitnessDashboard() {
  const { data: walks } = useQuery(['walks'], () =>
    fetch('/api/agentese/time.walk.list').then(r => r.json())
  );

  const sceneGraph = useMemo(() => {
    if (!walks) return null;
    // walks is already SceneGraph JSON from warp_converters
    return walks;
  }, [walks]);

  return { sceneGraph, isLoading: !walks };
}

// Witness.tsx
export function WitnessPage() {
  const { sceneGraph, isLoading } = useWitnessDashboard();

  if (isLoading) return <PersonalityLoading />;
  if (!sceneGraph) return <EmptyState message="No active walks" />;

  return (
    <ServoSceneRenderer
      scene={sceneGraph}
      onNodeSelect={handleNodeSelect}
    />
  );
}
```

#### 2.2 Wire AGENTESE Endpoint

Ensure `time.walk.list` AGENTESE node exists and returns SceneGraph:

```python
# Check if node exists
# protocols/agentese/contexts/time_trace_warp.py

@node(
    path="time.walk.list",
    description="List active and recent Walks as SceneGraph",
)
async def list_walks(observer: Umwelt) -> SceneGraph:
    """Return dashboard of Walks."""
    from services.witness.walk import get_walk_store
    from protocols.agentese.projection.warp_converters import walk_dashboard_to_scene

    store = get_walk_store()
    walks = store.recent_walks(limit=20)
    return walk_dashboard_to_scene(walks)
```

#### 2.3 Enhancement: Trace Detail View

When a WALK node is clicked:
1. Fetch full Walk with traces
2. Convert to timeline SceneGraph
3. Render in detail panel

```typescript
// In Witness.tsx
const [selectedWalkId, setSelectedWalkId] = useState<string | null>(null);

const handleNodeSelect = (node: SceneNode) => {
  if (node.kind === 'WALK') {
    setSelectedWalkId(node.metadata.walk_id);
  }
};

// Fetch and display trace timeline when walk selected
const { data: traceTimeline } = useQuery(
  ['walk-traces', selectedWalkId],
  () => fetch(`/api/agentese/time.walk.${selectedWalkId}.traces`).then(r => r.json()),
  { enabled: !!selectedWalkId }
);
```

---

## Key Files to Read

1. `protocols/agentese/projection/warp_converters.py` - The converters
2. `protocols/agentese/projection/scene.py` - SceneGraph primitives
3. `web/src/components/servo/ServoSceneRenderer.tsx` - React renderer
4. `services/witness/walk.py` - Walk model
5. `protocols/agentese/contexts/time_trace_warp.py` - AGENTESE nodes

---

## Quick Start Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Verify Phase 2 baseline
uv run pytest protocols/agentese/projection/_tests/ -v

# Check types
uv run mypy protocols/agentese/projection/ --ignore-missing-imports

# Frontend
cd web
npm run typecheck
npm run dev  # Start dev server
```

---

## Anti-Sausage Anchors

Quote these when making decisions:

- *"Tasteful > feature-complete"* — Focus on TerrariumView foundation, not all 3 chunks
- *"The Mirror Test"* — Would Kent enjoy clicking through this dashboard?
- *"Daring, bold, creative"* — The breathing surfaces should feel alive
- *"Depth over breadth"* — Better to have one polished view than three half-baked

---

## Success Criteria

**Part 1 (QA)**:
- [ ] Edge case tests added for converters
- [ ] No mypy errors in warp_converters.py
- [ ] React components handle missing data gracefully
- [ ] Integration test verifies JSON round-trip

**Part 2 (Phase 3)**:
- [ ] Witness page renders Walk dashboard
- [ ] Clicking a Walk shows trace timeline
- [ ] AGENTESE nodes return SceneGraph
- [ ] Breathing animation visible on active Walks

---

## Constitution Reminder

| Principle | Check |
|-----------|-------|
| **Composable** | Do converters compose via `>>`? |
| **Joy-Inducing** | Does the dashboard feel alive? |
| **Tasteful** | Are we adding cruft or value? |
| **Generative** | Can spec regenerate impl? |

---

*"The webapp is not the UI. The webapp is the composition boundary."*
