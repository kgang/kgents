# Learning and Adaptation

> Get better at finding the right metaphor over time.

---

## Purpose

The Morphic Engine should learn from experience. Which metaphors work for which problem types? What abstraction levels succeed? This is the LEARN stage that runs in the background.

**The core insight**: Metaphor selection is a contextual bandit problem.

---

## The Learning Problem

At each problem:
- **Context**: Problem features (domain, complexity, embedding cluster)
- **Actions**: Which metaphor to try
- **Reward**: Did it verify successfully? How low was distortion?

This is different from simple frequency counting because:
1. Different problems need different metaphors
2. We want to explore new metaphors, not just exploit known good ones
3. Reward is delayed (we don't know until after VERIFY)

---

## Feedback Signal

```python
@dataclass(frozen=True)
class Feedback:
    """Feedback from a completed solve attempt."""

    problem_id: str
    problem_features: ProblemFeatures
    metaphor_id: str
    abstraction: float
    outcome: Outcome
    distortion: float | None
    time_to_solve_ms: int

class Outcome(Enum):
    SUCCESS = "success"                 # Verified, distortion acceptable
    PARTIAL = "partial"                 # Verified but high distortion
    CHALLENGE_FAILED = "challenge_failed"  # Metaphor broke under stress
    PROJECTION_FAILED = "projection_failed"  # Couldn't map problem
    SOLVE_FAILED = "solve_failed"       # Operations didn't help
    VERIFY_FAILED = "verify_failed"     # Solution didn't fit problem
```

### Reward Mapping

```python
def outcome_to_reward(outcome: Outcome, distortion: float | None) -> float:
    """Convert outcome to reward signal."""

    base_rewards = {
        Outcome.SUCCESS: 1.0,
        Outcome.PARTIAL: 0.3,
        Outcome.CHALLENGE_FAILED: -0.3,
        Outcome.PROJECTION_FAILED: -0.5,
        Outcome.SOLVE_FAILED: -0.2,
        Outcome.VERIFY_FAILED: -0.1,
    }

    reward = base_rewards[outcome]

    # Bonus/penalty based on distortion
    if outcome == Outcome.SUCCESS and distortion is not None:
        # Lower distortion = higher reward
        reward += (1.0 - distortion) * 0.3

    return reward
```

---

## Problem Features

What features of the problem predict metaphor success?

```python
@dataclass(frozen=True)
class ProblemFeatures:
    """Features extracted from a problem for learning."""

    domain: str                    # Problem domain
    domain_cluster: int            # Embedding-based cluster ID
    complexity: float              # 0.0 to 1.0
    constraint_count: int          # Number of constraints
    description_length: int        # Rough problem size
    has_embedding: bool            # Whether L-gent embedding exists
    embedding_cluster: int | None  # Cluster in embedding space

def extract_features(problem: Problem) -> ProblemFeatures:
    """Extract learning features from a problem."""

    # Domain cluster via simple hashing (or actual clustering)
    domain_cluster = hash(problem.domain) % 100

    # Embedding cluster if available
    embedding_cluster = None
    if problem.embedding:
        embedding_cluster = cluster_embedding(problem.embedding)

    return ProblemFeatures(
        domain=problem.domain,
        domain_cluster=domain_cluster,
        complexity=problem.complexity,
        constraint_count=len(problem.constraints),
        description_length=len(problem.description),
        has_embedding=problem.embedding is not None,
        embedding_cluster=embedding_cluster,
    )
```

---

## Retrieval Model Interface

```python
class RetrievalModel(Protocol):
    """Interface for learned metaphor retrieval."""

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Predict expected reward for (features, metaphor) pair."""
        ...

    def predict_with_uncertainty(
        self, features: ProblemFeatures, metaphor_id: str
    ) -> tuple[float, float]:
        """Predict expected reward and uncertainty."""
        ...

    def update(self, feedback: Feedback) -> None:
        """Update model with new feedback."""
        ...

    @property
    def is_trained(self) -> bool:
        """Has the model seen enough data to be useful?"""
        ...
```

---

## Model Implementations

### Level 1: Frequency Counting

Simplest approach. Track success rate per (domain, metaphor) pair.

```python
@dataclass
class FrequencyModel:
    """Simple frequency-based model."""

    counts: dict[tuple[str, str], tuple[int, int]] = field(default_factory=dict)
    # (domain, metaphor_id) → (successes, total)

    min_samples: int = 5

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        key = (features.domain, metaphor_id)
        if key not in self.counts:
            return 0.5  # Prior: uncertain
        successes, total = self.counts[key]
        if total < self.min_samples:
            return 0.5  # Not enough data
        return successes / total

    def update(self, feedback: Feedback) -> None:
        key = (feedback.problem_features.domain, feedback.metaphor_id)
        successes, total = self.counts.get(key, (0, 0))
        if feedback.outcome == Outcome.SUCCESS:
            successes += 1
        total += 1
        self.counts[key] = (successes, total)

    @property
    def is_trained(self) -> bool:
        return sum(t for _, t in self.counts.values()) >= 20
```

### Level 2: Linear Contextual Bandit

Use features to generalize across similar problems.

```python
@dataclass
class LinearBanditModel:
    """Linear model for contextual bandits."""

    # Per-metaphor weight vectors
    weights: dict[str, np.ndarray] = field(default_factory=dict)
    feature_dim: int = 10
    learning_rate: float = 0.1
    regularization: float = 0.01

    def _featurize(self, features: ProblemFeatures) -> np.ndarray:
        """Convert problem features to fixed-size vector."""
        return np.array([
            features.complexity,
            features.constraint_count / 10.0,
            features.description_length / 1000.0,
            float(features.has_embedding),
            (features.embedding_cluster or 0) / 100.0,
            features.domain_cluster / 100.0,
            # Add bias term
            1.0,
            # Padding
            0.0, 0.0, 0.0
        ])[:self.feature_dim]

    def _get_weights(self, metaphor_id: str) -> np.ndarray:
        if metaphor_id not in self.weights:
            self.weights[metaphor_id] = np.zeros(self.feature_dim)
        return self.weights[metaphor_id]

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        x = self._featurize(features)
        w = self._get_weights(metaphor_id)
        return float(np.clip(np.dot(w, x), 0.0, 1.0))

    def update(self, feedback: Feedback) -> None:
        x = self._featurize(feedback.problem_features)
        w = self._get_weights(feedback.metaphor_id)
        reward = outcome_to_reward(feedback.outcome, feedback.distortion)

        # Gradient descent update
        prediction = np.dot(w, x)
        error = reward - prediction
        gradient = error * x - self.regularization * w
        self.weights[feedback.metaphor_id] = w + self.learning_rate * gradient

    @property
    def is_trained(self) -> bool:
        total_updates = sum(np.abs(w).sum() > 0.1 for w in self.weights.values())
        return total_updates >= 5
```

### Level 3: Thompson Sampling

Balance exploration and exploitation properly.

```python
@dataclass
class ThompsonSamplingModel:
    """Thompson sampling for exploration/exploitation."""

    # Per (domain, metaphor) Beta distribution parameters
    alphas: dict[tuple[str, str], float] = field(default_factory=dict)
    betas: dict[tuple[str, str], float] = field(default_factory=dict)

    prior_alpha: float = 1.0  # Initial optimism
    prior_beta: float = 1.0

    def _get_params(self, key: tuple[str, str]) -> tuple[float, float]:
        alpha = self.alphas.get(key, self.prior_alpha)
        beta = self.betas.get(key, self.prior_beta)
        return alpha, beta

    def predict(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Return mean of Beta distribution (expected reward)."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        return alpha / (alpha + beta)

    def predict_with_uncertainty(
        self, features: ProblemFeatures, metaphor_id: str
    ) -> tuple[float, float]:
        """Return mean and standard deviation."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        return mean, np.sqrt(variance)

    def sample(self, features: ProblemFeatures, metaphor_id: str) -> float:
        """Sample from the posterior (for Thompson sampling)."""
        key = (features.domain, metaphor_id)
        alpha, beta = self._get_params(key)
        return np.random.beta(alpha, beta)

    def update(self, feedback: Feedback) -> None:
        key = (feedback.problem_features.domain, feedback.metaphor_id)
        alpha, beta = self._get_params(key)

        # Binary reward for Beta distribution
        if feedback.outcome == Outcome.SUCCESS:
            self.alphas[key] = alpha + 1
            self.betas[key] = beta
        else:
            self.alphas[key] = alpha
            self.betas[key] = beta + 1

    @property
    def is_trained(self) -> bool:
        total_observations = sum(
            self.alphas.get(k, 1) + self.betas.get(k, 1) - 2
            for k in set(self.alphas.keys()) | set(self.betas.keys())
        )
        return total_observations >= 20
```

---

## Using Learning in Retrieval

```python
def retrieve_with_learning(
    problem: Problem,
    corpus: list[Metaphor],
    model: RetrievalModel,
    strategy: str = "thompson"  # or "ucb" or "greedy"
) -> list[tuple[Metaphor, float]]:
    """Retrieval informed by learning model."""

    features = extract_features(problem)
    scored = []

    for metaphor in corpus:
        if strategy == "thompson" and hasattr(model, 'sample'):
            # Thompson sampling: sample from posterior
            score = model.sample(features, metaphor.id)
        elif strategy == "ucb":
            # Upper confidence bound
            mean, std = model.predict_with_uncertainty(features, metaphor.id)
            score = mean + 2.0 * std  # UCB with confidence 2
        else:
            # Greedy: use expected reward
            score = model.predict(features, metaphor.id)

        scored.append((metaphor, score))

    return sorted(scored, key=lambda x: x[1], reverse=True)
```

---

## Abstraction Learning

Also learn what abstraction level works for different problem types.

```python
@dataclass
class AbstractionModel:
    """Learn optimal abstraction level per problem type."""

    # (domain_cluster, complexity_bucket) → successful abstraction levels
    history: dict[tuple[int, int], list[float]] = field(default_factory=dict)

    def _bucket_complexity(self, complexity: float) -> int:
        """Bucket complexity into discrete levels."""
        return int(complexity * 5)  # 0, 1, 2, 3, 4

    def suggest_abstraction(self, features: ProblemFeatures) -> float:
        """Suggest abstraction level based on history."""
        key = (features.domain_cluster, self._bucket_complexity(features.complexity))

        if key not in self.history or not self.history[key]:
            # Default: scale with complexity
            return 0.3 + features.complexity * 0.4

        # Return median of successful abstractions
        successful = self.history[key]
        return float(np.median(successful))

    def update(self, feedback: Feedback) -> None:
        if feedback.outcome != Outcome.SUCCESS:
            return

        key = (
            feedback.problem_features.domain_cluster,
            self._bucket_complexity(feedback.problem_features.complexity)
        )

        if key not in self.history:
            self.history[key] = []
        self.history[key].append(feedback.abstraction)
```

---

## Integration with D-gent

Persist learning state using D-gent:

```python
class PersistentLearningModel:
    """Learning model with D-gent persistence."""

    def __init__(self, d_gent: DataAgent, model: RetrievalModel):
        self.d_gent = d_gent
        self.model = model
        self._load()

    def _load(self) -> None:
        """Load model state from D-gent."""
        state = self.d_gent.get("psi_learning_state")
        if state:
            self.model = deserialize_model(state, type(self.model))

    def _save(self) -> None:
        """Save model state to D-gent."""
        state = serialize_model(self.model)
        self.d_gent.set("psi_learning_state", state)

    def update(self, feedback: Feedback) -> None:
        self.model.update(feedback)
        self._save()  # Persist after each update
```

---

## Cold Start Strategy

When the model has no data:

```python
def cold_start_retrieval(
    problem: Problem,
    corpus: list[Metaphor]
) -> list[tuple[Metaphor, float]]:
    """Retrieval when learning model has no data."""

    # Fall back to embedding similarity
    if problem.embedding:
        return retrieve_by_embedding(problem, corpus)

    # Fall back to domain matching
    scored = []
    for metaphor in corpus:
        # Score by domain keyword overlap
        problem_words = set(problem.description.lower().split())
        metaphor_words = set(metaphor.description.lower().split())
        overlap = len(problem_words & metaphor_words)
        scored.append((metaphor, overlap))

    return sorted(scored, key=lambda x: x[1], reverse=True)
```

---

## Forgetting and Adaptation

Models should adapt to changing conditions:

```python
@dataclass
class AdaptiveModel:
    """Model that forgets old data gradually."""

    base_model: RetrievalModel
    decay_rate: float = 0.99  # Per-update decay
    update_count: int = 0

    def update(self, feedback: Feedback) -> None:
        # Update base model
        self.base_model.update(feedback)
        self.update_count += 1

        # Periodically decay old observations
        if self.update_count % 100 == 0:
            self._decay()

    def _decay(self) -> None:
        """Decay historical influence."""
        if isinstance(self.base_model, ThompsonSamplingModel):
            # Decay Beta parameters toward prior
            for key in self.base_model.alphas:
                self.base_model.alphas[key] *= self.decay_rate
                self.base_model.betas[key] *= self.decay_rate
                # Keep minimum mass
                self.base_model.alphas[key] = max(1.0, self.base_model.alphas[key])
                self.base_model.betas[key] = max(1.0, self.base_model.betas[key])
```

---

## Metrics and Monitoring

Track learning effectiveness:

```python
@dataclass
class LearningMetrics:
    """Metrics for monitoring learning."""

    total_feedback: int = 0
    success_rate_last_100: float = 0.0
    exploration_rate: float = 0.0
    model_coverage: float = 0.0  # Fraction of corpus with observations

    average_distortion_success: float = 0.0
    metaphor_diversity: float = 0.0  # How many different metaphors succeed

def compute_learning_metrics(
    model: RetrievalModel,
    recent_feedback: list[Feedback],
    corpus: list[Metaphor]
) -> LearningMetrics:
    """Compute learning metrics."""

    successes = sum(1 for f in recent_feedback[-100:] if f.outcome == Outcome.SUCCESS)
    success_rate = successes / min(100, len(recent_feedback))

    # Model coverage
    covered = sum(1 for m in corpus if model.predict(
        ProblemFeatures(domain="test", domain_cluster=0, complexity=0.5,
                       constraint_count=0, description_length=100,
                       has_embedding=False, embedding_cluster=None),
        m.id
    ) != 0.5)  # 0.5 is the prior
    coverage = covered / len(corpus) if corpus else 0.0

    return LearningMetrics(
        total_feedback=len(recent_feedback),
        success_rate_last_100=success_rate,
        model_coverage=coverage,
    )
```

---

## Summary

| Model Level | Complexity | Best For |
|-------------|------------|----------|
| Frequency | Simple | Small corpus, stable domains |
| Linear Bandit | Medium | Generalizing across problems |
| Thompson Sampling | Medium | Balancing exploration/exploitation |
| Neural Bandit | High | Large corpus, complex patterns |

Start with Thompson Sampling. It's the best balance of simplicity and effectiveness for contextual bandits.

---

*Learning is how the engine gets smarter. Without it, we're just guessing every time.*
