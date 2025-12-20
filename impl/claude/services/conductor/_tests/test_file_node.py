"""
Tests for FileNode AGENTESE integration.

CLI v7 Phase 1: File I/O Primitives

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Node creation and affordances
- Type II (Integration): Node + FileEditGuard
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

# =============================================================================
# Fixtures
# =============================================================================


@dataclass
class MockMeta:
    """Mock observer metadata."""

    name: str = "test_agent"
    archetype: str = "developer"


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    meta: MockMeta = field(default_factory=MockMeta)


@pytest.fixture
def temp_file() -> Path:
    """Create a temporary file with test content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def hello():\n    return 'world'\n\ndef goodbye():\n    return 'friend'\n")
        return Path(f.name)


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory with test files."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)
        # Create some test files
        (path / "file1.py").write_text("# Python file 1\n")
        (path / "file2.py").write_text("# Python file 2\n")
        (path / "data.json").write_text('{"key": "value"}\n')
        yield path


# =============================================================================
# Type I: Unit Tests
# =============================================================================


class TestFileNodeBasic:
    """Basic unit tests for FileNode."""

    def test_create_node(self) -> None:
        """Node creates with correct handle."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        assert node.handle == "world.file"

    def test_affordances(self) -> None:
        """Node exposes correct affordances."""
        from protocols.agentese.contexts.world_file import (
            FILE_AFFORDANCES,
            FileNode,
        )

        node = FileNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert affordances == FILE_AFFORDANCES
        assert "manifest" in affordances
        assert "read" in affordances
        assert "edit" in affordances
        assert "write" in affordances
        assert "glob" in affordances
        assert "grep" in affordances

    def test_factory_function(self) -> None:
        """Factory creates FileNode."""
        from protocols.agentese.contexts.world_file import (
            FileNode,
            create_file_node,
        )

        node = create_file_node()
        assert isinstance(node, FileNode)


class TestFileNodeRegistration:
    """Tests for AGENTESE registry integration."""

    def test_node_registers_on_import(self) -> None:
        """Node registers with AGENTESE registry on import."""
        # Import to trigger registration
        from protocols.agentese.contexts.world_file import FileNode  # noqa: F401
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        node = registry.get("world.file")

        assert node is not None
        if isinstance(node, type):
            assert node.__name__ == "FileNode"
        else:
            assert type(node).__name__ == "FileNode"


# =============================================================================
# Type II: Integration Tests - Manifest
# =============================================================================


class TestFileNodeManifest:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(self) -> None:
        """Manifest returns valid rendering."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node.manifest(observer)

        assert "File I/O" in result.summary
        assert "Claude Code" in result.content
        assert "read" in result.content.lower()
        assert "edit" in result.content.lower()
        assert "affordances" in result.metadata


# =============================================================================
# Type II: Integration Tests - Read Aspect
# =============================================================================


class TestFileNodeRead:
    """Tests for read aspect."""

    @pytest.mark.asyncio
    async def test_read_requires_path(self) -> None:
        """Read returns error when path not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("read", observer)

        assert result["status"] == "error"
        assert result["error"] == "path_required"

    @pytest.mark.asyncio
    async def test_read_success(self, temp_file: Path) -> None:
        """Read returns file content."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("read", observer, path=str(temp_file))

        assert result["status"] == "success"
        assert "def hello" in result["content"]
        assert result["size"] > 0
        assert result["lines"] > 0

    @pytest.mark.asyncio
    async def test_read_not_found(self) -> None:
        """Read returns error for nonexistent file."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("read", observer, path="/nonexistent/file.py")

        assert result["status"] == "error"
        assert result["error"] == "not_found"


# =============================================================================
# Type II: Integration Tests - Edit Aspect
# =============================================================================


class TestFileNodeEdit:
    """Tests for edit aspect."""

    @pytest.mark.asyncio
    async def test_edit_requires_path(self) -> None:
        """Edit returns error when path not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "edit",
            observer,
            old_string="foo",
            new_string="bar",
        )

        assert result["status"] == "error"
        assert result["error"] == "path_required"

    @pytest.mark.asyncio
    async def test_edit_requires_old_string(self) -> None:
        """Edit returns error when old_string not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "edit",
            observer,
            path="/test.py",
            new_string="bar",
        )

        assert result["status"] == "error"
        assert result["error"] == "old_string_required"

    @pytest.mark.asyncio
    async def test_edit_without_read_fails(self, temp_file: Path) -> None:
        """Edit fails if file wasn't read first."""
        from protocols.agentese.contexts.world_file import FileNode
        from services.conductor.file_guard import reset_file_guard

        reset_file_guard()  # Ensure clean state
        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "edit",
            observer,
            path=str(temp_file),
            old_string="def hello",
            new_string="def hi",
        )

        assert result["status"] == "error"
        assert result["error"] == "not_read"
        assert "suggestion" in result

    @pytest.mark.asyncio
    async def test_edit_after_read_succeeds(self, temp_file: Path) -> None:
        """Edit succeeds after reading file."""
        from protocols.agentese.contexts.world_file import FileNode
        from services.conductor.file_guard import reset_file_guard

        reset_file_guard()  # Ensure clean state
        node = FileNode()
        observer = MockUmwelt()

        # Read first
        await node._invoke_aspect("read", observer, path=str(temp_file))

        # Then edit
        result = await node._invoke_aspect(
            "edit",
            observer,
            path=str(temp_file),
            old_string="def hello",
            new_string="def hi",
        )

        assert result["status"] == "success"
        assert result["replacements"] == 1

        # Verify file changed
        content = temp_file.read_text()
        assert "def hi" in content


# =============================================================================
# Type II: Integration Tests - Write Aspect
# =============================================================================


class TestFileNodeWrite:
    """Tests for write aspect."""

    @pytest.mark.asyncio
    async def test_write_requires_path(self) -> None:
        """Write returns error when path not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("write", observer, content="hello")

        assert result["status"] == "error"
        assert result["error"] == "path_required"

    @pytest.mark.asyncio
    async def test_write_requires_content(self) -> None:
        """Write returns error when content not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("write", observer, path="/test.py")

        assert result["status"] == "error"
        assert result["error"] == "content_required"

    @pytest.mark.asyncio
    async def test_write_success(self, temp_dir: Path) -> None:
        """Write creates new file."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()
        new_file = temp_dir / "new_file.txt"

        result = await node._invoke_aspect(
            "write",
            observer,
            path=str(new_file),
            content="Hello, world!",
        )

        assert result["status"] == "success"
        assert result["size"] == len("Hello, world!")
        assert new_file.exists()


# =============================================================================
# Type II: Integration Tests - Glob Aspect
# =============================================================================


class TestFileNodeGlob:
    """Tests for glob aspect."""

    @pytest.mark.asyncio
    async def test_glob_requires_pattern(self) -> None:
        """Glob returns error when pattern not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("glob", observer)

        assert result["status"] == "error"
        assert result["error"] == "pattern_required"

    @pytest.mark.asyncio
    async def test_glob_finds_files(self, temp_dir: Path) -> None:
        """Glob finds matching files."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "glob",
            observer,
            pattern="*.py",
            root=str(temp_dir),
        )

        assert result["status"] == "success"
        assert len(result["matches"]) == 2
        assert result["total"] == 2


# =============================================================================
# Type II: Integration Tests - Grep Aspect
# =============================================================================


class TestFileNodeGrep:
    """Tests for grep aspect."""

    @pytest.mark.asyncio
    async def test_grep_requires_pattern(self) -> None:
        """Grep returns error when pattern not provided."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("grep", observer)

        assert result["status"] == "error"
        assert result["error"] == "pattern_required"

    @pytest.mark.asyncio
    async def test_grep_finds_matches(self, temp_dir: Path) -> None:
        """Grep finds matching content."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "grep",
            observer,
            pattern="Python file",
            path=str(temp_dir),
        )

        assert result["status"] == "success"
        assert len(result["matches"]) == 2

    @pytest.mark.asyncio
    async def test_grep_returns_context(self, temp_file: Path) -> None:
        """Grep returns context lines."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "grep",
            observer,
            pattern="def hello",
            path=str(temp_file.parent),
            glob="*.py",
            context_lines=1,
        )

        assert result["status"] == "success"
        if result["matches"]:
            match = result["matches"][0]
            assert "line_number" in match
            assert "content" in match

    @pytest.mark.asyncio
    async def test_grep_invalid_regex(self, temp_dir: Path) -> None:
        """Grep returns error for invalid regex."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect(
            "grep",
            observer,
            pattern="[invalid",  # Unclosed bracket
            path=str(temp_dir),
        )

        assert result["status"] == "error"
        assert result["error"] == "invalid_pattern"


# =============================================================================
# Type II: Integration Tests - Unknown Aspect
# =============================================================================


class TestFileNodeUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect(self) -> None:
        """Unknown aspect returns not implemented."""
        from protocols.agentese.contexts.world_file import FileNode

        node = FileNode()
        observer = MockUmwelt()

        result = await node._invoke_aspect("unknown", observer)

        assert result["status"] == "not implemented"
