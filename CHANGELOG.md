# Changelog

All notable changes to kgents will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-14

### Added

#### Reactive Substrate
- `KgentsWidget[S]` base class with `project(target)` functor pattern
- `CompositeWidget[S]` for operad-like widget composition via slots/fillers
- `Signal[T]`, `Computed[T]`, `Effect` reactive primitives
- Widget primitives:
  - `GlyphWidget` - atomic visual unit with phase semantics
  - `BarWidget` - progress/capacity visualization
  - `SparklineWidget` - time-series mini-charts
  - `DensityFieldWidget` - 2D spatial entropy visualization
- Card widgets:
  - `AgentCardWidget` - full agent representation (phase + activity + capability)
  - `YieldCardWidget` - yield/return value visualization
  - `ShadowCardWidget` - H-gent shadow introspection
  - `DialecticCardWidget` - thesis/antithesis/synthesis visualization
- `TextualAdapter` for TUI rendering via Textual
- `MarimoAdapter` for notebook rendering via anywidget
- `AgentTraceWidget` for agent observability in notebooks
- Unified demo with CLI, TUI, and notebook support
- 1460+ tests with comprehensive coverage
- Performance: >4,000 renders/sec on all targets

#### CLI
- `kg dashboard` command for live system health monitoring
- `kg dashboard --demo` for demo mode with sample data
- Fallback text-mode dashboard when Textual unavailable

### Architecture

The reactive substrate implements a **functor pattern**:

```
project : KgentsWidget[S] → Target → Renderable[Target]
```

Same widget state, different projections. Zero rewrites.

Supported targets:
- `RenderTarget.CLI` - ASCII art for terminal
- `RenderTarget.TUI` - Rich/Textual widgets
- `RenderTarget.MARIMO` - anywidget for notebooks
- `RenderTarget.JSON` - serializable dicts for APIs

### Principles

1. **Pure Entropy Algebra** - No random.random() in render paths
2. **Time Flows Downward** - Parent provides t to children
3. **Projections Are Manifest** - project() IS logos.invoke("manifest")
4. **Glyph as Atomic Unit** - Everything composes from glyphs
5. **Deterministic Joy** - Same seed -> same personality, forever
6. **Slots/Fillers Composition** - Operad-like widget composition

## [0.1.0] - 2025-11-01

### Added
- Initial kgents implementation
- AGENTESE protocol foundation
- Agent taxonomy (A-Z, Ψ, Ω)
- Basic CLI infrastructure
