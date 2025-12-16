"""
Directories Section Compiler.

Compiles the key directories reference section.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens

if TYPE_CHECKING:
    from ..compiler import CompilationContext


class DirectoriesSectionCompiler:
    """Compile the directories section of CLAUDE.md."""

    @property
    def name(self) -> str:
        return "directories"

    @property
    def required(self) -> bool:
        return True

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """Compile directories section."""
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
        """Estimate ~400 tokens for directories section."""
        return 400

    def _render_content(self, context: CompilationContext) -> str:
        """Render the directories section content."""
        return """## Key Directories

- `spec/` - The specification (conceptual, implementation-agnostic)
- `spec/protocols/agentese.md` - AGENTESE specification
- `spec/protocols/projection.md` - Projection Protocol (CLI/TUI/marimo/JSON/VR)
- `spec/protocols/auto-inducer.md` - Phase transition signifiers
- `impl/` - Reference implementations (Claude Code + Open Router)
- `impl/claude/protocols/agentese/` - AGENTESE implementation (559 tests)
- `impl/claude/agents/i/reactive/` - Reactive substrate (widgets, projections)
- `docs/` - Supporting documentation
- `docs/skills` - Project specific procedural knowledge
- `docs/systems-reference.md` - **Full inventory of built systems**
- `docs/local-development.md` - **Local dev setup guide**
- `impl/claude/web/` - Agent Town React frontend (see `web/README.md`)

## Running Locally

```bash
# Terminal 1: Backend API
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Web UI
cd impl/claude/web
npm install && npm run dev
# Visit http://localhost:3000
```

See `docs/local-development.md` for detailed setup and troubleshooting."""


__all__ = ["DirectoriesSectionCompiler"]
