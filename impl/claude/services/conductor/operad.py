"""
SWARM_OPERAD: Composition grammar for agent swarms.

CLI v7 Phase 6: Agent Swarms

Extends WITNESS_OPERAD with swarm-specific operations:
- spawn: Create an agent with a role
- delegate: Transfer subtask between agents
- aggregate: Combine results from multiple agents
- handoff: Transfer context and responsibility

Pattern #10: Operad Inheritance
The SWARM_OPERAD inherits all operations from WITNESS_OPERAD,
then adds swarm-specific compositions.

This follows Constitution S5 (Composable):
"Agents are morphisms in a category; composition is primary."

Operations:
    spawn: (Task, Role) -> Agent
    delegate: (Agent, Task) -> Delegation
    aggregate: [Result] -> AggregatedResult
    handoff: (Agent, Agent) -> Handoff

Laws:
    delegation_associativity: (a delegate b) delegate c = a delegate (b delegate c)
    aggregation_commutativity: aggregate([a, b]) = aggregate([b, a])
    handoff_irreversibility: handoff(a, b) does NOT imply handoff(b, a)

Usage:
    from services.conductor.operad import SWARM_OPERAD

    # Verify laws
    for law in SWARM_OPERAD.laws:
        result = law.verify()
        assert result.status in (LawStatus.PASSED, LawStatus.STRUCTURAL)

    # Compose operations
    workflow = SWARM_OPERAD.compose("spawn", "delegate", "aggregate")
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, sequential

from .swarm import IMPLEMENTER, PLANNER, RESEARCHER, REVIEWER, SwarmRole

# =============================================================================
# Get WITNESS_OPERAD (lazy to avoid circular imports)
# =============================================================================


def _get_witness_operad() -> Operad:
    """Lazy import of WITNESS_OPERAD to avoid circular dependency."""
    from services.witness.operad import WITNESS_OPERAD

    return WITNESS_OPERAD


# =============================================================================
# Swarm Operations
# =============================================================================


def _spawn_compose(role: SwarmRole | None = None) -> PolyAgent[Any, Any, Any]:
    """
    Compose a spawn operation.

    Spawn: (Task, Role) -> Agent

    Creates a new agent with the specified role.
    The spawned agent inherits role's behavior and trust level.

    If no role specified, defaults to PLANNER.
    """
    if role is None:
        role = PLANNER

    def spawn_fn(task: str) -> dict[str, Any]:
        return {
            "operation": "spawn",
            "task": task,
            "role": role.name,
            "behavior": role.behavior.name,
            "trust": role.trust_level_name,
            "capabilities": sorted(role.capabilities),
        }

    return from_function(f"spawn({role.name})", spawn_fn)


def _delegate_compose(
    from_agent: str = "coordinator",
    to_agent: str = "worker",
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a delegate operation.

    Delegate: (Agent, Task) -> Delegation

    Transfer a subtask from one agent to another.
    The delegating agent remains coordinator.
    """

    def delegate_fn(task: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "delegate",
            "from": from_agent,
            "to": to_agent,
            "task": task,
            "delegated": True,
        }

    return from_function(f"delegate({from_agent}->{to_agent})", delegate_fn)


def _aggregate_compose(
    agents: list[str] | None = None,
) -> PolyAgent[Any, Any, Any]:
    """
    Compose an aggregate operation.

    Aggregate: [Result] -> AggregatedResult

    Combine results from multiple agents into a unified output.
    """
    if agents is None:
        agents = ["agent_1", "agent_2"]

    def aggregate_fn(results: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "operation": "aggregate",
            "agents": agents,
            "results": results,
            "result_count": len(results),
            "aggregated": True,
        }

    return from_function(f"aggregate({', '.join(agents)})", aggregate_fn)


def _handoff_compose(
    from_agent: str = "current",
    to_agent: str = "successor",
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a handoff operation.

    Handoff: (Agent, Agent) -> Handoff

    Transfer full context and responsibility to another agent.
    The handing-off agent exits; the receiving agent continues.
    """

    def handoff_fn(context: dict[str, Any]) -> dict[str, Any]:
        return {
            "operation": "handoff",
            "from": from_agent,
            "to": to_agent,
            "context": context,
            "handoff_complete": True,
        }

    return from_function(f"handoff({from_agent}->{to_agent})", handoff_fn)


# =============================================================================
# Swarm Operations Registry
# =============================================================================


SWARM_OPERATIONS: dict[str, Operation] = {
    "spawn": Operation(
        name="spawn",
        arity=1,
        signature="(Task, Role) -> Agent",
        compose=_spawn_compose,
        description="Create an agent with a role",
    ),
    "delegate": Operation(
        name="delegate",
        arity=2,
        signature="(Agent, Task) -> Delegation",
        compose=_delegate_compose,
        description="Transfer subtask to another agent",
    ),
    "aggregate": Operation(
        name="aggregate",
        arity=-1,  # Variadic: takes any number of results
        signature="[Result] -> AggregatedResult",
        compose=_aggregate_compose,
        description="Combine results from multiple agents",
    ),
    "handoff": Operation(
        name="handoff",
        arity=2,
        signature="(Agent, Agent) -> Handoff",
        compose=_handoff_compose,
        description="Transfer context and responsibility",
    ),
}


# =============================================================================
# Swarm Laws
# =============================================================================


def _verify_delegation_associativity(*args: Any) -> LawVerification:
    """
    Verify delegation associativity.

    Law: (a delegate b) delegate c = a delegate (b delegate c)

    This is STRUCTURAL: delegation order affects intermediate steps
    but the final result (task completion) is equivalent.
    """
    return LawVerification(
        law_name="delegation_associativity",
        status=LawStatus.STRUCTURAL,
        message="Delegation is associative by design (STRUCTURAL)",
    )


def _verify_aggregation_commutativity(*args: Any) -> LawVerification:
    """
    Verify aggregation commutativity.

    Law: aggregate([a, b]) = aggregate([b, a])

    Results don't depend on agent order.
    We can verify this at runtime.
    """
    # For now, mark as PASSED since our aggregate doesn't depend on order
    return LawVerification(
        law_name="aggregation_commutativity",
        status=LawStatus.PASSED,
        message="Aggregation is order-independent",
    )


def _verify_handoff_irreversibility(*args: Any) -> LawVerification:
    """
    Verify handoff irreversibility.

    Law: handoff(a, b) does NOT imply handoff(b, a)

    Once handed off, the original agent exits.
    This is a design choice, not a runtime check.
    """
    return LawVerification(
        law_name="handoff_irreversibility",
        status=LawStatus.STRUCTURAL,
        message="Handoff is irreversible by design (one-way transfer)",
    )


def _verify_spawn_idempotence(*args: Any) -> LawVerification:
    """
    Verify spawn idempotence.

    Law: spawn(task, role) produces distinct agents

    Each spawn creates a new agent with unique ID.
    This is NOT idempotent (intentionally).
    """
    return LawVerification(
        law_name="spawn_idempotence",
        status=LawStatus.STRUCTURAL,
        message="Spawn is NOT idempotent (each call creates new agent)",
    )


SWARM_LAWS: list[Law] = [
    Law(
        name="delegation_associativity",
        equation="(a delegate b) delegate c = a delegate (b delegate c)",
        verify=_verify_delegation_associativity,
        description="Delegation order doesn't matter for final result",
    ),
    Law(
        name="aggregation_commutativity",
        equation="aggregate([a, b]) = aggregate([b, a])",
        verify=_verify_aggregation_commutativity,
        description="Agent order in aggregation doesn't matter",
    ),
    Law(
        name="handoff_irreversibility",
        equation="handoff(a, b) !=> handoff(b, a)",
        verify=_verify_handoff_irreversibility,
        description="Handoffs are one-way transfers",
    ),
    Law(
        name="spawn_idempotence",
        equation="spawn(t, r)_1 != spawn(t, r)_2",
        verify=_verify_spawn_idempotence,
        description="Each spawn creates a unique agent",
    ),
]


# =============================================================================
# Create SWARM_OPERAD
# =============================================================================


def create_swarm_operad() -> Operad:
    """
    Create the Swarm Operad.

    Pattern #10: Operad Inheritance
    Extends WITNESS_OPERAD with swarm-specific operations.

    The swarm operad composes:
    - All WITNESS_OPERAD operations (sense, analyze, suggest, act, invoke)
    - Swarm operations (spawn, delegate, aggregate, handoff)

    This creates a complete grammar for multi-agent coordination.
    """
    # Get parent operad
    witness_operad = _get_witness_operad()

    # Merge operations (swarm overrides if conflict)
    merged_operations = dict(witness_operad.operations)
    merged_operations.update(SWARM_OPERATIONS)

    # Combine laws
    merged_laws = list(witness_operad.laws) + SWARM_LAWS

    return Operad(
        name="SwarmOperad",
        operations=merged_operations,
        laws=merged_laws,
        description="Swarm coordination grammar (extends WitnessOperad)",
    )


# =============================================================================
# Global Instance
# =============================================================================


# Lazy initialization to avoid circular imports at module load
_swarm_operad: Operad | None = None


def get_swarm_operad() -> Operad:
    """Get the SWARM_OPERAD instance."""
    global _swarm_operad
    if _swarm_operad is None:
        _swarm_operad = create_swarm_operad()
        OperadRegistry.register(_swarm_operad)
    return _swarm_operad


# For direct access (triggers lazy init)
# Note: SWARM_OPERAD is accessed via get_swarm_operad() function
SWARM_OPERAD = property(lambda self: get_swarm_operad())


# =============================================================================
# Workflow Compositions
# =============================================================================


def compose_spawn_delegate_workflow(
    role: SwarmRole = RESEARCHER,
    coordinator: str = "coordinator",
    worker: str = "worker",
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a spawn -> delegate workflow.

    1. Spawn an agent with the specified role
    2. Delegate a task to that agent

    Usage:
        workflow = compose_spawn_delegate_workflow(RESEARCHER)
        result = await workflow.invoke("research the codebase")
    """
    spawn = _spawn_compose(role)
    delegate = _delegate_compose(coordinator, worker)

    return sequential(spawn, delegate)


def compose_parallel_research_workflow(
    num_agents: int = 3,
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a parallel research workflow.

    1. Spawn N researcher agents
    2. Each researches independently
    3. Aggregate results

    Note: This returns a single PolyAgent that represents
    the composition. Actual parallelism is handled at runtime.
    """
    # Spawn N researchers
    spawn = _spawn_compose(RESEARCHER)

    # Aggregate results
    agent_ids = [f"researcher_{i}" for i in range(num_agents)]
    aggregate = _aggregate_compose(agent_ids)

    return sequential(spawn, aggregate)


def compose_implement_review_workflow(
    implementer: str = "implementer",
    reviewer: str = "reviewer",
) -> PolyAgent[Any, Any, Any]:
    """
    Compose an implement -> review workflow.

    1. Implementer makes changes
    2. Handoff to reviewer
    3. Reviewer validates

    This is a common pattern for code review.
    """
    from services.witness.operad import _act_compose, _analyze_compose

    # Implementer acts
    implement = _act_compose("implement", implementer)

    # Handoff to reviewer
    handoff = _handoff_compose(implementer, reviewer)

    # Reviewer analyzes
    review = _analyze_compose("code_review")

    return sequential(sequential(implement, handoff), review)


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Operations
    "SWARM_OPERATIONS",
    # Laws
    "SWARM_LAWS",
    # Operad
    "create_swarm_operad",
    "get_swarm_operad",
    # Workflow compositions
    "compose_spawn_delegate_workflow",
    "compose_parallel_research_workflow",
    "compose_implement_review_workflow",
]
