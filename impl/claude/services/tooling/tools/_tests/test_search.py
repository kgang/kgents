"""
Tests for Search Tools: GlobTool, GrepTool.

Test Strategy (T-gent Type II: Delta Tests):
- Each test verifies search behavior and contract translation
- Focus on edge cases: empty results, truncation, invalid patterns

See: docs/skills/test-patterns.md
"""

from __future__ import annotations

import pytest

from services.tooling.base import ToolError
from services.tooling.contracts import GlobQuery, GrepQuery
from services.tooling.tools.search import GlobTool, GrepTool


class TestGlobTool:
    """Tests for GlobTool."""

    async def test_finds_matching_files(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool finds files matching pattern."""
        # Create test files
        (tmp_path / "file1.py").write_text("# Python file 1")  # type: ignore
        (tmp_path / "file2.py").write_text("# Python file 2")  # type: ignore
        (tmp_path / "file3.txt").write_text("Text file")  # type: ignore

        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="*.py", path=str(tmp_path))  # type: ignore
        )

        assert result.count == 2
        assert result.truncated is False
        assert all(".py" in m for m in result.matches)

    async def test_finds_nested_files(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool finds files in nested directories."""
        # Create nested structure
        (tmp_path / "src").mkdir()  # type: ignore
        (tmp_path / "src" / "main.py").write_text("# Main")  # type: ignore
        (tmp_path / "src" / "util").mkdir()  # type: ignore
        (tmp_path / "src" / "util" / "helper.py").write_text("# Helper")  # type: ignore

        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="**/*.py", path=str(tmp_path))  # type: ignore
        )

        assert result.count == 2
        assert any("main.py" in m for m in result.matches)
        assert any("helper.py" in m for m in result.matches)

    async def test_respects_limit(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool truncates results at limit."""
        # Create many files
        for i in range(10):
            (tmp_path / f"file{i}.py").write_text(f"# File {i}")  # type: ignore

        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="*.py", path=str(tmp_path), limit=3)  # type: ignore
        )

        assert result.count == 3
        assert result.truncated is True

    async def test_empty_result(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool returns empty result for no matches."""
        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="*.nonexistent", path=str(tmp_path))  # type: ignore
        )

        assert result.count == 0
        assert result.matches == []
        assert result.truncated is False

    async def test_excludes_directories(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool only returns files, not directories."""
        (tmp_path / "dir.py").mkdir()  # type: ignore
        (tmp_path / "file.py").write_text("# File")  # type: ignore

        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="*.py", path=str(tmp_path))  # type: ignore
        )

        assert result.count == 1
        assert "file.py" in result.matches[0]

    async def test_tool_properties(self) -> None:
        """GlobTool has correct metadata."""
        tool = GlobTool()

        assert tool.name == "search.glob"
        assert tool.trust_required == 0  # L0
        assert tool.cacheable is True


class TestGrepTool:
    """Tests for GrepTool."""

    async def test_finds_matching_content(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool finds content matching pattern."""
        (tmp_path / "file1.py").write_text("def foo():\n    # TODO: fix this\n    pass")  # type: ignore
        (tmp_path / "file2.py").write_text("def bar():\n    pass")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="TODO",
                path=str(tmp_path),  # type: ignore
                glob="*.py",
                output_mode="content",
            )
        )

        assert result.count == 1
        assert "file1.py" in result.matches[0].file_path
        assert "TODO" in result.matches[0].content or ""

    async def test_files_with_matches_mode(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool returns file paths only in files_with_matches mode."""
        (tmp_path / "match1.py").write_text("TODO here")  # type: ignore
        (tmp_path / "match2.py").write_text("TODO there")  # type: ignore
        (tmp_path / "nomatch.py").write_text("nothing special")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="TODO",
                path=str(tmp_path),  # type: ignore
                glob="*.py",
                output_mode="files_with_matches",
            )
        )

        assert result.count == 2
        # In files_with_matches mode, content is None
        file_paths = [m.file_path for m in result.matches]
        assert any("match1.py" in p for p in file_paths)
        assert any("match2.py" in p for p in file_paths)

    async def test_context_lines(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool includes context lines."""
        content = "line1\nline2\nMATCH\nline4\nline5"
        (tmp_path / "context.txt").write_text(content)  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="MATCH",
                path=str(tmp_path),  # type: ignore
                glob="*.txt",
                output_mode="content",
                context_lines=2,
            )
        )

        assert result.count == 1
        match = result.matches[0]
        assert "line2" in match.context_before
        assert "line4" in match.context_after

    async def test_case_insensitive(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool supports case-insensitive search."""
        (tmp_path / "case.txt").write_text("TODO and todo and Todo")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="todo",
                path=str(tmp_path),  # type: ignore
                case_insensitive=True,
                output_mode="content",
            )
        )

        # Should find the line (which contains all three variants)
        assert result.count == 1

    async def test_regex_pattern(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool supports regex patterns."""
        (tmp_path / "regex.py").write_text("def foo():\ndef bar():\ndef baz():")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern=r"def\s+\w+\(\)",
                path=str(tmp_path),  # type: ignore
                output_mode="content",
            )
        )

        assert result.count == 3

    async def test_invalid_regex_raises(self) -> None:
        """GrepTool raises ToolError for invalid regex."""
        tool = GrepTool()

        with pytest.raises(ToolError) as exc_info:
            await tool.invoke(GrepQuery(pattern="[invalid(regex", path="."))

        assert "invalid regex" in str(exc_info.value).lower()

    async def test_respects_limit(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool truncates results at limit."""
        # Create file with many matches
        lines = "\n".join([f"TODO item {i}" for i in range(20)])
        (tmp_path / "many.txt").write_text(lines)  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="TODO",
                path=str(tmp_path),  # type: ignore
                output_mode="content",
                limit=5,
            )
        )

        assert result.count == 5
        assert result.truncated is True

    async def test_skips_binary_files(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool skips binary files gracefully."""
        (tmp_path / "binary.bin").write_bytes(b"\x00\x01\x02\x03")  # type: ignore
        (tmp_path / "text.txt").write_text("searchable content")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="searchable",
                path=str(tmp_path),  # type: ignore
                output_mode="content",
            )
        )

        # Should find text file, skip binary
        assert result.count == 1
        assert "text.txt" in result.matches[0].file_path

    async def test_empty_result(self, tmp_path: pytest.TempPathFactory) -> None:
        """GrepTool returns empty result for no matches."""
        (tmp_path / "file.txt").write_text("nothing special")  # type: ignore

        tool = GrepTool()
        result = await tool.invoke(
            GrepQuery(
                pattern="NOTFOUND",
                path=str(tmp_path),  # type: ignore
            )
        )

        assert result.count == 0
        assert result.matches == []

    async def test_tool_properties(self) -> None:
        """GrepTool has correct metadata."""
        tool = GrepTool()

        assert tool.name == "search.grep"
        assert tool.trust_required == 0  # L0
        assert tool.cacheable is False  # Content may change
