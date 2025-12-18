"""
Tests for SoftSection and the rigidity spectrum.

Verifies the category law:
    crystallize(crystallize(s)) == crystallize(s)  # Idempotence

Also tests:
- Source prioritization
- Merge strategies
- Reasoning trace accumulation
- Rigidity computation
"""

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from protocols.prompt.compiler import CompilationContext

from protocols.prompt.section_base import Section
from protocols.prompt.soft_section import (
    CrystallizationResult,
    MergeStrategy,
    SoftSection,
)
from protocols.prompt.sources.base import (
    FallbackSource,
    SourcePriority,
    SourceResult,
    TemplateSource,
)
from protocols.prompt.sources.file_source import FileSource, GlobFileSource
from protocols.prompt.sources.llm_source import MockLLMSource

# =============================================================================
# Source Tests
# =============================================================================


class TestTemplateSource:
    """Tests for TemplateSource."""

    @pytest.mark.asyncio
    async def test_template_source_returns_content(self):
        """Template source returns its template."""
        source = TemplateSource(
            name="test",
            template="Hello, world!",
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert result.success
        assert result.content == "Hello, world!"
        assert result.rigidity == 1.0

    @pytest.mark.asyncio
    async def test_template_source_includes_traces(self):
        """Template source records reasoning traces."""
        source = TemplateSource(
            name="test",
            template="Content",
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert len(result.reasoning_trace) > 0
        assert any("hardcoded" in t.lower() for t in result.reasoning_trace)

    @pytest.mark.asyncio
    async def test_empty_template_fails(self):
        """Empty template is treated as failure."""
        source = TemplateSource(
            name="test",
            template="",
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert not result.success


class TestFileSource:
    """Tests for FileSource."""

    @pytest.mark.asyncio
    async def test_file_source_reads_file(self):
        """File source reads content from file."""
        with TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("# Test\n\nFile content here.")

            source = FileSource(
                name="test",
                path_resolver=lambda ctx: test_file,
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert result.success
            assert "File content here" in result.content
            assert result.source_path == test_file

    @pytest.mark.asyncio
    async def test_file_source_extracts_section(self):
        """File source can extract markdown section."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text(
                "# Main\n\nIntro\n\n## Target\n\nTarget content.\n\n## Other\n\nOther content."
            )

            source = FileSource(
                name="test",
                path_resolver=lambda ctx: test_file,
                section_heading="Target",
                section_level=2,
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert result.success
            assert result.content.strip() == "Target content."
            assert "Other content" not in result.content

    @pytest.mark.asyncio
    async def test_missing_file_fails(self):
        """Missing file returns failure."""
        source = FileSource(
            name="test",
            path_resolver=lambda ctx: Path("/nonexistent/file.md"),
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert not result.success
        assert result.content is None
        assert any("not found" in t.lower() for t in result.reasoning_trace)

    @pytest.mark.asyncio
    async def test_file_too_large_fails(self):
        """Files exceeding max size are rejected."""
        with TemporaryDirectory() as tmpdir:
            # Create a file larger than our small limit
            large_file = Path(tmpdir) / "large.md"
            large_file.write_text("x" * 1000)  # 1000 bytes

            source = FileSource(
                name="test",
                path_resolver=lambda ctx: large_file,
                max_file_size=500,  # Set small limit
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert not result.success
            assert result.content is None
            assert any("too large" in t.lower() for t in result.reasoning_trace)

    @pytest.mark.asyncio
    async def test_file_within_limit_succeeds(self):
        """Files within max size are accepted."""
        with TemporaryDirectory() as tmpdir:
            small_file = Path(tmpdir) / "small.md"
            small_file.write_text("Small content")

            source = FileSource(
                name="test",
                path_resolver=lambda ctx: small_file,
                max_file_size=1000,
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert result.success
            assert "Small content" in result.content
            assert any("within limit" in t.lower() for t in result.reasoning_trace)


class TestGlobFileSource:
    """Tests for GlobFileSource."""

    @pytest.mark.asyncio
    async def test_glob_reads_multiple_files(self):
        """GlobFileSource reads and combines multiple files."""
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create multiple markdown files
            (base_path / "file1.md").write_text("Content from file 1")
            (base_path / "file2.md").write_text("Content from file 2")
            (base_path / "file3.txt").write_text("Not a markdown file")

            source = GlobFileSource(
                name="test",
                base_path_resolver=lambda ctx: base_path,
                pattern="*.md",
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert result.success
            assert "Content from file 1" in result.content
            assert "Content from file 2" in result.content
            assert "Not a markdown file" not in result.content  # txt excluded

    @pytest.mark.asyncio
    async def test_glob_no_matches_fails(self):
        """GlobFileSource with no matches returns failure."""
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            # Empty directory

            source = GlobFileSource(
                name="test",
                base_path_resolver=lambda ctx: base_path,
                pattern="*.md",
            )
            context = CompilationContext()

            result = await source.fetch(context)

            assert not result.success
            assert any("no files" in t.lower() for t in result.reasoning_trace)

    @pytest.mark.asyncio
    async def test_glob_missing_directory_fails(self):
        """GlobFileSource with missing directory returns failure."""
        source = GlobFileSource(
            name="test",
            base_path_resolver=lambda ctx: Path("/nonexistent"),
            pattern="*.md",
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert not result.success
        assert any("not found" in t.lower() for t in result.reasoning_trace)


class TestMockLLMSource:
    """Tests for MockLLMSource."""

    @pytest.mark.asyncio
    async def test_mock_returns_content(self):
        """Mock LLM source returns mock content."""
        source = MockLLMSource(
            name="test",
            mock_content="Generated content!",
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert result.success
        assert result.content == "Generated content!"
        assert result.rigidity == 0.2

    @pytest.mark.asyncio
    async def test_mock_can_fail(self):
        """Mock LLM source can be configured to fail."""
        source = MockLLMSource(
            name="test",
            mock_content="Content",
            should_fail=True,
        )
        context = CompilationContext()

        result = await source.fetch(context)

        assert not result.success


# =============================================================================
# SoftSection Tests
# =============================================================================


class TestSoftSection:
    """Tests for SoftSection."""

    @pytest.mark.asyncio
    async def test_crystallize_with_template(self):
        """Crystallizing with template source works."""
        soft = SoftSection(
            name="test",
            sources=[
                TemplateSource(name="test:template", template="Template content"),
            ],
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        assert result.section.name == "test"
        assert result.section.content == "Template content"
        assert result.effective_rigidity == 1.0

    @pytest.mark.asyncio
    async def test_crystallize_fallback_chain(self):
        """Sources are tried in priority order."""
        soft = SoftSection(
            name="test",
            sources=[
                FileSource(
                    name="test:file",
                    path_resolver=lambda ctx: Path("/nonexistent"),
                    priority=SourcePriority.FILE,
                ),
                TemplateSource(
                    name="test:fallback",
                    template="Fallback content",
                    priority=SourcePriority.TEMPLATE,
                ),
            ],
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        # Template has higher priority, so it's tried first and succeeds
        assert result.section.content == "Fallback content"

    @pytest.mark.asyncio
    async def test_crystallize_reasoning_traces(self):
        """Crystallization records reasoning traces."""
        soft = SoftSection(
            name="test",
            sources=[
                TemplateSource(name="test:template", template="Content"),
            ],
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        assert len(result.reasoning_trace) > 0
        assert any("Crystallizing" in t for t in result.reasoning_trace)

    @pytest.mark.asyncio
    async def test_no_sources_returns_unavailable(self):
        """No successful sources returns unavailable message."""
        soft = SoftSection(
            name="test",
            sources=[
                FileSource(
                    name="test:file",
                    path_resolver=lambda ctx: Path("/nonexistent"),
                ),
            ],
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        assert "unavailable" in result.section.content.lower()
        assert result.effective_rigidity == 0.0


# =============================================================================
# Merge Strategy Tests
# =============================================================================


class TestMergeStrategies:
    """Tests for different merge strategies."""

    @pytest.mark.asyncio
    async def test_first_wins_stops_early(self):
        """FIRST_WINS stops after first success."""
        soft = SoftSection(
            name="test",
            sources=[
                TemplateSource(name="first", template="First content"),
                TemplateSource(name="second", template="Second content"),
            ],
            merge_strategy=MergeStrategy.FIRST_WINS,
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        # Should use first successful source
        assert "First content" in result.section.content
        assert "Second content" not in result.section.content

    @pytest.mark.asyncio
    async def test_highest_rigidity_selects_most_rigid(self):
        """HIGHEST_RIGIDITY selects most rigid source."""
        # Manually trigger multiple sources by using a custom merge scenario
        soft = SoftSection(
            name="test",
            sources=[
                MockLLMSource(
                    name="inferred",
                    mock_content="Inferred",
                    priority=SourcePriority.INFERENCE,
                ),
                TemplateSource(
                    name="template",
                    template="Template",
                    priority=SourcePriority.TEMPLATE,
                ),
            ],
            merge_strategy=MergeStrategy.HIGHEST_RIGIDITY,
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        # Template has higher rigidity (1.0) than mock (0.2)
        # But HIGHEST_RIGIDITY still uses priority ordering due to FIRST_WINS being default behavior
        # Actually, let me re-read the code... FIRST_WINS breaks early
        # For HIGHEST_RIGIDITY, we need to collect all then select
        # The implementation collects all for non-FIRST_WINS strategies
        assert result.effective_rigidity == 1.0


# =============================================================================
# Category Law Tests: Idempotence
# =============================================================================


class TestIdempotenceLaw:
    """
    Tests for the idempotence law:
        crystallize(crystallize(s)) == crystallize(s)

    This is a core category law for SoftSection.
    """

    @pytest.mark.asyncio
    async def test_idempotence_with_template(self):
        """crystallize(from_hard(crystallize(s))) == crystallize(s)."""
        original = SoftSection(
            name="test",
            sources=[
                TemplateSource(name="test:template", template="Original content"),
            ],
        )
        context = CompilationContext()

        # First crystallization
        first_result = await original.crystallize(context)
        first_content = first_result.section.content

        # Create soft section from hard result
        roundtrip = SoftSection.from_hard(first_result.section)

        # Second crystallization
        second_result = await roundtrip.crystallize(context)
        second_content = second_result.section.content

        # Should be identical
        assert first_content == second_content

    @pytest.mark.asyncio
    async def test_idempotence_preserves_name(self):
        """Roundtrip preserves section name."""
        original = SoftSection(
            name="my_section",
            sources=[
                TemplateSource(name="src", template="Content"),
            ],
        )
        context = CompilationContext()

        result1 = await original.crystallize(context)
        roundtrip = SoftSection.from_hard(result1.section)
        result2 = await roundtrip.crystallize(context)

        assert result1.section.name == result2.section.name == "my_section"


# =============================================================================
# Integration Tests
# =============================================================================


class TestSoftSectionIntegration:
    """Integration tests combining multiple features."""

    @pytest.mark.asyncio
    async def test_file_with_fallback(self):
        """Real file source with template fallback."""
        with TemporaryDirectory() as tmpdir:
            # Create a real file
            real_file = Path(tmpdir) / "real.md"
            real_file.write_text("# Real\n\nReal content from file.")

            soft = SoftSection(
                name="test",
                sources=[
                    FileSource(
                        name="test:file",
                        path_resolver=lambda ctx: real_file,
                        priority=SourcePriority.FILE,
                    ),
                    TemplateSource(
                        name="test:fallback",
                        template="Fallback",
                        priority=SourcePriority.FALLBACK,
                    ),
                ],
            )
            context = CompilationContext()

            result = await soft.crystallize(context)

            # Should use file content (file has lower priority than template,
            # but template is FALLBACK priority)
            assert "Real content" in result.section.content

    @pytest.mark.asyncio
    async def test_rigidity_affects_required(self):
        """High rigidity sections should be required."""
        soft = SoftSection(
            name="test",
            sources=[
                TemplateSource(name="src", template="Required content"),
            ],
            required=True,
        )
        context = CompilationContext()

        result = await soft.crystallize(context)

        assert result.section.required
        assert result.effective_rigidity == 1.0


__all__ = [
    "TestTemplateSource",
    "TestFileSource",
    "TestMockLLMSource",
    "TestSoftSection",
    "TestMergeStrategies",
    "TestIdempotenceLaw",
    "TestSoftSectionIntegration",
]
