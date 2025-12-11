"""
AGENTESE Context Resolvers

The Five Strict Contexts:
- world.*   - The External (Heterarchical)
- self.*    - The Internal (Ethical)
- concept.* - The Abstract (Generative)
- void.*    - The Accursed Share (Meta-Principle)
- time.*    - The Temporal (Heterarchical)

No sixth context allowed without spec change.
"""

from typing import Any

# Valid context names (immutable)
VALID_CONTEXTS = frozenset({"world", "self", "concept", "void", "time"})

# Import context resolvers
from .world import (
    WorldContextResolver,
    WorldNode,
    create_world_resolver,
    create_world_node,
    WORLD_ARCHETYPE_AFFORDANCES,
)

from .self_ import (
    SelfContextResolver,
    MemoryNode,
    CapabilitiesNode,
    StateNode,
    IdentityNode,
    create_self_resolver,
    SELF_AFFORDANCES,
)

from .concept import (
    ConceptContextResolver,
    ConceptNode,
    create_concept_resolver,
    create_concept_node,
    CONCEPT_ARCHETYPE_AFFORDANCES,
)

from .void import (
    VoidContextResolver,
    EntropyPool,
    EntropyNode,
    SerendipityNode,
    GratitudeNode,
    RandomnessGrant,
    create_void_resolver,
    create_entropy_pool,
)

from .time import (
    TimeContextResolver,
    TraceNode,
    PastNode,
    FutureNode,
    ScheduleNode,
    ScheduledAction,
    create_time_resolver,
    TIME_AFFORDANCES,
)

# Agent discovery (world.agent.* namespace)
from .agents import (
    AgentContextResolver,
    AgentNode,
    AgentListNode,
    AGENT_REGISTRY,
    create_agent_resolver,
    create_agent_node,
)


# === Unified Resolver Factory ===


def create_context_resolvers(
    registry: Any = None,
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
    grammarian: Any = None,
    entropy_budget: float = 100.0,
) -> dict[str, Any]:
    """
    Create all five context resolvers with unified configuration.

    Args:
        registry: L-gent registry for entity lookup
        narrator: N-gent for narrative traces
        d_gent: D-gent for persistence and temporal projection
        b_gent: B-gent for budgeting and forecasting
        grammarian: G-gent for validation
        entropy_budget: Initial entropy budget for void context

    Returns:
        Dictionary mapping context names to resolvers
    """
    return {
        "world": create_world_resolver(registry=registry, narrator=narrator),
        "self": create_self_resolver(d_gent=d_gent, n_gent=narrator),
        "concept": create_concept_resolver(registry=registry, grammarian=grammarian),
        "void": create_void_resolver(initial_budget=entropy_budget),
        "time": create_time_resolver(narrator=narrator, d_gent=d_gent, b_gent=b_gent),
    }


__all__ = [
    # Constants
    "VALID_CONTEXTS",
    "WORLD_ARCHETYPE_AFFORDANCES",
    "SELF_AFFORDANCES",
    "CONCEPT_ARCHETYPE_AFFORDANCES",
    "TIME_AFFORDANCES",
    "AGENT_REGISTRY",
    # World context
    "WorldContextResolver",
    "WorldNode",
    "create_world_resolver",
    "create_world_node",
    # Self context
    "SelfContextResolver",
    "MemoryNode",
    "CapabilitiesNode",
    "StateNode",
    "IdentityNode",
    "create_self_resolver",
    # Concept context
    "ConceptContextResolver",
    "ConceptNode",
    "create_concept_resolver",
    "create_concept_node",
    # Void context
    "VoidContextResolver",
    "EntropyPool",
    "EntropyNode",
    "SerendipityNode",
    "GratitudeNode",
    "RandomnessGrant",
    "create_void_resolver",
    "create_entropy_pool",
    # Time context
    "TimeContextResolver",
    "TraceNode",
    "PastNode",
    "FutureNode",
    "ScheduleNode",
    "ScheduledAction",
    "create_time_resolver",
    # Agent discovery (world.agent.*)
    "AgentContextResolver",
    "AgentNode",
    "AgentListNode",
    "create_agent_resolver",
    "create_agent_node",
    # Unified factory
    "create_context_resolvers",
]
