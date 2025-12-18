"""
SpecGraph Discovery: Spec-Driven Gap Detection and Stub Generation.

The Discovery module implements Option C: Hybrid Spec-Driven Discovery.
Instead of generating everything from spec, it:
1. Discovers what SHOULD exist according to specs
2. Audits what DOES exist in impl
3. Generates stubs only for MISSING components

The autopoietic invariant becomes:
    audit_impl(impl/, discover_from_spec(spec/)) = no_gaps

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .compile import compile_spec
from .parser import parse_spec_directory, parse_spec_file
from .reflect import reflect_impl, reflect_node, reflect_operad, reflect_polynomial
from .types import (
    CompileResult,
    SpecDomain,
    SpecGraph,
    SpecNode,
)

# === Discovery Types ===


class GapSeverity(str, Enum):
    """Severity of a spec-impl gap."""

    CRITICAL = "critical"  # Core component missing (polynomial, operad)
    IMPORTANT = "important"  # Discoverability missing (node)
    MINOR = "minor"  # Optional component missing (sheaf)


class ComponentType(str, Enum):
    """Types of components that can have gaps."""

    POLYNOMIAL = "polynomial"
    OPERAD = "operad"
    NODE = "node"
    SHEAF = "sheaf"
    SERVICE = "service"


@dataclass(frozen=True)
class Gap:
    """A gap between what spec defines and what impl provides."""

    spec_path: str  # AGENTESE path (e.g., "world.town")
    component: ComponentType
    severity: GapSeverity
    message: str
    spec_file: Path | None = None
    impl_dir: Path | None = None


@dataclass
class DiscoveryReport:
    """Report of what specs define should exist."""

    spec_graph: SpecGraph
    total_specs: int = 0
    specs_with_polynomial: int = 0
    specs_with_operad: int = 0
    specs_with_node: int = 0
    specs_with_sheaf: int = 0
    domains: dict[SpecDomain, int] = field(default_factory=dict)


@dataclass
class AuditReport:
    """Report of gaps between spec and impl."""

    gaps: list[Gap] = field(default_factory=list)
    aligned: list[str] = field(default_factory=list)  # Paths that are aligned
    total_components: int = 0
    missing_components: int = 0
    extra_components: int = 0  # Impl has but spec doesn't define

    @property
    def has_gaps(self) -> bool:
        return len(self.gaps) > 0

    @property
    def critical_gaps(self) -> list[Gap]:
        return [g for g in self.gaps if g.severity == GapSeverity.CRITICAL]

    @property
    def alignment_score(self) -> float:
        """Percentage of components that are aligned (0.0 - 1.0)."""
        if self.total_components == 0:
            return 1.0
        return len(self.aligned) / self.total_components


@dataclass
class StubResult:
    """Result of generating stubs for gaps."""

    gaps_addressed: int = 0
    files_generated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)  # Already exists


# === Discovery Functions ===


def discover_from_spec(spec_root: Path) -> DiscoveryReport:
    """
    Parse all specs with YAML frontmatter.

    Returns what SHOULD exist according to spec.

    Args:
        spec_root: Root of spec directory (e.g., kgents/spec/)

    Returns:
        DiscoveryReport with parsed specs and statistics
    """
    graph = parse_spec_directory(spec_root)

    report = DiscoveryReport(
        spec_graph=graph,
        total_specs=len(graph.nodes),
        domains={d: 0 for d in SpecDomain},
    )

    for node in graph.nodes.values():
        # Count by domain
        report.domains[node.domain] = report.domains.get(node.domain, 0) + 1

        # Count by component
        if node.has_polynomial:
            report.specs_with_polynomial += 1
        if node.has_operad:
            report.specs_with_operad += 1
        if node.agentese:
            report.specs_with_node += 1
        if node.has_sheaf:
            report.specs_with_sheaf += 1

    return report


def _resolve_impl_paths(spec_node: SpecNode, impl_root: Path) -> list[Path]:
    """
    Resolve all candidate implementation paths for a spec node.

    Crown Jewels can live in either agents/ or services/:
    - agents/<holon>/ - polynomial, operad, state logic
    - services/<holon>/ - node.py, service facades

    Returns:
        List of candidate paths (first existing wins in audit)
    """
    holon = spec_node.holon
    candidates: list[Path] = []

    if spec_node.domain == SpecDomain.WORLD:
        # World domain: check both agents/ and services/
        candidates = [
            impl_root / "agents" / holon,
            impl_root / "services" / holon,
        ]
    elif spec_node.domain == SpecDomain.SELF:
        # self.memory -> agents/brain (special case)
        if holon == "memory":
            candidates = [impl_root / "agents" / "brain"]
        else:
            candidates = [
                impl_root / "services" / holon,
                impl_root / "agents" / holon,
            ]
    elif spec_node.domain == SpecDomain.CONCEPT:
        candidates = [impl_root / "protocols" / "agentese" / "contexts"]
    elif spec_node.domain == SpecDomain.TIME:
        candidates = [impl_root / "agents" / "n"]  # N-gent for time
    else:
        candidates = [
            impl_root / "agents" / holon,
            impl_root / "services" / holon,
        ]

    return candidates


def _find_component_file(
    candidates: list[Path],
    filename: str,
) -> Path | None:
    """
    Find a component file across candidate directories.

    Returns the first existing file path, or None if not found.
    """
    for candidate in candidates:
        file_path = candidate / filename
        if file_path.exists():
            return file_path
    return None


def audit_impl(
    impl_root: Path,
    discovery: DiscoveryReport,
) -> AuditReport:
    """
    Compare what exists vs what spec says should exist.

    Args:
        impl_root: Root of impl directory (e.g., impl/claude/)
        discovery: Discovery report from discover_from_spec()

    Returns:
        AuditReport with gaps and alignment status
    """
    report = AuditReport()

    for spec_path, spec_node in discovery.spec_graph.nodes.items():
        # Resolve candidate impl locations (Crown Jewels can span agents/ + services/)
        impl_candidates = _resolve_impl_paths(spec_node, impl_root)
        # Use first candidate for gap reporting (primary location)
        primary_impl_path = impl_candidates[0] if impl_candidates else impl_root

        # Check polynomial
        if spec_node.has_polynomial and spec_node.polynomial is not None:
            report.total_components += 1
            poly_file = _find_component_file(impl_candidates, "polynomial.py")
            position_count = len(spec_node.polynomial.positions)
            if poly_file:
                impl_poly = reflect_polynomial(poly_file)
                if impl_poly:
                    report.aligned.append(f"{spec_path}.polynomial")
                else:
                    report.gaps.append(
                        Gap(
                            spec_path=spec_path,
                            component=ComponentType.POLYNOMIAL,
                            severity=GapSeverity.CRITICAL,
                            message="polynomial.py exists but structure not extractable",
                            spec_file=spec_node.source_path,
                            impl_dir=poly_file.parent,
                        )
                    )
            else:
                report.gaps.append(
                    Gap(
                        spec_path=spec_path,
                        component=ComponentType.POLYNOMIAL,
                        severity=GapSeverity.CRITICAL,
                        message=f"polynomial.py missing (spec defines {position_count} positions)",
                        spec_file=spec_node.source_path,
                        impl_dir=primary_impl_path,
                    )
                )
                report.missing_components += 1

        # Check operad
        if spec_node.has_operad and spec_node.operad is not None:
            report.total_components += 1
            operad_file = _find_component_file(impl_candidates, "operad.py")
            op_count = len(spec_node.operad.operations)
            law_count = len(spec_node.operad.laws)
            if operad_file:
                impl_operad = reflect_operad(operad_file)
                if impl_operad:
                    report.aligned.append(f"{spec_path}.operad")
                else:
                    report.gaps.append(
                        Gap(
                            spec_path=spec_path,
                            component=ComponentType.OPERAD,
                            severity=GapSeverity.CRITICAL,
                            message="operad.py exists but structure not extractable",
                            spec_file=spec_node.source_path,
                            impl_dir=operad_file.parent,
                        )
                    )
            else:
                report.gaps.append(
                    Gap(
                        spec_path=spec_path,
                        component=ComponentType.OPERAD,
                        severity=GapSeverity.CRITICAL,
                        message=f"operad.py missing (spec defines {op_count} operations, {law_count} laws)",
                        spec_file=spec_node.source_path,
                        impl_dir=primary_impl_path,
                    )
                )
                report.missing_components += 1

        # Check node
        if spec_node.agentese:
            report.total_components += 1
            node_file = _find_component_file(impl_candidates, "node.py")
            if node_file:
                impl_node = reflect_node(node_file)
                if impl_node:
                    report.aligned.append(f"{spec_path}.node")
                else:
                    report.gaps.append(
                        Gap(
                            spec_path=spec_path,
                            component=ComponentType.NODE,
                            severity=GapSeverity.IMPORTANT,
                            message="node.py exists but @node decorator not found",
                            spec_file=spec_node.source_path,
                            impl_dir=node_file.parent,
                        )
                    )
            else:
                aspect_count = len(spec_node.agentese.aspects)
                report.gaps.append(
                    Gap(
                        spec_path=spec_path,
                        component=ComponentType.NODE,
                        severity=GapSeverity.IMPORTANT,
                        message=f"node.py missing (spec defines path {spec_node.agentese.path} with {aspect_count} aspects)",
                        spec_file=spec_node.source_path,
                        impl_dir=primary_impl_path,
                    )
                )
                report.missing_components += 1

        # Check sheaf (optional)
        if spec_node.has_sheaf:
            report.total_components += 1
            sheaf_file = _find_component_file(impl_candidates, "sheaf.py")
            if sheaf_file:
                report.aligned.append(f"{spec_path}.sheaf")
            else:
                report.gaps.append(
                    Gap(
                        spec_path=spec_path,
                        component=ComponentType.SHEAF,
                        severity=GapSeverity.MINOR,
                        message="sheaf.py missing (spec defines gluing function)",
                        spec_file=spec_node.source_path,
                        impl_dir=primary_impl_path,
                    )
                )
                report.missing_components += 1

    return report


def generate_stubs(
    gaps: list[Gap],
    impl_root: Path,
    dry_run: bool = True,
) -> StubResult:
    """
    Generate stubs only for MISSING components.

    Existing files are never touched.

    Args:
        gaps: List of gaps from audit_impl()
        impl_root: Root of impl directory
        dry_run: If True, don't write files

    Returns:
        StubResult with what was generated
    """
    result = StubResult()

    # Group gaps by spec path to avoid duplicate compilation
    gaps_by_path: dict[str, list[Gap]] = {}
    for gap in gaps:
        if gap.spec_path not in gaps_by_path:
            gaps_by_path[gap.spec_path] = []
        gaps_by_path[gap.spec_path].append(gap)

    for spec_path, path_gaps in gaps_by_path.items():
        # Get the spec file from the first gap
        spec_file = path_gaps[0].spec_file
        if not spec_file or not spec_file.exists():
            result.errors.append(f"Spec file not found for {spec_path}")
            continue

        try:
            spec_node = parse_spec_file(spec_file)
        except Exception as e:
            result.errors.append(f"Failed to parse {spec_file}: {e}")
            continue

        # Check which components need generation
        needs_polynomial = any(
            g.component == ComponentType.POLYNOMIAL for g in path_gaps
        )
        needs_operad = any(g.component == ComponentType.OPERAD for g in path_gaps)
        needs_node = any(g.component == ComponentType.NODE for g in path_gaps)

        # Create a partial spec node with only what's needed
        partial_node = SpecNode(
            domain=spec_node.domain,
            holon=spec_node.holon,
            source_path=spec_node.source_path,
            polynomial=spec_node.polynomial if needs_polynomial else None,
            operad=spec_node.operad if needs_operad else None,
            agentese=spec_node.agentese if needs_node else None,
        )

        # Skip if nothing to generate
        if not needs_polynomial and not needs_operad and not needs_node:
            result.skipped.append(spec_path)
            continue

        # Compile the partial node
        compile_result = compile_spec(partial_node, impl_root, dry_run=dry_run)

        if compile_result.success:
            result.gaps_addressed += len(path_gaps)
            result.files_generated.extend(compile_result.generated_files)
        else:
            result.errors.extend(compile_result.errors)

    return result


# === Convenience Functions ===


def full_audit(
    spec_root: Path,
    impl_root: Path,
) -> tuple[DiscoveryReport, AuditReport]:
    """
    Perform full discovery and audit in one call.

    Args:
        spec_root: Root of spec directory
        impl_root: Root of impl directory

    Returns:
        Tuple of (DiscoveryReport, AuditReport)
    """
    discovery = discover_from_spec(spec_root)
    audit = audit_impl(impl_root, discovery)
    return discovery, audit


def print_audit_report(audit: AuditReport, verbose: bool = False) -> str:
    """
    Format audit report as human-readable string.

    Args:
        audit: The audit report to format
        verbose: If True, include file paths and additional details

    Returns:
        Formatted string suitable for terminal output
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("SPECGRAPH AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Summary section
    lines.append("📊 SUMMARY")
    lines.append("-" * 40)
    lines.append(f"   Total components specified: {audit.total_components}")
    lines.append(f"   Aligned: {len(audit.aligned)} ({audit.alignment_score:.1%})")
    lines.append(f"   Missing: {audit.missing_components}")
    lines.append(f"   Critical gaps: {len(audit.critical_gaps)}")
    lines.append("")

    if audit.gaps:
        # Group gaps by severity
        critical = [g for g in audit.gaps if g.severity == GapSeverity.CRITICAL]
        important = [g for g in audit.gaps if g.severity == GapSeverity.IMPORTANT]
        minor = [g for g in audit.gaps if g.severity == GapSeverity.MINOR]

        if critical:
            lines.append("🔴 CRITICAL GAPS (blocking)")
            lines.append("-" * 40)
            for gap in critical:
                lines.append(f"   {gap.spec_path}.{gap.component.value}")
                lines.append(f"      → {gap.message}")
                if verbose and gap.spec_file:
                    lines.append(f"      spec: {gap.spec_file}")
                if verbose and gap.impl_dir:
                    lines.append(f"      impl: {gap.impl_dir}")
            lines.append("")

        if important:
            lines.append("🟡 IMPORTANT GAPS (recommended)")
            lines.append("-" * 40)
            for gap in important:
                lines.append(f"   {gap.spec_path}.{gap.component.value}")
                lines.append(f"      → {gap.message}")
                if verbose and gap.spec_file:
                    lines.append(f"      spec: {gap.spec_file}")
            lines.append("")

        if minor:
            lines.append("⚪ MINOR GAPS (optional)")
            lines.append("-" * 40)
            for gap in minor:
                lines.append(f"   {gap.spec_path}.{gap.component.value}")
                lines.append(f"      → {gap.message}")
            lines.append("")

        # Actionable guidance
        lines.append("💡 TO FIX")
        lines.append("-" * 40)
        lines.append("   1. Add missing implementations, OR")
        lines.append("   2. Remove requirements from spec YAML frontmatter")
        lines.append(
            "   3. Run `generate_stubs(audit.gaps, impl_root)` for scaffolding"
        )
        lines.append("")
    else:
        lines.append("✅ No gaps found! Spec and impl are aligned.")
        lines.append("")

    # Aligned components (verbose mode only)
    if verbose and audit.aligned:
        lines.append("✅ ALIGNED COMPONENTS")
        lines.append("-" * 40)
        for aligned in sorted(audit.aligned)[:10]:
            lines.append(f"   {aligned}")
        if len(audit.aligned) > 10:
            lines.append(f"   ... and {len(audit.aligned) - 10} more")
        lines.append("")

    return "\n".join(lines)


# === Exports ===

__all__ = [
    # Types
    "GapSeverity",
    "ComponentType",
    "Gap",
    "DiscoveryReport",
    "AuditReport",
    "StubResult",
    # Functions
    "discover_from_spec",
    "audit_impl",
    "generate_stubs",
    "full_audit",
    "print_audit_report",
]
