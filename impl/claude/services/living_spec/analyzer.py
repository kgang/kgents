"""
Spec Analyzer: Bootstrap the Living Spec ledger.

Scans all specs, extracts claims, finds contradictions and harmonies.

Philosophy:
    "Upload spec → Parse → Accumulate evidence → Brilliant executions"
    "If proofs valid, supported. If not used, dead."
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

# =============================================================================
# Types
# =============================================================================


class SpecStatus(Enum):
    """Spec health status."""

    ACTIVE = auto()  # Has evidence, being used
    ORPHAN = auto()  # No evidence, not referenced
    DEPRECATED = auto()  # Explicitly marked deprecated
    ARCHIVED = auto()  # In _archive folder
    CONFLICTING = auto()  # Contradicts another spec


class ClaimType(Enum):
    """Types of claims specs can make."""

    DEFINITION = auto()  # "X is Y"
    ASSERTION = auto()  # "X should do Y"
    CONSTRAINT = auto()  # "X must not do Y"
    DEPENDENCY = auto()  # "X requires Y"
    IMPLEMENTATION = auto()  # "X is implemented in Y"
    DEPRECATION = auto()  # "X is deprecated"


@dataclass
class Claim:
    """A single claim extracted from a spec."""

    claim_type: ClaimType
    subject: str
    predicate: str
    source_file: str
    line_number: int
    raw_text: str


@dataclass
class SpecRecord:
    """Parsed spec with extracted metadata."""

    path: str
    title: str
    status: SpecStatus
    claims: list[Claim] = field(default_factory=list)
    references: list[str] = field(default_factory=list)  # Other specs referenced
    implementations: list[str] = field(default_factory=list)  # Code paths
    tests: list[str] = field(default_factory=list)  # Test paths
    word_count: int = 0
    heading_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize for ledger."""
        return {
            "path": self.path,
            "title": self.title,
            "status": self.status.name,
            "claim_count": len(self.claims),
            "reference_count": len(self.references),
            "impl_count": len(self.implementations),
            "test_count": len(self.tests),
            "word_count": self.word_count,
            "heading_count": self.heading_count,
        }


@dataclass
class Contradiction:
    """Two specs that conflict."""

    spec_a: str
    spec_b: str
    claim_a: Claim
    claim_b: Claim
    conflict_type: str
    severity: str  # "hard" = direct conflict, "soft" = tension

    def describe(self) -> str:
        return f"[{self.severity.upper()}] {self.spec_a} vs {self.spec_b}: {self.conflict_type}"


@dataclass
class Harmony:
    """Two specs that reinforce each other."""

    spec_a: str
    spec_b: str
    relationship: str  # "extends", "implements", "supports"
    strength: float  # 0.0 to 1.0

    def describe(self) -> str:
        return f"{self.spec_a} --[{self.relationship}]--> {self.spec_b} (strength: {self.strength:.2f})"


@dataclass
class LedgerReport:
    """Full analysis of spec corpus."""

    specs: list[SpecRecord]
    contradictions: list[Contradiction]
    harmonies: list[Harmony]
    orphans: list[str]  # Specs with no evidence
    deprecated: list[str]  # Explicitly deprecated
    archived: list[str]  # In _archive

    def summary(self) -> dict[str, Any]:
        return {
            "total_specs": len(self.specs),
            "active": sum(1 for s in self.specs if s.status == SpecStatus.ACTIVE),
            "orphans": len(self.orphans),
            "deprecated": len(self.deprecated),
            "archived": len(self.archived),
            "contradictions": len(self.contradictions),
            "harmonies": len(self.harmonies),
            "total_claims": sum(len(s.claims) for s in self.specs),
        }


# =============================================================================
# Parsing
# =============================================================================


# Patterns for extracting claims
PATTERNS = {
    # Definitions: "X is Y", "X: Y"
    "definition": re.compile(r"(?:^|\n)#+\s*(.+?)\s*(?:is|:)\s*(.+?)(?:\n|$)", re.IGNORECASE),
    # Assertions: "X should/must/shall Y"
    "assertion": re.compile(r"(.+?)\s+(?:should|must|shall)\s+(.+?)(?:\.|$)", re.IGNORECASE),
    # Constraints: "X must not/cannot/should not Y"
    "constraint": re.compile(
        r"(.+?)\s+(?:must not|cannot|should not|shall not)\s+(.+?)(?:\.|$)", re.IGNORECASE
    ),
    # Deprecation markers
    "deprecated": re.compile(r"(?:deprecated|obsolete|superseded|replaced by)", re.IGNORECASE),
    # Implementation references
    "impl_ref": re.compile(r"(?:impl/|services/|protocols/)[\w/.-]+\.(?:py|ts|tsx)", re.IGNORECASE),
    # Test references
    "test_ref": re.compile(r"(?:_tests/|tests/|test_)[\w/.-]+\.py", re.IGNORECASE),
    # Spec references (other .md files in spec/)
    "spec_ref": re.compile(r"(?:spec/[\w/-]+\.md|`[\w.-]+\.md`)", re.IGNORECASE),
    # AGENTESE paths
    "agentese": re.compile(r"`((?:self|world|concept|void|time)\.[\w.]+)`"),
}


def parse_spec(path: Path) -> SpecRecord:
    """Parse a single spec file."""
    content = path.read_text(encoding="utf-8", errors="replace")
    relative_path = str(path.relative_to(path.parents[2]))  # Relative to kgents/

    # Determine status
    status = SpecStatus.ACTIVE
    if "/_archive/" in str(path):
        status = SpecStatus.ARCHIVED
    elif PATTERNS["deprecated"].search(content):
        status = SpecStatus.DEPRECATED

    # Extract title from first heading
    title_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else path.stem

    # Count metrics
    word_count = len(content.split())
    heading_count = len(re.findall(r"^#+\s+", content, re.MULTILINE))

    # Extract claims
    claims: list[Claim] = []

    # Find assertions
    for i, match in enumerate(PATTERNS["assertion"].finditer(content)):
        claims.append(
            Claim(
                claim_type=ClaimType.ASSERTION,
                subject=match.group(1).strip()[:100],
                predicate=match.group(2).strip()[:200],
                source_file=relative_path,
                line_number=content[: match.start()].count("\n") + 1,
                raw_text=match.group(0)[:300],
            )
        )

    # Find constraints
    for match in PATTERNS["constraint"].finditer(content):
        claims.append(
            Claim(
                claim_type=ClaimType.CONSTRAINT,
                subject=match.group(1).strip()[:100],
                predicate=match.group(2).strip()[:200],
                source_file=relative_path,
                line_number=content[: match.start()].count("\n") + 1,
                raw_text=match.group(0)[:300],
            )
        )

    # Extract references
    references = list(set(PATTERNS["spec_ref"].findall(content)))
    implementations = list(set(PATTERNS["impl_ref"].findall(content)))
    tests = list(set(PATTERNS["test_ref"].findall(content)))

    return SpecRecord(
        path=relative_path,
        title=title,
        status=status,
        claims=claims,
        references=references,
        implementations=implementations,
        tests=tests,
        word_count=word_count,
        heading_count=heading_count,
    )


# =============================================================================
# Analysis
# =============================================================================


def find_contradictions(specs: list[SpecRecord]) -> list[Contradiction]:
    """Find conflicting claims across specs."""
    contradictions: list[Contradiction] = []

    # Build claim index by subject
    claim_index: dict[str, list[tuple[SpecRecord, Claim]]] = {}
    for spec in specs:
        for claim in spec.claims:
            # Normalize subject
            subject_key = claim.subject.lower().strip()
            if len(subject_key) > 5:  # Skip very short subjects
                if subject_key not in claim_index:
                    claim_index[subject_key] = []
                claim_index[subject_key].append((spec, claim))

    # Find conflicts: assertions vs constraints on same subject
    for subject, claims_list in claim_index.items():
        assertions = [(s, c) for s, c in claims_list if c.claim_type == ClaimType.ASSERTION]
        constraints = [(s, c) for s, c in claims_list if c.claim_type == ClaimType.CONSTRAINT]

        for spec_a, claim_a in assertions:
            for spec_b, claim_b in constraints:
                if spec_a.path != spec_b.path:
                    # Potential conflict: assertion vs constraint
                    contradictions.append(
                        Contradiction(
                            spec_a=spec_a.path,
                            spec_b=spec_b.path,
                            claim_a=claim_a,
                            claim_b=claim_b,
                            conflict_type=f"Assertion vs Constraint on '{subject[:50]}'",
                            severity="soft",
                        )
                    )

    return contradictions


def find_harmonies(specs: list[SpecRecord]) -> list[Harmony]:
    """Find reinforcing relationships between specs."""
    harmonies: list[Harmony] = []

    # Build reference graph
    for spec in specs:
        for ref in spec.references:
            # Find target spec
            ref_clean = ref.strip("`").replace("spec/", "")
            for other in specs:
                if ref_clean in other.path:
                    harmonies.append(
                        Harmony(
                            spec_a=spec.path,
                            spec_b=other.path,
                            relationship="references",
                            strength=0.5,
                        )
                    )
                    break

    # Find implementation relationships
    for spec in specs:
        if spec.implementations:
            harmonies.append(
                Harmony(
                    spec_a=spec.path,
                    spec_b="[has implementations]",
                    relationship="implemented",
                    strength=0.8,
                )
            )
        if spec.tests:
            harmonies.append(
                Harmony(
                    spec_a=spec.path,
                    spec_b="[has tests]",
                    relationship="tested",
                    strength=0.9,
                )
            )

    return harmonies


def find_orphans(specs: list[SpecRecord]) -> list[str]:
    """Find specs with no evidence of use."""
    orphans = []

    # Build reference set
    all_references = set()
    for spec in specs:
        all_references.update(spec.references)

    for spec in specs:
        if spec.status in (SpecStatus.ARCHIVED, SpecStatus.DEPRECATED):
            continue

        # Orphan if: no implementations, no tests, not referenced
        has_impl = len(spec.implementations) > 0
        has_tests = len(spec.tests) > 0
        is_referenced = any(
            spec.path in ref or spec.title.lower() in ref.lower() for ref in all_references
        )

        if not has_impl and not has_tests and not is_referenced:
            orphans.append(spec.path)

    return orphans


# =============================================================================
# Main Entry Point
# =============================================================================


def analyze_spec_corpus(spec_root: Path) -> LedgerReport:
    """
    Analyze entire spec corpus.

    Args:
        spec_root: Path to spec/ directory

    Returns:
        LedgerReport with full analysis
    """
    # Find all spec files
    spec_files = list(spec_root.glob("**/*.md"))

    # Parse each
    specs = [parse_spec(f) for f in spec_files]

    # Analyze
    contradictions = find_contradictions(specs)
    harmonies = find_harmonies(specs)
    orphans = find_orphans(specs)
    deprecated = [s.path for s in specs if s.status == SpecStatus.DEPRECATED]
    archived = [s.path for s in specs if s.status == SpecStatus.ARCHIVED]

    return LedgerReport(
        specs=specs,
        contradictions=contradictions,
        harmonies=harmonies,
        orphans=orphans,
        deprecated=deprecated,
        archived=archived,
    )


def print_report(report: LedgerReport) -> None:
    """Print human-readable report."""
    summary = report.summary()

    print("=" * 60)
    print("LIVING SPEC LEDGER REPORT")
    print("=" * 60)
    print()
    print(f"Total specs:      {summary['total_specs']}")
    print(f"Active:           {summary['active']}")
    print(f"Orphans:          {summary['orphans']}")
    print(f"Deprecated:       {summary['deprecated']}")
    print(f"Archived:         {summary['archived']}")
    print(f"Total claims:     {summary['total_claims']}")
    print(f"Contradictions:   {summary['contradictions']}")
    print(f"Harmonies:        {summary['harmonies']}")
    print()

    if report.contradictions:
        print("-" * 60)
        print("CONTRADICTIONS")
        print("-" * 60)
        for c in report.contradictions[:20]:  # Top 20
            print(f"  {c.describe()}")
        if len(report.contradictions) > 20:
            print(f"  ... and {len(report.contradictions) - 20} more")
        print()

    if report.orphans:
        print("-" * 60)
        print("ORPHANS (no evidence)")
        print("-" * 60)
        for o in sorted(report.orphans)[:30]:
            print(f"  {o}")
        if len(report.orphans) > 30:
            print(f"  ... and {len(report.orphans) - 30} more")
        print()

    # Top specs by claims
    print("-" * 60)
    print("TOP SPECS BY CLAIMS")
    print("-" * 60)
    by_claims = sorted(report.specs, key=lambda s: len(s.claims), reverse=True)
    for spec in by_claims[:15]:
        print(f"  {len(spec.claims):3d} claims: {spec.path}")
    print()

    # Specs with implementations
    print("-" * 60)
    print("SPECS WITH EVIDENCE")
    print("-" * 60)
    with_evidence = [s for s in report.specs if s.implementations or s.tests]
    for spec in sorted(
        with_evidence, key=lambda s: len(s.implementations) + len(s.tests), reverse=True
    )[:15]:
        print(f"  {spec.path}")
        if spec.implementations:
            print(f"    impl: {', '.join(spec.implementations[:3])}")
        if spec.tests:
            print(f"    test: {', '.join(spec.tests[:3])}")
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        spec_root = Path(sys.argv[1])
    else:
        # Default to finding spec/ relative to this file
        spec_root = Path(__file__).parents[4] / "spec"

    report = analyze_spec_corpus(spec_root)
    print_report(report)
