"""
kgents Bootstrap Agents

The 7 irreducible agents from which all of kgents can be regenerated.

    {Id, Compose, Judge, Ground, Contradict, Sublate, Fix}

These are the "residue" after maximal algorithmic compression—what remains
when recursion, composition, and dialectic have done all they can.

Minimal bootstrap: {Compose, Judge, Ground} = structure + direction + material.

Usage:
    from bootstrap import id_agent, compose, judge, ground, contradict, sublate, fix

    # Identity
    result = await id_agent.invoke(x)  # returns x

    # Composition
    pipeline = compose(agent_a, agent_b)
    result = await pipeline.invoke(input)

    # Judgment
    verdict = await judge(some_agent)

    # Ground truth
    state = await ground()

    # Contradiction detection
    tension = await contradict(thesis, antithesis)

    # Synthesis
    if tension:
        synthesis = await sublate(tension)

    # Fixed point
    stable = await fix(transform, initial)
"""

# Types
from .types import (
    # Core
    Agent,

    # Verdict
    Verdict,
    VerdictStatus,

    # Principles
    Principle,
    PRINCIPLE_QUESTIONS,

    # Tension
    Tension,
    TensionMode,

    # Synthesis
    Synthesis,
    HoldTension,
    SynthesisResult,

    # Ground state
    PersonaState,
    GroundState,

    # Fix
    FixResult,
    FixConfig,
)

# Agents
from .id import Id, id_agent
from .compose import Compose, ComposedAgent, compose_agent, compose, pipeline
from .judge import Judge, JudgeInput, JudgeOutput, judge_agent, judge
from .ground import Ground, ground_agent, ground, KENT_PERSONA
from .contradict import Contradict, ContradictInput, contradict_agent, contradict
from .sublate import Sublate, SublateConfig, sublate_agent, sublate
from .fix import Fix, FixInput, fix_agent, fix, iterate_until_stable

# The bootstrap set
BOOTSTRAP_AGENTS = {
    'Id': id_agent,
    'Compose': compose_agent,
    'Judge': judge_agent,
    'Ground': ground_agent,
    'Contradict': contradict_agent,
    'Sublate': sublate_agent,
    'Fix': fix_agent,
}

__all__ = [
    # Types
    'Agent',
    'Verdict', 'VerdictStatus',
    'Principle', 'PRINCIPLE_QUESTIONS',
    'Tension', 'TensionMode',
    'Synthesis', 'HoldTension', 'SynthesisResult',
    'PersonaState', 'GroundState',
    'FixResult', 'FixConfig',

    # Agent classes
    'Id', 'Compose', 'ComposedAgent', 'Judge', 'Ground', 'Contradict', 'Sublate', 'Fix',

    # Singleton instances
    'id_agent', 'compose_agent', 'judge_agent', 'ground_agent',
    'contradict_agent', 'sublate_agent', 'fix_agent',

    # Convenience functions
    'compose', 'pipeline', 'judge', 'ground', 'contradict', 'sublate',
    'fix', 'iterate_until_stable',

    # Data
    'BOOTSTRAP_AGENTS', 'KENT_PERSONA',
    'JudgeInput', 'JudgeOutput', 'ContradictInput', 'FixInput', 'SublateConfig',
]
