# Design Tokens Cheatsheet — Quick Reference

**For Developers**: Copy-paste these patterns when building kgents UI components.

---

## Color Variables

```css
/* Backgrounds */
background: var(--steel-950);  /* Deep canvas */
background: var(--steel-900);  /* Panels, modals */
background: var(--steel-800);  /* Buttons, inputs */

/* Borders */
border: 1px solid var(--steel-700);  /* Default */
border: 1px solid var(--steel-600);  /* Hover */

/* Text */
color: var(--steel-100);  /* Primary text */
color: var(--steel-400);  /* Secondary text (labels) */
color: var(--steel-500);  /* Muted text (placeholders) */

/* Status Colors (use sparingly!) */
border-top: 2px solid var(--status-insert);   /* Green mode indicator */
border-top: 2px solid var(--status-visual);   /* Purple dialectic */
background: var(--status-error);              /* Red error badge */

/* Accents */
background: var(--accent-gold);  /* Selection highlight */
caret-color: var(--accent-gold); /* Input caret */
```

---

## Typography

```css
/* Font Family */
font-family: var(--font-mono);  /* Use everywhere! */

/* Font Sizes */
font-size: var(--font-size-xs);  /* 10px — kbd, badges */
font-size: var(--font-size-sm);  /* 12px — labels */
font-size: var(--font-size-md);  /* 14px — body text */
font-size: var(--font-size-lg);  /* 16px — headings */

/* Line Heights */
line-height: var(--line-height-normal);   /* 1.5 — body */
line-height: var(--line-height-relaxed);  /* 1.7 — long form */
```

---

## Spacing

```css
/* Padding/Margin */
padding: var(--space-xs);   /* 4px — tight spacing */
padding: var(--space-sm);   /* 8px — compact */
padding: var(--space-md);   /* 16px — comfortable */
padding: var(--space-lg);   /* 24px — spacious */
padding: var(--space-xl);   /* 32px — generous */

/* Gaps */
gap: var(--space-sm);  /* Flexbox/Grid gaps */
```

---

## Border Radius

```css
/* Radius Scale */
border-radius: var(--radius-sm);    /* 2px — kbd, tight UI */
border-radius: var(--radius-md);    /* 4px — buttons, inputs */
border-radius: var(--radius-lg);    /* 6px — panels, cards */
border-radius: var(--radius-xl);    /* 8px — modals */
border-radius: var(--radius-pill);  /* 12px — tags, pills */
```

---

## Transitions & Animations

```css
/* Transition Durations */
transition: var(--transition-fast);    /* 0.15s — hover states */
transition: var(--transition-normal);  /* 0.2s — fade-ins */
transition: var(--transition-slow);    /* 0.3s — slide-ins */

/* Easing */
transition: transform var(--transition-slow); /* Uses cubic-bezier spring */

/* Fade-In Animation */
animation: fade-in var(--transition-normal) ease-out;

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

## Z-Index Layers

```css
/* Layer Hierarchy */
z-index: var(--z-base);      /* 0 — normal content */
z-index: var(--z-sidebar);   /* 100 — sidebars */
z-index: var(--z-panel);     /* 150 — temp overlays */
z-index: var(--z-overlay);   /* 200 — full-screen modals */
z-index: var(--z-modal);     /* 1000 — top-level UI */
```

**Rule**: Use named layers, never hardcoded numbers!

---

## Backdrop Effects

```css
/* Light Backdrop (temp panels, dialogs) */
background: var(--backdrop-overlay-medium);   /* rgba(0,0,0,0.75) */
backdrop-filter: var(--backdrop-blur-light);  /* blur(4px) */

/* Heavy Backdrop (command palette, major modals) */
background: var(--backdrop-overlay-heavy);    /* rgba(0,0,0,0.85) */
backdrop-filter: var(--backdrop-blur-heavy);  /* blur(8px) */
```

---

## Shadows

```css
/* Shadow Scale */
box-shadow: var(--shadow-sm);   /* 0 2px 8px — subtle */
box-shadow: var(--shadow-md);   /* 0 4px 16px — cards */
box-shadow: var(--shadow-lg);   /* 0 8px 32px — panels */
box-shadow: var(--shadow-xl);   /* 0 12px 48px — modals */
box-shadow: var(--shadow-2xl);  /* 0 16px 64px — command palette */
```

---

## Common Patterns

### Modal Overlay

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--backdrop-overlay-heavy);
  backdrop-filter: var(--backdrop-blur-heavy);
  z-index: var(--z-modal);
  animation: fade-in var(--transition-normal) ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

---

### Modal Dialog

```css
.modal-dialog {
  background: var(--steel-900);
  border: 2px solid var(--steel-700);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  padding: var(--space-lg);
  max-width: 640px;
  font-family: var(--font-mono);
  animation: slide-in var(--transition-slow);
}

@keyframes slide-in {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

---

### Button

```css
.button {
  padding: var(--space-sm) var(--space-md);
  background: var(--steel-800);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-md);
  color: var(--steel-100);
  font-family: var(--font-mono);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.button:hover {
  background: var(--steel-700);
  border-color: var(--steel-600);
}

.button:focus-visible {
  outline: 2px solid var(--accent-gold);
  outline-offset: 2px;
}

.button--primary {
  background: var(--status-visual);
  border-color: var(--status-visual);
  color: white;
  font-weight: 600;
}
```

---

### Input Field

**Philosophy**: Dark backgrounds ensure contrast with light text. Use semantic classes for consistent styling.

```css
/* Base input (use this everywhere!) */
.input-base {
  width: 100%;
  padding: var(--space-sm) var(--space-md);
  background: var(--steel-900);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-md);
  color: var(--steel-100);
  font-family: var(--font-mono);
  font-size: var(--font-size-md);
  line-height: var(--line-height-normal);
  transition: var(--transition-fast);
  caret-color: var(--accent-gold);
  outline: none;
}

.input-base:focus {
  border-color: var(--steel-600);
  background: var(--steel-800);
  box-shadow: 0 0 0 1px var(--steel-600);
}

.input-base::placeholder {
  color: var(--steel-500);
  opacity: 1;
}

.input-base:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--steel-850);
}
```

**Variants**:

```css
/* Inline (transparent background) - for command lines */
<input className="input-base input-inline" />

/* Accent (highlighted state) - for rename, special contexts */
<input className="input-base input-accent" />

/* Small (compact) - for search bars, filters */
<input className="input-base input-sm" />

/* Error state - for validation failures */
<input className="input-base input-error" />
```

**Usage Examples**:

```tsx
// Search bar
<input className="input-base input-sm" placeholder="Search..." />

// Rename input
<input className="input-base input-accent" value={newName} />

// Command line
<input className="input-base input-inline" />

// Error state
<input className="input-base input-error" placeholder="Required field" />
```

---

### Kbd Element

```css
/* Inherited from design-system.css global rule */
/* Just use <kbd>Enter</kbd> and styling is automatic! */

/* If you need to override: */
kbd {
  padding: 0.125rem 0.375rem;
  background: var(--steel-800);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--font-size-xs);
  color: var(--steel-300);
}
```

---

### Scrollbar

```css
/* Use class for consistent scrollbar styling */
.my-scrollable-container {
  overflow-y: auto;
}

.my-scrollable-container::-webkit-scrollbar {
  width: 8px;
}

.my-scrollable-container::-webkit-scrollbar-track {
  background: var(--steel-900);
}

.my-scrollable-container::-webkit-scrollbar-thumb {
  background: var(--steel-700);
  border-radius: var(--radius-md);
}

.my-scrollable-container::-webkit-scrollbar-thumb:hover {
  background: var(--steel-600);
}
```

---

### Tag/Badge

```css
.tag {
  padding: 0.25rem 0.625rem;
  background: var(--steel-800);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-pill);
  font-family: var(--font-mono);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--steel-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tag--selected {
  background: var(--status-visual);
  border-color: var(--status-visual);
  color: white;
}
```

---

### Panel/Card

```css
.panel {
  background: var(--steel-900);
  border: 1px solid var(--steel-800);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
}

.panel__header {
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--steel-800);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--steel-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.panel__content {
  padding-top: var(--space-md);
  font-size: var(--font-size-md);
  line-height: var(--line-height-normal);
  color: var(--steel-100);
}
```

---

## Performance Optimization

```css
/* For animated elements */
.will-animate {
  will-change: transform, opacity;
  transform: translateZ(0); /* Force GPU acceleration */
}

/* Apply to modals, sidebars, animated panels */
.modal-overlay,
.modal-dialog,
.sidebar {
  will-change: transform, opacity;
  transform: translateZ(0);
}
```

---

## Accessibility

```css
/* Focus visible (keyboard navigation) */
:focus-visible {
  outline: 2px solid var(--accent-gold);
  outline-offset: 2px;
}

/* High contrast for critical text */
.critical-text {
  color: var(--steel-100);  /* Highest contrast */
  font-weight: 600;
}

/* Ensure 4.5:1 contrast ratio */
/* Use --steel-100/200/300 on --steel-900/950 backgrounds */
```

---

## Anti-Patterns (DON'T DO THIS)

```css
/* ❌ DON'T: Hardcode colors */
background: #1a1a1a;
color: #888;

/* ✅ DO: Use tokens */
background: var(--steel-900);
color: var(--steel-400);

/* ❌ DON'T: Hardcode spacing */
padding: 16px;
margin: 8px;

/* ✅ DO: Use spacing scale */
padding: var(--space-md);
margin: var(--space-sm);

/* ❌ DON'T: Hardcode z-index */
z-index: 999;

/* ✅ DO: Use named layers */
z-index: var(--z-modal);

/* ❌ DON'T: Mix font families */
font-family: 'SF Mono', 'Courier', monospace;

/* ✅ DO: Use canonical stack */
font-family: var(--font-mono);
```

---

## Quick Reference Table

| Need | Use |
|------|-----|
| Background (deep) | `var(--steel-950)` |
| Background (panel) | `var(--steel-900)` |
| Background (button) | `var(--steel-800)` |
| Border | `var(--steel-700)` |
| Text (primary) | `var(--steel-100)` |
| Text (secondary) | `var(--steel-400)` |
| Text (muted) | `var(--steel-500)` |
| Mode indicator | `var(--status-insert/visual/witness)` |
| Selection | `var(--accent-gold)` |
| Error | `var(--status-error)` |
| Padding (tight) | `var(--space-sm)` |
| Padding (comfortable) | `var(--space-md)` |
| Padding (generous) | `var(--space-lg)` |
| Radius (button) | `var(--radius-md)` |
| Radius (modal) | `var(--radius-xl)` |
| Radius (tag) | `var(--radius-pill)` |
| Transition (hover) | `var(--transition-fast)` |
| Transition (fade) | `var(--transition-normal)` |
| Transition (slide) | `var(--transition-slow)` |
| Z-index (sidebar) | `var(--z-sidebar)` |
| Z-index (overlay) | `var(--z-overlay)` |
| Z-index (modal) | `var(--z-modal)` |
| Shadow (card) | `var(--shadow-md)` |
| Shadow (modal) | `var(--shadow-xl)` |

---

**Keep this cheatsheet open while coding. Copy-paste patterns. Never hardcode.**

---

*Source: `/impl/claude/web/src/hypergraph/design-system.css`*
*Last Updated: 2025-12-24*
