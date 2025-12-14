# Wave 9 Continuation Prompt

IMPLEMENT: Reactive Substrate Wave 9 - Widget Integration Pipeline

---
IMPLEMENT: Reactive Substrate Wave 9 - Widget Integration Pipeline

ATTACH

/hydrate

You are entering IMPLEMENT phase of the N-Phase Cycle (AD-005).

Context from Wave 8 (2025-12-14):
- Artifacts: animation/easing.py, animation/frame.py, animation/tween.py, animation/combinators.py, animation/spring.py, animation/animated.py
- Tests: 1066 reactive tests passing (218 new in Wave 8)
- Learnings: Animation is pure functions + physics. Springs feel alive because they preserve velocity on interruption.

Forest state: 14,100+ tests | reactive-substrate-unification active

---
## Your Mission

Build Wave 9 of the reactive substrate: Widget Integration Pipeline - connecting all pieces into a cohesive rendering system.

Target implementations:

### 1. Render Pipeline
Central orchestrator connecting animations to widgets:
- `RenderPipeline` class managing render loop
- Frame batching and dirty checking
- Priority queue for render order
- Integration with Clock and FrameScheduler

### 2. Layout System
Widget positioning and sizing:
- `Box` model (margin, padding, border)
- `Flex` layout (row, column, wrap)
- `Grid` layout for structured positioning
- Constraint-based sizing (min/max/fixed/fill)

### 3. Focus Management
Interactive widget selection:
- `FocusManager` tracking active widget
- Tab order navigation
- Focus transitions with animation
- Keyboard event routing

### 4. Theme System
Consistent styling across widgets:
- `Theme` dataclass with color/spacing tokens
- Dark/light mode support
- Animation timing presets
- Widget style inheritance

### 5. Integration Tests
Full pipeline verification:
- End-to-end render tests
- Animation integration tests
- Focus navigation tests
- Theme switching tests

Each implementation MUST:
- Use existing primitives (Signal, Clock, FrameScheduler, Tween, Spring)
- Build on Wave 1-8 foundations
- Support deterministic testing
- Tasteful: The pipeline should feel invisible - just smooth rendering
- Joy-Inducing: Focus transitions that feel natural

From CLAUDE.md:
- AGENTESE: Widget rendering is `world.*` context manifesting
- Composability: Pipeline stages are morphisms that compose

---
## Exit Criteria

- RenderPipeline orchestrating frame updates
- Basic layout system (Flex at minimum)
- FocusManager with animated transitions
- Theme system with dark/light modes
- mypy clean, ruff clean
- Commit with passing tests

---
## Entropy Budget

- Planned: 0.10 (10% exploration)
- Explore: Should we add declarative layout DSL?

---
## Continuation Imperative

Upon completing Wave 9, generate the continuation prompt for Wave 10: TUI Adapter - connecting to Textual for interactive terminal rendering.

---
"The best pipeline is the one you don't notice. Smooth, invisible, reliable."
