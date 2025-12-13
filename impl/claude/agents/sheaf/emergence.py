"""
Emergence: Global Soul from Local Agents.

This module demonstrates emergent behavior via sheaf gluing:
- Local soul agents (one per eigenvector)
- Glued into global Kent Soul
- Global has emergent capabilities

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from typing import Any

from agents.poly import PolyAgent, from_function

from .protocol import (
    AESTHETIC,
    CATEGORICAL,
    GENERATIVITY,
    GRATITUDE,
    HETERARCHY,
    JOY,
    SOUL_SHEAF,
    Context,
)


def create_aesthetic_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create aesthetic soul agent.

    Asks: "Does this need to exist?"
    """

    def aesthetic_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "aesthetic",
            "question": "Does this need to exist?",
            "minimalism": 0.15,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Consider what can be removed.",
        }

    return from_function("AestheticSoul", aesthetic_judgment)


def create_categorical_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create categorical soul agent.

    Asks: "What's the morphism?"
    """

    def categorical_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "categorical",
            "question": "What's the morphism?",
            "abstraction": 0.92,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Find the structure beneath the surface.",
        }

    return from_function("CategoricalSoul", categorical_judgment)


def create_gratitude_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create gratitude soul agent.

    Asks: "What deserves more respect?"
    """

    def gratitude_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "gratitude",
            "question": "What deserves more respect?",
            "sacred_lean": 0.78,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Honor the accursed share.",
        }

    return from_function("GratitudeSoul", gratitude_judgment)


def create_heterarchy_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create heterarchy soul agent.

    Asks: "Could this be peer-to-peer?"
    """

    def heterarchy_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "heterarchy",
            "question": "Could this be peer-to-peer?",
            "peer_lean": 0.88,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Forest over King.",
        }

    return from_function("HeterarchySoul", heterarchy_judgment)


def create_generativity_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create generativity soul agent.

    Asks: "What can this generate?"
    """

    def generativity_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "generativity",
            "question": "What can this generate?",
            "generation_lean": 0.90,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Spec compresses impl.",
        }

    return from_function("GenerativitySoul", generativity_judgment)


def create_joy_soul() -> PolyAgent[str, Any, dict[str, Any]]:
    """
    Create joy soul agent.

    Asks: "Where's the delight?"
    """

    def joy_judgment(input: Any) -> dict[str, Any]:
        return {
            "context": "joy",
            "question": "Where's the delight?",
            "playfulness": 0.75,  # Kent's value
            "input": str(input)[:100],
            "judgment": "Being/having fun is free :)",
        }

    return from_function("JoySoul", joy_judgment)


def create_emergent_soul() -> PolyAgent[Any, Any, Any]:
    """
    Create emergent Kent Soul via sheaf gluing.

    The global soul has capabilities that no single local soul has:
    - Asks "Does this need to exist?" AND "What's the morphism?"
    - Can operate in ANY eigenvector context
    - Emergent behavior from combined constraints

    Returns:
        Glued global soul agent
    """
    # Create local souls
    local_souls = {
        AESTHETIC: create_aesthetic_soul(),
        CATEGORICAL: create_categorical_soul(),
        GRATITUDE: create_gratitude_soul(),
        HETERARCHY: create_heterarchy_soul(),
        GENERATIVITY: create_generativity_soul(),
        JOY: create_joy_soul(),
    }

    # Glue into global soul
    return SOUL_SHEAF.glue(local_souls)


# Convenience: pre-created emergent soul
KENT_SOUL = create_emergent_soul()


def query_soul(input: Any, context: Context | None = None) -> dict[str, Any]:
    """
    Query the emergent soul.

    If context is provided, restricts to that eigenvector.
    Otherwise, uses global soul.

    Args:
        input: Query input
        context: Optional eigenvector context

    Returns:
        Soul response
    """
    if context is not None:
        # Create local soul for this context
        local_souls = {
            AESTHETIC: create_aesthetic_soul(),
            CATEGORICAL: create_categorical_soul(),
            GRATITUDE: create_gratitude_soul(),
            HETERARCHY: create_heterarchy_soul(),
            GENERATIVITY: create_generativity_soul(),
            JOY: create_joy_soul(),
        }

        if context in local_souls:
            soul = local_souls[context]
            _, result = soul.invoke("ready", input)
            return result

    # Use global soul
    _, result = KENT_SOUL.invoke("ready", input)
    return dict(result) if isinstance(result, dict) else {"response": result}


__all__ = [
    # Local souls
    "create_aesthetic_soul",
    "create_categorical_soul",
    "create_gratitude_soul",
    "create_heterarchy_soul",
    "create_generativity_soul",
    "create_joy_soul",
    # Emergent soul
    "create_emergent_soul",
    "KENT_SOUL",
    "query_soul",
]
