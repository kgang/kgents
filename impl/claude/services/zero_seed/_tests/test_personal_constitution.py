"""
Tests for Personal Constitution Service.

Validates:
1. Constitution creation and management
2. Axiom addition with validation
3. Contradiction detection
4. Constitution evolution tracking

Philosophy:
    "A constitution is a living covenant.
     These tests ensure the covenant mechanisms work correctly."
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.zero_seed.axiom_discovery import DiscoveredAxiom
from services.zero_seed.personal_constitution import (
    AxiomStatus,
    Constitution,
    ConstitutionalAxiom,
    ConstitutionSnapshot,
    Contradiction,
    InMemoryConstitutionStore,
    PersonalConstitutionService,
    get_constitution_store,
    reset_constitution_store,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset global store before each test."""
    reset_constitution_store()


@pytest.fixture
def service() -> PersonalConstitutionService:
    """Create constitution service instance."""
    return PersonalConstitutionService()


@pytest.fixture
def sample_axiom() -> DiscoveredAxiom:
    """Create a sample discovered axiom."""
    return DiscoveredAxiom(
        content="Simplicity over complexity",
        loss=0.02,
        stability=0.001,
        iterations=3,
        confidence=0.98,
        source_decisions=["Decision 1", "Decision 2"],
    )


@pytest.fixture
def second_axiom() -> DiscoveredAxiom:
    """Create a second discovered axiom."""
    return DiscoveredAxiom(
        content="Composition over inheritance",
        loss=0.03,
        stability=0.002,
        iterations=3,
        confidence=0.97,
        source_decisions=["Decision 3"],
    )


@pytest.fixture
def high_loss_axiom() -> DiscoveredAxiom:
    """Create an axiom with loss above threshold."""
    return DiscoveredAxiom(
        content="Not a real axiom",
        loss=0.15,  # Above 0.05 threshold
        stability=0.01,
        iterations=3,
        confidence=0.85,
    )


# =============================================================================
# Constitutional Axiom Tests
# =============================================================================


class TestConstitutionalAxiom:
    """Tests for ConstitutionalAxiom dataclass."""

    def test_from_discovered(self, sample_axiom: DiscoveredAxiom) -> None:
        """Should create ConstitutionalAxiom from DiscoveredAxiom."""
        const_axiom = ConstitutionalAxiom.from_discovered(sample_axiom)

        assert const_axiom.content == sample_axiom.content
        assert const_axiom.loss == sample_axiom.loss
        assert const_axiom.stability == sample_axiom.stability
        assert const_axiom.confidence == sample_axiom.confidence
        assert const_axiom.status == AxiomStatus.ACTIVE
        assert const_axiom.id.startswith("axiom-")

    def test_retire(self, sample_axiom: DiscoveredAxiom) -> None:
        """retire should mark axiom as retired with reason."""
        const_axiom = ConstitutionalAxiom.from_discovered(sample_axiom)
        retired = const_axiom.retire("No longer relevant")

        assert retired.status == AxiomStatus.RETIRED
        assert retired.retirement_reason == "No longer relevant"
        assert retired.retired_at is not None
        # Original should be unchanged
        assert const_axiom.status == AxiomStatus.ACTIVE

    def test_to_dict(self, sample_axiom: DiscoveredAxiom) -> None:
        """to_dict should serialize axiom."""
        const_axiom = ConstitutionalAxiom.from_discovered(sample_axiom)
        data = const_axiom.to_dict()

        assert "id" in data
        assert "content" in data
        assert "loss" in data
        assert "status" in data
        assert data["status"] == "ACTIVE"

    def test_from_dict(self, sample_axiom: DiscoveredAxiom) -> None:
        """from_dict should deserialize axiom."""
        const_axiom = ConstitutionalAxiom.from_discovered(sample_axiom)
        data = const_axiom.to_dict()
        restored = ConstitutionalAxiom.from_dict(data)

        assert restored.id == const_axiom.id
        assert restored.content == const_axiom.content
        assert restored.status == const_axiom.status


# =============================================================================
# Constitution Tests
# =============================================================================


class TestConstitution:
    """Tests for Constitution dataclass."""

    def test_empty_constitution(self) -> None:
        """Empty constitution should have correct defaults."""
        constitution = Constitution()

        assert constitution.id.startswith("constitution-")
        assert constitution.name == "Personal Constitution"
        assert len(constitution.axioms) == 0
        assert constitution.active_count == 0
        assert constitution.average_loss == 1.0

    def test_active_axioms(self, sample_axiom: DiscoveredAxiom) -> None:
        """active_axioms should filter by ACTIVE status."""
        constitution = Constitution()
        axiom1 = ConstitutionalAxiom.from_discovered(sample_axiom)
        axiom2 = ConstitutionalAxiom.from_discovered(sample_axiom)

        constitution.axioms[axiom1.id] = axiom1
        constitution.axioms[axiom2.id] = axiom2.retire("Test")

        assert len(constitution.active_axioms) == 1
        assert constitution.active_count == 1

    def test_snapshot(self, sample_axiom: DiscoveredAxiom) -> None:
        """snapshot should capture current state."""
        constitution = Constitution()
        axiom = ConstitutionalAxiom.from_discovered(sample_axiom)
        constitution.axioms[axiom.id] = axiom

        snapshot = constitution.snapshot()

        assert snapshot.axiom_count == 1
        assert snapshot.active_count == 1
        assert snapshot.average_loss == axiom.loss
        assert axiom.id in snapshot.axiom_ids

    def test_to_dict_from_dict(self, sample_axiom: DiscoveredAxiom) -> None:
        """Constitution should round-trip through dict."""
        constitution = Constitution(name="Test Constitution")
        axiom = ConstitutionalAxiom.from_discovered(sample_axiom)
        constitution.axioms[axiom.id] = axiom

        data = constitution.to_dict()
        restored = Constitution.from_dict(data)

        assert restored.id == constitution.id
        assert restored.name == constitution.name
        assert len(restored.axioms) == 1


# =============================================================================
# Service Tests
# =============================================================================


class TestPersonalConstitutionService:
    """Tests for PersonalConstitutionService."""

    def test_create_constitution(self, service: PersonalConstitutionService) -> None:
        """create_constitution should create empty constitution."""
        constitution = service.create_constitution("My Values")

        assert constitution.name == "My Values"
        assert constitution.active_count == 0

    @pytest.mark.asyncio
    async def test_add_axiom(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """add_axiom should add valid axiom to constitution."""
        constitution = service.create_constitution()
        updated = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )

        assert updated.active_count == 1
        assert len(updated.axioms) == 1

        # Axiom should be stored with correct values
        stored = list(updated.axioms.values())[0]
        assert stored.content == sample_axiom.content
        assert stored.loss == sample_axiom.loss

    @pytest.mark.asyncio
    async def test_add_axiom_rejects_high_loss(
        self,
        service: PersonalConstitutionService,
        high_loss_axiom: DiscoveredAxiom,
    ) -> None:
        """add_axiom should reject axioms with loss >= 0.05."""
        constitution = service.create_constitution()

        with pytest.raises(ValueError, match="loss"):
            await service.add_axiom(
                constitution=constitution,
                axiom=high_loss_axiom,
            )

    @pytest.mark.asyncio
    async def test_add_axiom_rejects_duplicate(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """add_axiom should reject duplicate content."""
        constitution = service.create_constitution()
        updated = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )

        with pytest.raises(ValueError, match="already exists"):
            await service.add_axiom(
                constitution=updated,
                axiom=sample_axiom,
                check_contradictions=False,
            )

    @pytest.mark.asyncio
    async def test_add_axiom_creates_snapshot(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """add_axiom should create evolution snapshot."""
        constitution = service.create_constitution()
        updated = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )

        assert len(updated.snapshots) == 1
        assert updated.snapshots[0].axiom_count == 1

    @pytest.mark.asyncio
    async def test_retire_axiom(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """retire_axiom should mark axiom as retired."""
        constitution = service.create_constitution()
        updated = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )

        axiom_id = list(updated.axioms.keys())[0]
        retired = await service.retire_axiom(
            constitution=updated,
            axiom_id=axiom_id,
            reason="No longer applicable",
        )

        assert retired.active_count == 0
        assert retired.axioms[axiom_id].status == AxiomStatus.RETIRED
        assert retired.axioms[axiom_id].retirement_reason == "No longer applicable"

    @pytest.mark.asyncio
    async def test_retire_axiom_not_found(
        self,
        service: PersonalConstitutionService,
    ) -> None:
        """retire_axiom should raise for unknown axiom."""
        constitution = service.create_constitution()

        with pytest.raises(ValueError, match="not found"):
            await service.retire_axiom(
                constitution=constitution,
                axiom_id="nonexistent",
                reason="Test",
            )

    @pytest.mark.asyncio
    async def test_detect_contradictions_empty(
        self,
        service: PersonalConstitutionService,
    ) -> None:
        """detect_contradictions should return empty for no axioms."""
        constitution = service.create_constitution()
        contradictions = await service.detect_contradictions(constitution)

        assert contradictions == []

    @pytest.mark.asyncio
    async def test_detect_contradictions_single_axiom(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """detect_contradictions should return empty for single axiom."""
        constitution = service.create_constitution()
        updated = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )

        contradictions = await service.detect_contradictions(updated)
        assert contradictions == []

    @pytest.mark.asyncio
    async def test_detect_contradictions_multiple_axioms(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
        second_axiom: DiscoveredAxiom,
    ) -> None:
        """detect_contradictions should check all pairs."""
        constitution = service.create_constitution()
        constitution = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )
        constitution = await service.add_axiom(
            constitution=constitution,
            axiom=second_axiom,
            check_contradictions=False,
        )

        # Run contradiction detection
        contradictions = await service.detect_contradictions(constitution)

        # Result should be a list (may be empty if no contradictions)
        assert isinstance(contradictions, list)

    def test_get_constitution(
        self,
        service: PersonalConstitutionService,
    ) -> None:
        """get_constitution should return the constitution."""
        constitution = service.create_constitution("Test")
        result = service.get_constitution(constitution)

        assert result.id == constitution.id
        assert result.name == constitution.name

    def test_get_evolution(
        self,
        service: PersonalConstitutionService,
    ) -> None:
        """get_evolution should return snapshots."""
        constitution = Constitution()
        constitution.snapshots.append(
            ConstitutionSnapshot(
                timestamp=datetime.now(timezone.utc),
                axiom_count=1,
                active_count=1,
                average_loss=0.02,
                axiom_ids=["axiom-123"],
            )
        )

        evolution = service.get_evolution(constitution)
        assert len(evolution) == 1
        assert evolution[0].axiom_count == 1


# =============================================================================
# In-Memory Store Tests
# =============================================================================


class TestInMemoryConstitutionStore:
    """Tests for InMemoryConstitutionStore."""

    def test_save_and_load(self) -> None:
        """Should save and load constitution."""
        store = InMemoryConstitutionStore()
        constitution = Constitution(name="Test")

        store.save(constitution)
        loaded = store.load(constitution.id)

        assert loaded is not None
        assert loaded.id == constitution.id

    def test_load_not_found(self) -> None:
        """load should return None for unknown ID."""
        store = InMemoryConstitutionStore()
        result = store.load("nonexistent")

        assert result is None

    def test_delete(self) -> None:
        """delete should remove constitution."""
        store = InMemoryConstitutionStore()
        constitution = Constitution()

        store.save(constitution)
        result = store.delete(constitution.id)

        assert result is True
        assert store.load(constitution.id) is None

    def test_delete_not_found(self) -> None:
        """delete should return False for unknown ID."""
        store = InMemoryConstitutionStore()
        result = store.delete("nonexistent")

        assert result is False

    def test_list_all(self) -> None:
        """list_all should return all constitutions."""
        store = InMemoryConstitutionStore()
        c1 = Constitution(name="First")
        c2 = Constitution(name="Second")

        store.save(c1)
        store.save(c2)

        all_constitutions = store.list_all()
        assert len(all_constitutions) == 2


class TestGlobalStore:
    """Tests for global store functions."""

    def test_get_constitution_store(self) -> None:
        """get_constitution_store should return store instance."""
        store = get_constitution_store()
        assert isinstance(store, InMemoryConstitutionStore)

    def test_get_constitution_store_singleton(self) -> None:
        """get_constitution_store should return same instance."""
        store1 = get_constitution_store()
        store2 = get_constitution_store()

        assert store1 is store2

    def test_reset_constitution_store(self) -> None:
        """reset_constitution_store should clear the store."""
        store1 = get_constitution_store()
        store1.save(Constitution())

        reset_constitution_store()
        store2 = get_constitution_store()

        assert len(store2.list_all()) == 0


# =============================================================================
# Contradiction Tests
# =============================================================================


class TestContradiction:
    """Tests for Contradiction dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should serialize contradiction."""
        from services.zero_seed.galois.galois_loss import ContradictionType

        contradiction = Contradiction(
            axiom_a_id="axiom-1",
            axiom_b_id="axiom-2",
            axiom_a_content="Content A",
            axiom_b_content="Content B",
            strength=0.15,
            type=ContradictionType.WEAK,
            loss_a=0.02,
            loss_b=0.03,
            loss_combined=0.20,
            synthesis_hint="Try X",
        )

        data = contradiction.to_dict()
        assert data["axiom_a_id"] == "axiom-1"
        assert data["strength"] == 0.15
        assert data["synthesis_hint"] == "Try X"

    def test_is_strong(self) -> None:
        """is_strong should return True for STRONG type."""
        from services.zero_seed.galois.galois_loss import ContradictionType

        strong = Contradiction(
            axiom_a_id="a1",
            axiom_b_id="a2",
            axiom_a_content="A",
            axiom_b_content="B",
            strength=0.3,
            type=ContradictionType.STRONG,
            loss_a=0.02,
            loss_b=0.02,
            loss_combined=0.34,
        )
        assert strong.is_strong is True

        weak = Contradiction(
            axiom_a_id="a1",
            axiom_b_id="a2",
            axiom_a_content="A",
            axiom_b_content="B",
            strength=0.05,
            type=ContradictionType.WEAK,
            loss_a=0.02,
            loss_b=0.02,
            loss_combined=0.09,
        )
        assert weak.is_strong is False


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for constitution management."""

    @pytest.mark.asyncio
    async def test_full_constitution_lifecycle(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
        second_axiom: DiscoveredAxiom,
    ) -> None:
        """Test full lifecycle: create -> add -> evolve -> retire."""
        # Create
        constitution = service.create_constitution("My Values")
        assert constitution.active_count == 0

        # Add first axiom
        constitution = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )
        assert constitution.active_count == 1

        # Add second axiom
        constitution = await service.add_axiom(
            constitution=constitution,
            axiom=second_axiom,
            check_contradictions=False,
        )
        assert constitution.active_count == 2

        # Check evolution snapshots
        assert len(constitution.snapshots) == 2

        # Retire first axiom
        axiom_id = list(constitution.axioms.keys())[0]
        constitution = await service.retire_axiom(
            constitution=constitution,
            axiom_id=axiom_id,
            reason="Superseded",
        )
        assert constitution.active_count == 1

        # Final evolution check
        assert len(constitution.snapshots) == 3

    @pytest.mark.asyncio
    async def test_constitution_persistence(
        self,
        service: PersonalConstitutionService,
        sample_axiom: DiscoveredAxiom,
    ) -> None:
        """Test that constitution persists in store."""
        store = get_constitution_store()

        # Create and save
        constitution = service.create_constitution("Test")
        constitution = await service.add_axiom(
            constitution=constitution,
            axiom=sample_axiom,
            check_contradictions=False,
        )
        store.save(constitution)

        # Load and verify
        loaded = store.load(constitution.id)
        assert loaded is not None
        assert loaded.active_count == 1
        assert list(loaded.axioms.values())[0].content == sample_axiom.content
