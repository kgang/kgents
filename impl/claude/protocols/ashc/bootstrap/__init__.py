"""
ASHC Bootstrap Regeneration Module

Phase 5 of ASHC: Regenerate bootstrap agents from spec/bootstrap.md
and verify behavioral isomorphism with installed implementations.

> "The kernel that proves itself is the kernel that trusts itself."

Usage:
    from protocols.ashc.bootstrap import (
        parse_bootstrap_spec,
        BootstrapRegenerator,
        BootstrapIsomorphism,
    )

    # Parse spec
    specs = parse_bootstrap_spec()
    print(f"Found {len(specs)} agent specs")

    # Regenerate and check isomorphism
    regenerator = BootstrapRegenerator()
    result = await regenerator.regenerate()

    if result.is_isomorphic:
        print("Bootstrap can be regenerated from spec!")
"""

from .isomorphism import (
    BehaviorComparison,
    BootstrapIsomorphism,
    check_isomorphism,
)
from .parser import (
    AGENT_NAMES,
    BootstrapAgentSpec,
    parse_bootstrap_spec,
)
from .regenerator import (
    BootstrapRegenerator,
    RegenerationConfig,
)

__all__ = [
    # Parser
    "AGENT_NAMES",
    "BootstrapAgentSpec",
    "parse_bootstrap_spec",
    # Isomorphism
    "BehaviorComparison",
    "BootstrapIsomorphism",
    "check_isomorphism",
    # Regenerator
    "BootstrapRegenerator",
    "RegenerationConfig",
]
