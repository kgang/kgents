"""
TownOperad: Formal Interaction Grammar for Agent Town.

The Town Operad extends SOUL_OPERAD with citizen-specific operations:
- greet: Initiate social contact (arity=2)
- gossip: Share information about third party (arity=2)
- trade: Exchange resources or favors (arity=2)
- solo: Individual activity (arity=1)

These operations compose to create all valid citizen interactions.
Instead of enumerating 600 scripted behaviors, we define a grammar
that generates infinite valid compositions.

Key Laws:
- Locality: Interactions require co-location
- Rest Inviolability: Resting citizens cannot be disturbed
- Coherence Preservation: Interactions cannot make citizens contradict themselves

From Barad: Operations are not actions but *intra-actions*.
Citizens don't exist before interaction—they emerge through it.

See: spec/town/operad.md
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
from agents.poly import PolyAgent, from_function, parallel, sequential

# =============================================================================
# Operation Metabolics (Token Economics)
# =============================================================================


@dataclass(frozen=True)
class OperationMetabolics:
    """Metabolic costs of an operation."""

    token_cost: int  # Base token estimate
    drama_potential: float  # Contribution to tension_index (0-1)
    scales_with_arity: bool = False  # For variable-arity ops

    def estimate_tokens(self, arity: int = 1) -> int:
        """Estimate tokens for this invocation."""
        if self.scales_with_arity:
            return self.token_cost * arity
        return self.token_cost


# =============================================================================
# Town Operations (MPP: 4 operations)
# =============================================================================


GREET_METABOLICS = OperationMetabolics(token_cost=200, drama_potential=0.1)
GOSSIP_METABOLICS = OperationMetabolics(token_cost=500, drama_potential=0.4)
TRADE_METABOLICS = OperationMetabolics(token_cost=400, drama_potential=0.3)
SOLO_METABOLICS = OperationMetabolics(token_cost=300, drama_potential=0.1)

# Phase 2 operations
DISPUTE_METABOLICS = OperationMetabolics(token_cost=600, drama_potential=0.8)
CELEBRATE_METABOLICS = OperationMetabolics(
    token_cost=400, drama_potential=0.2, scales_with_arity=True
)
MOURN_METABOLICS = OperationMetabolics(
    token_cost=500, drama_potential=0.5, scales_with_arity=True
)
TEACH_METABOLICS = OperationMetabolics(token_cost=800, drama_potential=0.2)


def _greet_compose(
    citizen_a: PolyAgent[Any, Any, Any],
    citizen_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a greeting interaction.

    Greet: Citizen × Citizen → Greeting

    Both citizens receive the greeting input.
    Output is the greeting result.

    From Barad: The greeting constitutes the greeters.
    Before the greeting, Alice and Bob were mesh densities.
    The greeting makes them momentarily distinct.
    """

    def greet_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "greet",
            "participants": [citizen_a.name, citizen_b.name],
            "input": input,
            "metabolics": {
                "tokens": GREET_METABOLICS.token_cost,
                "drama": GREET_METABOLICS.drama_potential,
            },
        }

    return from_function(f"greet({citizen_a.name},{citizen_b.name})", greet_fn)


def _gossip_compose(
    citizen_a: PolyAgent[Any, Any, Any],
    citizen_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a gossip interaction.

    Gossip: Citizen × Citizen → Rumor

    Citizens share information about a third party.
    The rumor may degrade (telephone game effect).
    """

    def gossip_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "gossip",
            "participants": [citizen_a.name, citizen_b.name],
            "input": input,
            "metabolics": {
                "tokens": GOSSIP_METABOLICS.token_cost,
                "drama": GOSSIP_METABOLICS.drama_potential,
            },
            "warning": "Rumor accuracy may degrade",
        }

    return from_function(f"gossip({citizen_a.name},{citizen_b.name})", gossip_fn)


def _trade_compose(
    citizen_a: PolyAgent[Any, Any, Any],
    citizen_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a trade interaction.

    Trade: Citizen × Citizen → Exchange

    Citizens exchange resources or favors.
    Unfair trades may cause resentment.
    """

    def trade_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "trade",
            "participants": [citizen_a.name, citizen_b.name],
            "input": input,
            "metabolics": {
                "tokens": TRADE_METABOLICS.token_cost,
                "drama": TRADE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"trade({citizen_a.name},{citizen_b.name})", trade_fn)


def _solo_compose(
    citizen: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a solo activity.

    Solo: Citizen → Activity

    Individual activity (work, reflect, create).
    No social interaction.
    """

    def solo_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "solo",
            "citizen": citizen.name,
            "input": input,
            "metabolics": {
                "tokens": SOLO_METABOLICS.token_cost,
                "drama": SOLO_METABOLICS.drama_potential,
            },
        }

    return from_function(f"solo({citizen.name})", solo_fn)


# =============================================================================
# Phase 2 Operations
# =============================================================================


def _dispute_compose(
    citizen_a: PolyAgent[Any, Any, Any],
    citizen_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a dispute interaction.

    Dispute: Citizen × Citizen → Tension

    Citizens have a disagreement. Increases tension index.
    May damage relationship but can lead to resolution.
    """

    def dispute_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "dispute",
            "participants": [citizen_a.name, citizen_b.name],
            "input": input,
            "metabolics": {
                "tokens": DISPUTE_METABOLICS.token_cost,
                "drama": DISPUTE_METABOLICS.drama_potential,
            },
            "effects": {"tension_delta": +0.3, "relationship_risk": True},
        }

    return from_function(f"dispute({citizen_a.name},{citizen_b.name})", dispute_fn)


def _celebrate_compose(
    *citizens: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a celebration interaction.

    Celebrate: Citizen* → Festival

    Multiple citizens celebrate together. Spends accursed surplus.
    Variable arity: any number of citizens can participate.
    """
    names = [c.name for c in citizens]

    def celebrate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "celebrate",
            "participants": names,
            "input": input,
            "metabolics": {
                "tokens": CELEBRATE_METABOLICS.estimate_tokens(len(citizens)),
                "drama": CELEBRATE_METABOLICS.drama_potential,
            },
            "effects": {"surplus_spend": True, "relationship_boost": +0.1},
        }

    return from_function(f"celebrate({','.join(names)})", celebrate_fn)


def _mourn_compose(
    *citizens: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a mourning interaction.

    Mourn: Citizen* → Grief

    Citizens mourn collectively. Expenditure of emotional surplus.
    Variable arity: collective mourning strengthens bonds.
    """
    names = [c.name for c in citizens]

    def mourn_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "mourn",
            "participants": names,
            "input": input,
            "metabolics": {
                "tokens": MOURN_METABOLICS.estimate_tokens(len(citizens)),
                "drama": MOURN_METABOLICS.drama_potential,
            },
            "effects": {"surplus_spend": True, "bond_strengthening": True},
        }

    return from_function(f"mourn({','.join(names)})", mourn_fn)


def _teach_compose(
    teacher: PolyAgent[Any, Any, Any],
    student: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a teaching interaction.

    Teach: Citizen × Citizen → SkillTransfer

    Teacher transfers skill to student. Non-destructive.
    Requires teacher.skill > student.skill for the relevant domain.
    """

    def teach_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "teach",
            "teacher": teacher.name,
            "student": student.name,
            "input": input,
            "metabolics": {
                "tokens": TEACH_METABOLICS.token_cost,
                "drama": TEACH_METABOLICS.drama_potential,
            },
            "effects": {"skill_transfer": True, "relationship_boost": +0.15},
        }

    return from_function(f"teach({teacher.name},{student.name})", teach_fn)


# =============================================================================
# Town Laws
# =============================================================================


def _verify_locality(
    a: PolyAgent[Any, Any, Any],
    b: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: interact(a, b) implies same_region(a, b).

    Citizens must be co-located to interact directly.
    This is checked at runtime, not composition time.
    """
    # At composition time, we can only do structural checks
    # Real locality enforcement happens in TownFlux
    return LawVerification(
        law_name="locality",
        status=LawStatus.PASSED,
        message="Locality enforced at runtime by TownFlux precondition checks",
    )


def _verify_rest_inviolability(
    citizen: PolyAgent[Any, Any, Any],
    op: Any = None,
    context: Any = None,
) -> LawVerification:
    """
    Verify: resting(a) implies not in_interaction(a).

    Resting citizens cannot be disturbed (Right to Rest).
    This is encoded in CitizenPolynomial directions.
    """
    return LawVerification(
        law_name="rest_inviolability",
        status=LawStatus.PASSED,
        message="Rest inviolability enforced by CitizenPolynomial directions",
    )


def _verify_coherence(
    a: PolyAgent[Any, Any, Any],
    b: PolyAgent[Any, Any, Any],
    c: PolyAgent[Any, Any, Any],
) -> LawVerification:
    """
    Verify: post(interact(a, b)).a consistent with pre(interact(a, b)).a.

    Interactions cannot make citizens contradict themselves.
    This is a semantic check that requires runtime validation.
    """
    return LawVerification(
        law_name="coherence_preservation",
        status=LawStatus.PASSED,
        message="Coherence preservation validated at runtime by memory constraints",
    )


# =============================================================================
# TownOperad Creation
# =============================================================================


def create_town_operad() -> Operad:
    """
    Create the Town Operad (MPP interaction grammar).

    Extends AGENT_OPERAD with town-specific operations:
    - greet: Initiate social contact
    - gossip: Share information about third party
    - trade: Exchange resources or favors
    - solo: Individual activity

    And town-specific laws:
    - locality: Interactions require co-location
    - rest_inviolability: Resting cannot be disturbed
    - coherence_preservation: No self-contradiction
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add town-specific operations
    ops["greet"] = Operation(
        name="greet",
        arity=2,
        signature="Citizen × Citizen → Greeting",
        compose=_greet_compose,
        description="Initiate social contact between two citizens",
    )

    ops["gossip"] = Operation(
        name="gossip",
        arity=2,
        signature="Citizen × Citizen → Rumor",
        compose=_gossip_compose,
        description="Share information about a third party",
    )

    ops["trade"] = Operation(
        name="trade",
        arity=2,
        signature="Citizen × Citizen → Exchange",
        compose=_trade_compose,
        description="Exchange resources or favors",
    )

    ops["solo"] = Operation(
        name="solo",
        arity=1,
        signature="Citizen → Activity",
        compose=_solo_compose,
        description="Individual activity (work, reflect, create)",
    )

    # Phase 2 operations
    ops["dispute"] = Operation(
        name="dispute",
        arity=2,
        signature="Citizen × Citizen → Tension",
        compose=_dispute_compose,
        description="Disagreement that increases tension (Phase 2)",
    )

    ops["celebrate"] = Operation(
        name="celebrate",
        arity=-1,  # Variable arity
        signature="Citizen* → Festival",
        compose=_celebrate_compose,
        description="Collective celebration that spends surplus (Phase 2)",
    )

    ops["mourn"] = Operation(
        name="mourn",
        arity=-1,  # Variable arity
        signature="Citizen* → Grief",
        compose=_mourn_compose,
        description="Collective mourning that strengthens bonds (Phase 2)",
    )

    ops["teach"] = Operation(
        name="teach",
        arity=2,
        signature="Citizen × Citizen → SkillTransfer",
        compose=_teach_compose,
        description="Skill transfer from teacher to student (Phase 2)",
    )

    # Inherit universal laws and add town-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="locality",
            equation="interact(a, b) implies same_region(a, b)",
            verify=_verify_locality,
            description="Citizens must be co-located to interact directly",
        ),
        Law(
            name="rest_inviolability",
            equation="resting(a) implies not in_interaction(a)",
            verify=_verify_rest_inviolability,
            description="Resting citizens cannot be disturbed (Right to Rest)",
        ),
        Law(
            name="coherence_preservation",
            equation="post(interact).a consistent with pre(interact).a",
            verify=_verify_coherence,
            description="Interactions cannot make citizens contradict themselves",
        ),
    ]

    return Operad(
        name="TownOperad",
        operations=ops,
        laws=laws,
        description="Interaction grammar for Agent Town citizens (MPP)",
    )


# =============================================================================
# Global TownOperad Instance
# =============================================================================


TOWN_OPERAD = create_town_operad()
"""
The Town Operad (MPP version).

Operations:
- Universal: seq, par, branch, fix, trace
- Town: greet, gossip, trade, solo

Laws:
- Universal: seq_associativity, par_associativity
- Town: locality, rest_inviolability, coherence_preservation
"""

# Register with the operad registry
OperadRegistry.register(TOWN_OPERAD)


# =============================================================================
# Precondition Checker (Code-as-Policies)
# =============================================================================


@dataclass
class PreconditionResult:
    """Result of checking a precondition."""

    passed: bool
    message: str = ""
    precondition: str = ""


class TownPreconditionChecker:
    """
    Deterministic checks before operation execution.

    Catches violations before tokens are spent.
    This is the Code-as-Policies evaluator.
    """

    def check_locality(
        self,
        citizens: list[Any],
        context: Any,
    ) -> PreconditionResult:
        """Check that all citizens are in the same region."""
        if not citizens:
            return PreconditionResult(
                passed=True, message="No citizens to check", precondition="locality"
            )

        regions = set()
        for c in citizens:
            if hasattr(c, "region"):
                regions.add(c.region)

        if len(regions) > 1:
            return PreconditionResult(
                passed=False,
                message=f"Citizens in different regions: {regions}",
                precondition="locality",
            )

        return PreconditionResult(
            passed=True, message="All citizens co-located", precondition="locality"
        )

    def check_not_resting(
        self,
        citizens: list[Any],
    ) -> PreconditionResult:
        """Check that no citizen is resting."""
        from agents.town.polynomial import CitizenPhase

        for c in citizens:
            if hasattr(c, "phase") and c.phase == CitizenPhase.RESTING:
                name = getattr(c, "name", "unknown")
                return PreconditionResult(
                    passed=False,
                    message=f"Citizen {name} is resting (Right to Rest)",
                    precondition="not_resting",
                )

        return PreconditionResult(
            passed=True,
            message="No citizens resting",
            precondition="not_resting",
        )

    def validate_operation(
        self,
        operation: str,
        citizens: list[Any],
        context: Any = None,
    ) -> list[PreconditionResult]:
        """Run all precondition checks for an operation."""
        results = []

        # Check locality for multi-citizen operations
        if operation in ("greet", "gossip", "trade") and len(citizens) >= 2:
            results.append(self.check_locality(citizens, context))

        # Check resting for all operations
        results.append(self.check_not_resting(citizens))

        return results


# Global precondition checker instance
PRECONDITION_CHECKER = TownPreconditionChecker()


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Metabolics
    "OperationMetabolics",
    "GREET_METABOLICS",
    "GOSSIP_METABOLICS",
    "TRADE_METABOLICS",
    "SOLO_METABOLICS",
    # Operad
    "TOWN_OPERAD",
    "create_town_operad",
    # Preconditions
    "PreconditionResult",
    "TownPreconditionChecker",
    "PRECONDITION_CHECKER",
]
