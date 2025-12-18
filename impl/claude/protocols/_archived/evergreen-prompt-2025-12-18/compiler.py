"""
Prompt Compiler: Assemble CLAUDE.md from Sections.

The compiler is a pure function: inputs -> output.
Side effects are isolated to writing the output file.

Pipeline:
1. Load section compilers
2. Filter sections by context (phase, pressure)
3. Compile each section
4. Validate category laws
5. Compose into final prompt

See: spec/protocols/evergreen-prompt-system.md Part X
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .section_base import (
    NPhase,
    Section,
    SectionCompiler,
    compose_sections,
    estimate_tokens,
)

if TYPE_CHECKING:
    pass


@dataclass
class CompilationContext:
    """
    Context for prompt compilation.

    Provides all inputs needed by section compilers.
    """

    # Project paths
    project_root: Path = field(default_factory=Path.cwd)
    spec_path: Path | None = None
    docs_path: Path | None = None

    # Forest Protocol
    forest_path: Path | None = None
    focus_intent: str | None = None

    # Memory (for memory section)
    memory_query: str | None = None

    # Session context
    current_phase: NPhase | None = None
    pressure_budget: float = 1.0  # 0.0 to 1.0, lower = fewer optional sections

    # Options
    include_timestamp: bool = True
    max_tokens: int = 8000  # Target max token count

    def __post_init__(self) -> None:
        """Set default paths based on project root."""
        if self.spec_path is None:
            self.spec_path = self.project_root / "spec"
        if self.docs_path is None:
            self.docs_path = self.project_root / "docs"
        if self.forest_path is None:
            self.forest_path = self.project_root / "plans"


@dataclass
class CompilationResult:
    """Result of section compilation validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        """Raise ValueError if validation failed."""
        if not self.valid:
            raise ValueError(f"Compilation validation failed: {self.errors}")


@dataclass(frozen=True)
class CompiledPrompt:
    """
    Output of the prompt compiler.

    Contains the final assembled prompt and compilation metadata.
    """

    content: str
    version: int
    sections: tuple[Section, ...]
    compiled_at: datetime
    token_count: int

    def __str__(self) -> str:
        return self.content

    def save(self, path: Path | str) -> None:
        """Save compiled prompt to file."""
        Path(path).write_text(self.content)

    def section_names(self) -> list[str]:
        """Get list of section names in order."""
        return [s.name for s in self.sections]


class PromptCompiler:
    """
    Compile CLAUDE.md from sections.

    The compiler orchestrates section compilers and handles:
    - Section ordering
    - Phase-based filtering
    - Token budget management
    - Law validation
    """

    def __init__(
        self,
        section_compilers: list[SectionCompiler] | None = None,
        version: int = 1,
    ) -> None:
        """
        Initialize the compiler.

        Args:
            section_compilers: List of section compilers in order.
                              If None, uses default compilers.
            version: Starting version number
        """
        self._compilers = section_compilers or []
        self._version = version

    def register_compiler(self, compiler: SectionCompiler) -> None:
        """Add a section compiler."""
        self._compilers.append(compiler)

    def compile(self, context: CompilationContext) -> CompiledPrompt:
        """
        Compile all sections into final prompt.

        Pipeline:
        1. Filter compilers by phase relevance
        2. Compile each section
        3. Filter by token budget
        4. Validate laws
        5. Compose and return

        Args:
            context: Compilation context with paths and options

        Returns:
            CompiledPrompt with final content and metadata

        Raises:
            ValueError: If compilation validation fails
        """
        # 1. Filter compilers by phase
        relevant_compilers = [
            c for c in self._compilers if self._is_phase_relevant(c, context.current_phase)
        ]

        # 2. Compile sections
        sections: list[Section] = []
        for compiler in relevant_compilers:
            section = compiler.compile(context)
            sections.append(section)

        # 3. Filter by token budget
        sections = self._filter_by_budget(sections, context)

        # 4. Validate laws
        validation = self._validate_laws(sections)
        validation.raise_if_invalid()

        # 5. Compose
        content = compose_sections(sections)

        # Add footer
        if context.include_timestamp:
            timestamp = datetime.now().isoformat(timespec="seconds")
            footer = f"\n\n---\n\n*Compiled: {timestamp} | Version: {self._version} | Sections: {len(sections)}*"
            content += footer

        return CompiledPrompt(
            content=content,
            version=self._version,
            sections=tuple(sections),
            compiled_at=datetime.now(),
            token_count=estimate_tokens(content),
        )

    def _is_phase_relevant(
        self,
        compiler: SectionCompiler,
        phase: NPhase | None,
    ) -> bool:
        """Check if compiler is relevant to current phase."""
        if not compiler.phases:
            return True  # Empty = all phases
        if phase is None:
            return True  # No phase = include all
        return phase in compiler.phases

    def _filter_by_budget(
        self,
        sections: list[Section],
        context: CompilationContext,
    ) -> list[Section]:
        """
        Filter sections by token budget.

        Required sections are always included.
        Optional sections are included based on pressure budget.
        """
        # Always include required sections
        required = [s for s in sections if s.required]
        optional = [s for s in sections if not s.required]

        # Calculate remaining budget
        required_tokens = sum(s.token_cost for s in required)
        remaining_budget = int((context.max_tokens - required_tokens) * context.pressure_budget)

        # Add optional sections within budget
        result = list(required)
        for section in optional:
            if section.token_cost <= remaining_budget:
                result.append(section)
                remaining_budget -= section.token_cost

        return result

    def _validate_laws(self, sections: list[Section]) -> CompilationResult:
        """
        Validate category laws.

        Laws checked:
        1. Composition determinism (same inputs -> same output)
        2. Section composability (associativity)

        For V1, we do basic validation. Full law checking comes in Wave 4.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Check for duplicate section names
        names = [s.name for s in sections]
        if len(names) != len(set(names)):
            errors.append("Duplicate section names detected")

        # Check for empty sections
        for section in sections:
            if not section.content.strip():
                errors.append(f"Section '{section.name}' has empty content")

        # Warning if no sections
        if not sections:
            warnings.append("No sections to compile")

        return CompilationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def increment_version(self) -> int:
        """Increment and return the new version number."""
        self._version += 1
        return self._version

    @property
    def version(self) -> int:
        """Current version number."""
        return self._version


__all__ = [
    "CompilationContext",
    "CompilationResult",
    "CompiledPrompt",
    "PromptCompiler",
]
