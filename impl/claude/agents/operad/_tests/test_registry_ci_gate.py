"""
CI Gate: Operad Registry Verification.

This test ensures ALL operads in kgents:
1. Use canonical types from agents.operad.core
2. Register with OperadRegistry
3. Extend AGENT_OPERAD operations and laws
4. Have verifiable laws

Run as part of CI to catch operad drift.

Phase 1 Operad Unification (2025-12-17):
- Migrated FLOW_OPERAD, CHAT_OPERAD, RESEARCH_OPERAD, COLLABORATION_OPERAD
- Migrated ATELIER_OPERAD
- Migrated GROWTH_OPERAD
- Target: 100% canonical usage (11/11 operads)
"""

from __future__ import annotations

import pytest
from agents.operad.core import AGENT_OPERAD, Law, Operad, OperadRegistry, Operation
from agents.poly import from_function

# ============================================================================
# Import all operads to ensure registration
# ============================================================================


def import_all_operads() -> None:
    """
    Import all operad modules to trigger registration.

    This ensures @module-level registration happens before tests.
    """
    # Core operad (already imported)

    # Town operad
    # Atelier operad
    from agents.atelier.workshop.operad import ATELIER_OPERAD

    # Brain operad (Phase 4)
    from agents.brain.operad import BRAIN_OPERAD

    # Flow operads (4 operads)
    from agents.f.operad import (
        CHAT_OPERAD,
        COLLABORATION_OPERAD,
        FLOW_OPERAD,
        RESEARCH_OPERAD,
    )

    # Park/Director operad (Phase 4)
    from agents.park.operad import DIRECTOR_OPERAD
    from agents.town.operad import TOWN_OPERAD

    # Growth operad
    from protocols.agentese.contexts.self_grow.operad import GROWTH_OPERAD

    # N-Phase operad
    from protocols.nphase.operad import NPHASE_OPERAD

    # Domain operad (if exists)
    try:
        from agents.domain.drills.operad import DRILL_OPERAD
    except ImportError:
        pass  # Optional

    # Soul operad (if exists)
    try:
        from agents.k.operad import SOUL_OPERAD
    except ImportError:
        pass  # Optional


# Import on module load
import_all_operads()


# ============================================================================
# Expected Operads
# ============================================================================


EXPECTED_OPERADS = [
    "AgentOperad",
    "TownOperad",
    "FlowOperad",
    "ChatOperad",
    "ResearchOperad",
    "CollaborationOperad",
    "AtelierOperad",
    "GrowthOperad",
    "NPHASE",  # N-Phase operad uses uppercase name
    "BrainOperad",  # Phase 4: Brain vertical slice
    "DirectorOperad",  # Phase 4: Park vertical slice
]

# Full operads that should extend AGENT_OPERAD completely
FULL_OPERADS = [
    "AgentOperad",
    "TownOperad",
    "FlowOperad",
    "AtelierOperad",
    "GrowthOperad",
    "BrainOperad",  # Phase 4
    "DirectorOperad",  # Phase 4
]

# Subset operads (intentionally filtered views of a parent operad)
SUBSET_OPERADS = ["ChatOperad", "ResearchOperad", "CollaborationOperad"]

# Domain operads (domain-specific, don't extend universal operations)
# These have their own operation vocabulary for their domain
DOMAIN_OPERADS = [
    "LAYOUT",  # Design system - layout composition
    "CONTENT",  # Design system - content degradation
    "MOTION",  # Design system - animation composition
    "DESIGN",  # Design system - unified
]

# Legacy operads (not yet migrated to canonical pattern)
LEGACY_OPERADS = ["NPHASE"]

# Test artifacts (registered by other tests, not real operads)
TEST_ARTIFACTS = ["CustomOperad"]

UNIVERSAL_OPERATIONS = ["seq", "par", "branch", "fix", "trace"]
UNIVERSAL_LAWS = ["seq_associativity", "par_associativity"]


# ============================================================================
# CI Gate Tests
# ============================================================================


class TestOperadRegistryCIGate:
    """
    CI Gate: Verify all operads are properly registered and canonical.

    These tests should pass in CI to ensure operad hygiene.
    """

    def test_all_expected_operads_registered(self) -> None:
        """All expected operads are registered."""
        registered = OperadRegistry.all_operads()

        for name in EXPECTED_OPERADS:
            assert name in registered, f"Operad '{name}' not registered"

    def test_all_registered_operads_are_canonical_type(self) -> None:
        """All registered operads use canonical Operad type."""
        for name, operad in OperadRegistry.all_operads().items():
            assert isinstance(operad, Operad), (
                f"Operad '{name}' is {type(operad).__name__}, not canonical Operad"
            )

    def test_all_operations_are_canonical_type(self) -> None:
        """All operations in registered operads use canonical Operation type."""
        for name, operad in OperadRegistry.all_operads().items():
            for op_name, op in operad.operations.items():
                assert isinstance(op, Operation), (
                    f"Operation '{op_name}' in operad '{name}' is "
                    f"{type(op).__name__}, not canonical Operation"
                )

    def test_all_laws_are_canonical_type(self) -> None:
        """All laws in registered operads use canonical Law type."""
        for name, operad in OperadRegistry.all_operads().items():
            for law in operad.laws:
                assert isinstance(law, Law), (
                    f"Law '{law.name if hasattr(law, 'name') else law}' in operad "
                    f"'{name}' is {type(law).__name__}, not canonical Law"
                )

    def test_full_operads_extend_agent_operad_operations(self) -> None:
        """Full operads extend AGENT_OPERAD operations completely."""
        for name, operad in OperadRegistry.all_operads().items():
            if name == "AgentOperad":
                continue
            if (
                name in SUBSET_OPERADS
                or name in DOMAIN_OPERADS
                or name in LEGACY_OPERADS
                or name in TEST_ARTIFACTS
            ):
                continue  # Skip subsets, domain-specific, legacy, and test artifacts

            for universal_op in UNIVERSAL_OPERATIONS:
                assert universal_op in operad.operations, (
                    f"Full operad '{name}' missing universal operation '{universal_op}'"
                )

    def test_subset_operads_have_minimal_operations(self) -> None:
        """Subset operads have at least seq and par."""
        for name, operad in OperadRegistry.all_operads().items():
            if name not in SUBSET_OPERADS:
                continue

            # Subset operads should at least have seq and par
            assert "seq" in operad.operations, (
                f"Subset operad '{name}' missing 'seq' operation"
            )
            assert "par" in operad.operations, (
                f"Subset operad '{name}' missing 'par' operation"
            )

    def test_full_operads_extend_agent_operad_laws(self) -> None:
        """Full operads extend AGENT_OPERAD laws."""
        for name, operad in OperadRegistry.all_operads().items():
            if name == "AgentOperad":
                continue
            if (
                name in SUBSET_OPERADS
                or name in DOMAIN_OPERADS
                or name in LEGACY_OPERADS
                or name in TEST_ARTIFACTS
            ):
                continue  # Skip subsets, domain-specific, legacy, and test artifacts

            law_names = [law.name for law in operad.laws]
            for universal_law in UNIVERSAL_LAWS:
                assert universal_law in law_names, (
                    f"Full operad '{name}' missing universal law '{universal_law}'"
                )

    def test_verify_canonical_operads(self) -> None:
        """Canonical operads (non-legacy) pass law verification."""
        # Create test agents
        a = from_function("A", lambda x: x + 1)
        b = from_function("B", lambda x: x * 2)
        c = from_function("C", lambda x: x - 1)

        # Verify only canonical operads
        for name, operad in OperadRegistry.all_operads().items():
            if name in LEGACY_OPERADS:
                continue  # Skip legacy operads that may have incompatible verify signatures

            verifications = operad.verify_all_laws(a, b, c)

            # Laws that can be verified should pass, skip, or be structurally verified
            for v in verifications:
                # Allow PASSED, SKIPPED, or STRUCTURAL (type-level verification)
                assert v.status.name in ("PASSED", "SKIPPED", "STRUCTURAL"), (
                    f"Law '{v.law_name}' in operad '{name}' FAILED: {v.message}"
                )

    def test_no_duplicate_operad_names(self) -> None:
        """No operads with duplicate names."""
        registered = OperadRegistry.all_operads()
        names = list(registered.keys())
        assert len(names) == len(set(names)), "Duplicate operad names detected"

    def test_all_operations_have_compose_function(self) -> None:
        """All operations have a compose function."""
        for name, operad in OperadRegistry.all_operads().items():
            for op_name, op in operad.operations.items():
                assert op.compose is not None, (
                    f"Operation '{op_name}' in operad '{name}' has no compose function"
                )

    def test_all_laws_have_verify_function(self) -> None:
        """All laws have a verify function."""
        for name, operad in OperadRegistry.all_operads().items():
            for law in operad.laws:
                assert law.verify is not None, (
                    f"Law '{law.name}' in operad '{name}' has no verify function"
                )


class TestOperadCoverageMetrics:
    """Metrics for operad coverage."""

    def test_print_operad_coverage(self) -> None:
        """Print operad coverage metrics."""
        registered = OperadRegistry.all_operads()

        print("\n=== OPERAD REGISTRY COVERAGE ===")
        print(f"Total registered: {len(registered)}")
        print(f"Expected: {len(EXPECTED_OPERADS)}")
        print(
            f"Coverage: {len(registered)}/{len(EXPECTED_OPERADS)} ({100 * len(registered) // len(EXPECTED_OPERADS)}%)"
        )

        print("\nRegistered operads:")
        for name, operad in sorted(registered.items()):
            ops_count = len(operad.operations)
            laws_count = len(operad.laws)
            universal_ops = sum(
                1 for op in UNIVERSAL_OPERATIONS if op in operad.operations
            )
            universal_laws = sum(
                1 for law in UNIVERSAL_LAWS if any(l.name == law for l in operad.laws)
            )
            print(f"  {name}:")
            print(
                f"    Operations: {ops_count} ({universal_ops}/{len(UNIVERSAL_OPERATIONS)} universal)"
            )
            print(
                f"    Laws: {laws_count} ({universal_laws}/{len(UNIVERSAL_LAWS)} universal)"
            )

        # Assert minimum coverage
        assert len(registered) >= len(EXPECTED_OPERADS), (
            f"Registry has {len(registered)} operads, expected at least {len(EXPECTED_OPERADS)}"
        )


class TestSpecificOperadIntegration:
    """Test specific operads are properly integrated."""

    def test_town_operad_registered(self) -> None:
        """TownOperad is properly registered."""
        operad = OperadRegistry.get("TownOperad")
        assert operad is not None
        assert "greet" in operad.operations
        assert "gossip" in operad.operations

    def test_flow_operad_registered(self) -> None:
        """FlowOperad is properly registered."""
        operad = OperadRegistry.get("FlowOperad")
        assert operad is not None
        assert "start" in operad.operations
        assert "turn" in operad.operations

    def test_atelier_operad_registered(self) -> None:
        """AtelierOperad is properly registered."""
        operad = OperadRegistry.get("AtelierOperad")
        assert operad is not None
        assert "duet" in operad.operations
        assert "ensemble" in operad.operations

    def test_growth_operad_registered(self) -> None:
        """GrowthOperad is properly registered."""
        operad = OperadRegistry.get("GrowthOperad")
        assert operad is not None
        assert "recognize" in operad.operations
        assert "propose" in operad.operations
        assert "germinate" in operad.operations


# ============================================================================
# Run as script for quick check
# ============================================================================


if __name__ == "__main__":
    import_all_operads()
    registered = OperadRegistry.all_operads()

    print("=== OPERAD REGISTRY ===")
    print(f"Total: {len(registered)}")
    for name in sorted(registered.keys()):
        operad = registered[name]
        print(f"  {name}: {len(operad.operations)} ops, {len(operad.laws)} laws")

    # Quick verification
    a = from_function("A", lambda x: x + 1)
    b = from_function("B", lambda x: x * 2)
    c = from_function("C", lambda x: x - 1)

    results = OperadRegistry.verify_all(a, b, c)
    print("\n=== VERIFICATION ===")
    for name, verifications in results.items():
        passed = sum(1 for v in verifications if v.passed)
        print(f"  {name}: {passed}/{len(verifications)} laws pass")
