"""
Mirror Protocol: Organizational introspection and alignment.

The Mirror Protocol is a composition of five agents: P >> W >> H >> O >> J

- P-gent: Extracts principles (thesis)
- W-gent: Observes patterns (antithesis candidate)
- H-gent: Detects tensions (dialectic)
- O-gent: Reports findings
- J-gent: Executes at kairos (timing)

Phase 1 Implementation: Obsidian vault analysis (0 token cost)
- Local-first (no API dependencies)
- File-based (easy to parse and test)
- Structural analysis (no LLM calls)

See spec/protocols/mirror.md for the composition pattern.
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

from .composition import (
    # Composition API
    mirror_observe,
    mirror_status,
    mirror_reflect,
    mirror_hold,
    IntegrityStatus,
    # Formatters
    format_report,
    format_status,
    format_synthesis_options,
    format_tensions,
)

__all__ = [
    # Composition API (primary interface)
    "mirror_observe",
    "mirror_status",
    "mirror_reflect",
    "mirror_hold",
    "IntegrityStatus",
    # Formatters
    "format_report",
    "format_status",
    "format_synthesis_options",
    "format_tensions",
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
