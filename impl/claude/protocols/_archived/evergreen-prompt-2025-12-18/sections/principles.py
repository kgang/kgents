"""
Principles Section Compiler.

Compiles the core principles section from spec/principles.md.

For the prompt, we include a summary version, not the full principles
document (which is ~1100 lines).

Wave 2: Now reads dynamically from spec/principles.md with fallback.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..section_base import (
    NPhase,
    Section,
    estimate_tokens,
    extract_principle_summary,
    read_file_safe,
)

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


class PrinciplesSectionCompiler:
    """
    Compile the principles section of CLAUDE.md.

    Wave 2: Reads dynamically from spec/principles.md.
    Falls back to hardcoded content if source file is missing.
    """

    @property
    def name(self) -> str:
        return "principles"

    @property
    def required(self) -> bool:
        return True

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """
        Compile principles section.

        Attempts to read from spec/principles.md, falls back to hardcoded.
        """
        source_path = context.spec_path / "principles.md" if context.spec_path else None

        if source_path:
            content = self._compile_dynamic(source_path)
            if content:
                return Section(
                    name=self.name,
                    content=content,
                    token_cost=estimate_tokens(content),
                    required=self.required,
                    phases=self.phases,
                    source_paths=(source_path,),
                )

        # Fallback to hardcoded
        logger.info("Using fallback content for principles section")
        content = self._compile_fallback()
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(),  # No source paths for fallback
        )

    def estimate_tokens(self) -> int:
        """Estimate ~400 tokens for principles summary."""
        return 400

    def _compile_dynamic(self, source_path) -> str | None:
        """
        Read and extract principles from source file.

        Returns None if file doesn't exist or parsing fails.
        """
        content = read_file_safe(source_path)
        if not content:
            return None

        # Extract principle summary
        principles_summary = extract_principle_summary(content)
        if not principles_summary:
            logger.warning(f"Could not extract principles from {source_path}")
            return None

        # Build the section content
        return f"""## Core Principles (Summary)

{principles_summary}

### The Unified Categorical Foundation

> *"The same categorical structure underlies everything. This is not coincidence—it is the ground."*

All kgents domains instantiate the same three-layer pattern:

| Layer | Purpose | Examples |
|-------|---------|----------|
| **PolyAgent** | State machine with mode-dependent inputs | CitizenPolynomial, SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL |
| **Operad** | Composition grammar with laws | TOWN_OPERAD, NPHASE_OPERAD, SOUL_OPERAD |
| **Sheaf** | Global coherence from local views | TownSheaf, ProjectSheaf, EigenvectorCoherence |

**Key Insight**: Understanding one domain teaches you the others.

See: `spec/principles.md` for full principles"""

    def _compile_fallback(self) -> str:
        """Hardcoded fallback content when source file is unavailable."""
        return """## Core Principles (Summary)

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary
6. **Heterarchical** - Autonomy and composability coexist
7. **Generative** - Spec is compression; design should generate implementation

### The Unified Categorical Foundation

> *"The same categorical structure underlies everything. This is not coincidence—it is the ground."*

All kgents domains instantiate the same three-layer pattern:

| Layer | Purpose | Examples |
|-------|---------|----------|
| **PolyAgent** | State machine with mode-dependent inputs | CitizenPolynomial, SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL |
| **Operad** | Composition grammar with laws | TOWN_OPERAD, NPHASE_OPERAD, SOUL_OPERAD |
| **Sheaf** | Global coherence from local views | TownSheaf, ProjectSheaf, EigenvectorCoherence |

**Key Insight**: Understanding one domain teaches you the others.

See: `spec/principles.md` for full principles"""


__all__ = ["PrinciplesSectionCompiler"]
