# Wave 10 Continuation Prompt

IMPLEMENT: Reactive Substrate Wave 10 - TUI Adapter

---
IMPLEMENT: Reactive Substrate Wave 10 - TUI Adapter

ATTACH

/hydrate

You are entering IMPLEMENT phase of the N-Phase Cycle (AD-005).

Context from Wave 9 (2025-12-14):
- Artifacts: pipeline/render.py, pipeline/layout.py, pipeline/focus.py, pipeline/theme.py
- Tests: 1198 reactive tests passing (132 new in Wave 9)
- Learnings: Pipeline is invisible when working. Dirty checking essential. Theme as Signal enables reactive switching.

Forest state: 14,100+ tests | reactive-substrate-unification active

---
## Your Mission

Build Wave 10 of the reactive substrate: TUI Adapter - connecting reactive widgets to Textual for interactive terminal rendering.

Target implementations:

### 1. Textual Widget Adapter
Bridge between KgentsWidget and Textual:
- `TextualAdapter` that wraps KgentsWidget
- Automatic re-rendering on Signal changes
- Mount/unmount lifecycle hooks
- Event translation (Textual events → KeyEvent, Interaction)

### 2. Layout Integration
Connect Wave 9 layouts to Textual containers:
- `FlexContainer` Textual widget using FlexLayout
- `GridContainer` Textual widget using GridLayout
- Constraint resolution at mount time
- Resize handling

### 3. Theme Binding
Bind Theme to Textual styling:
- `ThemeAdapter` connecting ThemeProvider to Textual CSS
- Dynamic theme switching
- CSS variable generation from theme tokens
- Focus ring styling

### 4. Focus Integration
Wire AnimatedFocus to Textual focus system:
- Sync between Textual.focus() and AnimatedFocus
- Animated focus ring overlay widget
- Keyboard navigation through adapters

### 5. Demo Application
Full TUI application using all adapters:
- Dashboard with agent cards
- Focus navigation between cards
- Theme toggle (Ctrl+T)
- Real-time updates from Clock

Each implementation MUST:
- Work with existing Textual apps
- Support deterministic testing
- Preserve reactive semantics
- Tasteful: Adapters should be thin bridges, not rewrites

From CLAUDE.md:
- RenderTarget.TUI is the projection target
- Adapters are morphisms that compose

---
## Exit Criteria

- TextualAdapter bridging Widget → Textual
- Layout containers working in Textual
- Theme binding with CSS generation
- Focus integration with animated ring
- Demo app with live dashboard
- mypy clean, ruff clean
- Commit with passing tests

---
## Entropy Budget

- Planned: 0.10 (10% exploration)
- Explore: Should we use Textual's built-in reactive or keep our Signal system?

---
## Continuation Imperative

Upon completing Wave 10, generate the continuation prompt for Wave 11: Marimo Adapter - connecting reactive widgets to marimo notebooks for interactive documentation.

---
"The adapter is the bridge. It should be invisible - just reactive widgets rendered wherever they need to be."
