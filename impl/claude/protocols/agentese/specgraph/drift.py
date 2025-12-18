"""
SpecGraph Drift Detection: Compare spec vs impl.

Drift detection compares:
1. Reflected impl (what exists in code)
2. Parsed spec (what should exist per spec)

Returns DriftReport with status:
- ALIGNED: Spec and impl match
- DIVERGED: Spec and impl differ
- MISSING_SPEC: Impl exists without spec
- MISSING_IMPL: Spec exists without impl
- PARTIAL: Some components missing

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

from pathlib import Path

from .parser import parse_spec_file
from .reflect import reflect_impl
from .types import (
    DriftReport,
    DriftStatus,
    SpecNode,
)


def _compare_polynomials(spec: SpecNode, impl: SpecNode) -> list[str]:
    """Compare polynomial specs and return differences."""
    diffs = []

    if spec.polynomial and not impl.polynomial:
        diffs.append("polynomial: missing in impl")
    elif not spec.polynomial and impl.polynomial:
        diffs.append("polynomial: extra in impl (not in spec)")
    elif spec.polynomial and impl.polynomial:
        spec_pos = set(spec.polynomial.positions)
        impl_pos = set(impl.polynomial.positions)
        if spec_pos != impl_pos:
            missing = spec_pos - impl_pos
            extra = impl_pos - spec_pos
            if missing:
                diffs.append(f"polynomial.positions: missing {missing}")
            if extra:
                diffs.append(f"polynomial.positions: extra {extra}")

    return diffs


def _compare_operads(spec: SpecNode, impl: SpecNode) -> list[str]:
    """Compare operad specs and return differences."""
    diffs = []

    if spec.operad and not impl.operad:
        diffs.append("operad: missing in impl")
    elif not spec.operad and impl.operad:
        diffs.append("operad: extra in impl (not in spec)")
    elif spec.operad and impl.operad:
        spec_ops = {op.name for op in spec.operad.operations}
        impl_ops = {op.name for op in impl.operad.operations}
        missing = spec_ops - impl_ops
        extra = impl_ops - spec_ops
        if missing:
            diffs.append(f"operad.operations: missing {missing}")
        if extra:
            diffs.append(f"operad.operations: extra {extra}")

        spec_laws = {law.name for law in spec.operad.laws}
        impl_laws = {law.name for law in impl.operad.laws}
        missing_laws = spec_laws - impl_laws
        extra_laws = impl_laws - spec_laws
        if missing_laws:
            diffs.append(f"operad.laws: missing {missing_laws}")
        if extra_laws:
            diffs.append(f"operad.laws: extra {extra_laws}")

    return diffs


def _compare_agentese(spec: SpecNode, impl: SpecNode) -> list[str]:
    """Compare AGENTESE path specs and return differences."""
    diffs = []

    if spec.agentese and not impl.agentese:
        diffs.append("agentese: missing in impl (no @node)")
    elif not spec.agentese and impl.agentese:
        diffs.append("agentese: extra in impl (not in spec)")
    elif spec.agentese and impl.agentese:
        if spec.agentese.path != impl.agentese.path:
            diffs.append(
                f"agentese.path: spec={spec.agentese.path}, impl={impl.agentese.path}"
            )

        spec_aspects = set(spec.agentese.aspects)
        impl_aspects = set(impl.agentese.aspects)
        missing = spec_aspects - impl_aspects
        extra = impl_aspects - spec_aspects
        if missing:
            diffs.append(f"agentese.aspects: missing {missing}")
        if extra:
            diffs.append(f"agentese.aspects: extra {extra}")

    return diffs


def check_drift(
    spec_path: Path | None,
    impl_path: Path | None,
) -> DriftReport:
    """
    Check drift between spec and impl.

    Args:
        spec_path: Path to spec markdown file (may be None)
        impl_path: Path to impl directory (may be None)

    Returns:
        DriftReport with status and details
    """
    # Handle missing cases
    if not spec_path and not impl_path:
        return DriftReport(
            module="unknown",
            status=DriftStatus.UNKNOWN,
            details="Both spec and impl paths are None",
        )

    if not spec_path or not spec_path.exists():
        if impl_path and impl_path.exists():
            return DriftReport(
                module=impl_path.name,
                status=DriftStatus.MISSING_SPEC,
                impl_path=str(impl_path),
                details="Impl exists without spec file",
            )
        return DriftReport(
            module="unknown",
            status=DriftStatus.UNKNOWN,
            details="Spec path not found",
        )

    if not impl_path or not impl_path.exists():
        return DriftReport(
            module=spec_path.stem,
            status=DriftStatus.MISSING_IMPL,
            spec_path=str(spec_path),
            details="Spec exists without impl directory",
        )

    # Parse spec
    try:
        spec_node = parse_spec_file(spec_path)
    except Exception as e:
        return DriftReport(
            module=spec_path.stem,
            status=DriftStatus.UNKNOWN,
            spec_path=str(spec_path),
            details=f"Failed to parse spec: {e}",
        )

    # Reflect impl
    reflect_result = reflect_impl(impl_path)
    if not reflect_result.spec_node:
        return DriftReport(
            module=impl_path.name,
            status=DriftStatus.PARTIAL,
            spec_path=str(spec_path),
            impl_path=str(impl_path),
            details="Failed to reflect impl structure",
        )

    impl_node = reflect_result.spec_node

    # Compare components
    all_diffs: list[str] = []
    all_diffs.extend(_compare_polynomials(spec_node, impl_node))
    all_diffs.extend(_compare_operads(spec_node, impl_node))
    all_diffs.extend(_compare_agentese(spec_node, impl_node))

    # Determine status
    if not all_diffs:
        status = DriftStatus.ALIGNED
        details = "Spec and impl are aligned"
    else:
        # Check if it's partial or diverged
        missing = [d for d in all_diffs if "missing" in d.lower()]
        extra = [d for d in all_diffs if "extra" in d.lower()]

        if missing and not extra:
            status = DriftStatus.PARTIAL
            details = f"Impl missing components: {len(missing)} issues"
        else:
            status = DriftStatus.DIVERGED
            details = f"Spec-impl divergence: {len(all_diffs)} issues"

    return DriftReport(
        module=spec_node.holon,
        status=status,
        spec_path=str(spec_path),
        impl_path=str(impl_path),
        missing_components=[d for d in all_diffs if "missing" in d],
        extra_components=[d for d in all_diffs if "extra" in d],
        details=details,
    )


def audit_all_jewels(
    spec_root: Path,
    impl_root: Path,
) -> list[DriftReport]:
    """
    Audit all Crown Jewels for drift.

    Args:
        spec_root: Root of spec directory
        impl_root: Root of impl directory

    Returns:
        List of DriftReports for each jewel
    """
    # Map jewel names to paths
    jewel_mappings = [
        ("town", spec_root / "town", impl_root / "agents" / "town"),
        (
            "brain",
            spec_root / "d-gents" / "persistence.md",
            impl_root / "agents" / "brain",
        ),
        ("atelier", spec_root / "a-gents" / "art", impl_root / "agents" / "atelier"),
        ("park", spec_root / "town" / "operad.md", impl_root / "agents" / "park"),
        ("gestalt", spec_root / "g-gents", impl_root / "agents" / "gestalt"),
        ("flow", spec_root / "c-gents" / "composition.md", impl_root / "agents" / "f"),
    ]

    reports = []
    for name, spec_path, impl_path in jewel_mappings:
        # Find spec file (may be directory or file)
        if spec_path.is_dir():
            # Look for main spec file
            for candidate in ["operad.md", "README.md", f"{name}.md"]:
                candidate_path = spec_path / candidate
                if candidate_path.exists():
                    spec_path = candidate_path
                    break

        report = check_drift(
            spec_path if spec_path.exists() else None,
            impl_path if impl_path.exists() else None,
        )
        reports.append(report)

    return reports


# === Exports ===

__all__ = [
    "DriftStatus",
    "check_drift",
    "audit_all_jewels",
]
