"""
Tests for ASHC Bootstrap Derivation (Workstream E).

Tests the ASHCBootstrap class which enables ASHC to derive itself
from Constitutional principles through a three-phase chain.

Test coverage:
- Phase 1: Constitution -> ASHC Principles
- Phase 2: ASHC Principles -> ASHC Spec
- Phase 3: ASHC Spec -> Implementation
- Full bootstrap derivation
- Fixed-point verification

Philosophy:
    "The test that proves the bootstrap is the bootstrap proving itself."
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from protocols.ashc.bootstrap_derive import (
    PHASE_1_LOSS_RANGE,
    PHASE_2_LOSS_RANGE,
    PHASE_3_LOSS_RANGE,
    SPEC_FIXED_POINT_THRESHOLD,
    TOTAL_LOSS_MAX,
    ASHCBootstrap,
    BootstrapResult,
    PhaseResult,
    bootstrap_ashc,
    create_bootstrap,
)
from protocols.ashc.paths import DerivationPath
from protocols.ashc.self_awareness import InMemoryDerivationStore

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> InMemoryDerivationStore:
    """Create empty in-memory store."""
    return InMemoryDerivationStore()


@pytest.fixture
def bootstrap(store: InMemoryDerivationStore) -> ASHCBootstrap:
    """Create ASHCBootstrap with empty store."""
    return ASHCBootstrap(store=store, emit_marks=False)


@pytest.fixture
def minimal_constitution() -> str:
    """Minimal constitution for testing."""
    return """
# The Constitution

## 1. TASTEFUL
Each agent serves a clear, justified purpose.

## 2. CURATED
Intentional selection over exhaustive cataloging.

## 3. ETHICAL
Agents augment human capability, never replace judgment.

## 4. JOY_INDUCING
Delight in interaction; personality matters.

## 5. COMPOSABLE
Agents are morphisms in a category; composition is primary.

## 6. HETERARCHICAL
Agents exist in flux, not fixed hierarchy.

## 7. GENERATIVE
Spec is compression; design should generate implementation.
"""


@pytest.fixture
def minimal_spec() -> str:
    """Minimal ASHC spec for testing."""
    return """
# ASHC: Agentic Self-Hosting Compiler

The compiler is a trace accumulator, not a code generator.
The proof is not formal - it's empirical.

## Core Insight
Evidence over generation. Run the tree a thousand times, and the pattern of nudges IS the proof.

## Phases
1. L0 Kernel: Five primitives
2. Evidence Engine: Run N variations, verify with pytest/mypy/ruff
3. Causal Graph: Learn nudge → outcome relationships
"""


# =============================================================================
# Basic Tests
# =============================================================================


class TestASHCBootstrapBasics:
    """Basic tests for ASHCBootstrap."""

    def test_create_bootstrap(self) -> None:
        """Test factory function creates valid instance."""
        bootstrap = create_bootstrap()
        assert bootstrap is not None
        assert bootstrap.store is not None
        assert bootstrap.emit_marks is True

    def test_create_bootstrap_no_marks(self) -> None:
        """Test creating bootstrap without mark emission."""
        bootstrap = create_bootstrap(emit_marks=False)
        assert bootstrap.emit_marks is False

    def test_constants_defined(self) -> None:
        """Test that constants are properly defined."""
        assert PHASE_1_LOSS_RANGE[0] < PHASE_1_LOSS_RANGE[1]
        assert PHASE_2_LOSS_RANGE[0] < PHASE_2_LOSS_RANGE[1]
        assert PHASE_3_LOSS_RANGE[0] < PHASE_3_LOSS_RANGE[1]
        assert TOTAL_LOSS_MAX > 0.0
        assert SPEC_FIXED_POINT_THRESHOLD < 0.5


# =============================================================================
# Phase Tests
# =============================================================================


class TestPhase1DerivePrinciples:
    """Tests for Phase 1: Constitution -> ASHC Principles."""

    @pytest.mark.asyncio
    async def test_derive_principles_creates_path(
        self, bootstrap: ASHCBootstrap, minimal_constitution: str
    ) -> None:
        """Phase 1 creates a derivation path."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            # Mock Galois loss computation
            mock_loss.return_value = type("obj", (object,), {"loss": 0.12})()

            result = await bootstrap._derive_principles(minimal_constitution)

            assert isinstance(result, PhaseResult)
            assert result.phase_name == "derive_principles"
            assert result.path is not None
            assert result.path.source_id == "CONSTITUTION"
            assert result.path.target_id == "ASHC_PRINCIPLES"

    @pytest.mark.asyncio
    async def test_derive_principles_extracts_witnesses(
        self, bootstrap: ASHCBootstrap, minimal_constitution: str
    ) -> None:
        """Phase 1 extracts witnesses from Constitution."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.12})()

            result = await bootstrap._derive_principles(minimal_constitution)

            # Should have witnesses for principles found in constitution
            assert len(result.witnesses) > 0


class TestPhase2DeriveSpec:
    """Tests for Phase 2: ASHC Principles -> ASHC Spec."""

    @pytest.mark.asyncio
    async def test_derive_spec_creates_path(
        self, bootstrap: ASHCBootstrap, minimal_spec: str
    ) -> None:
        """Phase 2 creates a derivation path."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.08})()

            result = await bootstrap._derive_spec("ASHC_PRINCIPLES", minimal_spec)

            assert isinstance(result, PhaseResult)
            assert result.phase_name == "derive_spec"
            assert result.path.source_id == "ASHC_PRINCIPLES"
            assert result.path.target_id == "ASHC_SPEC"


class TestPhase3CompileImplementation:
    """Tests for Phase 3: ASHC Spec -> Implementation."""

    @pytest.mark.asyncio
    async def test_compile_implementation_creates_path(
        self, bootstrap: ASHCBootstrap, minimal_spec: str
    ) -> None:
        """Phase 3 creates a derivation path."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.15})()

            result = await bootstrap._compile_implementation(minimal_spec)

            assert isinstance(result, PhaseResult)
            assert result.phase_name == "compile_implementation"
            assert result.path.source_id == "ASHC_SPEC"
            assert result.path.target_id == "ASHC_IMPL"


# =============================================================================
# Full Bootstrap Tests
# =============================================================================


class TestFullBootstrap:
    """Tests for full bootstrap derivation."""

    @pytest.mark.asyncio
    async def test_derive_self_returns_result(
        self,
        bootstrap: ASHCBootstrap,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """derive_self() returns BootstrapResult."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            # Mock low loss for success
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            result = await bootstrap.derive_self(minimal_constitution, minimal_spec)

            assert isinstance(result, BootstrapResult)
            assert len(result.phase_results) == 3
            assert result.message != ""

    @pytest.mark.asyncio
    async def test_derive_self_composes_phases(
        self,
        bootstrap: ASHCBootstrap,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """derive_self() composes all three phases."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            result = await bootstrap.derive_self(minimal_constitution, minimal_spec)

            # Full path should go from CONSTITUTION to ASHC_IMPL
            if result.full_path:
                assert result.full_path.source_id == "CONSTITUTION"
                assert result.full_path.target_id == "ASHC_IMPL"

    @pytest.mark.asyncio
    async def test_derive_self_with_high_loss_fails(
        self,
        bootstrap: ASHCBootstrap,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """derive_self() fails with high loss."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            # Mock high loss for failure
            mock_loss.return_value = type("obj", (object,), {"loss": 0.8})()

            result = await bootstrap.derive_self(minimal_constitution, minimal_spec)

            assert not result.success
            assert "failed" in result.message.lower() or result.total_loss > TOTAL_LOSS_MAX

    @pytest.mark.asyncio
    async def test_convenience_function_bootstrap_ashc(
        self,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """Test convenience function bootstrap_ashc()."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            result = await bootstrap_ashc(
                constitution=minimal_constitution,
                ashc_spec=minimal_spec,
                emit_marks=False,
            )

            assert isinstance(result, BootstrapResult)


# =============================================================================
# Fixed-Point Tests
# =============================================================================


class TestFixedPointVerification:
    """Tests for spec fixed-point verification."""

    @pytest.mark.asyncio
    async def test_low_loss_is_fixed_point(
        self, bootstrap: ASHCBootstrap, minimal_spec: str
    ) -> None:
        """Low loss spec is verified as fixed point."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            is_fixed, loss = await bootstrap._verify_spec_fixed_point(minimal_spec)

            assert is_fixed
            assert loss < SPEC_FIXED_POINT_THRESHOLD

    @pytest.mark.asyncio
    async def test_high_loss_not_fixed_point(
        self, bootstrap: ASHCBootstrap, minimal_spec: str
    ) -> None:
        """High loss spec is NOT a fixed point."""
        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.5})()

            is_fixed, loss = await bootstrap._verify_spec_fixed_point(minimal_spec)

            assert not is_fixed
            assert loss > SPEC_FIXED_POINT_THRESHOLD


# =============================================================================
# Result Message Tests
# =============================================================================


class TestResultMessages:
    """Tests for result message formatting."""

    def test_success_message(self, bootstrap: ASHCBootstrap) -> None:
        """Success message is properly formatted."""
        message = bootstrap._build_message(
            success=True,
            is_fixed_point=True,
            spec_loss=0.05,
            total_loss=0.25,
        )

        assert "successful" in message.lower()
        assert "0.05" in message or "0.050" in message

    def test_failure_message_not_fixed_point(self, bootstrap: ASHCBootstrap) -> None:
        """Failure message mentions fixed point issue."""
        message = bootstrap._build_message(
            success=False,
            is_fixed_point=False,
            spec_loss=0.5,
            total_loss=0.3,
        )

        assert "failed" in message.lower()
        assert "fixed point" in message.lower()

    def test_failure_message_high_loss(self, bootstrap: ASHCBootstrap) -> None:
        """Failure message mentions high loss."""
        message = bootstrap._build_message(
            success=False,
            is_fixed_point=True,
            spec_loss=0.05,
            total_loss=0.6,
        )

        assert "failed" in message.lower()
        assert "loss" in message.lower()


# =============================================================================
# Path Storage Tests
# =============================================================================


class TestPathStorage:
    """Tests for storing bootstrap path."""

    @pytest.mark.asyncio
    async def test_successful_bootstrap_stores_path(
        self,
        store: InMemoryDerivationStore,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """Successful bootstrap stores the full path."""
        bootstrap = ASHCBootstrap(store=store, emit_marks=False)

        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            result = await bootstrap.derive_self(minimal_constitution, minimal_spec)

            if result.success:
                # Path should be stored
                all_paths = await store.query_all_paths()
                assert len(all_paths) >= 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestBootstrapIntegration:
    """Integration tests for bootstrap with self-awareness."""

    @pytest.mark.asyncio
    async def test_bootstrap_then_check_grounded(
        self,
        minimal_constitution: str,
        minimal_spec: str,
    ) -> None:
        """After bootstrap, ASHC should be more grounded."""
        from protocols.ashc.self_awareness import ASHCSelfAwareness

        store = InMemoryDerivationStore()
        bootstrap = ASHCBootstrap(store=store, emit_marks=False)

        with patch(
            "protocols.ashc.bootstrap_derive.compute_galois_loss_async",
            new_callable=AsyncMock,
        ) as mock_loss:
            mock_loss.return_value = type("obj", (object,), {"loss": 0.05})()

            # Run bootstrap
            result = await bootstrap.derive_self(minimal_constitution, minimal_spec)

            if result.success:
                # Check self-awareness
                self_aware = ASHCSelfAwareness(
                    store=store,
                    components=["ASHC_IMPL"],  # The target of bootstrap
                    principles=["CONSTITUTION"],  # The source
                )

                # Explain the derivation
                paths = await self_aware.explain_derivation("CONSTITUTION", "ASHC_IMPL")
                assert len(paths) >= 1


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TestASHCBootstrapBasics",
    "TestPhase1DerivePrinciples",
    "TestPhase2DeriveSpec",
    "TestPhase3CompileImplementation",
    "TestFullBootstrap",
    "TestFixedPointVerification",
    "TestResultMessages",
    "TestPathStorage",
    "TestBootstrapIntegration",
]
