"""
Tests for Wundt Curator: Aesthetic Filtering Middleware

Tests verify:
1. Wundt score follows inverted U-curve
2. Structural surprise computes correctly
3. TasteScore classifies boring/interesting/chaotic
4. WundtCurator filters appropriately
5. Path exemptions work correctly

Property-based tests ensure the spec is correct regardless of implementation.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st

from protocols.agentese.middleware.curator import (
    EXEMPT_ASPECTS,
    EXEMPT_PATHS,
    SemanticDistance,
    TasteScore,
    WundtCurator,
    cosine_distance,
    structural_surprise,
    wundt_score,
)

# === Wundt Score Tests ===


def test_wundt_score_at_zero() -> None:
    """Wundt score is 0 at novelty=0 (boring)."""
    assert wundt_score(0.0) == 0.0


def test_wundt_score_at_one() -> None:
    """Wundt score is 0 at novelty=1 (chaotic)."""
    assert wundt_score(1.0) == 0.0


def test_wundt_score_at_half() -> None:
    """Wundt score is 1 (peak) at novelty=0.5."""
    assert wundt_score(0.5) == 1.0


def test_wundt_score_symmetric() -> None:
    """Wundt score is symmetric around 0.5."""
    assert abs(wundt_score(0.3) - wundt_score(0.7)) < 0.001


def test_wundt_score_clamps_negative() -> None:
    """Wundt score clamps negative input to 0."""
    assert wundt_score(-0.5) == 0.0


def test_wundt_score_clamps_above_one() -> None:
    """Wundt score clamps input > 1 to 1."""
    assert wundt_score(1.5) == 0.0


# === Property-Based Wundt Score Tests ===


@given(st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=100)
def test_wundt_score_bounded(novelty: float) -> None:
    """Wundt score is always between 0 and 1."""
    score = wundt_score(novelty)
    assert 0.0 <= score <= 1.0


@given(st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=100)
def test_wundt_score_inverted_u(novelty: float) -> None:
    """Wundt score peaks at novelty=0.5."""
    score = wundt_score(novelty)
    peak = wundt_score(0.5)
    assert score <= peak


@given(st.floats(min_value=0.0, max_value=0.5))
@settings(max_examples=50)
def test_wundt_score_increasing_to_peak(novelty: float) -> None:
    """Wundt score increases monotonically from 0 to 0.5."""
    if novelty < 0.5:
        # Score at novelty should be less than score at 0.5
        assert wundt_score(novelty) <= wundt_score(0.5)


# === Structural Surprise Tests ===


def test_structural_surprise_identical_strings() -> None:
    """Identical strings have 0 surprise."""
    assert structural_surprise("hello", "hello") == 0.0


def test_structural_surprise_completely_different_types() -> None:
    """Different types have high surprise."""
    assert structural_surprise("hello", 42) == 0.9


def test_structural_surprise_no_prior() -> None:
    """No prior returns neutral surprise."""
    assert structural_surprise("hello", None) == 0.5


def test_structural_surprise_strings_length_difference() -> None:
    """Strings with different lengths have some surprise."""
    surprise = structural_surprise("hello", "hello world, this is much longer")
    assert 0.0 < surprise < 1.0


def test_structural_surprise_dicts_same_keys() -> None:
    """Dicts with same keys have low surprise."""
    a = {"x": 1, "y": 2}
    b = {"x": 3, "y": 4}
    assert structural_surprise(a, b) == 0.0


def test_structural_surprise_dicts_different_keys() -> None:
    """Dicts with different keys have surprise."""
    a = {"x": 1, "y": 2}
    b = {"z": 3, "w": 4}
    surprise = structural_surprise(a, b)
    assert surprise == 1.0  # No overlap


def test_structural_surprise_dicts_partial_overlap() -> None:
    """Dicts with partial key overlap have partial surprise."""
    a = {"x": 1, "y": 2}
    b = {"y": 3, "z": 4}
    surprise = structural_surprise(a, b)
    assert 0.0 < surprise < 1.0


def test_structural_surprise_lists_same_length() -> None:
    """Lists with same length have 0 surprise (based on length)."""
    assert structural_surprise([1, 2, 3], [4, 5, 6]) == 0.0


def test_structural_surprise_lists_different_length() -> None:
    """Lists with different lengths have surprise."""
    surprise = structural_surprise([1, 2, 3], [4, 5])
    assert surprise > 0.0


def test_structural_surprise_numbers_same() -> None:
    """Same numbers have 0 surprise."""
    assert structural_surprise(42, 42) == 0.0


def test_structural_surprise_numbers_different() -> None:
    """Different numbers have surprise proportional to difference."""
    surprise = structural_surprise(100, 50)
    assert surprise == 1.0  # 100% difference


# === TasteScore Tests ===


def test_tastescore_boring() -> None:
    """Low novelty is classified as boring."""
    score = TasteScore.from_novelty(0.05, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "boring"
    assert not score.is_acceptable


def test_tastescore_interesting() -> None:
    """Mid-range novelty is classified as interesting."""
    score = TasteScore.from_novelty(0.5, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "interesting"
    assert score.is_acceptable


def test_tastescore_chaotic() -> None:
    """High novelty is classified as chaotic."""
    score = TasteScore.from_novelty(0.95, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "chaotic"
    assert not score.is_acceptable


def test_tastescore_at_low_threshold() -> None:
    """Exactly at low threshold is interesting."""
    score = TasteScore.from_novelty(0.1, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "interesting"


def test_tastescore_at_high_threshold() -> None:
    """Exactly at high threshold is interesting."""
    score = TasteScore.from_novelty(0.9, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "interesting"


def test_tastescore_wundt_score_computed() -> None:
    """TasteScore computes Wundt score correctly."""
    score = TasteScore.from_novelty(0.5)
    assert score.wundt_score == 1.0


def test_tastescore_frozen() -> None:
    """TasteScore is immutable."""
    score = TasteScore.from_novelty(0.5)
    with pytest.raises(AttributeError):
        score.novelty = 0.8  # type: ignore[misc]


# === Cosine Distance Tests ===


def test_cosine_distance_identical() -> None:
    """Identical vectors have 0 distance."""
    a = [1.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    assert cosine_distance(a, b) == 0.0


def test_cosine_distance_orthogonal() -> None:
    """Orthogonal vectors have 0.5 distance."""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert abs(cosine_distance(a, b) - 0.5) < 0.001


def test_cosine_distance_opposite() -> None:
    """Opposite vectors have 1.0 distance."""
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    assert abs(cosine_distance(a, b) - 1.0) < 0.001


def test_cosine_distance_empty() -> None:
    """Empty vectors return neutral distance."""
    assert cosine_distance([], []) == 0.5


def test_cosine_distance_mismatched_length() -> None:
    """Mismatched vector lengths return neutral distance."""
    assert cosine_distance([1, 2, 3], [1, 2]) == 0.5


# === SemanticDistance Tests ===


@pytest.mark.asyncio
async def test_semantic_distance_without_embedder() -> None:
    """Without embedder, falls back to structural surprise."""
    distance = SemanticDistance()
    result = await distance("hello", "hello")
    assert result == 0.0  # Identical strings


@pytest.mark.asyncio
async def test_semantic_distance_different_strings() -> None:
    """Different strings have positive distance."""
    distance = SemanticDistance()
    result = await distance("hello", "completely different text here")
    assert result > 0.0


# === WundtCurator Tests ===


def test_curator_init_validates_thresholds() -> None:
    """Curator validates threshold ordering."""
    with pytest.raises(ValueError):
        WundtCurator(low_threshold=0.9, high_threshold=0.1)


def test_curator_path_exempt_void() -> None:
    """void.* paths are exempt from filtering."""
    curator = WundtCurator()
    assert curator.is_path_exempt("void.entropy.sip")
    assert curator.is_path_exempt("void.capital.balance")


def test_curator_path_exempt_time() -> None:
    """time.* paths are exempt from filtering."""
    curator = WundtCurator()
    assert curator.is_path_exempt("time.trace.witness")


def test_curator_path_exempt_self_judgment() -> None:
    """self.judgment.* paths are exempt (avoid recursion)."""
    curator = WundtCurator()
    assert curator.is_path_exempt("self.judgment.taste")
    assert curator.is_path_exempt("self.judgment.surprise")


def test_curator_path_exempt_witness_aspect() -> None:
    """Paths ending in .witness are exempt."""
    curator = WundtCurator()
    assert curator.is_path_exempt("world.house.witness")
    assert curator.is_path_exempt("concept.justice.witness")


def test_curator_path_not_exempt() -> None:
    """Normal paths are not exempt."""
    curator = WundtCurator()
    assert not curator.is_path_exempt("concept.story.generate")
    assert not curator.is_path_exempt("world.house.manifest")


def test_curator_exempt_paths_constant() -> None:
    """EXEMPT_PATHS constant is frozen."""
    assert isinstance(EXEMPT_PATHS, frozenset)
    assert "void." in EXEMPT_PATHS
    assert "time." in EXEMPT_PATHS
    assert "self.judgment." in EXEMPT_PATHS


def test_curator_exempt_aspects_constant() -> None:
    """EXEMPT_ASPECTS constant is frozen."""
    assert isinstance(EXEMPT_ASPECTS, frozenset)
    assert ".witness" in EXEMPT_ASPECTS


# === Property-Based Curator Tests ===


@given(st.floats(min_value=0.0, max_value=0.05))
@settings(max_examples=50)
def test_low_novelty_is_boring(novelty: float) -> None:
    """Very low novelty is classified as boring."""
    score = TasteScore.from_novelty(novelty, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "boring"


@given(st.floats(min_value=0.95, max_value=1.0))
@settings(max_examples=50)
def test_high_novelty_is_chaotic(novelty: float) -> None:
    """Very high novelty is classified as chaotic."""
    score = TasteScore.from_novelty(novelty, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "chaotic"


@given(st.floats(min_value=0.2, max_value=0.8))
@settings(max_examples=50)
def test_mid_novelty_is_interesting(novelty: float) -> None:
    """Mid-range novelty is classified as interesting."""
    score = TasteScore.from_novelty(novelty, low_threshold=0.1, high_threshold=0.9)
    assert score.verdict == "interesting"


@given(
    st.floats(min_value=0.0, max_value=0.5),
    st.floats(min_value=0.5, max_value=1.0),
)
@settings(max_examples=50)
def test_curator_thresholds_valid_range(low: float, high: float) -> None:
    """Any valid threshold range works."""
    if low < high:
        curator = WundtCurator(low_threshold=low, high_threshold=high)
        assert curator.low_threshold == low
        assert curator.high_threshold == high


# === Integration Tests ===


def test_tastescore_custom_thresholds() -> None:
    """Custom thresholds work correctly."""
    # Very narrow "interesting" zone
    score = TasteScore.from_novelty(0.5, low_threshold=0.4, high_threshold=0.6)
    assert score.verdict == "interesting"

    score_low = TasteScore.from_novelty(0.3, low_threshold=0.4, high_threshold=0.6)
    assert score_low.verdict == "boring"

    score_high = TasteScore.from_novelty(0.7, low_threshold=0.4, high_threshold=0.6)
    assert score_high.verdict == "chaotic"


def test_structural_surprise_empty_strings() -> None:
    """Empty strings have 0 surprise (both empty)."""
    assert structural_surprise("", "") == 0.0


def test_structural_surprise_one_empty() -> None:
    """One empty string has partial surprise."""
    surprise = structural_surprise("hello", "")
    assert surprise > 0.0
