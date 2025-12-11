"""
Tests for L-gent Hypothesis Indexing (Cross-pollination T2.10).

Tests hypothesis outcome indexing and pattern learning.
"""

from dataclasses import dataclass

import pytest
from agents.l.hypothesis_indexing import (
    HypothesisIndex,
    HypothesisOutcome,
    HypothesisRecord,
    HypothesisSearchQuery,
    bgent_hypothesis_to_record,
)

# --- Test: HypothesisRecord Creation ---


def test_hypothesis_record_creation():
    """Test creating a hypothesis record."""
    record = HypothesisRecord(
        id="hyp-001",
        statement="Increased CO2 levels correlate with temperature rise",
        domain="climate_science",
        observations=["CO2 at 400ppm", "Temp +1.5C since 1950"],
        confidence=0.85,
        novelty="incremental",
        falsifiable_by=["Negative correlation in 10yr data"],
    )

    assert record.id == "hyp-001"
    assert record.outcome == HypothesisOutcome.PENDING
    assert record.domain == "climate_science"


def test_hypothesis_record_with_outcome():
    """Test hypothesis record with outcome."""
    record = HypothesisRecord(
        id="hyp-002",
        statement="Test hypothesis",
        domain="test_domain",
        observations=["obs1"],
        confidence=0.7,
        novelty="exploratory",
        falsifiable_by=["test"],
        outcome=HypothesisOutcome.CONFIRMED,
        outcome_confidence=0.9,
        outcome_evidence=["Evidence A", "Evidence B"],
    )

    assert record.outcome == HypothesisOutcome.CONFIRMED
    assert record.outcome_confidence == 0.9
    assert len(record.outcome_evidence) == 2


# --- Test: HypothesisIndex Basic Operations ---


def test_index_creation():
    """Test creating hypothesis index."""
    index = HypothesisIndex()

    assert len(index.hypotheses) == 0
    assert len(index.domain_index) == 0


def test_index_hypothesis():
    """Test indexing a hypothesis."""
    index = HypothesisIndex()

    record = HypothesisRecord(
        id="hyp-001",
        statement="Test hypothesis",
        domain="physics",
        observations=["obs1"],
        confidence=0.8,
        novelty="incremental",
        falsifiable_by=["test"],
        keywords=["gravity", "mass"],
    )

    index.index_hypothesis(record)

    assert len(index.hypotheses) == 1
    assert "hyp-001" in index.hypotheses
    assert "physics" in index.domain_index
    assert "gravity" in index.keyword_index


def test_index_multiple_hypotheses():
    """Test indexing multiple hypotheses."""
    index = HypothesisIndex()

    for i in range(5):
        record = HypothesisRecord(
            id=f"hyp-{i:03d}",
            statement=f"Hypothesis {i}",
            domain="biology" if i % 2 == 0 else "chemistry",
            observations=[f"obs-{i}"],
            confidence=0.5 + i * 0.1,
            novelty="incremental",
            falsifiable_by=[f"test-{i}"],
        )
        index.index_hypothesis(record)

    assert len(index.hypotheses) == 5
    assert len(index.domain_index["biology"]) == 3  # i=0,2,4
    assert len(index.domain_index["chemistry"]) == 2  # i=1,3


# --- Test: Outcome Updates ---


def test_update_outcome():
    """Test updating hypothesis outcome."""
    index = HypothesisIndex()

    record = HypothesisRecord(
        id="hyp-001",
        statement="Test",
        domain="test",
        observations=["obs"],
        confidence=0.8,
        novelty="incremental",
        falsifiable_by=["test"],
    )

    index.index_hypothesis(record)

    # Initially pending
    assert index.hypotheses["hyp-001"].outcome == HypothesisOutcome.PENDING
    assert len(index.outcome_index[HypothesisOutcome.PENDING]) == 1

    # Update to confirmed
    index.update_outcome(
        "hyp-001",
        HypothesisOutcome.CONFIRMED,
        ["Evidence A"],
        outcome_confidence=0.95,
    )

    assert index.hypotheses["hyp-001"].outcome == HypothesisOutcome.CONFIRMED
    assert index.hypotheses["hyp-001"].outcome_confidence == 0.95
    assert len(index.outcome_index[HypothesisOutcome.CONFIRMED]) == 1
    assert len(index.outcome_index[HypothesisOutcome.PENDING]) == 0


def test_update_outcome_nonexistent():
    """Test updating outcome for nonexistent hypothesis."""
    index = HypothesisIndex()

    with pytest.raises(ValueError, match="not found"):
        index.update_outcome("nonexistent", HypothesisOutcome.CONFIRMED, [])


# --- Test: Search ---


def test_search_by_domain():
    """Test searching hypotheses by domain."""
    index = HypothesisIndex()

    # Add hypotheses in different domains
    for i in range(3):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"bio-{i}",
                statement=f"Bio hypothesis {i}",
                domain="biology",
                observations=[],
                confidence=0.7,
                novelty="incremental",
                falsifiable_by=[],
            )
        )

    for i in range(2):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"chem-{i}",
                statement=f"Chem hypothesis {i}",
                domain="chemistry",
                observations=[],
                confidence=0.7,
                novelty="incremental",
                falsifiable_by=[],
            )
        )

    # Search for biology
    query = HypothesisSearchQuery(domain="biology")
    results = index.search(query)

    assert len(results) == 3
    assert all(r.record.domain == "biology" for r in results)


def test_search_by_outcome():
    """Test searching hypotheses by outcome."""
    index = HypothesisIndex()

    # Add confirmed and refuted hypotheses
    for i in range(2):
        record = HypothesisRecord(
            id=f"confirmed-{i}",
            statement="Confirmed",
            domain="test",
            observations=[],
            confidence=0.8,
            novelty="incremental",
            falsifiable_by=[],
            outcome=HypothesisOutcome.CONFIRMED,
        )
        index.index_hypothesis(record)

    for i in range(3):
        record = HypothesisRecord(
            id=f"refuted-{i}",
            statement="Refuted",
            domain="test",
            observations=[],
            confidence=0.6,
            novelty="incremental",
            falsifiable_by=[],
            outcome=HypothesisOutcome.REFUTED,
        )
        index.index_hypothesis(record)

    # Search for confirmed
    query = HypothesisSearchQuery(outcome=HypothesisOutcome.CONFIRMED)
    results = index.search(query)

    assert len(results) == 2
    assert all(r.record.outcome == HypothesisOutcome.CONFIRMED for r in results)


def test_search_by_confidence():
    """Test searching by minimum confidence."""
    index = HypothesisIndex()

    for i in range(5):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"hyp-{i}",
                statement=f"Hypothesis {i}",
                domain="test",
                observations=[],
                confidence=0.5 + i * 0.1,  # 0.5, 0.6, 0.7, 0.8, 0.9
                novelty="incremental",
                falsifiable_by=[],
            )
        )

    # Search for confidence >= 0.75
    query = HypothesisSearchQuery(min_confidence=0.75)
    results = index.search(query)

    assert len(results) == 2  # 0.8 and 0.9
    assert all(r.record.confidence >= 0.75 for r in results)


def test_search_by_keywords():
    """Test searching by keywords."""
    index = HypothesisIndex()

    index.index_hypothesis(
        HypothesisRecord(
            id="hyp-1",
            statement="Gravity affects mass",
            domain="physics",
            observations=[],
            confidence=0.8,
            novelty="incremental",
            falsifiable_by=[],
            keywords=["gravity", "mass", "force"],
        )
    )

    index.index_hypothesis(
        HypothesisRecord(
            id="hyp-2",
            statement="Photosynthesis requires light",
            domain="biology",
            observations=[],
            confidence=0.9,
            novelty="incremental",
            falsifiable_by=[],
            keywords=["photosynthesis", "light", "energy"],
        )
    )

    # Search for gravity
    query = HypothesisSearchQuery(keywords=["gravity"])
    results = index.search(query)

    assert len(results) >= 1
    assert any("gravity" in r.record.keywords for r in results)


def test_search_combined_filters():
    """Test search with multiple filters."""
    index = HypothesisIndex()

    # Add mix of hypotheses
    for i in range(10):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"hyp-{i}",
                statement=f"Hypothesis {i}",
                domain="physics" if i < 5 else "biology",
                observations=[],
                confidence=0.6 + i * 0.03,
                novelty="incremental" if i % 2 == 0 else "exploratory",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED
                if i < 3
                else HypothesisOutcome.PENDING,
            )
        )

    # Search: physics domain, confirmed, confidence >= 0.65
    query = HypothesisSearchQuery(
        domain="physics",
        outcome=HypothesisOutcome.CONFIRMED,
        min_confidence=0.65,
    )
    results = index.search(query)

    assert all(r.record.domain == "physics" for r in results)
    assert all(r.record.outcome == HypothesisOutcome.CONFIRMED for r in results)
    assert all(r.record.confidence >= 0.65 for r in results)


# --- Test: Pattern Analysis ---


def test_analyze_domain_patterns_empty():
    """Test pattern analysis for domain with no hypotheses."""
    index = HypothesisIndex()

    analysis = index.analyze_domain_patterns("nonexistent_domain")

    assert analysis.domain == "nonexistent_domain"
    assert analysis.total_hypotheses == 0
    assert analysis.success_rate == 0.0


def test_analyze_domain_patterns_basic():
    """Test basic pattern analysis."""
    index = HypothesisIndex()

    # Add 5 confirmed, 3 refuted, 2 pending in physics
    for i in range(5):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"confirmed-{i}",
                statement="Confirmed hypothesis",
                domain="physics",
                observations=[],
                confidence=0.8,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED,
            )
        )

    for i in range(3):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"refuted-{i}",
                statement="Refuted hypothesis",
                domain="physics",
                observations=[],
                confidence=0.6,
                novelty="exploratory",
                falsifiable_by=[],
                outcome=HypothesisOutcome.REFUTED,
            )
        )

    for i in range(2):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"pending-{i}",
                statement="Pending hypothesis",
                domain="physics",
                observations=[],
                confidence=0.7,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.PENDING,
            )
        )

    analysis = index.analyze_domain_patterns("physics")

    assert analysis.domain == "physics"
    assert analysis.total_hypotheses == 10
    assert analysis.confirmed_count == 5
    assert analysis.refuted_count == 3
    assert analysis.success_rate == pytest.approx(5 / 8)  # 5 confirmed out of 8 tested


def test_analyze_novelty_patterns():
    """Test novelty pattern analysis."""
    index = HypothesisIndex()

    # Incremental hypotheses more successful
    for i in range(4):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"inc-{i}",
                statement="Incremental",
                domain="test",
                observations=[],
                confidence=0.8,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED,
            )
        )

    # Exploratory hypotheses less successful
    for i in range(2):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"exp-{i}",
                statement="Exploratory",
                domain="test",
                observations=[],
                confidence=0.7,
                novelty="exploratory",
                falsifiable_by=[],
                outcome=HypothesisOutcome.REFUTED,
            )
        )

    analysis = index.analyze_domain_patterns("test")

    assert analysis.most_successful_novelty == "incremental"


def test_analyze_confidence_patterns():
    """Test confidence pattern analysis."""
    index = HypothesisIndex()

    # High confidence confirmed
    for i in range(3):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"high-conf-{i}",
                statement="High confidence",
                domain="test",
                observations=[],
                confidence=0.9,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED,
            )
        )

    # Low confidence refuted
    for i in range(2):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"low-conf-{i}",
                statement="Low confidence",
                domain="test",
                observations=[],
                confidence=0.5,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.REFUTED,
            )
        )

    analysis = index.analyze_domain_patterns("test")

    assert analysis.avg_confidence_when_confirmed > analysis.avg_confidence_when_refuted


def test_analyze_recommendations():
    """Test that analysis generates recommendations."""
    index = HypothesisIndex()

    for i in range(5):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"hyp-{i}",
                statement="Test",
                domain="test",
                observations=[],
                confidence=0.8,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED,
                keywords=["keyword1", "keyword2"],
            )
        )

    analysis = index.analyze_domain_patterns("test")

    assert len(analysis.recommendations) > 0


# --- Test: Statistics ---


def test_get_statistics():
    """Test getting index statistics."""
    index = HypothesisIndex()

    # Add hypotheses
    for i in range(3):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"bio-{i}",
                statement="Bio",
                domain="biology",
                observations=[],
                confidence=0.7,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.CONFIRMED
                if i < 2
                else HypothesisOutcome.REFUTED,
            )
        )

    for i in range(2):
        index.index_hypothesis(
            HypothesisRecord(
                id=f"chem-{i}",
                statement="Chem",
                domain="chemistry",
                observations=[],
                confidence=0.8,
                novelty="incremental",
                falsifiable_by=[],
                outcome=HypothesisOutcome.PENDING,
            )
        )

    stats = index.get_statistics()

    assert stats["total_hypotheses"] == 5
    assert stats["by_domain"]["biology"] == 3
    assert stats["by_domain"]["chemistry"] == 2
    assert stats["by_outcome"]["confirmed"] == 2
    assert stats["by_outcome"]["refuted"] == 1
    assert stats["by_outcome"]["pending"] == 2


# --- Test: B-gent Integration ---


def test_bgent_hypothesis_to_record():
    """Test converting B-gent Hypothesis to HypothesisRecord."""

    # Mock B-gent Hypothesis
    @dataclass
    class MockNoveltyLevel:
        value: str

    @dataclass
    class MockHypothesis:
        statement: str
        confidence: float
        novelty: MockNoveltyLevel
        falsifiable_by: list[str]

    hypothesis = MockHypothesis(
        statement="Test hypothesis",
        confidence=0.85,
        novelty=MockNoveltyLevel(value="exploratory"),
        falsifiable_by=["test1", "test2"],
    )

    record = bgent_hypothesis_to_record(
        hypothesis,
        domain="test_domain",
        observations=["obs1", "obs2"],
        hypothesis_id="test-001",
    )

    assert record.id == "test-001"
    assert record.statement == "Test hypothesis"
    assert record.domain == "test_domain"
    assert record.confidence == 0.85
    assert record.novelty == "exploratory"
    assert len(record.keywords) > 0  # Should have extracted keywords
