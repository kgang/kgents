# Changelog

All notable changes to kgents will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-12-23

### The Hardening Release

A controlled extinction, rebuilding, and hardening of the codebase.

#### Removed (The Extinction)
- **Agent Town** - Multi-agent simulation (archived to `_archive/`)
- **Park** - Agent recreation environment
- **Gestalt** - Emergent behavior patterns
- **Coalition** - Agent alliance formation
- **Muse** - Creative inspiration agent
- **Gardener** - Codebase cultivation agent
- ~67K lines archived to focus on core jewels

#### Added (The Rebuilding)
- **WitnessedGraph** - Edges carry evidence with confidence propagation
- **Hypergraph Emacs** - Six-mode modal editor (NORMAL/INSERT/EDGE/VISUAL/COMMAND/WITNESS)
- **Self-Hosting Specs** - Navigate, edit, witness specs from inside the system
- **Derivation DAG** - Specs form confidence-propagating directed graph
- **Living Spec** - Evidence-as-Marks unification
- **K-Block** - Monadic isolation for spec editing

#### Changed
- **AD-014**: Self-Hosting Spec Architecture
- **AD-015**: Proxy Handles (analysis ≠ reality)
- **AD-016**: Fail-Fast AGENTESE Resolution (no silent fallbacks)
- **AD-017**: Typed AGENTESE (paths have categorical types)
- CORS now configurable via `CORS_ORIGINS` environment variable
- Dead code audit removed ~14K additional lines

#### Security
- Fixed overly permissive CORS configuration
- Created .env.example templates

### Crown Jewel Status
- **Brain**: 100% complete
- **Witness**: 98% complete (678+ tests)
- **Atelier**: 75% complete
- **Liminal**: 50% complete

---

## [0.0.0] - 2025-12-14

### Initial Development

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

