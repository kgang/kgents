"""
Tests for SpecGraph Discovery Mode (Option C).

Tests the hybrid spec-driven discovery workflow:
1. discover_from_spec() - Parse all specs with YAML frontmatter
2. audit_impl() - Compare what exists vs what spec says should exist
3. generate_stubs() - Generate stubs only for missing components
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ..discovery import (
    AuditReport,
    ComponentType,
    DiscoveryReport,
    Gap,
    GapSeverity,
    StubResult,
    audit_impl,
    discover_from_spec,
    full_audit,
    generate_stubs,
    print_audit_report,
)
from ..types import (
    AgentesePath,
    OperadSpec,
    OperationSpec,
    PolynomialSpec,
    SpecDomain,
    SpecGraph,
    SpecNode,
)

# === Discovery Tests ===


class TestDiscoverFromSpec:
    """Tests for discover_from_spec()."""

    def test_discover_empty_directory(self, tmp_path: Path) -> None:
        """Discover from empty directory returns empty report."""
        spec_root = tmp_path / "spec"
        spec_root.mkdir()

        report = discover_from_spec(spec_root)

        assert report.total_specs == 0
        assert report.specs_with_polynomial == 0
        assert report.specs_with_operad == 0
        assert report.specs_with_node == 0

    def test_discover_with_polynomial_spec(self, tmp_path: Path) -> None:
        """Discover finds specs with polynomial."""
        spec_root = tmp_path / "spec"
        spec_root.mkdir()

        spec_file = spec_root / "test.md"
        spec_file.write_text("""---
domain: world
holon: test
polynomial:
  positions: [idle, active]
  transition: test_transition
---
# Test Spec
""")

        report = discover_from_spec(spec_root)

        assert report.total_specs == 1
        assert report.specs_with_polynomial == 1

    def test_discover_counts_domains(self, tmp_path: Path) -> None:
        """Discover counts specs by domain."""
        spec_root = tmp_path / "spec"
        spec_root.mkdir()

        # World domain spec
        world_spec = spec_root / "world.md"
        world_spec.write_text("""---
domain: world
holon: world_test
---
""")

        # Self domain spec
        self_spec = spec_root / "self.md"
        self_spec.write_text("""---
domain: self
holon: self_test
---
""")

        report = discover_from_spec(spec_root)

        assert report.total_specs == 2
        assert report.domains[SpecDomain.WORLD] == 1
        assert report.domains[SpecDomain.SELF] == 1


# === Audit Tests ===


class TestAuditImpl:
    """Tests for audit_impl()."""

    def test_audit_empty_discovery(self, tmp_path: Path) -> None:
        """Audit with no specs returns empty report."""
        impl_root = tmp_path / "impl"
        impl_root.mkdir()

        discovery = DiscoveryReport(
            spec_graph=SpecGraph(nodes={}),
            total_specs=0,
        )

        audit = audit_impl(impl_root, discovery)

        assert len(audit.gaps) == 0
        assert len(audit.aligned) == 0
        assert audit.alignment_score == 1.0

    def test_audit_finds_missing_polynomial(self, tmp_path: Path) -> None:
        """Audit detects missing polynomial.py."""
        impl_root = tmp_path / "impl"
        (impl_root / "agents" / "test").mkdir(parents=True)

        spec_node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/test.md"),
            polynomial=PolynomialSpec(
                positions=("idle", "active"),
                transition_fn="test_transition",
            ),
        )

        discovery = DiscoveryReport(
            spec_graph=SpecGraph(nodes={"world.test": spec_node}),
            total_specs=1,
            specs_with_polynomial=1,
        )

        audit = audit_impl(impl_root, discovery)

        assert len(audit.gaps) == 1
        gap = audit.gaps[0]
        assert gap.component == ComponentType.POLYNOMIAL
        assert gap.severity == GapSeverity.CRITICAL

    def test_audit_finds_aligned_polynomial(self, tmp_path: Path) -> None:
        """Audit detects aligned polynomial.py."""
        impl_root = tmp_path / "impl"
        impl_dir = impl_root / "agents" / "test"
        impl_dir.mkdir(parents=True)

        # Create polynomial.py
        poly_file = impl_dir / "polynomial.py"
        poly_file.write_text("""
from enum import Enum, auto

class TestPhase(Enum):
    IDLE = auto()
    ACTIVE = auto()
""")

        spec_node = SpecNode(
            domain=SpecDomain.WORLD,
            holon="test",
            source_path=Path("spec/test.md"),
            polynomial=PolynomialSpec(
                positions=("idle", "active"),
                transition_fn="test_transition",
            ),
        )

        discovery = DiscoveryReport(
            spec_graph=SpecGraph(nodes={"world.test": spec_node}),
            total_specs=1,
            specs_with_polynomial=1,
        )

        audit = audit_impl(impl_root, discovery)

        assert "world.test.polynomial" in audit.aligned


# === Gap Tests ===


class TestGap:
    """Tests for Gap dataclass."""

    def test_gap_attributes(self) -> None:
        """Gap has correct attributes."""
        gap = Gap(
            spec_path="world.test",
            component=ComponentType.POLYNOMIAL,
            severity=GapSeverity.CRITICAL,
            message="polynomial.py missing",
        )

        assert gap.spec_path == "world.test"
        assert gap.component == ComponentType.POLYNOMIAL
        assert gap.severity == GapSeverity.CRITICAL


class TestAuditReport:
    """Tests for AuditReport."""

    def test_has_gaps(self) -> None:
        """has_gaps property works."""
        report = AuditReport(gaps=[], aligned=[])
        assert not report.has_gaps

        report = AuditReport(
            gaps=[
                Gap(
                    spec_path="test",
                    component=ComponentType.POLYNOMIAL,
                    severity=GapSeverity.CRITICAL,
                    message="missing",
                )
            ],
            aligned=[],
        )
        assert report.has_gaps

    def test_critical_gaps_filter(self) -> None:
        """critical_gaps filters correctly."""
        report = AuditReport(
            gaps=[
                Gap(
                    spec_path="test1",
                    component=ComponentType.POLYNOMIAL,
                    severity=GapSeverity.CRITICAL,
                    message="missing",
                ),
                Gap(
                    spec_path="test2",
                    component=ComponentType.SHEAF,
                    severity=GapSeverity.MINOR,
                    message="missing",
                ),
            ],
            aligned=[],
        )

        assert len(report.critical_gaps) == 1
        assert report.critical_gaps[0].severity == GapSeverity.CRITICAL

    def test_alignment_score(self) -> None:
        """alignment_score calculates correctly."""
        report = AuditReport(
            gaps=[],
            aligned=["a", "b", "c"],
            total_components=4,
        )

        assert report.alignment_score == 0.75


# === Generate Stubs Tests ===


class TestGenerateStubs:
    """Tests for generate_stubs()."""

    def test_generate_stubs_empty(self, tmp_path: Path) -> None:
        """Generate stubs with no gaps returns empty result."""
        result = generate_stubs([], tmp_path, dry_run=True)

        assert result.gaps_addressed == 0
        assert len(result.files_generated) == 0

    def test_generate_stubs_dry_run(self, tmp_path: Path) -> None:
        """Generate stubs in dry run mode doesn't write files."""
        gap = Gap(
            spec_path="world.test",
            component=ComponentType.POLYNOMIAL,
            severity=GapSeverity.CRITICAL,
            message="missing",
            spec_file=tmp_path / "spec" / "test.md",
            impl_dir=tmp_path / "agents" / "test",
        )

        # Create spec file
        spec_dir = tmp_path / "spec"
        spec_dir.mkdir()
        spec_file = spec_dir / "test.md"
        spec_file.write_text("""---
domain: world
holon: test
polynomial:
  positions: [idle, active]
  transition: test_transition
---
""")

        result = generate_stubs([gap], tmp_path, dry_run=True)

        # Files should be listed but not created
        assert any("polynomial" in f for f in result.files_generated)
        impl_dir = tmp_path / "agents" / "test"
        assert not impl_dir.exists() or not (impl_dir / "polynomial.py").exists()


# === Print Report Tests ===


class TestPrintAuditReport:
    """Tests for print_audit_report()."""

    def test_print_empty_report(self) -> None:
        """Print empty report shows success."""
        report = AuditReport(gaps=[], aligned=[])
        output = print_audit_report(report)

        assert "SPECGRAPH AUDIT REPORT" in output
        assert "No gaps found" in output

    def test_print_report_with_gaps(self) -> None:
        """Print report with gaps shows details."""
        report = AuditReport(
            gaps=[
                Gap(
                    spec_path="world.test",
                    component=ComponentType.POLYNOMIAL,
                    severity=GapSeverity.CRITICAL,
                    message="polynomial.py missing",
                ),
            ],
            aligned=[],
            total_components=1,
            missing_components=1,
        )
        output = print_audit_report(report)

        assert "SPECGRAPH AUDIT REPORT" in output
        assert "world.test" in output
        assert "CRITICAL" in output


# === Integration Tests ===


class TestFullAudit:
    """Integration tests for full_audit()."""

    def test_full_audit(self, tmp_path: Path) -> None:
        """Full audit combines discover and audit."""
        spec_root = tmp_path / "spec"
        impl_root = tmp_path / "impl"
        spec_root.mkdir()
        impl_root.mkdir()

        discovery, audit = full_audit(spec_root, impl_root)

        assert isinstance(discovery, DiscoveryReport)
        assert isinstance(audit, AuditReport)
