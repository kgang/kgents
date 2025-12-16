"""
AGENTESE Section Compiler.

Compiles the AGENTESE ontology section explaining the verb-first
interaction model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens

if TYPE_CHECKING:
    from ..compiler import CompilationContext


class AgenteseSectionCompiler:
    """Compile the AGENTESE section of CLAUDE.md."""

    @property
    def name(self) -> str:
        return "agentese"

    @property
    def required(self) -> bool:
        return True

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """Compile AGENTESE section."""
        content = self._render_content(context)
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(context.spec_path / "protocols" / "agentese.md",)
            if context.spec_path
            else (),
        )

    def estimate_tokens(self) -> int:
        """Estimate ~500 tokens for AGENTESE section."""
        return 500

    def _render_content(self, context: CompilationContext) -> str:
        """Render the AGENTESE section content."""
        # Note: Use proper Unicode typography:
        # - Em-dash (—) not hyphen (-) for parenthetical
        # - Arrows (→) not ASCII (->)
        return """## AGENTESE: The Verb-First Ontology

> *"The noun is a lie. There is only the rate of change."*

AGENTESE is the meta-protocol for agent-world interaction. Instead of querying a database of nouns, agents grasp **handles** that yield **affordances** based on who is grasping.

**Spec**: `spec/protocols/agentese.md`
**Impl**: `impl/claude/protocols/agentese/`

### The Five Contexts

```
world.*    - The External (entities, environments, tools)
self.*     - The Internal (memory, capability, state)
concept.*  - The Abstract (platonics, definitions, logic)
void.*     - The Accursed Share (entropy, serendipity, gratitude)
time.*     - The Temporal (traces, forecasts, schedules)
```

### Core Insight

Traditional systems: `world.house` returns a JSON object.
AGENTESE: `world.house` returns a **handle**—a morphism that maps Observer → Interaction.

```python
# Different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
await logos.invoke("world.house.manifest", economist_umwelt)  # → Appraisal
```

### Key Aspects

| Aspect | Category | Meaning |
|--------|----------|---------|
| `manifest` | Perception | Collapse to observer's view |
| `witness` | Perception | Show history (N-gent) |
| `refine` | Generation | Dialectical challenge |
| `sip` | Entropy | Draw from Accursed Share |
| `tithe` | Entropy | Pay for order (gratitude) |
| `lens` | Composition | Get composable agent |
| `define` | Generation | Autopoiesis (create new) |"""


__all__ = ["AgenteseSectionCompiler"]
