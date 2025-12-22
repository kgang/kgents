# Visual Trail Graph: Full UI/UX Vision

> *"Bush's Memex realized: Force-directed graph showing exploration trails with reasoning traces."*
>
> Voice Anchor: *"Joy-inducing > merely functional"*, *"The persona is a garden, not a museum"*

**Status**: Active Development
**Created**: 2025-12-22
**Prerequisites**: Phase 1-2 complete (force layout, basic trail builder)

---

## Design Decisions (Resolved)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Branching during creation? | **Yes** | Captures real exploration patterns; trails fork naturally |
| Validate paths against files? | **Yes + Create** | Validate, but offer to create missing files naturally |
| Required vs optional reasoning? | **Hierarchical** | Required at sheaf/global level; optional for atomic steps |

---

## Current State (Done)

- [x] d3-force physics layout with semantic edge weighting
- [x] TrailBuilderPanel with undo/redo, reorder, topics
- [x] PathPicker modal with recent/suggestions
- [x] `self.trail.create` backend aspect
- [x] 13 edge types (8 structural + 5 semantic)
- [x] "Redistribute" button for layout refresh

---

## Phase 3: Branching & Validation

### 3.1 Branching Trail Creation

**Vision**: Trails aren't always linear. Real exploration branches—you try path A, backtrack, try path B. The UI should support this naturally.

#### Data Model Extension

```typescript
// stores/trailBuilder.ts
interface TrailBuilderStep {
  id: string;
  path: string;
  edge: EdgeType | null;
  reasoning: string;
  parentId: string | null;  // NEW: null = root, otherwise = branch from parent
  children: string[];       // NEW: IDs of child steps
}

interface TrailBuilderState {
  // ... existing
  rootStepId: string | null;      // Entry point
  currentBranchId: string | null; // Active branch tip

  // New actions
  branchFrom: (stepId: string) => void;     // Create branch point
  switchBranch: (stepId: string) => void;   // Navigate to different branch
  mergeBranches: (sourceId: string, targetId: string) => void; // Converge
}
```

#### UI Changes

```
┌─────────────────────────────────────┐
│  TRAIL BUILDER                      │
├─────────────────────────────────────┤
│  Name: [Exploring Auth Patterns   ] │
│                                     │
│  ─── Graph View ───                 │
│                                     │
│       ┌──────────┐                  │
│       │ spec/auth│ ← You are here   │
│       └────┬─────┘                  │
│            │                        │
│      ┌─────┴─────┐                  │
│      ▼           ▼                  │
│  ┌────────┐  ┌────────┐             │
│  │provider│  │ middleware│          │
│  └────────┘  └────┬───┘             │
│                   │                 │
│              [+ Branch]             │
│                                     │
│  ─── Current Path ───               │
│  1. spec/auth.md (start)            │
│  2. services/auth/middleware.py     │
│     [+ Add Step] [⑂ Branch Here]   │
│                                     │
└─────────────────────────────────────┘
```

**Interaction**:
- Click "⑂ Branch Here" on any step to create a fork
- Graph updates in real-time showing the branch
- Can switch between branches via graph click
- Merge branches by dragging one onto another

#### Backend: Branching Support

```python
# In self_trail.py - update create aspect

async def create(
    self,
    observer: "Umwelt[Any, Any] | Observer",
    name: str,
    steps: list[dict[str, Any]],  # Now includes parent_index field
    topics: list[str] | None = None,
    response_format: str = "json",
) -> Renderable:
    """
    Steps can now reference parent_index for branching:

    steps = [
        {"path": "spec/auth.md", "parent_index": None},      # Root
        {"path": "provider.py", "parent_index": 0},          # Child of root
        {"path": "middleware.py", "parent_index": 0},        # Branch from root
        {"path": "jwt.py", "parent_index": 2},               # Child of middleware
    ]
    """
```

---

### 3.2 Path Validation + File Creation

**Vision**: Paths should be validated against the actual codebase, but if a file doesn't exist, offer to create it. Trails can be aspirational—documenting what *should* exist.

#### Validation Flow

```
User types: "services/auth/new_provider.py"
                    │
                    ▼
            ┌──────────────┐
            │ File exists? │
            └──────┬───────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
       [YES]               [NO]
    Add step          Show options:
                      ┌─────────────────────┐
                      │ Path not found:     │
                      │                     │
                      │ ○ Create file       │
                      │ ○ Use as conceptual │
                      │ ○ Fix path          │
                      │                     │
                      │ [Continue] [Cancel] │
                      └─────────────────────┘
```

#### Implementation

```typescript
// api/trail.ts
export async function validatePath(path: string): Promise<PathValidation> {
  const response = await fetch('/api/agentese/world/repo/exists', {
    method: 'POST',
    body: JSON.stringify({ path }),
  });

  return response.json();
  // Returns: { exists: boolean, suggestions?: string[], canCreate: boolean }
}

// When adding step
const handleAddPath = async (path: string) => {
  const validation = await validatePath(path);

  if (validation.exists) {
    addStep(path);
  } else if (validation.canCreate) {
    setShowCreateDialog({ path, suggestions: validation.suggestions });
  } else {
    setShowConceptualDialog({ path });
  }
};
```

#### Backend: Path Validation

```python
# New aspect in world/repo or self.context

@aspect(category=AspectCategory.PERCEPTION)
async def exists(
    self,
    observer: "Umwelt[Any, Any] | Observer",
    path: str,
) -> Renderable:
    """Check if path exists, suggest alternatives."""
    import os
    from pathlib import Path

    full_path = Path(self.repo_root) / path
    exists = full_path.exists()

    suggestions = []
    if not exists:
        # Find similar paths
        suggestions = await self._find_similar_paths(path, limit=5)

    can_create = not exists and full_path.suffix in ('.py', '.md', '.ts', '.tsx')

    return BasicRendering(
        summary=f"Path {'exists' if exists else 'not found'}",
        metadata={
            "exists": exists,
            "suggestions": suggestions,
            "can_create": can_create,
        },
    )
```

---

### 3.3 Hierarchical Reasoning Requirements

**Vision**: Reasoning requirements follow a sheaf-like structure—global coherence requires justification, but local moves can be implicit.

#### Levels

| Level | Reasoning | Example |
|-------|-----------|---------|
| **Trail (Sheaf)** | **Required** | "This trail documents how auth flows from spec to implementation" |
| **Branch Point** | **Required** | "Branching here to explore JWT vs session approaches" |
| **Semantic Edge** | **Encouraged** | "Similar pattern to the witness architecture" |
| **Structural Edge** | **Optional** | (imports, contains—obvious from code) |

#### UI Implementation

```tsx
// In TrailBuilderPanel

const ReasoningPrompt = ({ step, isRequired }: Props) => {
  const reasoningLevel = getReasoningLevel(step);

  return (
    <div className={cn(
      "reasoning-prompt",
      isRequired && "border-amber-500"
    )}>
      {isRequired ? (
        <label className="text-amber-400">
          ✦ Reasoning required for {reasoningLevel}
        </label>
      ) : (
        <label className="text-gray-500">
          Reasoning (optional)
        </label>
      )}
      <textarea
        value={step.reasoning}
        onChange={...}
        placeholder={getPlaceholder(reasoningLevel)}
        required={isRequired}
      />
    </div>
  );
};

const getReasoningLevel = (step: TrailBuilderStep): ReasoningLevel => {
  if (step.parentId === null && step.children.length === 0) {
    return 'trail'; // Root with no children = trail-level
  }
  if (step.children.length > 1) {
    return 'branch'; // Multiple children = branch point
  }
  if (step.edge?.startsWith('semantic:')) {
    return 'semantic';
  }
  return 'structural';
};
```

#### Validation on Save

```typescript
// stores/trailBuilder.ts

const validateBeforeSave = (): ValidationResult => {
  const errors: string[] = [];

  // Trail-level reasoning required
  if (!trailReasoning.trim()) {
    errors.push("Trail description is required");
  }

  // Branch points need reasoning
  const branchPoints = steps.filter(s => s.children.length > 1);
  for (const bp of branchPoints) {
    if (!bp.reasoning.trim()) {
      errors.push(`Branch at "${bp.path}" needs reasoning`);
    }
  }

  return { valid: errors.length === 0, errors };
};
```

---

## Phase 4: Intelligence & Polish

### 4.1 AI-Suggested Connections

**Vision**: As you build a trail, the system suggests semantically related next steps.

```
┌─────────────────────────────────────────────┐
│  SUGGESTED NEXT STEPS                       │
├─────────────────────────────────────────────┤
│  Based on: services/auth/middleware.py      │
│                                             │
│  ● services/auth/jwt.py                     │
│    [imports] — 92% semantic match           │
│    "JWT token validation utilities"         │
│                                             │
│  ● models/user.py                           │
│    [uses] — 78% semantic match              │
│    "User model with auth fields"            │
│                                             │
│  ● spec/principles.md                       │
│    [semantic:grounds] — 65% semantic match  │
│    "Principle 3: Ethical"                   │
│                                             │
│  [Use Suggestion] [Ignore]                  │
└─────────────────────────────────────────────┘
```

#### Backend: Suggestion Endpoint

```python
@aspect(category=AspectCategory.PERCEPTION)
async def suggest(
    self,
    observer: "Umwelt[Any, Any] | Observer",
    current_path: str,
    exclude: list[str] | None = None,
    limit: int = 5,
) -> Renderable:
    """
    Suggest next steps based on semantic similarity.

    Uses pgvector embeddings to find related content.
    """
    storage = await self._ensure_storage()

    # Get embedding for current path content
    embedding = await self._get_path_embedding(current_path)

    # Search for similar paths
    similar = await storage.search_semantic(
        query_embedding=embedding,
        limit=limit * 2,  # Get extra for filtering
    )

    # Filter out excluded paths
    exclude_set = set(exclude or [])
    suggestions = [
        {
            "path": s.path,
            "edge": self._infer_edge_type(current_path, s.path),
            "score": s.score,
            "snippet": s.snippet,
        }
        for s in similar
        if s.path not in exclude_set
    ][:limit]

    return BasicRendering(
        summary=f"Found {len(suggestions)} suggestions",
        metadata={"suggestions": suggestions},
    )
```

---

### 4.2 Zoom-Dependent Detail

**Vision**: At low zoom, show only holon names. At high zoom, reveal full paths and reasoning.

```typescript
// components/trail/ContextNode.tsx

const ContextNode = ({ data, selected }: NodeProps<ContextNodeData>) => {
  const { zoom } = useViewport();

  return (
    <div className="context-node">
      {/* Always visible */}
      <div className="holon font-medium">{data.holon}</div>

      {/* Visible at medium zoom */}
      {zoom > 0.7 && (
        <div className="path text-xs text-gray-500 truncate">
          {data.path}
        </div>
      )}

      {/* Visible at high zoom */}
      {zoom > 1.0 && data.edge_type && (
        <EdgeBadge type={data.edge_type} />
      )}

      {/* Visible at very high zoom */}
      {zoom > 1.3 && data.reasoning && (
        <div className="reasoning text-xs italic text-gray-400 mt-2">
          "{data.reasoning.slice(0, 120)}..."
        </div>
      )}
    </div>
  );
};
```

---

### 4.3 Record Mode (Auto-Capture)

**Vision**: Toggle "recording" during Portal exploration. Navigation steps are captured as trail steps automatically.

```
┌─────────────────────────────────────────────┐
│  🔴 RECORDING: Auth Exploration             │
│  ─────────────────────────────────────────  │
│  Captured: 7 steps                          │
│                                             │
│  Latest:                                    │
│  → services/auth/jwt.py                     │
│    via [imports] from middleware.py         │
│                                             │
│  [Pause] [Stop & Edit] [Discard]            │
└─────────────────────────────────────────────┘
```

#### Integration with Portal

```typescript
// hooks/useTrailRecorder.ts

export function useTrailRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [capturedSteps, setCapturedSteps] = useState<RecordedStep[]>([]);

  // Subscribe to Portal navigation events
  useEffect(() => {
    if (!isRecording) return;

    const unsubscribe = portalEvents.on('navigate', (event) => {
      setCapturedSteps(prev => [
        ...prev,
        {
          path: event.targetPath,
          edge: event.edgeType || 'navigates',
          timestamp: Date.now(),
          fromPath: event.sourcePath,
        },
      ]);
    });

    return unsubscribe;
  }, [isRecording]);

  const stopAndEdit = () => {
    setIsRecording(false);
    // Open TrailBuilderPanel with captured steps pre-filled
    trailBuilder.loadFromRecording(capturedSteps);
    trailBuilder.open();
  };

  return { isRecording, capturedSteps, start, pause, stopAndEdit, discard };
}
```

---

### 4.4 Keyboard Navigation

**Vision**: Navigate the graph with keyboard for power users.

| Key | Action |
|-----|--------|
| `↑/↓` | Move to parent/child step |
| `←/→` | Switch between siblings (branches) |
| `Enter` | Expand/collapse reasoning panel |
| `Space` | Select step for editing |
| `b` | Branch from current step |
| `d` | Delete current step |
| `Escape` | Deselect / close panels |

```typescript
// hooks/useTrailKeyboard.ts

export function useTrailKeyboard(
  nodes: TrailGraphNode[],
  selectedId: string | null,
  onSelect: (id: string) => void,
) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!selectedId) return;

      const current = nodes.find(n => n.id === selectedId);
      if (!current) return;

      switch (e.key) {
        case 'ArrowDown':
          // Find child
          const child = nodes.find(n => n.data.parentId === selectedId);
          if (child) onSelect(child.id);
          break;
        case 'ArrowUp':
          // Find parent
          if (current.data.parentId) {
            onSelect(current.data.parentId);
          }
          break;
        // ... etc
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [nodes, selectedId, onSelect]);
}
```

---

### 4.5 Trail Templates

**Vision**: Start from common exploration patterns.

```
┌─────────────────────────────────────────────┐
│  START FROM TEMPLATE                        │
├─────────────────────────────────────────────┤
│                                             │
│  📋 Spec → Implementation                   │
│     spec/*.md → services/*/ → tests/        │
│                                             │
│  🔍 Understanding a Feature                 │
│     entrypoint → dependencies → tests       │
│                                             │
│  🐛 Bug Investigation                       │
│     symptom → hypothesis → evidence → fix   │
│                                             │
│  🏗️ Architecture Review                    │
│     principles → patterns → violations      │
│                                             │
│  [Use Template] [Start Blank]               │
└─────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Week 1: Branching Foundation ✅ COMPLETE (Session 1)
- [x] Update TrailBuilderStep data model with parentId/children
- [x] Implement branchFrom, switchBranch actions in store
- [x] Update UI to show branch indicators (amber border, purple ring)
- [x] Backend: Support parent_index in create aspect with validation
- [x] Tree layout algorithm in trail_to_react_flow()
- [ ] E2E tests for branching (deferred to Session 4)

**Session 1 Deliverables:**
- Model: `parent_index` column in TrailStepRow
- Migration: 009_trail_parent_index.py with composite index
- Backend: parent_index validation (must reference earlier step)
- Frontend: ⑂ Branch button, branch point indicators, current branch highlighting
- Layout: Hierarchical tree positioning for branching trails

### Week 2: Validation & Reasoning ✅ COMPLETE (Session 2)
- [x] Add path validation endpoint (`world.repo.validate`)
- [x] PathPicker: Show validation state, fuzzy suggestions, "Use as conceptual"
- [x] Implement hierarchical reasoning requirements (branch=required, semantic=encouraged)
- [x] Validation on save with clear error messages
- [x] Tests for validation flows (25 new tests)

**Session 2 Deliverables:**
- Backend: `world.repo.validate` aspect with fuzzy `difflib.get_close_matches()` suggestions
- API: `validatePath()` function in `trail.ts` with `PathValidation` interface
- PathPicker: Debounced validation (400ms), green/amber borders, suggestions section
- Store: `getReasoningLevel()`, `validateReasoning()`, `getReasoningPlaceholder()`
- UI: ✦ amber "required" for branch points, ☆ purple "encouraged" for semantic edges

### Week 3: Intelligence
- [ ] Implement self.trail.suggest with pgvector
- [ ] Integrate suggestions into PathPicker
- [ ] Add zoom-dependent detail to ContextNode
- [ ] Keyboard navigation hook
- [ ] Performance optimization for large trails

### Week 4: Integration & Polish
- [ ] Record mode hook and UI
- [ ] Portal integration for auto-capture
- [ ] Trail templates
- [ ] Export to markdown
- [ ] E2E tests for full flow

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Trail creation time | <2 min for 10 steps | Friction-free |
| Suggestion acceptance rate | >30% | AI adds value |
| Branch usage | >20% of trails | Feature discovery |
| Recording adoption | >40% of trails | Natural capture |

---

## Open Questions for Future

1. **Collaborative trails?** — Multiple authors, merge conflicts
2. **Trail versioning?** — Git-like history for trails
3. **Public trail gallery?** — Share discoveries across projects
4. **Trail embedding search?** — Find trails similar to a query

---

*"The trail becomes visible. The garden reveals its paths."*
