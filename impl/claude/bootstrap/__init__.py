"""
Bootstrap Agents - The irreducible kernel of kgents.

DEPRECATION NOTICE (2025-12-16):
    This module is deprecated. Import from the new locations:

    - Types: from agents.poly.types import Agent, Result, Tension, ...
    - DNA: from protocols.config.dna import BaseDNA, HypothesisDNA, ...
    - Operations: from agents.poly import PolyAgent, ...

    This shim re-exports for backward compatibility and will emit
    a DeprecationWarning on import.

The 7 bootstrap agents from which all of kgents can be regenerated:
- Id: Identity agent (composition unit)
- Compose: Sequential composition (f >> g)
- Judge: Value function (7 principles)
- Ground: Empirical seed (persona, world)
- Contradict: Tension detection
- Sublate: Hegelian synthesis
- Fix: Fixed-point iteration

See spec/bootstrap.md for the full specification.
"""

import warnings
from typing import Any, Dict, Optional

# Emit deprecation warning on import
warnings.warn(
    "The bootstrap module is deprecated. "
    "Import from agents.poly.types (for Agent, Result, Tension, etc.) "
    "or protocols.config.dna (for DNA classes) instead.",
    DeprecationWarning,
    stacklevel=2,
)

# === Types (from agents.poly.types) ===
from agents.poly.types import (
    VOID,
    Agent,
    AgentProtocol,
    ComposedAgent,
    ContradictInput,
    ContradictResult,
    Err,
    Facts,
    FixConfig,
    FixResult,
    HoldTension,
    JudgeInput,
    Ok,
    PartialVerdict,
    PersonaSeed,
    Principles,
    Result,
    SublateInput,
    SublateResult,
    Synthesis,
    Tension,
    TensionMode,
    Verdict,
    VerdictType,
    Void,
    WorldSeed,
    err,
    ok,
)

# === Agents (still in bootstrap for now, pending further migration) ===
from .compose import Compose, compose, decompose, depth, flatten, pipeline
from .contradict import Contradict, TensionDetector, contradict
from .fix import Fix, fix, iterate_until_stable, poll_until_stable
from .ground import Ground, ground
from .id import ID, Id
from .judge import Judge, accepts, judge
from .sublate import Sublate, resolve_or_hold, sublate

__all__ = [
    # Base types
    "Agent",
    "AgentProtocol",
    "ComposedAgent",
    # Result type
    "Result",
    "Ok",
    "Err",
    "ok",
    "err",
    # Tension types
    "Tension",
    "TensionMode",
    "Synthesis",
    "HoldTension",
    # Verdict types
    "Verdict",
    "VerdictType",
    "PartialVerdict",
    "Principles",
    # Ground types
    "PersonaSeed",
    "WorldSeed",
    "Facts",
    # Fix types
    "FixConfig",
    "FixResult",
    # Input/Output types
    "ContradictInput",
    "ContradictResult",
    "SublateInput",
    "SublateResult",
    "JudgeInput",
    # Void
    "Void",
    "VOID",
    # Agents
    "Id",
    "ID",
    "Ground",
    "ground",
    "Compose",
    "compose",
    "pipeline",
    "decompose",
    "flatten",
    "depth",
    "Contradict",
    "contradict",
    "TensionDetector",
    "Judge",
    "judge",
    "accepts",
    "Sublate",
    "sublate",
    "resolve_or_hold",
    "Fix",
    "fix",
    "iterate_until_stable",
    "poll_until_stable",
    # Helpers
    "make_default_principles",
]


# --- Helper Functions ---


def make_default_principles() -> Dict[str, Any]:
    """
    Create the default 7 principles configuration.

    Returns a dictionary with principle names and their default settings.
    This is used by evolve.py and other tools that need principle-aware judgment.
    """
    return {
        "tasteful": {
            "name": Principles.TASTEFUL,
            "description": "Clear, justified purpose; no bloat",
            "enabled": True,
        },
        "curated": {
            "name": Principles.CURATED,
            "description": "Unique value; quality over quantity",
            "enabled": True,
        },
        "ethical": {
            "name": Principles.ETHICAL,
            "description": "Transparent, respects agency",
            "enabled": True,
        },
        "joyful": {
            "name": Principles.JOYFUL,
            "description": "Personality, warmth, collaboration feel",
            "enabled": True,
        },
        "composable": {
            "name": Principles.COMPOSABLE,
            "description": "Works with others; single outputs; category laws",
            "enabled": True,
        },
        "heterarchical": {
            "name": Principles.HETERARCHICAL,
            "description": "Can lead or follow; no fixed hierarchy",
            "enabled": True,
        },
        "generative": {
            "name": Principles.GENERATIVE,
            "description": "Regenerable from spec; compressed design",
            "enabled": True,
        },
    }
