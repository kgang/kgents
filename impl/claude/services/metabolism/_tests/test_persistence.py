"""
Tests for MetabolismPersistence: D-gent backed storage for metabolic state.

Covers:
- Evidence CRUD operations
- Insight CRUD operations
- Stigmergy trace operations
- JSON fallback when no D-gent
- Cross-session persistence
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from services.metabolism.persistence import (
    CausalInsightRecord,
    MetabolismPersistence,
    StigmergyTraceRecord,
    StoredEvidenceRecord,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create a temporary directory for fallback files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def persistence_json(temp_dir):
    """Create a MetabolismPersistence with JSON fallback only."""
    return MetabolismPersistence(fallback_dir=temp_dir)


@pytest.fixture
def evidence_record():
    """Create a sample evidence record."""
    return StoredEvidenceRecord(
        task_pattern="verification integration",
        run_count=42,
        pass_rate=0.95,
        diversity_score=0.85,
        unique_signatures_count=35,
        created_at=datetime(2025, 12, 21, 10, 0, 0),
        last_run_at=datetime(2025, 12, 21, 14, 30, 0),
        runs_json="[]",
    )


@pytest.fixture
def insight_record():
    """Create a sample insight record."""
    return CausalInsightRecord(
        nudge_pattern="type hints",
        outcome_delta=0.08,
        observation_count=15,
        confidence=0.82,
        updated_at=datetime(2025, 12, 21, 12, 0, 0),
    )


@pytest.fixture
def stigmergy_record():
    """Create a sample stigmergy trace record."""
    return StigmergyTraceRecord(
        concept="verification",
        intensity=1.5,
        deposited_at=datetime(2025, 12, 21, 8, 0, 0),
        depositor="morning_voice",
        metadata_json='{"source_field": "success_criteria"}',
    )


# =============================================================================
# Evidence Tests
# =============================================================================


class TestEvidencePersistence:
    """Tests for evidence CRUD operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_evidence(self, persistence_json, evidence_record):
        """Test saving and loading evidence record."""
        await persistence_json.save_evidence("verification", evidence_record)

        loaded = await persistence_json.load_evidence("verification")
        assert loaded is not None
        assert loaded.task_pattern == "verification integration"
        assert loaded.run_count == 42
        assert loaded.pass_rate == 0.95
        assert loaded.diversity_score == 0.85

    @pytest.mark.asyncio
    async def test_list_evidence_patterns(self, persistence_json, evidence_record):
        """Test listing evidence patterns."""
        # Save multiple patterns
        await persistence_json.save_evidence("pattern1", evidence_record)

        record2 = StoredEvidenceRecord(
            task_pattern="type checking",
            run_count=20,
            pass_rate=0.9,
            diversity_score=0.7,
            unique_signatures_count=15,
            created_at=datetime.now(),
            last_run_at=None,
            runs_json="[]",
        )
        await persistence_json.save_evidence("pattern2", record2)

        patterns = await persistence_json.list_evidence_patterns()
        assert len(patterns) == 2
        assert "pattern1" in patterns
        assert "pattern2" in patterns

    @pytest.mark.asyncio
    async def test_delete_evidence(self, persistence_json, evidence_record):
        """Test deleting evidence."""
        await persistence_json.save_evidence("to_delete", evidence_record)

        # Verify it exists
        loaded = await persistence_json.load_evidence("to_delete")
        assert loaded is not None

        # Delete it
        deleted = await persistence_json.delete_evidence("to_delete")
        assert deleted is True

        # Verify it's gone
        loaded = await persistence_json.load_evidence("to_delete")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_load_nonexistent_evidence(self, persistence_json):
        """Test loading evidence that doesn't exist."""
        loaded = await persistence_json.load_evidence("nonexistent")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_evidence_record_serialization(self, evidence_record):
        """Test evidence record to_dict() method."""
        data = evidence_record.to_dict()

        assert data["task_pattern"] == "verification integration"
        assert data["run_count"] == 42
        assert data["pass_rate"] == 0.95
        assert data["diversity_score"] == 0.85
        assert "created_at" in data


# =============================================================================
# Insight Tests
# =============================================================================


class TestInsightPersistence:
    """Tests for causal insight CRUD operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_insight(self, persistence_json, insight_record):
        """Test saving and loading insight record."""
        await persistence_json.save_insight(insight_record)

        insights = await persistence_json.load_insights()
        assert len(insights) == 1
        assert insights[0].nudge_pattern == "type hints"
        assert insights[0].outcome_delta == 0.08
        assert insights[0].confidence == 0.82

    @pytest.mark.asyncio
    async def test_filter_insights_by_query(self, persistence_json, insight_record):
        """Test filtering insights by query."""
        # Save multiple insights
        await persistence_json.save_insight(insight_record)

        insight2 = CausalInsightRecord(
            nudge_pattern="docstrings",
            outcome_delta=0.05,
            observation_count=10,
            confidence=0.7,
        )
        await persistence_json.save_insight(insight2)

        # Filter by query
        hints_insights = await persistence_json.load_insights(query="type")
        assert len(hints_insights) == 1
        assert hints_insights[0].nudge_pattern == "type hints"

    @pytest.mark.asyncio
    async def test_insight_record_serialization(self, insight_record):
        """Test insight record to_dict() method."""
        data = insight_record.to_dict()

        assert data["nudge_pattern"] == "type hints"
        assert data["outcome_delta"] == 0.08
        assert data["observation_count"] == 15
        assert data["confidence"] == 0.82


# =============================================================================
# Stigmergy Tests
# =============================================================================


class TestStigmergyPersistence:
    """Tests for stigmergy trace operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_trace(self, persistence_json, stigmergy_record):
        """Test saving and loading stigmergy trace."""
        await persistence_json.save_stigmergy_trace(stigmergy_record)

        traces = await persistence_json.load_stigmergy_traces()
        assert len(traces) == 1
        assert traces[0].concept == "verification"
        assert traces[0].intensity == 1.5
        assert traces[0].depositor == "morning_voice"

    @pytest.mark.asyncio
    async def test_filter_traces_by_concept(self, persistence_json, stigmergy_record):
        """Test filtering traces by concept."""
        # Save multiple traces
        await persistence_json.save_stigmergy_trace(stigmergy_record)

        trace2 = StigmergyTraceRecord(
            concept="testing",
            intensity=0.8,
            deposited_at=datetime.now(),
            depositor="morning_voice",
            metadata_json="{}",
        )
        await persistence_json.save_stigmergy_trace(trace2)

        # Filter by concept
        verification_traces = await persistence_json.load_stigmergy_traces(concept="verification")
        assert len(verification_traces) == 1
        assert verification_traces[0].concept == "verification"

    @pytest.mark.asyncio
    async def test_filter_traces_by_intensity(self, persistence_json, stigmergy_record):
        """Test filtering traces by minimum intensity."""
        # Save trace with high intensity
        await persistence_json.save_stigmergy_trace(stigmergy_record)

        # Save trace with low intensity
        low_trace = StigmergyTraceRecord(
            concept="testing",
            intensity=0.1,
            deposited_at=datetime.now(),
            depositor="morning_voice",
            metadata_json="{}",
        )
        await persistence_json.save_stigmergy_trace(low_trace)

        # Filter by intensity
        strong_traces = await persistence_json.load_stigmergy_traces(min_intensity=1.0)
        assert len(strong_traces) == 1
        assert strong_traces[0].intensity == 1.5

    @pytest.mark.asyncio
    async def test_delete_evaporated_traces(self, persistence_json):
        """Test deleting traces below threshold."""
        # Save traces with different intensities
        strong = StigmergyTraceRecord(
            concept="strong",
            intensity=2.0,
            deposited_at=datetime.now(),
            depositor="test",
            metadata_json="{}",
        )
        weak = StigmergyTraceRecord(
            concept="weak",
            intensity=0.005,
            deposited_at=datetime.now(),
            depositor="test",
            metadata_json="{}",
        )
        await persistence_json.save_stigmergy_trace(strong)
        await persistence_json.save_stigmergy_trace(weak)

        # Delete evaporated (below 0.01)
        deleted = await persistence_json.delete_evaporated_traces(0.01)
        assert deleted == 1

        # Verify only strong survives
        traces = await persistence_json.load_stigmergy_traces()
        assert len(traces) == 1
        assert traces[0].concept == "strong"

    @pytest.mark.asyncio
    async def test_stigmergy_record_serialization(self, stigmergy_record):
        """Test stigmergy record to_dict() method."""
        data = stigmergy_record.to_dict()

        assert data["concept"] == "verification"
        assert data["intensity"] == 1.5
        assert data["depositor"] == "morning_voice"


# =============================================================================
# Fallback and Stats Tests
# =============================================================================


class TestFallbackBehavior:
    """Tests for JSON fallback behavior."""

    @pytest.mark.asyncio
    async def test_persistence_without_dgent_uses_json(self, temp_dir):
        """Test that persistence falls back to JSON without D-gent."""
        persistence = MetabolismPersistence(fallback_dir=temp_dir)

        assert not persistence.has_dgent

        # Save evidence
        record = StoredEvidenceRecord(
            task_pattern="test",
            run_count=1,
            pass_rate=1.0,
            diversity_score=1.0,
            unique_signatures_count=1,
            created_at=datetime.now(),
            last_run_at=None,
            runs_json="[]",
        )
        await persistence.save_evidence("test", record)

        # Verify JSON file exists
        json_file = temp_dir / "evidence.json"
        assert json_file.exists()

        # Verify content
        data = json.loads(json_file.read_text())
        assert "test" in data

    @pytest.mark.asyncio
    async def test_stats(self, persistence_json, evidence_record, insight_record, stigmergy_record):
        """Test stats() method."""
        # Save some data
        await persistence_json.save_evidence("test", evidence_record)
        await persistence_json.save_insight(insight_record)
        await persistence_json.save_stigmergy_trace(stigmergy_record)

        stats = await persistence_json.stats()

        assert stats["storage_type"] == "json_fallback"
        assert stats["evidence_patterns"] == 1
        assert stats["insight_count"] == 1
        assert stats["stigmergy_trace_count"] == 1


# =============================================================================
# Cross-Session Persistence Tests
# =============================================================================


class TestCrossSessionPersistence:
    """Tests for cross-session persistence behavior."""

    @pytest.mark.asyncio
    async def test_evidence_survives_new_persistence_instance(self, temp_dir, evidence_record):
        """Test that evidence persists across persistence instances."""
        # Session 1: Save evidence
        persistence1 = MetabolismPersistence(fallback_dir=temp_dir)
        await persistence1.save_evidence("cross_session", evidence_record)

        # Session 2: Load evidence with new instance
        persistence2 = MetabolismPersistence(fallback_dir=temp_dir)
        loaded = await persistence2.load_evidence("cross_session")

        assert loaded is not None
        assert loaded.task_pattern == "verification integration"
        assert loaded.run_count == 42

    @pytest.mark.asyncio
    async def test_insights_survive_new_persistence_instance(self, temp_dir, insight_record):
        """Test that insights persist across persistence instances."""
        # Session 1: Save insight
        persistence1 = MetabolismPersistence(fallback_dir=temp_dir)
        await persistence1.save_insight(insight_record)

        # Session 2: Load insight with new instance
        persistence2 = MetabolismPersistence(fallback_dir=temp_dir)
        insights = await persistence2.load_insights()

        assert len(insights) == 1
        assert insights[0].nudge_pattern == "type hints"

    @pytest.mark.asyncio
    async def test_stigmergy_survives_new_persistence_instance(self, temp_dir, stigmergy_record):
        """Test that stigmergy traces persist across persistence instances."""
        # Session 1: Save trace
        persistence1 = MetabolismPersistence(fallback_dir=temp_dir)
        await persistence1.save_stigmergy_trace(stigmergy_record)

        # Session 2: Load trace with new instance
        persistence2 = MetabolismPersistence(fallback_dir=temp_dir)
        traces = await persistence2.load_stigmergy_traces()

        assert len(traces) == 1
        assert traces[0].concept == "verification"
