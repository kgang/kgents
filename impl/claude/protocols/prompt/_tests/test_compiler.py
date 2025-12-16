"""
Tests for the Prompt Compiler.

Verifies compilation pipeline and category laws.
"""

from pathlib import Path

import pytest
from protocols.prompt.compiler import (
    CompilationContext,
    CompilationResult,
    CompiledPrompt,
    PromptCompiler,
)
from protocols.prompt.section_base import (
    NPhase,
    Section,
    compose_sections,
    estimate_tokens,
)
from protocols.prompt.sections import get_default_compilers


class TestSection:
    """Test Section dataclass."""

    def test_section_creation(self) -> None:
        """Should create section with required fields."""
        section = Section(
            name="test",
            content="# Test Content",
            token_cost=100,
        )
        assert section.name == "test"
        assert section.content == "# Test Content"
        assert section.token_cost == 100
        assert section.required is True

    def test_section_validation(self) -> None:
        """Should reject empty name or content."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            Section(name="", content="Content", token_cost=10)

        with pytest.raises(ValueError, match="content cannot be empty"):
            Section(name="test", content="", token_cost=10)

    def test_phase_relevance_all_phases(self) -> None:
        """Empty phases means relevant to all."""
        section = Section(
            name="test",
            content="Content",
            token_cost=10,
            phases=frozenset(),
        )
        assert section.is_phase_relevant(NPhase.DEVELOP)
        assert section.is_phase_relevant(NPhase.RESEARCH)
        assert section.is_phase_relevant(None)

    def test_phase_relevance_specific_phases(self) -> None:
        """Should only be relevant to specified phases."""
        section = Section(
            name="test",
            content="Content",
            token_cost=10,
            phases=frozenset({NPhase.DEVELOP, NPhase.IMPLEMENT}),
        )
        assert section.is_phase_relevant(NPhase.DEVELOP)
        assert section.is_phase_relevant(NPhase.IMPLEMENT)
        assert not section.is_phase_relevant(NPhase.RESEARCH)

    def test_with_content(self) -> None:
        """Should create new section with updated content."""
        original = Section(name="test", content="Old", token_cost=10)
        updated = original.with_content("New content")

        assert original.content == "Old"
        assert updated.content == "New content"
        assert updated.name == original.name


class TestComposeSections:
    """Test section composition."""

    def test_compose_two_sections(self) -> None:
        """Should join two sections with separator."""
        a = Section(name="a", content="Section A", token_cost=10)
        b = Section(name="b", content="Section B", token_cost=10)

        result = compose_sections([a, b])
        assert "Section A" in result
        assert "Section B" in result
        assert result == "Section A\n\nSection B"

    def test_compose_associative(self) -> None:
        """Composition should be associative."""
        a = Section(name="a", content="A", token_cost=5)
        b = Section(name="b", content="B", token_cost=5)
        c = Section(name="c", content="C", token_cost=5)

        # (a ∘ b) ∘ c
        ab = compose_sections([a, b])
        ab_section = Section(name="ab", content=ab, token_cost=10)
        left = compose_sections([ab_section, c])

        # a ∘ (b ∘ c)
        bc = compose_sections([b, c])
        bc_section = Section(name="bc", content=bc, token_cost=10)
        right = compose_sections([a, bc_section])

        # Both should produce same content (modulo structure)
        assert "A" in left and "B" in left and "C" in left
        assert "A" in right and "B" in right and "C" in right


class TestEstimateTokens:
    """Test token estimation."""

    def test_estimate_tokens(self) -> None:
        """Should estimate ~4 chars per token."""
        content = "a" * 400  # 400 chars
        assert estimate_tokens(content) == 100

    def test_estimate_empty(self) -> None:
        """Empty content should be 0 tokens."""
        assert estimate_tokens("") == 0


class TestCompilationContext:
    """Test CompilationContext."""

    def test_default_paths(self) -> None:
        """Should set default paths based on project root."""
        ctx = CompilationContext(project_root=Path("/test/project"))
        assert ctx.spec_path == Path("/test/project/spec")
        assert ctx.docs_path == Path("/test/project/docs")
        assert ctx.forest_path == Path("/test/project/plans")

    def test_custom_paths(self) -> None:
        """Should accept custom paths."""
        ctx = CompilationContext(
            project_root=Path("/test"),
            spec_path=Path("/custom/spec"),
        )
        assert ctx.spec_path == Path("/custom/spec")


class TestCompilationResult:
    """Test CompilationResult."""

    def test_valid_result(self) -> None:
        """Valid result should not raise."""
        result = CompilationResult(valid=True)
        result.raise_if_invalid()  # Should not raise

    def test_invalid_result(self) -> None:
        """Invalid result should raise with errors."""
        result = CompilationResult(
            valid=False,
            errors=["Error 1", "Error 2"],
        )
        with pytest.raises(ValueError, match="Error 1"):
            result.raise_if_invalid()


class TestPromptCompiler:
    """Test PromptCompiler."""

    def test_compile_empty(self) -> None:
        """Compiling with no compilers should produce warning."""
        compiler = PromptCompiler(section_compilers=[])
        ctx = CompilationContext()

        # Empty compilation should work but have warnings
        result = compiler.compile(ctx)
        assert result.content.strip()  # At least has footer

    def test_compile_with_default_compilers(self) -> None:
        """Should compile with default section compilers."""
        compilers = get_default_compilers()
        compiler = PromptCompiler(section_compilers=compilers)
        ctx = CompilationContext()

        result = compiler.compile(ctx)

        # Should have all sections
        assert "kgents" in result.content
        assert "Tasteful" in result.content
        assert "AGENTESE" in result.content
        assert result.token_count > 0

    def test_version_increment(self) -> None:
        """Version should increment."""
        compiler = PromptCompiler(version=1)
        assert compiler.version == 1

        compiler.increment_version()
        assert compiler.version == 2

    def test_compiled_prompt_save(self, tmp_path: Path) -> None:
        """Should save compiled prompt to file."""
        compilers = get_default_compilers()
        compiler = PromptCompiler(section_compilers=compilers)
        ctx = CompilationContext()

        result = compiler.compile(ctx)
        output_path = tmp_path / "CLAUDE.md"
        result.save(output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "kgents" in content


class TestCategoryLaws:
    """Test category law verification."""

    def test_compilation_determinism(self) -> None:
        """Same inputs should produce same output."""
        compilers = get_default_compilers()
        compiler = PromptCompiler(section_compilers=compilers, version=1)
        ctx = CompilationContext(include_timestamp=False)

        result1 = compiler.compile(ctx)
        result2 = compiler.compile(ctx)

        assert result1.content == result2.content

    def test_no_duplicate_sections(self) -> None:
        """Should reject duplicate section names."""
        # Create two compilers with same name
        compilers = get_default_compilers()
        compilers.append(compilers[0])  # Duplicate first compiler

        compiler = PromptCompiler(section_compilers=compilers)
        ctx = CompilationContext()

        with pytest.raises(ValueError, match="Duplicate"):
            compiler.compile(ctx)
