"""
WitnessOperad: Formal Grammar for Autonomous Developer Agency.

The Witness Operad extends AGENT_OPERAD with trust-gated operations:
- sense: Observe an event source (arity=1)
- analyze: Process observations into insights (arity=1)
- suggest: Propose an action (L2+, arity=1)
- act: Execute an action (L3, arity=1)
- invoke: Cross-jewel invocation (L3, arity=2)

These operations compose to create the witness workflow:
  sense >> analyze >> suggest >> [confirm] >> act

Key Laws:
- Trust Gate: Operations cannot exceed trust level
- Reversibility: All actions must be reversible (or forbidden)
- Rate Limit: Actions per hour are bounded
- Forbidden: Some actions are never allowed

The insight: Operads + Trust Levels → Safe Autonomous Agency.

See: plans/kgentsd-crown-jewel.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function, sequential

from .polynomial import TrustLevel

# =============================================================================
# Operation Metabolics (Token Economics)
# =============================================================================


@dataclass(frozen=True)
class WitnessMetabolics:
    """Metabolic costs of a witness operation."""

    token_cost: int  # Base token estimate
    trust_required: TrustLevel  # Minimum trust level
    reversible: bool = True  # Can this be undone?
    rate_limited: bool = False  # Subject to rate limiting?

    def can_execute(self, current_trust: TrustLevel) -> bool:
        """Check if operation can execute at given trust level."""
        return current_trust >= self.trust_required


# =============================================================================
# Witness Operations (5 core operations)
# =============================================================================


# L0: Anyone can sense and analyze
SENSE_METABOLICS = WitnessMetabolics(
    token_cost=50,
    trust_required=TrustLevel.READ_ONLY,
    reversible=True,
    rate_limited=False,
)

ANALYZE_METABOLICS = WitnessMetabolics(
    token_cost=100,
    trust_required=TrustLevel.READ_ONLY,
    reversible=True,
    rate_limited=False,
)

# L2+: Suggest requires trust
SUGGEST_METABOLICS = WitnessMetabolics(
    token_cost=200,
    trust_required=TrustLevel.SUGGESTION,
    reversible=True,
    rate_limited=False,
)

# L3: Act requires full autonomy
ACT_METABOLICS = WitnessMetabolics(
    token_cost=300,
    trust_required=TrustLevel.AUTONOMOUS,
    reversible=True,  # All actions must be reversible
    rate_limited=True,  # Subject to actions-per-hour limit
)

# L3: Cross-jewel invocation
INVOKE_METABOLICS = WitnessMetabolics(
    token_cost=500,
    trust_required=TrustLevel.AUTONOMOUS,
    reversible=True,
    rate_limited=True,
)


# =============================================================================
# Composition Functions
# =============================================================================


def _sense_compose(source: str) -> PolyAgent[Any, Any, Any]:
    """
    Compose a sense operation.

    Sense: Source → Observations

    Connects to an event source and emits observations.
    Always allowed (L0+).
    """

    def sense_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "sense",
            "source": source,
            "input": input,
            "metabolics": {
                "tokens": SENSE_METABOLICS.token_cost,
                "trust_required": SENSE_METABOLICS.trust_required.name,
            },
        }

    return from_function(f"sense({source})", sense_fn)


def _analyze_compose(analyzer: str) -> PolyAgent[Any, Any, Any]:
    """
    Compose an analyze operation.

    Analyze: Observations → Insights

    Processes observations into actionable insights.
    Always allowed (L0+).
    """

    def analyze_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "analyze",
            "analyzer": analyzer,
            "input": input,
            "metabolics": {
                "tokens": ANALYZE_METABOLICS.token_cost,
                "trust_required": ANALYZE_METABOLICS.trust_required.name,
            },
        }

    return from_function(f"analyze({analyzer})", analyze_fn)


def _suggest_compose(action_type: str) -> PolyAgent[Any, Any, Any]:
    """
    Compose a suggest operation.

    Suggest: Insights → Proposal

    Creates a suggestion for human review.
    Requires L2 (SUGGESTION) trust.
    """

    def suggest_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "suggest",
            "action_type": action_type,
            "input": input,
            "requires_confirmation": True,
            "metabolics": {
                "tokens": SUGGEST_METABOLICS.token_cost,
                "trust_required": SUGGEST_METABOLICS.trust_required.name,
            },
        }

    return from_function(f"suggest({action_type})", suggest_fn)


def _act_compose(action: str, target: str | None = None) -> PolyAgent[Any, Any, Any]:
    """
    Compose an act operation.

    Act: Proposal → Result

    Executes an action autonomously.
    Requires L3 (AUTONOMOUS) trust.
    """

    def act_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "act",
            "action": action,
            "target": target,
            "input": input,
            "reversible": True,
            "metabolics": {
                "tokens": ACT_METABOLICS.token_cost,
                "trust_required": ACT_METABOLICS.trust_required.name,
                "rate_limited": ACT_METABOLICS.rate_limited,
            },
        }

    return from_function(f"act({action})", act_fn)


def _invoke_compose(
    jewel: str,
    path: str,
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a cross-jewel invocation.

    Invoke: (Jewel, Path) → Result

    Invokes another Crown Jewel's AGENTESE path.
    Requires L3 (AUTONOMOUS) trust.
    """

    def invoke_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "invoke",
            "jewel": jewel,
            "path": path,
            "input": input,
            "metabolics": {
                "tokens": INVOKE_METABOLICS.token_cost,
                "trust_required": INVOKE_METABOLICS.trust_required.name,
                "rate_limited": INVOKE_METABOLICS.rate_limited,
            },
        }

    return from_function(f"invoke({jewel}:{path})", invoke_fn)


# =============================================================================
# Witness Operations
# =============================================================================


WITNESS_OPERATIONS: dict[str, Operation] = {
    "sense": Operation(
        name="sense",
        arity=1,
        signature="Source → Observations",
        compose=_sense_compose,
        description="Observe an event source",
    ),
    "analyze": Operation(
        name="analyze",
        arity=1,
        signature="Observations → Insights",
        compose=_analyze_compose,
        description="Process observations into insights",
    ),
    "suggest": Operation(
        name="suggest",
        arity=1,
        signature="Insights → Proposal",
        compose=_suggest_compose,
        description="Propose an action for human review (L2+)",
    ),
    "act": Operation(
        name="act",
        arity=1,
        signature="Proposal → Result",
        compose=_act_compose,
        description="Execute an action autonomously (L3)",
    ),
    "invoke": Operation(
        name="invoke",
        arity=2,
        signature="(Jewel, Path) → Result",
        compose=_invoke_compose,
        description="Invoke another Crown Jewel (L3)",
    ),
}


# =============================================================================
# Witness Laws
# =============================================================================


def _check_trust_gate(trust: TrustLevel, operation: str) -> LawVerification:
    """Verify that operation respects trust level."""
    metabolics_map = {
        "sense": SENSE_METABOLICS,
        "analyze": ANALYZE_METABOLICS,
        "suggest": SUGGEST_METABOLICS,
        "act": ACT_METABOLICS,
        "invoke": INVOKE_METABOLICS,
    }

    metabolics = metabolics_map.get(operation)
    if metabolics is None:
        return LawVerification(
            law_name="trust_gate",
            status=LawStatus.SKIPPED,
            message=f"Unknown operation: {operation}",
        )

    if metabolics.can_execute(trust):
        return LawVerification(
            law_name="trust_gate",
            status=LawStatus.PASSED,
            message=f"{operation} allowed at trust level {trust.name}",
        )
    else:
        return LawVerification(
            law_name="trust_gate",
            status=LawStatus.FAILED,
            message=f"{operation} requires {metabolics.trust_required.name}, got {trust.name}",
        )


def _check_reversibility(action: str) -> LawVerification:
    """Verify that action is reversible (not forbidden)."""
    FORBIDDEN_PATTERNS = frozenset(
        {
            "git push --force",
            "rm -rf /",
            "DROP DATABASE",
            "DELETE FROM",
            "kubectl delete namespace",
            "vault token",
            "stripe",
        }
    )

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in action.lower():
            return LawVerification(
                law_name="reversibility",
                status=LawStatus.FAILED,
                message=f"Forbidden action pattern: {pattern}",
            )

    return LawVerification(
        law_name="reversibility",
        status=LawStatus.PASSED,
        message="Action is reversible",
    )


def _check_rate_limit(actions_this_hour: int, max_per_hour: int = 60) -> LawVerification:
    """Verify rate limit is not exceeded."""
    if actions_this_hour >= max_per_hour:
        return LawVerification(
            law_name="rate_limit",
            status=LawStatus.FAILED,
            message=f"Rate limit exceeded: {actions_this_hour}/{max_per_hour} per hour",
        )

    return LawVerification(
        law_name="rate_limit",
        status=LawStatus.PASSED,
        message=f"Within rate limit: {actions_this_hour}/{max_per_hour}",
    )


WITNESS_LAWS: list[Law] = [
    Law(
        name="trust_gate",
        equation="can_execute(trust, op) ⟺ trust ≥ op.required_trust",
        verify=lambda trust, op: _check_trust_gate(trust, op),
        description="Operations cannot exceed trust level",
    ),
    Law(
        name="reversibility",
        equation="∀action: reversible(action) ∨ forbidden(action)",
        verify=lambda action: _check_reversibility(action),
        description="All actions must be reversible (or forbidden)",
    ),
    Law(
        name="rate_limit",
        equation="actions_this_hour < max_per_hour",
        verify=lambda actions, max_per_hour=60: _check_rate_limit(actions, max_per_hour),
        description="Actions per hour are bounded",
    ),
]


# =============================================================================
# Create Witness Operad
# =============================================================================


def create_witness_operad() -> Operad:
    """
    Create the Witness Operad.

    Extends AGENT_OPERAD with witness-specific operations and laws.
    """
    # Merge with AGENT_OPERAD's operations
    merged_operations = dict(AGENT_OPERAD.operations)
    merged_operations.update(WITNESS_OPERATIONS)

    # Combine laws
    merged_laws = list(AGENT_OPERAD.laws) + WITNESS_LAWS

    return Operad(
        name="WitnessOperad",
        operations=merged_operations,
        laws=merged_laws,
        description="Witness Crown Jewel composition grammar",
    )


# Global operad instance
WITNESS_OPERAD = create_witness_operad()

# Register with operad registry
OperadRegistry.register(WITNESS_OPERAD)


# =============================================================================
# Workflow Compositions
# =============================================================================


def compose_observe_workflow(sources: list[str]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a complete observation workflow.

    sense(git) >> sense(tests) >> analyze(patterns)
    """
    if not sources:
        raise ValueError("At least one source required")

    # Sequential sensing
    current = _sense_compose(sources[0])
    for source in sources[1:]:
        current = sequential(current, _sense_compose(source))

    return current


def compose_suggest_workflow(
    sources: list[str],
    analyzer: str,
    action_type: str,
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a complete suggestion workflow.

    sense >> analyze >> suggest
    """
    observe = compose_observe_workflow(sources)
    analyze = _analyze_compose(analyzer)
    suggest = _suggest_compose(action_type)

    return sequential(sequential(observe, analyze), suggest)


def compose_autonomous_workflow(
    sources: list[str],
    analyzer: str,
    action: str,
    target: str | None = None,
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a complete autonomous workflow.

    sense >> analyze >> act
    """
    observe = compose_observe_workflow(sources)
    analyze = _analyze_compose(analyzer)
    act = _act_compose(action, target)

    return sequential(sequential(observe, analyze), act)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Metabolics
    "WitnessMetabolics",
    "SENSE_METABOLICS",
    "ANALYZE_METABOLICS",
    "SUGGEST_METABOLICS",
    "ACT_METABOLICS",
    "INVOKE_METABOLICS",
    # Operations
    "WITNESS_OPERATIONS",
    # Laws
    "WITNESS_LAWS",
    # Operad
    "WITNESS_OPERAD",
    "create_witness_operad",
    # Workflow compositions
    "compose_observe_workflow",
    "compose_suggest_workflow",
    "compose_autonomous_workflow",
]
