"""
Projection Functor Base Class.

This module defines the abstract base class for projection functors that
transform meaning tokens to target-specific renderings. Projection functors
are natural transformations that preserve semantic structure while adapting
to the observer's capacity to receive.

Key Properties:
- Composition Law: P(A >> B) = P(A) >> P(B) for horizontal composition
- Naturality: Projecting before state change then applying target's update
  equals applying change then projecting
- Density Parameterization: Output adapts to observer density preference

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 2.1, 2.6
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from services.interactive_text.contracts import (
    Observer,
    ObserverDensity,
)

# Type variable for projection target
Target = TypeVar("Target")


# =============================================================================
# Density Parameters
# =============================================================================


@dataclass(frozen=True)
class DensityParams:
    """Parameters for density-based projection.

    These parameters control how tokens are rendered based on the
    observer's density preference (compact, comfortable, spacious).

    Attributes:
        padding: Padding in pixels
        font_size: Font size in pixels
        spacing: Spacing between elements in pixels
        show_details: Whether to show detailed information
        truncate_length: Maximum length before truncation (0 = no truncation)
    """

    padding: int
    font_size: int
    spacing: int
    show_details: bool = True
    truncate_length: int = 0

    @classmethod
    def for_density(cls, density: ObserverDensity) -> DensityParams:
        """Get density parameters for a given density level."""
        return DENSITY_PARAMS[density]


# Density parameter presets
DENSITY_PARAMS: dict[ObserverDensity, DensityParams] = {
    ObserverDensity.COMPACT: DensityParams(
        padding=4,
        font_size=14,
        spacing=2,
        show_details=False,
        truncate_length=50,
    ),
    ObserverDensity.COMFORTABLE: DensityParams(
        padding=8,
        font_size=16,
        spacing=4,
        show_details=True,
        truncate_length=100,
    ),
    ObserverDensity.SPACIOUS: DensityParams(
        padding=12,
        font_size=18,
        spacing=8,
        show_details=True,
        truncate_length=0,  # No truncation
    ),
}


# =============================================================================
# Projection Result Types
# =============================================================================


@dataclass(frozen=True)
class ProjectionResult(Generic[Target]):
    """Result of a projection operation.

    Attributes:
        target: The projected output
        source_token_id: ID of the source token
        observer_id: ID of the observer receiving the projection
        density: Density used for projection
        metadata: Additional projection metadata
    """

    target: Target
    source_token_id: str
    observer_id: str
    density: ObserverDensity
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompositionResult(Generic[Target]):
    """Result of composing multiple projections.

    Attributes:
        target: The composed projection output
        composition_type: Type of composition ("horizontal" or "vertical")
        source_token_ids: IDs of source tokens in composition order
        observer_id: ID of the observer receiving the projection
    """

    target: Target
    composition_type: str
    source_token_ids: tuple[str, ...]
    observer_id: str


# =============================================================================
# Projection Functor Protocol
# =============================================================================


class ProjectionFunctor(ABC, Generic[Target]):
    """Abstract base class for projection functors.

    Projection functors transform meaning tokens to target-specific renderings.
    They satisfy the functor laws:

    1. Identity: P(id) = id
    2. Composition: P(f ∘ g) = P(f) ∘ P(g)

    And the naturality condition:
    - For all state morphisms f : S₁ → S₂,
      P(f(s)) = P_target(P(s)) where P_target is the target's state update.

    Subclasses must implement:
    - target_name: The name of the projection target
    - project_token: Project a single token
    - project_document: Project an entire document
    - _compose: Compose projected elements

    Type Parameters:
        Target: The type of the projection output (e.g., str for CLI, dict for JSON)

    Requirements: 2.1, 2.6
    """

    @property
    @abstractmethod
    def target_name(self) -> str:
        """Name of the projection target (e.g., 'cli', 'web', 'json')."""
        ...

    @abstractmethod
    async def project_token(
        self,
        token: "MeaningToken[Any]",
        observer: Observer,
    ) -> Target:
        """Project a single token to target-specific rendering.

        Args:
            token: The meaning token to project
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of the token
        """
        ...

    @abstractmethod
    async def project_document(
        self,
        document: "Document",
        observer: Observer,
    ) -> Target:
        """Project an entire document to target-specific rendering.

        Args:
            document: The document to project
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of the document
        """
        ...

    @abstractmethod
    def _compose(
        self,
        projections: list[Target],
        composition_type: str,
    ) -> Target:
        """Compose multiple projected elements.

        Args:
            projections: List of projected elements to compose
            composition_type: Type of composition:
                - "horizontal" (>>): Elements arranged side by side
                - "vertical" (//): Elements arranged top to bottom

        Returns:
            Composed projection
        """
        ...

    async def project_composition(
        self,
        tokens: list["MeaningToken[Any]"],
        composition_type: str,
        observer: Observer,
    ) -> CompositionResult[Target]:
        """Project composed tokens.

        This method implements the composition law:
        - Horizontal (>>): P(A >> B) = P(A) >> P(B)
        - Vertical (//): P(A // B) = P(A) // P(B)

        Args:
            tokens: List of tokens to compose
            composition_type: Type of composition ("horizontal" or "vertical")
            observer: The observer receiving the projection

        Returns:
            CompositionResult containing the composed projection

        Requirements: 1.5, 2.6
        """
        # Project each token individually
        projections = [await self.project_token(token, observer) for token in tokens]

        # Compose the projections
        composed = self._compose(projections, composition_type)

        return CompositionResult(
            target=composed,
            composition_type=composition_type,
            source_token_ids=tuple(token.token_id for token in tokens),
            observer_id=observer.id,
        )

    def get_density_params(self, observer: Observer) -> DensityParams:
        """Get density parameters for an observer.

        Args:
            observer: The observer to get parameters for

        Returns:
            DensityParams for the observer's density preference
        """
        return DensityParams.for_density(observer.density)

    async def project_with_result(
        self,
        token: "MeaningToken[Any]",
        observer: Observer,
    ) -> ProjectionResult[Target]:
        """Project a token and return full result with metadata.

        Args:
            token: The meaning token to project
            observer: The observer receiving the projection

        Returns:
            ProjectionResult containing the projection and metadata
        """
        target = await self.project_token(token, observer)

        return ProjectionResult(
            target=target,
            source_token_id=token.token_id,
            observer_id=observer.id,
            density=observer.density,
            metadata={
                "target_name": self.target_name,
                "token_type": token.token_type,
            },
        )


# =============================================================================
# Type Imports (for type hints only)
# =============================================================================

# These are imported at runtime to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.interactive_text.contracts import MeaningToken

    @dataclass
    class Document:
        """Placeholder for Document type."""

        pass


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ProjectionFunctor",
    "ProjectionResult",
    "CompositionResult",
    "DensityParams",
    "DENSITY_PARAMS",
]
