"""
Tests for Umwelt: Agent-Specific World Projection.

Tests the Umwelt Protocol from spec/protocols/umwelt.md:
- Umwelt type (State + DNA + Gravity)
- Projector (creates Umwelts from root D-gent)
- Lens-based state access
- Hypothetical/temporal projection
"""

import pytest
from dataclasses import dataclass
from typing import Any

from agents.d.lens import key_lens, identity_lens
from agents.d.volatile import VolatileAgent
from bootstrap.dna import BaseDNA, DNAValidationError
from bootstrap.umwelt import (
    Umwelt,
    LightweightUmwelt,
    Projector,
    HypotheticalProjector,
)


# ============================================================================
# Mock Contracts
# ============================================================================


class MockContract:
    """Mock contract for testing."""

    def __init__(self, name: str = "MockContract", passes: bool = True):
        self._name = name
        self._passes = passes

    @property
    def name(self) -> str:
        return self._name

    def check(self, output: Any) -> str | None:
        if self._passes:
            return None
        return f"MockContract '{self._name}' violation"

    def admits(self, intent: str) -> bool:
        return self._passes


class NoNumbersContract:
    """Contract that rejects outputs containing numbers."""

    @property
    def name(self) -> str:
        return "NoNumbers"

    def check(self, output: Any) -> str | None:
        output_str = str(output)
        if any(char.isdigit() for char in output_str):
            return "Output contains numbers"
        return None

    def admits(self, intent: str) -> bool:
        return not any(char.isdigit() for char in intent)


# ============================================================================
# Test DNA for Umwelt Tests
# ============================================================================


@dataclass(frozen=True)
class TestDNA(BaseDNA):
    """Simple DNA for testing."""

    name: str = "test"
    level: int = 1


# ============================================================================
# Umwelt Tests
# ============================================================================


class TestUmwelt:
    """Test Umwelt type."""

    def test_umwelt_creation(self):
        """Umwelt can be created with state, dna, gravity."""
        lens = key_lens("test")
        dna = TestDNA.germinate(name="test_agent")
        contract = MockContract()

        umwelt = Umwelt(
            state=lens,
            dna=dna,
            gravity=(contract,),
        )

        assert umwelt.dna.name == "test_agent"
        assert len(umwelt.gravity) == 1

    def test_umwelt_is_grounded_passes(self):
        """is_grounded returns True when all contracts pass."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(MockContract(passes=True),),
        )

        assert umwelt.is_grounded("any output") is True

    def test_umwelt_is_grounded_fails(self):
        """is_grounded returns False when any contract fails."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(
                MockContract(passes=True),
                MockContract(name="Failing", passes=False),
            ),
        )

        assert umwelt.is_grounded("any output") is False

    def test_umwelt_check_grounding_returns_violations(self):
        """check_grounding returns list of violations."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(
                MockContract(name="Pass", passes=True),
                MockContract(name="Fail1", passes=False),
                MockContract(name="Fail2", passes=False),
            ),
        )

        violations = umwelt.check_grounding("output")
        assert len(violations) == 2
        assert any("Fail1" in v for v in violations)
        assert any("Fail2" in v for v in violations)

    def test_umwelt_with_no_numbers_contract(self):
        """NoNumbers contract rejects numeric output."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(NoNumbersContract(),),
        )

        assert umwelt.is_grounded("hello world") is True
        assert umwelt.is_grounded("hello 123") is False

    @pytest.mark.asyncio
    async def test_umwelt_get_without_storage_raises(self):
        """get() raises if storage not connected."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(),
        )

        with pytest.raises(RuntimeError, match="not connected"):
            await umwelt.get()

    @pytest.mark.asyncio
    async def test_umwelt_set_without_storage_raises(self):
        """set() raises if storage not connected."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(),
        )

        with pytest.raises(RuntimeError, match="not connected"):
            await umwelt.set({"test": "value"})


# ============================================================================
# LightweightUmwelt Tests
# ============================================================================


class TestLightweightUmwelt:
    """Test LightweightUmwelt for direct storage access."""

    @pytest.mark.asyncio
    async def test_lightweight_get(self):
        """LightweightUmwelt.get() returns storage state."""
        storage = VolatileAgent(_state={"key": "value"})
        umwelt = LightweightUmwelt(
            storage=storage,
            dna=TestDNA.germinate(),
            gravity=(),
        )

        state = await umwelt.get()
        assert state == {"key": "value"}

    @pytest.mark.asyncio
    async def test_lightweight_set(self):
        """LightweightUmwelt.set() updates storage."""
        storage = VolatileAgent(_state={})
        umwelt = LightweightUmwelt(
            storage=storage,
            dna=TestDNA.germinate(),
            gravity=(),
        )

        await umwelt.set({"new": "state"})
        state = await umwelt.get()
        assert state == {"new": "state"}

    def test_lightweight_is_grounded(self):
        """LightweightUmwelt.is_grounded() checks contracts."""
        storage = VolatileAgent(_state={})
        umwelt = LightweightUmwelt(
            storage=storage,
            dna=TestDNA.germinate(),
            gravity=(NoNumbersContract(),),
        )

        assert umwelt.is_grounded("text only") is True
        assert umwelt.is_grounded("has 123") is False


# ============================================================================
# Projector Tests
# ============================================================================


class TestProjector:
    """Test Projector for creating Umwelts."""

    @pytest.mark.asyncio
    async def test_projector_basic(self):
        """Projector creates Umwelt with lens and DNA."""
        root = VolatileAgent(
            _state={
                "agents": {
                    "k": {"persona": "curious"},
                },
            }
        )
        projector = Projector(root)

        umwelt = projector.project(
            agent_id="k",
            dna=TestDNA.germinate(name="k_agent"),
        )

        assert umwelt.dna.name == "k_agent"
        state = await umwelt.get()
        assert state == {"persona": "curious"}

    @pytest.mark.asyncio
    async def test_projector_custom_path(self):
        """Projector accepts custom lens path."""
        root = VolatileAgent(
            _state={
                "custom": {
                    "location": {
                        "data": "test_data",
                    },
                },
            }
        )
        projector = Projector(root)

        umwelt = projector.project(
            agent_id="test",
            dna=TestDNA.germinate(),
            path="custom.location",
        )

        state = await umwelt.get()
        assert state == {"data": "test_data"}

    @pytest.mark.asyncio
    async def test_projector_with_gravity(self):
        """Projector attaches gravity contracts."""
        root = VolatileAgent(_state={"agents": {"test": {}}})
        projector = Projector(root)

        contract = NoNumbersContract()
        umwelt = projector.project(
            agent_id="test",
            dna=TestDNA.germinate(),
            gravity=[contract],
        )

        assert len(umwelt.gravity) == 1
        assert umwelt.gravity[0].name == "NoNumbers"

    @pytest.mark.asyncio
    async def test_projector_register_gravity(self):
        """Projector can register default gravity for agent types."""
        root = VolatileAgent(_state={"agents": {}})
        projector = Projector(root)

        # Register default gravity for agent "k"
        projector.register_gravity("k", [MockContract(name="KDefault")])

        umwelt = projector.project(
            agent_id="k",
            dna=TestDNA.germinate(),
        )

        assert len(umwelt.gravity) == 1
        assert umwelt.gravity[0].name == "KDefault"

    def test_projector_validates_dna(self):
        """Projector validates DNA constraints."""
        root = VolatileAgent(_state={})
        projector = Projector(root)

        # Create invalid DNA (exploration_budget=0 violates positive_exploration)
        @dataclass(frozen=True)
        class InvalidDNA(BaseDNA):
            exploration_budget: float = 0  # Invalid!

        # Manual construction bypasses germinate validation
        invalid_dna = InvalidDNA()

        with pytest.raises(DNAValidationError):
            projector.project(agent_id="test", dna=invalid_dna)

    @pytest.mark.asyncio
    async def test_projector_state_write_through_lens(self):
        """Umwelt state writes propagate through lens."""
        root = VolatileAgent(
            _state={
                "agents": {
                    "k": {"value": "original"},
                },
            }
        )
        projector = Projector(root)

        umwelt = projector.project(
            agent_id="k",
            dna=TestDNA.germinate(),
        )

        # Write through umwelt
        await umwelt.set({"value": "updated"})

        # Verify root was updated
        root_state = await root.load()
        assert root_state["agents"]["k"]["value"] == "updated"

    @pytest.mark.asyncio
    async def test_projector_isolation(self):
        """Different agents have isolated views."""
        root = VolatileAgent(
            _state={
                "agents": {
                    "agent_a": {"data": "A"},
                    "agent_b": {"data": "B"},
                },
            }
        )
        projector = Projector(root)

        umwelt_a = projector.project(agent_id="agent_a", dna=TestDNA.germinate())
        umwelt_b = projector.project(agent_id="agent_b", dna=TestDNA.germinate())

        state_a = await umwelt_a.get()
        state_b = await umwelt_b.get()

        assert state_a == {"data": "A"}
        assert state_b == {"data": "B"}

        # Modifying A doesn't affect B
        await umwelt_a.set({"data": "A_modified"})
        state_b_after = await umwelt_b.get()
        assert state_b_after == {"data": "B"}


# ============================================================================
# LightweightProjector Tests
# ============================================================================


class TestProjectorLightweight:
    """Test Projector.project_lightweight()."""

    @pytest.mark.asyncio
    async def test_project_lightweight(self):
        """project_lightweight creates LightweightUmwelt."""
        root = VolatileAgent(_state={})
        projector = Projector(root)

        agent_storage = VolatileAgent(_state={"direct": "access"})

        umwelt = projector.project_lightweight(
            agent_id="test",
            dna=TestDNA.germinate(),
            storage=agent_storage,
        )

        assert isinstance(umwelt, LightweightUmwelt)
        state = await umwelt.get()
        assert state == {"direct": "access"}


# ============================================================================
# HypotheticalProjector Tests
# ============================================================================


class TestHypotheticalProjector:
    """Test HypotheticalProjector for counter-factual worlds."""

    @pytest.mark.asyncio
    async def test_hypothetical_from_snapshot(self):
        """HypotheticalProjector clones real world state."""
        real_root = VolatileAgent(
            _state={
                "agents": {
                    "b": {"hypothesis": "original"},
                },
            }
        )
        real_projector = Projector(real_root)

        # Create hypothetical world
        hypothetical = await HypotheticalProjector.from_snapshot(real_projector)

        assert hypothetical.is_hypothetical is True

        # Project in hypothetical
        umwelt = hypothetical.project(
            agent_id="b",
            dna=TestDNA.germinate(),
        )

        state = await umwelt.get()
        assert state == {"hypothesis": "original"}

    @pytest.mark.asyncio
    async def test_hypothetical_isolated_from_real(self):
        """Hypothetical modifications don't affect real world."""
        real_root = VolatileAgent(
            _state={
                "agents": {
                    "b": {"value": "real"},
                },
            }
        )
        real_projector = Projector(real_root)

        # Create hypothetical
        hypothetical = await HypotheticalProjector.from_snapshot(real_projector)
        hypo_umwelt = hypothetical.project(agent_id="b", dna=TestDNA.germinate())

        # Modify hypothetical
        await hypo_umwelt.set({"value": "hypothetical"})

        # Real world unchanged
        real_state = await real_root.load()
        assert real_state["agents"]["b"]["value"] == "real"

    @pytest.mark.asyncio
    async def test_multiple_hypothetical_worlds(self):
        """Can create multiple independent hypothetical worlds."""
        real_root = VolatileAgent(
            _state={
                "agents": {
                    "b": {"base": "state"},
                },
            }
        )
        real_projector = Projector(real_root)

        # Create two hypothetical worlds
        hypo_a = await HypotheticalProjector.from_snapshot(real_projector)
        hypo_b = await HypotheticalProjector.from_snapshot(real_projector)

        umwelt_a = hypo_a.project(agent_id="b", dna=TestDNA.germinate())
        umwelt_b = hypo_b.project(agent_id="b", dna=TestDNA.germinate())

        # Modify each differently
        await umwelt_a.set({"variant": "A"})
        await umwelt_b.set({"variant": "B"})

        # Each is independent
        state_a = await umwelt_a.get()
        state_b = await umwelt_b.get()

        assert state_a == {"variant": "A"}
        assert state_b == {"variant": "B"}


# ============================================================================
# Lens Composition Tests
# ============================================================================


class TestLensComposition:
    """Test that Projector correctly composes lenses."""

    @pytest.mark.asyncio
    async def test_deep_lens_path(self):
        """Projector handles deep lens paths."""
        root = VolatileAgent(
            _state={
                "level1": {
                    "level2": {
                        "level3": {
                            "deep_value": 42,
                        },
                    },
                },
            }
        )
        projector = Projector(root)

        umwelt = projector.project(
            agent_id="deep",
            dna=TestDNA.germinate(),
            path="level1.level2.level3",
        )

        state = await umwelt.get()
        assert state == {"deep_value": 42}

    @pytest.mark.asyncio
    async def test_lens_write_deep(self):
        """Deep lens writes propagate correctly."""
        root = VolatileAgent(
            _state={
                "a": {
                    "b": {
                        "c": {"old": "value"},
                    },
                },
            }
        )
        projector = Projector(root)

        umwelt = projector.project(
            agent_id="test",
            dna=TestDNA.germinate(),
            path="a.b.c",
        )

        await umwelt.set({"new": "value"})

        root_state = await root.load()
        assert root_state["a"]["b"]["c"] == {"new": "value"}


# ============================================================================
# Contract Integration Tests
# ============================================================================


class TestContractIntegration:
    """Test contracts work correctly with Umwelt."""

    def test_multiple_contracts_all_pass(self):
        """Multiple passing contracts → grounded."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(
                MockContract(name="A", passes=True),
                MockContract(name="B", passes=True),
                MockContract(name="C", passes=True),
            ),
        )

        assert umwelt.is_grounded("output") is True
        assert umwelt.check_grounding("output") == []

    def test_one_contract_fails(self):
        """One failing contract → not grounded."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(
                MockContract(name="A", passes=True),
                MockContract(name="B", passes=False),
                MockContract(name="C", passes=True),
            ),
        )

        assert umwelt.is_grounded("output") is False
        violations = umwelt.check_grounding("output")
        assert len(violations) == 1
        assert "B" in violations[0]

    def test_empty_gravity_always_grounded(self):
        """No contracts → always grounded."""
        umwelt = Umwelt(
            state=identity_lens(),
            dna=TestDNA.germinate(),
            gravity=(),
        )

        assert umwelt.is_grounded("anything") is True
        assert umwelt.is_grounded(None) is True
        assert umwelt.is_grounded({"complex": [1, 2, 3]}) is True
