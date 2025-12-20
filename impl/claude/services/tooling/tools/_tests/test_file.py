"""
Tests for File Tools: ReadTool, WriteTool, EditTool.

Test Strategy (T-gent Type II: Delta Tests):
- Each test verifies adapter behavior, not FileEditGuard internals
- Focus on contract translation and error wrapping
- FileEditGuard's own tests cover the core logic

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import pytest

from services.conductor.file_guard import get_file_guard, reset_file_guard
from services.tooling.base import CausalityViolation, ToolError
from services.tooling.contracts import EditRequest, ReadRequest, WriteRequest
from services.tooling.tools.file import EditTool, ReadTool, WriteTool


@pytest.fixture(autouse=True)
def reset_guard() -> None:
    """Reset FileEditGuard singleton between tests."""
    reset_file_guard()


class TestReadTool:
    """Tests for ReadTool adapter."""

    async def test_reads_file_content(self, tmp_path: pytest.TempPathFactory) -> None:
        """ReadTool reads file and returns FileContent."""
        file = tmp_path / "test.txt"  # type: ignore
        file.write_text("hello world")

        tool = ReadTool()
        result = await tool.invoke(ReadRequest(file_path=str(file)))

        assert result.path == str(file)
        assert result.content == "hello world"
        assert result.line_count == 1
        assert result.truncated is False

    async def test_reads_multiline_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """ReadTool correctly counts lines."""
        file = tmp_path / "multi.txt"  # type: ignore
        file.write_text("line1\nline2\nline3")

        tool = ReadTool()
        result = await tool.invoke(ReadRequest(file_path=str(file)))

        assert result.line_count == 3
        assert "line1" in result.content
        assert "line3" in result.content

    async def test_raises_on_not_found(self, tmp_path: pytest.TempPathFactory) -> None:
        """ReadTool raises ToolError for missing file."""
        tool = ReadTool()

        with pytest.raises(ToolError) as exc_info:
            await tool.invoke(ReadRequest(file_path=str(tmp_path / "missing.txt")))  # type: ignore

        assert exc_info.value.tool_name == "file.read"

    async def test_tool_properties(self) -> None:
        """ReadTool has correct metadata."""
        tool = ReadTool()

        assert tool.name == "file.read"
        assert tool.trust_required == 0  # L0
        assert tool.cacheable is True
        assert len(tool.effects) == 1
        assert tool.effects[0][0].value == "reads"


class TestWriteTool:
    """Tests for WriteTool adapter."""

    async def test_writes_new_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """WriteTool creates new file."""
        file = tmp_path / "new.txt"  # type: ignore

        tool = WriteTool()
        result = await tool.invoke(WriteRequest(file_path=str(file), content="new content"))

        assert result.success is True
        assert result.path == str(file)
        assert result.bytes_written == len("new content")
        assert result.created is True
        assert file.read_text() == "new content"

    async def test_overwrites_existing_file(self, tmp_path: pytest.TempPathFactory) -> None:
        """WriteTool overwrites existing file."""
        file = tmp_path / "existing.txt"  # type: ignore
        file.write_text("original")

        tool = WriteTool()
        result = await tool.invoke(WriteRequest(file_path=str(file), content="updated"))

        assert result.success is True
        assert result.created is False
        assert file.read_text() == "updated"

    async def test_creates_parent_dirs(self, tmp_path: pytest.TempPathFactory) -> None:
        """WriteTool creates parent directories."""
        file = tmp_path / "deep" / "nested" / "file.txt"  # type: ignore

        tool = WriteTool()
        result = await tool.invoke(WriteRequest(file_path=str(file), content="nested content"))

        assert result.success is True
        assert file.exists()
        assert file.read_text() == "nested content"

    async def test_tool_properties(self) -> None:
        """WriteTool has correct metadata."""
        tool = WriteTool()

        assert tool.name == "file.write"
        assert tool.trust_required == 2  # L2
        assert tool.cacheable is False
        assert len(tool.effects) == 1
        assert tool.effects[0][0].value == "writes"


class TestEditTool:
    """Tests for EditTool adapter."""

    async def test_edits_file_after_read(self, tmp_path: pytest.TempPathFactory) -> None:
        """EditTool succeeds when file was read first."""
        file = tmp_path / "edit.txt"  # type: ignore
        file.write_text("def foo():\n    pass")

        # Must read first (Claude Code pattern)
        read_tool = ReadTool()
        await read_tool.invoke(ReadRequest(file_path=str(file)))

        # Now edit succeeds
        edit_tool = EditTool()
        result = await edit_tool.invoke(
            EditRequest(
                file_path=str(file),
                old_string="def foo",
                new_string="def bar",
            )
        )

        assert result.success is True
        assert result.replacements == 1
        assert file.read_text() == "def bar():\n    pass"

    async def test_fails_without_read(self, tmp_path: pytest.TempPathFactory) -> None:
        """EditTool raises CausalityViolation without prior read."""
        file = tmp_path / "no_read.txt"  # type: ignore
        file.write_text("content")

        tool = EditTool()

        with pytest.raises(CausalityViolation) as exc_info:
            await tool.invoke(
                EditRequest(
                    file_path=str(file),
                    old_string="content",
                    new_string="updated",
                )
            )

        assert "not read before edit" in str(exc_info.value).lower()
        assert exc_info.value.tool_name == "file.edit"

    async def test_fails_string_not_found(self, tmp_path: pytest.TempPathFactory) -> None:
        """EditTool raises ToolError when string not found."""
        file = tmp_path / "not_found.txt"  # type: ignore
        file.write_text("hello world")

        # Read first
        await ReadTool().invoke(ReadRequest(file_path=str(file)))

        tool = EditTool()

        with pytest.raises(ToolError) as exc_info:
            await tool.invoke(
                EditRequest(
                    file_path=str(file),
                    old_string="nonexistent",
                    new_string="new",
                )
            )

        assert "not found" in str(exc_info.value).lower()

    async def test_fails_string_not_unique(self, tmp_path: pytest.TempPathFactory) -> None:
        """EditTool raises ToolError when string appears multiple times."""
        file = tmp_path / "not_unique.txt"  # type: ignore
        file.write_text("foo bar foo")

        # Read first
        await ReadTool().invoke(ReadRequest(file_path=str(file)))

        tool = EditTool()

        with pytest.raises(ToolError) as exc_info:
            await tool.invoke(
                EditRequest(
                    file_path=str(file),
                    old_string="foo",
                    new_string="baz",
                )
            )

        assert "replace_all" in str(exc_info.value).lower()

    async def test_replace_all_succeeds(self, tmp_path: pytest.TempPathFactory) -> None:
        """EditTool with replace_all replaces all occurrences."""
        file = tmp_path / "replace_all.txt"  # type: ignore
        file.write_text("foo bar foo baz foo")

        # Read first
        await ReadTool().invoke(ReadRequest(file_path=str(file)))

        tool = EditTool()
        result = await tool.invoke(
            EditRequest(
                file_path=str(file),
                old_string="foo",
                new_string="qux",
                replace_all=True,
            )
        )

        assert result.success is True
        assert result.replacements == 3
        assert file.read_text() == "qux bar qux baz qux"

    async def test_tool_properties(self) -> None:
        """EditTool has correct metadata."""
        tool = EditTool()

        assert tool.name == "file.edit"
        assert tool.trust_required == 2  # L2
        assert tool.cacheable is False
        assert len(tool.effects) == 1
        assert tool.effects[0][0].value == "writes"
