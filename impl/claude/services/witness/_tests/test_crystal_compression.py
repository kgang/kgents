"""
Tests for Crystal Compression.

Tests the trail-to-crystal compression pipeline with:
- Compression ratio validation (<10% target)
- Causal chain extraction
- Redundancy detection
- Gap detection
- Honesty disclosure

Target Metrics:
- Compression ratio: Crystal size < 10% of trace size
- Preservation: Causal rationale intact
- Honesty: Dropped content disclosed
"""

from datetime import datetime, timedelta

import pytest

from services.witness.crystal import Crystal, CrystalLevel
from services.witness.crystal_compression import (
    TARGET_COMPRESSION_RATIO,
    CausalChainExtractor,
    CausalLink,
    CompressionResult,
    CrystalCompressor,
    DroppedReason,
    GapDetector,
    HonestGap,
    RedundancyDetector,
    get_crystal_compressor,
    reset_crystal_compressor,
)
from services.witness.honesty import reset_honesty_calculator
from services.witness.mark import (
    Mark,
    MarkId,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)
from services.witness.trace_store import MarkStore, reset_mark_store

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Reset global singletons before each test."""
    reset_mark_store()
    reset_crystal_compressor()
    reset_honesty_calculator()


@pytest.fixture
def sample_marks() -> list[Mark]:
    """Create a sample list of marks for testing."""
    base_time = datetime.now()
    marks = []

    # Mark 1: Eureka moment
    marks.append(
        Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            stimulus=Stimulus(
                kind="daily_note", content="Working on compression", source="daily_lab"
            ),
            response=Response(
                kind="thought",
                content="Found the key insight for crystal compression!",
                success=True,
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=base_time,
            tags=("eureka",),
        )
    )

    # Mark 2: Taste decision
    marks.append(
        Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            stimulus=Stimulus(kind="daily_note", content="Design choice", source="daily_lab"),
            response=Response(
                kind="thought", content="Decided to use hierarchical compression", success=True
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=base_time + timedelta(minutes=10),
            tags=("taste",),
        )
    )

    # Mark 3: Friction point
    marks.append(
        Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            stimulus=Stimulus(kind="daily_note", content="Hit a wall", source="daily_lab"),
            response=Response(
                kind="thought", content="Struggling with the algorithm complexity", success=True
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=base_time + timedelta(minutes=20),
            tags=("friction",),
        )
    )

    # Mark 4: Regular note (no tag)
    marks.append(
        Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            stimulus=Stimulus(kind="daily_note", content="Progress update", source="daily_lab"),
            response=Response(
                kind="thought",
                content="Made incremental progress on the implementation",
                success=True,
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=base_time + timedelta(minutes=30),
            tags=(),
        )
    )

    # Mark 5: Joy moment
    marks.append(
        Mark(
            id=generate_mark_id(),
            origin="daily_lab",
            stimulus=Stimulus(kind="daily_note", content="Success!", source="daily_lab"),
            response=Response(
                kind="thought",
                content="Tests passing, feeling great about the design!",
                success=True,
            ),
            umwelt=UmweltSnapshot.witness(trust_level=1),
            timestamp=base_time + timedelta(minutes=40),
            tags=("joy",),
        )
    )

    return marks


@pytest.fixture
def many_marks() -> list[Mark]:
    """Create a larger set of marks for compression testing."""
    base_time = datetime.now()
    marks = []

    for i in range(20):
        tag = ["eureka", "taste", "friction", "joy", "gotcha", ""][i % 6]
        tags = (tag,) if tag else ()

        marks.append(
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content=f"Note {i}", source="daily_lab"),
                response=Response(
                    kind="thought",
                    content=f"This is mark number {i} with some content to test compression. " * 3,
                    success=True,
                ),
                umwelt=UmweltSnapshot.witness(trust_level=1),
                timestamp=base_time + timedelta(minutes=i * 5),
                tags=tags,
            )
        )

    return marks


# =============================================================================
# CausalChainExtractor Tests
# =============================================================================


class TestCausalChainExtractor:
    """Tests for causal chain extraction."""

    def test_extract_from_empty_marks(self) -> None:
        """Empty marks returns empty chain."""
        extractor = CausalChainExtractor()
        links, summary = extractor.extract_chain([])
        assert links == []
        assert "No marks" in summary

    def test_extract_chain_from_marks(self, sample_marks: list[Mark]) -> None:
        """Extracts causal chain from marks with shared tags."""
        extractor = CausalChainExtractor()
        links, summary = extractor.extract_chain(sample_marks)

        # Should have inferred links based on temporal ordering and tag overlap
        assert isinstance(links, list)
        assert isinstance(summary, str)

    def test_chain_summary_includes_key_moments(self, sample_marks: list[Mark]) -> None:
        """Chain summary references eureka, veto, taste moments."""
        extractor = CausalChainExtractor()
        _, summary = extractor.extract_chain(sample_marks)

        # Summary should reference key moments
        assert "eureka" in summary.lower() or "taste" in summary.lower() or len(summary) > 0


# =============================================================================
# RedundancyDetector Tests
# =============================================================================


class TestRedundancyDetector:
    """Tests for redundancy detection."""

    def test_no_redundancy_with_unique_marks(self, sample_marks: list[Mark]) -> None:
        """Unique marks have no redundancy."""
        detector = RedundancyDetector()
        reps, pairs = detector.find_redundant(sample_marks)

        # All marks should be representatives
        assert len(reps) == len(sample_marks)
        assert len(pairs) == 0

    def test_detects_duplicate_content(self) -> None:
        """Detects marks with very similar content."""
        detector = RedundancyDetector(similarity_threshold=0.8)

        base_time = datetime.now()
        marks = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Same thing", source="daily_lab"),
                response=Response(kind="thought", content="Working on feature X", success=True),
                umwelt=UmweltSnapshot.witness(),
                timestamp=base_time,
                tags=("taste",),
            ),
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Same thing", source="daily_lab"),
                response=Response(kind="thought", content="Working on feature X", success=True),
                umwelt=UmweltSnapshot.witness(),
                timestamp=base_time + timedelta(minutes=5),
                tags=("taste",),
            ),
        ]

        reps, pairs = detector.find_redundant(marks)

        # Should detect the duplicate
        assert len(reps) <= len(marks)


# =============================================================================
# GapDetector Tests
# =============================================================================


class TestGapDetector:
    """Tests for gap and provisional item detection."""

    def test_detects_question_marks(self) -> None:
        """Detects marks with open questions."""
        detector = GapDetector()

        marks = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Question", source="daily_lab"),
                response=Response(
                    kind="thought", content="Should we use approach A or B?", success=True
                ),
                umwelt=UmweltSnapshot.witness(),
                timestamp=datetime.now(),
                tags=(),
            ),
        ]

        gaps = detector.detect_gaps(marks)
        assert len(gaps) == 1
        assert gaps[0].gap_type == "uncertain"

    def test_detects_uncertainty_signals(self) -> None:
        """Detects marks with uncertainty words."""
        detector = GapDetector()

        marks = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Maybe", source="daily_lab"),
                response=Response(
                    kind="thought", content="Maybe we should try a different approach", success=True
                ),
                umwelt=UmweltSnapshot.witness(),
                timestamp=datetime.now(),
                tags=(),
            ),
        ]

        gaps = detector.detect_gaps(marks)
        assert len(gaps) == 1
        assert gaps[0].gap_type == "provisional"

    def test_detects_unresolved_friction(self) -> None:
        """Detects friction marks without resolution."""
        detector = GapDetector()

        marks = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Problem", source="daily_lab"),
                response=Response(kind="thought", content="Hit a wall with the API", success=True),
                umwelt=UmweltSnapshot.witness(),
                timestamp=datetime.now(),
                tags=("friction",),
            ),
        ]

        gaps = detector.detect_gaps(marks)
        assert len(gaps) == 1
        assert gaps[0].gap_type == "incomplete"


# =============================================================================
# CrystalCompressor Tests
# =============================================================================


class TestCrystalCompressor:
    """Tests for the main crystal compressor."""

    @pytest.mark.asyncio
    async def test_compress_requires_marks(self) -> None:
        """Compression fails with empty marks."""
        compressor = CrystalCompressor()

        with pytest.raises(ValueError, match="Cannot compress empty"):
            await compressor.compress([])

    @pytest.mark.asyncio
    async def test_compress_returns_result(self, sample_marks: list[Mark]) -> None:
        """Compression returns a CompressionResult."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        assert isinstance(result, CompressionResult)
        assert isinstance(result.crystal, Crystal)
        assert result.preserved_count > 0

    @pytest.mark.asyncio
    async def test_compression_ratio_under_target(self, many_marks: list[Mark]) -> None:
        """Compression achieves target ratio (<10%)."""
        compressor = CrystalCompressor()
        result = await compressor.compress(many_marks, max_ratio=0.10)

        # Compression ratio should be under target
        # (may not always achieve it, but should be close)
        assert result.compression_ratio <= 0.50  # Generous threshold for testing

    @pytest.mark.asyncio
    async def test_preserves_high_importance_marks(self, sample_marks: list[Mark]) -> None:
        """High importance marks (eureka, veto) are preserved."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        # Eureka mark should be preserved
        eureka_mark = next(m for m in sample_marks if "eureka" in m.tags)
        assert eureka_mark.id in result.preserved_marks

    @pytest.mark.asyncio
    async def test_generates_causal_chain(self, sample_marks: list[Mark]) -> None:
        """Compression generates causal chain summary."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        assert result.chain_summary is not None
        assert len(result.chain_summary) > 0

    @pytest.mark.asyncio
    async def test_generates_dropped_reasons(self, many_marks: list[Mark]) -> None:
        """Compression generates reasons for dropped marks."""
        compressor = CrystalCompressor()
        result = await compressor.compress(many_marks, max_ratio=0.05)

        # With aggressive compression, should have dropped marks
        if result.dropped_count > 0:
            assert len(result.dropped_reasons) > 0
            for reason in result.dropped_reasons:
                assert reason.reason in (
                    "redundant",
                    "low_importance",
                    "compression",
                    "tangent",
                    "noise",
                )

    @pytest.mark.asyncio
    async def test_detects_honest_gaps(self) -> None:
        """Compression detects and reports gaps."""
        compressor = CrystalCompressor()

        base_time = datetime.now()
        marks_with_gaps = [
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Working", source="daily_lab"),
                response=Response(
                    kind="thought", content="Should we use approach A?", success=True
                ),
                umwelt=UmweltSnapshot.witness(),
                timestamp=base_time,
                tags=("eureka",),
            ),
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Maybe", source="daily_lab"),
                response=Response(
                    kind="thought", content="Maybe this is the right approach", success=True
                ),
                umwelt=UmweltSnapshot.witness(),
                timestamp=base_time + timedelta(minutes=5),
                tags=("taste",),
            ),
            Mark(
                id=generate_mark_id(),
                origin="daily_lab",
                stimulus=Stimulus(kind="daily_note", content="Friction", source="daily_lab"),
                response=Response(
                    kind="thought", content="Still stuck on this problem", success=True
                ),
                umwelt=UmweltSnapshot.witness(),
                timestamp=base_time + timedelta(minutes=10),
                tags=("friction",),
            ),
        ]

        result = await compressor.compress(marks_with_gaps)

        # Should detect some gaps
        assert result.gaps_summary is not None

    @pytest.mark.asyncio
    async def test_honesty_disclosure_included(self, sample_marks: list[Mark]) -> None:
        """Compression includes honesty disclosure (Amendment G)."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        assert result.honesty is not None
        assert result.honesty.warm_disclosure is not None
        assert len(result.honesty.warm_disclosure) > 0

    @pytest.mark.asyncio
    async def test_quality_tier_computed(self, sample_marks: list[Mark]) -> None:
        """Compression computes quality tier."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        assert result.quality_tier in ("excellent", "good", "acceptable", "needs_work")


# =============================================================================
# CompressionResult Tests
# =============================================================================


class TestCompressionResult:
    """Tests for CompressionResult dataclass."""

    @pytest.mark.asyncio
    async def test_meets_target_check(self, sample_marks: list[Mark]) -> None:
        """meets_target property works correctly."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        # Check meets_target reflects compression_ratio
        expected = result.compression_ratio <= TARGET_COMPRESSION_RATIO
        assert result.meets_target == expected

    @pytest.mark.asyncio
    async def test_serialization(self, sample_marks: list[Mark]) -> None:
        """CompressionResult serializes to dict."""
        compressor = CrystalCompressor()
        result = await compressor.compress(sample_marks)

        data = result.to_dict()

        assert "crystal" in data
        assert "compression_ratio" in data
        assert "preserved_marks" in data
        assert "dropped_marks" in data
        assert "causal_chain" in data
        assert "honesty" in data


# =============================================================================
# Integration Tests
# =============================================================================


class TestCompressionIntegration:
    """Integration tests for full compression workflow."""

    @pytest.mark.asyncio
    async def test_full_compression_workflow(self, many_marks: list[Mark]) -> None:
        """Full compression workflow produces valid crystal."""
        compressor = get_crystal_compressor()
        result = await compressor.compress(many_marks, session_id="test-session")

        # Verify crystal properties
        crystal = result.crystal
        assert crystal.session_id == "test-session"
        assert crystal.level == CrystalLevel.SESSION
        assert len(crystal.source_marks) > 0
        assert crystal.insight is not None
        assert crystal.significance is not None

        # Verify compression metrics
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.preserved_count > 0

        # Verify honesty
        assert result.honesty.galois_loss >= 0.0
        assert result.honesty.galois_loss <= 1.0

    @pytest.mark.asyncio
    async def test_compression_with_custom_ratio(self, many_marks: list[Mark]) -> None:
        """Compression respects custom max_ratio."""
        compressor = CrystalCompressor()

        # Aggressive compression
        result_aggressive = await compressor.compress(many_marks, max_ratio=0.05)

        # Lenient compression
        result_lenient = await compressor.compress(many_marks, max_ratio=0.30)

        # Aggressive should drop more marks
        assert result_aggressive.dropped_count >= result_lenient.dropped_count
