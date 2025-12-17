"""
Tests for CLI Projection Functor - Wave 1 Crown Jewels Migration.

Tests the core projection infrastructure from spec/protocols/cli.md Part III.
"""

from __future__ import annotations

import pytest

from protocols.agentese.affordances import (
    AspectCategory,
    AspectMetadata,
    DeclaredEffect,
    Effect,
)
from protocols.cli.dimensions import (
    Backend,
    CommandDimensions,
    Execution,
    Intent,
    Interactivity,
    Seriousness,
    Statefulness,
    derive_dimensions,
)
from protocols.cli.projection import (
    CLIProjection,
    TerminalOutput,
    _format_result,
    _parse_kwargs_from_args,
    route_to_path,
)


# === Test TerminalOutput ===


def test_terminal_output_to_json():
    """TerminalOutput.to_json renders metadata."""
    output = TerminalOutput(
        content="Hello",
        metadata={"key": "value"},
        exit_code=0,
    )
    json_str = output.to_json()
    assert '"content": "Hello"' in json_str
    assert '"key": "value"' in json_str


def test_terminal_output_to_plain():
    """TerminalOutput.to_plain renders content."""
    output = TerminalOutput(content="Hello world")
    assert output.to_plain() == "Hello world"


def test_terminal_output_error():
    """TerminalOutput.to_plain shows error message."""
    output = TerminalOutput(content="", error="Something went wrong")
    assert "Something went wrong" in output.to_plain()


# === Test Dimension Derivation for Crown Jewels ===


def test_brain_capture_dimensions():
    """self.memory.capture should derive ASYNC, STATEFUL, with budget."""
    meta = AspectMetadata(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("memory_crystals"),
            Effect.CALLS("embedder"),
        ],
        requires_archetype=(),
        idempotent=False,
        description="Capture content to holographic memory",
        help="Capture content to holographic memory",
        budget_estimate="~50 tokens (embedding)",
    )
    dims = derive_dimensions("self.memory.capture", meta)

    assert dims.execution == Execution.ASYNC
    assert dims.statefulness == Statefulness.STATEFUL
    # Backend depends on effect target - embedder isn't "llm" so EXTERNAL
    assert dims.backend == Backend.EXTERNAL
    # "memory_crystals" is not in PROTECTED_RESOURCES (only "memory" is), so NEUTRAL
    assert dims.seriousness == Seriousness.NEUTRAL


def test_brain_search_dimensions():
    """self.memory.recall (search) should derive PERCEPTION characteristics."""
    meta = AspectMetadata(
        category=AspectCategory.PERCEPTION,
        effects=[
            Effect.READS("memory_crystals"),
            Effect.CALLS("embedder"),
        ],
        requires_archetype=(),
        idempotent=True,
        description="Semantic search for similar memories",
        help="Semantic search for similar memories",
        budget_estimate="~50 tokens",
    )
    dims = derive_dimensions("self.memory.recall", meta)

    # PERCEPTION is sync by default, but CALLS overrides to async
    assert dims.execution == Execution.ASYNC
    # READS makes it stateful
    assert dims.statefulness == Statefulness.STATEFUL
    # Not SENSITIVE because only reads (not writes to protected)
    assert dims.seriousness == Seriousness.NEUTRAL


def test_brain_surface_dimensions():
    """void.memory.surface should derive ENTROPY/PLAYFUL characteristics."""
    meta = AspectMetadata(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("memory_crystals")],
        requires_archetype=(),
        idempotent=True,
        description="Surface a serendipitous memory",
        help="Surface a serendipitous memory from the void",
    )
    dims = derive_dimensions("void.memory.surface", meta)

    # ENTROPY is sync by default
    assert dims.execution == Execution.SYNC
    # void.* context is PLAYFUL
    assert dims.seriousness == Seriousness.PLAYFUL


def test_soul_dialogue_dimensions():
    """self.soul.dialogue should derive MUTATION with LLM backend."""
    meta = AspectMetadata(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.CALLS("llm"),
            Effect.CHARGES("tokens"),
        ],
        requires_archetype=(),
        idempotent=False,
        description="Direct dialogue with K-gent",
        help="Direct dialogue with K-gent (legacy, prefer chat.*)",
        budget_estimate="~500 tokens",
    )
    dims = derive_dimensions("self.soul.dialogue", meta)

    assert dims.execution == Execution.ASYNC
    assert dims.backend == Backend.LLM
    assert dims.needs_budget_display is True


# === Test Kwargs Parsing ===


def test_parse_kwargs_capture():
    """Parse kwargs for capture command."""
    args = ["capture", "Hello", "world"]
    kwargs = _parse_kwargs_from_args(args, "self.memory.capture")

    assert kwargs.get("content") == "Hello world"


def test_parse_kwargs_search():
    """Parse kwargs for search command."""
    args = ["search", "category", "theory"]
    # Note: recall path doesn't contain "search" so uses default "content"
    kwargs = _parse_kwargs_from_args(args, "self.memory.search")

    assert kwargs.get("query") == "category theory"


def test_parse_kwargs_surface():
    """Parse kwargs for surface command."""
    args = ["surface", "agents"]
    kwargs = _parse_kwargs_from_args(args, "void.memory.surface")

    assert kwargs.get("context") == "agents"


def test_parse_kwargs_with_flags():
    """Parse kwargs with --key=value flags."""
    args = ["capture", "content", "--limit=10", "--dry-run"]
    kwargs = _parse_kwargs_from_args(args, "self.memory.capture")

    assert kwargs.get("content") == "content"
    assert kwargs.get("limit") == "10"
    assert kwargs.get("dry_run") is True


def test_parse_kwargs_with_key_value():
    """Parse kwargs with --key value pairs."""
    args = ["search", "--limit", "20", "query text"]
    kwargs = _parse_kwargs_from_args(args, "self.memory.search")

    assert kwargs.get("limit") == "20"
    assert kwargs.get("query") == "query text"


# === Test Subcommand Routing ===


def test_route_to_path_brain():
    """Test subcommand routing for brain."""
    BRAIN_MAP = {
        "capture": "self.memory.capture",
        "search": "self.memory.recall",
        "ghost": "self.memory.ghost.surface",
        "surface": "void.memory.surface",
        "list": "self.memory.manifest",
        "status": "self.memory.manifest",
    }

    assert route_to_path("capture", BRAIN_MAP, "self.memory.manifest") == "self.memory.capture"
    assert route_to_path("search", BRAIN_MAP, "self.memory.manifest") == "self.memory.recall"
    assert route_to_path("unknown", BRAIN_MAP, "self.memory.manifest") == "self.memory.manifest"


def test_route_to_path_soul():
    """Test subcommand routing for soul."""
    SOUL_MAP = {
        "reflect": "self.soul.reflect",
        "challenge": "self.soul.challenge",
        "manifest": "self.soul.manifest",
        "starters": "self.soul.starters",
    }

    assert route_to_path("reflect", SOUL_MAP, "self.soul.manifest") == "self.soul.reflect"
    assert route_to_path("challenge", SOUL_MAP, "self.soul.manifest") == "self.soul.challenge"


# === Test Result Formatting ===


def test_format_result_dict():
    """Format dict result with neutral seriousness."""
    dims = CommandDimensions(
        execution=Execution.SYNC,
        statefulness=Statefulness.STATELESS,
        backend=Backend.PURE,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.NEUTRAL,
        interactivity=Interactivity.ONESHOT,
    )
    result = {"status": "captured", "concept_id": "abc123"}

    output = _format_result(result, dims)
    assert output.exit_code == 0
    assert "status" in output.content
    assert "captured" in output.content


def test_format_result_playful():
    """Format dict result with playful seriousness (emojis)."""
    dims = CommandDimensions(
        execution=Execution.SYNC,
        statefulness=Statefulness.STATELESS,
        backend=Backend.PURE,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.PLAYFUL,
        interactivity=Interactivity.ONESHOT,
    )
    result = {"status": "surfaced", "count": 5}

    output = _format_result(result, dims)
    # Playful format should include emoji
    assert any(char not in "abcdefghijklmnopqrstuvwxyz0123456789:_ \n" for char in output.content)


def test_format_result_error():
    """Format dict result with error."""
    dims = CommandDimensions(
        execution=Execution.SYNC,
        statefulness=Statefulness.STATELESS,
        backend=Backend.PURE,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.NEUTRAL,
        interactivity=Interactivity.ONESHOT,
    )
    result = {"error": "content is required"}

    output = _format_result(result, dims)
    assert output.exit_code == 1
    assert output.error == "content is required"


def test_format_result_json():
    """Format dict result as JSON."""
    dims = CommandDimensions(
        execution=Execution.SYNC,
        statefulness=Statefulness.STATELESS,
        backend=Backend.PURE,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.NEUTRAL,
        interactivity=Interactivity.ONESHOT,
    )
    result = {"status": "captured", "concept_id": "abc123"}

    output = _format_result(result, dims, json_output=True)
    assert '"status"' in output.content
    assert '"captured"' in output.content


# === Test Dimension Convenience Properties ===


def test_dimension_convenience_properties():
    """Test CommandDimensions convenience properties."""
    dims = CommandDimensions(
        execution=Execution.ASYNC,
        statefulness=Statefulness.STATEFUL,
        backend=Backend.LLM,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.SENSITIVE,
        interactivity=Interactivity.STREAMING,
    )

    assert dims.is_async is True
    assert dims.needs_state is True
    assert dims.needs_budget_display is True
    assert dims.needs_confirmation is True
    assert dims.is_streaming is True
    assert dims.is_interactive is False


def test_dimension_str():
    """Test CommandDimensions string representation."""
    dims = CommandDimensions(
        execution=Execution.ASYNC,
        statefulness=Statefulness.STATEFUL,
        backend=Backend.LLM,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.NEUTRAL,
        interactivity=Interactivity.ONESHOT,
    )

    dim_str = str(dims)
    assert "ASYNC" in dim_str
    assert "STATEFUL" in dim_str
    assert "LLM" in dim_str


# === Integration Tests (if Logos available) ===


@pytest.mark.asyncio
async def test_cli_projection_with_mock_logos():
    """Test CLIProjection with mock Logos."""
    from protocols.agentese.node import Observer

    # Create a mock logos
    class MockLogos:
        async def invoke(self, path, observer, **kwargs):
            return {"status": "invoked", "path": path, "kwargs": kwargs}

        def get_aspect_meta(self, path):
            return AspectMetadata(
                category=AspectCategory.PERCEPTION,
                effects=[],
                requires_archetype=(),
                idempotent=True,
                description="Test",
                help="Test",
            )

    logos = MockLogos()
    projection = CLIProjection(logos=logos, json_output=False)

    # Observer uses archetype and capabilities, not name
    observer = Observer.from_archetype("cli")

    dims = CommandDimensions(
        execution=Execution.SYNC,
        statefulness=Statefulness.STATELESS,
        backend=Backend.PURE,
        intent=Intent.FUNCTIONAL,
        seriousness=Seriousness.NEUTRAL,
        interactivity=Interactivity.ONESHOT,
    )

    output = await projection.project(
        "self.memory.manifest",
        observer,
        dims,
        {},
    )

    assert output.exit_code == 0
    assert "invoked" in output.content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
