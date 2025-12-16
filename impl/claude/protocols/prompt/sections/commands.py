"""
Commands Section Compiler.

Compiles the DevEx commands section.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens

if TYPE_CHECKING:
    from ..compiler import CompilationContext


class CommandsSectionCompiler:
    """Compile the commands section of CLAUDE.md."""

    @property
    def name(self) -> str:
        return "commands"

    @property
    def required(self) -> bool:
        return False  # Optional

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """Compile commands section."""
        content = self._render_content(context)
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(),
        )

    def estimate_tokens(self) -> int:
        """Estimate ~150 tokens for commands section."""
        return 150

    def _render_content(self, context: CompilationContext) -> str:
        """Render the commands section content."""
        return """## DevEx Commands (Slash Commands)

| Command | Purpose |
|---------|---------|
| `/harden <target>` | Robustify, shore up durability of a module |
| `/trace <target>` | Trace execution paths and data flow |
| `/diff-spec <spec>` | Compare implementation against specification |
| `/debt <path>` | Technical debt audit |"""


__all__ = ["CommandsSectionCompiler"]
