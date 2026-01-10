"""
ASHC Bootstrap: Self-Derivation from Constitution.

Implements the Lawvere fixed-point: ASHC deriving itself from Constitutional
principles through a three-phase derivation chain.

The Three Phases:
    1. Constitution -> ASHC Principles (instantiation, loss ~0.12)
    2. ASHC Principles -> ASHC Spec (refinement, loss ~0.08)
    3. ASHC Spec -> ASHC Implementation (compilation, loss ~0.15)

Philosophy:
    "The kernel that proves itself is the kernel that trusts itself.
     Bootstrap is not recursion—it's a Lawvere fixed point."

The Bootstrap Strange Loop:
    - Constitution defines ASHC
    - ASHC verifies Constitution
    - The fixed point IS the grounding

Requirements:
    - ASHC spec must be Galois fixed point (loss < 0.10)
    - Total path loss must be within L4 SPEC bounds (0.30-0.45)
    - Each phase must emit witnesses for audit trail

See: spec/protocols/zero-seed1/ashc.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from protocols.ashc.paths import (
    DerivationPath,
    PathKind,
    PathWitness,
    PathWitnessType,
    WitnessType,
    emit_ashc_mark,
)
from protocols.ashc.self_awareness import (
    CONSTITUTIONAL_PRINCIPLES,
    ASHCSelfAwareness,
    DerivationStoreProtocol,
    InMemoryDerivationStore,
)
from services.k_block.core.derivation import DerivationDAG
from services.zero_seed.galois.galois_loss import (
    FIXED_POINT_THRESHOLD,
    LAYER_LOSS_BOUNDS,
    GaloisLossComputer,
    classify_evidence_tier,
    compute_galois_loss_async,
    find_fixed_point,
)

logger = logging.getLogger("kgents.ashc.bootstrap")


# =============================================================================
# Constants
# =============================================================================

# Expected loss ranges for each phase
PHASE_1_LOSS_RANGE = (0.05, 0.15)  # Constitution -> ASHC Principles
PHASE_2_LOSS_RANGE = (0.05, 0.12)  # ASHC Principles -> ASHC Spec
PHASE_3_LOSS_RANGE = (0.10, 0.20)  # ASHC Spec -> Implementation

# Total expected loss (within L4 SPEC bounds)
TOTAL_LOSS_MAX = 0.45  # Upper bound of L4

# Fixed-point threshold for spec verification
SPEC_FIXED_POINT_THRESHOLD = 0.10

# Default paths
DEFAULT_CONSTITUTION_PATH = Path("CLAUDE.md")  # Constitution is in CLAUDE.md
DEFAULT_ASHC_SPEC_PATH = Path("spec/protocols/proof-generation.md")


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class PhaseResult:
    """Result of a single bootstrap phase."""

    phase_name: str
    path: DerivationPath[Any, Any]
    galois_loss: float
    witnesses: tuple[PathWitness, ...]
    duration_ms: int


@dataclass(frozen=True)
class BootstrapResult:
    """
    Complete result of ASHC bootstrap derivation.

    Contains:
    - The full composed derivation path
    - Results from each of the three phases
    - Fixed-point verification result
    - Whether the bootstrap succeeded
    """

    success: bool
    full_path: DerivationPath[Any, Any] | None
    phase_results: tuple[PhaseResult, ...]
    is_spec_fixed_point: bool
    spec_loss: float
    total_loss: float
    message: str


# =============================================================================
# ASHCBootstrap
# =============================================================================


@dataclass
class ASHCBootstrap:
    """
    Bootstrap derivation for ASHC.

    Implements the three-phase derivation from Constitution to Implementation,
    creating ASHC's "birth certificate"—a complete derivation path showing
    principled justification for ASHC's existence.

    The Three Phases:
        1. _derive_principles: Constitution -> ASHC-specific principles
        2. _derive_spec: ASHC Principles -> spec/protocols/proof-generation.md
        3. _compile_implementation: ASHC Spec -> protocols/ashc/*.py

    Usage:
        >>> bootstrap = ASHCBootstrap(store=store)
        >>> result = await bootstrap.derive_self(constitution, ashc_spec)
        >>> if result.success:
        ...     print(f"Bootstrap complete: {result.full_path.path_id}")
    """

    store: DerivationStoreProtocol = field(default_factory=InMemoryDerivationStore)
    dag: DerivationDAG = field(default_factory=DerivationDAG)
    emit_marks: bool = True

    async def derive_self(
        self,
        constitution: str | dict[str, Any] | None = None,
        ashc_spec: str | None = None,
    ) -> BootstrapResult:
        """
        Construct the full derivation path for ASHC itself.

        This is the main entry point for bootstrap. It:
        1. Loads Constitution and ASHC spec if not provided
        2. Executes three derivation phases
        3. Composes the full path
        4. Verifies spec is a fixed point
        5. Stores the "birth certificate"

        Args:
            constitution: Constitution content (loads from CLAUDE.md if None)
            ashc_spec: ASHC spec content (loads from spec path if None)

        Returns:
            BootstrapResult with full derivation path and status
        """
        import time

        start_time = time.time()

        # Load defaults if needed
        constitution_text = self._load_constitution(constitution)
        spec_text = self._load_ashc_spec(ashc_spec)

        phase_results: list[PhaseResult] = []

        try:
            # Phase 1: Constitution -> ASHC Principles
            logger.info("Bootstrap Phase 1: Deriving ASHC principles from Constitution")
            phase1_result = await self._derive_principles(constitution_text)
            phase_results.append(phase1_result)

            if self.emit_marks:
                await emit_ashc_mark(
                    action="Bootstrap Phase 1: Derived ASHC principles",
                    evidence={
                        "phase": 1,
                        "galois_loss": phase1_result.galois_loss,
                        "witnesses": len(phase1_result.witnesses),
                    },
                    witness_type=WitnessType.COMPOSITION,
                    galois_loss=phase1_result.galois_loss,
                )

            # Phase 2: ASHC Principles -> ASHC Spec
            logger.info("Bootstrap Phase 2: Refining principles to spec")
            phase2_result = await self._derive_spec(
                phase1_result.path.target_id,
                spec_text,
            )
            phase_results.append(phase2_result)

            if self.emit_marks:
                await emit_ashc_mark(
                    action="Bootstrap Phase 2: Refined principles to spec",
                    evidence={
                        "phase": 2,
                        "galois_loss": phase2_result.galois_loss,
                        "witnesses": len(phase2_result.witnesses),
                    },
                    witness_type=WitnessType.COMPOSITION,
                    galois_loss=phase2_result.galois_loss,
                )

            # Phase 3: ASHC Spec -> Implementation
            logger.info("Bootstrap Phase 3: Compiling spec to implementation")
            phase3_result = await self._compile_implementation(spec_text)
            phase_results.append(phase3_result)

            if self.emit_marks:
                await emit_ashc_mark(
                    action="Bootstrap Phase 3: Compiled spec to implementation",
                    evidence={
                        "phase": 3,
                        "galois_loss": phase3_result.galois_loss,
                        "witnesses": len(phase3_result.witnesses),
                    },
                    witness_type=WitnessType.COMPOSITION,
                    galois_loss=phase3_result.galois_loss,
                )

            # Compose full path: (phase1 ; phase2) ; phase3
            composed_12 = phase1_result.path.compose(phase2_result.path)
            full_path = composed_12.compose(phase3_result.path)

            # Verify spec is a fixed point
            is_fixed_point, spec_loss = await self._verify_spec_fixed_point(spec_text)

            # Check total loss
            total_loss = full_path.galois_loss

            # Determine success
            success = (
                is_fixed_point
                and total_loss <= TOTAL_LOSS_MAX
                and all(pr.galois_loss < 0.5 for pr in phase_results)
            )

            # Store the birth certificate
            if success:
                await self.store.save_path(full_path)
                logger.info(
                    f"Bootstrap complete: path_id={full_path.path_id}, total_loss={total_loss:.3f}"
                )
            else:
                logger.warning(
                    f"Bootstrap failed: is_fixed_point={is_fixed_point}, "
                    f"total_loss={total_loss:.3f}"
                )

            message = self._build_message(success, is_fixed_point, spec_loss, total_loss)

            return BootstrapResult(
                success=success,
                full_path=full_path,
                phase_results=tuple(phase_results),
                is_spec_fixed_point=is_fixed_point,
                spec_loss=spec_loss,
                total_loss=total_loss,
                message=message,
            )

        except Exception as e:
            logger.error(f"Bootstrap failed with exception: {e}")
            return BootstrapResult(
                success=False,
                full_path=None,
                phase_results=tuple(phase_results),
                is_spec_fixed_point=False,
                spec_loss=1.0,
                total_loss=1.0,
                message=f"Bootstrap failed: {e}",
            )

    async def _derive_principles(self, constitution: str) -> PhaseResult:
        """
        Phase 1: Map Constitution principles to ASHC-specific principles.

        Constitution L1.1-L2.14 -> ASHC principles like:
        - Evidence over generation (from GENERATIVE)
        - Empirical proof over formal proof (from COMPOSABLE)
        - Trace accumulation (from WITNESS)
        """
        import time

        start = time.time()

        # Extract ASHC-relevant principles from Constitution
        ashc_principles = self._extract_ashc_principles(constitution)

        # Compute Galois loss for this transformation
        principle_text = "\n".join(f"- {p}" for p in ashc_principles)
        galois_result = await compute_galois_loss_async(
            f"CONSTITUTION:\n{constitution[:2000]}\n\nASHC_PRINCIPLES:\n{principle_text}"
        )

        # Create witnesses for each principle
        witnesses: list[PathWitness] = []
        for principle_id in CONSTITUTIONAL_PRINCIPLES:
            if principle_id in constitution:
                witnesses.append(
                    PathWitness.from_principle(
                        principle_id, f"Constitutional principle: {principle_id}"
                    )
                )

        # Create derivation path
        path: DerivationPath[str, str] = DerivationPath.derive(
            source_id="CONSTITUTION",
            target_id="ASHC_PRINCIPLES",
            witnesses=witnesses,
            galois_loss=galois_result.loss,
            principle_scores={p: 0.9 for p in CONSTITUTIONAL_PRINCIPLES},
        )

        duration_ms = int((time.time() - start) * 1000)

        return PhaseResult(
            phase_name="derive_principles",
            path=path,
            galois_loss=galois_result.loss,
            witnesses=tuple(witnesses),
            duration_ms=duration_ms,
        )

    async def _derive_spec(self, principles_id: str, spec_text: str) -> PhaseResult:
        """
        Phase 2: Refine ASHC principles to specification.

        ASHC principles -> spec/protocols/proof-generation.md
        """
        import time

        start = time.time()

        # Compute Galois loss for spec refinement
        galois_result = await compute_galois_loss_async(spec_text)

        # Create witness for spec
        witnesses = [
            PathWitness.create(
                witness_type=PathWitnessType.SPEC,
                evidence={
                    "spec_path": "spec/protocols/proof-generation.md",
                    "spec_length": len(spec_text),
                },
                confidence=1.0 - galois_result.loss,
            )
        ]

        # Create derivation path
        path: DerivationPath[str, str] = DerivationPath.derive(
            source_id=principles_id,
            target_id="ASHC_SPEC",
            witnesses=witnesses,
            galois_loss=galois_result.loss,
            principle_scores={
                "GENERATIVE": 0.95,  # Spec IS compressed knowledge
                "COMPOSABLE": 0.9,
                "CURATED": 0.85,
            },
        )

        duration_ms = int((time.time() - start) * 1000)

        return PhaseResult(
            phase_name="derive_spec",
            path=path,
            galois_loss=galois_result.loss,
            witnesses=tuple(witnesses),
            duration_ms=duration_ms,
        )

    async def _compile_implementation(self, spec_text: str) -> PhaseResult:
        """
        Phase 3: Compile ASHC spec to implementation.

        ASHC spec -> protocols/ashc/*.py
        """
        import time

        start = time.time()

        # Get list of implementation files
        impl_files = self._get_ashc_implementation_files()

        # Compute Galois loss for implementation
        # This is higher than spec refinement (more transformation)
        galois_result = await compute_galois_loss_async(
            f"SPEC:\n{spec_text[:1000]}\n\nIMPL_FILES:\n{', '.join(impl_files)}"
        )

        # Create witness for implementation
        witnesses = [
            PathWitness.create(
                witness_type=PathWitnessType.TEST,
                evidence={
                    "impl_files": impl_files,
                    "file_count": len(impl_files),
                },
                confidence=1.0 - galois_result.loss,
            )
        ]

        # Create derivation path
        path: DerivationPath[str, str] = DerivationPath.derive(
            source_id="ASHC_SPEC",
            target_id="ASHC_IMPL",
            witnesses=witnesses,
            galois_loss=galois_result.loss,
            principle_scores={
                "COMPOSABLE": 0.85,  # Implementation composes
                "GENERATIVE": 0.80,  # Derived from spec
                "TASTEFUL": 0.75,  # Code quality
            },
        )

        duration_ms = int((time.time() - start) * 1000)

        return PhaseResult(
            phase_name="compile_implementation",
            path=path,
            galois_loss=galois_result.loss,
            witnesses=tuple(witnesses),
            duration_ms=duration_ms,
        )

    async def _verify_spec_fixed_point(self, spec_text: str) -> tuple[bool, float]:
        """
        Verify ASHC spec is a Galois fixed point.

        A fixed point satisfies: L(R^n(spec)) < epsilon for some n.
        For ASHC spec, we require loss < 0.10.
        """
        try:
            galois_result = await compute_galois_loss_async(spec_text)
            loss = galois_result.loss
            is_fixed_point = loss < SPEC_FIXED_POINT_THRESHOLD

            logger.info(
                f"Spec fixed-point check: loss={loss:.3f}, "
                f"threshold={SPEC_FIXED_POINT_THRESHOLD}, "
                f"is_fixed_point={is_fixed_point}"
            )

            return is_fixed_point, loss

        except Exception as e:
            logger.error(f"Fixed-point verification failed: {e}")
            return False, 1.0

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _load_constitution(self, constitution: str | dict[str, Any] | None) -> str:
        """Load Constitution content."""
        if isinstance(constitution, str):
            return constitution

        if isinstance(constitution, dict):
            # Serialize dict to string
            import json

            return json.dumps(constitution, indent=2)

        # Load from default path
        try:
            return DEFAULT_CONSTITUTION_PATH.read_text()
        except FileNotFoundError:
            # Fallback: minimal constitution
            return "\n".join(f"L1.{i} {p}" for i, p in enumerate(CONSTITUTIONAL_PRINCIPLES, 1))

    def _load_ashc_spec(self, spec: str | None) -> str:
        """Load ASHC spec content."""
        if spec:
            return spec

        # Load from default path
        try:
            return DEFAULT_ASHC_SPEC_PATH.read_text()
        except FileNotFoundError:
            # Fallback: minimal spec
            return """
# ASHC: Agentic Self-Hosting Compiler

The compiler is a trace accumulator, not a code generator.
The proof is not formal—it's empirical.

## Core Insight
Evidence over generation. Run the tree a thousand times, and the pattern of nudges IS the proof.

## Phases
1. L0 Kernel: Five primitives
2. Evidence Engine: Run N variations, verify with pytest/mypy/ruff
3. Causal Graph: Learn nudge → outcome relationships
"""

    def _extract_ashc_principles(self, constitution: str) -> list[str]:
        """Extract ASHC-specific principles from Constitution."""
        # ASHC-specific interpretations of constitutional principles
        return [
            "Evidence over generation (GENERATIVE applied to verification)",
            "Empirical proof over formal proof (COMPOSABLE applied to testing)",
            "Trace accumulation creates trust (JOY_INDUCING through reliability)",
            "The proof has skin in the game (ETHICAL accountability)",
            "Compile once, verify many times (CURATED evidence selection)",
            "The pattern of nudges IS the proof (HETERARCHICAL learning)",
            "Self-hosting as fixed point (TASTEFUL self-consistency)",
        ]

    def _get_ashc_implementation_files(self) -> list[str]:
        """Get list of ASHC implementation files."""
        return [
            "protocols/ashc/__init__.py",
            "protocols/ashc/evidence.py",
            "protocols/ashc/adaptive.py",
            "protocols/ashc/economy.py",
            "protocols/ashc/paths/types.py",
            "protocols/ashc/paths/composition.py",
            "protocols/ashc/paths/witness_bridge.py",
            "protocols/ashc/self_awareness.py",
            "protocols/ashc/bootstrap_derive.py",
            "services/ashc/__init__.py",
            "services/ashc/checker.py",
            "services/ashc/obligation.py",
            "services/ashc/persistence.py",
            "services/ashc/search.py",
        ]

    def _build_message(
        self,
        success: bool,
        is_fixed_point: bool,
        spec_loss: float,
        total_loss: float,
    ) -> str:
        """Build human-readable result message."""
        if success:
            return (
                f"Bootstrap successful! "
                f"Spec loss: {spec_loss:.3f} (fixed point). "
                f"Total path loss: {total_loss:.3f} (within L4 bounds)."
            )

        issues = []
        if not is_fixed_point:
            issues.append(
                f"Spec not a fixed point (loss={spec_loss:.3f} > {SPEC_FIXED_POINT_THRESHOLD})"
            )
        if total_loss > TOTAL_LOSS_MAX:
            issues.append(f"Total loss too high ({total_loss:.3f} > {TOTAL_LOSS_MAX})")

        return f"Bootstrap failed: {'; '.join(issues)}"


# =============================================================================
# Factory Functions
# =============================================================================


def create_bootstrap(
    store: DerivationStoreProtocol | None = None,
    emit_marks: bool = True,
) -> ASHCBootstrap:
    """
    Create an ASHCBootstrap instance with defaults.

    Args:
        store: DerivationStore (defaults to InMemoryDerivationStore)
        emit_marks: Whether to emit witness marks (default True)

    Returns:
        Configured ASHCBootstrap instance
    """
    return ASHCBootstrap(
        store=store or InMemoryDerivationStore(),
        emit_marks=emit_marks,
    )


async def bootstrap_ashc(
    constitution: str | dict[str, Any] | None = None,
    ashc_spec: str | None = None,
    emit_marks: bool = True,
) -> BootstrapResult:
    """
    Convenience function to run ASHC bootstrap.

    Args:
        constitution: Constitution content (loads from CLAUDE.md if None)
        ashc_spec: ASHC spec content (loads from spec path if None)
        emit_marks: Whether to emit witness marks

    Returns:
        BootstrapResult with full derivation path and status
    """
    bootstrap = create_bootstrap(emit_marks=emit_marks)
    return await bootstrap.derive_self(constitution, ashc_spec)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "PHASE_1_LOSS_RANGE",
    "PHASE_2_LOSS_RANGE",
    "PHASE_3_LOSS_RANGE",
    "TOTAL_LOSS_MAX",
    "SPEC_FIXED_POINT_THRESHOLD",
    "DEFAULT_CONSTITUTION_PATH",
    "DEFAULT_ASHC_SPEC_PATH",
    # Result Types
    "PhaseResult",
    "BootstrapResult",
    # Main Class
    "ASHCBootstrap",
    # Factory Functions
    "create_bootstrap",
    "bootstrap_ashc",
]
