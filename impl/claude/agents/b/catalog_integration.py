"""
B-gent L-gent Catalog Integration

Enables scientific hypotheses to be registered, discovered, and tracked
in the L-gent ecosystem catalog.

Key Features:
- Register hypotheses as HYPOTHESIS entity type
- Track hypothesis evolution and lineage
- Find related/similar hypotheses across domains
- Record hypothesis testing and validation

Unblocks:
- D-gent: Persistent hypothesis storage with lineage tracking
- L-gent: Scientific artifact discovery and composition
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from agents.l import (
    Registry,
    CatalogEntry,
    EntityType,
    Status,
    SearchResult,
    LineageGraph,
    RelationshipType,
)
from .hypothesis_parser import Hypothesis, NoveltyLevel


@dataclass
class HypothesisCatalogEntry:
    """
    Extended catalog entry with hypothesis-specific metadata.

    Wraps CatalogEntry with B-gent specific fields for scientific inquiry.
    """

    entry: CatalogEntry
    hypothesis: Hypothesis

    # B-gent specific metadata
    domain: str
    observations_count: int
    test_results: list[TestResult] = field(default_factory=list)
    is_falsified: bool = False
    falsified_by: str | None = None  # ID of experiment that falsified
    refinements: list[str] = field(default_factory=list)  # IDs of refined hypotheses


@dataclass
class TestResult:
    """Result of testing a hypothesis."""

    test_id: str
    test_name: str
    passed: bool
    evidence_strength: float  # 0.0 to 1.0
    notes: str = ""
    tested_at: datetime = field(default_factory=datetime.now)


# ─────────────────────────────────────────────────────────────────
# Registration Functions
# ─────────────────────────────────────────────────────────────────


async def register_hypothesis(
    hypothesis: Hypothesis,
    registry: Registry,
    domain: str,
    author: str = "B-gent",
    observations: list[str] | None = None,
    forged_from: str | None = None,
) -> CatalogEntry:
    """
    Register a hypothesis with the L-gent catalog.

    Args:
        hypothesis: The hypothesis to register
        registry: L-gent registry instance
        domain: Scientific domain (e.g., "biochemistry", "neuroscience")
        author: Who generated this hypothesis
        observations: Observations that led to this hypothesis
        forged_from: Optional research question/intent

    Returns:
        CatalogEntry for the registered hypothesis
    """
    # Generate unique ID for hypothesis
    hyp_id = f"hyp_{uuid4().hex[:12]}"

    # Build keywords from hypothesis content
    keywords = _extract_keywords(hypothesis, domain)

    # Create catalog entry with hypothesis-specific metadata
    entry = CatalogEntry(
        id=hyp_id,
        entity_type=EntityType.HYPOTHESIS
        if hasattr(EntityType, "HYPOTHESIS")
        else EntityType.SPEC,  # Fallback if HYPOTHESIS not added yet
        name=_generate_hypothesis_name(hypothesis),
        version="1.0.0",
        description=hypothesis.statement,
        keywords=keywords,
        author=author,
        forged_from=forged_from,
        # Type info
        input_type="HypothesisInput",
        output_type="HypothesisOutput",
        # Health - start with defaults
        status=Status.ACTIVE,
        usage_count=0,
        success_rate=1.0,
        # Custom metadata stored in relationships
        relationships={
            "falsifiable_by": hypothesis.falsifiable_by,
            "assumptions": hypothesis.assumptions,
            "supporting_observations": [
                str(i) for i in hypothesis.supporting_observations
            ],
            "observations": observations or [],
            "domain": [domain],
            "novelty": [hypothesis.novelty.value],
            "confidence": [str(hypothesis.confidence)],
        },
    )

    # Register with L-gent
    await registry.register(entry)

    return entry


async def register_hypothesis_batch(
    hypotheses: list[Hypothesis],
    registry: Registry,
    domain: str,
    author: str = "B-gent",
    observations: list[str] | None = None,
    forged_from: str | None = None,
) -> list[CatalogEntry]:
    """
    Register multiple hypotheses at once.

    Useful for batch registration from HypothesisEngine output.
    """
    entries = []
    for hyp in hypotheses:
        entry = await register_hypothesis(
            hypothesis=hyp,
            registry=registry,
            domain=domain,
            author=author,
            observations=observations,
            forged_from=forged_from,
        )
        entries.append(entry)

    return entries


# ─────────────────────────────────────────────────────────────────
# Discovery Functions
# ─────────────────────────────────────────────────────────────────


async def find_hypotheses(
    registry: Registry,
    domain: str | None = None,
    novelty: NoveltyLevel | str | None = None,
    min_confidence: float | None = None,
    query: str | None = None,
) -> list[SearchResult]:
    """
    Find hypotheses matching criteria.

    Args:
        registry: L-gent registry
        domain: Filter by scientific domain
        novelty: Filter by novelty level
        min_confidence: Minimum confidence threshold
        query: Text query for semantic search

    Returns:
        List of SearchResult with matching hypotheses
    """
    # Use L-gent find for base search
    # Note: EntityType.HYPOTHESIS may not exist yet, fall back to SPEC
    entity_type = (
        EntityType.HYPOTHESIS if hasattr(EntityType, "HYPOTHESIS") else EntityType.SPEC
    )

    # Pass None for empty query so registry returns all matching entity_type
    results = await registry.find(
        query=query if query else None,
        entity_type=entity_type,
    )

    # Apply B-gent specific filters
    filtered = []
    for result in results:
        entry = result.entry

        # Domain filter
        if domain:
            entry_domain = entry.relationships.get("domain", [])
            if domain.lower() not in [d.lower() for d in entry_domain]:
                continue

        # Novelty filter
        if novelty:
            novelty_val = (
                novelty.value if isinstance(novelty, NoveltyLevel) else novelty
            )
            entry_novelty = entry.relationships.get("novelty", [])
            if novelty_val not in entry_novelty:
                continue

        # Confidence filter
        if min_confidence is not None:
            entry_confidence = entry.relationships.get("confidence", ["1.0"])
            try:
                conf = float(entry_confidence[0]) if entry_confidence else 1.0
                if conf < min_confidence:
                    continue
            except (ValueError, IndexError):
                pass

        filtered.append(result)

    return filtered


async def find_related_hypotheses(
    registry: Registry,
    hypothesis_id: str,
    max_results: int = 10,
) -> list[SearchResult]:
    """
    Find hypotheses related to a given hypothesis.

    Uses assumptions and falsifiable_by criteria for similarity.
    """
    # Get source hypothesis
    source = await registry.get(hypothesis_id)
    if not source:
        return []

    # Build query from source metadata
    assumptions = source.relationships.get("assumptions", [])
    domain = source.relationships.get("domain", [])

    query = " ".join(assumptions + domain)

    results = await registry.find(query=query)

    # Filter out source hypothesis
    filtered = [r for r in results if r.entry.id != hypothesis_id]

    return filtered[:max_results]


# ─────────────────────────────────────────────────────────────────
# Lineage Functions
# ─────────────────────────────────────────────────────────────────


async def record_hypothesis_evolution(
    lineage: LineageGraph,
    parent_id: str,
    refined_hypothesis: Hypothesis,
    registry: Registry,
    domain: str,
    author: str = "B-gent",
    refinement_reason: str = "",
) -> CatalogEntry:
    """
    Record hypothesis refinement as lineage.

    When a hypothesis is refined (e.g., after new evidence), this records
    the evolution relationship.

    Args:
        lineage: L-gent lineage graph
        parent_id: ID of original hypothesis
        refined_hypothesis: The refined hypothesis
        registry: L-gent registry
        domain: Scientific domain
        author: Who refined it
        refinement_reason: Why it was refined

    Returns:
        CatalogEntry for the new hypothesis
    """
    # Register refined hypothesis
    new_entry = await register_hypothesis(
        hypothesis=refined_hypothesis,
        registry=registry,
        domain=domain,
        author=author,
    )

    # Record lineage
    await lineage.add_relationship(
        source_id=new_entry.id,
        target_id=parent_id,
        relationship_type=RelationshipType.SUCCESSOR_TO,
        created_by=author,
        context={
            "refinement_reason": refinement_reason,
            "type": "hypothesis_refinement",
        },
    )

    return new_entry


async def record_hypothesis_fork(
    lineage: LineageGraph,
    parent_id: str,
    forked_hypothesis: Hypothesis,
    registry: Registry,
    domain: str,
    author: str = "B-gent",
    fork_reason: str = "",
) -> CatalogEntry:
    """
    Record a hypothesis fork.

    When a hypothesis branches into competing alternatives.
    """
    # Register forked hypothesis
    new_entry = await register_hypothesis(
        hypothesis=forked_hypothesis,
        registry=registry,
        domain=domain,
        author=author,
    )

    # Record fork relationship
    await lineage.add_relationship(
        source_id=new_entry.id,
        target_id=parent_id,
        relationship_type=RelationshipType.FORKED_FROM,
        created_by=author,
        context={
            "fork_reason": fork_reason,
            "type": "hypothesis_fork",
        },
    )

    return new_entry


async def get_hypothesis_lineage(
    lineage: LineageGraph,
    hypothesis_id: str,
    max_depth: int | None = None,
) -> dict[str, list[str]]:
    """
    Get full lineage of a hypothesis.

    Returns ancestors and descendants for tracing hypothesis evolution.

    Args:
        lineage: L-gent lineage graph
        hypothesis_id: Hypothesis to trace
        max_depth: Maximum traversal depth

    Returns:
        Dict with "ancestors" and "descendants" lists
    """
    ancestors = await lineage.get_ancestors(
        hypothesis_id,
        relationship_type=RelationshipType.SUCCESSOR_TO,
        max_depth=max_depth,
    )

    # Also include forks
    fork_ancestors = await lineage.get_ancestors(
        hypothesis_id,
        relationship_type=RelationshipType.FORKED_FROM,
        max_depth=max_depth,
    )

    descendants = await lineage.get_descendants(
        hypothesis_id,
        relationship_type=RelationshipType.SUCCESSOR_TO,
        max_depth=max_depth,
    )

    return {
        "ancestors": list(set(ancestors + fork_ancestors)),
        "descendants": descendants,
    }


# ─────────────────────────────────────────────────────────────────
# Metrics Functions
# ─────────────────────────────────────────────────────────────────


async def update_hypothesis_metrics(
    registry: Registry,
    hypothesis_id: str,
    test_passed: bool,
    evidence_strength: float = 0.5,
) -> CatalogEntry | None:
    """
    Update hypothesis metrics after testing.

    Args:
        registry: L-gent registry
        hypothesis_id: Hypothesis that was tested
        test_passed: Did the test support or refute?
        evidence_strength: How strong is the evidence (0.0-1.0)

    Returns:
        Updated catalog entry
    """
    entry = await registry.get(hypothesis_id)
    if not entry:
        return None

    # Update usage and success rate
    await registry.update_usage(
        hypothesis_id,
        success=test_passed,
    )

    return await registry.get(hypothesis_id)


async def mark_hypothesis_falsified(
    registry: Registry,
    hypothesis_id: str,
    falsified_by: str,
    evidence: str,
) -> bool:
    """
    Mark a hypothesis as falsified.

    Args:
        registry: L-gent registry
        hypothesis_id: Hypothesis to falsify
        falsified_by: What evidence falsified it
        evidence: Description of falsifying evidence

    Returns:
        True if successfully updated
    """
    entry = await registry.get(hypothesis_id)
    if not entry:
        return False

    # Deprecate the hypothesis
    return await registry.deprecate(
        hypothesis_id,
        reason=f"Falsified by: {falsified_by}. Evidence: {evidence}",
        successor_id=None,  # No successor for falsified hypotheses
    )


# ─────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────


def _extract_keywords(hypothesis: Hypothesis, domain: str) -> list[str]:
    """Extract searchable keywords from hypothesis."""
    keywords = [domain.lower(), hypothesis.novelty.value]

    # Extract key terms from statement (simple word extraction)
    statement_words = hypothesis.statement.lower().split()
    # Filter to significant words (length > 3, not common words)
    common = {"the", "that", "this", "with", "from", "have", "which", "would"}
    significant = [w for w in statement_words if len(w) > 3 and w not in common]
    keywords.extend(significant[:5])  # Add top 5 significant words

    # Add assumption keywords
    for assumption in hypothesis.assumptions[:3]:
        assumption_words = assumption.lower().split()
        significant_assumption = [
            w for w in assumption_words if len(w) > 3 and w not in common
        ]
        keywords.extend(significant_assumption[:2])

    return list(set(keywords))


def _generate_hypothesis_name(hypothesis: Hypothesis) -> str:
    """Generate a readable name for the hypothesis."""
    # Extract first meaningful phrase
    statement = hypothesis.statement
    if len(statement) <= 50:
        return statement

    # Truncate at word boundary
    words = statement.split()
    name = ""
    for word in words:
        if len(name) + len(word) + 1 <= 47:
            name = f"{name} {word}".strip()
        else:
            break

    return f"{name}..."


# ─────────────────────────────────────────────────────────────────
# Convenience Exports
# ─────────────────────────────────────────────────────────────────

__all__ = [
    # Types
    "HypothesisCatalogEntry",
    "TestResult",
    # Registration
    "register_hypothesis",
    "register_hypothesis_batch",
    # Discovery
    "find_hypotheses",
    "find_related_hypotheses",
    # Lineage
    "record_hypothesis_evolution",
    "record_hypothesis_fork",
    "get_hypothesis_lineage",
    # Metrics
    "update_hypothesis_metrics",
    "mark_hypothesis_falsified",
]
