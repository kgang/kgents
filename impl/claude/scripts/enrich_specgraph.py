#!/usr/bin/env python3
"""
Batch Enrichment Script for SpecGraph

Scans the implementation for spec references and builds richer edges:
- Heritage references in docstrings
- Test file → spec mappings
- Implementation file → spec mappings
- Confidence scores based on test coverage

Run from repo root:
    PYTHONPATH=impl/claude uv run python impl/claude/scripts/enrich_specgraph.py

Output: JSON file with enriched edge data for frontend consumption.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EnrichedSpec:
    """Enriched spec data with implementation evidence."""

    path: str
    title: str
    tier: str

    # Implementation evidence
    impl_files: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)

    # Derived metrics
    impl_count: int = 0
    test_count: int = 0
    coverage_score: float = 0.0  # 0-1 based on test presence
    confidence: float = 0.5  # Bayesian confidence

    def compute_metrics(self) -> None:
        """Compute derived metrics from evidence."""
        self.impl_count = len(self.impl_files)
        self.test_count = len(self.test_files)

        # Coverage score: has tests?
        if self.test_count > 0:
            self.coverage_score = min(1.0, self.test_count / 10)  # Cap at 10 tests
        else:
            self.coverage_score = 0.0

        # Confidence: Bayesian update
        # Prior: 0.5, Evidence: impl files, test files
        evidence_strength = (
            0.1 * min(self.impl_count, 10)  # Up to +0.1 per impl (max 1.0)
            + 0.05 * min(self.test_count, 10)  # Up to +0.05 per test (max 0.5)
        )
        self.confidence = min(0.95, 0.3 + evidence_strength)


@dataclass
class EnrichmentResult:
    """Full enrichment result."""

    specs: dict[str, EnrichedSpec] = field(default_factory=dict)
    edges: list[dict[str, Any]] = field(default_factory=list)

    # Stats
    total_specs: int = 0
    specs_with_impl: int = 0
    specs_with_tests: int = 0
    total_impl_files: int = 0
    total_test_files: int = 0


# Patterns to find spec references
SPEC_REF_PATTERNS = [
    re.compile(r"spec/[a-zA-Z0-9_/-]+\.md"),
    re.compile(r"Heritage:\s*-?\s*(spec/[^\n]+)"),
    re.compile(r"Implements:\s*`?([^`\n]+)`?"),
]


def scan_implementations(impl_dir: Path, spec_dir: Path) -> EnrichmentResult:
    """Scan implementation directory for spec references."""

    result = EnrichmentResult()

    # Build spec catalog
    spec_catalog: dict[str, str] = {}  # name -> path
    for spec_file in spec_dir.rglob("*.md"):
        rel_path = str(spec_file)
        spec_catalog[spec_file.stem.lower()] = rel_path
        spec_catalog[spec_file.stem.replace("-", "_").lower()] = rel_path

    # Scan Python files
    impl_to_spec: dict[str, set[str]] = defaultdict(set)
    spec_to_impl: dict[str, set[str]] = defaultdict(set)
    test_to_spec: dict[str, set[str]] = defaultdict(set)

    py_files = list(impl_dir.rglob("*.py"))

    for py_file in py_files:
        try:
            content = py_file.read_text(errors="ignore")
            rel_path = str(py_file)

            # Find spec references
            for pattern in SPEC_REF_PATTERNS:
                for match in pattern.finditer(content):
                    spec_ref = match.group(1) if match.lastindex else match.group(0)
                    spec_ref = spec_ref.strip()
                    if spec_ref and spec_ref.startswith("spec/"):
                        impl_to_spec[rel_path].add(spec_ref)
                        spec_to_impl[spec_ref].add(rel_path)

            # Map tests to specs
            if "_tests/" in rel_path or "test_" in py_file.name:
                parts = py_file.parts
                for component in ["services", "protocols", "agents"]:
                    if component in parts:
                        idx = parts.index(component)
                        if idx + 1 < len(parts):
                            name = parts[idx + 1].replace("_", "-")
                            # Find matching specs
                            for spec_path in spec_to_impl.keys():
                                if name in spec_path:
                                    test_to_spec[rel_path].add(spec_path)
                            # Also check catalog
                            for key, spec_path in spec_catalog.items():
                                if name in key or name in spec_path:
                                    test_to_spec[rel_path].add(spec_path)
                        break
        except Exception as e:
            continue

    # Build enriched specs
    all_specs: set[str] = set(spec_to_impl.keys())
    for spec_file in spec_dir.rglob("*.md"):
        all_specs.add(str(spec_file))

    for spec_path in all_specs:
        # Get title from path
        title = Path(spec_path).stem.replace("-", " ").replace("_", " ").title()

        # Determine tier from path
        if "principles" in spec_path or "bootstrap" in spec_path:
            tier = "bootstrap"
        elif "protocols" in spec_path:
            tier = "protocol"
        elif "agents" in spec_path or "gents" in spec_path:
            tier = "agent"
        elif "services" in spec_path:
            tier = "service"
        else:
            tier = "application"

        enriched = EnrichedSpec(
            path=spec_path,
            title=title,
            tier=tier,
            impl_files=sorted(spec_to_impl.get(spec_path, set())),
            test_files=sorted([t for t, specs in test_to_spec.items() if spec_path in specs]),
        )
        enriched.compute_metrics()
        result.specs[spec_path] = enriched

        # Create edges
        for impl in enriched.impl_files:
            result.edges.append(
                {
                    "source": spec_path,
                    "target": impl,
                    "type": "implements",
                    "discovered_by": "batch_enrichment",
                }
            )

        for test in enriched.test_files:
            result.edges.append(
                {
                    "source": spec_path,
                    "target": test,
                    "type": "tests",
                    "discovered_by": "batch_enrichment",
                }
            )

    # Compute stats
    result.total_specs = len(result.specs)
    result.specs_with_impl = sum(1 for s in result.specs.values() if s.impl_count > 0)
    result.specs_with_tests = sum(1 for s in result.specs.values() if s.test_count > 0)
    result.total_impl_files = len(set(impl_to_spec.keys()))
    result.total_test_files = len(test_to_spec)

    return result


def main():
    """Run batch enrichment."""

    # Paths
    repo_root = Path.cwd()
    impl_dir = repo_root / "impl" / "claude"
    spec_dir = repo_root / "spec"
    output_file = impl_dir / "web" / "public" / "specgraph-enriched.json"

    if not impl_dir.exists() or not spec_dir.exists():
        print(
            f"Error: Run from repo root. impl_dir={impl_dir.exists()}, spec_dir={spec_dir.exists()}"
        )
        sys.exit(1)

    print("=" * 60)
    print("SPECGRAPH BATCH ENRICHMENT")
    print("=" * 60)
    print(f"\nScanning {impl_dir}...")

    result = scan_implementations(impl_dir, spec_dir)

    print(f"\n{'=' * 60}")
    print("RESULTS")
    print("=" * 60)
    print(f"Total specs: {result.total_specs}")
    print(
        f"Specs with implementations: {result.specs_with_impl} ({100 * result.specs_with_impl / result.total_specs:.0f}%)"
    )
    print(
        f"Specs with tests: {result.specs_with_tests} ({100 * result.specs_with_tests / result.total_specs:.0f}%)"
    )
    print(f"Total implementation files: {result.total_impl_files}")
    print(f"Total test files: {result.total_test_files}")
    print(f"Total edges discovered: {len(result.edges)}")

    # Top specs by confidence
    print(f"\n{'=' * 60}")
    print("TOP SPECS BY CONFIDENCE")
    print("=" * 60)
    sorted_specs = sorted(result.specs.values(), key=lambda s: -s.confidence)
    for spec in sorted_specs[:15]:
        bar = "█" * int(spec.confidence * 10) + "░" * (10 - int(spec.confidence * 10))
        print(f"  [{bar}] {spec.confidence:.0%} {spec.path[:50]}")

    # Export to JSON
    output_data = {
        "generated_at": str(Path.cwd()),
        "stats": {
            "total_specs": result.total_specs,
            "specs_with_impl": result.specs_with_impl,
            "specs_with_tests": result.specs_with_tests,
            "total_edges": len(result.edges),
        },
        "specs": {
            path: {
                "path": s.path,
                "title": s.title,
                "tier": s.tier,
                "impl_count": s.impl_count,
                "test_count": s.test_count,
                "confidence": s.confidence,
                "coverage_score": s.coverage_score,
            }
            for path, s in result.specs.items()
        },
        "edges": result.edges,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Wrote enriched data to {output_file}")
    print("   Frontend can fetch /specgraph-enriched.json")


if __name__ == "__main__":
    main()
