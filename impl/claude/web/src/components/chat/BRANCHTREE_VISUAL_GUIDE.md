# BranchTree Visual Guide

> *"The file is a lie. There is only the graph."*

---

## Visual Examples

### Example 1: Basic Tree (3 branches)

```
┌────────────────────────────────────────────────────────┐
│ BRANCH TREE                                    (3/3) ▲ │
├────────────────────────────────────────────────────────┤
│                                                        │
│                    ◼ main (12 turns)                   │
│                    │                                   │
│         ┌──────────┼──────────┐                        │
│         │          │          │                        │
│    ◻ explore   ◼ refactor  ◻ cache                    │
│      (3 turns)   (5 turns)   (2 turns)                │
│                 [ACTIVE]                               │
│                                                        │
│ ◆ Maximum 3 branches. Merge or archive to fork again. │
└────────────────────────────────────────────────────────┘
```

**Legend**:
- `◼` = Active branch (white fill, white outline, subtle glow)
- `◻` = Inactive branch (dark fill, grey outline)
- `──┼──` = Angular paths (L-shaped, not curved)

---

### Example 2: After Merge

```
┌────────────────────────────────────────────────────────┐
│ BRANCH TREE                                    (2/3) ▲ │
├────────────────────────────────────────────────────────┤
│                                                        │
│                    ◼ main (17 turns)                   │
│                    │                                   │
│         ┌──────────┼──────────┐                        │
│         │          │          │                        │
│    ◻ explore   ⬚ refactor  ◻ cache                    │
│      (3 turns)   (merged)    (2 turns)                │
│                                                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Legend**:
- `⬚` = Merged branch (dashed outline, semi-transparent)

---

### Example 3: Context Menu (Right-click)

```
Right-click on "explore" branch:

┌──────────────────────────────┐
│ ⇥ Merge (Sequential)         │
│ ⇄ Merge (Interleave)         │
│ ⊕ Merge (Manual)             │
├──────────────────────────────┤
│ ◇ Archive                    │
│ ◆ Delete                     │
└──────────────────────────────┘
```

---

### Example 4: Tooltip (Hover)

```
Hover on "refactor" branch:

┌────────────────────────────────┐
│ REFACTOR                       │
│ 5 turns • Created Dec 24       │
│ Last active Dec 25             │
└────────────────────────────────┘
```

---

### Example 5: Compact Mode (Sidebar)

```
┌────────────────────────┐
│ BRANCH TREE     (2/3) ▲│
├────────────────────────┤
│                        │
│      ◼ 12              │  (turn count only, no labels)
│      │                 │
│   ┌──┼──┐              │
│   │  │  │              │
│  ◻3 ◼5 ◻2              │
│                        │
└────────────────────────┘
```

---

## Component Anatomy

### SVG Structure

```svg
<svg viewBox="0 0 400 300">
  <defs>
    <!-- Arrow marker for active edges -->
    <marker id="arrow-active">
      <path d="..." fill="#fff" />
    </marker>
  </defs>

  <!-- Edges (render first, behind nodes) -->
  <g class="branch-edges">
    <path class="branch-edge" d="M x1 y1 L x1 yMid L x2 yMid L x2 y2" />
    <path class="branch-edge branch-edge--to-active" d="..." markerEnd="url(#arrow-active)" />
  </g>

  <!-- Nodes (render second, in front) -->
  <g class="branch-nodes">
    <g class="branch-node branch-node--active" transform="translate(200, 50)">
      <!-- Glow (active only) -->
      <rect class="branch-node__glow" x="-16" y="-16" width="32" height="32" />
      <!-- Node square -->
      <rect class="branch-node__square" x="-12" y="-12" width="24" height="24" />
      <!-- Label -->
      <text class="branch-node__label" y="-20">main</text>
      <!-- Turn count -->
      <text class="branch-node__turn-count" y="28">12 turns</text>
    </g>
  </g>
</svg>
```

---

## D3 Layout Algorithm

### Step 1: Convert to Hierarchy

```typescript
const root = hierarchy(branchTree, (d) => d.children);
// Produces: D3 HierarchyNode<BranchTreeNode>
```

### Step 2: Apply Tree Layout

```typescript
const treeLayout = d3Tree<BranchTreeNode>()
  .size([width - PADDING * 2, height - PADDING * 2])
  .separation((a, b) => (a.parent === b.parent ? 1 : 1.2));

const treeData = treeLayout(root);
```

**Separation logic**:
- Siblings (same parent): `1.0` spacing unit
- Cousins (different parents): `1.2` spacing unit

### Step 3: Extract Positions

```typescript
const nodes: LayoutNode[] = [];
treeData.each((node) => {
  nodes.push({
    branch: node.data.branch,
    x: node.x + PADDING,
    y: node.y + PADDING,
  });
});
```

### Step 4: Generate Angular Paths

```typescript
const midY = (source.y + target.y) / 2;
const path = `
  M ${source.x} ${source.y}      // Move to source
  L ${source.x} ${midY}           // Vertical line to midpoint
  L ${target.x} ${midY}           // Horizontal line to target column
  L ${target.x} ${target.y}       // Vertical line to target
`;
```

**Result**: L-shaped path with right angles.

---

## Color Palette (Brutalist)

```css
/* Dark background */
--brutalist-bg: #0a0a0a

/* Surface elements (nodes, panels) */
--brutalist-surface: #141414

/* Borders and inactive lines */
--brutalist-border: #333

/* Active elements (current branch) */
--brutalist-accent: #fff

/* Primary text */
--brutalist-text: #e0e0e0

/* Secondary text (turn counts, meta) */
--brutalist-text-dim: #888

/* Danger actions (delete) */
--brutalist-danger: #ff4444
```

---

## Interaction Flow

### Click to Switch Branch

```
User clicks "explore" node
  ↓
onNodeClick(branch)
  ↓
onSwitchBranch(branch.id)
  ↓
setCurrentBranch(branch.id)
  ↓
Re-render with new active branch
  ↓
"explore" node gets white fill + glow
```

### Right-click to Merge

```
User right-clicks "refactor" node
  ↓
onNodeRightClick(e, branch)
  ↓
setContextMenu({ x, y, branchId })
  ↓
Context menu appears at cursor
  ↓
User clicks "Merge (Sequential)"
  ↓
handleMerge(branchId, 'sequential')
  ↓
onMergeBranch(branchId, strategy)
  ↓
Backend: POST /api/chat/{branch_id}/merge
  ↓
Re-fetch branches
  ↓
"refactor" marked as merged (dashed outline)
```

### Hover to Preview

```
User hovers "cache" node
  ↓
onNodeHover(e, branch)
  ↓
setTooltip({ x, y, branch })
  ↓
Tooltip appears at cursor + offset
  ↓
User moves mouse away
  ↓
onNodeLeave()
  ↓
setTooltip(null)
```

---

## Responsive Behavior

### Desktop (> 640px)

- Full labels and turn counts
- Wide spacing (120px between nodes)
- Tall levels (100px height)
- All features enabled

### Mobile (< 640px)

- Compact mode auto-enabled
- Smaller nodes (10px)
- Reduced spacing (80px)
- Hide branch count badge
- Max height: 200px (scrollable)

---

## Performance Characteristics

### Layout Computation

**Time Complexity**:
- D3 tree layout: `O(n)` where `n` = number of branches
- Path generation: `O(n-1)` for edges
- **Total**: `O(n)` — scales linearly

**Space Complexity**:
- `O(n)` for nodes
- `O(n-1)` for edges
- **Total**: `O(n)`

**Typical Performance**:
- 3 branches: ~1-2ms to compute layout
- 10 branches: ~3-5ms
- 100 branches: ~30-50ms

### Rendering

**SVG Rendering**:
- Browser-native (no canvas overhead)
- Hardware-accelerated transforms
- Efficient repaints (only changed nodes)

**React Reconciliation**:
- Keys on nodes/edges prevent unnecessary re-renders
- `React.memo()` on tooltip/context menu

---

## Edge Cases

### Single Branch (No Fork Yet)

```
┌────────────────────────┐
│ BRANCH TREE     (1/3) ▲│
├────────────────────────┤
│                        │
│      ◼ main            │
│      (12 turns)        │
│                        │
│  No branches yet       │
└────────────────────────┘
```

### Max Branches Reached

```
┌────────────────────────────────────────────┐
│ BRANCH TREE                         (3/3) ▲│
├────────────────────────────────────────────┤
│ ◆ Maximum 3 branches. Merge or archive    │
│   to fork again.                           │
├────────────────────────────────────────────┤
│           ◼ main (12 turns)                │
│           │                                │
│    ┌──────┼──────┐                         │
│    │      │      │                         │
│   ◻a     ◻b     ◻c                         │
└────────────────────────────────────────────┘
```

### Deep Nesting (Recursive Forks)

```
◼ main
│
└─ ◻ feature-a
   │
   └─ ◻ bugfix-a1
      │
      └─ ◻ hotfix-a1b
```

**D3 handles automatically** — tree layout adjusts height.

---

## Accessibility Details

### Screen Reader Announcements

```html
<g
  role="button"
  tabIndex={0}
  aria-label="Branch: explore-auth (3 turns)"
  aria-pressed={isActive}
>
  <!-- node contents -->
</g>
```

**Announced as**:
> "Branch: explore-auth, 3 turns. Button. Not pressed."

When active:
> "Branch: main, 12 turns. Button. Pressed."

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Focus next node |
| `Shift+Tab` | Focus previous node |
| `Enter` / `Space` | Switch to focused branch |
| `Esc` | Close context menu |
| `?` | Show help panel (global) |

### Focus Ring

```css
.branch-node:focus-visible {
  outline: 2px solid var(--brutalist-accent);
  outline-offset: 0;
}
```

**Visual**: White rectangle around focused node.

---

## Testing Checklist

### Visual Tests

- [ ] Square nodes (not circles)
- [ ] Angular paths (not curved)
- [ ] Glow only on active branch
- [ ] No glow on hover
- [ ] Dashed outline on merged branches
- [ ] Context menu positioned at cursor
- [ ] Tooltip follows cursor

### Interaction Tests

- [ ] Click node switches branch
- [ ] Right-click opens context menu
- [ ] Hover shows tooltip
- [ ] Tab focuses nodes
- [ ] Enter activates focused node
- [ ] Esc closes context menu

### Layout Tests

- [ ] Tree centers in viewport
- [ ] Scrollable when too large
- [ ] Compact mode reduces size
- [ ] Labels hidden in compact mode
- [ ] Responsive to container resize

### State Tests

- [ ] Active branch has white fill
- [ ] Inactive branches have dark fill
- [ ] Merged branches have dashed outline
- [ ] Warning shows at 3/3 branches
- [ ] Count badge updates on fork/merge

---

*"90% steel, 10% earned glow. The graph shows only what has been earned."*
