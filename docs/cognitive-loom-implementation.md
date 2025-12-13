# Cognitive Loom Implementation - Track B Complete

## Overview

Track B of the Generative TUI Framework is now complete. The Cognitive Loom replaces the Dashboard Fallacy with a tree-based visualization of agent cognition, making the Shadow (rejected hypotheses) visible.

## Key Insight

> Agent cognition is a TREE SEARCH, not a linear log.

Traditional monitoring shows only what the agent did. The Cognitive Loom shows:
- **Main trunk**: Selected actions (the path taken)
- **Ghost branches**: Rejected hypotheses (the Shadow)
- **Current state**: Where the agent is now

Bugs often hide in "the path not taken" - making ghost branches visible helps debug agent reasoning.

## Implementation

### 1. Data Structures (`impl/claude/agents/i/data/loom.py`)

#### CognitiveBranch
Represents a node in the cognitive tree:

```python
@dataclass
class CognitiveBranch:
    id: str
    timestamp: datetime
    content: str
    reasoning: str
    selected: bool  # Main trunk or ghost?
    children: list["CognitiveBranch"]
    parent_id: Optional[str]

    @property
    def glyph(self) -> str:
        """● for current, ○ for selected, ✖ for rejected"""

    @property
    def opacity(self) -> float:
        """Ghost branches fade over time (1 hour)"""
```

#### CognitiveTree
The full cognitive history:

```python
@dataclass
class CognitiveTree:
    root: CognitiveBranch
    current_id: str

    def main_path(self) -> list[CognitiveBranch]:
        """Get selected path from root to current"""

    def ghost_branches(self) -> list[CognitiveBranch]:
        """Get all rejected nodes - the Shadow"""

    def all_nodes(self) -> list[CognitiveBranch]:
        """Get everything"""
```

### 2. BranchTree Widget (`impl/claude/agents/i/widgets/branch_tree.py`)

Renders the cognitive tree as git-graph style ASCII art:

```python
class BranchTree(Widget):
    tree: reactive[CognitiveTree | None]
    show_ghosts: reactive[bool] = reactive(True)

    def render(self) -> RenderResult:
        """Render tree with box-drawing characters"""
```

Features:
- Box-drawing characters: `│ ├ └ ─`
- Current node highlighted (bold)
- Ghost branches dimmed
- Reasoning shown for significant branch points
- Toggle ghost visibility

### 3. Timeline Widget (`impl/claude/agents/i/widgets/timeline.py`)

Horizontal timeline with activity bars grouped by day:

```python
class Timeline(Widget):
    events: reactive[list[tuple[datetime, float]]]
    cursor_index: reactive[int]
    num_days: reactive[int] = reactive(7)

    def move_cursor_left(self) -> None
    def move_cursor_right(self) -> None
```

Features:
- Sparkline-style activity bars per day
- Cursor navigation
- Configurable number of days to show

## Example Output

```
└─○ Received user query: 'Find all TODO comments'
  ├─○ Plan A: Use grep to search
  │ └─○ Action: grep -r 'TODO' .
  │   └─○ Result: Permission denied on .git/
  │     ├─○ Option: Retry grep with --exclude-dir
  │     │ └─○ Action: grep -r 'TODO' --exclude-dir=.git .
  │     │   └─● Result: Found 42 TODO comments [CURRENT]
  │     └─✖ Option: Fall back to find command
  │         (Unsafe - might search too many files)
  └─✖ Plan B: Use find with exec
      (Too slow for large codebases)
```

## Test Coverage

All 52 tests passing:

### Data Layer (`test_loom.py`) - 21 tests
- CognitiveBranch initialization and properties
- Glyph rendering (●, ○, ✖)
- Opacity calculation for ghost fading
- Tree traversal (get_node, main_path, ghost_branches)
- Depth calculation

### BranchTree Widget (`test_branch_tree.py`) - 13 tests
- Rendering single nodes, linear paths, branching trees
- Ghost visibility toggle
- Current node highlighting
- Dimmed styling for ghosts
- Long content truncation

### Timeline Widget (`test_timeline.py`) - 18 tests
- Day grouping and bar generation
- Cursor navigation (left/right)
- Activity level visualization
- Event addition

## Usage

### Basic Example

```python
from agents.i.data.loom import CognitiveBranch, CognitiveTree
from agents.i.widgets.branch_tree import BranchTree

# Create a tree
root = CognitiveBranch(
    id="start",
    timestamp=datetime.now(),
    content="Initial state",
    reasoning="",
)

# Add selected child
selected = CognitiveBranch(
    id="action-1",
    timestamp=datetime.now(),
    content="Took action A",
    reasoning="Best option",
    selected=True,
    parent_id="start",
)

# Add rejected child (ghost)
ghost = CognitiveBranch(
    id="action-2",
    timestamp=datetime.now(),
    content="Considered action B",
    reasoning="Too risky",
    selected=False,
    parent_id="start",
)

root.children.extend([selected, ghost])

# Create tree
tree = CognitiveTree(root=root, current_id="action-1")

# Render
widget = BranchTree(tree=tree)
print(widget.render())
```

### Timeline Example

```python
from agents.i.widgets.timeline import Timeline
from datetime import datetime

timeline = Timeline()

# Add events
now = datetime.now()
timeline.add_event(now, 0.5)  # 50% activity
timeline.add_event(now, 0.8)  # 80% activity

# Navigate
timeline.move_cursor_right()
```

## Design Principles

### 1. The Shadow is Visible
Rejected branches are not hidden - they're faded but present. This transparency aids debugging.

### 2. Time is Topology
Navigate up/down through time, left/right through branches. The tree structure reveals decision-making patterns.

### 3. Temporal Gradient
Ghost branches fade over time (1 hour decay). Recent rejections are vivid, old ones dim to background.

### 4. Crystallization (Stubbed)
The `c` key will eventually crystallize a moment to D-gent memory. This allows preserving important decision points for future reference.

## Integration Points

### Current
- Exports added to `/Users/kentgang/git/kgents/impl/claude/agents/i/data/__init__.py`
- Exports added to `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/__init__.py`

### Future
- Wire FluxAgent to emit CognitiveBranch nodes during execution
- Create LoomScreen with navigation keybindings (h/j/k/l)
- Implement crystallization to D-gent memory (c key)
- Add forecasting visualization (potential futures)

## Files Created

### Data Layer
- `/Users/kentgang/git/kgents/impl/claude/agents/i/data/loom.py` (217 lines)
- `/Users/kentgang/git/kgents/impl/claude/agents/i/data/_tests/test_loom.py` (440 lines)

### Widgets
- `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/branch_tree.py` (166 lines)
- `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/timeline.py` (172 lines)
- `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/_tests/test_branch_tree.py` (327 lines)
- `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/_tests/test_timeline.py` (213 lines)

### Demo
- `/Users/kentgang/git/kgents/impl/claude/agents/i/widgets/_tests/demo_loom.py` (177 lines)

**Total**: ~1,712 lines of code + tests + demo

## Next Steps (Track C: Visual Hints)

Track B is complete. The next phase is Track C: Visual Hint Protocol, which will allow agents to emit VisualHints to shape their own representation (heterarchical UI).

## Cross-References

- **Framework spec**: `/Users/kentgang/git/kgents/plans/interfaces/alethic-workbench.md`
- **Primitives spec**: `/Users/kentgang/git/kgents/plans/interfaces/primitives.md` (P6: BranchTree, P7: Timeline)
- **Roadmap**: `/Users/kentgang/git/kgents/plans/interfaces/implementation-roadmap.md` (Track B)

---

*"The noun is a lie. There is only the rate of change."*

*"Don't just look at the agent. Look through the agent."*

**Make the Shadow visible.**
