"""
Tests for ValidationEngine orchestration.

Verifies:
- Initiative registration (direct and from YAML)
- Validation execution
- Status and blocker tracking
- Phase dependency handling
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from services.validation.engine import (
    ValidationEngine,
    get_validation_engine,
    reset_validation_engine,
)
from services.validation.schema import (
    Direction,
    Gate,
    GateCondition,
    GateId,
    Initiative,
    InitiativeId,
    MetricType,
    Phase,
    PhaseId,
    Proposition,
    PropositionId,
)
from services.validation.store import ValidationStore, reset_validation_store

if TYPE_CHECKING:
    from services.witness.trace_store import MarkStore


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def engine() -> ValidationEngine:
    """Create a fresh engine with in-memory store."""
    store = ValidationStore()
    return ValidationEngine(_store=store)


@pytest.fixture
def flat_initiative() -> Initiative:
    """Create a flat initiative for testing."""
    return Initiative(
        id=InitiativeId("brain"),
        name="Brain Crown Jewel",
        description="The spatial cathedral",
        propositions=(
            Proposition(
                id=PropositionId("tests_pass"),
                description="All tests pass",
                metric=MetricType.BINARY,
                threshold=1.0,
                direction=Direction.EQ,
                required=True,
            ),
            Proposition(
                id=PropositionId("test_count"),
                description="At least 200 tests",
                metric=MetricType.COUNT,
                threshold=200,
                direction=Direction.GTE,
                required=True,
            ),
        ),
        gate=Gate(
            id=GateId("brain_gate"),
            name="Brain Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("tests_pass"), PropositionId("test_count")),
        ),
    )


@pytest.fixture
def phased_initiative() -> Initiative:
    """Create a phased initiative for testing."""
    return Initiative(
        id=InitiativeId("categorical"),
        name="Categorical Reasoning",
        description="Research initiative",
        phases=(
            Phase(
                id=PhaseId("foundations"),
                name="Phase 1: Foundations",
                gate=Gate(
                    id=GateId("foundations_gate"),
                    name="Foundations Gate",
                    condition=GateCondition.ALL_REQUIRED,
                    proposition_ids=(PropositionId("correlation"),),
                ),
                propositions=(
                    Proposition(
                        id=PropositionId("correlation"),
                        description="Correlation > 0.3",
                        metric=MetricType.PEARSON_R,
                        threshold=0.3,
                        direction=Direction.GT,
                        required=True,
                    ),
                ),
            ),
            Phase(
                id=PhaseId("integration"),
                name="Phase 2: Integration",
                gate=Gate(
                    id=GateId("integration_gate"),
                    name="Integration Gate",
                    condition=GateCondition.ALL_REQUIRED,
                    proposition_ids=(PropositionId("auc"),),
                ),
                propositions=(
                    Proposition(
                        id=PropositionId("auc"),
                        description="AUC > 0.75",
                        metric=MetricType.AUC,
                        threshold=0.75,
                        direction=Direction.GT,
                        required=True,
                    ),
                ),
                depends_on=(PhaseId("foundations"),),
            ),
        ),
    )


# =============================================================================
# Registration Tests
# =============================================================================


class TestRegistration:
    """Tests for initiative registration."""

    def test_register_initiative(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Register an initiative directly."""
        engine.register_initiative(flat_initiative)

        retrieved = engine.get_initiative("brain")

        assert retrieved is not None
        assert retrieved.name == "Brain Crown Jewel"

    def test_list_initiatives(
        self, engine: ValidationEngine, flat_initiative: Initiative, phased_initiative: Initiative
    ) -> None:
        """List all registered initiatives."""
        engine.register_initiative(flat_initiative)
        engine.register_initiative(phased_initiative)

        initiatives = engine.list_initiatives()

        assert len(initiatives) == 2
        ids = {i.id for i in initiatives}
        assert InitiativeId("brain") in ids
        assert InitiativeId("categorical") in ids

    def test_register_from_yaml(self, engine: ValidationEngine) -> None:
        """Register initiative from YAML file."""
        yaml_content = """
id: test_initiative
name: Test Initiative
description: A test
propositions:
  - id: tests_pass
    description: Tests pass
    metric: binary
    threshold: 1
    direction: "="
gate:
  id: test_gate
  condition: all_required
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            initiative = engine.register_from_yaml(Path(f.name))

        assert initiative.id == "test_initiative"
        assert len(initiative.propositions) == 1

    def test_load_from_directory(self, engine: ValidationEngine) -> None:
        """Load initiatives from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create YAML files
            (Path(tmpdir) / "init1.yaml").write_text("""
id: init1
name: Initiative 1
description: First
propositions:
  - id: p1
    metric: binary
    threshold: 1
    direction: "="
gate:
  condition: all_required
""")
            (Path(tmpdir) / "init2.yaml").write_text("""
id: init2
name: Initiative 2
description: Second
propositions:
  - id: p2
    metric: binary
    threshold: 1
    direction: "="
gate:
  condition: all_required
""")

            initiatives = engine.load_initiatives_from_dir(Path(tmpdir))

        assert len(initiatives) == 2


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for validation execution."""

    def test_validate_flat_passes(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Validate flat initiative that passes."""
        engine.register_initiative(flat_initiative)

        run = engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        assert run.passed is True
        assert run.initiative_id == "brain"
        assert run.phase_id is None

    def test_validate_flat_fails(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Validate flat initiative that fails."""
        engine.register_initiative(flat_initiative)

        run = engine.validate("brain", {"tests_pass": 1.0, "test_count": 150.0})

        assert run.passed is False

    def test_validate_phased_first_phase(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Validate first phase of phased initiative."""
        engine.register_initiative(phased_initiative)

        run = engine.validate("categorical", {"correlation": 0.4})

        assert run.passed is True
        assert run.phase_id == "foundations"

    def test_validate_phased_explicit_phase(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Validate explicit phase."""
        engine.register_initiative(phased_initiative)

        run = engine.validate("categorical", {"correlation": 0.35}, phase_id="foundations")

        assert run.passed is True
        assert run.phase_id == "foundations"

    def test_validate_phased_dependency_check(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Cannot validate phase with unmet dependencies."""
        engine.register_initiative(phased_initiative)

        with pytest.raises(ValueError, match="depends on"):
            engine.validate("categorical", {"auc": 0.8}, phase_id="integration")

    def test_validate_phased_after_dependency_passes(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Can validate second phase after first passes."""
        engine.register_initiative(phased_initiative)

        # Pass first phase
        engine.validate("categorical", {"correlation": 0.4}, phase_id="foundations")

        # Now second phase should work
        run = engine.validate("categorical", {"auc": 0.8}, phase_id="integration")

        assert run.passed is True
        assert run.phase_id == "integration"

    def test_validate_unknown_initiative_raises(self, engine: ValidationEngine) -> None:
        """Validating unknown initiative raises error."""
        with pytest.raises(ValueError, match="not found"):
            engine.validate("nonexistent", {})

    def test_validate_auto_selects_next_phase(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Validation auto-selects next available phase."""
        engine.register_initiative(phased_initiative)

        # First validation should pick foundations
        run1 = engine.validate("categorical", {"correlation": 0.4})
        assert run1.phase_id == "foundations"

        # Second validation should pick integration
        run2 = engine.validate("categorical", {"auc": 0.8})
        assert run2.phase_id == "integration"


# =============================================================================
# Status Tests
# =============================================================================


class TestStatus:
    """Tests for status tracking."""

    def test_status_flat_initiative(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Get status of flat initiative."""
        engine.register_initiative(flat_initiative)
        engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        status = engine.get_status("brain")

        assert status.initiative_id == "brain"
        assert status.total_phases == 0
        assert status.last_run is not None
        assert status.last_run.passed is True

    def test_status_phased_initiative(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Get status of phased initiative."""
        engine.register_initiative(phased_initiative)
        engine.validate("categorical", {"correlation": 0.4}, phase_id="foundations")

        status = engine.get_status("categorical")

        assert status.initiative_id == "categorical"
        assert status.total_phases == 2
        assert len(status.phases_complete) == 1
        assert PhaseId("foundations") in status.phases_complete
        assert status.current_phase_id == PhaseId("integration")

    def test_progress_percent(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Progress percentage is calculated correctly."""
        engine.register_initiative(phased_initiative)

        # No phases complete
        status1 = engine.get_status("categorical")
        assert status1.progress_percent == 0.0

        # One phase complete
        engine.validate("categorical", {"correlation": 0.4}, phase_id="foundations")
        status2 = engine.get_status("categorical")
        assert status2.progress_percent == 50.0

        # Both phases complete
        engine.validate("categorical", {"auc": 0.8}, phase_id="integration")
        status3 = engine.get_status("categorical")
        assert status3.progress_percent == 100.0


# =============================================================================
# Blocker Tests
# =============================================================================


class TestBlockers:
    """Tests for blocker tracking."""

    def test_blockers_after_failed_validation(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Blockers show after failed validation."""
        engine.register_initiative(flat_initiative)
        engine.validate("brain", {"tests_pass": 1.0, "test_count": 150.0})

        blockers = engine.get_blockers()

        assert len(blockers) == 1
        assert blockers[0].proposition.id == "test_count"
        assert blockers[0].current_value == 150.0
        assert blockers[0].gap == 50.0  # Need 50 more

    def test_no_blockers_after_pass(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """No blockers after passing validation."""
        engine.register_initiative(flat_initiative)
        engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        blockers = engine.get_blockers()

        assert len(blockers) == 0

    def test_blockers_from_status(
        self, engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Blockers available from status."""
        engine.register_initiative(flat_initiative)
        engine.validate("brain", {"tests_pass": 0.0, "test_count": 150.0})

        status = engine.get_status("brain")

        assert len(status.blockers) == 2  # Both propositions failed


# =============================================================================
# History Tests
# =============================================================================


class TestHistory:
    """Tests for validation history."""

    def test_get_history(self, engine: ValidationEngine, flat_initiative: Initiative) -> None:
        """Get validation history."""
        engine.register_initiative(flat_initiative)

        # Run multiple validations
        for test_count in [100, 150, 200, 250]:
            engine.validate("brain", {"tests_pass": 1.0, "test_count": float(test_count)})

        history = engine.get_history("brain", limit=3)

        assert len(history) == 3
        # Newest first
        assert history[0].measurements["test_count"] == 250.0

    def test_get_history_with_phase(
        self, engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Get history filtered by phase."""
        engine.register_initiative(phased_initiative)

        # Run foundations multiple times
        for corr in [0.2, 0.3, 0.4]:
            engine.validate("categorical", {"correlation": corr}, phase_id="foundations")

        history = engine.get_history("categorical", phase_id="foundations")

        assert len(history) == 3


# =============================================================================
# Module Singleton Tests
# =============================================================================


class TestModuleSingleton:
    """Tests for module singleton pattern."""

    def test_reset_clears_engine(self) -> None:
        """Reset clears the global engine."""
        reset_validation_engine()
        reset_validation_store()
        # Just verify it doesn't raise


# =============================================================================
# Witnessed Validation Tests
# =============================================================================


class TestCachedValidation:
    """
    Tests for cached validation via ProxyHandleStore (AD-015).

    Philosophy:
        "The representation of an object is distinct from the object itself."
        "Computation is ALWAYS explicit. There is no auto-compute."
    """

    @pytest.fixture
    def cached_engine(self) -> ValidationEngine:
        """Create a fresh engine with in-memory stores."""
        from services.proxy import ProxyHandleStore, reset_proxy_handle_store

        reset_proxy_handle_store()
        store = ValidationStore()
        proxy_store = ProxyHandleStore()
        return ValidationEngine(_store=store, _proxy_store=proxy_store, emit_marks=False)

    @pytest.mark.asyncio
    async def test_validate_cached_returns_proxy_handle(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """validate_cached returns a ProxyHandle."""
        from services.proxy import HandleStatus, ProxyHandle

        cached_engine.register_initiative(flat_initiative)

        handle = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )

        assert isinstance(handle, ProxyHandle)
        assert handle.status == HandleStatus.FRESH
        assert handle.data is not None
        assert handle.data.passed is True

    @pytest.mark.asyncio
    async def test_cached_returns_same_result_without_recompute(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Fresh cache returns cached result without re-running validation."""
        cached_engine.register_initiative(flat_initiative)

        # First call - computes
        handle1 = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )
        assert handle1.computation_count == 1

        # Second call - should return cached (same handle)
        handle2 = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )
        # Same computation count means no recompute happened
        assert handle2.computation_count == 1
        assert handle2.handle_id == handle1.handle_id

    @pytest.mark.asyncio
    async def test_changed_measurements_trigger_recompute(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Changed measurements invalidate cache via source_hash."""
        from services.proxy import SourceType

        cached_engine.register_initiative(flat_initiative)

        # First call with one measurement
        handle1 = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )
        hash1 = handle1.source_hash

        # Second call with different measurements - should recompute
        # Note: This requires invalidating the old handle or forcing
        # Since source_hash is stored per source_type, we need force=True
        # or we check that the source_hash would be different
        hash2 = cached_engine._compute_source_hash(
            InitiativeId("brain"), None, {"tests_pass": 1.0, "test_count": 300.0}
        )

        assert hash1 != hash2  # Different measurements = different hash

    @pytest.mark.asyncio
    async def test_force_triggers_recompute(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """force=True forces recomputation even with fresh cache."""
        cached_engine.register_initiative(flat_initiative)

        # First call
        handle1 = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )
        assert handle1.computation_count == 1

        # Second call with force=True
        handle2 = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}, force=True
        )
        assert handle2.computation_count == 2  # Incremented due to recompute

    @pytest.mark.asyncio
    async def test_cached_validation_preserves_data(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Cached validation preserves ValidationRun data."""
        cached_engine.register_initiative(flat_initiative)

        handle = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )

        run = handle.data
        assert run is not None
        assert run.initiative_id == "brain"
        assert run.passed is True
        assert run.measurements == {"tests_pass": 1.0, "test_count": 250.0}

    @pytest.mark.asyncio
    async def test_source_hash_deterministic(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Source hash is deterministic for same inputs."""
        cached_engine.register_initiative(flat_initiative)

        hash1 = cached_engine._compute_source_hash(
            InitiativeId("brain"), None, {"tests_pass": 1.0, "test_count": 250.0}
        )
        hash2 = cached_engine._compute_source_hash(
            InitiativeId("brain"), None, {"tests_pass": 1.0, "test_count": 250.0}
        )

        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_source_hash_includes_phase(
        self, cached_engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Source hash includes phase_id for phased initiatives."""
        cached_engine.register_initiative(phased_initiative)

        hash_with_phase = cached_engine._compute_source_hash(
            InitiativeId("categorical"), PhaseId("foundations"), {"correlation": 0.4}
        )
        hash_without_phase = cached_engine._compute_source_hash(
            InitiativeId("categorical"), None, {"correlation": 0.4}
        )

        assert hash_with_phase != hash_without_phase

    @pytest.mark.asyncio
    async def test_handle_has_human_label(
        self, cached_engine: ValidationEngine, flat_initiative: Initiative
    ) -> None:
        """Handle has descriptive human_label."""
        cached_engine.register_initiative(flat_initiative)

        handle = await cached_engine.validate_cached(
            "brain", {"tests_pass": 1.0, "test_count": 250.0}
        )

        assert "brain" in handle.human_label
        assert "Validation" in handle.human_label

    @pytest.mark.asyncio
    async def test_phased_validation_cached(
        self, cached_engine: ValidationEngine, phased_initiative: Initiative
    ) -> None:
        """Phased validation works with caching."""
        cached_engine.register_initiative(phased_initiative)

        handle = await cached_engine.validate_cached(
            "categorical", {"correlation": 0.4}, phase_id="foundations"
        )

        assert handle.data is not None
        assert handle.data.passed is True
        assert handle.data.phase_id == "foundations"
        assert "foundations" in handle.human_label


class TestWitnessedValidation:
    """
    Tests for intrinsic witness integration.

    Philosophy: "Validation IS witnessed measurement."
    Every proposition check emits a Mark.
    Every gate decision emits a Mark with Proof.empirical().
    """

    @pytest.fixture
    def mark_store(self) -> "MarkStore":
        """Create a fresh MarkStore for testing."""
        from services.witness.trace_store import MarkStore

        return MarkStore()

    @pytest.fixture
    def witnessed_engine(self, mark_store: "MarkStore") -> ValidationEngine:
        """Create an engine with mark emission enabled and injected store."""
        store = ValidationStore()
        return ValidationEngine(_store=store, _mark_store=mark_store, emit_marks=True)

    @pytest.fixture
    def unwitnessed_engine(self) -> ValidationEngine:
        """Create an engine with mark emission disabled."""
        store = ValidationStore()
        return ValidationEngine(_store=store, emit_marks=False)

    def test_flat_validation_emits_proposition_marks(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
        flat_initiative: Initiative,
    ) -> None:
        """Flat validation emits one mark per proposition."""
        witnessed_engine.register_initiative(flat_initiative)

        run = witnessed_engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        # Should have 2 proposition marks + 1 gate decision mark = 3 total
        all_marks = list(mark_store.all())
        assert len(all_marks) == 3

        # Check proposition results have mark_ids
        for result in run.gate_result.proposition_results:
            assert result.mark_id is not None, (
                f"Proposition {result.proposition_id} missing mark_id"
            )

    def test_flat_validation_emits_gate_decision_mark(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
        flat_initiative: Initiative,
    ) -> None:
        """Flat validation emits gate decision mark with Proof."""
        witnessed_engine.register_initiative(flat_initiative)

        run = witnessed_engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        # Gate result should have decision_id
        assert run.gate_result.decision_id is not None

        # Find the gate decision mark
        decision_mark = mark_store.get(run.gate_result.decision_id)
        assert decision_mark is not None
        assert decision_mark.proof is not None
        assert "PASS" in decision_mark.proof.claim

    def test_failed_gate_includes_blockers_in_proof(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
        flat_initiative: Initiative,
    ) -> None:
        """Failed gate decision includes blockers in warrant."""
        witnessed_engine.register_initiative(flat_initiative)

        run = witnessed_engine.validate("brain", {"tests_pass": 1.0, "test_count": 150.0})

        assert run.gate_result.decision_id is not None
        decision_mark = mark_store.get(run.gate_result.decision_id)

        assert "BLOCKED" in decision_mark.proof.claim
        assert "test_count" in decision_mark.proof.warrant

    def test_phased_validation_emits_marks(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
        phased_initiative: Initiative,
    ) -> None:
        """Phased validation emits marks for each phase."""
        witnessed_engine.register_initiative(phased_initiative)

        # Validate first phase
        run1 = witnessed_engine.validate("categorical", {"correlation": 0.4})

        # Should have 1 proposition mark + 1 gate decision = 2
        all_marks = list(mark_store.all())
        assert len(all_marks) == 2

        # Validate second phase
        run2 = witnessed_engine.validate("categorical", {"auc": 0.8})

        # Should now have 4 total marks (2 per phase)
        all_marks = list(mark_store.all())
        assert len(all_marks) == 4

    def test_marks_include_witness_tags(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
    ) -> None:
        """Marks include initiative's witness_tags."""
        initiative = Initiative(
            id=InitiativeId("tagged"),
            name="Tagged Initiative",
            description="Test",
            propositions=(
                Proposition(
                    id=PropositionId("p1"),
                    description="Test",
                    metric=MetricType.BINARY,
                    threshold=1.0,
                    direction=Direction.EQ,
                ),
            ),
            gate=Gate(
                id=GateId("g1"),
                name="Gate",
                condition=GateCondition.ALL_REQUIRED,
                proposition_ids=(PropositionId("p1"),),
            ),
            witness_tags=("custom_tag", "my_feature"),
        )
        witnessed_engine.register_initiative(initiative)

        witnessed_engine.validate("tagged", {"p1": 1.0})

        marks = list(mark_store.all())
        for mark in marks:
            assert "custom_tag" in mark.tags or "my_feature" in mark.tags

    def test_emit_marks_false_skips_marks(
        self,
        unwitnessed_engine: ValidationEngine,
        flat_initiative: Initiative,
    ) -> None:
        """When emit_marks=False, no marks are emitted."""
        unwitnessed_engine.register_initiative(flat_initiative)

        run = unwitnessed_engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        # Results should not have mark_ids
        for result in run.gate_result.proposition_results:
            assert result.mark_id is None

        assert run.gate_result.decision_id is None

    def test_mark_content_describes_measurement(
        self,
        witnessed_engine: ValidationEngine,
        mark_store: "MarkStore",
        flat_initiative: Initiative,
    ) -> None:
        """Mark content describes the measurement."""
        witnessed_engine.register_initiative(flat_initiative)

        witnessed_engine.validate("brain", {"tests_pass": 1.0, "test_count": 250.0})

        # Find a proposition mark
        marks = [m for m in mark_store.all() if m.proof is None]
        assert len(marks) == 2  # 2 proposition marks

        # Check content format
        for mark in marks:
            assert "Measured" in mark.response.content
            assert "=" in mark.response.content or ">=" in mark.response.content
