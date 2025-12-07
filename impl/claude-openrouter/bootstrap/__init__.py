"""
Bootstrap Agents - The irreducible kernel from which all of kgents can be regenerated.

The 7 bootstrap agents:
    {Id, Compose, Judge, Ground, Contradict, Sublate, Fix}

These are the residue after maximal algorithmic compression—what remains
when recursion, composition, and dialectic have done all they can.

Usage:
    from bootstrap import Id, Compose, Judge, Ground, Contradict, Sublate, Fix

    # Build a pipeline
    pipeline = validate >> transform >> persist

    # Get grounded facts
    ground = Ground()
    facts = await ground.invoke(None)

    # Check for contradictions
    contradict = Contradict()
    tension = await contradict.invoke(ContradictInput(a, b))

    # Resolve or hold
    if tension:
        sublate = Sublate()
        result = await sublate.invoke(tension)

    # Iterate to stability
    result = await fix(transform=step, initial=state)

    # Judge quality
    judge = Judge()
    verdict = await judge.invoke(JudgeInput(agent, principles))

Regeneration Sequence:
    1. Ground - Load persona from spec/k-gent/persona.md
    2. Judge - Encode 7 principles as executable evaluation
    3. Compose - Build pipelines (associative, Id as unit)
    4. Contradict - Surface tensions before they become errors
    5. Sublate - Synthesize or consciously hold
    6. Fix - Iterate until stable (Judge accepts, Contradict finds nothing)

See spec/bootstrap.md for the full specification.
"""

# Types
from .types import (
    # Base
    Agent,
    # Verdict
    Verdict,
    VerdictType,
    # Tension
    Tension,
    TensionMode,
    # Synthesis
    Synthesis,
    ResolutionType,
    HoldTension,
    # Ground
    Facts,
    PersonaSeed,
    WorldSeed,
    # Principles
    Principle,
    Principles,
)

# Bootstrap Agents
from .id import Id
from .compose import compose, ComposedAgent
from .judge import (
    Judge,
    JudgeInput,
    JudgeTaste,
    JudgeCurate,
    JudgeEthics,
    JudgeJoy,
    JudgeCompose,
    JudgeHetero,
    JudgeGenerate,
    make_default_principles,
)
from .ground import Ground
from .contradict import (
    Contradict,
    ContradictInput,
    NameCollisionChecker,
    ConfigConflictChecker,
)
from .sublate import Sublate, MergeConfigSublate
from .fix import Fix, FixConfig, FixResult, fix, RetryFix, ConvergeFix

__all__ = [
    # Types
    "Agent",
    "Verdict",
    "VerdictType",
    "Tension",
    "TensionMode",
    "Synthesis",
    "ResolutionType",
    "HoldTension",
    "Facts",
    "PersonaSeed",
    "WorldSeed",
    "Principle",
    "Principles",
    # The 7 Bootstrap Agents
    "Id",
    "compose",
    "ComposedAgent",
    "Judge",
    "JudgeInput",
    "Ground",
    "Contradict",
    "ContradictInput",
    "Sublate",
    "Fix",
    "fix",
    # Utilities
    "FixConfig",
    "FixResult",
    "make_default_principles",
    # Specialized agents
    "JudgeTaste",
    "JudgeCurate",
    "JudgeEthics",
    "JudgeJoy",
    "JudgeCompose",
    "JudgeHetero",
    "JudgeGenerate",
    "NameCollisionChecker",
    "ConfigConflictChecker",
    "MergeConfigSublate",
    "RetryFix",
    "ConvergeFix",
]

# Verify bootstrap is complete
BOOTSTRAP_AGENTS = {"Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix"}
