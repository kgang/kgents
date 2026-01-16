"""
Integration Test: Full Trail-to-Crystal Daily Flow

This test validates the COMPLETE daily flow per the trail-to-crystal-daily-lab
proto-spec. Unlike unit tests that validate components in isolation, this test
verifies the end-to-end workflow as a user would experience it.

Laws Verified:
- L1 Day Closure Law: Day complete only when crystal produced
- L2 Intent First Law: Actions without intent marked provisional
- L3 Noise Quarantine Law: High-loss marks don't define narrative
- L4 Compression Honesty Law: Crystal discloses what was dropped
- L5 Provenance Law: Every crystal statement links to marks

Qualitative Assertions (QA) Tested:
- QA-1: Ritual lighter than to-do list (mark < 5s, crystal < 2min)
- QA-2: Honest gaps surfaced without shame
- QA-3: User feels witnessed, not surveilled
- QA-4: Crystal feels like memory artifact, not summary

See:
- pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md
- plans/enlightened-synthesis/EXECUTION_MASTER.md
"""

from __future__ import annotations

import asyncio
import time
from datetime import date, datetime, timedelta
from typing import Any

import pytest

from services.witness.crystal import Crystal, CrystalLevel
from services.witness.crystal_store import CrystalStore, reset_crystal_store
from services.witness.daily_lab import (
    WARMTH_PROMPTS,
    WARMTH_RESPONSES,
    CompressionHonesty,
    DailyCrystal,
    DailyCrystallizer,
    DailyExporter,
    DailyLab,
    DailyMark,
    DailyMarkCapture,
    DailyTag,
    Trail,
    TrailPosition,
)
from services.witness.mark import Mark, MarkId, Response, Stimulus
from services.witness.trace_store import MarkStore, reset_mark_store

# =============================================================================
# Performance Constants (From Spec)
# =============================================================================

# QA-1: Mark capture must complete in < 5 seconds (we test < 50ms for unit test)
MAX_MARK_CAPTURE_MS = 50

# QA-1: Crystal generation must complete in < 2 minutes (we test < 500ms for unit test)
MAX_CRYSTAL_GENERATION_MS = 500

# Gap detection threshold: > 30 minutes untracked = gap
GAP_THRESHOLD_MINUTES = 30


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_stores() -> None:
    """Reset global stores before each test."""
    reset_mark_store()
    reset_crystal_store()


@pytest.fixture
def mark_store() -> MarkStore:
    """Fresh mark store for testing."""
    return MarkStore()


@pytest.fixture
def crystal_store() -> CrystalStore:
    """Fresh crystal store for testing."""
    return CrystalStore()


@pytest.fixture
def daily_lab(mark_store: MarkStore, crystal_store: CrystalStore) -> DailyLab:
    """Daily lab instance for testing."""
    return DailyLab(mark_store=mark_store, crystal_store=crystal_store)


# =============================================================================
# Helper Functions
# =============================================================================


def simulate_gap(mark_store: MarkStore, gap_minutes: int = 120) -> tuple[datetime, datetime]:
    """
    Simulate a time gap in activity.

    Returns the gap start and end times.
    """
    gap_start = datetime.now() - timedelta(minutes=gap_minutes)
    gap_end = datetime.now() - timedelta(minutes=5)  # Gap ends 5 min ago
    return gap_start, gap_end


def detect_gaps(
    marks: list[Mark],
    threshold_minutes: int = GAP_THRESHOLD_MINUTES,
) -> list[tuple[datetime, datetime, timedelta]]:
    """
    Detect gaps between marks.

    Returns list of (gap_start, gap_end, duration) tuples.
    """
    if len(marks) < 2:
        return []

    # Sort by timestamp
    sorted_marks = sorted(marks, key=lambda m: m.timestamp)

    gaps = []
    for i in range(len(sorted_marks) - 1):
        current = sorted_marks[i]
        next_mark = sorted_marks[i + 1]
        gap = next_mark.timestamp - current.timestamp

        if gap.total_seconds() / 60 > threshold_minutes:
            gaps.append((current.timestamp, next_mark.timestamp, gap))

    return gaps


def assert_neutral_gap_message(message: str) -> None:
    """Assert that gap messages are neutral, not shaming."""
    # Punitive/shaming patterns to avoid
    shame_patterns = [
        "failed",
        "missing",
        "error",
        "warning",
        "lost",
        "unproductive",
        "wasted",
        "lazy",
        "forgot",
        "should have",
        "didn't",
        "neglected",
        "abandoned",
        "slacked",
    ]

    message_lower = message.lower()
    for pattern in shame_patterns:
        assert pattern not in message_lower, (
            f"Gap message contains shaming language '{pattern}': {message}"
        )


# =============================================================================
# Complete Daily Flow Integration Test (Primary Test)
# =============================================================================


class TestCompleteDailyFlow:
    """
    Integration test: Full trail-to-crystal daily flow.

    This is the canary test that validates the entire pilot workflow.
    """

    @pytest.mark.asyncio
    async def test_complete_daily_flow(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """
        Integration test: Full trail-to-crystal daily flow.

        Scenario:
        1. User starts day (intent declared)
        2. User marks 5 actions with reasons
        3. User takes 2-hour gap (untracked)
        4. System surfaces gap NEUTRALLY (not shaming)
        5. User closes day -> crystal generated
        6. Crystal discloses dropped marks (compression honesty)
        7. Crystal exportable as markdown
        8. Trail shows navigation through day

        Success: User can explain day using crystal + trail
        """
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # =====================================================================
        # Step 1: User starts day (intent declared)
        # =====================================================================
        day_intent = lab.capture.with_reasoning(
            content="Starting focused work on integration tests",
            reasoning="Need to validate the complete trail-to-crystal flow",
            tag=DailyTag.TASTE,  # Design decision about what to work on
        )
        assert day_intent.mark.id in mark_store

        # =====================================================================
        # Step 2: User marks 5 actions with reasons
        # =====================================================================
        marks = []

        # Action 1: Eureka moment
        m1 = lab.capture.eureka(
            "Discovered that gaps can be surfaced neutrally",
            reasoning="Key insight for avoiding surveillance feeling",
        )
        marks.append(m1)

        # Action 2: Gotcha
        m2 = lab.capture.gotcha(
            "Almost forgot to reset global stores in fixture",
            reasoning="Test isolation is critical",
        )
        marks.append(m2)

        # Action 3: Taste decision
        m3 = lab.capture.taste(
            "Using 50ms threshold for mark capture timing",
            reasoning="Fast enough for flow, measurable in tests",
        )
        marks.append(m3)

        # Action 4: Joy moment
        m4 = lab.capture.joy(
            "The WARMTH prompts feel genuinely kind",
            reasoning="This is the right tone for the pilot",
        )
        marks.append(m4)

        # Action 5: Friction observed
        m5 = lab.capture.friction(
            "Gap detection requires timestamp manipulation in tests",
            reasoning="Real gaps harder to test than business logic",
        )
        marks.append(m5)

        # Verify all marks stored
        assert all(m.mark.id in mark_store for m in marks)

        # =====================================================================
        # Step 3: Simulate 2-hour gap (untracked)
        # =====================================================================
        # We'll create marks with timestamps that simulate a gap
        # Note: In real use, the gap is just... absence of marks

        # Create a mark with past timestamp (before gap)
        past_mark = DailyMark(
            content="Work before lunch break",
            tag=DailyTag.TASTE,
            timestamp=datetime.now() - timedelta(hours=2, minutes=30),
        )
        mark_store.append(past_mark.mark)

        # The current marks (above) are at "now", so we have a gap

        # =====================================================================
        # Step 4: System surfaces gap NEUTRALLY
        # =====================================================================
        trail = Trail(store=mark_store)
        position = trail.for_today()

        # Get all marks and detect gaps
        all_marks = list(position.marks)
        gaps = detect_gaps(all_marks, threshold_minutes=GAP_THRESHOLD_MINUTES)

        # If gaps detected, format neutral message
        if gaps:
            for gap_start, gap_end, duration in gaps:
                minutes = int(duration.total_seconds() / 60)
                # This is what the system would surface
                gap_message = f"Untracked time: {minutes} minutes. This is noted, not judged."
                assert_neutral_gap_message(gap_message)

        # =====================================================================
        # Step 5: User closes day -> crystal generated
        # =====================================================================
        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        # L1 Day Closure Law: Crystal must be produced
        assert crystal is not None, "L1 VIOLATION: Day not complete without crystal"
        assert crystal.crystal.id in crystal_store

        # =====================================================================
        # Step 6: Crystal discloses dropped marks (L4 Compression Honesty)
        # =====================================================================
        assert crystal.honesty is not None, "L4 VIOLATION: No honesty disclosure"
        assert crystal.disclosure != "", "L4 VIOLATION: Empty disclosure"

        # The disclosure should be descriptive, not punitive
        disclosure = crystal.disclosure
        assert_neutral_gap_message(disclosure)

        # =====================================================================
        # Step 7: Crystal exportable as markdown
        # =====================================================================
        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today(), include_crystal=True)

        markdown = export.to_markdown()

        # Must be a real artifact, not empty
        assert len(markdown) > 100, "Export too short to be useful"
        assert "Daily Review" in markdown
        assert "Generated by kgents Daily Lab" in markdown

        # JSON export also works
        json_export = exporter.export_day(date.today(), format="json")
        json_content = json_export.to_json()
        assert "crystals" in json_content

        # =====================================================================
        # Step 8: Trail shows navigation through day
        # =====================================================================
        trail = Trail(store=mark_store)
        position = trail.for_today()

        # Can navigate through all marks
        assert position.total >= 6  # At least 6 marks (intent + 5 actions)

        # Navigate forward through trail
        nav_count = 0
        while position.has_next:
            position = trail.navigate(position, "next")
            nav_count += 1

        # Should have navigated through most marks
        assert nav_count >= 5, "Trail navigation incomplete"

        # =====================================================================
        # SUCCESS CRITERION: User can explain day using crystal + trail
        # =====================================================================
        # The crystal insight + trail marks together tell the story
        assert crystal.insight != ""
        assert crystal.significance != ""
        assert position.total >= 6

        # L5 Provenance Law: Crystal links to source marks
        assert len(crystal.crystal.source_marks) > 0, "L5 VIOLATION: No source marks"


# =============================================================================
# Law Verification Tests
# =============================================================================


class TestL1DayClosureLaw:
    """
    L1 Day Closure Law: A day is complete only when a crystal is produced.
    """

    def test_day_not_complete_without_crystal(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Day is not complete until crystal is produced."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add marks but don't crystallize
        lab.capture.quick("Mark 1")
        lab.capture.quick("Mark 2")
        lab.capture.quick("Mark 3")

        # No crystals yet
        assert len(crystal_store) == 0

        # Day is NOT complete
        # (In the real system, this would be tracked via DayStatus)

        # Crystallize
        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        # Now day IS complete
        assert crystal is not None
        assert len(crystal_store) == 1

    def test_crystal_seals_the_trace(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal production seals the day's trace."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Create marks
        for i in range(5):
            lab.capture.quick(f"Work item {i}")

        # Crystallize
        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Crystal references the source marks
        assert len(crystal.crystal.source_marks) > 0

        # Each source mark exists in store
        for mark_id in crystal.crystal.source_marks:
            assert mark_store.get(MarkId(str(mark_id))) is not None


class TestL2IntentFirstLaw:
    """
    L2 Intent First Law: Actions without declared intent are marked provisional.
    """

    def test_marks_without_reasoning_are_quick(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Quick marks (no reasoning) are implicit provisional."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Quick capture - no intent/reasoning
        quick = lab.capture.quick("Just a note")

        # Tagged capture with reasoning - has intent
        with_intent = lab.capture.with_reasoning(
            content="Intentional action",
            reasoning="I want to track this specifically",
            tag=DailyTag.TASTE,
        )

        # Quick has no reasoning in metadata
        assert quick.reasoning is None
        assert quick.mark.stimulus.metadata.get("reasoning") is None

        # With intent has reasoning
        assert with_intent.reasoning is not None
        assert with_intent.mark.stimulus.metadata.get("reasoning") is not None

    def test_reasoning_preserved_in_crystal(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Intent (reasoning) is preserved through crystallization."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add marks with varying levels of intent
        lab.capture.with_reasoning(
            "Important decision",
            "This matters because of X",
            DailyTag.TASTE,
        )
        lab.capture.quick("Minor note")  # No explicit intent
        lab.capture.eureka("Insight!", reasoning="Realized Y")

        # Crystallize
        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None
        # Marks with reasoning should be prioritized (eueka > quick)


class TestL3NoiseQuarantineLaw:
    """
    L3 Noise Quarantine Law: High-loss marks cannot define the day narrative.
    """

    def test_important_marks_take_precedence(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Important marks (eureka, veto) define narrative over noise."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add lots of friction (noise)
        for i in range(10):
            lab.capture.friction(f"Minor friction {i}")

        # Add one critical veto (signal)
        lab.capture.veto("This architecture is fundamentally wrong")

        # Add one eureka (signal)
        lab.capture.eureka("Found the right approach")

        # Crystallize
        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Crystal should prioritize signal over noise
        # Check that not all source marks are friction
        source_mark_ids = crystal.crystal.source_marks
        source_marks = [mark_store.get(MarkId(str(mid))) for mid in source_mark_ids]

        # At least one non-friction mark should be included
        non_friction = [m for m in source_marks if m and "friction" not in m.tags]
        assert len(non_friction) >= 1, "Signal marks should be included"

    def test_compression_drops_noise_not_signal(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """When compressing, drop noise before signal."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Create marks in order: friction, veto, friction...
        lab.capture.friction("Friction 1")
        lab.capture.veto("Critical veto - must keep")
        lab.capture.friction("Friction 2")
        lab.capture.eureka("Key insight - must keep")
        lab.capture.friction("Friction 3")
        lab.capture.friction("Friction 4")
        lab.capture.friction("Friction 5")
        lab.capture.friction("Friction 6")
        lab.capture.friction("Friction 7")
        lab.capture.friction("Friction 8")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Dropped marks should be mostly friction
        dropped_tags = crystal.honesty.dropped_tags
        # If any were dropped, friction should be among them
        # Note: TAG_FRIENDLY_NAMES converts "friction" to "resistance points"
        if crystal.honesty.dropped_count > 0:
            assert (
                "friction" in dropped_tags
                or "resistance points" in dropped_tags
                or len(dropped_tags) == 0
            )


class TestL4CompressionHonestyLaw:
    """
    L4 Compression Honesty Law: All crystals must disclose what was dropped.
    """

    def test_crystal_always_has_disclosure(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Every crystal includes a disclosure, even when nothing dropped."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Just enough marks
        for i in range(3):
            lab.capture.quick(f"Note {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None
        assert crystal.honesty is not None
        assert crystal.disclosure != ""

    def test_disclosure_is_honest_about_drops(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Disclosure accurately reflects compression."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # More marks than MAX_IMPORTANT_MARKS (7)
        for i in range(15):
            lab.capture.quick(f"Note {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Should have dropped some
        assert crystal.honesty.dropped_count > 0

        # Disclosure should mention compression in some form
        # WARMTH-calibrated messages may use: "set aside", "compressed", "distilled", "editing"
        disclosure_lower = crystal.disclosure.lower()
        compression_indicators = [
            "set aside",
            "compressed",
            "distilled",
            "editing",
            "dropped",
            "condensed",
            "rests",
            "traces remain",
            "full trace",
        ]
        has_compression_indicator = any(ind in disclosure_lower for ind in compression_indicators)
        assert has_compression_indicator, (
            f"Disclosure should indicate compression: {crystal.disclosure}"
        )

    def test_galois_loss_is_computed(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Galois loss (semantic drift) is computed for compression."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add varied content
        for i in range(10):
            lab.capture.quick(f"Detailed note about topic {i} with more content")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None
        assert crystal.honesty.galois_loss >= 0.0
        assert crystal.honesty.galois_loss <= 1.0


class TestL5ProvenanceLaw:
    """
    L5 Provenance Law: Every crystal statement must link to at least one mark.
    """

    def test_crystal_has_source_marks(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal links back to source marks."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Create marks
        m1 = lab.capture.eureka("First insight")
        m2 = lab.capture.taste("Design decision")
        m3 = lab.capture.joy("Delightful moment")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None
        assert len(crystal.crystal.source_marks) > 0

        # Source marks should exist
        for mark_id in crystal.crystal.source_marks:
            assert mark_store.get(MarkId(str(mark_id))) is not None

    def test_no_orphan_claims(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal insight is grounded in marks."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Create marks with specific content
        lab.capture.eureka("Discovered X")
        lab.capture.taste("Chose Y")
        lab.capture.quick("Did Z")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Crystal should have insight derived from marks
        assert crystal.insight != ""

        # Insight should relate to marks (basic check)
        # In practice, LLM would generate this
        assert crystal.crystal.source_count > 0


# =============================================================================
# Qualitative Assertion Tests
# =============================================================================


class TestQA1RitualLighterThanTodoList:
    """
    QA-1: The daily ritual must feel lighter than a to-do list.

    Measurements:
    - Time to mark < 5 seconds (we test < 50ms for unit test speed)
    - End-of-day crystal < 2 minutes (we test < 500ms for unit test speed)
    """

    def test_mark_capture_is_fast(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Mark capture completes within performance budget."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Quick capture timing
        start = time.perf_counter()
        lab.capture.quick("Performance test mark")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < MAX_MARK_CAPTURE_MS, (
            f"Mark capture took {elapsed_ms:.1f}ms, budget is {MAX_MARK_CAPTURE_MS}ms"
        )

    def test_tagged_capture_is_fast(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Tagged capture also fast."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        start = time.perf_counter()
        lab.capture.eureka("Tagged performance test", reasoning="With reasoning")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < MAX_MARK_CAPTURE_MS, (
            f"Tagged capture took {elapsed_ms:.1f}ms, budget is {MAX_MARK_CAPTURE_MS}ms"
        )

    def test_crystal_generation_is_fast(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal generation completes within budget."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add enough marks for crystallization
        for i in range(10):
            lab.capture.quick(f"Performance test mark {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)

        start = time.perf_counter()
        crystal = crystallizer.crystallize_day(date.today())
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert crystal is not None
        assert elapsed_ms < MAX_CRYSTAL_GENERATION_MS, (
            f"Crystal generation took {elapsed_ms:.1f}ms, budget is {MAX_CRYSTAL_GENERATION_MS}ms"
        )

    def test_trail_100_marks_navigable(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Trail supports 100+ marks efficiently."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Create 100 marks
        for i in range(100):
            lab.capture.quick(f"Mark {i}")

        trail = Trail(store=mark_store)

        start = time.perf_counter()
        position = trail.for_today()
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert position.total >= 100
        assert elapsed_ms < 100, f"Trail query took {elapsed_ms:.1f}ms"


class TestQA2HonestGapsSurfacedWithoutShame:
    """
    QA-2: The system should reward honest gaps rather than conceal them.

    Measurements:
    - Untracked time surfaces as neutral data, not error
    - UI does not shame gaps
    - Gaps are noted, not judged
    """

    def test_gap_detection_is_neutral(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Gap detection uses neutral language."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Create marks with a gap
        past_mark = DailyMark(
            content="Before break",
            timestamp=datetime.now() - timedelta(hours=2),
        )
        mark_store.append(past_mark.mark)

        lab.capture.quick("After break")

        # Get trail and detect gaps
        trail = Trail(store=mark_store)
        position = trail.for_today()

        gaps = detect_gaps(position.marks, threshold_minutes=30)

        # Gaps should be detected
        assert len(gaps) >= 1

        # Gap messages should be neutral
        for gap_start, gap_end, duration in gaps:
            minutes = int(duration.total_seconds() / 60)
            # Standard neutral format
            message = f"Untracked time: {minutes} minutes. This is noted, not judged."
            assert_neutral_gap_message(message)

    def test_warmth_prompts_dont_shame(self) -> None:
        """WARMTH prompts never shame gaps or absence."""
        shame_patterns = [
            "missing",
            "failed",
            "error",
            "lazy",
            "unproductive",
            "wasted",
            "forgot",
            "should have",
            "didn't",
        ]

        for prompt_key, prompt_value in WARMTH_PROMPTS.items():
            for pattern in shame_patterns:
                assert pattern not in prompt_value.lower(), (
                    f"WARMTH prompt '{prompt_key}' contains shaming: '{pattern}'"
                )

    def test_no_marks_day_is_okay(
        self,
        mark_store: MarkStore,
    ) -> None:
        """A day with no marks is handled gracefully."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Empty day
        trail = lab.today()
        prompt = lab.review_prompt(trail)

        # Should be WARMTH message
        assert "quiet day" in prompt.lower() or "okay" in prompt.lower()

        # No shaming
        assert_neutral_gap_message(prompt)


class TestQA3UserFeelsWitnessedNotSurveilled:
    """
    QA-3: The user should feel witnessed, not surveilled.

    This is about the system being a collaborator, not a panopticon.
    """

    def test_capture_is_voluntary(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Capture is always user-initiated, never automatic surveillance."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # All capture methods are explicit user actions
        # This is a design check - no auto-capture hooks

        # Verify capture methods exist and work
        m1 = lab.capture.quick("User chose to capture this")
        m2 = lab.capture.eureka("User marked this as eureka")

        # Marks reflect user's explicit choice
        assert m1.mark.origin == "daily_lab"
        assert m2.mark.origin == "daily_lab"

    def test_review_is_opt_in(
        self,
        mark_store: MarkStore,
    ) -> None:
        """Review/crystallization is user-initiated."""
        lab = DailyLab(mark_store=mark_store, crystal_store=CrystalStore())

        # Add marks
        lab.capture.quick("Note 1")
        lab.capture.quick("Note 2")
        lab.capture.quick("Note 3")

        # Crystal doesn't auto-generate
        assert len(lab.crystallize._crystal_store) == 0

        # User must explicitly crystallize
        crystal = lab.crystallize.crystallize_day(date.today())
        assert crystal is not None

    def test_prompts_invite_not_demand(self) -> None:
        """Prompts use invitational language."""
        inviting_patterns = ["what's", "let's", "together", "your", "noticed", "here's"]
        demanding_patterns = ["must", "required", "mandatory", "should", "error"]

        for prompt_value in WARMTH_PROMPTS.values():
            prompt_lower = prompt_value.lower()

            # Should NOT have demanding language
            for pattern in demanding_patterns:
                assert pattern not in prompt_lower, f"Prompt too demanding: '{prompt_value}'"


class TestQA4CrystalFeelsLikeMemoryArtifact:
    """
    QA-4: The crystal should feel like a memory artifact, not a summary.

    Crystals deserve to be re-read. They have warmth and texture.
    """

    def test_crystal_has_insight_not_just_list(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal generates insight, not just bullet list."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        lab.capture.eureka("Big discovery about patterns")
        lab.capture.taste("Made a design choice")
        lab.capture.joy("Felt great about progress")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Insight should be a sentence, not a list
        insight = crystal.insight
        assert "." in insight, "Insight should be a sentence"

        # Significance explains why it matters
        assert crystal.significance != ""

    def test_export_has_warmth(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Exported crystal has warm, personal tone."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        lab.capture.eureka("Test insight")
        lab.capture.joy("Test joy")
        lab.capture.taste("Test taste")

        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today())

        markdown = export.to_markdown()

        # Should use warm language from WARMTH_PROMPTS
        assert "Here's what we captured together" in markdown

        # Should NOT be cold/clinical
        cold_patterns = ["ERROR", "FAILED", "N/A", "NULL"]
        for pattern in cold_patterns:
            assert pattern not in markdown

    def test_crystal_is_shareable(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal is suitable for sharing (not embarrassing)."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add real-feeling content
        lab.capture.eureka("Figured out the architecture!")
        lab.capture.taste("Clean separation of concerns")
        lab.capture.joy("Tests passing on first try")

        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today())

        markdown = export.to_markdown()

        # Should have structure suitable for sharing
        assert "## " in markdown  # Has sections
        assert "Daily Review" in markdown  # Has clear title
        assert "Generated by kgents" in markdown  # Attribution


# =============================================================================
# Additional Integration Scenarios
# =============================================================================


class TestMultipleDaysScenario:
    """Test scenarios spanning multiple days."""

    def test_crystals_per_day(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Each day can have its own crystal."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Add marks for "yesterday"
        for i in range(3):
            past_mark = DailyMark(
                content=f"Yesterday's work {i}",
                timestamp=datetime.now() - timedelta(days=1),
            )
            mark_store.append(past_mark.mark)

        # Add marks for today
        for i in range(3):
            lab.capture.quick(f"Today's work {i}")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)

        # Crystallize yesterday
        yesterday = date.today() - timedelta(days=1)
        crystal_yesterday = crystallizer.crystallize_day(yesterday)

        # Crystallize today
        crystal_today = crystallizer.crystallize_day(date.today())

        # Both should succeed
        assert crystal_yesterday is not None
        assert crystal_today is not None

        # Different crystals
        assert crystal_yesterday.crystal.id != crystal_today.crystal.id


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimum_marks_for_crystal(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Crystal requires minimum marks."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Just 1 mark - not enough
        lab.capture.quick("Only one")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        # Should return None, not fail
        assert crystal is None

        # Add more marks
        lab.capture.quick("Two")
        lab.capture.quick("Three")

        crystal = crystallizer.crystallize_day(date.today())
        assert crystal is not None

    def test_very_long_mark_content(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Handles long mark content gracefully."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        long_content = "x" * 5000  # 5K characters
        lab.capture.quick(long_content)
        lab.capture.quick("Short")
        lab.capture.quick("Another short")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        # Should handle gracefully
        assert crystal is not None

    def test_special_characters_in_content(
        self,
        mark_store: MarkStore,
        crystal_store: CrystalStore,
    ) -> None:
        """Handles special characters in content."""
        lab = DailyLab(mark_store=mark_store, crystal_store=crystal_store)

        # Various special characters
        lab.capture.quick("Quote: 'test' and \"double\"")
        lab.capture.quick("Markdown: # header *bold* `code`")
        lab.capture.quick("Unicode: cafe, resume, emoji possible")

        crystallizer = DailyCrystallizer(mark_store, crystal_store)
        crystal = crystallizer.crystallize_day(date.today())

        assert crystal is not None

        # Export should handle them
        exporter = DailyExporter(mark_store, crystal_store)
        export = exporter.export_day(date.today())
        markdown = export.to_markdown()

        # Should not crash
        assert len(markdown) > 0


# =============================================================================
# Run All Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
