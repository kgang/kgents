"""
Mirror Protocol: Organizational introspection and alignment.

The Mirror Protocol surfaces tensions between stated values and actual behaviors,
enabling organizations (or individuals) to become more self-aware and integrated.

Core Operations:
- Extract: P-gent extracts principles from knowledge bases
- Witness: W-gent observes behavioral patterns
- Contradict: H-gent finds tensions between stated and actual
- Sublate: H-gent proposes resolutions (when appropriate)

Phase 1 Implementation: Obsidian vault analysis
- Local-first (no API dependencies)
- File-based (easy to parse and test)
- Personal use (test on ourselves first)

See docs/mirror-protocol-implementation.md for full roadmap.
"""

from .types import (
    # Enums
    TensionMode,
    TensionType,
    InterventionType,
    PatternType,
    HoldReason,
    # Core types
    Thesis,
    Antithesis,
    Tension,
    Synthesis,
    HoldTension,
    SublateResult,
    DivergenceScore,
    # Observation types
    PatternObservation,
    # Report types
    MirrorReport,
    # Configuration
    MirrorConfig,
    # Marker constants
    SYMBOLIC_MARKERS,
    IMAGINARY_MARKERS,
    REAL_MARKERS,
    SHADOW_MAPPINGS,
)

__all__ = [
    # Enums
    "TensionMode",
    "TensionType",
    "InterventionType",
    "PatternType",
    "HoldReason",
    # Core types
    "Thesis",
    "Antithesis",
    "Tension",
    "Synthesis",
    "HoldTension",
    "SublateResult",
    "DivergenceScore",
    # Observation types
    "PatternObservation",
    # Report types
    "MirrorReport",
    # Configuration
    "MirrorConfig",
    # Marker constants
    "SYMBOLIC_MARKERS",
    "IMAGINARY_MARKERS",
    "REAL_MARKERS",
    "SHADOW_MAPPINGS",
]
