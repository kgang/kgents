Wave 8 Continuation Prompt

  IMPLEMENT: Reactive Substrate Wave 8 - Animation Loop

  ---
  IMPLEMENT: Reactive Substrate Wave 8 - Animation Loop

  ATTACH

  /hydrate

  You are entering IMPLEMENT phase of the N-Phase Cycle (AD-005).

  Context from Wave 7 (2025-12-14):
  - Artifacts: terminal/ansi.py, terminal/box.py, terminal/art.py, terminal/adapter.py
  - Tests: 848 reactive tests passing (199 new in Wave 7)
  - Learnings: Terminal rendering is pure functions with graceful degradation

  Forest state: 13,900+ tests | 0 mypy errors | reactive-substrate-unification active

  ---
  Your Mission

  Build Wave 8 of the reactive substrate: Animation Loop - frame timing, transitions, and smooth updates.

  Target implementations:
  1. Frame Timing System - Consistent animation frames:
     - FrameScheduler with configurable FPS (30, 60, 120)
     - RequestAnimationFrame-like callback registration
     - Delta time calculations for smooth interpolation
     - Frame skipping under load

  2. Transition Functions - Easing and interpolation:
     - Easing functions (linear, ease-in, ease-out, ease-in-out, bounce, elastic)
     - Value interpolation (numbers, colors, positions)
     - Transition state machine (pending, running, complete)
     - Interruptible transitions

  3. Animation Primitives - Composable animations:
     - Tween[T] for property animation
     - Sequence for chained animations
     - Parallel for concurrent animations
     - Spring dynamics for physics-based motion

  4. Render Loop Integration - Connect to existing widgets:
     - AnimatedWidget base class
     - Frame callback subscription
     - Dirty checking for efficient updates
     - Integration with Clock from wiring/clock.py

  Each implementation MUST:
  - Use existing primitives (Signal, Clock, Effect)
  - Support deterministic testing (mock time)
  - Be pure where possible (easing functions are pure)
  - Tasteful: Smooth 60fps feels alive
  - Joy-Inducing: Spring physics brings delight

  From CLAUDE.md:
  - AGENTESE: Animation is time.* context manifesting
  - Signal: Animation state flows through reactive subscriptions

  ---
  Exit Criteria

  - Frame scheduler with configurable FPS
  - Easing functions (at least 6 standard curves)
  - Tween animation primitive
  - Sequence and Parallel combinators
  - Integration with existing Clock
  - mypy clean, ruff clean
  - Commit with passing tests

  ---
  Entropy Budget

  - Planned: 0.10 (10% exploration)
  - Explore: Should we add declarative animation DSL?

  ---
  Continuation Imperative

  Upon completing Wave 8, generate the continuation prompt for Wave 9: Widget Integration - connecting all pieces into a cohesive rendering pipeline.

  ---
  "Animation is the soul of the interface. Every frame tells a story."
