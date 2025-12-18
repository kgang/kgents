"""
ParkOperad: Formal Composition Grammar for Park.

Auto-generated from: spec/world/park.md
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function

# =============================================================================
# Operations
# =============================================================================


def _observe_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a observe operation.

    Scene → Metrics
    """

    def observe_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "observe",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"observe({agent_a.name})", observe_fn)


def _evaluate_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a evaluate operation.

    Metrics → Assessment
    """

    def evaluate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "evaluate",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"evaluate({agent_a.name})", evaluate_fn)


def _build_tension_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a build_tension operation.

    Scene → Scene
    """

    def build_tension_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "build_tension",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"build_tension({agent_a.name})", build_tension_fn)


def _inject_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a inject operation.

    Scene × Event → Scene
    """

    def inject_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "inject",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"inject({agent_a.name, agent_b.name})", inject_fn)


def _cooldown_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a cooldown operation.

    Scene → Scene
    """

    def cooldown_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "cooldown",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"cooldown({agent_a.name})", cooldown_fn)


def _intervene_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a intervene operation.

    Scene × Directive → Scene
    """

    def intervene_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "intervene",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"intervene({agent_a.name, agent_b.name})", intervene_fn)


# =============================================================================
# Laws
# =============================================================================


def _verify_consent(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: intervene requires participant_consent

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="consent",
        status=LawStatus.PASSED,
        message="consent verification pending implementation",
    )


def _verify_reversibility(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: inject(s, e) can be undone within window

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="reversibility",
        status=LawStatus.PASSED,
        message="reversibility verification pending implementation",
    )


def _verify_drama_bounds(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: tension_index always in [0, 1]

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="drama_bounds",
        status=LawStatus.PASSED,
        message="drama_bounds verification pending implementation",
    )


# =============================================================================
# Operad Creation
# =============================================================================


def create_park_operad() -> Operad:
    """
    Create the Park Operad.

    Extends AGENT_OPERAD with park-specific operations.
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add park-specific operations
    ops["observe"] = Operation(
        name="observe",
        arity=1,
        signature="Scene → Metrics",
        compose=_observe_compose,
        description="Observe scene metrics",
    )
    ops["evaluate"] = Operation(
        name="evaluate",
        arity=1,
        signature="Metrics → Assessment",
        compose=_evaluate_compose,
        description="Evaluate drama potential",
    )
    ops["build_tension"] = Operation(
        name="build_tension",
        arity=1,
        signature="Scene → Scene",
        compose=_build_tension_compose,
        description="Increase dramatic tension",
    )
    ops["inject"] = Operation(
        name="inject",
        arity=2,
        signature="Scene × Event → Scene",
        compose=_inject_compose,
        description="Inject serendipity",
    )
    ops["cooldown"] = Operation(
        name="cooldown",
        arity=1,
        signature="Scene → Scene",
        compose=_cooldown_compose,
        description="Reduce tension",
    )
    ops["intervene"] = Operation(
        name="intervene",
        arity=2,
        signature="Scene × Directive → Scene",
        compose=_intervene_compose,
        description="Direct intervention",
    )

    # Inherit universal laws and add park-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="consent",
            equation="intervene requires participant_consent",
            verify=_verify_consent,
            description="Consent before intervention",
        ),
        Law(
            name="reversibility",
            equation="inject(s, e) can be undone within window",
            verify=_verify_reversibility,
            description="Injections are reversible",
        ),
        Law(
            name="drama_bounds",
            equation="tension_index always in [0, 1]",
            verify=_verify_drama_bounds,
            description="Bounded drama",
        ),
    ]

    return Operad(
        name="ParkOperad",
        operations=ops,
        laws=laws,
        description="Composition grammar for Park",
    )


# =============================================================================
# Global Operad Instance
# =============================================================================


PARK_OPERAD = create_park_operad()
"""
The Park Operad.

Operations: 6
Laws: 3
Generated from: spec/world/park.md
"""

# Register with the operad registry
OperadRegistry.register(PARK_OPERAD)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "PARK_OPERAD",
    "create_park_operad",
]
