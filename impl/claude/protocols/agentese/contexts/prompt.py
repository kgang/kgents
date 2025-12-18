"""
AGENTESE Prompt Context Resolver

NOTE: Core compilation infrastructure archived 2025-12-18.
Most concept.prompt.* paths now return deprecation notices.
Use self.forest.* for meta-file operations instead.

See: protocols/_archived/evergreen-prompt-2025-12-18/README.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Prompt Affordances by Role ===

PROMPT_ROLE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "developer": ("manifest", "history"),
    "architect": ("manifest",),
    "reviewer": ("manifest", "history"),
    "default": ("manifest",),
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

    NOTE: Most functionality archived 2025-12-18.
    Use self.forest.* for meta-file operations.

    concept.prompt.* handles:
    - manifest: Read current CLAUDE.md (still works)
    - history: Get rollback history (still works if registry exists)
    - evolve: DEPRECATED - use manual editing
    - validate: DEPRECATED - use self.forest.witness
    - compile: DEPRECATED - use self.forest.reconcile
    """

    _handle: str = "concept.prompt"
    _project_root: Path | None = None

    def __post_init__(self) -> None:
        if self._project_root is None:
            # Default to finding project root
            self._project_root = Path(__file__).parent.parent.parent.parent.parent.parent

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return role-specific affordances."""
        return PROMPT_ROLE_AFFORDANCES.get(archetype, PROMPT_ROLE_AFFORDANCES["default"])

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Render current CLAUDE.md.

        Simply reads the file - no compilation needed since CLAUDE.md is hand-curated.
        """
        try:
            claude_md_path = self._project_root / "CLAUDE.md"
            if not claude_md_path.exists():
                return BasicRendering(
                    summary="CLAUDE.md not found",
                    content="CLAUDE.md does not exist at project root.",
                    metadata={"error": True},
                )

            content = claude_md_path.read_text(encoding="utf-8")
            lines = content.count("\n")
            chars = len(content)

            return BasicRendering(
                summary=f"CLAUDE.md ({lines} lines, {chars:,} chars)",
                content=content,
                metadata={
                    "lines": lines,
                    "chars": chars,
                    "path": str(claude_md_path),
                },
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
                return self._deprecated_result(
                    "evolve",
                    "Prompt evolution via TextGRAD archived 2025-12-18. Edit CLAUDE.md manually.",
                )
            case "validate":
                return self._deprecated_result(
                    "validate",
                    "Prompt validation archived 2025-12-18. "
                    "Use self.forest.witness for drift detection.",
                )
            case "compile":
                return self._deprecated_result(
                    "compile",
                    "Prompt compilation archived 2025-12-18. "
                    "CLAUDE.md is now hand-curated. "
                    "Use self.forest.reconcile for meta-file regeneration.",
                )
            case "history":
                return await self._history(observer, **kwargs)
            case "rollback":
                return self._deprecated_result(
                    "rollback",
                    "Prompt rollback archived 2025-12-18. Use git to revert CLAUDE.md changes.",
                )
            case "diff":
                return self._deprecated_result(
                    "diff",
                    "Prompt diff archived 2025-12-18. Use git diff for CLAUDE.md changes.",
                )
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def _deprecated_result(self, aspect: str, message: str) -> dict[str, Any]:
        """Return a deprecation notice for archived functionality."""
        return {
            "aspect": aspect,
            "status": "deprecated",
            "message": message,
            "archived": "2025-12-18",
            "see": "protocols/_archived/evergreen-prompt-2025-12-18/README.md",
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
            List of checkpoint summaries (or empty if registry not available)
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
            # Registry may not exist or have history
            return []


# === Context Resolver ===


@dataclass
class PromptContextResolver:
    """
    Resolver for prompt.* context paths.

    NOTE: Most functionality archived 2025-12-18.
    """

    _node: PromptNode | None = None
    _project_root: Path | None = None

    def resolve(self, holon: str, rest: list[str]) -> PromptNode:
        """Resolve to singleton PromptNode."""
        if self._node is None:
            self._node = PromptNode(_project_root=self._project_root)
        return self._node


def create_prompt_resolver(
    project_root: Path | None = None,
) -> PromptContextResolver:
    """Create a PromptContextResolver with optional project root."""
    return PromptContextResolver(_project_root=project_root)
