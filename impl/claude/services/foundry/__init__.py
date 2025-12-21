"""
Agent Foundry — Crown Jewel for JIT Agent Synthesis.

The Foundry synthesizes J-gent JIT intelligence with Alethic Projection compilation.

AGENTESE: self.foundry.* (forge, inspect, cache, promote, manifest)

Pipeline:
    Intent → RealityClassifier → MetaArchitect → Chaosmonger → TargetSelector → Projector → Artifact

Components:
- AgentFoundry: Main orchestrator service (core.py)
- FoundryNode: AGENTESE @node("self.foundry") registration (node.py)
- EphemeralAgentCache: LRU cache with metrics for ephemeral agents (cache.py)
- FoundryPolynomial: State machine for pipeline progress (polynomial.py)
- FoundryOperad: Composition grammar and laws (operad.py)
- Contracts: Frozen Request/Response dataclasses (contracts.py)

Teaching:
    gotcha: The Foundry follows the Crown Jewel Pattern — each component is a
            separate file with clear responsibility. If you're adding new
            functionality, determine which component owns it first.

    gotcha: All exports are explicit in __all__. If you add a new type, add it
            to both the import AND the __all__ list. Missing __all__ entries
            break `from services.foundry import *` patterns.

    gotcha: SAFETY IS INVIOLABLE. The Foundry ALWAYS routes CHAOTIC reality
            or unstable code to WASM sandbox. This is not configurable.
            See target_selector.py and core.py forge() for the enforcement points.

Usage:
    from services.foundry import AgentFoundry, ForgeRequest

    foundry = AgentFoundry()
    response = await foundry.forge(ForgeRequest(
        intent="parse CSV files and extract headers",
        context={"interactive": True}
    ))

    if response.success:
        print(f"Target: {response.target}")  # 'marimo' for interactive
        print(f"Artifact: {response.artifact_type}")  # 'cell'

AGENTESE:
    await logos.invoke("self.foundry", umwelt, aspect="forge", intent="parse CSV files")

See: spec/services/foundry.md, plans/foundry-synthesis.md
"""

from .cache import CacheEntry, EphemeralAgentCache
from .contracts import (
    CacheRequest,
    CacheResponse,
    ForgeRequest,
    ForgeResponse,
    FoundryManifestResponse,
    InspectRequest,
    InspectResponse,
    PromoteRequest,
    PromoteResponse,
)
from .core import AgentFoundry
from .node import (
    CacheRendering,
    ForgeRendering,
    FoundryNode,
    InspectRendering,
)
from .operad import (
    CACHE_COHERENCE_LAW,
    CACHE_GET_OPERATION,
    CACHE_LIST_OPERATION,
    FORGE_OPERATION,
    FOUNDRY_OPERAD,
    IDEMPOTENT_FORGE_LAW,
    INSPECT_OPERATION,
    INSPECT_PRESERVES_LAW,
    PROMOTE_OPERATION,
    FoundryLaw,
    FoundryLawStatus,
    FoundryLawVerification,
    FoundryOperad,
    FoundryOperation,
)
from .polynomial import (
    FOUNDRY_POLYNOMIAL,
    VALID_TRANSITIONS,
    FoundryEvent,
    FoundryPolynomial,
    FoundryState,
    FoundryStateMachine,
    FoundryTransition,
    can_transition,
    get_valid_next_states,
)

__all__ = [
    # Core
    "AgentFoundry",
    # Node
    "FoundryNode",
    "ForgeRendering",
    "InspectRendering",
    "CacheRendering",
    # Cache
    "CacheEntry",
    "EphemeralAgentCache",
    # Contracts
    "ForgeRequest",
    "ForgeResponse",
    "InspectRequest",
    "InspectResponse",
    "CacheRequest",
    "CacheResponse",
    "PromoteRequest",
    "PromoteResponse",
    "FoundryManifestResponse",
    # Polynomial
    "FoundryState",
    "FoundryEvent",
    "FoundryTransition",
    "FoundryStateMachine",
    "FoundryPolynomial",
    "FOUNDRY_POLYNOMIAL",
    "can_transition",
    "get_valid_next_states",
    "VALID_TRANSITIONS",
    # Operad
    "FoundryOperation",
    "FoundryLaw",
    "FoundryLawStatus",
    "FoundryLawVerification",
    "FoundryOperad",
    "FOUNDRY_OPERAD",
    "FORGE_OPERATION",
    "INSPECT_OPERATION",
    "PROMOTE_OPERATION",
    "CACHE_GET_OPERATION",
    "CACHE_LIST_OPERATION",
    "IDEMPOTENT_FORGE_LAW",
    "CACHE_COHERENCE_LAW",
    "INSPECT_PRESERVES_LAW",
]
