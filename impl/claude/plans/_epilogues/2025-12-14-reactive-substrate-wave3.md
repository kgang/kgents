# Wave 3 Complete: AgentCard & YieldCard

**Date**: 2025-12-14
**Focus**: Composed widgets that bring agents to life

## Summary

Wave 3 implemented the "molecule → organism" level of our reactive substrate: composed widgets that represent agents and their outputs.

## Artifacts

| File | Purpose |
|------|---------|
| `agents/i/reactive/primitives/agent_card.py` | AgentCardWidget - full agent representation |
| `agents/i/reactive/primitives/yield_card.py` | YieldCardWidget - agent output/yield display |
| `agents/i/reactive/_tests/test_agent_card.py` | 35 tests for AgentCard |
| `agents/i/reactive/_tests/test_yield_card.py` | 43 tests for YieldCard |

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Test count (reactive) | 205 | 283 |
| Wave 3 tests | 0 | 78 |
| Primitives | 4 | 6 |

## What We Built

### AgentCardWidget

Composes from Wave 1-2 primitives:
- **Header**: GlyphWidget (phase indicator) + agent name
- **Body**: SparklineWidget (activity history)
- **Footer**: BarWidget (capability/health)

Features:
- Three styles: `full`, `compact`, `minimal`
- Optional "breathing" animation for active agents
- Entropy flows to all children
- Time flows downward for synchronized animation

### YieldCardWidget

Composes from Wave 1-2 primitives:
- **Type indicator**: GlyphWidget (thought/action/artifact/error)
- **Importance bar**: BarWidget (visual weight)

Features:
- Type-specific glyphs (emoji or ASCII mode)
- Content truncation with preview
- Importance-based styling
- High-importance yields show emphasized borders/colors

## Composition Verification

Both widgets properly compose from Wave 1-2 primitives:
- No code duplication
- Entropy propagates correctly
- Time propagates correctly
- All 4 render targets work (CLI, TUI, MARIMO, JSON)

## Entropy Budget

- Planned: 0.07 (7% exploration)
- Actual: ~0.03
- Explored: Breathing animation for active agents (implemented)

## Learnings

1. **CompositeWidget pattern works well** - slots + rebuild pattern is clean
2. **Importance as entropy boost** - high-importance yields get extra visual emphasis
3. **Style variants** - full/compact/minimal provides flexibility
4. **Immutable state chains** - with_* methods maintain purity

## Wave 4 Readiness

Cards are ready. Next: Screen-level compositions that tie it all together.

---

*"The glyph is the atom. The bar is a sentence. The card is a paragraph. The screen is the story."*
