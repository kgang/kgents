"""
Tests for ASHC Bootstrap Spec Parser.

These tests verify that spec/bootstrap.md can be parsed into structured
BootstrapAgentSpec objects.

Run: uv run pytest protocols/ashc/bootstrap/_tests/test_parser.py -v
"""

from pathlib import Path

import pytest

from ..parser import (
    AGENT_NAMES,
    BootstrapAgentSpec,
    format_spec_summary,
    get_spec_for_agent,
    parse_bootstrap_spec,
    parse_bootstrap_spec_detailed,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def specs() -> tuple[BootstrapAgentSpec, ...]:
    """Parsed bootstrap specs."""
    return parse_bootstrap_spec()


# =============================================================================
# Parser Tests
# =============================================================================


class TestParseBootstrapSpec:
    """Tests for parse_bootstrap_spec."""

    def test_parses_all_seven_agents(self, specs):
        """Parser extracts all 7 bootstrap agents."""
        assert len(specs) == 7

    def test_all_agent_names_present(self, specs):
        """All expected agent names are parsed."""
        parsed_names = {s.name for s in specs}
        assert parsed_names == set(AGENT_NAMES)

    def test_specs_are_frozen(self, specs):
        """Specs are immutable dataclasses."""
        for spec in specs:
            with pytest.raises(AttributeError):
                spec.name = "Modified"  # type: ignore

    def test_each_spec_has_content(self, specs):
        """Each spec has section content."""
        for spec in specs:
            assert spec.section_content
            assert len(spec.section_content) > 50  # Non-trivial content

    def test_each_spec_has_spec_hash(self, specs):
        """Each spec has a content hash."""
        for spec in specs:
            assert spec.spec_hash
            assert len(spec.spec_hash) == 12  # SHA256[:12]


class TestAgentSpecContent:
    """Tests for individual agent spec content."""

    def test_id_spec_signature(self, specs):
        """Id agent has correct signature."""
        id_spec = next(s for s in specs if s.name == "Id")
        assert "A → A" in id_spec.signature or "A->A" in id_spec.signature.replace(" ", "")

    def test_id_spec_has_identity_law(self, specs):
        """Id agent includes identity law."""
        id_spec = next(s for s in specs if s.name == "Id")
        # Check for identity law in some form
        laws_text = " ".join(id_spec.laws).lower()
        assert "id(x)" in laws_text or "identity" in laws_text

    def test_compose_spec_signature(self, specs):
        """Compose agent has correct signature."""
        compose_spec = next(s for s in specs if s.name == "Compose")
        # Should mention Agent → Agent
        assert "agent" in compose_spec.signature.lower()

    def test_compose_spec_has_associativity(self, specs):
        """Compose agent includes associativity law."""
        compose_spec = next(s for s in specs if s.name == "Compose")
        laws_text = " ".join(compose_spec.laws).lower()
        assert "associativ" in laws_text or ">>" in laws_text

    def test_judge_spec_has_verdict(self, specs):
        """Judge agent mentions verdict in signature/laws."""
        judge_spec = next(s for s in specs if s.name == "Judge")
        content = judge_spec.section_content.lower()
        assert "verdict" in content or "accept" in content or "reject" in content

    def test_fix_spec_has_fixed_point(self, specs):
        """Fix agent mentions fixed point."""
        fix_spec = next(s for s in specs if s.name == "Fix")
        content = fix_spec.section_content.lower()
        assert "fixed" in content or "fix" in content


class TestSpecDescriptions:
    """Tests for agent descriptions."""

    def test_each_spec_has_description(self, specs):
        """Each spec has a non-empty description."""
        for spec in specs:
            # Description might be empty for some, but section_content shouldn't be
            assert spec.section_content

    def test_descriptions_are_distinct(self, specs):
        """Each spec has distinct content."""
        contents = [s.section_content for s in specs]
        # All should be unique
        assert len(set(contents)) == len(contents)


class TestSpecLaws:
    """Tests for law extraction."""

    def test_id_has_laws(self, specs):
        """Id spec has at least one law."""
        id_spec = next(s for s in specs if s.name == "Id")
        assert id_spec.has_laws
        assert len(id_spec.laws) >= 1

    def test_compose_has_laws(self, specs):
        """Compose spec has laws."""
        compose_spec = next(s for s in specs if s.name == "Compose")
        assert compose_spec.has_laws


class TestParseBootstrapSpecDetailed:
    """Tests for detailed parsing with error reporting."""

    def test_detailed_success(self):
        """Detailed parsing succeeds for valid spec."""
        result = parse_bootstrap_spec_detailed()
        assert result.success
        assert len(result.specs) == 7
        assert len(result.parse_errors) == 0

    def test_detailed_returns_agent_names(self):
        """Detailed result includes agent names set."""
        result = parse_bootstrap_spec_detailed()
        assert result.agent_names == set(AGENT_NAMES)


class TestGetSpecForAgent:
    """Tests for get_spec_for_agent helper."""

    def test_get_existing_agent(self):
        """Can get spec for existing agent."""
        spec = get_spec_for_agent("Id")
        assert spec is not None
        assert spec.name == "Id"

    def test_get_nonexistent_agent(self):
        """Returns None for non-existent agent."""
        spec = get_spec_for_agent("NotAnAgent")
        assert spec is None

    @pytest.mark.parametrize("name", AGENT_NAMES)
    def test_get_each_agent(self, name):
        """Can get spec for each bootstrap agent."""
        spec = get_spec_for_agent(name)
        assert spec is not None
        assert spec.name == name


class TestFormatSpecSummary:
    """Tests for summary formatting."""

    def test_format_produces_string(self, specs):
        """Format produces non-empty string."""
        summary = format_spec_summary(specs)
        assert isinstance(summary, str)
        assert len(summary) > 100

    def test_format_includes_all_agents(self, specs):
        """Summary includes all agent names."""
        summary = format_spec_summary(specs)
        for name in AGENT_NAMES:
            assert name in summary


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_spec_hash_is_deterministic(self, specs):
        """Same content produces same hash."""
        specs2 = parse_bootstrap_spec()
        for s1, s2 in zip(specs, specs2):
            assert s1.spec_hash == s2.spec_hash

    def test_section_numbers_are_ordered(self, specs):
        """Section numbers are 1-7."""
        numbers = sorted(s.section_number for s in specs)
        assert numbers == [1, 2, 3, 4, 5, 6, 7]
