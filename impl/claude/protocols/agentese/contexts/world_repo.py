"""
AGENTESE World Repo Context: Repository navigation and path validation.

Visual Trail Graph Session 2: Path Validation

This implements the path validation endpoint for trail creation:
- world.repo.validate → Check if path exists with fuzzy suggestions
- world.repo.manifest → Show repo status

Key Patterns:
- FUZZY SUGGESTIONS: Use difflib.get_close_matches for similar paths
- CREATABLE DETECTION: Check if file extension supports creation
- WARM ERRORS: Helpful messages with suggestions

AGENTESE: world.repo.*

Teaching:
    gotcha: This node is for PATH validation, not file content.
            For reading/writing files, use world.file.* instead.

    gotcha: Suggestions use fuzzy matching with cutoff=0.4 to catch
            typos while avoiding false positives.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# Repository affordances
REPO_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "validate",
)

# Extensions that can be created via the UI
CREATABLE_EXTENSIONS = frozenset({
    ".py", ".md", ".ts", ".tsx", ".js", ".jsx",
    ".json", ".yaml", ".yml", ".toml",
    ".txt", ".html", ".css", ".scss",
})

# Maximum files to scan for suggestions (performance guard)
MAX_FILES_SCAN = 10000

# Maximum suggestions to return
MAX_SUGGESTIONS = 5


@node(
    "world.repo",
    description="Repository navigation and path validation",
    singleton=True,
    examples=[
        ("validate", {"path": "CLAUDE.md"}, "Check if CLAUDE.md exists"),
        ("validate", {"path": "CLAUED.md"}, "Get suggestions for typo"),
        ("validate", {"path": "new/file.py"}, "Check creatable path"),
    ],
)
@dataclass
class RepoNode(BaseLogosNode):
    """
    world.repo - Repository navigation and validation node.

    Provides path validation for trail creation with fuzzy suggestions.
    Does NOT read or modify file contents (use world.file for that).
    """

    _handle: str = "world.repo"
    _repo_root: Path | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def set_repo_root(self, root: Path) -> None:
        """Set custom repo root (for testing)."""
        self._repo_root = root

    def _get_repo_root(self) -> Path:
        """Get the repository root path."""
        if self._repo_root is not None:
            return self._repo_root
        # Default to current working directory
        return Path.cwd()

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Repo affordances available to all archetypes."""
        return REPO_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View repo node status and capabilities."""
        repo_root = self._get_repo_root()

        content_lines = [
            "Repository Navigation & Validation",
            "",
            "Capabilities:",
            "  - validate: Check if path exists with fuzzy suggestions",
            "",
            f"Repository Root: {repo_root}",
            "",
            "Creatable Extensions:",
            f"  {', '.join(sorted(CREATABLE_EXTENSIONS))}",
        ]

        return BasicRendering(
            summary="world.repo manifest",
            content="\n".join(content_lines),
            metadata={
                "repo_root": str(repo_root),
                "creatable_extensions": list(CREATABLE_EXTENSIONS),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("filesystem")],
        help="Validate a path exists in the repository with fuzzy suggestions",
        examples=[
            "world.repo.validate[path='CLAUDE.md']",
            "world.repo.validate[path='services/brain/core.py']",
        ],
    )
    async def validate(
        self,
        observer: "Umwelt[Any, Any]",
        path: str,
        response_format: str = "json",
    ) -> Renderable:
        """
        Check if a path exists in the repository.

        Returns:
        - exists: Whether the file/directory exists
        - suggestions: Similar paths if not found (fuzzy match)
        - can_create: Whether the extension supports file creation

        Teaching:
            gotcha: Suggestions are computed lazily only when path not found.
                    This keeps validation fast for existing paths.
        """
        repo_root = self._get_repo_root()

        # Normalize the path (handle both / and \ separators)
        normalized_path = path.replace("\\", "/")
        full_path = repo_root / normalized_path

        # Check existence
        exists = full_path.exists()

        # Compute suggestions only if not found
        suggestions: list[str] = []
        if not exists:
            suggestions = await self._get_suggestions(normalized_path, repo_root)

        # Check if creatable
        suffix = Path(normalized_path).suffix.lower()
        can_create = suffix in CREATABLE_EXTENSIONS

        # Build response
        if exists:
            summary = f"Path exists: {normalized_path}"
        elif suggestions:
            summary = f"Path not found, {len(suggestions)} suggestions"
        else:
            summary = f"Path not found: {normalized_path}"

        metadata = {
            "status": "success",
            "exists": exists,
            "suggestions": suggestions,
            "can_create": can_create,
            "path": normalized_path,
        }

        if response_format == "cli":
            # CLI-friendly output
            lines = [summary]
            if suggestions:
                lines.append("")
                lines.append("Did you mean?")
                for suggestion in suggestions:
                    lines.append(f"  - {suggestion}")
            if can_create and not exists:
                lines.append("")
                lines.append(f"You can create this file ({suffix})")
            content = "\n".join(lines)
        else:
            content = ""

        return BasicRendering(
            summary=summary,
            content=content,
            metadata=metadata,
        )

    async def _get_suggestions(
        self,
        path: str,
        repo_root: Path,
    ) -> list[str]:
        """
        Get fuzzy suggestions for a path.

        Uses two strategies:
        1. Fuzzy match on full path
        2. Fuzzy match on filename only (more permissive)

        Teaching:
            gotcha: We limit file scanning to MAX_FILES_SCAN to prevent
                    performance issues on large repos.
        """
        # Get all files in repo (with limit)
        all_files: list[str] = []
        try:
            for i, file_path in enumerate(repo_root.glob("**/*")):
                if i >= MAX_FILES_SCAN:
                    break
                if file_path.is_file():
                    # Skip hidden files and common noise
                    relative = str(file_path.relative_to(repo_root))
                    if not any(part.startswith(".") for part in relative.split("/")):
                        all_files.append(relative)
        except Exception as e:
            logger.warning(f"Error scanning repo for suggestions: {e}")
            return []

        if not all_files:
            return []

        # Strategy 1: Fuzzy match on full path
        suggestions = get_close_matches(path, all_files, n=MAX_SUGGESTIONS, cutoff=0.4)

        # Strategy 2: If no matches, try matching just the filename
        if not suggestions:
            filename = Path(path).name
            filename_matches = get_close_matches(
                filename,
                [Path(f).name for f in all_files],
                n=MAX_SUGGESTIONS * 2,  # Get more, we'll filter
                cutoff=0.4,
            )
            # Map back to full paths
            for match in filename_matches:
                for file_path in all_files:
                    if Path(file_path).name == match and file_path not in suggestions:
                        suggestions.append(file_path)
                        if len(suggestions) >= MAX_SUGGESTIONS:
                            break
                if len(suggestions) >= MAX_SUGGESTIONS:
                    break

        return suggestions[:MAX_SUGGESTIONS]

    async def _invoke_aspect(
        self,
        aspect_name: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Route aspect invocations."""
        match aspect_name:
            case "manifest":
                return await self.manifest(observer)
            case "validate":
                path = kwargs.get("path", "")
                response_format = kwargs.get("response_format", "json")
                return await self.validate(observer, path=path, response_format=response_format)
            case _:
                return BasicRendering(
                    summary=f"Unknown aspect: {aspect_name}",
                    content=f"Available aspects: {', '.join(REPO_AFFORDANCES)}",
                    metadata={"error": "unknown_aspect", "aspect": aspect_name},
                )


# === Module-level accessors ===

_repo_node: RepoNode | None = None


def get_repo_node() -> RepoNode:
    """Get the singleton RepoNode instance."""
    global _repo_node
    if _repo_node is None:
        _repo_node = RepoNode()
    return _repo_node


def set_repo_node(node: RepoNode) -> None:
    """Set the RepoNode instance (for testing)."""
    global _repo_node
    _repo_node = node


def create_repo_node() -> RepoNode:
    """Factory function for creating RepoNode."""
    return RepoNode()


__all__ = [
    "REPO_AFFORDANCES",
    "CREATABLE_EXTENSIONS",
    "RepoNode",
    "get_repo_node",
    "set_repo_node",
    "create_repo_node",
]
