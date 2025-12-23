"""
Bootstrap Layer: CONSTITUTION as the Axiomatic Root.

This module establishes CONSTITUTION as the single root of the derivation DAG.
All bootstrap agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)
derive from CONSTITUTION, making the derivation hierarchy explicit:

    CONSTITUTION (AXIOM tier, confidence = 1.0)
         |
         +-- Id, Compose, Judge, Ground, Contradict, Sublate, Fix (BOOTSTRAP tier)
                   |
                   +-- Flux, Cooled, etc. (FUNCTOR tier)
                            |
                            +-- ... (lower tiers)

The CONSTITUTION derivation carries all seven principles with categorical
evidence. This is not redundant—it establishes that:

1. The principles ARE the axiom base (not derived from anything)
2. Every agent's principle draws can trace back to CONSTITUTION
3. The derivation DAG has a single, visualizable root

Teaching:
    gotcha: CONSTITUTION is AXIOM tier, not BOOTSTRAP. AXIOM is above BOOTSTRAP.
            This is the only place where Law 1 (Monotonicity) allows derivation
            from a higher tier—because AXIOM -> BOOTSTRAP is the special case.

    gotcha: CONSTITUTION's principle draws are the SOURCE of principles.
            Bootstrap agents "inherit" their principle draws through derivation,
            though they also have their own specific categorical evidence.

    eureka: The derivation DAG now has one root, not seven. This enables:
            - Single-root visualization
            - Complete ancestry chains for any agent
            - Unified confidence propagation from the source
"""

from __future__ import annotations

from .types import (
    Derivation,
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)

# The seven principles from spec/principles/CONSTITUTION.md
SEVEN_PRINCIPLES: tuple[str, ...] = (
    "Tasteful",
    "Curated",
    "Ethical",
    "Joy-Inducing",
    "Composable",
    "Heterarchical",
    "Generative",
)


def _make_constitutional_draw(principle: str) -> PrincipleDraw:
    """
    Create a constitutional principle draw.

    Constitutional draws are:
    - Strength 1.0 (fully instantiated)
    - CATEGORICAL evidence (formal, never decays)
    - Source: "constitution" (the axiom itself)
    """
    return PrincipleDraw(
        principle=principle,
        draw_strength=1.0,
        evidence_type=EvidenceType.CATEGORICAL,
        evidence_sources=("constitution",),
    )


# The CONSTITUTION derivation—axiomatic root of all derivations
CONSTITUTION_DERIVATION: Derivation = Derivation(
    agent_name="CONSTITUTION",
    tier=DerivationTier.AXIOM,
    derives_from=(),  # True root—no parents
    principle_draws=tuple(_make_constitutional_draw(p) for p in SEVEN_PRINCIPLES),
    inherited_confidence=1.0,
    empirical_confidence=1.0,
    stigmergic_confidence=1.0,
)


# Bootstrap agents now derive from CONSTITUTION
# This mapping is used by the registry to seed bootstrap agents correctly
BOOTSTRAP_AGENT_NAMES: tuple[str, ...] = (
    "Id",
    "Compose",
    "Judge",
    "Ground",
    "Contradict",
    "Sublate",
    "Fix",
)


__all__ = [
    "SEVEN_PRINCIPLES",
    "CONSTITUTION_DERIVATION",
    "BOOTSTRAP_AGENT_NAMES",
]
