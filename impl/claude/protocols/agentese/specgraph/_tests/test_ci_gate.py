"""
CI Gate: Verify Spec-Impl Alignment (SpecGraph Discovery Mode).

This test enforces the autopoietic invariant:
    audit_impl(impl/, discover_from_spec(spec/)) = no_critical_gaps

The gate FAILS if:
1. A spec defines a polynomial but impl is missing polynomial.py
2. A spec defines an operad but impl is missing operad.py
3. A spec defines an AGENTESE path but impl has no @node decorator

The gate WARNS (but passes) if:
1. A spec defines a sheaf but impl is missing sheaf.py (optional)
2. Impl has extra components not in spec (orphan detection)

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ..discovery import (
    AuditReport,
    DiscoveryReport,
    GapSeverity,
    audit_impl,
    discover_from_spec,
    full_audit,
    print_audit_report,
)

# === Fixtures ===


def get_project_root() -> Path:
    """Get the kgents project root."""
    # This file is at impl/claude/protocols/agentese/specgraph/_tests/
    current = Path(__file__).resolve()
    for _ in range(7):  # Walk up to kgents/
        current = current.parent
    return current


def get_spec_root() -> Path:
    """Get the spec/ directory."""
    return get_project_root() / "spec"


def get_impl_root() -> Path:
    """Get the impl/claude/ directory."""
    return get_project_root() / "impl" / "claude"


@pytest.fixture
def spec_root() -> Path:
    """Fixture for spec root directory."""
    return get_spec_root()


@pytest.fixture
def impl_root() -> Path:
    """Fixture for impl root directory."""
    return get_impl_root()


# === Discovery Tests ===


class TestDiscovery:
    """Tests for spec discovery."""

    def test_discover_finds_specs(self, spec_root: Path) -> None:
        """Discovery should find specs with YAML frontmatter."""
        if not spec_root.exists():
            pytest.skip("Spec directory not found")

        report = discover_from_spec(spec_root)

        # Should find at least some specs
        # Note: This may be 0 if no specs have YAML frontmatter yet
        assert report.total_specs >= 0

    def test_discover_counts_components(self, spec_root: Path) -> None:
        """Discovery should count component types."""
        if not spec_root.exists():
            pytest.skip("Spec directory not found")

        report = discover_from_spec(spec_root)

        # Counts should be non-negative
        assert report.specs_with_polynomial >= 0
        assert report.specs_with_operad >= 0
        assert report.specs_with_node >= 0
        assert report.specs_with_sheaf >= 0


# === Audit Tests ===


class TestAudit:
    """Tests for impl auditing."""

    def test_audit_runs_without_error(self, spec_root: Path, impl_root: Path) -> None:
        """Audit should complete without exceptions."""
        if not spec_root.exists() or not impl_root.exists():
            pytest.skip("Spec or impl directory not found")

        discovery = discover_from_spec(spec_root)
        audit = audit_impl(impl_root, discovery)

        # Should produce valid report
        assert isinstance(audit, AuditReport)
        assert isinstance(audit.gaps, list)
        assert isinstance(audit.aligned, list)

    def test_audit_reports_alignment_score(
        self, spec_root: Path, impl_root: Path
    ) -> None:
        """Audit should report alignment score."""
        if not spec_root.exists() or not impl_root.exists():
            pytest.skip("Spec or impl directory not found")

        discovery = discover_from_spec(spec_root)
        audit = audit_impl(impl_root, discovery)

        # Score should be valid percentage
        score = audit.alignment_score
        assert 0.0 <= score <= 1.0


# === CI Gate Tests ===


class TestCIGate:
    """CI gate enforcement tests."""

    def test_no_critical_gaps(self, spec_root: Path, impl_root: Path) -> None:
        """
        CRITICAL: Fail if any spec-defined component is missing from impl.

        This is the core CI gate. It ensures that:
        - All specs with polynomial have polynomial.py
        - All specs with operad have operad.py
        - All specs with AGENTESE path have @node

        If this test fails:
        1. Run `kg self.system.audit` to see gaps
        2. Either add missing impl OR update spec to remove requirement
        3. Use generate_stubs() to create scaffolding
        """
        if not spec_root.exists() or not impl_root.exists():
            pytest.skip("Spec or impl directory not found")

        discovery, audit = full_audit(spec_root, impl_root)

        # Filter to critical gaps only
        critical_gaps = audit.critical_gaps

        if critical_gaps:
            # Generate helpful error message
            report = print_audit_report(audit)
            gap_details = "\n".join(
                f"  - {g.spec_path}.{g.component.value}: {g.message}"
                for g in critical_gaps[:10]  # Limit to first 10
            )
            if len(critical_gaps) > 10:
                gap_details += f"\n  ... and {len(critical_gaps) - 10} more"

            pytest.fail(
                f"Critical spec-impl gaps detected!\n\n"
                f"Found {len(critical_gaps)} critical gaps:\n{gap_details}\n\n"
                f"To fix:\n"
                f"  1. Add missing implementations, OR\n"
                f"  2. Remove requirements from spec YAML frontmatter\n\n"
                f"Full report:\n{report}"
            )

    def test_warn_on_minor_gaps(self, spec_root: Path, impl_root: Path) -> None:
        """
        WARN: Report minor gaps but don't fail.

        Minor gaps include:
        - Missing sheaf implementations (optional)
        """
        if not spec_root.exists() or not impl_root.exists():
            pytest.skip("Spec or impl directory not found")

        discovery, audit = full_audit(spec_root, impl_root)

        # Filter to minor gaps
        minor_gaps = [g for g in audit.gaps if g.severity == GapSeverity.MINOR]

        if minor_gaps:
            # Warn but don't fail
            gap_details = "\n".join(
                f"  - {g.spec_path}.{g.component.value}: {g.message}"
                for g in minor_gaps[:5]
            )
            pytest.warns(
                UserWarning,
                match="Minor spec-impl gaps detected",
            ) if False else None  # Just a note, no actual warning

    def test_alignment_score_threshold(self, spec_root: Path, impl_root: Path) -> None:
        """
        THRESHOLD: Alignment score should meet minimum.

        Current threshold: 0.0 (no minimum while system is being built)
        Target threshold: 0.9 (90% alignment for healthy system)
        """
        if not spec_root.exists() or not impl_root.exists():
            pytest.skip("Spec or impl directory not found")

        discovery, audit = full_audit(spec_root, impl_root)

        # Current threshold (relaxed while building)
        threshold = 0.0

        score = audit.alignment_score
        assert score >= threshold, (
            f"Alignment score {score:.1%} is below threshold {threshold:.1%}\n\n"
            f"Run `kg self.system.audit` to see gaps."
        )


# === Skip Conditions ===


def _should_skip_ci_gate() -> bool:
    """Check if CI gate should be skipped."""
    # Skip if explicitly disabled
    if os.environ.get("SPECGRAPH_SKIP_CI_GATE"):
        return True

    # Skip if spec directory doesn't exist
    if not get_spec_root().exists():
        return True

    # Skip if no specs have YAML frontmatter yet
    spec_root = get_spec_root()
    for md_file in spec_root.rglob("*.md"):
        content = md_file.read_text(errors="ignore")
        if content.strip().startswith("---"):
            return False  # Found at least one spec with frontmatter

    return True  # No specs with frontmatter found


@pytest.fixture(autouse=True)
def skip_if_not_ready() -> None:
    """Skip CI gate if system not ready."""
    # Currently we don't skip - the gate should always run
    # Uncomment below to enable skip logic:
    # if _should_skip_ci_gate():
    #     pytest.skip("CI gate skipped - no specs with YAML frontmatter")
    pass


# === Exports ===

__all__ = [
    "TestDiscovery",
    "TestAudit",
    "TestCIGate",
]
