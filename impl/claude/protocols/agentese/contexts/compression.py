"""
AGENTESE Compression Context: MDL-Compliant Quality Metrics

Implements the Ventura Fix: Minimum Description Length with reconstruction validation.

Problem:
    CompressionRatio = len(artifact) / len(spec) rewards empty specs.
    An empty spec has infinite compression ratio but zero utility.

The Fix:
    Quality = CompressionRatio * (1.0 - SemanticDistance(artifact, regenerated))

This ensures:
    - High compression alone isn't rewarded
    - The spec must actually encode the artifact faithfully
    - Reconstruction error penalizes lossy or fake compression

AGENTESE: concept.*.compress (validation layer)

Source: Ventura & Brown - "Creativity as Search for Small, Interesting Programs" (ICCC 2024)

Principle Alignment:
- Tasteful: Quality over quantity
- Ethical: No fake compression (honest representation)
- Composable: Pluggable regenerator and distance functions
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from ..middleware.curator import SemanticDistance, structural_surprise

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bootstrap.umwelt import Umwelt


# === Protocols ===


@runtime_checkable
class Regenerator(Protocol):
    """Protocol for regenerating artifacts from compressed specs."""

    async def __call__(self, spec: str) -> Any:
        """Regenerate artifact from spec."""
        ...


@runtime_checkable
class DistanceFunction(Protocol):
    """Protocol for computing semantic distance between artifacts."""

    async def __call__(self, original: Any, regenerated: Any) -> float:
        """Compute distance between original and regenerated artifacts."""
        ...


# === CompressionQuality Dataclass ===


@dataclass(frozen=True)
class CompressionQuality:
    """
    MDL-compliant compression quality measurement.

    Attributes:
        compression_ratio: len(artifact) / len(spec) - raw compression
        reconstruction_error: Semantic distance between original and regenerated
        quality: Final MDL score = ratio * (1 - error)
        spec_length: Length of compressed spec
        artifact_length: Length of original artifact
    """

    compression_ratio: float
    reconstruction_error: float
    quality: float
    spec_length: int
    artifact_length: int

    def __post_init__(self) -> None:
        """Validate quality metrics are in valid ranges."""
        if self.compression_ratio < 0:
            raise ValueError(
                f"compression_ratio must be >= 0, got {self.compression_ratio}"
            )
        if not 0.0 <= self.reconstruction_error <= 1.0:
            raise ValueError(
                f"reconstruction_error must be between 0.0 and 1.0, "
                f"got {self.reconstruction_error}"
            )
        if self.quality < 0:
            raise ValueError(f"quality must be >= 0, got {self.quality}")

    @classmethod
    def create(
        cls,
        spec: str,
        artifact: Any,
        reconstruction_error: float,
    ) -> "CompressionQuality":
        """
        Create CompressionQuality with computed metrics.

        Args:
            spec: The compressed specification
            artifact: The original artifact
            reconstruction_error: Distance between original and regenerated

        Returns:
            CompressionQuality with all metrics computed
        """
        spec_length = len(spec)
        artifact_length = len(str(artifact))

        # Avoid division by zero - empty spec gets ratio 0 (not infinity!)
        if spec_length == 0:
            compression_ratio = 0.0
        else:
            compression_ratio = artifact_length / spec_length

        # Quality = compression * (1 - reconstruction_error)
        quality = compression_ratio * (1.0 - reconstruction_error)

        return cls(
            compression_ratio=compression_ratio,
            reconstruction_error=reconstruction_error,
            quality=quality,
            spec_length=spec_length,
            artifact_length=artifact_length,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "compression_ratio": self.compression_ratio,
            "reconstruction_error": self.reconstruction_error,
            "quality": self.quality,
            "spec_length": self.spec_length,
            "artifact_length": self.artifact_length,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return (
            f"Compression Quality: {self.quality:.3f}\n"
            f"  Ratio: {self.compression_ratio:.2f}x ({self.artifact_length} -> {self.spec_length})\n"
            f"  Reconstruction Error: {self.reconstruction_error:.3f}"
        )

    @property
    def is_valid(self) -> bool:
        """Check if compression is valid (positive quality, low error)."""
        return self.quality > 0.0 and self.reconstruction_error < 0.5

    @property
    def is_high_quality(self) -> bool:
        """Check if compression is high quality (good ratio, very low error)."""
        return self.quality > 1.0 and self.reconstruction_error < 0.1


# === Core Validation Functions ===


async def validate_compression(
    spec: str,
    artifact: Any,
    regenerator: "Callable[[str], Awaitable[Any]]",
    distance: "Callable[[Any, Any], Awaitable[float]] | None" = None,
) -> CompressionQuality:
    """
    MDL-compliant compression quality validation.

    The Ventura Fix: ensures spec actually encodes the artifact.

    Args:
        spec: The compressed specification
        artifact: The original artifact
        regenerator: Async function to regenerate artifact from spec
        distance: Optional distance function (defaults to structural_surprise)

    Returns:
        CompressionQuality with MDL metrics

    Example:
        async def my_regenerator(spec: str) -> str:
            return await llm.complete(f"Expand this spec: {spec}")

        quality = await validate_compression(
            spec="A story about a hero's journey",
            artifact=full_story_text,
            regenerator=my_regenerator,
        )

        if quality.is_valid:
            print(f"Compression is valid with quality {quality.quality}")
    """
    # Regenerate from spec
    regenerated = await regenerator(spec)

    # Compute reconstruction error
    if distance is not None:
        reconstruction_error = await distance(artifact, regenerated)
    else:
        # Fall back to structural surprise
        reconstruction_error = structural_surprise(artifact, regenerated)

    return CompressionQuality.create(
        spec=spec,
        artifact=artifact,
        reconstruction_error=reconstruction_error,
    )


def validate_compression_sync(
    spec: str,
    artifact: Any,
    regenerated: Any,
    distance: "Callable[[Any, Any], float] | None" = None,
) -> CompressionQuality:
    """
    Synchronous MDL validation when regenerated artifact is pre-computed.

    Args:
        spec: The compressed specification
        artifact: The original artifact
        regenerated: The regenerated artifact (pre-computed)
        distance: Optional distance function

    Returns:
        CompressionQuality with MDL metrics
    """
    if distance is not None:
        reconstruction_error = distance(artifact, regenerated)
    else:
        reconstruction_error = structural_surprise(artifact, regenerated)

    return CompressionQuality.create(
        spec=spec,
        artifact=artifact,
        reconstruction_error=reconstruction_error,
    )


# === Compression Validator Class ===


@dataclass
class CompressionValidator:
    """
    Reusable compression validator with configurable thresholds.

    Usage:
        validator = CompressionValidator(
            min_quality=1.0,
            max_reconstruction_error=0.3,
        )

        quality = await validator.validate(spec, artifact, regenerator)
        if validator.is_acceptable(quality):
            # Compression passes quality gate
    """

    min_quality: float = 0.5
    max_reconstruction_error: float = 0.5
    distance: SemanticDistance | None = None

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.min_quality < 0:
            raise ValueError(f"min_quality must be >= 0, got {self.min_quality}")
        if not 0.0 <= self.max_reconstruction_error <= 1.0:
            raise ValueError(
                f"max_reconstruction_error must be between 0.0 and 1.0, "
                f"got {self.max_reconstruction_error}"
            )

    async def validate(
        self,
        spec: str,
        artifact: Any,
        regenerator: "Callable[[str], Awaitable[Any]]",
    ) -> CompressionQuality:
        """
        Validate compression quality.

        Args:
            spec: The compressed specification
            artifact: The original artifact
            regenerator: Async function to regenerate artifact from spec

        Returns:
            CompressionQuality with MDL metrics
        """
        # Use SemanticDistance if configured, otherwise structural
        if self.distance is not None:
            distance = self.distance  # Local binding for closure

            async def distance_fn(a: Any, b: Any) -> float:
                return await distance(str(a), str(b))

            return await validate_compression(spec, artifact, regenerator, distance_fn)
        else:
            return await validate_compression(spec, artifact, regenerator)

    def is_acceptable(self, quality: CompressionQuality) -> bool:
        """Check if compression quality meets thresholds."""
        return (
            quality.quality >= self.min_quality
            and quality.reconstruction_error <= self.max_reconstruction_error
        )

    def rejection_reason(self, quality: CompressionQuality) -> str | None:
        """Get rejection reason if quality is unacceptable, None if acceptable."""
        if quality.reconstruction_error > self.max_reconstruction_error:
            return (
                f"Reconstruction error too high: {quality.reconstruction_error:.3f} "
                f"> {self.max_reconstruction_error:.3f}"
            )
        if quality.quality < self.min_quality:
            return f"Quality too low: {quality.quality:.3f} < {self.min_quality:.3f}"
        return None


# === AGENTESE Integration ===


async def compress_with_validation(
    artifact: Any,
    compressor: "Callable[[Any], Awaitable[str]]",
    regenerator: "Callable[[str], Awaitable[Any]]",
    observer: "Umwelt[Any, Any]",
    validator: CompressionValidator | None = None,
) -> tuple[str, CompressionQuality]:
    """
    Compress artifact with MDL validation.

    Integrates with AGENTESE concept.*.compress aspects.

    Args:
        artifact: The artifact to compress
        compressor: Async function to produce spec from artifact
        regenerator: Async function to regenerate artifact from spec
        observer: Observer's Umwelt
        validator: Optional validator with thresholds

    Returns:
        Tuple of (spec, CompressionQuality)

    Raises:
        ValueError: If compression fails validation
    """
    # Generate spec
    spec = await compressor(artifact)

    # Validate
    v = validator or CompressionValidator()
    quality = await v.validate(spec, artifact, regenerator)

    # Check quality
    rejection = v.rejection_reason(quality)
    if rejection:
        raise ValueError(f"Compression failed validation: {rejection}")

    return spec, quality


# === Exports ===


__all__ = [
    "CompressionQuality",
    "CompressionValidator",
    "compress_with_validation",
    "validate_compression",
    "validate_compression_sync",
]
