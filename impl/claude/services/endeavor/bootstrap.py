"""
Pilot Bootstrap Service: Match and create pilots from endeavor axioms.

Given a set of EndeavorAxioms, this service:
1. Matches existing pilots that fit the endeavor
2. Creates custom pilots when no match exists
3. Sets up witness infrastructure for new pilots

The Self-Reflective OS Pattern:
- Axioms are the specification
- Pilots are the implementation
- Witness infrastructure is the observability layer

Example:
    bootstrap = PilotBootstrapService()

    # Find matching pilot
    match = await bootstrap.match_pilot(axioms)
    if match:
        print(f"Found: {match.pilot.name} with score {match.score}")

    # Or create custom pilot
    pilot = await bootstrap.bootstrap_pilot(axioms, name="my-daily-lab")

    # Setup witness infrastructure
    config = await bootstrap.setup_witness_infrastructure(pilot)

Teaching:
    gotcha: Matching uses semantic similarity between axioms and pilot
            metadata. A score > 0.6 is considered a strong match.

    gotcha: Custom pilots are NOT persisted by default. Call
            persist_pilot() to save to disk.

    gotcha: Witness infrastructure setup creates domain-specific mark
            types and trail templates, but does NOT start the trail.

See: services/pilots/registry.py, services/witness/
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from services.pilots import PilotMetadata, PilotRegistry, get_pilot_registry

from .discovery import EndeavorAxioms

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================


@dataclass(frozen=True)
class PilotMatch:
    """
    A matched pilot for an endeavor.

    Attributes:
        pilot: The matching pilot metadata
        score: Match score (0.0 to 1.0)
        reasons: Why this pilot matches
        adaptations: Suggested adaptations to fit the endeavor
    """

    pilot: PilotMetadata
    score: float
    reasons: tuple[str, ...]
    adaptations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pilot": self.pilot.to_dict(),
            "score": self.score,
            "reasons": list(self.reasons),
            "adaptations": list(self.adaptations),
        }


@dataclass
class CustomPilot:
    """
    A custom pilot bootstrapped from axioms.

    Attributes:
        pilot_id: Unique identifier
        name: Pilot name (directory name)
        display_name: Human-readable name
        axioms: Source axioms
        composition_chain: Generated composition chain
        laws: Generated laws from axioms
        created_at: Creation timestamp
        based_on: Pilot this was based on (if any)
        persisted: Whether saved to disk
    """

    pilot_id: str
    name: str
    display_name: str
    axioms: EndeavorAxioms
    composition_chain: str
    laws: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    based_on: str | None = None
    persisted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pilot_id": self.pilot_id,
            "name": self.name,
            "display_name": self.display_name,
            "axioms": self.axioms.to_dict(),
            "composition_chain": self.composition_chain,
            "laws": self.laws,
            "created_at": self.created_at.isoformat(),
            "based_on": self.based_on,
            "persisted": self.persisted,
        }


@dataclass(frozen=True)
class WitnessConfig:
    """
    Witness infrastructure configuration for a pilot.

    Attributes:
        domain: Witness mark domain (e.g., "my-daily-lab")
        mark_types: Valid mark types for this pilot
        trail_template: Template for daily trails
        crystal_template: Template for crystal compression
        laws: Laws to enforce on marks
    """

    domain: str
    mark_types: tuple[str, ...]
    trail_template: dict[str, Any]
    crystal_template: dict[str, Any]
    laws: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "mark_types": list(self.mark_types),
            "trail_template": self.trail_template,
            "crystal_template": self.crystal_template,
            "laws": list(self.laws),
        }


# =============================================================================
# Matching Logic
# =============================================================================


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase words."""
    return set(re.findall(r"\b\w+\b", text.lower()))


def _jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def _compute_match_score(axioms: EndeavorAxioms, pilot: PilotMetadata) -> float:
    """
    Compute match score between axioms and pilot.

    Uses weighted Jaccard similarity across multiple fields.
    """
    # Build axiom tokens
    axiom_tokens = set()
    axiom_tokens.update(_tokenize(axioms.raw_endeavor))
    axiom_tokens.update(_tokenize(axioms.success_definition))
    axiom_tokens.update(_tokenize(axioms.feeling_target))
    for constraint in axioms.constraints:
        axiom_tokens.update(_tokenize(constraint))
    axiom_tokens.update(_tokenize(axioms.verification))

    # Build pilot tokens
    pilot_tokens = set()
    pilot_tokens.update(_tokenize(pilot.name))
    pilot_tokens.update(_tokenize(pilot.display_name))
    pilot_tokens.update(_tokenize(pilot.personality_tag))
    pilot_tokens.update(_tokenize(pilot.description))
    for integration in pilot.integrations:
        pilot_tokens.update(_tokenize(integration))

    # Base similarity
    base_score = _jaccard_similarity(axiom_tokens, pilot_tokens)

    # Boost for specific matches
    boost = 0.0

    # Boost for witness/mark/trace/crystal mentions
    witness_keywords = {"witness", "mark", "trace", "crystal", "daily", "journal", "lab"}
    if witness_keywords & axiom_tokens and witness_keywords & pilot_tokens:
        boost += 0.1

    # Boost for feeling alignment
    feeling_keywords = {"honest", "warm", "present", "joy", "meaningful"}
    if feeling_keywords & _tokenize(axioms.feeling_target) and feeling_keywords & _tokenize(
        pilot.personality_tag
    ):
        boost += 0.1

    return min(1.0, base_score + boost)


def _generate_match_reasons(axioms: EndeavorAxioms, pilot: PilotMetadata) -> list[str]:
    """Generate human-readable reasons for a match."""
    reasons = []

    # Check personality alignment
    personality_lower = pilot.personality_tag.lower()
    if "honest" in personality_lower:
        reasons.append("Values honesty in tracking")
    if "witness" in personality_lower:
        reasons.append("Uses witness-based observation")
    if "daily" in pilot.name.lower():
        reasons.append("Designed for daily practice")

    # Check integration alignment
    if "Witness Mark" in pilot.integrations:
        reasons.append("Supports mark capture for actions")
    if "Witness Crystal" in pilot.integrations:
        reasons.append("Compresses experience into crystals")

    # Check constraint alignment
    for constraint in axioms.constraints:
        if "time" in constraint.lower() or "minute" in constraint.lower():
            if "light" in personality_lower or "quick" in personality_lower:
                reasons.append(f"Aligns with time constraint: {constraint}")

    return reasons or ["General alignment with pilot objectives"]


def _generate_adaptations(axioms: EndeavorAxioms, pilot: PilotMetadata) -> list[str]:
    """Generate suggested adaptations to fit the endeavor."""
    adaptations = []

    # Check if pilot needs customization for constraints
    for constraint in axioms.constraints:
        if "offline" in constraint.lower():
            adaptations.append("Enable offline mode for marks")
        if "private" in constraint.lower():
            adaptations.append("Configure local-only storage")

    # Check for feeling alignment gaps
    feeling = axioms.feeling_target.lower()
    personality = pilot.personality_tag.lower()
    if "productive" in feeling and "productive" not in personality:
        adaptations.append("Add productivity indicators to trail view")
    if "calm" in feeling or "peace" in feeling:
        adaptations.append("Enable minimal UI mode")

    return adaptations


# =============================================================================
# Pilot Generation
# =============================================================================


def _generate_laws_from_axioms(axioms: EndeavorAxioms) -> list[str]:
    """Generate pilot laws from endeavor axioms."""
    laws = []

    # L1: Success verification law
    laws.append(
        f"L1 Success Verification Law: Success is defined as '{axioms.success_definition}'. "
        "The system must track progress toward this definition."
    )

    # L2: Feeling alignment law
    laws.append(
        f"L2 Feeling Alignment Law: The experience should foster '{axioms.feeling_target}'. "
        "UI and feedback must support this emotional target."
    )

    # L3-N: Constraint laws
    for i, constraint in enumerate(axioms.constraints, start=3):
        laws.append(f"L{i} Constraint Law: {constraint}. This is non-negotiable.")

    # Verification law
    n = 3 + len(axioms.constraints)
    laws.append(
        f"L{n} Verification Law: '{axioms.verification}'. "
        "This is how the system proves it's working."
    )

    return laws


def _generate_composition_chain(axioms: EndeavorAxioms) -> str:
    """Generate a composition chain for the pilot."""
    # Default chain based on axiom patterns
    chain_parts = ["Action"]

    if "daily" in axioms.raw_endeavor.lower():
        chain_parts.extend(["Mark.emit(intent)", "Trace.append(mark)", "Crystal.compress(day)"])
    elif "track" in axioms.raw_endeavor.lower():
        chain_parts.extend(["Mark.emit(event)", "Trace.accumulate(marks)", "Crystal.summarize()"])
    else:
        chain_parts.extend(["Mark.emit(action)", "Trace.append(mark)", "Crystal.compress(meaning)"])

    return " -> ".join(chain_parts)


def _slugify(name: str) -> str:
    """Convert a name to a valid directory slug."""
    # Lowercase and replace spaces with hyphens
    slug = name.lower().strip()
    slug = re.sub(r"\s+", "-", slug)
    # Remove invalid characters
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


# =============================================================================
# Service
# =============================================================================


class PilotBootstrapService:
    """
    Service for matching and creating pilots from endeavor axioms.

    Provides:
    - Pilot matching based on axiom-metadata similarity
    - Custom pilot creation from axioms
    - Witness infrastructure setup

    Example:
        bootstrap = PilotBootstrapService()

        # Match existing pilot
        match = await bootstrap.match_pilot(axioms)
        if match and match.score > 0.6:
            print(f"Use existing: {match.pilot.name}")
        else:
            # Create custom
            pilot = await bootstrap.bootstrap_pilot(axioms, "my-lab")

        # Setup witness
        config = await bootstrap.setup_witness_infrastructure(pilot)

    AI Agent Usage:
        Via AGENTESE:
            await logos.invoke(
                "self.tangibility.endeavor",
                observer,
                aspect="match",
                axioms=axioms.to_dict()
            )
    """

    def __init__(self, registry: PilotRegistry | None = None) -> None:
        """
        Initialize the bootstrap service.

        Args:
            registry: PilotRegistry to use for matching. Defaults to global.
        """
        self._registry = registry or get_pilot_registry()
        self._custom_pilots: dict[str, CustomPilot] = {}

    async def match_pilot(
        self,
        axioms: EndeavorAxioms,
        min_score: float = 0.3,
    ) -> PilotMatch | None:
        """
        Match axioms to an existing pilot.

        Args:
            axioms: Discovered endeavor axioms
            min_score: Minimum score to consider a match (default 0.3)

        Returns:
            PilotMatch if a suitable pilot found, None otherwise

        Example:
            match = await bootstrap.match_pilot(axioms)
            if match:
                print(f"Match: {match.pilot.name} ({match.score:.0%})")
                for reason in match.reasons:
                    print(f"  - {reason}")
        """
        pilots = await self._registry.list_pilots()
        best_match: PilotMatch | None = None

        for pilot in pilots:
            score = _compute_match_score(axioms, pilot)

            if score >= min_score:
                reasons = _generate_match_reasons(axioms, pilot)
                adaptations = _generate_adaptations(axioms, pilot)

                match = PilotMatch(
                    pilot=pilot,
                    score=score,
                    reasons=tuple(reasons),
                    adaptations=tuple(adaptations),
                )

                if best_match is None or score > best_match.score:
                    best_match = match

        if best_match:
            logger.info(
                f"Matched axioms to pilot '{best_match.pilot.name}' "
                f"with score {best_match.score:.2f}"
            )

        return best_match

    async def bootstrap_pilot(
        self,
        axioms: EndeavorAxioms,
        name: str,
        based_on: str | None = None,
    ) -> CustomPilot:
        """
        Bootstrap a custom pilot from axioms.

        Args:
            axioms: Discovered endeavor axioms
            name: Name for the new pilot
            based_on: Optional existing pilot to base on

        Returns:
            CustomPilot with generated laws and composition chain

        Example:
            pilot = await bootstrap.bootstrap_pilot(
                axioms,
                name="My Daily Lab",
                based_on="trail-to-crystal-daily-lab"
            )
            print(pilot.laws)
        """
        slug = _slugify(name)
        pilot_id = str(uuid.uuid4())

        # Generate laws from axioms
        laws = _generate_laws_from_axioms(axioms)

        # Generate composition chain
        chain = _generate_composition_chain(axioms)

        # If based on existing pilot, inherit some properties
        if based_on:
            base_pilot = await self._registry.get_pilot(based_on)
            if base_pilot:
                # Inherit chain pattern
                chain = base_pilot.composition_chain

        pilot = CustomPilot(
            pilot_id=pilot_id,
            name=slug,
            display_name=name,
            axioms=axioms,
            composition_chain=chain,
            laws=laws,
            based_on=based_on,
        )

        self._custom_pilots[pilot_id] = pilot

        logger.info(f"Bootstrapped custom pilot '{name}' ({slug})")
        return pilot

    async def setup_witness_infrastructure(
        self,
        pilot: CustomPilot | PilotMetadata,
    ) -> WitnessConfig:
        """
        Setup witness infrastructure for a pilot.

        Creates domain-specific mark types, trail templates, and
        crystal compression templates.

        Args:
            pilot: Custom pilot or existing pilot metadata

        Returns:
            WitnessConfig ready for use

        Example:
            config = await bootstrap.setup_witness_infrastructure(pilot)
            print(f"Domain: {config.domain}")
            print(f"Mark types: {config.mark_types}")
        """
        if isinstance(pilot, CustomPilot):
            domain = pilot.name
            axioms = pilot.axioms
            laws = tuple(pilot.laws)
        else:
            domain = pilot.name
            # For existing pilots, use generic axioms
            axioms = None
            laws = pilot.laws

        # Generate mark types
        mark_types = ["action", "reflection", "decision", "milestone"]
        if axioms and "daily" in axioms.raw_endeavor.lower():
            mark_types.extend(["morning", "evening", "gap"])

        # Generate trail template
        trail_template = {
            "name": f"{domain}-trail",
            "domain": domain,
            "structure": "chronological",
            "grouping": "by_day",
            "default_view": "timeline",
        }

        # Generate crystal template
        crystal_template = {
            "name": f"{domain}-crystal",
            "domain": domain,
            "compression": "narrative",
            "include_metrics": True,
            "warmth_target": "meaningful",
        }

        if axioms:
            crystal_template["feeling_target"] = axioms.feeling_target
            crystal_template["success_criteria"] = axioms.success_definition

        config = WitnessConfig(
            domain=domain,
            mark_types=tuple(mark_types),
            trail_template=trail_template,
            crystal_template=crystal_template,
            laws=laws,
        )

        logger.info(f"Setup witness infrastructure for domain '{domain}'")
        return config

    async def get_custom_pilot(self, pilot_id: str) -> CustomPilot | None:
        """
        Get a custom pilot by ID.

        Args:
            pilot_id: Pilot ID

        Returns:
            CustomPilot or None if not found
        """
        return self._custom_pilots.get(pilot_id)

    async def list_custom_pilots(self) -> list[CustomPilot]:
        """List all custom pilots."""
        return list(self._custom_pilots.values())

    def stats(self) -> dict[str, Any]:
        """Get service statistics."""
        return {
            "custom_pilots": len(self._custom_pilots),
            "persisted_pilots": sum(1 for p in self._custom_pilots.values() if p.persisted),
        }


# =============================================================================
# Singleton Factory
# =============================================================================


_service: PilotBootstrapService | None = None


def get_pilot_bootstrap_service() -> PilotBootstrapService:
    """
    Get the global PilotBootstrapService singleton.

    Returns:
        The singleton PilotBootstrapService instance

    Example:
        bootstrap = get_pilot_bootstrap_service()
        match = await bootstrap.match_pilot(axioms)
    """
    global _service
    if _service is None:
        _service = PilotBootstrapService()
    return _service


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "PilotBootstrapService",
    "PilotMatch",
    "CustomPilot",
    "WitnessConfig",
    "get_pilot_bootstrap_service",
]
