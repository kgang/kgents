"""
Tests for Wave 2: Dynamic Section Compilers.

Tests dynamic reading from source files and graceful fallback behavior.
"""

from pathlib import Path
from textwrap import dedent

import pytest
from protocols.prompt.compiler import CompilationContext
from protocols.prompt.sections.principles import PrinciplesSectionCompiler
from protocols.prompt.sections.skills import SkillsSectionCompiler
from protocols.prompt.sections.systems import SystemsSectionCompiler

from protocols.prompt.section_base import (
    extract_markdown_section,
    extract_principle_summary,
    extract_skills_from_directory,
    glob_source_paths,
    read_file_safe,
)


class TestReadFileSafe:
    """Test read_file_safe utility."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
        """Should read existing file content."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content\n\nHello world")

        content = read_file_safe(test_file)
        assert content is not None
        assert "Test Content" in content
        assert "Hello world" in content

    def test_read_missing_file(self, tmp_path: Path) -> None:
        """Should return None for missing file."""
        missing = tmp_path / "nonexistent.md"
        content = read_file_safe(missing)
        assert content is None

    def test_read_with_encoding(self, tmp_path: Path) -> None:
        """Should handle UTF-8 content."""
        test_file = tmp_path / "unicode.md"
        test_file.write_text("# Test with émojis 🎉", encoding="utf-8")

        content = read_file_safe(test_file)
        assert content is not None
        assert "émojis" in content
        assert "🎉" in content


class TestExtractMarkdownSection:
    """Test markdown section extraction."""

    def test_extract_section(self) -> None:
        """Should extract content under heading."""
        content = dedent("""
            # Title

            ## Section One

            Content for section one.

            ## Section Two

            Content for section two.
        """).strip()

        result = extract_markdown_section(content, "Section One")
        assert result is not None
        assert "Content for section one" in result
        assert "Content for section two" not in result

    def test_extract_section_with_number(self) -> None:
        """Should extract section with numbered heading."""
        content = dedent("""
            ## 1. First Section

            First content.

            ## 2. Second Section

            Second content.
        """).strip()

        result = extract_markdown_section(content, "First Section")
        assert result is not None
        assert "First content" in result

    def test_extract_missing_section(self) -> None:
        """Should return None for missing section."""
        content = "## Existing\n\nContent"
        result = extract_markdown_section(content, "Nonexistent")
        assert result is None

    def test_extract_section_case_insensitive(self) -> None:
        """Should be case-insensitive."""
        content = "## TASTEFUL\n\n> Quality over quantity"
        result = extract_markdown_section(content, "tasteful")
        assert result is not None


class TestExtractPrincipleSummary:
    """Test principle summary extraction."""

    def test_extract_principles(self) -> None:
        """Should extract 7 principles with taglines."""
        content = dedent("""
            # Design Principles

            ## 1. Tasteful

            > Each agent serves a clear, justified purpose.

            More content here.

            ## 2. Curated

            > Intentional selection over exhaustive cataloging.

            ## 3. Ethical

            > Agents augment human capability, never replace judgment.

            ## 4. Joy-Inducing

            > Delight in interaction; personality matters.

            ## 5. Composable

            > Agents are morphisms in a category; composition is primary.

            ## 6. Heterarchical

            > Agents exist in flux, not fixed hierarchy.

            ## 7. Generative

            > Spec is compression; design should generate implementation.
        """).strip()

        result = extract_principle_summary(content)
        assert result is not None
        assert "Tasteful" in result
        assert "Curated" in result
        assert "Ethical" in result
        assert "Joy-Inducing" in result
        assert "Composable" in result
        assert "Heterarchical" in result
        assert "Generative" in result
        assert "Each agent serves a clear, justified purpose" in result

    def test_extract_principles_incomplete(self) -> None:
        """Should return None if fewer than 7 principles."""
        content = dedent("""
            ## 1. Tasteful

            > Quality

            ## 2. Curated

            > Selection
        """).strip()

        result = extract_principle_summary(content)
        assert result is None


class TestExtractSkillsFromDirectory:
    """Test skills directory extraction."""

    def test_extract_skills(self, tmp_path: Path) -> None:
        """Should extract skills from directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create test skill files
        (skills_dir / "test-skill.md").write_text(
            "---\npath: test\n---\n\n# Skill: Test Skill\n\nContent"
        )
        (skills_dir / "another-skill.md").write_text("# Another Skill\n\nMore content")

        skills = extract_skills_from_directory(tmp_path)
        assert len(skills) == 2

        names = [s[0] for s in skills]
        assert "Test Skill" in names
        assert "Another Skill" in names

    def test_extract_skills_empty_dir(self, tmp_path: Path) -> None:
        """Should return empty list for empty directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skills = extract_skills_from_directory(tmp_path)
        assert skills == []

    def test_extract_skills_missing_dir(self, tmp_path: Path) -> None:
        """Should return empty list for missing directory."""
        skills = extract_skills_from_directory(tmp_path)
        assert skills == []

    def test_extract_skills_skips_readme(self, tmp_path: Path) -> None:
        """Should skip README.md files."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        (skills_dir / "README.md").write_text("# Skills README")
        (skills_dir / "real-skill.md").write_text("# Real Skill")

        skills = extract_skills_from_directory(tmp_path)
        assert len(skills) == 1
        assert skills[0][0] == "Real Skill"


class TestGlobSourcePaths:
    """Test source path globbing."""

    def test_glob_existing_files(self, tmp_path: Path) -> None:
        """Should return sorted tuple of matching paths."""
        (tmp_path / "b.md").write_text("B")
        (tmp_path / "a.md").write_text("A")
        (tmp_path / "c.txt").write_text("C")

        result = glob_source_paths(tmp_path, "*.md")
        assert len(result) == 2
        assert result[0].name == "a.md"  # Sorted
        assert result[1].name == "b.md"

    def test_glob_missing_directory(self, tmp_path: Path) -> None:
        """Should return empty tuple for missing directory."""
        result = glob_source_paths(tmp_path / "nonexistent", "*.md")
        assert result == ()

    def test_glob_is_deterministic(self, tmp_path: Path) -> None:
        """Glob should return same order on repeated calls."""
        for i in range(5):
            (tmp_path / f"file{i}.md").write_text(f"{i}")

        result1 = glob_source_paths(tmp_path, "*.md")
        result2 = glob_source_paths(tmp_path, "*.md")
        assert result1 == result2


class TestPrinciplesSectionCompilerDynamic:
    """Test PrinciplesSectionCompiler with dynamic reading."""

    def test_compile_from_source(self, tmp_path: Path) -> None:
        """Should compile from actual source file."""
        spec_path = tmp_path / "spec"
        spec_path.mkdir()

        # Create principles.md with valid content
        principles_content = dedent("""
            # Design Principles

            ## 1. Tasteful

            > Each agent serves a clear, justified purpose.

            ## 2. Curated

            > Intentional selection over exhaustive cataloging.

            ## 3. Ethical

            > Agents augment human capability, never replace judgment.

            ## 4. Joy-Inducing

            > Delight in interaction; personality matters.

            ## 5. Composable

            > Agents are morphisms in a category; composition is primary.

            ## 6. Heterarchical

            > Agents exist in flux, not fixed hierarchy.

            ## 7. Generative

            > Spec is compression; design should generate implementation.
        """).strip()
        (spec_path / "principles.md").write_text(principles_content)

        ctx = CompilationContext(
            project_root=tmp_path,
            spec_path=spec_path,
        )
        compiler = PrinciplesSectionCompiler()
        section = compiler.compile(ctx)

        # Should use dynamic content
        assert "Each agent serves a clear, justified purpose" in section.content
        assert section.source_paths == (spec_path / "principles.md",)

    def test_compile_fallback_on_missing(self, tmp_path: Path) -> None:
        """Should fall back to hardcoded when file missing."""
        ctx = CompilationContext(
            project_root=tmp_path,
            spec_path=tmp_path / "nonexistent",
        )
        compiler = PrinciplesSectionCompiler()
        section = compiler.compile(ctx)

        # Should use fallback
        assert "Tasteful" in section.content
        assert section.source_paths == ()  # No source paths for fallback

    def test_compile_fallback_on_invalid_content(self, tmp_path: Path) -> None:
        """Should fall back when content can't be parsed."""
        spec_path = tmp_path / "spec"
        spec_path.mkdir()
        (spec_path / "principles.md").write_text("# Empty principles file")

        ctx = CompilationContext(
            project_root=tmp_path,
            spec_path=spec_path,
        )
        compiler = PrinciplesSectionCompiler()
        section = compiler.compile(ctx)

        # Should use fallback (only 7 principles can be parsed)
        assert "Tasteful" in section.content
        assert section.source_paths == ()


class TestSystemsSectionCompilerDynamic:
    """Test SystemsSectionCompiler with dynamic reading."""

    def test_compile_from_source(self, tmp_path: Path) -> None:
        """Should compile from actual source file."""
        docs_path = tmp_path / "docs"
        docs_path.mkdir()

        systems_content = dedent("""
            # Systems Reference

            ## Categorical Foundation

            | Component | Location | Purpose |
            |-----------|----------|---------|
            | **PolyAgent** | `agents/poly/` | State machines |
            | **Operad** | `agents/operad/` | Composition |

            ## Streaming

            | Component | Purpose |
            |-----------|---------|
            | **FluxAgent** | Stream processing |
        """).strip()
        (docs_path / "systems-reference.md").write_text(systems_content)

        ctx = CompilationContext(
            project_root=tmp_path,
            docs_path=docs_path,
        )
        compiler = SystemsSectionCompiler()
        section = compiler.compile(ctx)

        assert "Built Infrastructure" in section.content
        assert section.source_paths == (docs_path / "systems-reference.md",)

    def test_compile_fallback_on_missing(self, tmp_path: Path) -> None:
        """Should fall back when file missing."""
        ctx = CompilationContext(
            project_root=tmp_path,
            docs_path=tmp_path / "nonexistent",
        )
        compiler = SystemsSectionCompiler()
        section = compiler.compile(ctx)

        assert "Built Infrastructure" in section.content
        assert "PolyAgent" in section.content
        assert section.source_paths == ()


class TestSkillsSectionCompilerDynamic:
    """Test SkillsSectionCompiler with dynamic reading."""

    def test_compile_from_source(self, tmp_path: Path) -> None:
        """Should compile from actual skill files."""
        docs_path = tmp_path / "docs"
        skills_path = docs_path / "skills"
        skills_path.mkdir(parents=True)

        (skills_path / "test-skill.md").write_text("# Skill: Test Skill\n\nContent")
        (skills_path / "another-skill.md").write_text("# Another Skill\n\nContent")

        ctx = CompilationContext(
            project_root=tmp_path,
            docs_path=docs_path,
        )
        compiler = SkillsSectionCompiler()
        section = compiler.compile(ctx)

        assert "Skills Directory" in section.content
        assert "2 documented patterns" in section.content  # Dynamic count
        assert len(section.source_paths) == 2

    def test_compile_fallback_on_missing(self, tmp_path: Path) -> None:
        """Should fall back when directory missing."""
        ctx = CompilationContext(
            project_root=tmp_path,
            docs_path=tmp_path / "nonexistent",
        )
        compiler = SkillsSectionCompiler()
        section = compiler.compile(ctx)

        assert "Skills Directory" in section.content
        assert section.source_paths == ()

    def test_source_paths_are_sorted(self, tmp_path: Path) -> None:
        """Source paths should be in deterministic order."""
        docs_path = tmp_path / "docs"
        skills_path = docs_path / "skills"
        skills_path.mkdir(parents=True)

        # Create files in non-alphabetical order
        (skills_path / "z-skill.md").write_text("# Z Skill")
        (skills_path / "a-skill.md").write_text("# A Skill")
        (skills_path / "m-skill.md").write_text("# M Skill")

        ctx = CompilationContext(project_root=tmp_path, docs_path=docs_path)
        compiler = SkillsSectionCompiler()
        section = compiler.compile(ctx)

        # Verify sorted order
        names = [p.name for p in section.source_paths]
        assert names == sorted(names)


class TestDynamicCompilationIntegration:
    """Integration tests for dynamic compilation."""

    def test_source_change_propagates(self, tmp_path: Path) -> None:
        """Changes to source files should propagate to compiled output."""
        spec_path = tmp_path / "spec"
        spec_path.mkdir()

        # Initial content
        initial_content = dedent("""
            # Design Principles

            ## 1. Tasteful

            > Initial tagline for tasteful.

            ## 2. Curated

            > Second principle.

            ## 3. Ethical

            > Third principle.

            ## 4. Joy-Inducing

            > Fourth principle.

            ## 5. Composable

            > Fifth principle.

            ## 6. Heterarchical

            > Sixth principle.

            ## 7. Generative

            > Seventh principle.
        """).strip()
        (spec_path / "principles.md").write_text(initial_content)

        ctx = CompilationContext(project_root=tmp_path, spec_path=spec_path)
        compiler = PrinciplesSectionCompiler()

        # First compilation
        section1 = compiler.compile(ctx)
        assert "Initial tagline for tasteful" in section1.content

        # Update source file
        updated_content = initial_content.replace(
            "Initial tagline for tasteful", "Updated tagline for tasteful"
        )
        (spec_path / "principles.md").write_text(updated_content)

        # Second compilation should reflect change
        section2 = compiler.compile(ctx)
        assert "Updated tagline for tasteful" in section2.content
        assert "Initial tagline for tasteful" not in section2.content

    def test_compilation_determinism_with_dynamic(self, tmp_path: Path) -> None:
        """Dynamic compilation should still be deterministic."""
        docs_path = tmp_path / "docs"
        skills_path = docs_path / "skills"
        skills_path.mkdir(parents=True)

        for i in range(5):
            (skills_path / f"skill-{i}.md").write_text(f"# Skill {i}")

        ctx = CompilationContext(project_root=tmp_path, docs_path=docs_path)
        compiler = SkillsSectionCompiler()

        section1 = compiler.compile(ctx)
        section2 = compiler.compile(ctx)

        assert section1.content == section2.content
        assert section1.source_paths == section2.source_paths
