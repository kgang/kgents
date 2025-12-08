"""
Bootstrap Agents - The irreducible kernel of kgents.

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

from typing import Optional, Dict, Any

# Types
from .types import (
    # Base types
    Agent,
    AgentProtocol,
    ComposedAgent,
    # Result type
    Result,
    Ok,
    Err,
    ok,
    err,
    # Tension types
    Tension,
    TensionMode,
    Synthesis,
    HoldTension,
    # Verdict types
    Verdict,
    VerdictType,
    PartialVerdict,
    Principles,
    # Ground types
    PersonaSeed,
    WorldSeed,
    Facts,
    # Fix types
    FixConfig,
    FixResult,
    # Input/Output types
    ContradictInput,
    ContradictResult,
    SublateInput,
    SublateResult,
    JudgeInput,
    # Void
    Void,
    VOID,
)

# Agents
from .id import Id, ID
from .ground import Ground, ground
from .compose import Compose, compose, pipeline, decompose, flatten, depth
from .contradict import Contradict, contradict, TensionDetector
from .judge import Judge, judge, accepts
from .sublate import Sublate, sublate, resolve_or_hold
from .fix import Fix, fix, iterate_until_stable, poll_until_stable

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
