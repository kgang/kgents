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
]
