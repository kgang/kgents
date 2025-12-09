"""
Obsidian Integration for Mirror Protocol.

This module provides local-first analysis of Obsidian vaults:
- extractor.py: P-gent for extracting principles from vault
- witness.py: W-gent for observing behavioral patterns
- tension.py: H-gent for detecting contradictions

Why Obsidian first:
- Local-first (no API rate limits, no privacy concerns)
- File-based (easy to parse, easy to test)
- Knowledge-focused (principles are explicit)
- Personal use possible (test on ourselves first)
"""

from .extractor import (
    ObsidianPrincipleExtractor,
    extract_principles_from_vault,
)
from .witness import (
    ObsidianPatternWitness,
    observe_vault_patterns,
)
from .tension import (
    ObsidianTensionDetector,
    detect_tensions,
)

__all__ = [
    # Extractor (P-gent)
    "ObsidianPrincipleExtractor",
    "extract_principles_from_vault",
    # Witness (W-gent)
    "ObsidianPatternWitness",
    "observe_vault_patterns",
    # Tension (H-gent)
    "ObsidianTensionDetector",
    "detect_tensions",
]
