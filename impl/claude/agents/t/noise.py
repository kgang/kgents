"""NoiseAgent - Identity morphism with semantic perturbation.

Category Theory: N_ε: A → A + ε
The morphism that adds small perturbations while preserving semantics.

Type II Saboteur - Chaos Engineering for robustness testing.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar

if TYPE_CHECKING:
    from agents.poly.types import Agent, ComposedAgent

A = TypeVar("A")
B = TypeVar("B")


class NoiseType(Enum):
    """Types of semantic perturbations."""

    CASE = "case_change"  # Change capitalization
    WHITESPACE = "whitespace"  # Add/remove spaces
    TYPOS = "typos"  # Swap adjacent characters
    PUNCTUATION = "punctuation"  # Add/remove punctuation


@dataclass
class NoiseConfig:
    """Configuration for NoiseAgent."""

    level: float = 0.1  # 0.0 (no noise) to 1.0 (maximal noise)
    seed: Optional[int] = None  # For reproducibility
    noise_types: List[NoiseType] = field(
        default_factory=lambda: [
            NoiseType.CASE,
            NoiseType.WHITESPACE,
            NoiseType.TYPOS,
        ]
    )


class NoiseAgent(Generic[A]):
    """Identity morphism with semantic noise N_ε.

    Category Theory:
    - Morphism: N_ε: A → A + ε
    - Properties: Near-identity (preserves semantics)
    - Purpose: Test robustness to input perturbations

    Algebraic Laws:
    - N_0 ≈ id (zero noise is identity)
    - N_ε ∘ N_ε ≈ N_{2ε} (noise accumulates)
    - lim_{ε→0} N_ε = id (continuous)

    Example:
        >>> noise = NoiseAgent(level=0.3, seed=42)
        >>> result = await noise.invoke("Fix the bug")
        >>> # Result might be "Fix  the  Bug" or "Fxi the bug"
    """

    def __init__(
        self,
        level: float = 0.1,
        seed: Optional[int] = None,
        noise_types: Optional[List[NoiseType]] = None,
    ) -> None:
        """Initialize NoiseAgent.

        Args:
            level: Noise level 0.0-1.0 (probability of perturbation)
            seed: Random seed for reproducibility
            noise_types: List of noise types to apply (default: CASE, WHITESPACE, TYPOS)
        """
        self.name = f"Noise(ε={level})"
        self.level = level
        self.rng = random.Random(seed)
        self.noise_types = noise_types or [
            NoiseType.CASE,
            NoiseType.WHITESPACE,
            NoiseType.TYPOS,
        ]
        self.__is_test__ = True

    async def invoke(self, input_data: A) -> A:
        """Add noise to input while preserving semantics.

        Category Theory: N_ε: A → A + ε

        Args:
            input_data: Input to perturb

        Returns:
            Perturbed input (same type, slightly modified)
        """
        if isinstance(input_data, str):
            return self._perturb_string(input_data)  # type: ignore[return-value]
        # For non-string types, return unchanged
        return input_data

    def _perturb_string(self, s: str) -> str:
        """Apply string perturbations.

        Args:
            s: String to perturb

        Returns:
            Perturbed string
        """
        if self.rng.random() > self.level:
            return s  # No noise this time

        # Select applicable operations
        operations = []
        if NoiseType.CASE in self.noise_types:
            operations.append(self._change_case)
        if NoiseType.WHITESPACE in self.noise_types:
            operations.append(self._add_whitespace)
        if NoiseType.TYPOS in self.noise_types:
            operations.append(self._introduce_typo)
        if NoiseType.PUNCTUATION in self.noise_types:
            operations.append(self._add_punctuation)

        if not operations:
            return s

        operation = self.rng.choice(operations)
        return operation(s)

    def _change_case(self, s: str) -> str:
        """Randomly change case of first word.

        Args:
            s: Input string

        Returns:
            String with modified case
        """
        if not s:
            return s
        words = s.split()
        if not words:
            return s

        # Change case of first word
        first = words[0]
        if self.rng.random() > 0.5:
            words[0] = first.upper()
        else:
            words[0] = first.lower()

        return " ".join(words)

    def _add_whitespace(self, s: str) -> str:
        """Add extra spaces between words.

        Args:
            s: Input string

        Returns:
            String with extra whitespace
        """
        words = s.split()
        return "  ".join(words)

    def _introduce_typo(self, s: str) -> str:
        """Swap adjacent characters to simulate typo.

        Args:
            s: Input string

        Returns:
            String with typo
        """
        if len(s) < 2:
            return s
        idx = self.rng.randint(0, len(s) - 2)
        chars = list(s)
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
        return "".join(chars)

    def _add_punctuation(self, s: str) -> str:
        """Add random punctuation.

        Args:
            s: Input string

        Returns:
            String with added punctuation
        """
        punctuation = [".", "!", "?", ","]
        punct = self.rng.choice(punctuation)
        return s + punct

    def __rshift__(self, other: Agent[A, B]) -> ComposedAgent[A, A, B]:
        """Composition operator: self >> other.

        Args:
            other: Agent to compose with

        Returns:
            Composed agent
        """
        from agents.poly.types import ComposedAgent

        return ComposedAgent(self, other)  # type: ignore[arg-type]
