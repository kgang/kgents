# Collapsed Sidebar Pattern

**Status**: Canonical Pattern (2025-12-25)

## Philosophy

"The collapsed sidebar is not an accident—it's an intentional UI state that deserves the same care as the expanded state."

## Problem Statement

Collapsible sidebars with vertical text labels (using `writing-mode: vertical-rl`) face a common issue:

1. **Too narrow** → Label gets cut off by `overflow: hidden`
2. **No overflow control** → Label escapes container bounds
3. **Inconsistent widths** → Different collapsed states across the app

## The Canonical Pattern

### Container (`.sidebar--collapsed`)

```css
.sidebar--collapsed {
  width: 40px;           /* Fixed width - sufficient for vertical text */
  min-width: 40px;       /* Prevent flexbox shrinking */
  overflow: hidden;      /* CRITICAL: Prevents content escape */
}

.sidebar--collapsed .sidebar__content {
  opacity: 0;            /* Hide main content */
  pointer-events: none;  /* Disable interactions */
}
```

### Toggle Button (`.sidebar__toggle`)

```css
.sidebar__toggle {
  position: absolute;    /* Remove from normal flow */
  top: 0;
  left: 0;               /* Or right: 0 for right-side panels */
  width: 40px;           /* Match collapsed container width */
  height: 100%;          /* Full height clickable area */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  z-index: 10;           /* Above content */
  transition: color 0.15s ease, background-color 0.15s ease;
}

.sidebar__toggle:hover {
  background: var(--subtle-hover-bg);
}
```

### Label (`.sidebar__toggle-label`)

```css
.sidebar__toggle-label {
  writing-mode: vertical-rl;  /* Vertical text */
  text-orientation: mixed;    /* Natural orientation */
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  opacity: 0.7;               /* Subtle when expanded */
}

/* More prominent when collapsed */
.sidebar--collapsed .sidebar__toggle-label {
  opacity: 1;
}
```

### Content Padding (Account for Toggle Button)

```css
.sidebar__content {
  padding: 0.75rem;
  padding-left: calc(40px + 0.75rem);  /* Account for toggle button */
  transition: opacity 0.15s ease;
}
```

## Implementation Checklist

When creating a new collapsible sidebar:

- [ ] Container has **40px** collapsed width
- [ ] Container has `overflow: hidden`
- [ ] Toggle button is **absolutely positioned**
- [ ] Toggle button is **40px wide**
- [ ] Label uses `writing-mode: vertical-rl`
- [ ] Content has padding to account for toggle button width
- [ ] Collapsed state hides content with `opacity: 0` and `pointer-events: none`
- [ ] Focus states are keyboard-accessible (`focus-visible`)
- [ ] Hover states provide visual feedback

## Current Implementations

### ✅ Workspace Sidebars (`Workspace.tsx`, `Workspace.css`)

- **Left sidebar**: Files panel
- **Right sidebar**: Chat panel
- **Pattern**: Original canonical implementation

### ✅ ProofPanel (`ProofPanel.tsx`, `ProofPanel.css`)

- **Location**: Right sidebar in HypergraphEditor
- **Pattern**: Updated to match Workspace pattern (2025-12-25)
- **Changes**:
  - Width: 32px → 40px
  - Toggle button: Absolute positioning
  - Content padding: Added left padding for toggle button

## Why 40px?

Through iteration, we found:

- **32px**: Too narrow—vertical text feels cramped
- **40px**: Goldilocks—comfortable for uppercase labels with letter-spacing
- **48px+**: Too wide—wasteful of screen real estate

## Anti-Patterns (Avoid These)

❌ **Variable collapsed widths** across the app
❌ **Relying on `overflow: visible`** (breaks visual bounds)
❌ **Static positioning for toggle button** (harder to manage layout)
❌ **Missing focus states** (inaccessible to keyboard users)
❌ **Inconsistent transitions** (jarring UX)

## Future Sidebars

Any new collapsible sidebar MUST follow this pattern. No exceptions.

If you need a different pattern (e.g., bottom panel, horizontal collapse), document it here as a separate pattern.

---

**Lesson**: Consistency is earned through deliberate pattern enforcement, not emergent behavior.
