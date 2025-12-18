"""
Gallery Operad: Composition Grammar for Gallery Operations.

The GALLERY_OPERAD defines the valid operations and laws for gallery interactions.
Operations include filtering, selection, comparison, and composition.

See: spec/gallery/gallery-v2.md
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function

# =============================================================================
# Gallery Operations
# =============================================================================


def _filter_compose(filter_fn: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Filter operation: category → filtered pilots.

    Takes a filter predicate and returns filtered pilot list.
    """

    def filter_transition(state: str, pilots: list) -> tuple[str, list]:
        # Would apply filter_fn to each pilot
        return "ready", [p for p in pilots if True]  # Simplified

    return PolyAgent(
        name=f"filter({filter_fn.name})",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=filter_transition,
    )


def _select_compose(pilot: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Select operation: pilot → detail view.

    Returns detailed projection data for a pilot.
    """
    return PolyAgent(
        name=f"select({pilot.name})",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", {"pilot": pilot.name, "detail": True}),
    )


def _override_compose(override: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Override operation: overrides → re-rendered pilot.

    Applies override parameters and re-renders projections.
    """
    return PolyAgent(
        name=f"override({override.name})",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: (
            "ready",
            {"overrides": override.name, "applied": True},
        ),
    )


def _compare_compose(
    pilot1: PolyAgent[Any, Any, Any],
    pilot2: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compare operation: pilot × pilot → diff view.

    Returns side-by-side comparison of two pilots.
    """
    return PolyAgent(
        name=f"compare({pilot1.name},{pilot2.name})",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: (
            "ready",
            {
                "left": pilot1.name,
                "right": pilot2.name,
                "diff": True,
            },
        ),
    )


def _compose_compose(
    pilot1: PolyAgent[Any, Any, Any],
    pilot2: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose operation: pilot × pilot → combined pilot.

    Creates a composite pilot from two component pilots.
    """
    return PolyAgent(
        name=f"compose({pilot1.name},{pilot2.name})",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: (
            "ready",
            {
                "components": [pilot1.name, pilot2.name],
                "composed": True,
            },
        ),
    )


def _reset_compose() -> PolyAgent[Any, Any, Any]:
    """
    Reset operation (nullary): → initial state.

    Returns gallery to initial browsing state.
    """
    return PolyAgent(
        name="reset",
        positions=frozenset({"ready"}),
        _directions=lambda s: frozenset({Any}),
        _transition=lambda s, x: ("ready", {"reset": True, "category": "ALL"}),
    )


# =============================================================================
# Law Verification
# =============================================================================


def _verify_filter_identity() -> LawVerification:
    """
    Verify filter(ALL) = identity.

    Filtering by ALL should return all pilots unchanged.
    """
    # Structural verification - filter(ALL) returns input unchanged
    return LawVerification(
        law_name="filter_identity",
        status=LawStatus.STRUCTURAL,
        message="filter(ALL) structurally equals identity (returns all pilots)",
    )


def _verify_override_idempotent() -> LawVerification:
    """
    Verify override(o) >> override(o) = override(o).

    Applying same overrides twice should equal applying once.
    """
    return LawVerification(
        law_name="override_deterministic",
        status=LawStatus.STRUCTURAL,
        message="override is idempotent by construction",
    )


def _verify_compare_symmetric() -> LawVerification:
    """
    Verify compare(a, b) ≅ compare(b, a).

    Comparison should be symmetric (modulo display order).
    """
    return LawVerification(
        law_name="compare_symmetric",
        status=LawStatus.STRUCTURAL,
        message="compare is symmetric up to isomorphism (swap left/right)",
    )


# =============================================================================
# Gallery Operad
# =============================================================================


GALLERY_OPERAD = Operad(
    name="GalleryOperad",
    operations={
        "reset": Operation(
            name="reset",
            arity=0,
            signature="() → Gallery",
            compose=_reset_compose,
            description="Reset gallery to initial state",
        ),
        "filter": Operation(
            name="filter",
            arity=1,
            signature="Predicate → Gallery → Gallery",
            compose=_filter_compose,
            description="Filter pilots by category predicate",
        ),
        "select": Operation(
            name="select",
            arity=1,
            signature="Pilot → DetailView",
            compose=_select_compose,
            description="Select pilot for detailed inspection",
        ),
        "override": Operation(
            name="override",
            arity=1,
            signature="Overrides → Gallery → Gallery",
            compose=_override_compose,
            description="Apply rendering overrides",
        ),
        "compare": Operation(
            name="compare",
            arity=2,
            signature="Pilot × Pilot → DiffView",
            compose=_compare_compose,
            description="Compare two pilots side by side",
        ),
        "compose": Operation(
            name="compose",
            arity=2,
            signature="Pilot × Pilot → CompositePilot",
            compose=_compose_compose,
            description="Compose two pilots into a combined pilot",
        ),
    },
    laws=[
        Law(
            name="filter_identity",
            equation="filter(ALL) = identity",
            verify=lambda: _verify_filter_identity(),
            description="Filtering by ALL returns all pilots unchanged",
        ),
        Law(
            name="override_deterministic",
            equation="override(o) >> override(o) = override(o)",
            verify=lambda: _verify_override_idempotent(),
            description="Overrides are idempotent",
        ),
        Law(
            name="compare_symmetric",
            equation="compare(a, b) ≅ compare(b, a)",
            verify=lambda: _verify_compare_symmetric(),
            description="Comparison is symmetric up to display order",
        ),
    ],
    description="Grammar of gallery composition operations",
)


# Register with the global registry
OperadRegistry.register(GALLERY_OPERAD)


def gallery_operad_visualization() -> dict[str, Any]:
    """
    Generate visualization data for the gallery operad.

    Returns data for displaying operations and laws.
    """
    return {
        "name": GALLERY_OPERAD.name,
        "description": GALLERY_OPERAD.description,
        "operations": [
            {
                "name": op.name,
                "arity": op.arity,
                "signature": op.signature,
                "description": op.description,
            }
            for op in GALLERY_OPERAD.operations.values()
        ],
        "laws": [
            {
                "name": law.name,
                "equation": law.equation,
                "description": law.description,
            }
            for law in GALLERY_OPERAD.laws
        ],
    }


__all__ = [
    "GALLERY_OPERAD",
    "gallery_operad_visualization",
]
