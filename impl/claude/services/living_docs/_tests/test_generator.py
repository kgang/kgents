"""
Tests for ReferenceGenerator Phase 3: Directory-based generation.

These tests verify the new directory output functionality:
- generate_to_directory() creates proper structure
- Category pages are generated correctly
- Index with navigation is created
- Overwrite behavior works as expected

Note: Tests that scan the entire codebase are marked @pytest.mark.slow.
Run fast tests only: pytest -m "not slow"
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ..generator import (
    CategoryConfig,
    GeneratedFile,
    GenerationManifest,
    ReferenceGenerator,
    generate_to_directory,
)
from ..types import DocNode, TeachingMoment, Tier


class TestGenerationManifest:
    """Tests for GenerationManifest dataclass."""

    def test_file_count_property(self) -> None:
        """file_count returns number of files."""
        manifest = GenerationManifest()
        assert manifest.file_count == 0

        manifest.files.append(
            GeneratedFile(
                path=Path("test.md"),
                title="Test",
                symbol_count=10,
                teaching_count=2,
                category="test",
            )
        )
        assert manifest.file_count == 1

    def test_to_dict_serialization(self) -> None:
        """to_dict produces valid serialization."""
        manifest = GenerationManifest(
            total_symbols=100,
            total_teaching=20,
        )
        manifest.files.append(
            GeneratedFile(
                path=Path("docs/test.md"),
                title="Test",
                symbol_count=50,
                teaching_count=10,
                category="test",
            )
        )

        result = manifest.to_dict()

        assert result["total_symbols"] == 100
        assert result["total_teaching"] == 20
        assert result["file_count"] == 1
        assert len(result["files"]) == 1
        assert result["files"][0]["title"] == "Test"
        assert "generated_at" in result


class TestCategoryNaming:
    """Tests for category name conversion."""

    def test_category_to_dirname(self) -> None:
        """Category names convert to directory names."""
        gen = ReferenceGenerator()

        assert gen._category_to_dirname("Crown Jewels") == "crown-jewels"
        assert gen._category_to_dirname("AGENTESE Protocol") == "agentese-protocol"
        assert gen._category_to_dirname("Categorical Foundation") == "categorical-foundation"

    def test_category_to_filename(self) -> None:
        """Category names convert to filenames."""
        gen = ReferenceGenerator()

        assert gen._category_to_filename("Crown Jewels") == "crown-jewels.md"
        assert gen._category_to_filename("AGENTESE Protocol") == "agentese-protocol.md"


@pytest.mark.slow
class TestDirectoryGeneration:
    """Tests for generate_to_directory functionality (scans entire codebase)."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path: Path) -> Path:
        """Provide a temporary output directory."""
        return tmp_path / "docs" / "reference"

    def test_creates_output_directory(self, temp_output_dir: Path) -> None:
        """Output directory is created if it doesn't exist."""
        gen = ReferenceGenerator(include_specs=False)

        manifest = gen.generate_to_directory(temp_output_dir)

        assert temp_output_dir.exists()
        assert manifest.file_count > 0

    def test_creates_index_file(self, temp_output_dir: Path) -> None:
        """index.md is created with navigation."""
        gen = ReferenceGenerator(include_specs=False)

        gen.generate_to_directory(temp_output_dir)

        index_path = temp_output_dir / "index.md"
        assert index_path.exists()

        content = index_path.read_text()
        assert "# kgents Reference Documentation" in content
        assert "## Summary" in content
        assert "## Navigation" in content
        assert "## Quick Links" in content

    def test_creates_category_subdirectories(self, temp_output_dir: Path) -> None:
        """Category subdirectories are created."""
        gen = ReferenceGenerator(include_specs=False)

        gen.generate_to_directory(temp_output_dir)

        # Check expected directories
        assert (temp_output_dir / "teaching").exists()
        # Crown jewels should exist if there are nodes
        # (depends on actual codebase content)

    def test_creates_gotchas_file(self, temp_output_dir: Path) -> None:
        """teaching/gotchas.md is created."""
        gen = ReferenceGenerator(include_specs=False)

        gen.generate_to_directory(temp_output_dir)

        gotchas_path = temp_output_dir / "teaching" / "gotchas.md"
        assert gotchas_path.exists()

        content = gotchas_path.read_text()
        assert "# Teaching Moments" in content

    def test_no_overwrite_by_default(self, temp_output_dir: Path) -> None:
        """
        Files are not overwritten by default.

        Teaching:
            gotcha: generate_to_directory() creates directories if they don't exist.
                    It will NOT overwrite existing files unless overwrite=True.
                    (Evidence: test_generator.py::test_no_overwrite_by_default)
        """
        gen = ReferenceGenerator(include_specs=False)

        # First generation
        gen.generate_to_directory(temp_output_dir)

        # Modify index
        index_path = temp_output_dir / "index.md"
        original_content = index_path.read_text()
        index_path.write_text("MODIFIED CONTENT")

        # Second generation without overwrite
        gen.generate_to_directory(temp_output_dir, overwrite=False)

        # Content should still be modified
        assert index_path.read_text() == "MODIFIED CONTENT"

    def test_overwrite_when_requested(self, temp_output_dir: Path) -> None:
        """Files are overwritten when overwrite=True."""
        gen = ReferenceGenerator(include_specs=False)

        # First generation
        gen.generate_to_directory(temp_output_dir)

        # Modify index
        index_path = temp_output_dir / "index.md"
        index_path.write_text("MODIFIED CONTENT")

        # Second generation with overwrite
        gen.generate_to_directory(temp_output_dir, overwrite=True)

        # Content should be regenerated
        content = index_path.read_text()
        assert content != "MODIFIED CONTENT"
        assert "# kgents Reference Documentation" in content

    def test_manifest_tracks_all_files(self, temp_output_dir: Path) -> None:
        """Manifest includes all generated files."""
        gen = ReferenceGenerator(include_specs=False)

        manifest = gen.generate_to_directory(temp_output_dir)

        # Should have at least index and gotchas
        assert manifest.file_count >= 2

        # Index should be first
        assert manifest.files[0].category == "index"

        # Should have teaching file
        teaching_files = [f for f in manifest.files if f.category == "teaching"]
        assert len(teaching_files) >= 1

    def test_manifest_totals_are_correct(self, temp_output_dir: Path) -> None:
        """Manifest totals match sum of file counts."""
        gen = ReferenceGenerator(include_specs=False)

        manifest = gen.generate_to_directory(temp_output_dir)

        # Total symbols should match sum (excluding index which has aggregate)
        non_index_files = [f for f in manifest.files if f.category != "index"]
        expected_symbols = sum(f.symbol_count for f in non_index_files)
        assert manifest.total_symbols == expected_symbols


class TestCategoryPageGeneration:
    """Tests for individual category page generation."""

    @pytest.fixture
    def sample_nodes(self) -> list[DocNode]:
        """Provide sample DocNodes for testing."""
        return [
            DocNode(
                symbol="TestClass",
                signature="class TestClass",
                summary="A test class for documentation.",
                examples=(">>> tc = TestClass()",),
                teaching=(
                    TeachingMoment(
                        insight="Always initialize before use.",
                        severity="warning",
                        evidence="test_class.py::test_init",
                    ),
                ),
                tier=Tier.RICH,
                module="services.test",
            ),
            DocNode(
                symbol="helper_function",
                signature="def helper_function(x: int) -> str",
                summary="A helper function.",
                tier=Tier.RICH,
                module="services.test",
            ),
        ]

    def test_category_page_includes_header(
        self, tmp_path: Path, sample_nodes: list[DocNode]
    ) -> None:
        """Category pages have proper header."""
        gen = ReferenceGenerator()
        category = CategoryConfig(
            name="Test Category",
            paths=[],
            description="Test description.",
        )

        gen._generate_category_page(
            category=category,
            nodes=sample_nodes,
            output_dir=tmp_path,
        )

        filepath = tmp_path / "test-category.md"
        content = filepath.read_text()

        assert "# Test Category" in content
        assert "Test description." in content

    def test_category_page_groups_by_module(
        self, tmp_path: Path, sample_nodes: list[DocNode]
    ) -> None:
        """Category pages group symbols by module."""
        gen = ReferenceGenerator()
        category = CategoryConfig(name="Test Category", paths=[])

        gen._generate_category_page(
            category=category,
            nodes=sample_nodes,
            output_dir=tmp_path,
        )

        filepath = tmp_path / "test-category.md"
        content = filepath.read_text()

        assert "## services.test" in content

    def test_category_page_returns_metadata(
        self, tmp_path: Path, sample_nodes: list[DocNode]
    ) -> None:
        """_generate_category_page returns GeneratedFile metadata."""
        gen = ReferenceGenerator()
        category = CategoryConfig(name="Test Category", paths=[])

        result = gen._generate_category_page(
            category=category,
            nodes=sample_nodes,
            output_dir=tmp_path,
        )

        assert result is not None
        assert result.title == "Test Category"
        assert result.symbol_count == 2
        assert result.teaching_count == 1  # One teaching moment in sample_nodes


@pytest.mark.slow
class TestConvenienceFunction:
    """Tests for the generate_to_directory convenience function (scans entire codebase)."""

    def test_convenience_function_works(self, tmp_path: Path) -> None:
        """generate_to_directory() convenience function works."""
        output_dir = tmp_path / "docs"

        manifest = generate_to_directory(output_dir, overwrite=True)

        assert manifest.file_count > 0
        assert (output_dir / "index.md").exists()
