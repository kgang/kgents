"""
Decision Operad: Composition grammar for agent decisions.

Categorical Structure:
    DECISION_OPERAD = {
        operations: {strategic, tactical, reflex, witness}
        composition: (strategic ∘ tactical) ∘ reflex = strategic ∘ (tactical ∘ reflex)
    }

The operad defines how decisions compose:
- Strategic decisions decompose into tactical decisions
- Tactical decisions decompose into reflexes
- All decisions produce witness data

This follows the kgents Operad pattern from spec/agents/operad.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, TypeVar

from .agent import AgentMode

# Type variables for generic composition
X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")
T = TypeVar("T")


class DecisionOp(Enum):
    """Operations in the decision operad."""

    STRATEGIC = "strategic"  # n inputs → 1 strategic plan
    TACTICAL = "tactical"  # n inputs → 1 tactical action
    REFLEX = "reflex"  # 1 input → 1 reflex action
    WITNESS = "witness"  # n inputs → 1 witness mark


@dataclass
class OperadOperation:
    """An operation in the decision operad."""

    op: DecisionOp
    arity: int  # Number of inputs
    description: str

    def __call__(self, *inputs: Any) -> Any:
        """Apply the operation (abstract - implementations provided by agent)."""
        raise NotImplementedError("Operations are applied by the agent")


@dataclass
class DecisionTrace:
    """
    A trace of a decision for witnessing.

    This is re-exported from witness.py for convenience,
    but defined here to show its role in the operad.
    """

    timestamp_ms: float
    mode: str
    percept_hash: str
    reasoning: str
    action_chosen: str
    alternatives_considered: list[str]
    confidence: float
    reaction_time_ms: float
    human_likeness_score: float


class DecisionOperad:
    """
    The decision operad: Grammar for agent decision composition.

    Laws:
    1. Associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
    2. Identity: Id ∘ f = f = f ∘ Id
    3. Decomposition: strategic → tactical* → reflex*

    The operad ensures that:
    - Strategic decisions can be broken into tactical decisions
    - Tactical decisions can be broken into reflexes
    - All compositions produce valid witness data
    """

    def __init__(self) -> None:
        self.operations = {
            DecisionOp.STRATEGIC: self._strategic_op,
            DecisionOp.TACTICAL: self._tactical_op,
            DecisionOp.REFLEX: self._reflex_op,
            DecisionOp.WITNESS: self._witness_op,
        }

    def compose(
        self,
        f: Callable[[X], Y],
        g: Callable[[Y], Z],
    ) -> Callable[[X], Z]:
        """
        Compose two decision functions.

        Satisfies: compose(compose(f, g), h) = compose(f, compose(g, h))
        """
        return lambda x: g(f(x))

    def identity(self) -> Callable[[T], T]:
        """
        Identity operation.

        Satisfies: compose(identity(), f) = f = compose(f, identity())
        """
        return lambda x: x

    def _strategic_op(self, considerations: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Strategic operation: Combine n considerations into a plan.

        Input: List of strategic considerations (game state, goals, threats)
        Output: Strategic plan with priorities and constraints
        """
        # Aggregate considerations
        priorities = []
        constraints = []

        for c in considerations:
            if "priority" in c:
                priorities.append(c["priority"])
            if "constraint" in c:
                constraints.append(c["constraint"])

        return {
            "type": "strategic_plan",
            "priorities": priorities,
            "constraints": constraints,
            "mode": AgentMode.STRATEGIC.value,
        }

    def _tactical_op(self, factors: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Tactical operation: Combine n factors into an action.

        Input: List of tactical factors (targets, threats, resources)
        Output: Tactical action with target and parameters
        """
        # Score factors
        scored = []
        for f in factors:
            score = f.get("score", 0)
            action = f.get("action")
            if action:
                scored.append((action, score))

        if not scored:
            return {
                "type": "tactical_action",
                "action": "none",
                "mode": AgentMode.TACTICAL.value,
            }

        best = max(scored, key=lambda x: x[1])
        return {
            "type": "tactical_action",
            "action": best[0],
            "score": best[1],
            "mode": AgentMode.TACTICAL.value,
        }

    def _reflex_op(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        """
        Reflex operation: Single stimulus → response.

        Input: Stimulus (threat, cue, etc.)
        Output: Reflex action
        """
        stimulus_type = stimulus.get("type", "unknown")

        # Hardcoded reflex mappings
        reflex_map: dict[str, dict[str, Any]] = {
            "projectile": {"action": "dodge", "direction": stimulus.get("dodge_dir")},
            "close_enemy": {"action": "retreat", "direction": stimulus.get("retreat_dir")},
            "low_health": {"action": "heal", "priority": "immediate"},
            "audio_telegraph": {"action": "prepare_dodge", "window_ms": stimulus.get("window_ms")},
        }

        response: dict[str, Any] = dict(reflex_map.get(stimulus_type, {"action": "none"}))
        response["type"] = "reflex_action"
        response["mode"] = AgentMode.REFLEXIVE.value
        return response

    def _witness_op(self, observations: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Witness operation: Combine n observations into a mark.

        Input: List of observations (actions, states, outcomes)
        Output: Witness mark for evidence
        """
        return {
            "type": "witness_mark",
            "observations": observations,
            "count": len(observations),
            "mode": "witness",
        }

    def decompose_strategic(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Decompose a strategic plan into tactical actions.

        This is the key categorical property: strategies decompose into tactics.
        """
        tactics = []

        for priority in plan.get("priorities", []):
            tactics.append(
                {
                    "type": "tactical_goal",
                    "priority": priority,
                    "from_strategic": True,
                }
            )

        return tactics

    def decompose_tactical(self, action: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Decompose a tactical action into reflexes.

        Tactics decompose into moment-to-moment reflexes.
        """
        reflexes: list[dict[str, Any]] = []

        # Attack action decomposes into: aim, fire, track
        if action.get("action") == "attack":
            reflexes.extend(
                [
                    {"type": "reflex", "action": "aim", "target": action.get("target")},
                    {"type": "reflex", "action": "fire"},
                    {"type": "reflex", "action": "track_result"},
                ]
            )

        # Move action decomposes into: orient, move, check
        elif action.get("action") == "move":
            reflexes.extend(
                [
                    {"type": "reflex", "action": "orient", "direction": action.get("direction")},
                    {"type": "reflex", "action": "move"},
                    {"type": "reflex", "action": "check_obstacles"},
                ]
            )

        return reflexes if reflexes else [{"type": "reflex", "action": "none"}]

    def verify_associativity(self) -> bool:
        """
        Verify the associativity law: (f ∘ g) ∘ h = f ∘ (g ∘ h)

        This is a categorical requirement for operads.
        """
        # Test functions
        f: Callable[[int], int] = lambda x: x + 1
        g: Callable[[int], int] = lambda x: x * 2
        h: Callable[[int], int] = lambda x: x - 3

        # Test value
        x = 10

        # (f ∘ g) ∘ h
        left = self.compose(self.compose(f, g), h)(x)

        # f ∘ (g ∘ h)
        right = self.compose(f, self.compose(g, h))(x)

        return bool(left == right)

    def verify_identity(self) -> bool:
        """
        Verify the identity law: Id ∘ f = f = f ∘ Id

        This is a categorical requirement for operads.
        """
        f: Callable[[int], int] = lambda x: x * 2
        x = 10

        # Id ∘ f
        left = self.compose(self.identity(), f)(x)

        # f
        middle = f(x)

        # f ∘ Id
        right = self.compose(f, self.identity())(x)

        return bool(left == middle == right)


# Singleton instance
DECISION_OPERAD = DecisionOperad()
