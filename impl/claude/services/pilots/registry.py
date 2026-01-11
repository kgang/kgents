"""
Pilot Registry: Metadata discovery and management for tangible endeavor pilots.

Every pilot is defined by a PROTO_SPEC.md file that acts as a BUILD order.
This registry scans and parses those specs to provide structured metadata.

The Self-Reflective OS Pattern:
- Pilots are the tangibility layer - where specs become real
- Each pilot follows Mark -> Trace -> Crystal pipeline
- The registry is the interface between endeavors and implementations

Example:
    registry = PilotRegistry()

    # List all pilots
    all_pilots = await registry.list_pilots()

    # List by tier
    core_pilots = await registry.list_pilots(tier="core")

    # Get pilot details
    pilot = await registry.get_pilot("trail-to-crystal-daily-lab")

    # Get PROTO_SPEC content
    spec_content = await registry.get_pilot_spec("wasm-survivors-game")

Teaching:
    gotcha: Pilots are discovered at runtime by scanning pilots/*/PROTO_SPEC.md.
            If a new pilot is added, restart the service to pick it up.

    gotcha: Tier classification is inferred from PROTO_SPEC content. If the spec
            doesn't match expected patterns, the pilot defaults to "domain" tier.

    gotcha: Personality tag extraction looks for the pattern:
            > *"..."* or *"..."* after "## Personality Tag"

See: pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md (canonical example)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================


class PilotTier(str, Enum):
    """
    Classification tier for pilots.

    - CORE: Foundation pilots that implement witness infrastructure
    - DOMAIN: Domain-specific applications (games, tools, etc.)
    - META: Pilots that extend or compose other pilots
    """

    CORE = "core"
    DOMAIN = "domain"
    META = "meta"


class PilotStatus(str, Enum):
    """
    Implementation status of a pilot.

    - PRODUCTION: Fully implemented, tested, deployed
    - BETA: Feature-complete but still being refined
    - EXPERIMENTAL: Early stage, may change significantly
    - PROTO: Spec exists but minimal implementation
    """

    PRODUCTION = "production"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    PROTO = "proto"


@dataclass(frozen=True)
class PilotMetadata:
    """
    Structured metadata for a pilot.

    Extracted from PROTO_SPEC.md frontmatter and content.

    Attributes:
        name: Directory name (e.g., "trail-to-crystal-daily-lab")
        display_name: Human-readable name (e.g., "Trail to Crystal: Daily Lab")
        tier: Classification tier (core, domain, meta)
        personality_tag: The one-liner voice/philosophy
        description: Short pitch from narrative section
        proto_spec_path: Absolute path to PROTO_SPEC.md
        composition_chain: The Mark -> Trace -> Crystal chain
        status: Implementation status
        laws: List of law names (L1, L2, etc.)
        qualitative_assertions: List of QA names
        integrations: kgents primitives used
    """

    name: str
    display_name: str
    tier: PilotTier
    personality_tag: str
    description: str
    proto_spec_path: str
    composition_chain: str
    status: PilotStatus
    laws: tuple[str, ...] = field(default_factory=tuple)
    qualitative_assertions: tuple[str, ...] = field(default_factory=tuple)
    integrations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "tier": self.tier.value,
            "personality_tag": self.personality_tag,
            "description": self.description,
            "proto_spec_path": self.proto_spec_path,
            "composition_chain": self.composition_chain,
            "status": self.status.value,
            "laws": list(self.laws),
            "qualitative_assertions": list(self.qualitative_assertions),
            "integrations": list(self.integrations),
        }


# =============================================================================
# Spec Parser
# =============================================================================


def _extract_title(content: str) -> str:
    """Extract title from first H1 heading."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        # Remove any markdown formatting
        title = match.group(1).strip()
        # Remove trailing colon and anything after it for cleaner titles
        return title.split(":")[0].strip() if ":" in title else title
    return "Unknown Pilot"


def _extract_status(content: str) -> PilotStatus:
    """Extract status from Status: line."""
    # Look for "Status: **production**" or similar
    match = re.search(r"Status:\s*\*\*(\w+)\*\*", content, re.IGNORECASE)
    if match:
        status_str = match.group(1).lower()
        try:
            return PilotStatus(status_str)
        except ValueError:
            pass
    return PilotStatus.PROTO


def _extract_personality_tag(content: str) -> str:
    """Extract personality tag - the italicized quote after ## Personality Tag."""
    # Look for ## Personality Tag section
    personality_section = re.search(
        r"##\s*Personality Tag\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL
    )
    if personality_section:
        section_text = personality_section.group(1)
        # Extract italicized content: *"..."* or just *...*
        italics = re.findall(r"\*([^*]+)\*", section_text)
        if italics:
            # Join multiple italicized parts
            return " ".join(italics).strip('"').strip()
    return ""


def _extract_narrative(content: str) -> str:
    """Extract narrative description."""
    narrative_section = re.search(
        r"##\s*Narrative\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL
    )
    if narrative_section:
        # Get first sentence or paragraph
        text = narrative_section.group(1).strip()
        # Take first sentence
        first_sentence = text.split(".")[0] + "." if "." in text else text
        return first_sentence[:200]  # Limit length
    return ""


def _extract_composition_chain(content: str) -> str:
    """Extract composition chain from kgents Integrations section."""
    # Look for the chain in code block
    chain_match = re.search(
        r"(?:Composition Chain|Chain)[^`]*```\s*\n(.+?)```", content, re.IGNORECASE | re.DOTALL
    )
    if chain_match:
        chain = chain_match.group(1).strip()
        # Simplify to key primitives
        primitives = re.findall(r"(\w+(?:\.(?:emit|append|compress|seal|navigate|render))?)", chain)
        if primitives:
            # Get unique primitives in order
            seen = set()
            unique = []
            for p in primitives:
                base = p.split(".")[0]
                if base not in seen and base not in ("on", "throughout", "Action", "user"):
                    seen.add(base)
                    unique.append(base)
            return " -> ".join(unique[:6])  # Limit to first 6
    return "Mark -> Trace -> Crystal"


def _extract_laws(content: str) -> tuple[str, ...]:
    """Extract law names from Laws section."""
    laws_section = re.search(r"##\s*Laws\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL)
    if laws_section:
        # Find all L1, L2, etc. patterns
        laws = re.findall(r"\*\*L(\d+)[^*]*\*\*", laws_section.group(1))
        return tuple(f"L{n}" for n in sorted(set(laws), key=int))
    return ()


def _extract_qas(content: str) -> tuple[str, ...]:
    """Extract qualitative assertion names."""
    qa_section = re.search(
        r"##\s*Qualitative Assertions\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL
    )
    if qa_section:
        qas = re.findall(r"\*\*QA-(\d+)\*\*", qa_section.group(1))
        return tuple(f"QA-{n}" for n in sorted(set(qas), key=int))
    return ()


def _extract_integrations(content: str) -> tuple[str, ...]:
    """Extract kgents integration primitives."""
    integrations_section = re.search(
        r"##\s*kgents Integrations\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL
    )
    if integrations_section:
        # Extract primitive names from table
        primitives = re.findall(r"\*\*(\w+(?:\s+\w+)?)\*\*", integrations_section.group(1))
        return tuple(sorted(set(primitives)))
    return ()


def _infer_tier(name: str, content: str) -> PilotTier:
    """Infer tier from pilot name and content."""
    name_lower = name.lower()

    # Core pilots: witness infrastructure
    if "daily-lab" in name_lower or "trail-to-crystal" in name_lower:
        return PilotTier.CORE

    # Meta pilots: foundations, frameworks
    if "foundation" in name_lower or "categorical" in name_lower:
        return PilotTier.META

    # Zero seed is meta (governance)
    if "zero-seed" in name_lower or "governance" in name_lower:
        return PilotTier.META

    # Default to domain
    return PilotTier.DOMAIN


def _parse_proto_spec(spec_path: Path) -> PilotMetadata | None:
    """
    Parse a PROTO_SPEC.md file into PilotMetadata.

    Returns None if parsing fails.
    """
    try:
        content = spec_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to read {spec_path}: {e}")
        return None

    name = spec_path.parent.name
    display_name = _extract_title(content)
    status = _extract_status(content)
    personality_tag = _extract_personality_tag(content)
    description = _extract_narrative(content)
    composition_chain = _extract_composition_chain(content)
    tier = _infer_tier(name, content)
    laws = _extract_laws(content)
    qas = _extract_qas(content)
    integrations = _extract_integrations(content)

    return PilotMetadata(
        name=name,
        display_name=display_name,
        tier=tier,
        personality_tag=personality_tag,
        description=description,
        proto_spec_path=str(spec_path),
        composition_chain=composition_chain,
        status=status,
        laws=laws,
        qualitative_assertions=qas,
        integrations=integrations,
    )


# =============================================================================
# Registry
# =============================================================================


class PilotRegistry:
    """
    Registry for discovering and introspecting pilots.

    Scans the pilots/ directory for PROTO_SPEC.md files and provides
    structured access to pilot metadata.

    Example:
        registry = PilotRegistry()

        # List all pilots
        pilots = await registry.list_pilots()

        # Filter by tier
        core_pilots = await registry.list_pilots(tier="core")

        # Get specific pilot
        pilot = await registry.get_pilot("trail-to-crystal-daily-lab")

        # Get raw spec content
        spec = await registry.get_pilot_spec("wasm-survivors-game")
    """

    def __init__(self, pilots_root: Path | None = None) -> None:
        """
        Initialize the registry.

        Args:
            pilots_root: Root directory containing pilot subdirectories.
                        Defaults to kgents/pilots/
        """
        if pilots_root is None:
            # Navigate from impl/claude/services/pilots to kgents/pilots
            pilots_root = Path(__file__).parent.parent.parent.parent.parent / "pilots"
        self._pilots_root = pilots_root
        self._cache: dict[str, PilotMetadata] = {}
        self._scanned = False

    def _scan_pilots(self) -> None:
        """Scan for pilot PROTO_SPEC.md files and populate cache."""
        if self._scanned:
            return

        if not self._pilots_root.exists():
            logger.warning(f"Pilots directory not found: {self._pilots_root}")
            self._scanned = True
            return

        for spec_path in self._pilots_root.glob("*/PROTO_SPEC.md"):
            metadata = _parse_proto_spec(spec_path)
            if metadata:
                self._cache[metadata.name] = metadata
                logger.debug(f"Discovered pilot: {metadata.name}")

        self._scanned = True
        logger.info(f"Discovered {len(self._cache)} pilots")

    async def list_pilots(
        self,
        tier: str | PilotTier | None = None,
        status: str | PilotStatus | None = None,
    ) -> list[PilotMetadata]:
        """
        List all pilots, optionally filtered by tier or status.

        Args:
            tier: Filter by tier ("core", "domain", "meta")
            status: Filter by status ("production", "beta", etc.)

        Returns:
            List of PilotMetadata matching filters

        Example:
            # All pilots
            pilots = await registry.list_pilots()

            # Core pilots only
            core = await registry.list_pilots(tier="core")

            # Production pilots
            prod = await registry.list_pilots(status="production")
        """
        self._scan_pilots()

        # Normalize tier
        tier_filter: PilotTier | None = None
        if tier is not None:
            if isinstance(tier, str):
                tier_filter = PilotTier(tier.lower())
            else:
                tier_filter = tier

        # Normalize status
        status_filter: PilotStatus | None = None
        if status is not None:
            if isinstance(status, str):
                status_filter = PilotStatus(status.lower())
            else:
                status_filter = status

        # Filter
        result = []
        for metadata in self._cache.values():
            if tier_filter and metadata.tier != tier_filter:
                continue
            if status_filter and metadata.status != status_filter:
                continue
            result.append(metadata)

        # Sort by tier priority, then alphabetically
        tier_order = {PilotTier.CORE: 0, PilotTier.META: 1, PilotTier.DOMAIN: 2}
        result.sort(key=lambda p: (tier_order[p.tier], p.name))

        return result

    async def get_pilot(self, name: str) -> PilotMetadata | None:
        """
        Get metadata for a specific pilot.

        Args:
            name: Pilot directory name (e.g., "trail-to-crystal-daily-lab")

        Returns:
            PilotMetadata or None if not found

        Example:
            pilot = await registry.get_pilot("wasm-survivors-game")
            if pilot:
                print(pilot.personality_tag)
        """
        self._scan_pilots()
        return self._cache.get(name)

    async def get_pilot_spec(self, name: str) -> str | None:
        """
        Get the raw PROTO_SPEC.md content for a pilot.

        Args:
            name: Pilot directory name

        Returns:
            PROTO_SPEC.md content as string, or None if not found

        Example:
            spec = await registry.get_pilot_spec("trail-to-crystal-daily-lab")
            if spec:
                print(spec[:500])
        """
        self._scan_pilots()

        metadata = self._cache.get(name)
        if not metadata:
            return None

        try:
            return Path(metadata.proto_spec_path).read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read spec for {name}: {e}")
            return None

    async def match_endeavor(
        self,
        keywords: list[str],
        tier: str | None = None,
    ) -> list[tuple[PilotMetadata, float]]:
        """
        Match an endeavor to relevant pilots based on keywords.

        Args:
            keywords: Keywords from endeavor description
            tier: Optional tier filter

        Returns:
            List of (PilotMetadata, score) tuples, sorted by score descending

        Example:
            matches = await registry.match_endeavor(
                keywords=["daily", "journal", "reflection"],
                tier="core"
            )
        """
        pilots = await self.list_pilots(tier=tier)
        scored: list[tuple[PilotMetadata, float]] = []

        for pilot in pilots:
            score = 0.0
            searchable = (
                pilot.name.lower()
                + " "
                + pilot.display_name.lower()
                + " "
                + pilot.personality_tag.lower()
                + " "
                + pilot.description.lower()
                + " "
                + " ".join(pilot.integrations).lower()
            )

            for keyword in keywords:
                if keyword.lower() in searchable:
                    score += 1.0

            # Normalize by keyword count
            if keywords:
                score = score / len(keywords)

            if score > 0:
                scored.append((pilot, score))

        scored.sort(key=lambda x: -x[1])
        return scored

    def stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        self._scan_pilots()

        by_tier: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for pilot in self._cache.values():
            tier = pilot.tier.value
            status = pilot.status.value
            by_tier[tier] = by_tier.get(tier, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total": len(self._cache),
            "by_tier": by_tier,
            "by_status": by_status,
            "pilots_root": str(self._pilots_root),
        }


# =============================================================================
# Singleton Factory
# =============================================================================


_registry: PilotRegistry | None = None


def get_pilot_registry() -> PilotRegistry:
    """
    Get the global PilotRegistry singleton.

    Returns:
        The singleton PilotRegistry instance

    Example:
        registry = get_pilot_registry()
        pilots = await registry.list_pilots()
    """
    global _registry
    if _registry is None:
        _registry = PilotRegistry()
    return _registry


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "PilotMetadata",
    "PilotRegistry",
    "PilotTier",
    "PilotStatus",
    "get_pilot_registry",
]
