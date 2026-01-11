"""
Categorical Playthrough Agent System.

A revelatory testing framework that generates ASHC evidence through
AI-driven gameplay, grounded in category theory.

Core Insight: A playthrough is a morphism in the category of game states.

    Playthrough : InitialState → FinalState

The PlaythroughAgent is a polynomial functor:

    PlayAgent[Mode, Percept] → (Action, Witness)

Where Mode = Strategic | Tactical | Reflexive | Observing

The PlaythroughFarm runs multiple personas in parallel:

    FarmFunctor = product_{p in Personas} PlayAgent_p

Usage:
    # Single agent
    from services.playthrough import PlaythroughAgent, PERSONAS

    agent = PlaythroughAgent(PERSONAS["aggressive"], llm_client)
    evidence = await agent.run_playthrough(game, max_waves=10)

    # Parallel farm
    from services.playthrough import PlaythroughFarm, run_farm

    async with WasmSurvivorsFactory() as factory:
        farm_evidence = await run_farm(
            adapter_factory=factory,
            personas=["aggressive", "defensive", "novice"],
            time_scale=4.0,
            max_waves=5,
        )
"""

from .agent import AgentMode, AgentPersona, PlaythroughAgent
from .decision import DECISION_OPERAD, DecisionOperad, DecisionTrace
from .farm import (
    BalanceMatrix,
    FarmEvidence,
    FunFloorReport,
    GameAdapter,
    GameAdapterFactory,
    MockAdapterFactory,
    MockGameAdapter,
    PlaythroughFarm,
    UpgradeStats,
    run_farm,
    run_mock_farm,
)
from .perception import PerceptionSheaf, UnifiedPercept
from .personas import CORE_PERSONAS, PERSONAS, get_persona
from .reaction import HumanReactionModel
from .witness import PlaythroughEvidence, WitnessAccumulator

__all__ = [
    # Core agent
    "PlaythroughAgent",
    "AgentMode",
    "AgentPersona",
    # Perception
    "PerceptionSheaf",
    "UnifiedPercept",
    # Decision operad
    "DecisionOperad",
    "DecisionTrace",
    "DECISION_OPERAD",
    # Human model
    "HumanReactionModel",
    # Witness
    "WitnessAccumulator",
    "PlaythroughEvidence",
    # Personas
    "PERSONAS",
    "CORE_PERSONAS",
    "get_persona",
    # Farm (parallel execution)
    "PlaythroughFarm",
    "FarmEvidence",
    "FunFloorReport",
    "BalanceMatrix",
    "UpgradeStats",
    "GameAdapter",
    "GameAdapterFactory",
    "MockGameAdapter",
    "MockAdapterFactory",
    "run_farm",
    "run_mock_farm",
]
