# Mode Transition Diagram

```
                                 ┌──────────┐
                                 │  NORMAL  │ ◄──── Escape (from any mode)
                                 │  (Steel) │
                                 └────┬─────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              │ i                     │ v                     │ e
              ▼                       ▼                       ▼
        ┌──────────┐            ┌──────────┐           ┌──────────┐
        │  INSERT  │            │  VISUAL  │           │   EDGE   │
        │  (Moss)  │            │  (Sage)  │           │ (Amber)  │
        └──────────┘            └──────────┘           └──────────┘
              │                       │                       │
              └───────────────────────┴───────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              │ :                     │ w                     │
              ▼                       ▼                       │
        ┌──────────┐            ┌──────────┐                 │
        │ COMMAND  │            │ WITNESS  │                 │
        │  (Rust)  │            │  (Gold)  │                 │
        └──────────┘            └──────────┘                 │
              │                       │                       │
              └───────────────────────┴───────────────────────┘
                                      │
                                      │ Esc
                                      ▼
                                 ┌──────────┐
                                 │  NORMAL  │
                                 └──────────┘
```

## Keybinding Matrix

| From Mode | Key | To Mode | Description |
|-----------|-----|---------|-------------|
| NORMAL | `i` | INSERT | Create new K-Blocks |
| NORMAL | `v` | VISUAL | Multi-select for batch ops |
| NORMAL | `e` | EDGE | Create relationships |
| NORMAL | `:` | COMMAND | Execute slash commands |
| NORMAL | `w` | WITNESS | Commit with witness mark |
| ANY | `Esc` | NORMAL | Return to NORMAL (N-03) |

## Navigation in NORMAL Mode

| Key | Action | Description |
|-----|--------|-------------|
| `j` / `↓` | Scroll down | N-01: j primary, arrow alias |
| `k` / `↑` | Scroll up | N-01: k primary, arrow alias |
| `{` | Scroll up paragraph | Jump to previous paragraph |
| `}` | Scroll down paragraph | Jump to next paragraph |
| `g` `g` | Scroll to top | Go to document top |
| `G` | Scroll to bottom | Go to document bottom |

## Mode-Specific Features

### NORMAL Mode
- **Color**: Steel (#475569)
- **Navigation**: j/k, arrows, g-prefix, z-prefix
- **Captures Input**: No
- **Blocks Navigation**: No

### INSERT Mode
- **Color**: Moss (#2E4A2E)
- **Purpose**: Create K-Blocks
- **Captures Input**: Yes (for K-Block content)
- **Blocks Navigation**: No

### EDGE Mode
- **Color**: Amber (#D4A574)
- **Purpose**: Create relationships
- **Captures Input**: Partially (edge type selection)
- **Blocks Navigation**: No

### VISUAL Mode
- **Color**: Sage (#4A6B4A)
- **Purpose**: Multi-select, comparison
- **Captures Input**: No
- **Blocks Navigation**: No

### COMMAND Mode
- **Color**: Rust (#8B5A2B)
- **Purpose**: Slash commands
- **Captures Input**: Yes (command text)
- **Blocks Navigation**: No

### WITNESS Mode
- **Color**: Gold (#E8C4A0)
- **Purpose**: Commit with marks
- **Captures Input**: Yes (witness message)
- **Blocks Navigation**: Yes

## Law Compliance

### N-01: Home-Row Primary Arrow Alias ✅
Both `j` and `ArrowDown` perform the same action. Home-row keys are primary, arrows are friendly aliases.

### N-03: Mode Return to NORMAL ✅
`Escape` key ALWAYS returns to NORMAL mode, from any mode, at any time. This is enforced globally by ModeProvider.

## Visual Feedback

The ModeIndicator (bottom-left pill) shows:
1. **Background color** - Mode-specific (Living Earth palette)
2. **Label** - Mode name in uppercase
3. **Description** - Short description of current mode
4. **Hint** - "Esc to exit" (when not in NORMAL)

## Transition Animations

- **Duration**: 300ms
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1)
- **Properties**: background-color, transform
- **Effects**: Subtle pulse on mode change

## History Tracking

The mode system tracks the last 10 mode transitions:
```typescript
{
  from: 'NORMAL',
  to: 'INSERT',
  timestamp: 1735146000000,
  reason: 'keyboard:i'
}
```

Access via `useMode().history`
