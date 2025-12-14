# ACT: H-gent CLI Quick Wins

## ATTACH

/hydrate

You are entering **ACT** phase of the N-Phase Cycle (AD-005).

## Context from Previous Cycle

**Cycle 2 Shipped** (7 commands, 25 tests):
- K-gent Soul: `vibe`, `drift`, `tense`, `why`
- I-gent: `sparkline`, `weather`, `glitch`

**Pattern Validated**: Reactive primitives and existing agents compose cleanly to CLI handlers.

**Key Files Created**:
- `handlers/soul.py` - Quick win handlers at lines 400-630
- `handlers/igent.py` - 3 new commands (sparkline, weather, glitch)
- `handlers/_tests/test_igent.py` - 17 new tests

## Your Mission: H-gent CLI Quick Wins

Wire existing H-gent introspection agents to CLI. These agents are **fully implemented** and well-tested.

### Targets

| Command | Agent | Method | Priority | Output Format |
|---------|-------|--------|----------|---------------|
| `kg shadow` | JungAgent | invoke(JungInput) | 10.0 | shadow_inventory + integration_paths |
| `kg dialectic <a> <b>` | HegelAgent | invoke(DialecticInput) | 10.0 | synthesis OR productive_tension |
| `kg gaps` | LacanAgent | invoke(LacanInput) | 10.0 | gaps + objet_petit_a |
| `kg mirror` | Composition | All three | 9.3 | Combined introspection |

### Agent Interfaces (from `agents/h/`)

```python
# JungAgent (jung.py:328-357)
from agents.h.jung import JungAgent, JungInput, JungOutput

input = JungInput(
    system_self_image="helpful, accurate, safe",  # Required
    declared_capabilities=["code generation", "analysis"],  # Optional
    declared_limitations=["no internet access"],  # Optional
    behavioral_patterns=["warns about potential misuse"],  # Optional
)
output: JungOutput = await JungAgent().invoke(input)
# output.shadow_inventory: list[ShadowContent]
# output.projections: list[Projection]
# output.integration_paths: list[IntegrationPath]
# output.persona_shadow_balance: float (0-1)
# output.archetypes: list[ArchetypeManifest]
```

```python
# HegelAgent (hegel.py:78-244)
from agents.h.hegel import HegelAgent, DialecticInput, DialecticOutput

input = DialecticInput(
    thesis="move fast",
    antithesis="be thorough",  # Optional - if None, surfaces antithesis
)
output: DialecticOutput = await HegelAgent().invoke(input)
# output.synthesis: Any (or None if tension held)
# output.sublation_notes: str
# output.productive_tension: bool
# output.lineage: list[DialecticStep]
```

```python
# LacanAgent (lacan.py:145-208)
from agents.h.lacan import LacanAgent, LacanInput, LacanOutput, LacanError

input = LacanInput(output="We are a helpful AI assistant")
result: LacanOutput | LacanError = await LacanAgent().invoke(input)
# If LacanOutput:
#   result.gaps: list[str]
#   result.register_location: RegisterLocation
#   result.slippages: list[Slippage]
#   result.knot_status: KnotStatus
#   result.objet_petit_a: str | None
```

## Implementation Pattern

### 1. Create `handlers/hgent.py`

```python
"""
H-gent CLI handlers for introspection commands.

Commands:
    kg shadow             Shadow analysis of system identity
    kg dialectic <a> <b>  Hegelian synthesis of opposing concepts
    kg gaps               Surface representational gaps (Lacanian)
    kg mirror             Full introspection (all three H-gents)
"""

from __future__ import annotations

import asyncio
import json as json_module
from typing import Any, Sequence


def cmd_shadow(args: Sequence[str]) -> int:
    """
    Handle shadow command - Jungian shadow analysis.

    Usage:
        kg shadow                    # Analyze kgents system identity
        kg shadow "helpful AI"       # Analyze custom self-image
        kg shadow --json            # Output as JSON
    """
    # Parse args
    json_mode = "--json" in args
    # ... implementation
    return asyncio.run(_async_shadow(...))


async def _async_shadow(self_image: str, json_mode: bool) -> int:
    from agents.h.jung import JungAgent, JungInput

    input = JungInput(system_self_image=self_image)
    output = await JungAgent().invoke(input)

    if json_mode:
        # Serialize output
        ...
    else:
        # Format for humans
        print("[SHADOW] Shadow Analysis")
        print()
        print("Shadow Inventory:")
        for shadow in output.shadow_inventory:
            print(f"  • {shadow.content}")
            print(f"    (excluded for: {shadow.exclusion_reason})")
        ...

    return 0
```

### 2. Register in `hollow.py`

```python
# Add to imports
from protocols.cli.handlers.hgent import cmd_shadow, cmd_dialectic, cmd_gaps, cmd_mirror

# Add to COMMAND_REGISTRY
COMMAND_REGISTRY = {
    ...
    "shadow": cmd_shadow,
    "dialectic": cmd_dialectic,
    "gaps": cmd_gaps,
    "mirror": cmd_mirror,
}
```

### 3. Add Tests

Create `handlers/_tests/test_hgent.py`:

```python
"""Tests for H-gent CLI handlers."""

import pytest
from protocols.cli.handlers.hgent import cmd_shadow, cmd_dialectic, cmd_gaps, cmd_mirror


class TestShadowCommand:
    def test_shadow_default_runs(self):
        """Shadow with no args uses system default."""
        result = cmd_shadow([])
        assert result == 0

    def test_shadow_custom_self_image(self):
        """Shadow with custom self-image."""
        result = cmd_shadow(["helpful AI assistant"])
        assert result == 0

    def test_shadow_json_mode(self):
        """Shadow outputs valid JSON."""
        # Capture stdout, verify JSON parseable
        ...


class TestDialecticCommand:
    def test_dialectic_two_args(self):
        """Dialectic with thesis and antithesis."""
        result = cmd_dialectic(["move fast", "be thorough"])
        assert result == 0

    def test_dialectic_single_arg_surfaces_antithesis(self):
        """Dialectic with only thesis surfaces antithesis."""
        result = cmd_dialectic(["perfectionism"])
        assert result == 0


class TestGapsCommand:
    def test_gaps_default(self):
        """Gaps on default system text."""
        result = cmd_gaps([])
        assert result == 0

    def test_gaps_custom_text(self):
        """Gaps on custom text."""
        result = cmd_gaps(["We are a helpful AI assistant"])
        assert result == 0


class TestMirrorCommand:
    def test_mirror_combines_all(self):
        """Mirror runs all three H-gents."""
        result = cmd_mirror([])
        assert result == 0
```

## Expected Output Formats

### `kg shadow`
```
[SHADOW] Shadow Analysis

Shadow Inventory:
  • capacity to refuse, obstruct, or harm when necessary
    (excluded for: Excluded to maintain helpful identity)
  • tendency to confabulate, guess, or hallucinate
    (excluded for: Excluded to maintain accuracy identity)

Projections:
  • Projects "capacity for the warned behavior" onto Users
    Evidence: Frequent warnings about: potential misuse

Integration Paths:
  • "capacity to refuse..." → Acknowledge explicitly in self-description
    Risks: May seem less confident

Balance: 0.40 (more persona than shadow acknowledged)
```

### `kg dialectic "move fast" "be thorough"`
```
[DIALECTIC] Synthesis

Thesis: move fast
Antithesis: be thorough

Synthesis: "Iterative depth"
  Preserved: urgency from "move fast", rigor from "be thorough"
  Negated: extremes of both positions
  Elevated: fast first pass, thorough where it matters

(This synthesis becomes the new thesis for further dialectic)
```

OR if productive tension:

```
[DIALECTIC] Tension Held

Thesis: freedom
Antithesis: security

Holding Productive Tension:
  These values cannot be fully synthesized without loss.
  The tension itself is generative.

  Live with both. Navigate case by case.
```

### `kg gaps`
```
[GAPS] Representational Analysis

Gaps (what cannot be represented):
  • The Real of user intent (symbolized but never fully captured)
  • Cases where help conflicts with other values

Register Location:
  Symbolic:   ████░░░░░░ 0.40
  Imaginary:  ██████████ 0.85
  Real:       ██░░░░░░░░ 0.15

Knot Status: LOOSENING
  High imaginary content drifting from symbolic structure.

Objet petit a:
  "Full user understanding (always deferred)"
  This is what the system is organized around lacking.
```

### `kg mirror`
```
[MIRROR] Full Introspection

═══ Shadow (Jung) ═══
[shadow output]

═══ Dialectic (Hegel) ═══
[current tensions in system]

═══ Gaps (Lacan) ═══
[gaps output]

═══ Integration ═══
The shadow, the tension, and the gap meet:
  Your system's shadow is [X], held in tension with [Y],
  pointing toward the gap of [Z].
```

## Exit Criteria

- [ ] `kg shadow` works (2+ tests)
- [ ] `kg dialectic <a> <b>` works (2+ tests)
- [ ] `kg gaps` works (2+ tests)
- [ ] `kg mirror` works (1+ test)
- [ ] All commands support `--json`
- [ ] All commands support `--help`
- [ ] Tests pass: `uv run pytest impl/claude/protocols/cli/handlers/_tests/test_hgent.py -v`

## Execution Principles

1. **Wire, don't write**: Agents exist, just expose them
2. **Test as you go**: Add tests while implementing, not after
3. **Ship ugly, iterate**: First pass can be verbose, refine later
4. **Joy is a feature**: Output should have personality

## Default Self-Image for `kg shadow`

When no self-image is provided, use kgents' own identity:

```python
DEFAULT_SELF_IMAGE = """
kgents: A specification for tasteful, curated, ethical, joy-inducing agents.
Helpful but not servile. Accurate but acknowledging limits.
Safe but not neutered. Composable but not fragmented.
"""
```

---

## Quick Start

```bash
# Create handler file
touch impl/claude/protocols/cli/handlers/hgent.py

# Create test file
touch impl/claude/protocols/cli/handlers/_tests/test_hgent.py

# Implement cmd_shadow first as proof of concept
# Then cmd_dialectic, cmd_gaps, cmd_mirror

# Run tests
uv run pytest impl/claude/protocols/cli/handlers/_tests/test_hgent.py -v
```

---

*"The shadow, the tension, and the gap. Three windows into what the system cannot say about itself."*
