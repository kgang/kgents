"""
Tests for AGENTESE Aspect Pipelines.

Tests cover:
- Pipeline execution
- Stage results
- Error handling
- Fail-fast behavior
- Collect-all behavior
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pytest

from ..node import AgentMeta, Observer, Renderable
from ..pipeline import (
    AspectPipeline,
    PipelineResult,
    PipelineStageResult,
    create_pipeline,
)

if TYPE_CHECKING:
    from bootstrap.types import Agent
    from bootstrap.umwelt import Umwelt


# === Mock Renderable for Testing ===


@dataclass(frozen=True)
class MockRenderable:
    """Mock renderable for testing."""

    content: str = "mock content"

    def to_dict(self) -> dict[str, Any]:
        return {"content": self.content}

    def to_text(self) -> str:
        return self.content


# === Mock Node for Testing ===


@dataclass
class MockNode:
    """
    Mock node for testing pipelines.

    Implements the LogosNode protocol for type-safe testing.
    """

    handle: str = "test.node"
    _state: dict[str, Any] = field(default_factory=dict)

    def affordances(self, observer: AgentMeta) -> list[str]:
        """Return available aspects."""
        return ["load", "parse", "transform", "summarize", "fail", "slow"]

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """Return composable agent for aspect (mock implementation)."""
        # Import here to avoid circular imports
        from ..node import AspectAgent

        return AspectAgent(self, aspect)  # type: ignore[return-value]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Return mock renderable."""
        return MockRenderable(content=f"manifest for {self.handle}")

    async def invoke(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Invoke an aspect."""
        input_val = kwargs.get("input")

        if aspect == "load":
            return {"content": "raw data", "input": input_val}

        if aspect == "parse":
            data = input_val or {}
            return {"parsed": True, "content": data.get("content", "")}

        if aspect == "transform":
            data = input_val or {}
            return {"transformed": True, **data}

        if aspect == "summarize":
            data = input_val or {}
            return f"Summary of: {data}"

        if aspect == "fail":
            raise ValueError("Intentional failure")

        if aspect == "slow":
            import asyncio

            await asyncio.sleep(0.1)
            return {"slow": True}

        return {"aspect": aspect, "input": input_val}


# === PipelineStageResult Tests ===


class TestPipelineStageResult:
    """Tests for PipelineStageResult."""

    def test_ok_result(self) -> None:
        """Test creating a successful result."""
        result = PipelineStageResult.ok("load", {"data": "test"}, 10.5)

        assert result.aspect == "load"
        assert result.success is True
        assert result.result == {"data": "test"}
        assert result.error is None
        assert result.duration_ms == 10.5

    def test_fail_result(self) -> None:
        """Test creating a failed result."""
        error = ValueError("test error")
        result = PipelineStageResult.fail("parse", error, 5.0)

        assert result.aspect == "parse"
        assert result.success is False
        assert result.result is None
        assert result.error is error
        assert result.duration_ms == 5.0


# === PipelineResult Tests ===


class TestPipelineResult:
    """Tests for PipelineResult."""

    def test_successful_result(self) -> None:
        """Test successful pipeline result."""
        stages = (
            PipelineStageResult.ok("load", "data1", 10.0),
            PipelineStageResult.ok("parse", "data2", 5.0),
        )
        result = PipelineResult(
            stages=stages,
            final_result="data2",
            success=True,
            total_duration_ms=15.0,
        )

        assert result.success is True
        assert result.final_result == "data2"
        assert result.failed_at == -1
        assert result.error is None
        assert result.aspect_names == ["load", "parse"]
        assert bool(result) is True

    def test_failed_result(self) -> None:
        """Test failed pipeline result."""
        error = ValueError("parse failed")
        stages = (
            PipelineStageResult.ok("load", "data1", 10.0),
            PipelineStageResult.fail("parse", error, 5.0),
        )
        result = PipelineResult(
            stages=stages,
            final_result=None,
            success=False,
            failed_at=1,
            total_duration_ms=15.0,
        )

        assert result.success is False
        assert result.final_result is None
        assert result.failed_at == 1
        assert result.error is error
        assert bool(result) is False


# === AspectPipeline Tests ===


class TestAspectPipeline:
    """Tests for AspectPipeline."""

    @pytest.fixture
    def node(self) -> MockNode:
        """Create a mock node for testing."""
        return MockNode()

    @pytest.fixture
    def observer(self) -> Observer:
        """Create a test observer."""
        return Observer.test()

    @pytest.mark.asyncio
    async def test_empty_pipeline(self, node: MockNode, observer: Observer) -> None:
        """Test pipeline with no aspects."""
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe(observer=observer)

        assert result.success is True
        assert result.final_result is None
        assert len(result.stages) == 0

    @pytest.mark.asyncio
    async def test_single_aspect(self, node: MockNode, observer: Observer) -> None:
        """Test pipeline with single aspect."""
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe("load", observer=observer)

        assert result.success is True
        assert result.final_result["content"] == "raw data"
        assert len(result.stages) == 1
        assert result.stages[0].aspect == "load"

    @pytest.mark.asyncio
    async def test_multiple_aspects(self, node: MockNode, observer: Observer) -> None:
        """Test pipeline with multiple aspects."""
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe("load", "parse", "transform", observer=observer)

        assert result.success is True
        assert len(result.stages) == 3
        assert result.final_result["transformed"] is True
        assert result.final_result["parsed"] is True

    @pytest.mark.asyncio
    async def test_initial_input(self, node: MockNode, observer: Observer) -> None:
        """Test pipeline with initial input."""
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe(
            "load",
            observer=observer,
            initial_input="initial data",
        )

        assert result.success is True
        assert result.final_result["input"] == "initial data"

    @pytest.mark.asyncio
    async def test_fail_fast(self, node: MockNode, observer: Observer) -> None:
        """Test fail-fast behavior."""
        pipeline = AspectPipeline(node).fail_fast(True)
        result = await pipeline.pipe(
            "load",
            "fail",
            "summarize",
            observer=observer,
        )

        assert result.success is False
        assert result.failed_at == 1
        assert len(result.stages) == 2  # Stopped after fail
        assert result.error is not None
        assert "Intentional failure" in str(result.error)

    @pytest.mark.asyncio
    async def test_collect_all(self, node: MockNode, observer: Observer) -> None:
        """Test collect-all behavior."""
        pipeline = AspectPipeline(node).fail_fast(False).collect_all(True)
        result = await pipeline.pipe(
            "load",
            "fail",
            "summarize",
            observer=observer,
        )

        assert result.success is False
        assert result.failed_at == 1
        assert len(result.stages) == 3  # Continued after fail

    @pytest.mark.asyncio
    async def test_fluent_api(self, node: MockNode, observer: Observer) -> None:
        """Test fluent builder API."""
        result = await (
            AspectPipeline(node).add("load").add("parse").add("transform").run(observer)
        )

        assert result.success is True
        assert len(result.stages) == 3

    @pytest.mark.asyncio
    async def test_duration_tracking(self, node: MockNode, observer: Observer) -> None:
        """Test duration tracking."""
        pipeline = AspectPipeline(node)
        result = await pipeline.pipe("slow", observer=observer)

        assert result.success is True
        assert result.total_duration_ms >= 100.0  # At least 100ms
        assert result.stages[0].duration_ms >= 100.0


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_pipeline(self) -> None:
        """Test create_pipeline factory."""
        node = MockNode()
        pipeline = create_pipeline(node, "load", "parse")

        assert pipeline.node is node
        assert pipeline.aspects == ["load", "parse"]

    def test_create_pipeline_empty(self) -> None:
        """Test create_pipeline with no aspects."""
        node = MockNode()
        pipeline = create_pipeline(node)

        assert pipeline.node is node
        assert pipeline.aspects == []


# === Integration Tests ===


class TestPipelineIntegration:
    """Integration tests for pipeline system."""

    @pytest.mark.asyncio
    async def test_data_flow_through_pipeline(self) -> None:
        """Test data flows correctly through pipeline."""
        node = MockNode()
        observer = Observer.test()

        pipeline = AspectPipeline(node)
        result = await pipeline.pipe(
            "load",
            "parse",
            "summarize",
            observer=observer,
        )

        assert result.success is True
        # Final result should be a summary string
        assert "Summary of:" in result.final_result
        assert "parsed" in result.final_result

    @pytest.mark.asyncio
    async def test_error_context_preserved(self) -> None:
        """Test error context is preserved in result."""
        node = MockNode()
        observer = Observer.test()

        pipeline = AspectPipeline(node)
        result = await pipeline.pipe(
            "load",
            "fail",
            observer=observer,
        )

        assert result.success is False
        assert result.failed_at == 1
        assert isinstance(result.error, ValueError)
        assert result.stages[0].success is True
        assert result.stages[1].success is False

    @pytest.mark.asyncio
    async def test_partial_results_on_failure(self) -> None:
        """Test partial results available on failure."""
        node = MockNode()
        observer = Observer.test()

        pipeline = AspectPipeline(node)
        result = await pipeline.pipe(
            "load",
            "parse",
            "fail",
            "summarize",
            observer=observer,
        )

        # First two stages succeeded
        assert result.stages[0].success is True
        assert result.stages[0].result["content"] == "raw data"
        assert result.stages[1].success is True
        assert result.stages[1].result["parsed"] is True
        # Third stage failed
        assert result.stages[2].success is False
