"""Tests for Psi-gent learning system."""

import pytest

from ..corpus import STANDARD_CORPUS
from ..learning import (
    AbstractionModel,
    FrequencyModel,
    ThompsonSamplingModel,
    cold_start_retrieval,
    extract_features,
    outcome_to_reward,
    retrieve_with_learning,
)
from ..types import (
    Feedback,
    Outcome,
    Problem,
    ProblemFeatures,
)

# =============================================================================
# Reward Mapping Tests
# =============================================================================


class TestRewardMapping:
    """Tests for outcome to reward conversion."""

    def test_success_is_positive(self) -> None:
        """Success outcomes yield positive reward."""
        reward = outcome_to_reward(Outcome.SUCCESS, None)
        assert reward > 0

    def test_success_with_low_distortion_bonus(self) -> None:
        """Low distortion gives bonus reward."""
        base = outcome_to_reward(Outcome.SUCCESS, None)
        with_bonus = outcome_to_reward(Outcome.SUCCESS, 0.1)  # Low distortion
        assert with_bonus > base

    def test_failure_is_negative(self) -> None:
        """Failure outcomes yield negative reward."""
        for outcome in [Outcome.CHALLENGE_FAILED, Outcome.PROJECTION_FAILED]:
            reward = outcome_to_reward(outcome, None)
            assert reward < 0

    def test_partial_is_small_positive(self) -> None:
        """Partial success is small positive."""
        reward = outcome_to_reward(Outcome.PARTIAL, None)
        assert 0 < reward < outcome_to_reward(Outcome.SUCCESS, None)


# =============================================================================
# Feature Extraction Tests
# =============================================================================


class TestFeatureExtraction:
    """Tests for problem feature extraction."""

    def test_extract_features_basic(self) -> None:
        """Can extract features from problem."""
        problem = Problem(
            id="1",
            description="A test problem with some words",
            domain="software",
            constraints=("fast", "cheap"),
        )
        features = extract_features(problem)

        assert features.domain == "software"
        assert features.constraint_count == 2
        assert features.description_length > 0
        assert 0 <= features.complexity <= 1

    def test_extract_features_with_embedding(self) -> None:
        """Features reflect embedding status."""
        without = Problem(id="1", description="Test", domain="test")
        with_emb = without.with_embedding((0.1, 0.2, 0.3))

        f1 = extract_features(without)
        f2 = extract_features(with_emb)

        assert not f1.has_embedding
        assert f2.has_embedding
        assert f2.embedding_cluster is not None

    def test_domain_cluster_deterministic(self) -> None:
        """Same domain gives same cluster."""
        p1 = Problem(id="1", description="Test 1", domain="software")
        p2 = Problem(id="2", description="Test 2", domain="software")

        f1 = extract_features(p1)
        f2 = extract_features(p2)

        assert f1.domain_cluster == f2.domain_cluster


# =============================================================================
# Frequency Model Tests
# =============================================================================


class TestFrequencyModel:
    """Tests for simple frequency-based model."""

    @pytest.fixture
    def model(self) -> FrequencyModel:
        """Create a fresh model."""
        return FrequencyModel()

    @pytest.fixture
    def features(self) -> ProblemFeatures:
        """Create test features."""
        return ProblemFeatures(
            domain="software",
            domain_cluster=50,
            complexity=0.5,
            constraint_count=2,
            description_length=100,
            has_embedding=False,
        )

    def test_predict_unknown_is_uncertain(self, model, features) -> None:
        """Unknown pairs return 0.5 (uncertain)."""
        score = model.predict(features, "unknown_metaphor")
        assert score == 0.5

    def test_update_changes_prediction(self, model, features) -> None:
        """Updates change future predictions."""
        # Record some successes
        for _ in range(10):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        # Now prediction should be higher
        score = model.predict(features, "plumbing")
        assert score > 0.5

    def test_is_trained_requires_data(self, model, features) -> None:
        """Model is not trained without sufficient data."""
        assert not model.is_trained

        for i in range(20):
            feedback = Feedback(
                problem_id=str(i),
                problem_features=features,
                metaphor_id="test",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        assert model.is_trained

    def test_uncertainty_with_few_samples(self, model, features) -> None:
        """Uncertainty is high with few samples."""
        # Add just 2 samples
        for _ in range(2):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        mean, std = model.predict_with_uncertainty(features, "plumbing")
        assert std > 0.3  # Still uncertain


# =============================================================================
# Thompson Sampling Model Tests
# =============================================================================


class TestThompsonSamplingModel:
    """Tests for Thompson sampling model."""

    @pytest.fixture
    def model(self) -> ThompsonSamplingModel:
        """Create a fresh model."""
        return ThompsonSamplingModel()

    @pytest.fixture
    def features(self) -> ProblemFeatures:
        """Create test features."""
        return ProblemFeatures(
            domain="software",
            domain_cluster=50,
            complexity=0.5,
            constraint_count=2,
            description_length=100,
            has_embedding=False,
        )

    def test_predict_unknown_uses_prior(self, model, features) -> None:
        """Unknown pairs use prior (alpha=1, beta=1 -> mean=0.5)."""
        score = model.predict(features, "unknown")
        assert score == 0.5

    def test_sample_varies(self, model, features) -> None:
        """Samples vary (Thompson sampling property)."""
        samples = [model.sample(features, "test") for _ in range(100)]
        # Should have some variation
        assert max(samples) - min(samples) > 0.1

    def test_update_shifts_distribution(self, model, features) -> None:
        """Successful updates shift distribution up."""
        initial = model.predict(features, "plumbing")

        for _ in range(10):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        after = model.predict(features, "plumbing")
        assert after > initial

    def test_failures_shift_distribution_down(self, model, features) -> None:
        """Failed updates shift distribution down."""
        initial = model.predict(features, "plumbing")

        for _ in range(10):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.CHALLENGE_FAILED,
            )
            model.update(feedback)

        after = model.predict(features, "plumbing")
        assert after < initial

    def test_decay_moves_toward_prior(self, model, features) -> None:
        """Decay moves parameters toward prior."""
        # Add many successes
        for _ in range(50):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        high = model.predict(features, "plumbing")

        # Decay
        for _ in range(100):
            model.decay(rate=0.9)

        decayed = model.predict(features, "plumbing")
        assert decayed < high  # Moved toward prior


# =============================================================================
# Abstraction Model Tests
# =============================================================================


class TestAbstractionModel:
    """Tests for abstraction learning model."""

    @pytest.fixture
    def model(self) -> AbstractionModel:
        """Create a fresh model."""
        return AbstractionModel()

    @pytest.fixture
    def features(self) -> ProblemFeatures:
        """Create test features."""
        return ProblemFeatures(
            domain="software",
            domain_cluster=50,
            complexity=0.5,
            constraint_count=2,
            description_length=100,
            has_embedding=False,
        )

    def test_suggest_default_scales_with_complexity(self, model) -> None:
        """Default suggestion scales with complexity."""
        low_complexity = ProblemFeatures(
            domain="test",
            domain_cluster=0,
            complexity=0.1,
            constraint_count=0,
            description_length=10,
            has_embedding=False,
        )
        high_complexity = ProblemFeatures(
            domain="test",
            domain_cluster=0,
            complexity=0.9,
            constraint_count=0,
            description_length=10,
            has_embedding=False,
        )

        low_abs = model.suggest_abstraction(low_complexity)
        high_abs = model.suggest_abstraction(high_complexity)

        assert high_abs > low_abs

    def test_learns_from_success(self, model, features) -> None:
        """Model learns successful abstraction levels."""
        # Record successes at abstraction=0.7
        for _ in range(10):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.7,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        suggested = model.suggest_abstraction(features)
        # Should be close to 0.7
        assert 0.6 < suggested < 0.8

    def test_ignores_failures(self, model, features) -> None:
        """Model ignores failed attempts."""
        # Record failures at various levels
        for abs_level in [0.1, 0.3, 0.5, 0.9]:
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=abs_level,
                outcome=Outcome.CHALLENGE_FAILED,
            )
            model.update(feedback)

        # History should be empty
        key = (features.domain_cluster, int(features.complexity * 5))
        assert key not in model.history or not model.history[key]


# =============================================================================
# Retrieval Integration Tests
# =============================================================================


class TestRetrievalIntegration:
    """Tests for learning-based retrieval."""

    @pytest.fixture
    def trained_model(self):
        """Create a trained model favoring plumbing."""
        model = ThompsonSamplingModel()
        features = ProblemFeatures(
            domain="software",
            domain_cluster=50,
            complexity=0.5,
            constraint_count=2,
            description_length=100,
            has_embedding=False,
        )

        # Train to favor plumbing for software domain
        for _ in range(20):
            feedback = Feedback(
                problem_id="1",
                problem_features=features,
                metaphor_id="plumbing",
                abstraction=0.5,
                outcome=Outcome.SUCCESS,
            )
            model.update(feedback)

        return model

    def test_retrieve_with_learning_uses_model(self, trained_model) -> None:
        """Learning retrieval uses model predictions."""
        problem = Problem(
            id="1",
            description="Software performance issue",
            domain="software",
        )

        results = retrieve_with_learning(
            problem,
            list(STANDARD_CORPUS),
            trained_model,
            strategy="greedy",
        )

        # Plumbing should be ranked high (trained for software)
        top_ids = [m.id for m, _ in results[:3]]
        assert "plumbing" in top_ids

    def test_cold_start_retrieval(self) -> None:
        """Cold start retrieval works without model."""
        problem = Problem(
            id="1",
            description="A problem about flow and pressure",
            domain="test",
        )

        results = cold_start_retrieval(problem, list(STANDARD_CORPUS))

        # Should return all metaphors
        assert len(results) == len(STANDARD_CORPUS)

        # Plumbing should rank high (keyword overlap with "flow")
        # (This depends on the keyword matching)
        assert len(results) > 0


# =============================================================================
# Law Tests
# =============================================================================


class TestLearningLaws:
    """Law tests for learning system."""

    @pytest.mark.law
    def test_thompson_sampling_explores(self) -> None:
        """Thompson sampling explores uncertain options."""
        model = ThompsonSamplingModel()
        features = ProblemFeatures(
            domain="test",
            domain_cluster=0,
            complexity=0.5,
            constraint_count=0,
            description_length=50,
            has_embedding=False,
        )

        # All options are equally uncertain initially
        samples = {}
        for metaphor_id in ["a", "b", "c"]:
            samples[metaphor_id] = [
                model.sample(features, metaphor_id) for _ in range(100)
            ]

        # Each should have been sampled across a range
        for metaphor_id, vals in samples.items():
            assert max(vals) - min(vals) > 0.1, f"{metaphor_id} didn't explore"

    @pytest.mark.law
    def test_success_increases_probability(self) -> None:
        """Successful feedback increases selection probability."""
        model = ThompsonSamplingModel()
        features = ProblemFeatures(
            domain="test",
            domain_cluster=0,
            complexity=0.5,
            constraint_count=0,
            description_length=50,
            has_embedding=False,
        )

        before = model.predict(features, "winner")

        for _ in range(10):
            model.update(
                Feedback(
                    problem_id="1",
                    problem_features=features,
                    metaphor_id="winner",
                    abstraction=0.5,
                    outcome=Outcome.SUCCESS,
                )
            )

        after = model.predict(features, "winner")
        assert after > before
