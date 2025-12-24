"""
Drift Detection: Compare spec against implementation.

Uses the existing SpecGraph drift detection from protocols.agentese.specgraph.

This module integrates SpecGraph's drift checking with the audit service,
converting SpecGraph's DriftReport into our AuditResult format.

See: protocols/agentese/specgraph/drift.py
"""

from __future__ import annotations

from pathlib import Path

from protocols.agentese.specgraph.drift import check_drift as specgraph_check_drift
from protocols.agentese.specgraph.types import DriftStatus

from .types import AuditSeverity, DriftItem


def detect_drift(
    spec_path: Path,
    impl_path: Path | None = None,
) -> list[DriftItem]:
    """
    Detect drift between spec and implementation.

    Args:
        spec_path: Path to spec markdown file
        impl_path: Path to implementation directory (auto-inferred if None)

    Returns:
        List of DriftItems found

    Note:
        If impl_path is None, will attempt to infer from spec_path:
        - spec/agents/x/y.md -> impl/claude/agents/x/y/
        - spec/protocols/x.md -> impl/claude/protocols/x/
    """
    # Auto-infer impl path if not provided
    if impl_path is None:
        impl_path = _infer_impl_path(spec_path)

    # Use SpecGraph drift detection
    drift_report = specgraph_check_drift(spec_path, impl_path)

    # Convert to DriftItems
    items: list[DriftItem] = []

    # Handle missing spec/impl cases
    if drift_report.status == DriftStatus.MISSING_SPEC:
        items.append(
            DriftItem(
                component="spec",
                spec_says="Spec should exist",
                impl_does="Impl exists without spec",
                severity=AuditSeverity.ERROR,
            )
        )
        return items

    if drift_report.status == DriftStatus.MISSING_IMPL:
        items.append(
            DriftItem(
                component="implementation",
                spec_says="Implementation should exist",
                impl_does="No implementation found",
                severity=AuditSeverity.WARNING,
            )
        )
        return items

    # Convert missing components
    for comp in drift_report.missing_components:
        items.append(
            DriftItem(
                component=comp.split(":")[0].strip(),
                spec_says=comp,
                impl_does="Missing in implementation",
                severity=AuditSeverity.ERROR,
            )
        )

    # Convert extra components
    for comp in drift_report.extra_components:
        items.append(
            DriftItem(
                component=comp.split(":")[0].strip(),
                spec_says="Not in spec",
                impl_does=comp,
                severity=AuditSeverity.WARNING,
            )
        )

    return items


def _infer_impl_path(spec_path: Path) -> Path | None:
    """
    Infer implementation path from spec path.

    Examples:
        spec/agents/brain/brain.md -> impl/claude/agents/brain/
        spec/protocols/witness.md -> impl/claude/protocols/witness/
        spec/services/brain.md -> impl/claude/services/brain/

    Returns:
        Path to implementation directory, or None if cannot infer
    """
    # Get spec root
    parts = spec_path.parts
    if "spec" not in parts:
        # Not in spec directory - cannot infer impl path
        return None

    try:
        spec_idx = parts.index("spec")
        spec_root = Path(*parts[: spec_idx + 1])
        rel_path = spec_path.relative_to(spec_root)

        # Remove .md extension and get parent
        rel_parts = list(rel_path.parts)
        if rel_parts[-1].endswith(".md"):
            rel_parts[-1] = rel_parts[-1][:-3]

        # Build impl path
        # spec -> impl/claude
        impl_root = spec_root.parent / "impl" / "claude"
        impl_path = impl_root / Path(*rel_parts)

        return impl_path
    except (ValueError, IndexError):
        # Failed to infer - return None
        return None


async def detect_drift_async(
    spec_path: Path,
    impl_path: Path | None = None,
) -> list[DriftItem]:
    """Async version of detect_drift (currently just wraps sync version)."""
    return detect_drift(spec_path, impl_path)
