"""
Phase 4 Archetypes: Builder, Trader, Healer, Scholar, Watcher.

Each archetype represents a distinct cosmotechnical approach to the world.
Factory functions create citizens with appropriate eigenvector biases
and cosmotechnics mappings.

Heritage:
- CHATDEV: Multi-agent software dev with roles
- SIMULACRA: Generative agents with memory streams
- AGENT HOSPITAL: Domain-specific simulation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

from agents.town.citizen import (
    CONSTRUCTION_V2,
    EXCHANGE_V2,
    MEMORY_V2,
    RESTORATION,
    SYNTHESIS_V2,
    Citizen,
    Cosmotechnics,
    Eigenvectors,
)
from agents.town.evolving import EvolvingCitizen, create_evolving_citizen

# =============================================================================
# Archetype Enum
# =============================================================================


class ArchetypeKind(Enum):
    """The five Phase 4 archetypes."""

    BUILDER = auto()  # Infrastructure creation
    TRADER = auto()  # Resource exchange
    HEALER = auto()  # Social/emotional repair
    SCHOLAR = auto()  # Skill discovery, teaching
    WATCHER = auto()  # Memory witnesses, historians


# =============================================================================
# Archetype Specifications
# =============================================================================


@dataclass(frozen=True)
class ArchetypeSpec:
    """
    Specification for an archetype.

    Contains the default eigenvector biases and cosmotechnics.
    """

    kind: ArchetypeKind
    cosmotechnics: Cosmotechnics
    # Eigenvector biases (deviation from 0.5 baseline)
    warmth_bias: float = 0.0
    curiosity_bias: float = 0.0
    trust_bias: float = 0.0
    creativity_bias: float = 0.0
    patience_bias: float = 0.0
    resilience_bias: float = 0.0
    ambition_bias: float = 0.0

    def create_eigenvectors(self, variance: float = 0.1) -> Eigenvectors:
        """
        Create eigenvectors with archetype biases.

        Args:
            variance: Random variance to add (future: use RNG)

        Returns:
            Eigenvectors with biases applied
        """
        return Eigenvectors(
            warmth=0.5 + self.warmth_bias,
            curiosity=0.5 + self.curiosity_bias,
            trust=0.5 + self.trust_bias,
            creativity=0.5 + self.creativity_bias,
            patience=0.5 + self.patience_bias,
            resilience=0.5 + self.resilience_bias,
            ambition=0.5 + self.ambition_bias,
        )


# Define the five archetypes
BUILDER_SPEC = ArchetypeSpec(
    kind=ArchetypeKind.BUILDER,
    cosmotechnics=CONSTRUCTION_V2,
    creativity_bias=0.2,  # creativity↑
    patience_bias=0.2,  # patience↑
    resilience_bias=0.1,  # resilience↑
    ambition_bias=0.15,  # ambition↑
)

TRADER_SPEC = ArchetypeSpec(
    kind=ArchetypeKind.TRADER,
    cosmotechnics=EXCHANGE_V2,
    curiosity_bias=0.2,  # curiosity↑
    trust_bias=-0.1,  # trust↓ (cautious)
    ambition_bias=0.25,  # ambition↑
    resilience_bias=0.1,  # resilience↑
)

HEALER_SPEC = ArchetypeSpec(
    kind=ArchetypeKind.HEALER,
    cosmotechnics=RESTORATION,
    warmth_bias=0.25,  # warmth↑
    patience_bias=0.2,  # patience↑
    trust_bias=0.15,  # trust↑
    resilience_bias=0.15,  # resilience↑
)

SCHOLAR_SPEC = ArchetypeSpec(
    kind=ArchetypeKind.SCHOLAR,
    cosmotechnics=SYNTHESIS_V2,
    curiosity_bias=0.3,  # curiosity↑↑
    patience_bias=0.2,  # patience↑
    creativity_bias=0.1,  # creativity↑
    ambition_bias=0.1,  # ambition↑
)

WATCHER_SPEC = ArchetypeSpec(
    kind=ArchetypeKind.WATCHER,
    cosmotechnics=MEMORY_V2,
    patience_bias=0.25,  # patience↑↑
    trust_bias=0.2,  # trust↑
    resilience_bias=0.2,  # resilience↑
    warmth_bias=0.1,  # warmth↑
)

# Registry for lookup
ARCHETYPE_SPECS: dict[ArchetypeKind, ArchetypeSpec] = {
    ArchetypeKind.BUILDER: BUILDER_SPEC,
    ArchetypeKind.TRADER: TRADER_SPEC,
    ArchetypeKind.HEALER: HEALER_SPEC,
    ArchetypeKind.SCHOLAR: SCHOLAR_SPEC,
    ArchetypeKind.WATCHER: WATCHER_SPEC,
}


# =============================================================================
# Factory Functions
# =============================================================================


def create_builder(
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a Builder citizen.

    Builders create infrastructure. They are patient, creative,
    resilient, and ambitious. Life is architecture.
    """
    spec = BUILDER_SPEC
    eigenvectors = spec.create_eigenvectors()

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    if evolving:
        return create_evolving_citizen(
            name=name,
            archetype="Builder",
            region=region,
            cosmotechnics=spec.cosmotechnics,
            eigenvectors=eigenvectors,
        )

    return Citizen(
        name=name,
        archetype="Builder",
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


def create_trader(
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a Trader citizen.

    Traders facilitate exchange. They are curious, ambitious,
    cautious with trust. Life is negotiation.
    """
    spec = TRADER_SPEC
    eigenvectors = spec.create_eigenvectors()

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    if evolving:
        return create_evolving_citizen(
            name=name,
            archetype="Trader",
            region=region,
            cosmotechnics=spec.cosmotechnics,
            eigenvectors=eigenvectors,
        )

    return Citizen(
        name=name,
        archetype="Trader",
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


def create_healer(
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a Healer citizen.

    Healers repair relationships and mend wounds. They are warm,
    patient, trusting, resilient. Life is mending.
    """
    spec = HEALER_SPEC
    eigenvectors = spec.create_eigenvectors()

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    if evolving:
        return create_evolving_citizen(
            name=name,
            archetype="Healer",
            region=region,
            cosmotechnics=spec.cosmotechnics,
            eigenvectors=eigenvectors,
        )

    return Citizen(
        name=name,
        archetype="Healer",
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


def create_scholar(
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a Scholar citizen.

    Scholars discover and teach. They are intensely curious,
    patient, creative. Life is discovery.
    """
    spec = SCHOLAR_SPEC
    eigenvectors = spec.create_eigenvectors()

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    if evolving:
        return create_evolving_citizen(
            name=name,
            archetype="Scholar",
            region=region,
            cosmotechnics=spec.cosmotechnics,
            eigenvectors=eigenvectors,
        )

    return Citizen(
        name=name,
        archetype="Scholar",
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


def create_watcher(
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a Watcher citizen.

    Watchers witness and record. They are patient, trusting,
    resilient. Life is testimony.
    """
    spec = WATCHER_SPEC
    eigenvectors = spec.create_eigenvectors()

    if eigenvector_overrides:
        eigenvectors = eigenvectors.apply_bounded_drift(eigenvector_overrides, 0.3)

    if evolving:
        return create_evolving_citizen(
            name=name,
            archetype="Watcher",
            region=region,
            cosmotechnics=spec.cosmotechnics,
            eigenvectors=eigenvectors,
        )

    return Citizen(
        name=name,
        archetype="Watcher",
        region=region,
        cosmotechnics=spec.cosmotechnics,
        eigenvectors=eigenvectors,
    )


# Registry of factory functions
ARCHETYPE_FACTORIES: dict[ArchetypeKind, Callable[..., Citizen | EvolvingCitizen]] = {
    ArchetypeKind.BUILDER: create_builder,
    ArchetypeKind.TRADER: create_trader,
    ArchetypeKind.HEALER: create_healer,
    ArchetypeKind.SCHOLAR: create_scholar,
    ArchetypeKind.WATCHER: create_watcher,
}


def create_archetype(
    kind: ArchetypeKind,
    name: str,
    region: str,
    evolving: bool = False,
    eigenvector_overrides: dict[str, float] | None = None,
) -> Citizen | EvolvingCitizen:
    """
    Create a citizen of the specified archetype.

    Generic factory that dispatches to the appropriate archetype factory.
    """
    factory = ARCHETYPE_FACTORIES[kind]
    return factory(name, region, evolving, eigenvector_overrides)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "ArchetypeKind",
    "ArchetypeSpec",
    "ARCHETYPE_SPECS",
    "BUILDER_SPEC",
    "TRADER_SPEC",
    "HEALER_SPEC",
    "SCHOLAR_SPEC",
    "WATCHER_SPEC",
    "create_builder",
    "create_trader",
    "create_healer",
    "create_scholar",
    "create_watcher",
    "create_archetype",
    "ARCHETYPE_FACTORIES",
]
