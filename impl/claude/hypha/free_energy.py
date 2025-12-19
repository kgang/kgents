"""
Free Energy - Active Inference Foundation.

Free Energy F = Complexity + Inaccuracy

The agent acts to minimize F by:
1. Updating beliefs (reduce inaccuracy)
2. Taking action (change world to match beliefs)
3. Attending selectively (ignore irrelevant)

Mathematical Foundation:
- Variational Free Energy bounds the negative log evidence
- Minimizing F is equivalent to maximizing model evidence
- Prediction error drives exploration
- Low prediction error + reward drives exploitation

References:
- Friston, "The Free Energy Principle" (2010)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

# Type alias for vectors
Vector = NDArray[np.floating[Any]]


@dataclass
class FreeEnergyState:
    """
    Active Inference state.

    Free Energy F = Complexity + Inaccuracy

    The agent acts to minimize F by:
    1. Updating beliefs (reduce inaccuracy)
    2. Taking action (change world to match beliefs)
    3. Attending selectively (ignore irrelevant)

    Attributes:
        expected_observation: Generative model's prediction
        actual_observation: Actual sensory observation
        complexity: Model complexity (how many parameters)
    """

    expected_observation: Vector
    actual_observation: Vector
    complexity: float = 0.0

    @property
    def prediction_error(self) -> float:
        """Inaccuracy: divergence between expected and actual."""
        return float(np.linalg.norm(self.expected_observation - self.actual_observation))

    @property
    def free_energy(self) -> float:
        """Variational Free Energy (to be minimized)."""
        return self.complexity + self.prediction_error

    @property
    def surprise(self) -> float:
        """Surprise is prediction error (for biological intuition)."""
        return self.prediction_error

    @property
    def normalized_surprise(self) -> float:
        """
        Surprise normalized to [0, 1] range.

        Uses sigmoid-like normalization.
        """
        # Use sigmoid to map to [0, 1]
        # High surprise (>2.0) -> ~1.0
        # Low surprise (<0.5) -> ~0.0
        return float(1.0 / (1.0 + np.exp(-self.surprise + 1.0)))

    def is_surprising(self, threshold: float = 0.8) -> bool:
        """Check if current state is surprising."""
        return self.normalized_surprise > threshold

    def is_predictable(self, threshold: float = 0.2) -> bool:
        """Check if current state is predictable (low surprise)."""
        return self.normalized_surprise < threshold


@dataclass
class GenerativeModel:
    """
    The Hypha's internal model of the world.

    Predicts observations and updates based on error.

    The generative model maintains:
    - Weights for prediction
    - Complexity measure (L2 norm)
    - Learning rate for updates

    Mathematical Model:
    - prediction = context * weights
    - error = actual - prediction
    - weights += learning_rate * error
    """

    dimensions: int = 10_000

    # Model weights
    weights: Vector = field(init=False)

    # Learning history
    update_count: int = 0
    cumulative_error: float = 0.0

    def __post_init__(self) -> None:
        """Initialize weights."""
        self.weights = np.random.randn(self.dimensions).astype(np.float64)
        # Normalize
        norm = np.linalg.norm(self.weights)
        if norm > 0:
            self.weights = self.weights / norm

    @property
    def complexity(self) -> float:
        """Model complexity (L2 norm of weights)."""
        return float(np.linalg.norm(self.weights))

    def predict(self, context: Vector) -> Vector:
        """
        Predict expected observation from context.

        Uses element-wise multiplication to combine context
        with learned weights.
        """
        prediction = context * self.weights
        # Normalize
        norm = np.linalg.norm(prediction)
        if norm > 0:
            prediction = prediction / norm
        return prediction

    def update(
        self,
        context: Vector,
        actual: Vector,
        learning_rate: float = 0.1,
    ) -> float:
        """
        Update model based on actual observation.

        Uses gradient descent on prediction error.

        Args:
            context: The context used for prediction
            actual: The actual observation
            learning_rate: Step size for update

        Returns:
            The prediction error before update
        """
        # Predict
        predicted = self.predict(context)

        # Compute error
        error = actual - predicted
        error_magnitude = float(np.linalg.norm(error))

        # Gradient descent step
        # Simplified: move weights toward reducing error
        self.weights += learning_rate * error * context

        # Re-normalize weights
        norm = np.linalg.norm(self.weights)
        if norm > 0:
            self.weights = self.weights / norm

        # Track history
        self.update_count += 1
        self.cumulative_error += error_magnitude

        return error_magnitude

    @property
    def average_error(self) -> float:
        """Average error over all updates."""
        if self.update_count == 0:
            return 0.0
        return self.cumulative_error / self.update_count

    def reset(self) -> None:
        """Reset the model to initial state."""
        self.__post_init__()
        self.update_count = 0
        self.cumulative_error = 0.0


def compute_free_energy(
    expected: Vector,
    actual: Vector,
    model_complexity: float = 0.0,
) -> float:
    """
    Compute variational free energy.

    F = Complexity + Inaccuracy

    Args:
        expected: Expected observation (from generative model)
        actual: Actual observation
        model_complexity: Model complexity term

    Returns:
        Free energy value
    """
    inaccuracy = float(np.linalg.norm(expected - actual))
    return model_complexity + inaccuracy


def compute_surprise(
    expected: Vector,
    actual: Vector,
) -> float:
    """
    Compute surprise (prediction error).

    High surprise indicates unexpected observation.
    Low surprise indicates predictions are accurate.

    Args:
        expected: Expected observation
        actual: Actual observation

    Returns:
        Surprise value (non-negative)
    """
    return float(np.linalg.norm(expected - actual))
