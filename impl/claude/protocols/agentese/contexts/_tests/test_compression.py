"""
Tests for AGENTESE Compression Context: MDL-Compliant Quality Metrics

Tests verify:
1. Empty specs get zero compression ratio (not infinity)
2. Good specs that reconstruct artifacts get high quality scores
3. Semantic distance integration works correctly
4. CompressionValidator thresholds are enforced
5. compress_with_validation raises on poor quality
"""

from __future__ import annotations

from typing import Any

import pytest

from protocols.agentese.contexts.compression import (
    CompressionQuality,
    CompressionValidator,
    compress_with_validation,
    validate_compression,
    validate_compression_sync,
)
from protocols.agentese.middleware.curator import SemanticDistance

# === CompressionQuality Tests ===


class TestCompressionQuality:
    """Tests for CompressionQuality dataclass."""

    def test_compression_quality_rejects_empty_spec(self) -> None:
        """Empty spec gets compression ratio of 0, not infinity (The Ventura Fix)."""
        quality = CompressionQuality.create(
            spec="",
            artifact="This is a long artifact with lots of content.",
            reconstruction_error=0.5,
        )

        # Empty spec should NOT be rewarded with infinite ratio
        assert quality.compression_ratio == 0.0
        # Quality should be 0 (ratio * (1 - error) = 0 * anything = 0)
        assert quality.quality == 0.0
        # Should not be valid
        assert not quality.is_valid

    def test_compression_quality_rewards_reconstructable(self) -> None:
        """Good spec with low reconstruction error gets high quality score."""
        artifact = "The quick brown fox jumps over the lazy dog."
        spec = "fox jumps dog"  # Compressed but captures essence

        quality = CompressionQuality.create(
            spec=spec,
            artifact=artifact,
            reconstruction_error=0.05,  # Very low error = good reconstruction
        )

        # Compression ratio = 44 / 13 = ~3.38
        assert quality.compression_ratio > 3.0
        # Quality = ratio * (1 - 0.05) = ratio * 0.95
        assert quality.quality > 3.0
        # Should be valid
        assert quality.is_valid
        # Should be high quality (quality > 1.0 AND error < 0.1)
        assert quality.is_high_quality

    def test_compression_quality_penalizes_lossy_compression(self) -> None:
        """High reconstruction error penalizes quality score."""
        artifact = "The quick brown fox jumps over the lazy dog."
        spec = "fox jumps dog"

        quality = CompressionQuality.create(
            spec=spec,
            artifact=artifact,
            reconstruction_error=0.9,  # Very high error = bad reconstruction
        )

        # Ratio is still good
        assert quality.compression_ratio > 3.0
        # But quality is terrible: ratio * (1 - 0.9) = ratio * 0.1
        assert quality.quality < 0.5
        # Should not be valid
        assert not quality.is_valid

    def test_compression_quality_frozen(self) -> None:
        """CompressionQuality is immutable."""
        quality = CompressionQuality.create(
            spec="test",
            artifact="test artifact",
            reconstruction_error=0.2,
        )

        with pytest.raises(AttributeError):
            quality.quality = 999.0  # type: ignore[misc]

    def test_compression_quality_validation_errors(self) -> None:
        """CompressionQuality validates its fields."""
        with pytest.raises(ValueError, match="compression_ratio"):
            CompressionQuality(
                compression_ratio=-1.0,  # Invalid
                reconstruction_error=0.5,
                quality=-0.5,
                spec_length=10,
                artifact_length=50,
            )

        with pytest.raises(ValueError, match="reconstruction_error"):
            CompressionQuality(
                compression_ratio=5.0,
                reconstruction_error=1.5,  # Invalid: > 1.0
                quality=2.5,
                spec_length=10,
                artifact_length=50,
            )

    def test_compression_quality_to_dict(self) -> None:
        """to_dict() returns all fields."""
        quality = CompressionQuality.create(
            spec="test spec",
            artifact="test artifact",
            reconstruction_error=0.3,
        )

        d = quality.to_dict()
        assert "compression_ratio" in d
        assert "reconstruction_error" in d
        assert "quality" in d
        assert "spec_length" in d
        assert "artifact_length" in d

    def test_compression_quality_to_text(self) -> None:
        """to_text() returns human-readable format."""
        quality = CompressionQuality.create(
            spec="test spec",
            artifact="test artifact",
            reconstruction_error=0.3,
        )

        text = quality.to_text()
        assert "Compression Quality" in text
        assert "Ratio" in text
        assert "Reconstruction Error" in text


# === validate_compression Tests ===


class TestValidateCompression:
    """Tests for validate_compression function."""

    @pytest.mark.asyncio
    async def test_validate_compression_with_perfect_reconstruction(self) -> None:
        """Perfect reconstruction gives zero error."""
        artifact = "Hello, world!"

        async def regenerator(spec: str) -> str:
            # Perfect regeneration
            return artifact

        quality = await validate_compression(
            spec="hello world greeting",
            artifact=artifact,
            regenerator=regenerator,
        )

        # Perfect reconstruction = 0 error
        assert quality.reconstruction_error == 0.0
        # Quality = ratio * 1.0 = ratio
        assert quality.quality > 0.0

    @pytest.mark.asyncio
    async def test_validate_compression_with_poor_reconstruction(self) -> None:
        """Poor reconstruction gives high error."""
        artifact = "Hello, world!"

        async def regenerator(spec: str) -> str:
            # Completely wrong regeneration
            return "Goodbye, moon!"

        quality = await validate_compression(
            spec="hello world greeting",
            artifact=artifact,
            regenerator=regenerator,
        )

        # Different strings = high error
        assert quality.reconstruction_error > 0.3

    @pytest.mark.asyncio
    async def test_validate_compression_with_custom_distance(self) -> None:
        """Custom distance function is used when provided."""
        artifact = "Hello, world!"
        custom_distance_called = False

        async def regenerator(spec: str) -> str:
            return artifact

        async def custom_distance(a: Any, b: Any) -> float:
            nonlocal custom_distance_called
            custom_distance_called = True
            return 0.25  # Fixed distance

        quality = await validate_compression(
            spec="hello world greeting",
            artifact=artifact,
            regenerator=regenerator,
            distance=custom_distance,
        )

        assert custom_distance_called
        assert quality.reconstruction_error == 0.25

    @pytest.mark.asyncio
    async def test_semantic_distance_integration(self) -> None:
        """SemanticDistance can be used for reconstruction error."""
        artifact = "The quick brown fox"

        async def regenerator(spec: str) -> str:
            return "The fast brown fox"  # Similar but not identical

        distance = SemanticDistance()

        async def semantic_distance_wrapper(a: Any, b: Any) -> float:
            return await distance(str(a), str(b))

        quality = await validate_compression(
            spec="fox description",
            artifact=artifact,
            regenerator=regenerator,
            distance=semantic_distance_wrapper,
        )

        # Similar strings should have some distance
        assert 0.0 < quality.reconstruction_error < 0.5


# === validate_compression_sync Tests ===


class TestValidateCompressionSync:
    """Tests for synchronous validation."""

    def test_validate_compression_sync_identical(self) -> None:
        """Identical artifacts have zero error."""
        artifact = "Hello, world!"

        quality = validate_compression_sync(
            spec="hello greeting",
            artifact=artifact,
            regenerated=artifact,
        )

        assert quality.reconstruction_error == 0.0

    def test_validate_compression_sync_different(self) -> None:
        """Different artifacts have positive error."""
        quality = validate_compression_sync(
            spec="hello greeting",
            artifact="Hello, world!",
            regenerated="Goodbye, moon!",
        )

        assert quality.reconstruction_error > 0.0


# === CompressionValidator Tests ===


class TestCompressionValidator:
    """Tests for CompressionValidator class."""

    def test_validator_default_thresholds(self) -> None:
        """Validator has sensible default thresholds."""
        validator = CompressionValidator()
        assert validator.min_quality == 0.5
        assert validator.max_reconstruction_error == 0.5

    def test_validator_custom_thresholds(self) -> None:
        """Validator accepts custom thresholds."""
        validator = CompressionValidator(
            min_quality=1.0,
            max_reconstruction_error=0.3,
        )
        assert validator.min_quality == 1.0
        assert validator.max_reconstruction_error == 0.3

    def test_validator_threshold_validation(self) -> None:
        """Validator validates its thresholds."""
        with pytest.raises(ValueError, match="min_quality"):
            CompressionValidator(min_quality=-1.0)

        with pytest.raises(ValueError, match="max_reconstruction_error"):
            CompressionValidator(max_reconstruction_error=1.5)

    def test_is_acceptable_passes_good_quality(self) -> None:
        """is_acceptable returns True for good quality."""
        validator = CompressionValidator(
            min_quality=0.5,
            max_reconstruction_error=0.5,
        )

        quality = CompressionQuality.create(
            spec="test spec",
            artifact="test artifact content here",
            reconstruction_error=0.2,
        )

        assert validator.is_acceptable(quality)

    def test_is_acceptable_rejects_low_quality(self) -> None:
        """is_acceptable returns False for low quality."""
        validator = CompressionValidator(
            min_quality=2.0,  # High threshold to ensure rejection
            max_reconstruction_error=0.3,
        )

        quality = CompressionQuality.create(
            spec="test spec",
            artifact="test artifact",  # Similar length = low ratio (~1.44)
            reconstruction_error=0.2,
        )

        # Quality is ~1.15 which is below min_quality of 2.0
        assert not validator.is_acceptable(quality)

    def test_is_acceptable_rejects_high_error(self) -> None:
        """is_acceptable returns False for high reconstruction error."""
        validator = CompressionValidator(
            min_quality=0.5,
            max_reconstruction_error=0.3,
        )

        quality = CompressionQuality.create(
            spec="test",
            artifact="long artifact content",
            reconstruction_error=0.5,  # Above threshold
        )

        assert not validator.is_acceptable(quality)

    def test_rejection_reason_for_high_error(self) -> None:
        """rejection_reason explains high error rejection."""
        validator = CompressionValidator(max_reconstruction_error=0.3)

        quality = CompressionQuality.create(
            spec="test",
            artifact="artifact",
            reconstruction_error=0.5,
        )

        reason = validator.rejection_reason(quality)
        assert reason is not None
        assert "Reconstruction error" in reason
        assert "too high" in reason

    def test_rejection_reason_for_low_quality(self) -> None:
        """rejection_reason explains low quality rejection."""
        validator = CompressionValidator(min_quality=5.0)

        quality = CompressionQuality.create(
            spec="test spec",
            artifact="test artifact",
            reconstruction_error=0.1,
        )

        reason = validator.rejection_reason(quality)
        assert reason is not None
        assert "Quality" in reason
        assert "too low" in reason

    def test_rejection_reason_none_for_acceptable(self) -> None:
        """rejection_reason returns None for acceptable quality."""
        validator = CompressionValidator(
            min_quality=0.1,
            max_reconstruction_error=0.9,
        )

        quality = CompressionQuality.create(
            spec="test",
            artifact="artifact",
            reconstruction_error=0.5,
        )

        assert validator.rejection_reason(quality) is None

    @pytest.mark.asyncio
    async def test_validator_validate_method(self) -> None:
        """Validator.validate() works end-to-end."""
        validator = CompressionValidator()

        async def regenerator(spec: str) -> str:
            return "regenerated artifact"

        quality = await validator.validate(
            spec="test spec",
            artifact="original artifact",
            regenerator=regenerator,
        )

        assert isinstance(quality, CompressionQuality)


# === compress_with_validation Tests ===


class TestCompressWithValidation:
    """Tests for compress_with_validation function."""

    @pytest.mark.asyncio
    async def test_compress_with_validation_success(self) -> None:
        """compress_with_validation succeeds for good compression."""
        artifact = "The quick brown fox jumps over the lazy dog." * 10

        async def compressor(a: Any) -> str:
            return "fox jumps dog"  # Short spec

        async def regenerator(spec: str) -> Any:
            return artifact  # Perfect regeneration

        # Create mock umwelt
        from protocols.agentese._tests.conftest import MockUmwelt

        observer = MockUmwelt()

        spec, quality = await compress_with_validation(
            artifact=artifact,
            compressor=compressor,
            regenerator=regenerator,
            observer=observer,  # type: ignore[arg-type]
        )

        assert spec == "fox jumps dog"
        assert quality.is_valid

    @pytest.mark.asyncio
    async def test_compress_with_validation_raises_on_poor_quality(self) -> None:
        """compress_with_validation raises ValueError for poor quality."""
        artifact = "test"

        async def compressor(a: Any) -> str:
            return "test"  # Same length = ratio 1

        async def regenerator(spec: str) -> Any:
            return "completely different"  # Bad regeneration

        from protocols.agentese._tests.conftest import MockUmwelt

        observer = MockUmwelt()

        validator = CompressionValidator(
            min_quality=2.0,  # High threshold
            max_reconstruction_error=0.1,  # Strict threshold
        )

        with pytest.raises(ValueError, match="Compression failed validation"):
            await compress_with_validation(
                artifact=artifact,
                compressor=compressor,
                regenerator=regenerator,
                observer=observer,  # type: ignore[arg-type]
                validator=validator,
            )
