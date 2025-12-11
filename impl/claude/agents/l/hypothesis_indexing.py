"""
L-gent + B-gent Integration: Hypothesis Outcome Indexing.

Cross-pollination Opportunity T2.10:
    Problem: B-gent doesn't learn from past hypothesis successes/failures
    Solution: L-gent indexes hypotheses + outcomes → pattern analysis
    Impact: Learn what hypothesis types work in which domains

This module indexes scientific hypotheses and their outcomes in the L-gent catalog,
enabling pattern analysis and learning across domains.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HypothesisOutcome(Enum):
    """Outcome of hypothesis testing/evaluation."""

    CONFIRMED = "confirmed"  # Evidence supports hypothesis
    REFUTED = "refuted"  # Evidence contradicts hypothesis
    PENDING = "pending"  # Not yet tested
    INCONCLUSIVE = "inconclusive"  # Evidence insufficient to decide
    PARTIALLY_CONFIRMED = "partially_confirmed"  # Mixed evidence


@dataclass
class HypothesisRecord:
    """
    A hypothesis stored in the L-gent catalog with metadata and outcomes.

    This extends the basic Hypothesis from B-gent with outcome tracking,
    experimental data, and domain-specific metadata.
    """

    # Core hypothesis data (from B-gent)
    id: str  # Unique identifier
    statement: str  # The hypothesis itself
    domain: str  # Scientific domain
    observations: list[str]  # Observations that led to hypothesis
    confidence: float  # Initial confidence (0.0-1.0)
    novelty: str  # "incremental", "exploratory", or "paradigm_shifting"
    falsifiable_by: list[str]  # How it can be disproven

    # Outcome tracking
    outcome: HypothesisOutcome = HypothesisOutcome.PENDING
    outcome_confidence: float | None = None  # Confidence in outcome (0.0-1.0)
    outcome_evidence: list[str] = field(default_factory=list)  # Evidence for outcome
    tested_at: datetime | None = None  # When outcome was determined

    # Metadata
    generated_by: str = "unknown"  # B-gent instance that created it
    generated_at: datetime = field(default_factory=datetime.now)
    keywords: list[str] = field(default_factory=list)  # For search
    related_hypotheses: list[str] = field(
        default_factory=list
    )  # IDs of related hypotheses

    # Experimental data
    experiments_conducted: list[dict[str, Any]] = field(default_factory=list)
    # Each experiment: {"name": str, "date": datetime, "result": str, "data": Any}

    # Learning metadata
    success_rate: float | None = None  # For similar hypotheses in this domain
    domain_patterns: dict[str, Any] = field(default_factory=dict)  # Learned patterns


@dataclass
class HypothesisSearchQuery:
    """Query for searching hypothesis index."""

    domain: str | None = None  # Filter by scientific domain
    outcome: HypothesisOutcome | None = None  # Filter by outcome
    min_confidence: float | None = None  # Minimum initial confidence
    novelty: str | None = None  # Filter by novelty level
    keywords: list[str] | None = None  # Keyword search
    min_success_rate: float | None = None  # For learning analysis


@dataclass
class HypothesisSearchResult:
    """Result from hypothesis search."""

    record: HypothesisRecord
    relevance_score: float  # 0.0-1.0
    match_reason: str  # Why this hypothesis matched


@dataclass
class HypothesisPatternAnalysis:
    """
    Analysis of hypothesis patterns learned from the index.

    This enables B-gent to learn what types of hypotheses work
    in which domains.
    """

    domain: str
    total_hypotheses: int
    confirmed_count: int
    refuted_count: int
    success_rate: float  # confirmed / (confirmed + refuted)

    # Pattern insights
    most_successful_novelty: str | None = None  # Which novelty level works best
    avg_confidence_when_confirmed: float | None = None
    avg_confidence_when_refuted: float | None = None
    common_success_keywords: list[str] = field(default_factory=list)
    common_failure_keywords: list[str] = field(default_factory=list)

    # Recommendations
    recommendations: list[str] = field(default_factory=list)


class HypothesisIndex:
    """
    L-gent index for hypothesis outcomes.

    Stores hypotheses from B-gent with their testing outcomes,
    enabling learning and pattern analysis.

    Cross-pollination T2.10: This is the core integration point.
    """

    def __init__(self, storage_path: str | None = None) -> None:
        """
        Initialize hypothesis index.

        Args:
            storage_path: Path for persistent storage (default: in-memory)
        """
        self.storage_path = storage_path
        self.hypotheses: dict[str, HypothesisRecord] = {}

        # Domain-specific indices
        self.domain_index: dict[str, list[str]] = {}  # domain -> hypothesis IDs
        self.outcome_index: dict[HypothesisOutcome, list[str]] = {
            outcome: [] for outcome in HypothesisOutcome
        }
        self.keyword_index: dict[str, list[str]] = {}  # keyword -> hypothesis IDs

        logger.info(
            f"Initialized HypothesisIndex (storage: {storage_path or 'in-memory'})"
        )

    def index_hypothesis(
        self,
        hypothesis_record: HypothesisRecord,
    ) -> None:
        """
        Add a hypothesis to the index.

        Args:
            hypothesis_record: HypothesisRecord to index
        """
        # Store hypothesis
        self.hypotheses[hypothesis_record.id] = hypothesis_record

        # Update domain index
        if hypothesis_record.domain not in self.domain_index:
            self.domain_index[hypothesis_record.domain] = []
        self.domain_index[hypothesis_record.domain].append(hypothesis_record.id)

        # Update outcome index
        self.outcome_index[hypothesis_record.outcome].append(hypothesis_record.id)

        # Update keyword index
        for keyword in hypothesis_record.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            self.keyword_index[keyword].append(hypothesis_record.id)

        logger.info(
            f"Indexed hypothesis: {hypothesis_record.id} ({hypothesis_record.domain})"
        )

    def update_outcome(
        self,
        hypothesis_id: str,
        outcome: HypothesisOutcome,
        evidence: list[str],
        outcome_confidence: float | None = None,
    ) -> None:
        """
        Update the outcome of a hypothesis.

        Args:
            hypothesis_id: ID of hypothesis to update
            outcome: New outcome
            evidence: Evidence for the outcome
            outcome_confidence: Confidence in outcome determination
        """
        if hypothesis_id not in self.hypotheses:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in index")

        record = self.hypotheses[hypothesis_id]

        # Remove from old outcome index
        self.outcome_index[record.outcome].remove(hypothesis_id)

        # Update record
        record.outcome = outcome
        record.outcome_evidence = evidence
        record.outcome_confidence = outcome_confidence
        record.tested_at = datetime.now()

        # Add to new outcome index
        self.outcome_index[outcome].append(hypothesis_id)

        logger.info(f"Updated hypothesis {hypothesis_id} outcome: {outcome}")

    def search(
        self,
        query: HypothesisSearchQuery,
    ) -> list[HypothesisSearchResult]:
        """
        Search the hypothesis index.

        Args:
            query: Search criteria

        Returns:
            List of matching HypothesisSearchResult ordered by relevance
        """
        results: list[HypothesisSearchResult] = []

        # Start with all hypotheses
        candidates = list(self.hypotheses.values())

        # Apply filters
        if query.domain:
            candidates = [h for h in candidates if h.domain == query.domain]

        if query.outcome:
            candidates = [h for h in candidates if h.outcome == query.outcome]

        if query.min_confidence:
            candidates = [h for h in candidates if h.confidence >= query.min_confidence]

        if query.novelty:
            candidates = [h for h in candidates if h.novelty == query.novelty]

        if query.min_success_rate:
            candidates = [
                h
                for h in candidates
                if h.success_rate is not None
                and h.success_rate >= query.min_success_rate
            ]

        # Keyword scoring
        for candidate in candidates:
            score = 1.0
            match_reasons = []

            if query.keywords:
                matching_keywords = set(query.keywords) & set(candidate.keywords)
                keyword_score = (
                    len(matching_keywords) / len(query.keywords)
                    if query.keywords
                    else 0
                )
                score *= 0.5 + 0.5 * keyword_score  # Keyword match boosts score
                if matching_keywords:
                    match_reasons.append(f"Keywords: {', '.join(matching_keywords)}")

            if not match_reasons:
                match_reasons.append("Matched filters")

            results.append(
                HypothesisSearchResult(
                    record=candidate,
                    relevance_score=score,
                    match_reason="; ".join(match_reasons),
                )
            )

        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        logger.info(f"Search returned {len(results)} results")
        return results

    def analyze_domain_patterns(
        self,
        domain: str,
    ) -> HypothesisPatternAnalysis:
        """
        Analyze patterns in hypotheses for a specific domain.

        This is the key learning function for T2.10.

        Args:
            domain: Scientific domain to analyze

        Returns:
            HypothesisPatternAnalysis with learned patterns
        """
        if domain not in self.domain_index:
            return HypothesisPatternAnalysis(
                domain=domain,
                total_hypotheses=0,
                confirmed_count=0,
                refuted_count=0,
                success_rate=0.0,
            )

        domain_hypotheses = [self.hypotheses[hid] for hid in self.domain_index[domain]]

        total = len(domain_hypotheses)
        confirmed = [
            h for h in domain_hypotheses if h.outcome == HypothesisOutcome.CONFIRMED
        ]
        refuted = [
            h for h in domain_hypotheses if h.outcome == HypothesisOutcome.REFUTED
        ]

        confirmed_count = len(confirmed)
        refuted_count = len(refuted)
        success_rate = (
            confirmed_count / (confirmed_count + refuted_count)
            if (confirmed_count + refuted_count) > 0
            else 0.0
        )

        # Analyze novelty distribution
        novelty_success: dict[str, int] = {}
        for h in confirmed:
            novelty_success[h.novelty] = novelty_success.get(h.novelty, 0) + 1

        most_successful_novelty = (
            max(novelty_success, key=lambda k: novelty_success[k])
            if novelty_success
            else None
        )

        # Confidence analysis
        avg_conf_confirmed = (
            sum(h.confidence for h in confirmed) / len(confirmed) if confirmed else None
        )
        avg_conf_refuted = (
            sum(h.confidence for h in refuted) / len(refuted) if refuted else None
        )

        # Keyword analysis
        confirmed_keywords: dict[str, int] = {}
        refuted_keywords: dict[str, int] = {}

        for h in confirmed:
            for kw in h.keywords:
                confirmed_keywords[kw] = confirmed_keywords.get(kw, 0) + 1

        for h in refuted:
            for kw in h.keywords:
                refuted_keywords[kw] = refuted_keywords.get(kw, 0) + 1

        common_success_keywords = sorted(
            confirmed_keywords.keys(),
            key=lambda k: confirmed_keywords[k],
            reverse=True,
        )[:5]

        common_failure_keywords = sorted(
            refuted_keywords.keys(),
            key=lambda k: refuted_keywords[k],
            reverse=True,
        )[:5]

        # Generate recommendations
        recommendations = []

        if most_successful_novelty:
            recommendations.append(
                f"'{most_successful_novelty}' hypotheses have highest success rate in {domain}"
            )

        if avg_conf_confirmed and avg_conf_refuted:
            if avg_conf_confirmed > avg_conf_refuted:
                recommendations.append(
                    f"Higher initial confidence correlates with success (confirmed avg: {avg_conf_confirmed:.2f}, refuted avg: {avg_conf_refuted:.2f})"
                )
            else:
                recommendations.append(
                    f"Be cautious: higher confidence doesn't guarantee success in {domain}"
                )

        if common_success_keywords:
            recommendations.append(
                f"Successful hypotheses often involve: {', '.join(common_success_keywords[:3])}"
            )

        return HypothesisPatternAnalysis(
            domain=domain,
            total_hypotheses=total,
            confirmed_count=confirmed_count,
            refuted_count=refuted_count,
            success_rate=success_rate,
            most_successful_novelty=most_successful_novelty,
            avg_confidence_when_confirmed=avg_conf_confirmed,
            avg_confidence_when_refuted=avg_conf_refuted,
            common_success_keywords=common_success_keywords,
            common_failure_keywords=common_failure_keywords,
            recommendations=recommendations,
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get overall index statistics."""
        total = len(self.hypotheses)
        by_outcome = {
            outcome.value: len(ids) for outcome, ids in self.outcome_index.items()
        }
        by_domain = {domain: len(ids) for domain, ids in self.domain_index.items()}

        return {
            "total_hypotheses": total,
            "by_outcome": by_outcome,
            "by_domain": by_domain,
            "domains": list(by_domain.keys()),
        }


# --- B-gent Integration Functions ---


def bgent_hypothesis_to_record(
    hypothesis: Any,  # B-gent Hypothesis object
    domain: str,
    observations: list[str],
    hypothesis_id: str | None = None,
) -> HypothesisRecord:
    """
    Convert B-gent Hypothesis to HypothesisRecord for indexing.

    Args:
        hypothesis: Hypothesis from B-gent
        domain: Scientific domain
        observations: Observations that led to hypothesis
        hypothesis_id: Optional ID (will be auto-generated if None)

    Returns:
        HypothesisRecord ready for indexing
    """
    import uuid

    return HypothesisRecord(
        id=hypothesis_id or str(uuid.uuid4()),
        statement=hypothesis.statement,
        domain=domain,
        observations=observations,
        confidence=hypothesis.confidence,
        novelty=hypothesis.novelty.value
        if hasattr(hypothesis.novelty, "value")
        else hypothesis.novelty,
        falsifiable_by=hypothesis.falsifiable_by,
        keywords=_extract_keywords_from_statement(hypothesis.statement),
        generated_at=datetime.now(),
    )


def _extract_keywords_from_statement(statement: str) -> list[str]:
    """Extract keywords from hypothesis statement for indexing."""
    # Simple keyword extraction (could be enhanced with NLP)
    words = statement.lower().split()
    # Filter out common words
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "if",
        "then",
        "that",
        "this",
        "is",
        "are",
        "was",
        "were",
    }
    keywords = [w.strip(".,;:!?") for w in words if w not in stopwords and len(w) > 3]
    return list(set(keywords))[:10]  # Max 10 keywords
