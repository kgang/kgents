"""
Frontend Contract Tests: Validate backend JSON matches TypeScript types.

This module ensures the Python `_to_json()` output matches the frontend
TypeScript types defined in `web/src/reactive/types.ts`.

WHY THIS EXISTS:
----------------
Bug discovered 2024-12: ColonyDashboard._to_json() was sending `id` instead
of `citizen_id` and missing `eigenvectors` field entirely. The frontend
CitizenPanel.tsx tried to access `citizen.eigenvectors.warmth`, causing
a TypeError that crashed React's entire render tree -> blank screen.

These contract tests prevent such mismatches by validating that backend
JSON output contains all fields expected by the frontend TypeScript types.

MAINTENANCE:
------------
When updating web/src/reactive/types.ts:
1. Update the corresponding schema in FRONTEND_SCHEMAS below
2. Run: uv run pytest protocols/api/_tests/test_frontend_contracts.py -v

See: web/src/reactive/types.ts for the authoritative TypeScript definitions.
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

# =============================================================================
# Frontend Schema Definitions
# Mirror of web/src/reactive/types.ts
# =============================================================================


# Type validators
def is_string(v: Any) -> bool:
    return isinstance(v, str)


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float))


def is_list(v: Any) -> bool:
    return isinstance(v, list)


def is_list_of_numbers(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, (int, float)) for x in v)


def is_optional_string(v: Any) -> bool:
    return v is None or isinstance(v, str)


def is_citizen_phase(v: Any) -> bool:
    return v in ("IDLE", "SOCIALIZING", "WORKING", "REFLECTING", "RESTING")


def is_nphase(v: Any) -> bool:
    # UNDERSTAND is primary name, SENSE is backwards-compat alias
    return v in ("UNDERSTAND", "SENSE", "ACT", "REFLECT")


def is_town_phase(v: Any) -> bool:
    return v in ("MORNING", "AFTERNOON", "EVENING", "NIGHT")


# Schema definitions: field_name -> validator function
# These mirror the TypeScript interfaces in web/src/reactive/types.ts

CITIZEN_EIGENVECTORS_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "warmth": is_number,
    "curiosity": is_number,
    "trust": is_number,
}

CITIZEN_CARD_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "type": lambda v: v == "citizen_card",
    "citizen_id": is_string,  # NOT "id" - this was the bug!
    "name": is_string,
    "archetype": is_string,
    "phase": is_citizen_phase,
    "nphase": is_nphase,
    "activity": is_list_of_numbers,
    "capability": is_number,
    "entropy": is_number,
    "region": is_string,
    "mood": is_string,
    "eigenvectors": lambda v: isinstance(v, dict),  # Validated separately
}

COLONY_METRICS_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "total_events": is_number,
    "total_tokens": is_number,
    "entropy_budget": is_number,
}

COLONY_DASHBOARD_SCHEMA: dict[str, Callable[[Any], bool]] = {
    "type": lambda v: v == "colony_dashboard",
    "colony_id": is_string,
    "phase": is_town_phase,
    "day": is_number,
    "metrics": lambda v: isinstance(v, dict),  # Validated separately
    "citizens": is_list,  # Each item validated separately
    "grid_cols": is_number,
    "selected_citizen_id": is_optional_string,
}


def validate_schema(
    data: dict[str, Any],
    schema: dict[str, Callable[[Any], bool]],
    path: str = "",
) -> list[str]:
    """
    Validate data against schema, returning list of errors.

    Args:
        data: The JSON data to validate
        schema: Dict of field_name -> validator function
        path: Current path for error messages

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check for missing required fields
    for field, validator in schema.items():
        full_path = f"{path}.{field}" if path else field

        if field not in data:
            errors.append(f"Missing required field: {full_path}")
            continue

        value = data[field]
        if not validator(value):
            errors.append(
                f"Invalid value for {full_path}: got {type(value).__name__} = {value!r}"
            )

    return errors


# =============================================================================
# Contract Tests
# =============================================================================


class TestCitizenCardContract:
    """Verify CitizenWidget._to_json() matches CitizenCardJSON TypeScript type."""

    @pytest.fixture
    def citizen_widget(self) -> Any:
        """Create a CitizenWidget with realistic data."""
        from agents.i.reactive.primitives.citizen_card import (
            CitizenState,
            CitizenWidget,
        )
        from agents.town.polynomial import CitizenPhase
        from protocols.nphase.operad import NPhase

        state = CitizenState(
            citizen_id="test-citizen-123",
            name="Alice",
            archetype="builder",
            phase=CitizenPhase.WORKING,
            nphase=NPhase.ACT,
            activity=(0.5, 0.7, 0.3, 0.8),
            capability=0.85,
            entropy=0.15,
            region="plaza",
            mood="focused",
            warmth=0.6,
            curiosity=0.8,
            trust=0.7,
        )
        return CitizenWidget(state)

    def test_citizen_card_has_required_fields(self, citizen_widget: Any) -> None:
        """Verify all CitizenCardJSON required fields are present."""
        from agents.i.reactive.widget import RenderTarget

        json_output = citizen_widget.project(RenderTarget.JSON)

        errors = validate_schema(json_output, CITIZEN_CARD_SCHEMA)
        assert not errors, "Schema validation failed:\n" + "\n".join(errors)

    def test_citizen_card_eigenvectors_structure(self, citizen_widget: Any) -> None:
        """Verify eigenvectors field matches CitizenEigenvectors TypeScript type."""
        from agents.i.reactive.widget import RenderTarget

        json_output = citizen_widget.project(RenderTarget.JSON)

        assert "eigenvectors" in json_output, "Missing eigenvectors field"
        eigenvectors = json_output["eigenvectors"]

        errors = validate_schema(
            eigenvectors, CITIZEN_EIGENVECTORS_SCHEMA, "eigenvectors"
        )
        assert not errors, "Eigenvectors schema validation failed:\n" + "\n".join(
            errors
        )

    def test_citizen_card_uses_citizen_id_not_id(self, citizen_widget: Any) -> None:
        """
        CRITICAL: Verify field is 'citizen_id' not 'id'.

        This was the exact bug that caused blank screens when clicking agents.
        The backend was sending 'id' but frontend expected 'citizen_id'.
        """
        from agents.i.reactive.widget import RenderTarget

        json_output = citizen_widget.project(RenderTarget.JSON)

        assert "citizen_id" in json_output, "Must use 'citizen_id' not 'id'"
        assert "id" not in json_output, "Must NOT have 'id' field (use 'citizen_id')"

    def test_citizen_card_eigenvectors_has_all_fields(
        self, citizen_widget: Any
    ) -> None:
        """
        CRITICAL: Verify eigenvectors has warmth, curiosity, trust.

        Missing eigenvectors caused: citizen.eigenvectors.warmth -> TypeError
        """
        from agents.i.reactive.widget import RenderTarget

        json_output = citizen_widget.project(RenderTarget.JSON)
        eigenvectors = json_output.get("eigenvectors", {})

        required = ["warmth", "curiosity", "trust"]
        for field in required:
            assert field in eigenvectors, f"Missing eigenvectors.{field}"
            assert isinstance(eigenvectors[field], (int, float)), (
                f"eigenvectors.{field} must be a number"
            )


class TestColonyDashboardContract:
    """Verify ColonyDashboard._to_json() matches ColonyDashboardJSON TypeScript type."""

    @pytest.fixture
    def colony_dashboard(self) -> Any:
        """Create a ColonyDashboard with multiple citizens."""
        from agents.i.reactive.colony_dashboard import (
            ColonyDashboard,
            ColonyState,
            TownPhase,
        )
        from agents.i.reactive.primitives.citizen_card import CitizenState
        from agents.town.polynomial import CitizenPhase
        from protocols.nphase.operad import NPhase

        citizens = (
            CitizenState(
                citizen_id="alice",
                name="Alice",
                archetype="builder",
                phase=CitizenPhase.WORKING,
                nphase=NPhase.ACT,
                warmth=0.6,
                curiosity=0.8,
                trust=0.7,
            ),
            CitizenState(
                citizen_id="bob",
                name="Bob",
                archetype="trader",
                phase=CitizenPhase.SOCIALIZING,
                nphase=NPhase.SENSE,
                warmth=0.8,
                curiosity=0.5,
                trust=0.6,
            ),
        )

        state = ColonyState(
            colony_id="test-colony",
            citizens=citizens,
            phase=TownPhase.MORNING,
            day=3,
            total_events=42,
            total_tokens=1500,
            entropy_budget=0.75,
            grid_cols=4,
        )
        return ColonyDashboard(state)

    def test_colony_dashboard_has_required_fields(self, colony_dashboard: Any) -> None:
        """Verify all ColonyDashboardJSON required fields are present."""
        from agents.i.reactive.widget import RenderTarget

        json_output = colony_dashboard.project(RenderTarget.JSON)

        errors = validate_schema(json_output, COLONY_DASHBOARD_SCHEMA)
        assert not errors, "Schema validation failed:\n" + "\n".join(errors)

    def test_colony_dashboard_metrics_structure(self, colony_dashboard: Any) -> None:
        """Verify metrics field matches ColonyMetrics TypeScript type."""
        from agents.i.reactive.widget import RenderTarget

        json_output = colony_dashboard.project(RenderTarget.JSON)

        assert "metrics" in json_output, "Missing metrics field"
        metrics = json_output["metrics"]

        errors = validate_schema(metrics, COLONY_METRICS_SCHEMA, "metrics")
        assert not errors, "Metrics schema validation failed:\n" + "\n".join(errors)

    def test_colony_dashboard_citizens_match_citizen_card_schema(
        self, colony_dashboard: Any
    ) -> None:
        """
        CRITICAL: Verify each citizen in dashboard matches CitizenCardJSON.

        This is the main contract that was violated - citizens were missing
        'citizen_id' and 'eigenvectors' fields.
        """
        from agents.i.reactive.widget import RenderTarget

        json_output = colony_dashboard.project(RenderTarget.JSON)

        assert "citizens" in json_output, "Missing citizens array"
        assert len(json_output["citizens"]) > 0, "Expected at least one citizen"

        for i, citizen in enumerate(json_output["citizens"]):
            # Validate against CitizenCardJSON schema
            errors = validate_schema(citizen, CITIZEN_CARD_SCHEMA, f"citizens[{i}]")
            assert not errors, f"Citizen {i} schema validation failed:\n" + "\n".join(
                errors
            )

            # Validate eigenvectors nested structure
            if "eigenvectors" in citizen:
                eig_errors = validate_schema(
                    citizen["eigenvectors"],
                    CITIZEN_EIGENVECTORS_SCHEMA,
                    f"citizens[{i}].eigenvectors",
                )
                assert not eig_errors, (
                    f"Citizen {i} eigenvectors validation failed:\n"
                    + "\n".join(eig_errors)
                )


class TestLiveStateContract:
    """Verify /live SSE endpoint emits data matching frontend types."""

    def test_build_colony_dashboard_matches_contract(self) -> None:
        """
        Verify build_colony_dashboard() output matches ColonyDashboardJSON.

        This function is used by the /live SSE endpoint to emit state updates.
        """
        from agents.i.reactive.widget import RenderTarget
        from agents.town.environment import create_phase3_environment
        from agents.town.flux import TownFlux
        from protocols.api.town import build_colony_dashboard

        # Create a minimal environment
        env = create_phase3_environment()
        flux = TownFlux(env, seed=42)

        # Build dashboard (same as API does)
        dashboard = build_colony_dashboard(env, flux, tick=10)
        json_output = dashboard.project(RenderTarget.JSON)

        # Validate top-level structure
        errors = validate_schema(json_output, COLONY_DASHBOARD_SCHEMA)
        assert not errors, "Dashboard schema validation failed:\n" + "\n".join(errors)

        # Validate each citizen
        for i, citizen in enumerate(json_output["citizens"]):
            errors = validate_schema(citizen, CITIZEN_CARD_SCHEMA, f"citizens[{i}]")
            assert not errors, f"Citizen {i} schema validation failed:\n" + "\n".join(
                errors
            )

            # Extra strict: verify the exact fields that caused the bug
            assert "citizen_id" in citizen, (
                f"citizens[{i}] must have 'citizen_id' not 'id'"
            )
            assert "eigenvectors" in citizen, f"citizens[{i}] must have 'eigenvectors'"
            assert "warmth" in citizen["eigenvectors"], (
                f"citizens[{i}].eigenvectors must have 'warmth'"
            )


# =============================================================================
# Documentation
# =============================================================================


class TestContractDocumentation:
    """Ensure contract test documentation stays current."""

    def test_typescript_types_location_documented(self) -> None:
        """Verify we document where the source of truth is."""
        # This test exists to remind maintainers where types are defined
        import os

        types_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "web",
            "src",
            "reactive",
            "types.ts",
        )
        # Normalize the path
        types_path = os.path.normpath(types_path)

        # The file should exist (if web module is present)
        # This is a soft check - web may not be installed in all CI environments
        if os.path.exists(os.path.dirname(types_path)):
            assert os.path.exists(types_path), (
                f"TypeScript types file not found at expected location: {types_path}\n"
                "If you moved the types file, update the contract tests!"
            )
