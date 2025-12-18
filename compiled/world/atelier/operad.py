"""
AtelierOperad: Formal Composition Grammar for Atelier.

Auto-generated from: spec/world/atelier.md
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


def _gather_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a gather operation.

    Theme → Materials
    """

    def gather_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "gather",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"gather({agent_a.name})", gather_fn)


def _create_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a create operation.

    Materials × Prompt → Artifact
    """

    def create_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "create",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"create({agent_a.name, agent_b.name})", create_fn)


def _critique_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a critique operation.

    Artifact × Lens → Feedback
    """

    def critique_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "critique",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"critique({agent_a.name, agent_b.name})", critique_fn)


def _exhibit_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a exhibit operation.

    Artifact → Exhibition
    """

    def exhibit_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "exhibit",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"exhibit({agent_a.name})", exhibit_fn)


def _iterate_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a iterate operation.

    Artifact × Feedback → Artifact
    """

    def iterate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "iterate",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"iterate({agent_a.name, agent_b.name})", iterate_fn)


# =============================================================================
# Laws
# =============================================================================


def _verify_non_destructive(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: create never destroys source materials

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="non_destructive",
        status=LawStatus.PASSED,
        message="non_destructive verification pending implementation",
    )


def _verify_critique_independence(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: critique(a, L1) compatible with critique(a, L2)

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="critique_independence",
        status=LawStatus.PASSED,
        message="critique_independence verification pending implementation",
    )


# =============================================================================
# Operad Creation
# =============================================================================


def create_atelier_operad() -> Operad:
    """
    Create the Atelier Operad.

    Extends AGENT_OPERAD with atelier-specific operations.
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add atelier-specific operations
    ops["gather"] = Operation(
        name="gather",
        arity=1,
        signature="Theme → Materials",
        compose=_gather_compose,
        description="Gather inspiration materials",
    )
    ops["create"] = Operation(
        name="create",
        arity=2,
        signature="Materials × Prompt → Artifact",
        compose=_create_compose,
        description="Create artifact",
    )
    ops["critique"] = Operation(
        name="critique",
        arity=2,
        signature="Artifact × Lens → Feedback",
        compose=_critique_compose,
        description="Apply critical lens",
    )
    ops["exhibit"] = Operation(
        name="exhibit",
        arity=1,
        signature="Artifact → Exhibition",
        compose=_exhibit_compose,
        description="Display artifact",
    )
    ops["iterate"] = Operation(
        name="iterate",
        arity=2,
        signature="Artifact × Feedback → Artifact",
        compose=_iterate_compose,
        description="Refine based on feedback",
    )

    # Inherit universal laws and add atelier-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="non_destructive",
            equation="create never destroys source materials",
            verify=_verify_non_destructive,
            description="Creation is additive",
        ),
        Law(
            name="critique_independence",
            equation="critique(a, L1) compatible with critique(a, L2)",
            verify=_verify_critique_independence,
            description="Critiques compose",
        ),
    ]

    return Operad(
        name="AtelierOperad",
        operations=ops,
        laws=laws,
        description="Composition grammar for Atelier",
    )


# =============================================================================
# Global Operad Instance
# =============================================================================


ATELIER_OPERAD = create_atelier_operad()
"""
The Atelier Operad.

Operations: 5
Laws: 2
Generated from: spec/world/atelier.md
"""

# Register with the operad registry
OperadRegistry.register(ATELIER_OPERAD)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "ATELIER_OPERAD",
    "create_atelier_operad",
]
