# ChatSidebar — Visual Design Guide

> "90% steel, 10% earned glow"

## Layout States

### Open State (320px wide)

```
┌────────────────────────────────┐
│ ┌────┐                         │ ← Toggle button (40px)
│ │ ▸  │  Chat         Ctrl+J    │ ← Header (48px)
│ └────┘─────────────────────────│
│                                │
│  ◇ You:                        │
│  How do I implement X?         │
│                                │
│  ◇ Claude:                     │
│  To implement X, you can...    │ ← Message list (flex: 1)
│                                │
│  ⚠️ File write detected        │ ← Mutation (if any)
│     Acknowledge ✓              │
│                                │
│ ┌────────────────────────────┐ │
│ │ Type message...       Send │ │ ← Input (always visible)
│ └────────────────────────────┘ │
└────────────────────────────────┘
```

### Collapsed State (40px wide)

```
┌────┐
│ ◂  │ ← Toggle icon
│    │
│ C  │
│ h  │ ← Vertical label
│ a  │
│ t  │
│    │
│ •  │ ← Unread indicator (if unread)
│    │
│ ─  │
│ │  │
│ C  │ ← "Ctrl+J" hint (on hover)
│ t  │
│ r  │
│ l  │
│ +  │
│ J  │
│ │  │
│ ─  │
└────┘
```

### Collapsed with Unread

```
┌────┐
│ ◂  │
│    │
│ 🔴 │ ← Red dot (pulsing)
│    │
│ C  │
│ h  │
│ a  │
│ t  │
└────┘
```

## Color Palette

```css
/* Background */
--steel-950: #0a0a0a    /* Main background */
--steel-900: #18181b    /* Elevated surfaces */

/* Borders */
--steel-800: #27272a    /* Primary borders */
--steel-700: #3f3f46    /* Secondary borders */

/* Text */
--steel-100: #f4f4f5    /* Active text */
--steel-300: #d4d4d8    /* Primary text */
--steel-400: #a1a1aa    /* Muted text */
--steel-500: #71717a    /* Disabled text */

/* Indicators */
--error-500: #ef4444    /* Unread dot */
--focus-ring: #3b82f6   /* Focus glow */
--success-500: #22c55e  /* Success glow */
```

## Glow Animations

### Focus Glow (Earned)

```
Input at rest         Input focused
┌──────────────┐     ┌──────────────┐
│              │     │░░░░░░░░░░░░░░│ ← Blue glow (8px, 15% opacity)
│ Type here... │  →  │ Type here|   │
│              │     │░░░░░░░░░░░░░░│
└──────────────┘     └──────────────┘
```

### Success Glow (Earned)

```
Message sent
┌──────────────┐
│░░░░░░░░░░░░░░│ ← Green flash (0.6s)
│ Sent ✓       │    Starts at 30% opacity
│░░░░░░░░░░░░░░│    Fades to 15%
└──────────────┘
```

### Unread Pulse (Subtle)

```
Frame 1        Frame 2        Frame 3
  🔴     →      🔴      →      🔴
100% opacity   60% opacity    100% opacity
(2s cycle, ease-in-out)
```

## Spacing Scale

```
Compact Mode (sidebar):
- Messages padding: 6px
- Context padding: 4px 8px
- Mutations gap: 2px
- Header padding: 12px 16px

Default Mode (full):
- Messages padding: 8px
- Context padding: 6px 8px
- Mutations gap: 4px
- Header padding: 12px 16px
```

## Typography

```css
/* Header */
.workspace__sidebar-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Shortcut hint */
.workspace__sidebar-shortcut {
  font-size: 11px;
  font-family: monospace;
}

/* Messages */
.chat-panel {
  font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
}

/* Collapsed label */
.workspace__sidebar-toggle-label {
  font-size: 11px;
  writing-mode: vertical-rl;
  letter-spacing: 0.05em;
}
```

## Interactive States

### Toggle Button

```
Rest              Hover             Focused
┌────┐           ┌────┐            ┌────┐
│ ◂  │    →      │ ◂  │     →      │║◂ ║│ ← Focus ring (2px blue)
│    │           │▓▓▓▓│            │║  ║│
└────┘           └────┘            └────┘
steel-400        steel-100         focus-ring
transparent      steel-900         outline
```

### Unread Dot

```
No unread      Has unread       Clicked
              ┌────┐
   ─          │ ◂  │            ─
              │ 🔴 │     →
   ─          └────┘            ─

(appears)    (pulsing)      (disappears)
```

## Responsive Breakpoints

### Desktop (>1024px)

```
┌─────────┬──────────────┬────────┐
│ Files   │ Graph        │ Chat   │
│ (280px) │ (flex: 1)    │ (360px)│
└─────────┴──────────────┴────────┘
```

### Tablet (768-1024px)

```
┌─────────────────────┬────────┐
│ Graph (flex: 1)     │ Chat   │
│                     │ overlay│
└─────────────────────┴────────┘
(Files becomes overlay on left)
```

### Mobile (<768px)

```
┌─────────────────────┐
│ Graph (flex: 1)     │
│                     │
│                     │
└─────────────────────┘
(Chat overlay full width)
```

## Animation Curves

```css
/* Sidebar open/close */
transition: width 0.2s ease;

/* Glow appearance */
transition: box-shadow 0.2s ease, border-color 0.2s ease;

/* Success flash */
animation: success-flash 0.6s ease-out;

/* Unread pulse */
animation: pulse-subtle 2s ease-in-out infinite;
```

## Component Hierarchy

```
Workspace
├── Left Sidebar (Files)
│   ├── Toggle Button
│   ├── Header
│   └── FileExplorer
│
├── Center (Graph Editor)
│   └── HypergraphEditor
│
└── Right Sidebar (Chat)
    ├── Toggle Button
    │   └── Unread Indicator (if unread)
    ├── Header
    └── ChatSidebar
        ├── Unread Badge (duplicate, internal)
        └── ChatPanel (compact=true)
            ├── Message List
            ├── Mutation Acknowledgment
            └── Input Area
```

## Edge Cases

### Long Message Scrolling

```
┌────────────────────────────────┐
│ Chat         Ctrl+J            │
│────────────────────────────────│
│ Long message continues...      │
│ ...more content...             ↑
│ ...keeps scrolling...          │ Scrollbar
│ ...until...                    ↓
│ ...end of message.             │
│                                │
│ Type message...                │
└────────────────────────────────┘
```

### Multiple Mutations

```
┌────────────────────────────────┐
│ Messages...                    │
├────────────────────────────────┤
│ ⚠️ File write: foo.ts          │
│    Acknowledge ✓               │
├────────────────────────────────┤
│ ⚠️ File write: bar.ts          │
│    Acknowledge ✓               │
├────────────────────────────────┤
│ Type message...                │
└────────────────────────────────┘
```

### Empty State

```
┌────────────────────────────────┐
│ Chat         Ctrl+J            │
│────────────────────────────────│
│                                │
│            ◇                   │
│                                │
│     Start a conversation       │
│                                │
│                                │
│                                │
│ Type message...                │
└────────────────────────────────┘
```

## Accessibility Annotations

```
┌────────────────────────────────┐
│ <aside aria-label="Chat">     │
│   <button aria-expanded="true" │
│           title="Close (Ctrl+J)"│
│   >                            │
│     <span aria-hidden="true">  │ ← Toggle icon
│       ▸                        │
│     </span>                    │
│     <span aria-label="Unread"> │ ← Unread (if any)
│       •                        │
│     </span>                    │
│   </button>                    │
│                                │
│   <ChatPanel ... />            │
│ </aside>                       │
└────────────────────────────────┘
```

## Testing Checklist

Visual regression tests to capture:

- [ ] Open state (with messages)
- [ ] Collapsed state (no unread)
- [ ] Collapsed state (with unread)
- [ ] Focus glow on input
- [ ] Success glow after send
- [ ] Mutation acknowledgment
- [ ] Empty state
- [ ] Long message scrolling
- [ ] Mobile overlay
- [ ] Reduced motion (no animations)

---

**Design Status**: Production-ready
**Follows**: UX-LAWS.md ("90% steel, 10% earned glow")
**Updated**: 2025-12-25
