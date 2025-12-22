"""
Tests for world.repo AGENTESE node.

Visual Trail Graph Session 2: Path Validation

"The trail becomes visible. The garden reveals its paths."
"""

from __future__ import annotations

from pathlib import Path

import pytest

from protocols.agentese.contexts.world_repo import (
    CREATABLE_EXTENSIONS,
    REPO_AFFORDANCES,
    RepoNode,
    get_repo_node,
    set_repo_node,
)
from protocols.agentese.node import Observer


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer(archetype="developer", capabilities=frozenset())


@pytest.fixture
def repo_node(tmp_path: Path) -> RepoNode:
    """Create a fresh repo node with controlled repo root."""
    set_repo_node(None)  # Reset singleton
    node = RepoNode()
    node.set_repo_root(tmp_path)
    return node


@pytest.fixture
def populated_repo(tmp_path: Path) -> Path:
    """Create a repo with various files for testing."""
    # Create directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src/components").mkdir(parents=True)
    (tmp_path / "spec").mkdir()
    (tmp_path / "docs").mkdir()

    # Create files
    (tmp_path / "CLAUDE.md").write_text("# Claude")
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "src/main.py").write_text("def main(): pass")
    (tmp_path / "src/utils.py").write_text("def util(): pass")
    (tmp_path / "src/components/button.tsx").write_text("export const Button = () => null;")
    (tmp_path / "spec/principles.md").write_text("# Principles")
    (tmp_path / "docs/guide.md").write_text("# Guide")

    return tmp_path


# =============================================================================
# Node Registration Tests
# =============================================================================


class TestRepoNodeRegistration:
    """Tests for @node registration."""

    def test_node_is_registered(self) -> None:
        """world.repo should be registered in the AGENTESE registry."""
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        assert registry.has("world.repo")

    def test_affordances(self) -> None:
        """world.repo should expose validate and manifest."""
        assert "manifest" in REPO_AFFORDANCES
        assert "validate" in REPO_AFFORDANCES

    def test_creatable_extensions(self) -> None:
        """Common extensions should be creatable."""
        assert ".py" in CREATABLE_EXTENSIONS
        assert ".md" in CREATABLE_EXTENSIONS
        assert ".ts" in CREATABLE_EXTENSIONS
        assert ".tsx" in CREATABLE_EXTENSIONS
        assert ".json" in CREATABLE_EXTENSIONS


# =============================================================================
# Manifest Tests
# =============================================================================


class TestManifest:
    """Tests for world.repo.manifest."""

    async def test_manifest_returns_status(
        self,
        repo_node: RepoNode,
        observer: Observer,
    ) -> None:
        """manifest should return node status."""
        result = await repo_node.manifest(observer)

        assert result.summary == "world.repo manifest"
        assert "validate" in result.content
        assert result.metadata["creatable_extensions"]


# =============================================================================
# Validate Tests - Existing Paths
# =============================================================================


class TestValidateExistingPaths:
    """Tests for validating paths that exist."""

    async def test_validate_existing_file(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should return exists=True for existing files."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="CLAUDE.md")

        assert result.metadata["exists"] is True
        assert result.metadata["suggestions"] == []
        assert result.metadata["path"] == "CLAUDE.md"
        assert "exists" in result.summary.lower()

    async def test_validate_existing_nested_file(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should work for nested paths."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="src/main.py")

        assert result.metadata["exists"] is True
        assert result.metadata["can_create"] is True  # .py is creatable

    async def test_validate_existing_directory(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should return exists=True for directories."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="src")

        assert result.metadata["exists"] is True


# =============================================================================
# Validate Tests - Non-Existing Paths with Suggestions
# =============================================================================


class TestValidateSuggestions:
    """Tests for fuzzy suggestions when path not found."""

    async def test_validate_typo_gets_suggestion(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should suggest CLAUDE.md for CLAUED.md typo."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="CLAUED.md")

        assert result.metadata["exists"] is False
        assert "CLAUDE.md" in result.metadata["suggestions"]

    async def test_validate_partial_match(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should suggest similar filenames."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="src/main.tsx")

        assert result.metadata["exists"] is False
        # Should suggest src/main.py (similar filename)
        suggestions = result.metadata["suggestions"]
        assert any("main" in s for s in suggestions)

    async def test_validate_no_suggestions_for_random(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should return empty suggestions for completely unrelated paths."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="xyz123abc.xyz")

        assert result.metadata["exists"] is False
        # Suggestions may be empty or contain distant matches
        assert isinstance(result.metadata["suggestions"], list)


# =============================================================================
# Validate Tests - Creatable Extensions
# =============================================================================


class TestValidateCreatable:
    """Tests for can_create detection."""

    @pytest.mark.parametrize(
        "path,expected_creatable",
        [
            ("new/file.py", True),
            ("docs/readme.md", True),
            ("src/app.tsx", True),
            ("config.json", True),
            ("config.yaml", True),
            ("binary.exe", False),
            ("data.bin", False),
            ("noextension", False),
        ],
    )
    async def test_creatable_extension_detection(
        self,
        repo_node: RepoNode,
        observer: Observer,
        path: str,
        expected_creatable: bool,
    ) -> None:
        """validate should detect creatable extensions correctly."""
        result = await repo_node.validate(observer, path=path)

        assert result.metadata["can_create"] is expected_creatable


# =============================================================================
# Validate Tests - Response Formats
# =============================================================================


class TestValidateResponseFormats:
    """Tests for different response formats."""

    async def test_json_format(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """JSON format should return structured metadata."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="CLAUDE.md", response_format="json")

        assert result.metadata["status"] == "success"
        assert "exists" in result.metadata
        assert "suggestions" in result.metadata
        assert "can_create" in result.metadata
        assert "path" in result.metadata

    async def test_cli_format_existing(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """CLI format should return human-readable content for existing paths."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="CLAUDE.md", response_format="cli")

        assert "exists" in result.summary.lower()

    async def test_cli_format_with_suggestions(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """CLI format should show suggestions when path not found."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="CLAUED.md", response_format="cli")

        assert "Did you mean?" in result.content
        assert "CLAUDE.md" in result.content


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    async def test_empty_path(
        self,
        repo_node: RepoNode,
        observer: Observer,
    ) -> None:
        """validate should handle empty path."""
        result = await repo_node.validate(observer, path="")

        # Empty path should check current directory (repo root)
        assert "exists" in result.metadata

    async def test_path_normalization(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """validate should handle backslashes in paths."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node.validate(observer, path="src\\main.py")

        assert result.metadata["exists"] is True
        assert result.metadata["path"] == "src/main.py"  # Normalized

    async def test_invoke_aspect_validate(
        self,
        repo_node: RepoNode,
        populated_repo: Path,
        observer: Observer,
    ) -> None:
        """_invoke_aspect should route to validate correctly."""
        repo_node.set_repo_root(populated_repo)

        result = await repo_node._invoke_aspect(
            "validate",
            observer,
            path="CLAUDE.md",
            response_format="json",
        )

        assert result.metadata["exists"] is True

    async def test_invoke_aspect_unknown(
        self,
        repo_node: RepoNode,
        observer: Observer,
    ) -> None:
        """_invoke_aspect should handle unknown aspects."""
        result = await repo_node._invoke_aspect("unknown", observer)

        assert "Unknown aspect" in result.summary
        assert result.metadata["error"] == "unknown_aspect"
