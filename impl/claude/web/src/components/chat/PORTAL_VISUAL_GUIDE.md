# ChatPortal Visual Guide

**Design Pattern**: "The doc comes to you"

---

## Component States

### 1. Collapsed (Default)
```
┌────────────────────────────────────────────────────────┐
│ ▶ [references] ──→ spec/protocols/witness.md      ↗ │
├────────────────────────────────────────────────────────┤
│ 42 lines · read                                        │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Steel-carbon background (`#141418`)
- Life-mint icon (`#6b8b6b`)
- Collapsed arrow `▶`
- Navigate button `↗` on hover

---

### 2. Expanded (Read Mode)
```
┌────────────────────────────────────────────────────────┐
│ ▼ [references] ──→ spec/protocols/witness.md      ↗ │
├────────────────────────────────────────────────────────┤
│ 42 lines · read · auto-expanded                        │
├────────────────────────────────────────────────────────┤
│ Witness Protocol                                       │
│ ================                                       │
│                                                        │
│ The witness protocol enables...                       │
│                                                        │
│ ## Core Concepts                                       │
│                                                        │
│ 1. **Evidence**: Traces of computation                │
│ 2. **Marks**: Witnessed decisions                     │
│ 3. **Crystals**: Compressed knowledge                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Life-sage border (`rgba(74, 107, 74, 0.5)`)
- Steel-slate header (`#1c1c22`)
- Expanded arrow `▼`
- Monospaced code font

---

### 3. Edit Mode (Readwrite)
```
┌────────────────────────────────────────────────────────┐
│ ▼ [modifies] ──→ impl/...cortex.py             ↗ ✎  │
├────────────────────────────────────────────────────────┤
│ 15 lines · readwrite                                   │
├────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────┐   │
│ │ class CortexObserver:                            │   │
│ │     """Observes cortex activity."""             │   │
│ │                                                  │   │
│ │     def __init__(self):                         │   │
│ │         self.observers = []                     │   │
│ │         |  ← cursor here                        │   │
│ └──────────────────────────────────────────────────┘   │
│                                                        │
│ [Save] [Cancel]                         Cmd+Enter save │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- **Glow-spore border** (`rgba(196, 167, 125, 0.6)`) — EARNED STATE
- Box shadow glow (`0 0 12px rgba(196, 167, 125, 0.2)`)
- Edit button `✎` in header
- Save/Cancel buttons (life-sage for save)
- Keyboard hint in footer

---

### 4. Saving State
```
┌────────────────────────────────────────────────────────┐
│ ▼ [modifies] ──→ impl/...cortex.py          ↗ ✎ ◐  │
│                                                    ↑   │
│                                              pulsing   │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Sync status: `◐` (pulsing animation)
- Muted cyan color (`#7faaaa`)

---

### 5. Saved State
```
┌────────────────────────────────────────────────────────┐
│ ▼ [modifies] ──→ impl/...cortex.py          ↗ ✎ ✓  │
│                                                    ↑   │
│                                               saved   │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Sync status: `✓` (checkmark)
- Life-mint color (`#8bc48b`)
- Auto-fades to idle after 2 seconds

---

### 6. Failed State
```
┌────────────────────────────────────────────────────────┐
│ ▼ [modifies] ──→ impl/...cortex.py          ↗ ✎ ⚠️ │
│                                                    ↑   │
│                                         Network error  │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Sync status: `⚠️` (warning)
- Muted rust color (`#a65d4a`)
- Error message shown

---

### 7. Missing File
```
┌────────────────────────────────────────────────────────┐
│ ▶ [references] ──→ spec/protocols/not-found.md        │
├────────────────────────────────────────────────────────┤
│ 0 lines · read · file missing                          │
└────────────────────────────────────────────────────────┘
```

**Visual Traits**:
- Rust border (`rgba(166, 93, 74, 0.4)`)
- Warning badge: "file missing"
- Reduced opacity (0.8)
- No expand affordance (can't show what doesn't exist)

---

## Interaction Flows

### Flow 1: Read → Navigate
```
1. User sees collapsed portal
2. Clicks ▶ to expand
3. Reads content inline
4. Clicks ↗ to open in editor
   → Navigates to file
```

### Flow 2: Read → Edit → Save
```
1. User sees collapsed portal (readwrite)
2. Clicks ▶ to expand
3. Clicks ✎ to edit
   → Textarea appears with content
4. User edits content
5. Presses Cmd+Enter (or clicks Save)
   → Status shows ◐ (saving)
   → Status shows ✓ (saved)
   → Edit mode closes
```

### Flow 3: Read → Edit → Cancel
```
1. User sees collapsed portal (readwrite)
2. Clicks ▶ to expand
3. Clicks ✎ to edit
   → Textarea appears with content
4. User edits content
5. Presses Esc (or clicks Cancel)
   → Changes discarded
   → Edit mode closes
```

---

## Color Palette

### STARK BIOME
| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Background | Steel-carbon | `#141418` | Portal body |
| Border (default) | Steel-gunmetal | `#28282f` | Collapsed state |
| Border (expanded) | Life-sage | `rgba(74, 107, 74, 0.5)` | Expanded state |
| Border (editing) | Glow-spore | `rgba(196, 167, 125, 0.6)` | Edit mode |
| Border (missing) | Rust | `rgba(166, 93, 74, 0.4)` | Missing file |
| Text (header) | Foreground | `rgb(180 180 190)` | Headers |
| Text (code) | Foreground | `rgb(180 180 190)` | Code content |
| Accent (edge type) | Life-mint | `#6b8b6b` | Edge type label |
| Accent (arrow) | Steel-zinc | `#3a3a44` | Arrow separator |
| Success (saved) | Life-mint | `#8bc48b` | Checkmark |
| Warning (failed) | Rust | `#a65d4a` | Error icon |
| Loading (saving) | Cyan | `#7faaaa` | Pulse animation |

---

## Typography

### Fonts
- **Monospace**: `'JetBrains Mono', 'Berkeley Mono', monospace`
- **Size**: `0.85em` for code, `0.9em` for labels

### Line Height
- **Code**: `1.6` (readable, matches docs)
- **Headers**: `1.3` (compact)

---

## Spacing

### Brutalist Philosophy
- **No rounded corners** (`border-radius: 0`)
- **Sharp edges** (rectangular containers)
- **Minimal padding** (`0.5em - 0.75em`)
- **Tight gaps** (`0.5em` between elements)

### Layout Grid
```
Margin: 0.75em (vertical between portals)
Padding: 0.6em - 0.75em (header/content)
Gap: 0.5em (between header elements)
```

---

## Responsive Behavior

### Mobile (<768px)
```
┌─────────────────────────┐
│ ▶ [references] ──→      │
│ spec/protocols/...      │
├─────────────────────────┤
│               ↗ ✎      │
├─────────────────────────┤
│ 42 lines · read         │
└─────────────────────────┘
```

**Changes**:
- Header wraps (toggle full width, actions below)
- Metadata wraps
- Code font smaller (`0.8em`)
- Keyboard hint hidden

---

## Accessibility

### Keyboard Navigation
| Key | Action |
|-----|--------|
| `Space` / `Enter` | Toggle expand |
| `Tab` | Navigate to actions |
| `Enter` | Activate button |
| `Cmd+Enter` | Save (in edit mode) |
| `Esc` | Cancel (in edit mode) |

### ARIA
- `aria-expanded` on toggle button
- `title` attributes on all buttons
- `disabled` state for saving operations

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  /* Disable animations */
  transition: none;
}
```

---

## Summary

**Visual Language**: Brutalist + STARK BIOME
**90% Steel**: Frames, backgrounds, structural elements
**10% Life**: Accents, interactive elements, success states
**Earned Glow**: Edit mode gets golden spore border
**Philosophy**: "The doc comes to you" — content inline, zero navigation
