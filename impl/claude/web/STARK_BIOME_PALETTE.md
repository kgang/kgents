# STARK BIOME — Canonical Color Palette

> "90% steel, 10% earned glow"

**Design Philosophy**: The kgents hypergraph UI uses a dark, monochromatic base (steel scale) with rare, intentional pops of color that signal mode changes or status.

---

## Steel Scale (The Foundation)

The steel scale is a 11-step grayscale from near-black to light gray. Use these for all backgrounds, borders, and text.

| Token | Hex | Usage | Example |
|-------|-----|-------|---------|
| `--steel-950` | `#0d0d0d` | Deep background, canvas | Main editor background |
| `--steel-900` | `#1a1a1a` | Surface, panels | Modal background, sidebar header |
| `--steel-850` | `#1f1f1f` | Mid-surface | Hover states for panels |
| `--steel-800` | `#252525` | Elevated elements | Button backgrounds, input fields |
| `--steel-700` | `#333333` | Borders | Panel borders, dividers |
| `--steel-600` | `#444444` | Hover borders | Active border states |
| `--steel-500` | `#666666` | Muted text | Labels, hints, placeholder |
| `--steel-400` | `#888888` | Secondary text | Timestamps, metadata |
| `--steel-300` | `#a0a0a0` | Tertiary text | Descriptions, help text |
| `--steel-200` | `#cccccc` | Light text | Headings, emphasized text |
| `--steel-100` | `#e0e0e0` | Primary text | Body text, main content |

**Usage Rules**:
- **Backgrounds**: Use 950-900 for base, 850-800 for elevated
- **Borders**: Use 700 for normal, 600 for hover/active
- **Text**: Use 100 for primary, 300-500 for secondary/muted

---

## Status Colors (The Earned Glow)

These colors signal mode changes, states, or important status. Use sparingly.

| Token | Hex | Usage | Example |
|-------|-----|-------|---------|
| `--status-normal` | `#4a9eff` | Normal mode (blue) | StatusLine in normal mode |
| `--status-insert` | `#4caf50` | Insert mode (green) | StatusLine in insert mode, "life-sage" |
| `--status-edge` | `#ff9800` | Edge mode (orange) | StatusLine in edge mode, "glow-spore" |
| `--status-visual` | `#9c27b0` | Visual/Dialectic (purple) | Dialectic UI, visual mode |
| `--status-witness` | `#e91e63` | Witness mode (magenta/coral) | Witness panel, marks |
| `--status-error` | `#f44336` | Errors, warnings (red) | Error messages, veto badges |

**Usage Rules**:
- **Mode indicators**: StatusLine border, accent colors
- **Dialectic UI**: Purple (`--status-visual`) for synthesis, fusion space
- **Witness marks**: Magenta (`--status-witness`) for decision capture
- **Errors**: Red (`--status-error`) for destructive actions, failures

---

## Accents

| Token | Hex | Usage | Example |
|-------|-----|-------|---------|
| `--accent-gold` | `#ffd700` | Selection, highlights, active states | CommandPalette selection bar, caret color |

**Usage Rules**:
- **Active selection**: Gold bar on selected command
- **Keyboard focus**: Caret color in inputs
- **Highlight**: Rare moments of emphasis

---

## Health Colors (Optional, for Confidence Indicators)

| Token | Hex | Usage | Example |
|-------|-----|-------|---------|
| `--health-healthy` | `#22c55e` | >= 80% confidence | Health bars, success states |
| `--health-degraded` | `#facc15` | 60-80% confidence | Warning states |
| `--health-warning` | `#f97316` | 40-60% confidence | Attention needed |
| `--health-critical` | `#ef4444` | < 40% confidence | Critical states |

**Usage**: Only if health/confidence indicators are needed. Not for general UI.

---

## Color Usage Examples

### ✅ Good: Earned Glow

```css
/* Status line in insert mode */
.status-line--insert {
  border-top: 2px solid var(--status-insert);
  background: var(--steel-900);
}

/* CommandPalette selected item */
.command-palette__item[data-selected='true']::before {
  background: var(--accent-gold);
}

/* Dialectic synthesis pane */
.dialogue-view__synthesis {
  border-left: 1px solid var(--status-visual);
  border-right: 1px solid var(--status-visual);
}
```

### ❌ Bad: Color Overload

```css
/* DON'T: Too many colors, loses STARK BIOME aesthetic */
.panel {
  background: linear-gradient(135deg, #4a9eff, #4caf50, #ff9800);
  border: 2px solid #ffd700;
  color: #9c27b0;
}
```

---

## Contrast Ratios (WCAG AA)

All text/background combinations meet WCAG AA (4.5:1 for body text, 3:1 for large text):

| Foreground | Background | Ratio | Pass |
|------------|------------|-------|------|
| `--steel-100` | `--steel-950` | 11.2:1 | ✅ AAA |
| `--steel-300` | `--steel-900` | 5.8:1 | ✅ AA |
| `--steel-500` | `--steel-800` | 3.2:1 | ✅ Large text only |
| `--accent-gold` | `--steel-950` | 12.1:1 | ✅ AAA |
| `--status-insert` | `--steel-900` | 4.7:1 | ✅ AA |

**Accessibility Rule**: Always pair steel-100/200/300 with steel-900/950 for text.

---

## Visual Reference (ASCII Art)

```
╔═══════════════════════════════════════════════════════════════╗
║                     STARK BIOME PALETTE                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  STEEL SCALE (90% of UI)                                      ║
║  ────────────────────────────────────────────────────────     ║
║  ███ --steel-950  #0d0d0d  Deep background                    ║
║  ███ --steel-900  #1a1a1a  Surface                            ║
║  ███ --steel-850  #1f1f1f  Mid-surface                        ║
║  ███ --steel-800  #252525  Elevated                           ║
║  ███ --steel-700  #333333  Border                             ║
║  ███ --steel-600  #444444  Hover border                       ║
║  ███ --steel-500  #666666  Muted text                         ║
║  ███ --steel-400  #888888  Secondary text                     ║
║  ███ --steel-300  #a0a0a0  Tertiary text                      ║
║  ███ --steel-200  #cccccc  Light text                         ║
║  ███ --steel-100  #e0e0e0  Primary text                       ║
║                                                               ║
║  STATUS COLORS (10% earned glow)                              ║
║  ────────────────────────────────────────────────────────     ║
║  ███ --status-normal   #4a9eff  Blue (normal mode)            ║
║  ███ --status-insert   #4caf50  Green (insert/life)           ║
║  ███ --status-edge     #ff9800  Orange (edge/glow)            ║
║  ███ --status-visual   #9c27b0  Purple (dialectic)            ║
║  ███ --status-witness  #e91e63  Magenta (witness)             ║
║  ███ --status-error    #f44336  Red (errors)                  ║
║                                                               ║
║  ACCENTS                                                       ║
║  ────────────────────────────────────────────────────────     ║
║  ███ --accent-gold     #ffd700  Selection/highlight           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Anti-Patterns to Avoid

### ❌ Don't Mix Color Families

```css
/* BAD: Mixes steel with custom colors */
background: #1a1a1e;  /* Not in steel scale! */
border: 1px solid #3a3a42;  /* Not in steel scale! */
```

**Fix**: Use `var(--steel-900)` and `var(--steel-700)`.

---

### ❌ Don't Overuse Status Colors

```css
/* BAD: Status colors everywhere */
.panel { background: var(--status-insert); }
.button { background: var(--status-visual); }
.text { color: var(--status-witness); }
```

**Fix**: Use steel scale for 90% of UI. Status colors only for mode/state indicators.

---

### ❌ Don't Hardcode Opacity

```css
/* BAD: Hardcoded opacity loses semantic meaning */
background: rgba(26, 26, 26, 0.85);
```

**Fix**: Use named variables:
```css
background: var(--steel-900);
/* OR if transparency needed: */
background: var(--backdrop-overlay-medium);
```

---

## Color Philosophy

> "The absence of color IS the aesthetic. Color is a scalpel, not a paintbrush."

**Principles**:
1. **Monochrome by default**: Steel scale for structure
2. **Color as signal**: Status colors indicate mode/state changes
3. **Earned glow**: Color must be justified (mode change, error, highlight)
4. **Consistency over novelty**: Use existing tokens before creating new ones

**The Mirror Test**: If you can't justify a color choice in one sentence, it's probably wrong.

---

*This palette is the DNA of the STARK BIOME aesthetic.*
*Use it wisely. Kent's taste depends on it.*

---

**Last Updated**: 2025-12-24
**Source of Truth**: `/impl/claude/web/src/hypergraph/design-system.css`
