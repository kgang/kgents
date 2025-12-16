"""
Identity Section Compiler.

Compiles the project identity section including:
- Project name and tagline
- Philosophy (specification-first, Python/CPython model, etc.)
- Current focus
- Agent taxonomy table

This is always a required section.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens

if TYPE_CHECKING:
    from ..compiler import CompilationContext


class IdentitySectionCompiler:
    """Compile the identity section of CLAUDE.md."""

    @property
    def name(self) -> str:
        return "identity"

    @property
    def required(self) -> bool:
        return True

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """Compile identity section."""
        content = self._render_content(context)
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(context.project_root / "CLAUDE.md",),
        )

    def estimate_tokens(self) -> int:
        """Estimate ~600 tokens for identity section."""
        return 600

    def _render_content(self, context: CompilationContext) -> str:
        """Render the identity section content."""
        # Note: Use proper Unicode typography:
        # - Em-dash (—) not hyphen (-) for "none"
        # - Arrows (→) not ASCII (->)
        return """# kgents - Kent's Agents

A specification for tasteful, curated, ethical, joy-inducing agents.

## Project Philosophy

- **Specification-first**: Define what agents should be, not just how to build them
- **The Python/CPython model**: `spec/` is the language spec, `impl/` is the reference implementation
- **Alphabetical taxonomy**: Each letter represents a distinct agent genus
- **AGENTESE**: The verb-first ontology for agent-world interaction

## Current Focus

Deeply specifying and implementing the agent ecosystem with AGENTESE as the meta-protocol.

| Letter | Name | Theme | Polynomial |
|--------|------|-------|------------|
| A | Agents | Abstract architectures + Art/Creativity coaches | `ALETHIC_AGENT` |
| B | Bgents | Bio/Scientific discovery + Economics + Distillation | — |
| C | Cgents | Category Theory basis (composability) | — |
| D | Dgents | Data Agents (state, memory, persistence) | `MEMORY_POLYNOMIAL` |
| E | Egents | Evolution (teleological thermodynamics) | `EVOLUTION_POLYNOMIAL` |
| K | Kgent | Kent simulacra (interactive persona) | `SOUL_POLYNOMIAL` |
| L | Lgents | Lattice/Library (semantic registry) | — |
| M | Mgents | Memory/Map (holographic cartography) | — |
| N | Ngents | Narrative (witness/trace) | — |
| T | Tgents | Testing (algebraic reliability, Types I-V) | — |
| U | Ugents | Utility (tool use, MCP integration) | — |
| Y | Ygent | Y-Combinator (cognitive + somatic topology) | — |
| Ψ | Psigent | Psychopomp (metaphor engine) | — |
| Ω | Omegagent | Somatic Orchestrator (morphemes, proprioception) | — |

**Note**: Polynomial agents (`PolyAgent[S, A, B]`) capture state-dependent behavior. See `docs/skills/polynomial-agent.md`."""


__all__ = ["IdentitySectionCompiler"]
