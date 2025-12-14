"""
Tests for TownOperad.

Verifies:
- Operations exist and have correct arity
- Laws are defined
- Precondition checker works
- Composition produces valid agents
"""

from __future__ import annotations

from typing import Any

import pytest
from agents.poly import PolyAgent, from_function
from agents.town.operad import (
    CELEBRATE_METABOLICS,
    DISPUTE_METABOLICS,
    GOSSIP_METABOLICS,
    GREET_METABOLICS,
    MOURN_METABOLICS,
    PRECONDITION_CHECKER,
    SOLO_METABOLICS,
    TEACH_METABOLICS,
    TOWN_OPERAD,
    TRADE_METABOLICS,
    OperationMetabolics,
    PreconditionResult,
    create_town_operad,
)


class TestOperationMetabolics:
    """Test metabolic costs."""

    def test_greet_metabolics(self) -> None:
        """Greet has correct metabolics."""
        assert GREET_METABOLICS.token_cost == 200
        assert GREET_METABOLICS.drama_potential == 0.1

    def test_gossip_metabolics(self) -> None:
        """Gossip has higher drama potential."""
        assert GOSSIP_METABOLICS.token_cost == 500
        assert GOSSIP_METABOLICS.drama_potential == 0.4
        assert GOSSIP_METABOLICS.drama_potential > GREET_METABOLICS.drama_potential

    def test_trade_metabolics(self) -> None:
        """Trade has moderate metabolics."""
        assert TRADE_METABOLICS.token_cost == 400
        assert TRADE_METABOLICS.drama_potential == 0.3

    def test_solo_metabolics(self) -> None:
        """Solo has low drama."""
        assert SOLO_METABOLICS.token_cost == 300
        assert SOLO_METABOLICS.drama_potential == 0.1

    def test_estimate_tokens(self) -> None:
        """Token estimation works."""
        m = OperationMetabolics(token_cost=100, drama_potential=0.5)
        assert m.estimate_tokens() == 100

    def test_estimate_tokens_scaling(self) -> None:
        """Scaling works for variable arity."""
        m = OperationMetabolics(
            token_cost=100, drama_potential=0.5, scales_with_arity=True
        )
        assert m.estimate_tokens(1) == 100
        assert m.estimate_tokens(3) == 300


class TestTownOperad:
    """Test TownOperad structure."""

    def test_operad_exists(self) -> None:
        """TOWN_OPERAD is defined."""
        assert TOWN_OPERAD is not None
        assert TOWN_OPERAD.name == "TownOperad"

    def test_has_universal_operations(self) -> None:
        """Has universal operations from AGENT_OPERAD."""
        assert "seq" in TOWN_OPERAD.operations
        assert "par" in TOWN_OPERAD.operations
        assert "branch" in TOWN_OPERAD.operations
        assert "fix" in TOWN_OPERAD.operations
        assert "trace" in TOWN_OPERAD.operations

    def test_has_town_operations(self) -> None:
        """Has town-specific operations."""
        assert "greet" in TOWN_OPERAD.operations
        assert "gossip" in TOWN_OPERAD.operations
        assert "trade" in TOWN_OPERAD.operations
        assert "solo" in TOWN_OPERAD.operations

    def test_greet_arity(self) -> None:
        """Greet has arity 2."""
        assert TOWN_OPERAD.operations["greet"].arity == 2

    def test_gossip_arity(self) -> None:
        """Gossip has arity 2."""
        assert TOWN_OPERAD.operations["gossip"].arity == 2

    def test_trade_arity(self) -> None:
        """Trade has arity 2."""
        assert TOWN_OPERAD.operations["trade"].arity == 2

    def test_solo_arity(self) -> None:
        """Solo has arity 1."""
        assert TOWN_OPERAD.operations["solo"].arity == 1


class TestTownLaws:
    """Test TownOperad laws."""

    def test_has_universal_laws(self) -> None:
        """Has universal laws from AGENT_OPERAD."""
        law_names = [law.name for law in TOWN_OPERAD.laws]
        assert "seq_associativity" in law_names
        assert "par_associativity" in law_names

    def test_has_town_laws(self) -> None:
        """Has town-specific laws."""
        law_names = [law.name for law in TOWN_OPERAD.laws]
        assert "locality" in law_names
        assert "rest_inviolability" in law_names
        assert "coherence_preservation" in law_names

    def test_locality_law_verify(self) -> None:
        """Locality law verification works."""
        a: PolyAgent[Any, Any, Any] = from_function("A", lambda x: x)
        b: PolyAgent[Any, Any, Any] = from_function("B", lambda x: x)

        result = TOWN_OPERAD.verify_law("locality", a, b)
        assert result.passed

    def test_rest_inviolability_verify(self) -> None:
        """Rest inviolability verification works."""
        a: PolyAgent[Any, Any, Any] = from_function("A", lambda x: x)

        result = TOWN_OPERAD.verify_law("rest_inviolability", a)
        assert result.passed


class TestOperationComposition:
    """Test operation composition."""

    def test_greet_composition(self) -> None:
        """Greet composes two citizens."""
        citizen_a: PolyAgent[Any, Any, Any] = from_function(
            "Alice", lambda x: {"name": "Alice", "input": x}
        )
        citizen_b: PolyAgent[Any, Any, Any] = from_function(
            "Bob", lambda x: {"name": "Bob", "input": x}
        )

        composed = TOWN_OPERAD.compose("greet", citizen_a, citizen_b)

        assert composed is not None
        assert "greet" in composed.name.lower()

    def test_gossip_composition(self) -> None:
        """Gossip composes two citizens."""
        citizen_a: PolyAgent[Any, Any, Any] = from_function("Alice", lambda x: x)
        citizen_b: PolyAgent[Any, Any, Any] = from_function("Bob", lambda x: x)

        composed = TOWN_OPERAD.compose("gossip", citizen_a, citizen_b)

        assert composed is not None
        assert "gossip" in composed.name.lower()

    def test_solo_composition(self) -> None:
        """Solo composes one citizen."""
        citizen: PolyAgent[Any, Any, Any] = from_function("Alice", lambda x: x)

        composed = TOWN_OPERAD.compose("solo", citizen)

        assert composed is not None
        assert "solo" in composed.name.lower()

    def test_wrong_arity_raises(self) -> None:
        """Wrong arity raises ValueError."""
        citizen: PolyAgent[Any, Any, Any] = from_function("Alice", lambda x: x)

        with pytest.raises(ValueError):
            TOWN_OPERAD.compose("greet", citizen)  # Needs 2, got 1


class TestPreconditionChecker:
    """Test precondition checking."""

    def test_locality_check_same_region(self) -> None:
        """Locality passes for same region."""
        from agents.town.citizen import Citizen

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="inn")

        result = PRECONDITION_CHECKER.check_locality([alice, bob], None)

        assert result.passed

    def test_locality_check_different_regions(self) -> None:
        """Locality fails for different regions."""
        from agents.town.citizen import Citizen

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="square")

        result = PRECONDITION_CHECKER.check_locality([alice, bob], None)

        assert not result.passed

    def test_not_resting_check_pass(self) -> None:
        """Not resting passes for awake citizens."""
        from agents.town.citizen import Citizen

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")

        result = PRECONDITION_CHECKER.check_not_resting([alice])

        assert result.passed

    def test_not_resting_check_fail(self) -> None:
        """Not resting fails for resting citizen."""
        from agents.town.citizen import Citizen

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        alice.rest()  # Put to rest

        result = PRECONDITION_CHECKER.check_not_resting([alice])

        assert not result.passed

    def test_validate_operation_greet(self) -> None:
        """Full validation for greet operation."""
        from agents.town.citizen import Citizen

        alice = Citizen(name="Alice", archetype="Innkeeper", region="inn")
        bob = Citizen(name="Bob", archetype="Builder", region="inn")

        results = PRECONDITION_CHECKER.validate_operation("greet", [alice, bob], None)

        assert all(r.passed for r in results)


class TestCreateTownOperad:
    """Test operad creation function."""

    def test_create_fresh_operad(self) -> None:
        """Can create fresh operad."""
        operad = create_town_operad()

        assert operad is not None
        assert operad.name == "TownOperad"
        assert "greet" in operad.operations


class TestPhase2Operations:
    """Test Phase 2 operations."""

    def test_has_phase2_operations(self) -> None:
        """TOWN_OPERAD has Phase 2 operations."""
        assert "dispute" in TOWN_OPERAD.operations
        assert "celebrate" in TOWN_OPERAD.operations
        assert "mourn" in TOWN_OPERAD.operations
        assert "teach" in TOWN_OPERAD.operations

    def test_dispute_arity(self) -> None:
        """Dispute has arity 2."""
        assert TOWN_OPERAD.operations["dispute"].arity == 2

    def test_celebrate_variable_arity(self) -> None:
        """Celebrate has variable arity (-1)."""
        assert TOWN_OPERAD.operations["celebrate"].arity == -1

    def test_mourn_variable_arity(self) -> None:
        """Mourn has variable arity (-1)."""
        assert TOWN_OPERAD.operations["mourn"].arity == -1

    def test_teach_arity(self) -> None:
        """Teach has arity 2."""
        assert TOWN_OPERAD.operations["teach"].arity == 2

    def test_dispute_metabolics(self) -> None:
        """Dispute has high drama potential."""
        assert DISPUTE_METABOLICS.token_cost == 600
        assert DISPUTE_METABOLICS.drama_potential == 0.8
        assert DISPUTE_METABOLICS.drama_potential > GOSSIP_METABOLICS.drama_potential

    def test_celebrate_metabolics_scaling(self) -> None:
        """Celebrate scales with arity."""
        assert CELEBRATE_METABOLICS.scales_with_arity is True
        assert CELEBRATE_METABOLICS.estimate_tokens(3) == 3 * CELEBRATE_METABOLICS.token_cost

    def test_mourn_metabolics_scaling(self) -> None:
        """Mourn scales with arity."""
        assert MOURN_METABOLICS.scales_with_arity is True
        assert MOURN_METABOLICS.estimate_tokens(5) == 5 * MOURN_METABOLICS.token_cost

    def test_teach_metabolics(self) -> None:
        """Teach has high token cost."""
        assert TEACH_METABOLICS.token_cost == 800
        assert TEACH_METABOLICS.drama_potential == 0.2

    def test_dispute_composition(self) -> None:
        """Dispute composes two citizens."""
        citizen_a: PolyAgent[Any, Any, Any] = from_function("Alice", lambda x: x)
        citizen_b: PolyAgent[Any, Any, Any] = from_function("Bob", lambda x: x)

        composed = TOWN_OPERAD.compose("dispute", citizen_a, citizen_b)

        assert composed is not None
        assert "dispute" in composed.name.lower()

    def test_teach_composition(self) -> None:
        """Teach composes teacher and student."""
        teacher: PolyAgent[Any, Any, Any] = from_function("Eve", lambda x: x)
        student: PolyAgent[Any, Any, Any] = from_function("Diana", lambda x: x)

        composed = TOWN_OPERAD.compose("teach", teacher, student)

        assert composed is not None
        assert "teach" in composed.name.lower()
