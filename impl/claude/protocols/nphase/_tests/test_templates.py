"""
Tests for N-Phase Templates.
"""

import pytest
from protocols.nphase.templates import (
    PHASE_FAMILIES,
    PHASE_TEMPLATES,
    PhaseTemplate,
    get_compressed_template,
    get_template,
)


class TestPhaseTemplates:
    """Tests for phase template constants."""

    def test_all_11_phases_present(self) -> None:
        """All 11 phases have templates."""
        expected = [
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "REFLECT",
        ]
        for phase in expected:
            assert phase in PHASE_TEMPLATES

    def test_each_template_has_required_fields(self) -> None:
        """Each template has all required fields."""
        for name, tmpl in PHASE_TEMPLATES.items():
            assert isinstance(tmpl, PhaseTemplate)
            assert tmpl.name == name
            assert tmpl.mission
            assert tmpl.actions
            assert tmpl.exit_criteria
            assert tmpl.continuation
            assert tmpl.minimum_artifact

    def test_continuations_are_valid(self) -> None:
        """Each template's continuation points to valid next phase or COMPLETE."""
        valid_targets = set(PHASE_TEMPLATES.keys()) | {"COMPLETE"}
        for tmpl in PHASE_TEMPLATES.values():
            assert tmpl.continuation in valid_targets


class TestGetTemplate:
    """Tests for get_template function."""

    def test_get_valid_phase(self) -> None:
        """get_template returns template for valid phase."""
        tmpl = get_template("PLAN")
        assert tmpl.name == "PLAN"
        assert "scope" in tmpl.mission.lower()

    def test_get_invalid_phase_raises(self) -> None:
        """get_template raises for invalid phase."""
        with pytest.raises(ValueError, match="Unknown phase"):
            get_template("INVALID")


class TestPhaseFamilies:
    """Tests for 3-phase compression."""

    def test_families_cover_all_phases(self) -> None:
        """All 11 phases are covered by the 3 families."""
        all_phases = set()
        for phases in PHASE_FAMILIES.values():
            all_phases.update(phases)
        assert all_phases == set(PHASE_TEMPLATES.keys())

    def test_get_compressed_template_understand(self) -> None:
        """UNDERSTAND family combines PLAN, RESEARCH, DEVELOP, STRATEGIZE, CROSS-SYNERGIZE."""
        tmpl = get_compressed_template("UNDERSTAND")
        assert tmpl.name == "UNDERSTAND"
        assert tmpl.continuation == "ACT"
        # Should include content from all five phases
        assert "PLAN" in tmpl.actions
        assert "RESEARCH" in tmpl.actions
        assert "DEVELOP" in tmpl.actions
        assert "STRATEGIZE" in tmpl.actions
        assert "CROSS-SYNERGIZE" in tmpl.actions

    def test_get_compressed_template_sense_alias(self) -> None:
        """SENSE alias resolves to UNDERSTAND."""
        tmpl = get_compressed_template("SENSE")
        assert tmpl.name == "UNDERSTAND"  # Resolved to canonical name
        assert tmpl.continuation == "ACT"

    def test_get_compressed_template_act(self) -> None:
        """ACT family combines middle phases."""
        tmpl = get_compressed_template("ACT")
        assert tmpl.name == "ACT"
        assert tmpl.continuation == "REFLECT"

    def test_get_compressed_template_reflect(self) -> None:
        """REFLECT family combines final phases."""
        tmpl = get_compressed_template("REFLECT")
        assert tmpl.name == "REFLECT"
        assert tmpl.continuation == "COMPLETE"

    def test_get_compressed_invalid_raises(self) -> None:
        """get_compressed_template raises for invalid family."""
        with pytest.raises(ValueError, match="Unknown family"):
            get_compressed_template("INVALID")
