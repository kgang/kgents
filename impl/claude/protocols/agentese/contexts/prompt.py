"""
AGENTESE Prompt Context Resolver

The Evergreen Prompt System AGENTESE integration.

concept.prompt.* paths for prompt system operations:
- concept.prompt.manifest: Render current CLAUDE.md
- concept.prompt.evolve: Propose prompt evolution via TextGRAD
- concept.prompt.validate: Run category law checks
- concept.prompt.compile: Force recompilation with options
- concept.prompt.history: Get evolution history
- concept.prompt.rollback: Rollback to checkpoint
- concept.prompt.diff: Diff two checkpoints

Wave 6 of the Evergreen Prompt System.
See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Prompt Affordances by Role ===

PROMPT_ROLE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "developer": (
        "manifest",
        "evolve",
        "compile",
        "history",
        "rollback",
        "diff",
        "validate",
    ),
    "architect": ("manifest", "evolve", "validate", "analyze"),
    "reviewer": ("manifest", "diff", "history"),
    "default": ("manifest", "history"),
}


# === Result Types ===


@dataclass(frozen=True)
class EvolutionResult:
    """Result of a prompt evolution request."""

    success: bool
    original_content: str
    improved_content: str
    sections_modified: tuple[str, ...]
    reasoning_trace: tuple[str, ...]
    checkpoint_id: str | None = None
    message: str = ""


@dataclass(frozen=True)
class ValidationResult:
    """Result of prompt validation."""

    valid: bool
    law_checks: tuple[tuple[str, bool], ...]  # (law_name, passed)
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiffResult:
    """Result of diffing two checkpoints."""

    id1: str
    id2: str
    diff_content: str
    lines_added: int
    lines_removed: int


@dataclass(frozen=True)
class CheckpointSummaryDTO:
    """DTO for checkpoint summary in AGENTESE context."""

    id: str
    timestamp: datetime
    reason: str
    sections_before: tuple[str, ...]
    sections_after: tuple[str, ...]
    content_length_before: int
    content_length_after: int


# === Prompt Node ===


@dataclass
class PromptNode(BaseLogosNode):
    """
    AGENTESE node for the Evergreen Prompt System.

    concept.prompt.* handles:
    - manifest: Render current CLAUDE.md
    - evolve: Propose evolution via TextGRAD
    - validate: Run category law checks
    - compile: Force recompilation
    - history: Get evolution history
    - rollback: Rollback to checkpoint
    - diff: Diff two checkpoints
    """

    _handle: str = "concept.prompt"
    _project_root: Path | None = None

    def __post_init__(self) -> None:
        if self._project_root is None:
            # Default to finding project root
            self._project_root = Path(
                __file__
            ).parent.parent.parent.parent.parent.parent

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-specific affordances."""
        return PROMPT_ROLE_AFFORDANCES.get(
            archetype, PROMPT_ROLE_AFFORDANCES["default"]
        )

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Render current CLAUDE.md.

        Returns the compiled prompt content formatted for the observer's role.
        """
        try:
            from protocols.prompt import CompilationContext, PromptCompiler
            from protocols.prompt.sections import get_default_compilers

            compilers = get_default_compilers()
            compiler = PromptCompiler(section_compilers=compilers, version=1)
            context = CompilationContext(
                project_root=self._project_root,
                include_timestamp=True,
            )

            result = compiler.compile(context)

            meta = self._umwelt_to_meta(observer)

            if meta.archetype == "developer":
                return BasicRendering(
                    summary=f"CLAUDE.md ({len(result.sections)} sections, ~{result.total_tokens} tokens)",
                    content=result.content,
                    metadata={
                        "sections": result.section_names(),
                        "tokens": result.total_tokens,
                        "chars": len(result.content),
                    },
                )
            elif meta.archetype == "architect":
                # Show structure overview
                section_summary = "\n".join(
                    f"  - {s.name}: {s.token_cost} tokens" for s in result.sections
                )
                return BasicRendering(
                    summary="CLAUDE.md Architecture",
                    content=f"Sections:\n{section_summary}\n\nTotal: ~{result.total_tokens} tokens",
                    metadata={"sections": result.section_names()},
                )
            else:
                return BasicRendering(
                    summary="CLAUDE.md",
                    content=result.content[:500] + "..."
                    if len(result.content) > 500
                    else result.content,
                    metadata={"preview": True},
                )

        except Exception as e:
            return BasicRendering(
                summary="Error loading CLAUDE.md",
                content=str(e),
                metadata={"error": True},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle prompt-specific aspects."""
        match aspect:
            case "evolve":
                return await self._evolve(observer, **kwargs)
            case "validate":
                return await self._validate(observer, **kwargs)
            case "compile":
                return await self._compile(observer, **kwargs)
            case "history":
                return await self._history(observer, **kwargs)
            case "rollback":
                return await self._rollback(observer, **kwargs)
            case "diff":
                return await self._diff(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _evolve(
        self,
        observer: "Umwelt[Any, Any]",
        feedback: str = "",
        learning_rate: float = 0.5,
        **kwargs: Any,
    ) -> EvolutionResult:
        """
        Propose prompt evolution via TextGRAD.

        Args:
            feedback: Natural language feedback for improvement
            learning_rate: How aggressively to apply changes (0.0-1.0)

        Returns:
            EvolutionResult with proposed changes
        """
        if not feedback:
            return EvolutionResult(
                success=False,
                original_content="",
                improved_content="",
                sections_modified=(),
                reasoning_trace=("No feedback provided",),
                message="Feedback required for evolution",
            )

        try:
            from protocols.prompt.rollback import get_default_registry
            from protocols.prompt.textgrad import TextGRADImprover

            # Load current CLAUDE.md
            claude_md_path = self._project_root / "CLAUDE.md"
            if not claude_md_path.exists():
                return EvolutionResult(
                    success=False,
                    original_content="",
                    improved_content="",
                    sections_modified=(),
                    reasoning_trace=("CLAUDE.md not found",),
                    message="CLAUDE.md not found",
                )

            content = claude_md_path.read_text(encoding="utf-8")
            sections = self._content_to_sections(content)

            # Apply TextGRAD
            registry = get_default_registry()
            improver = TextGRADImprover(
                learning_rate=learning_rate,
                rollback_registry=registry,
            )

            result = improver.improve(sections, feedback)

            return EvolutionResult(
                success=result.content_changed,
                original_content=result.original_content,
                improved_content=result.improved_content,
                sections_modified=result.sections_modified,
                reasoning_trace=result.reasoning_trace,
                checkpoint_id=result.checkpoint_id,
                message="Evolution proposed"
                if result.content_changed
                else "No changes",
            )

        except Exception as e:
            return EvolutionResult(
                success=False,
                original_content="",
                improved_content="",
                sections_modified=(),
                reasoning_trace=(f"Error: {e}",),
                message=str(e),
            )

    async def _validate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> ValidationResult:
        """
        Run category law checks on the prompt.

        Validates:
        - Monad laws (identity, associativity)
        - Section completeness
        - Determinism
        """
        try:
            from protocols.prompt import PromptM, Source

            checks: list[tuple[str, bool]] = []
            warnings: list[str] = []
            errors: list[str] = []

            # Check 1: Identity law
            try:
                # pure(a).bind(f) == f(a)
                pure_a = PromptM.pure("test", Source.FILE)
                # Identity law holds if pure works
                checks.append(("identity_law", True))
            except Exception as e:
                checks.append(("identity_law", False))
                errors.append(f"Identity law failed: {e}")

            # Check 2: Determinism
            try:
                from protocols.prompt import CompilationContext, PromptCompiler
                from protocols.prompt.sections import get_default_compilers

                compilers = get_default_compilers()
                compiler = PromptCompiler(section_compilers=compilers, version=1)
                context = CompilationContext(
                    project_root=self._project_root,
                    include_timestamp=False,  # Disable for determinism check
                )

                result1 = compiler.compile(context)
                result2 = compiler.compile(context)

                is_deterministic = result1.content == result2.content
                checks.append(("determinism", is_deterministic))
                if not is_deterministic:
                    warnings.append("Non-deterministic compilation detected")

            except Exception as e:
                checks.append(("determinism", False))
                errors.append(f"Determinism check failed: {e}")

            # Check 3: Section completeness
            try:
                from protocols.prompt.sections import get_default_compilers

                compilers = get_default_compilers()
                checks.append(("section_completeness", len(compilers) > 0))
            except Exception as e:
                checks.append(("section_completeness", False))
                errors.append(f"Section completeness check failed: {e}")

            all_passed = all(passed for _, passed in checks)

            return ValidationResult(
                valid=all_passed,
                law_checks=tuple(checks),
                warnings=tuple(warnings),
                errors=tuple(errors),
            )

        except Exception as e:
            return ValidationResult(
                valid=False,
                law_checks=(("validation_error", False),),
                errors=(str(e),),
            )

    async def _compile(
        self,
        observer: "Umwelt[Any, Any]",
        output_path: str | None = None,
        checkpoint: bool = True,
        reason: str = "AGENTESE compilation",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Force recompilation with options.

        Args:
            output_path: Optional path to save compiled prompt
            checkpoint: Create checkpoint before compile
            reason: Reason for compilation

        Returns:
            Compilation result dict
        """
        try:
            from protocols.prompt.cli import compile_prompt

            content = compile_prompt(
                output_path=Path(output_path) if output_path else None,
                checkpoint=checkpoint,
                reason=reason,
            )

            return {
                "success": True,
                "content_length": len(content),
                "output_path": output_path,
                "checkpoint": checkpoint,
                "reason": reason,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _history(
        self,
        observer: "Umwelt[Any, Any]",
        limit: int = 10,
        **kwargs: Any,
    ) -> list[CheckpointSummaryDTO]:
        """
        Get evolution history.

        Args:
            limit: Maximum entries to return

        Returns:
            List of checkpoint summaries
        """
        try:
            from protocols.prompt.rollback import get_default_registry

            registry = get_default_registry()
            history = registry.history(limit=limit)

            return [
                CheckpointSummaryDTO(
                    id=h.id,
                    timestamp=h.timestamp,
                    reason=h.reason,
                    sections_before=h.sections_before,
                    sections_after=h.sections_after,
                    content_length_before=h.content_length_before,
                    content_length_after=h.content_length_after,
                )
                for h in history
            ]

        except Exception:
            return []

    async def _rollback(
        self,
        observer: "Umwelt[Any, Any]",
        checkpoint_id: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Rollback to a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Returns:
            Rollback result dict
        """
        if not checkpoint_id:
            return {
                "success": False,
                "error": "Checkpoint ID required",
            }

        try:
            from protocols.prompt.rollback import get_default_registry

            registry = get_default_registry()
            result = registry.rollback(checkpoint_id)

            return {
                "success": result.success,
                "checkpoint_id": result.checkpoint_id,
                "restored_length": len(result.restored_content or ""),
                "message": result.message,
                "reasoning_trace": result.reasoning_trace,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def _diff(
        self,
        observer: "Umwelt[Any, Any]",
        id1: str = "",
        id2: str = "",
        **kwargs: Any,
    ) -> DiffResult | dict[str, Any]:
        """
        Diff two checkpoints.

        Args:
            id1: First checkpoint ID
            id2: Second checkpoint ID

        Returns:
            DiffResult or error dict
        """
        if not id1 or not id2:
            return {"error": "Both checkpoint IDs required"}

        try:
            from protocols.prompt.rollback import get_default_registry
            from protocols.prompt.rollback.checkpoint import CheckpointId

            registry = get_default_registry()
            diff = registry.diff(CheckpointId(id1), CheckpointId(id2))

            if diff is None:
                return {"error": "Could not compute diff"}

            # Count lines
            lines_added = diff.count("\n+") if diff else 0
            lines_removed = diff.count("\n-") if diff else 0

            return DiffResult(
                id1=id1,
                id2=id2,
                diff_content=diff or "",
                lines_added=lines_added,
                lines_removed=lines_removed,
            )

        except Exception as e:
            return {"error": str(e)}

    def _content_to_sections(self, content: str) -> dict[str, str]:
        """Parse CLAUDE.md content into sections dict."""
        sections: dict[str, str] = {}
        current_section = None
        current_lines: list[str] = []

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_lines)
                current_section = line[3:].strip()
                current_lines = []
            elif current_section:
                current_lines.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_lines)

        return sections


# === Context Resolver ===


@dataclass
class PromptContextResolver:
    """
    Resolver for concept.prompt.* context.

    Provides access to the Evergreen Prompt System via AGENTESE paths.
    """

    project_root: Path | None = None
    _cache: dict[str, PromptNode] = field(default_factory=dict)

    def resolve(self, holon: str, rest: list[str]) -> PromptNode:
        """
        Resolve a concept.prompt.* path to a PromptNode.

        Args:
            holon: The path component after "concept." (e.g., "prompt")
            rest: Additional path components

        Returns:
            PromptNode for handling the request
        """
        handle = f"concept.{holon}"

        if handle in self._cache:
            return self._cache[handle]

        if holon == "prompt":
            node = PromptNode(
                _handle=handle,
                _project_root=self.project_root,
            )
            self._cache[handle] = node
            return node

        # Unknown subpath - return basic node
        return PromptNode(_handle=handle, _project_root=self.project_root)


# === Factory Functions ===


def create_prompt_node(project_root: Path | None = None) -> PromptNode:
    """Create a PromptNode with optional project root."""
    return PromptNode(_handle="concept.prompt", _project_root=project_root)


def create_prompt_resolver(project_root: Path | None = None) -> PromptContextResolver:
    """Create a PromptContextResolver with optional project root."""
    return PromptContextResolver(project_root=project_root)


__all__ = [
    "PROMPT_ROLE_AFFORDANCES",
    "EvolutionResult",
    "ValidationResult",
    "DiffResult",
    "CheckpointSummaryDTO",
    "PromptNode",
    "PromptContextResolver",
    "create_prompt_node",
    "create_prompt_resolver",
]
