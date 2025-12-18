"""Tests for joy engine (deterministic personality generation)."""

from __future__ import annotations

import pytest

from agents.i.reactive.joy import (
    CATCHPHRASES,
    CELEBRATIONS,
    FRUSTRATION_TELLS,
    IDLE_ANIMATIONS,
    QUIRKS,
    WORK_STYLES,
    AgentPersonality,
    SerendipityEvent,
    generate_personality,
    hash_string,
    roll_for_serendipity,
    seeded_random,
)


class TestSeededRandom:
    """Tests for seeded PRNG."""

    def test_deterministic_same_seed(self) -> None:
        """Same seed produces same sequence."""
        rng1 = seeded_random(42)
        rng2 = seeded_random(42)

        seq1 = [rng1() for _ in range(10)]
        seq2 = [rng2() for _ in range(10)]

        assert seq1 == seq2

    def test_different_seeds_different_sequence(self) -> None:
        """Different seeds produce different sequences."""
        rng1 = seeded_random(42)
        rng2 = seeded_random(43)

        seq1 = [rng1() for _ in range(10)]
        seq2 = [rng2() for _ in range(10)]

        assert seq1 != seq2

    def test_values_in_range(self) -> None:
        """All values are in [0, 1) range."""
        rng = seeded_random(12345)

        for _ in range(1000):
            value = rng()
            assert 0.0 <= value < 1.0

    def test_reproducible_sequence(self) -> None:
        """Sequence is exactly reproducible."""
        rng = seeded_random(99999)

        # Record first 5 values
        expected = [rng() for _ in range(5)]

        # New RNG with same seed
        rng2 = seeded_random(99999)
        actual = [rng2() for _ in range(5)]

        assert expected == actual


class TestHashString:
    """Tests for string hashing."""

    def test_deterministic(self) -> None:
        """Same string always produces same hash."""
        assert hash_string("agent-001") == hash_string("agent-001")

    def test_different_strings_different_hash(self) -> None:
        """Different strings produce different hashes."""
        h1 = hash_string("agent-001")
        h2 = hash_string("agent-002")

        assert h1 != h2

    def test_empty_string(self) -> None:
        """Empty string produces valid hash."""
        h = hash_string("")
        assert isinstance(h, int)

    def test_returns_positive_int(self) -> None:
        """Hash is always positive."""
        for s in ["test", "hello", "agent-xyz", ""]:
            h = hash_string(s)
            assert h >= 0


class TestGeneratePersonality:
    """Tests for personality generation."""

    def test_deterministic_same_seed(self) -> None:
        """CRITICAL: Same seed produces same personality forever."""
        p1 = generate_personality(42)
        p2 = generate_personality(42)
        p3 = generate_personality(42)

        assert p1 == p2 == p3

    def test_different_seeds_different_personality(self) -> None:
        """Different seeds (usually) produce different personalities."""
        p1 = generate_personality(42)
        p2 = generate_personality(43)

        # At least some fields should differ
        assert p1 != p2

    def test_personality_fields_from_pools(self) -> None:
        """All personality fields come from defined pools."""
        p = generate_personality(12345)

        assert p.quirk in QUIRKS
        assert p.catchphrase in CATCHPHRASES
        assert p.work_style in WORK_STYLES
        assert p.celebration_style in CELEBRATIONS
        assert p.frustration_tell in FRUSTRATION_TELLS
        assert p.idle_animation in IDLE_ANIMATIONS

    def test_personality_is_frozen(self) -> None:
        """AgentPersonality is immutable (frozen dataclass)."""
        p = generate_personality(42)

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            p.quirk = "new quirk"  # type: ignore[misc]

    def test_personality_from_agent_id(self) -> None:
        """Typical usage: hash agent_id to get seed."""
        agent_id = "agent-k-001"
        seed = hash_string(agent_id)
        p1 = generate_personality(seed)

        # Same agent_id -> same personality
        p2 = generate_personality(hash_string(agent_id))
        assert p1 == p2

        # Different agent_id -> different personality
        p3 = generate_personality(hash_string("agent-k-002"))
        assert p1 != p3


class TestRollForSerendipity:
    """Tests for serendipity event rolling."""

    def test_low_entropy_rarely_triggers(self) -> None:
        """Low entropy rarely produces serendipity."""
        # With entropy=0, threshold is 0.95
        # Most rolls should be below this
        hits = 0
        for seed in range(1000):
            result = roll_for_serendipity(seed, entropy=0.0)
            if result is not None:
                hits += 1

        # Should hit less than 15% of the time (allowing for variance)
        assert hits < 150

    def test_high_entropy_more_likely(self) -> None:
        """High entropy makes serendipity more likely."""
        # Use larger sample and different seed ranges for more reliable test
        low_entropy_hits = sum(
            1 for seed in range(10000, 15000) if roll_for_serendipity(seed, entropy=0.1) is not None
        )
        high_entropy_hits = sum(
            1 for seed in range(10000, 15000) if roll_for_serendipity(seed, entropy=0.9) is not None
        )

        # High entropy should have more or equal hits
        # With threshold = 0.95 - entropy*0.3:
        # Low (0.1): threshold = 0.92, ~8% chance
        # High (0.9): threshold = 0.68, ~32% chance
        assert high_entropy_hits >= low_entropy_hits

    def test_serendipity_event_structure(self) -> None:
        """SerendipityEvent has correct structure when returned."""
        # Use high entropy to increase chance of hit
        for seed in range(1000):
            result = roll_for_serendipity(seed, entropy=0.9)
            if result is not None:
                assert isinstance(result, SerendipityEvent)
                assert result.id.startswith("serendipity-")
                assert result.type in (
                    "discovery",
                    "connection",
                    "insight",
                    "flourish",
                    "easter_egg",
                )
                assert result.message
                assert result.duration_ms > 0
                assert result.rarity in ("common", "uncommon", "rare", "legendary")
                break
        else:
            pytest.skip("No serendipity event generated in 1000 rolls")

    def test_serendipity_deterministic_within_time_window(self) -> None:
        """Serendipity is deterministic within same 10-second window."""
        # Note: This test depends on current time, but within a 10-second
        # window, same seed+entropy should give same result
        result1 = roll_for_serendipity(42, entropy=0.9)
        result2 = roll_for_serendipity(42, entropy=0.9)

        # Both should be same (either both None or both same event)
        if result1 is None:
            assert result2 is None
        else:
            assert result2 is not None
            assert result1.type == result2.type
            assert result1.rarity == result2.rarity


class TestSerendipityEvent:
    """Tests for SerendipityEvent dataclass."""

    def test_event_is_frozen(self) -> None:
        """SerendipityEvent is immutable."""
        event = SerendipityEvent(
            id="test-1",
            type="discovery",
            message="Test message",
            visual="sparkle",
            duration_ms=2000,
            rarity="common",
        )

        with pytest.raises(Exception):
            event.message = "changed"  # type: ignore[misc]
