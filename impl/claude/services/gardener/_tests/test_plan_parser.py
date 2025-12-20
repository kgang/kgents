"""
Tests for plan_parser.py - Phase 5 Batteries Included.

Tests:
1. parse_progress_string() - Progress value parsing
2. parse_forest_table() - _forest.md table extraction
3. parse_plan_progress() - Individual plan file parsing
4. infer_crown_jewel() - Crown Jewel mapping
5. infer_agentese_path() - AGENTESE path inference
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pytest

from services.gardener.plan_parser import (
    infer_agentese_path,
    infer_crown_jewel,
    parse_forest_table,
    parse_plan_progress,
    parse_progress_string,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Tests for parse_progress_string()
# =============================================================================


class TestParseProgressString:
    """Test progress string parsing."""

    def test_percentage(self):
        """Parse percentage strings."""
        assert parse_progress_string("88%") == 0.88
        assert parse_progress_string("100%") == 1.0
        assert parse_progress_string("0%") == 0.0
        assert parse_progress_string("50%") == 0.5

    def test_decimal(self):
        """Parse decimal strings."""
        assert parse_progress_string("0.88") == 0.88
        assert parse_progress_string("1.0") == 1.0
        assert parse_progress_string("0") == 0.0

    def test_integer_as_percentage(self):
        """Parse integer as percentage when > 1."""
        assert parse_progress_string("88") == 0.88
        assert parse_progress_string("100") == 1.0

    def test_em_dash(self):
        """Em-dash means no progress."""
        assert parse_progress_string("—") == 0.0
        assert parse_progress_string("-") == 0.0

    def test_empty(self):
        """Empty string means no progress."""
        assert parse_progress_string("") == 0.0
        assert parse_progress_string("  ") == 0.0

    def test_invalid(self):
        """Invalid strings default to 0."""
        assert parse_progress_string("foo") == 0.0
        assert parse_progress_string("abc%") == 0.0


# =============================================================================
# Tests for parse_forest_table()
# =============================================================================


class TestParseForestTable:
    """Test _forest.md table parsing."""

    def test_basic_table(self, tmp_path: Path):
        """Parse a basic forest table."""
        forest_content = """# Forest Health

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| plans/foo | 88% | active | Some notes |
| plans/bar | 0% | planning | Other notes |
| **plans/baz** | 100% | **complete** | Done |
"""
        forest_file = tmp_path / "_forest.md"
        forest_file.write_text(forest_content)

        result = parse_forest_table(forest_file)

        assert "foo" in result
        assert result["foo"].progress == 0.88
        assert result["foo"].status == "active"

        assert "bar" in result
        assert result["bar"].progress == 0.0
        assert result["bar"].status == "planning"

        assert "baz" in result
        assert result["baz"].progress == 1.0
        assert result["baz"].status == "complete"

    def test_core_apps_plans(self, tmp_path: Path):
        """Parse plans with core-apps/ prefix."""
        forest_content = """| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| plans/core-apps/atelier-experience | 75% | active | Notes |
"""
        forest_file = tmp_path / "_forest.md"
        forest_file.write_text(forest_content)

        result = parse_forest_table(forest_file)

        assert "atelier-experience" in result
        assert result["atelier-experience"].progress == 0.75

    def test_em_dash_progress(self, tmp_path: Path):
        """Handle em-dash progress values."""
        forest_content = """| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| plans/unknown | — | active | No progress |
"""
        forest_file = tmp_path / "_forest.md"
        forest_file.write_text(forest_content)

        result = parse_forest_table(forest_file)

        assert "unknown" in result
        assert result["unknown"].progress == 0.0

    def test_nonexistent_file(self, tmp_path: Path):
        """Return empty dict for missing file."""
        forest_file = tmp_path / "nonexistent.md"
        result = parse_forest_table(forest_file)
        assert result == {}

    def test_skips_header_row(self, tmp_path: Path):
        """Skip the header row."""
        forest_content = """| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| plans/foo | 50% | active | Notes |
"""
        forest_file = tmp_path / "_forest.md"
        forest_file.write_text(forest_content)

        result = parse_forest_table(forest_file)

        # Should not contain "plan" from header
        assert "plan" not in result
        assert "Plan" not in result
        assert "foo" in result


# =============================================================================
# Tests for parse_plan_progress()
# =============================================================================


class TestParsePlanProgress:
    """Test individual plan file parsing."""

    @pytest.mark.asyncio
    async def test_yaml_frontmatter_progress(self, tmp_path: Path):
        """Parse progress from YAML frontmatter."""
        plan_content = """---
progress: 0.75
status: active
---

# My Plan

Some content.
"""
        plan_file = tmp_path / "my-plan.md"
        plan_file.write_text(plan_content)

        result = await parse_plan_progress(plan_file)

        assert result.name == "my-plan"
        assert result.progress == 0.75
        assert result.status == "active"

    @pytest.mark.asyncio
    async def test_status_line_with_percentage(self, tmp_path: Path):
        """Parse progress from Status line."""
        plan_content = """# My Plan

**Status**: 50% complete

Some content.
"""
        plan_file = tmp_path / "my-plan.md"
        plan_file.write_text(plan_content)

        result = await parse_plan_progress(plan_file)

        assert result.progress == 0.50

    @pytest.mark.asyncio
    async def test_status_executing(self, tmp_path: Path):
        """Parse executing status."""
        plan_content = """# My Plan

**Status**: EXECUTING (Phase 0.5)

Some content.
"""
        plan_file = tmp_path / "my-plan.md"
        plan_file.write_text(plan_content)

        result = await parse_plan_progress(plan_file)

        assert result.status == "executing"

    @pytest.mark.asyncio
    async def test_momentum_as_fallback(self, tmp_path: Path):
        """Use momentum as fallback progress indicator."""
        plan_content = """---
momentum: 0.85
---

# My Plan
"""
        plan_file = tmp_path / "my-plan.md"
        plan_file.write_text(plan_content)

        result = await parse_plan_progress(plan_file)

        assert result.progress == 0.85

    @pytest.mark.asyncio
    async def test_nonexistent_file(self, tmp_path: Path):
        """Handle missing file gracefully."""
        plan_file = tmp_path / "nonexistent.md"

        result = await parse_plan_progress(plan_file)

        assert result.name == "nonexistent"
        assert result.progress == 0.0
        assert result.status == "unknown"

    @pytest.mark.asyncio
    async def test_no_progress_defaults(self, tmp_path: Path):
        """Default to 0 progress when not specified."""
        plan_content = """# My Plan

Just a simple plan with no progress markers.
"""
        plan_file = tmp_path / "simple.md"
        plan_file.write_text(plan_content)

        result = await parse_plan_progress(plan_file)

        assert result.progress == 0.0
        assert result.status == "active"


# =============================================================================
# Tests for infer_crown_jewel()
# =============================================================================


class TestInferCrownJewel:
    """Test Crown Jewel inference from plan names."""

    def test_direct_match(self):
        """Direct plan name to jewel mapping."""
        assert infer_crown_jewel("holographic-brain") == "holographic-brain"
        assert infer_crown_jewel("the-gardener") == "gardener"
        assert infer_crown_jewel("coalition-forge") == "coalition-forge"
        assert infer_crown_jewel("kgentsd-crown-jewel") == "kgentsd"

    def test_partial_match(self):
        """Partial match for related plans."""
        assert infer_crown_jewel("town-visualizer-renaissance") == "punchdrunk-park"
        assert infer_crown_jewel("town-rebuild") == "punchdrunk-park"

    def test_no_match(self):
        """Unknown plans return None."""
        assert infer_crown_jewel("random-plan") is None
        assert infer_crown_jewel("something-else") is None


# =============================================================================
# Tests for infer_agentese_path()
# =============================================================================


class TestInferAgentesePath:
    """Test AGENTESE path inference from plan file location."""

    def test_core_apps_atelier(self, tmp_path: Path):
        """Core apps atelier -> world.atelier."""
        plan_file = tmp_path / "core-apps" / "atelier-experience.md"
        assert infer_agentese_path(plan_file) == "world.atelier"

    def test_core_apps_coalition(self, tmp_path: Path):
        """Core apps coalition -> world.forge."""
        plan_file = tmp_path / "core-apps" / "coalition-forge.md"
        assert infer_agentese_path(plan_file) == "world.forge"

    def test_kgentsd(self, tmp_path: Path):
        """kgentsd plans -> self.witness."""
        plan_file = tmp_path / "kgentsd-crown-jewel.md"
        assert infer_agentese_path(plan_file) == "self.witness"

    def test_brain(self, tmp_path: Path):
        """Brain plans -> self.memory."""
        plan_file = tmp_path / "holographic-brain.md"
        assert infer_agentese_path(plan_file) == "self.memory"

    def test_gardener(self, tmp_path: Path):
        """Gardener plans -> concept.gardener."""
        plan_file = tmp_path / "the-gardener.md"
        assert infer_agentese_path(plan_file) == "concept.gardener"

    def test_generic(self, tmp_path: Path):
        """Generic plans -> concept.plan.*."""
        plan_file = tmp_path / "random-thing.md"
        assert infer_agentese_path(plan_file) == "concept.plan.random_thing"


# =============================================================================
# Integration Test
# =============================================================================


class TestForestIntegration:
    """Integration test with realistic forest structure."""

    @pytest.mark.asyncio
    async def test_full_parsing_flow(self, tmp_path: Path):
        """Full parsing of a realistic plans/ directory."""
        # Create plans directory
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()

        # Create _forest.md
        forest_content = """# Forest Health

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| plans/brain-upgrade | 100% | complete | Done |
| plans/garden-phase2 | 50% | active | In progress |
"""
        (plans_dir / "_forest.md").write_text(forest_content)

        # Create individual plan files
        (plans_dir / "brain-upgrade.md").write_text("""# Brain Upgrade
**Status**: COMPLETE
Some notes.
""")
        (plans_dir / "garden-phase2.md").write_text("""# Garden Phase 2
**Status**: ACTIVE
In progress.
""")
        (plans_dir / "untracked-plan.md").write_text("""---
progress: 0.25
---
# Untracked Plan
Not in forest table.
""")

        # Parse forest table
        forest_progress = parse_forest_table(plans_dir / "_forest.md")

        assert "brain-upgrade" in forest_progress
        assert forest_progress["brain-upgrade"].progress == 1.0

        assert "garden-phase2" in forest_progress
        assert forest_progress["garden-phase2"].progress == 0.5

        # Parse individual file not in table
        untracked = await parse_plan_progress(plans_dir / "untracked-plan.md")
        assert untracked.progress == 0.25
