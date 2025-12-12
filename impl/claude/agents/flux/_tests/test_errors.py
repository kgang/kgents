"""Tests for Flux error types."""

import pytest
from agents.flux.errors import (
    FluxBackpressureError,
    FluxEntropyError,
    FluxError,
    FluxPerturbationError,
    FluxPipelineError,
    FluxSourceError,
    FluxStateError,
)


class TestFluxError:
    """Test base FluxError class."""

    def test_basic_error(self):
        error = FluxError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_with_context(self):
        error = FluxError("Failed", context={"key": "value"})
        assert "key" in str(error)
        assert error.context == {"key": "value"}

    def test_error_without_context(self):
        error = FluxError("Failed")
        assert error.context == {}

    def test_error_inheritance(self):
        error = FluxError("test")
        assert isinstance(error, Exception)


class TestFluxStateError:
    """Test FluxStateError class."""

    def test_basic_state_error(self):
        error = FluxStateError("Invalid state")
        assert str(error) == "Invalid state"

    def test_state_error_with_current_state(self):
        error = FluxStateError("Cannot start", current_state="flowing")
        assert error.current_state == "flowing"
        assert "flowing" in str(error)

    def test_state_error_with_operation(self):
        error = FluxStateError("Failed", attempted_operation="start")
        assert error.attempted_operation == "start"
        assert "start" in str(error)

    def test_state_error_inheritance(self):
        error = FluxStateError("test")
        assert isinstance(error, FluxError)


class TestFluxEntropyError:
    """Test FluxEntropyError class."""

    def test_basic_entropy_error(self):
        error = FluxEntropyError("Out of entropy")
        assert str(error) == "Out of entropy"

    def test_entropy_error_with_remaining(self):
        error = FluxEntropyError("Budget exhausted", entropy_remaining=0.001)
        assert error.entropy_remaining == 0.001
        assert "0.001" in str(error)

    def test_entropy_error_with_required(self):
        error = FluxEntropyError("Need more", entropy_required=0.1)
        assert error.entropy_required == 0.1

    def test_entropy_error_inheritance(self):
        error = FluxEntropyError("test")
        assert isinstance(error, FluxError)


class TestFluxBackpressureError:
    """Test FluxBackpressureError class."""

    def test_basic_backpressure_error(self):
        error = FluxBackpressureError("Buffer full")
        assert str(error) == "Buffer full"

    def test_backpressure_error_with_buffer_size(self):
        error = FluxBackpressureError("Full", buffer_size=100)
        assert error.buffer_size == 100
        assert "100" in str(error)

    def test_backpressure_error_with_policy(self):
        error = FluxBackpressureError("Failed", drop_policy="block")
        assert error.drop_policy == "block"

    def test_backpressure_error_inheritance(self):
        error = FluxBackpressureError("test")
        assert isinstance(error, FluxError)


class TestFluxPerturbationError:
    """Test FluxPerturbationError class."""

    def test_basic_perturbation_error(self):
        error = FluxPerturbationError("Perturbation failed")
        assert str(error) == "Perturbation failed"

    def test_perturbation_error_with_data(self):
        error = FluxPerturbationError("Failed", perturbation_data={"key": "value"})
        assert error.perturbation_data == {"key": "value"}

    def test_perturbation_error_with_inner_exception(self):
        inner = ValueError("Inner error")
        error = FluxPerturbationError("Failed", inner_exception=inner)
        assert error.inner_exception is inner
        assert "Inner error" in str(error)

    def test_perturbation_error_inheritance(self):
        error = FluxPerturbationError("test")
        assert isinstance(error, FluxError)


class TestFluxPipelineError:
    """Test FluxPipelineError class."""

    def test_basic_pipeline_error(self):
        error = FluxPipelineError("Pipeline failed")
        assert str(error) == "Pipeline failed"

    def test_pipeline_error_with_stage_index(self):
        error = FluxPipelineError("Stage failed", stage_index=2)
        assert error.stage_index == 2
        assert "2" in str(error)

    def test_pipeline_error_with_stage_name(self):
        error = FluxPipelineError("Failed", stage_name="Transformer")
        assert error.stage_name == "Transformer"

    def test_pipeline_error_inheritance(self):
        error = FluxPipelineError("test")
        assert isinstance(error, FluxError)


class TestFluxSourceError:
    """Test FluxSourceError class."""

    def test_basic_source_error(self):
        error = FluxSourceError("Source failed")
        assert str(error) == "Source failed"

    def test_source_error_with_type(self):
        error = FluxSourceError("Failed", source_type="EventBus")
        assert error.source_type == "EventBus"

    def test_source_error_with_events_count(self):
        error = FluxSourceError("Error", events_before_error=42)
        assert error.events_before_error == 42
        assert "42" in str(error)

    def test_source_error_inheritance(self):
        error = FluxSourceError("test")
        assert isinstance(error, FluxError)


class TestErrorHierarchy:
    """Test that all errors inherit from FluxError."""

    @pytest.mark.parametrize(
        "error_class",
        [
            FluxStateError,
            FluxEntropyError,
            FluxBackpressureError,
            FluxPerturbationError,
            FluxPipelineError,
            FluxSourceError,
        ],
    )
    def test_inheritance(self, error_class):
        error = error_class("test")
        assert isinstance(error, FluxError)
        assert isinstance(error, Exception)

    def test_catch_all_flux_errors(self):
        """Verify all specific errors can be caught with FluxError."""
        errors = [
            FluxStateError("1"),
            FluxEntropyError("2"),
            FluxBackpressureError("3"),
            FluxPerturbationError("4"),
            FluxPipelineError("5"),
            FluxSourceError("6"),
        ]

        caught = 0
        for err in errors:
            try:
                raise err
            except FluxError:
                caught += 1

        assert caught == len(errors)
