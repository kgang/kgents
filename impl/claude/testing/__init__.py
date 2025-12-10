"""
kgents testing infrastructure.

Philosophy: Tests are the executable specification.

This package provides:
- Phase 2: Law marker system and templates
- Phase 3: Property-based testing strategies (Hypothesis)
- Phase 4: Autopoietic witnesses (pytest plugin)
- Phase 5: Accursed share exploratory tests

See docs/test-evolution-plan.md for the full strategy.
"""

from .strategies import (
    simple_agents,
    agent_chains,
    valid_dna,
    invalid_dna,
    type_names,
)
from .pytest_witness import WitnessPlugin
from .flaky_registry import FlakyPattern, FlakyRegistry
from .accursed_share import Discovery, DiscoveryLog

__all__ = [
    # Strategies (Phase 3)
    "simple_agents",
    "agent_chains",
    "valid_dna",
    "invalid_dna",
    "type_names",
    # Plugin (Phase 4)
    "WitnessPlugin",
    # Flaky Registry (Phase 4)
    "FlakyPattern",
    "FlakyRegistry",
    # Discovery (Phase 5)
    "Discovery",
    "DiscoveryLog",
]
