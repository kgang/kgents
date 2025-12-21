"""Tests for L0 primitives."""

import pytest

from protocols.ashc.ast import LiteralPattern, WildcardPattern
from protocols.ashc.primitives import (
    Artifact,
    ComposedCallable,
    L0Primitives,
    TraceWitnessResult,
    VerificationStatus,
    get_primitives,
)


class TestCompose:
    """Tests for compose primitive."""

    def test_compose_sync_functions(self) -> None:
        """Compose synchronous functions."""
        prims = get_primitives()
        f = lambda x: x + 1
        g = lambda x: x * 2

        composed = prims.compose(f, g)
        assert isinstance(composed, ComposedCallable)

    @pytest.mark.asyncio
    async def test_composed_execution(self) -> None:
        """Composed callable executes correctly."""
        prims = get_primitives()
        f = lambda x: x + 1
        g = lambda x: x * 2

        composed = prims.compose(f, g)
        result = await composed(5)
        # (5 + 1) * 2 = 12
        assert result == 12

    @pytest.mark.asyncio
    async def test_compose_async_functions(self) -> None:
        """Compose async functions."""
        prims = get_primitives()

        async def f(x: int) -> int:
            return x + 1

        async def g(x: int) -> int:
            return x * 2

        composed = prims.compose(f, g)
        result = await composed(5)
        assert result == 12

    @pytest.mark.asyncio
    async def test_compose_mixed_sync_async(self) -> None:
        """Compose mixed sync and async functions."""
        prims = get_primitives()

        def f(x: int) -> int:
            return x + 1

        async def g(x: int) -> int:
            return x * 2

        composed = prims.compose(f, g)
        result = await composed(5)
        assert result == 12


class TestApply:
    """Tests for apply primitive."""

    @pytest.mark.asyncio
    async def test_apply_sync_function(self) -> None:
        """Apply sync function."""
        prims = get_primitives()
        f = lambda x: x * 2
        result = await prims.apply(f, 21)
        assert result == 42

    @pytest.mark.asyncio
    async def test_apply_async_function(self) -> None:
        """Apply async function."""
        prims = get_primitives()

        async def f(x: int) -> int:
            return x * 2

        result = await prims.apply(f, 21)
        assert result == 42


class TestMatch:
    """Tests for match primitive."""

    def test_match_literal(self) -> None:
        """Match literal pattern."""
        prims = get_primitives()
        result = prims.match(LiteralPattern(42), 42)
        assert result == {}

    def test_match_wildcard(self) -> None:
        """Match wildcard pattern."""
        prims = get_primitives()
        result = prims.match(WildcardPattern("x"), 42)
        assert result == {"x": 42}

    def test_match_failure(self) -> None:
        """Match failure returns None."""
        prims = get_primitives()
        result = prims.match(LiteralPattern(42), 43)
        assert result is None


class TestEmit:
    """Tests for emit primitive."""

    def test_emit_creates_artifact(self) -> None:
        """Emit creates artifact with correct type."""
        prims = get_primitives()
        artifact = prims.emit("JSON", {"key": "value"})
        assert isinstance(artifact, Artifact)
        assert artifact.artifact_type == "JSON"
        assert artifact.content == {"key": "value"}

    def test_emit_has_timestamp(self) -> None:
        """Emitted artifact has timestamp."""
        prims = get_primitives()
        artifact = prims.emit("IR", "code")
        assert artifact.timestamp is not None


class TestWitness:
    """Tests for witness primitive."""

    def test_witness_creates_result(self) -> None:
        """Witness creates TraceWitnessResult."""
        prims = get_primitives()
        witness = prims.witness(
            "test_pass",
            {"input": "data"},
            {"output": "result"},
        )
        assert isinstance(witness, TraceWitnessResult)
        assert witness.agent_path == "concept.compiler.l0.test_pass"
        assert witness.verification_status == VerificationStatus.SUCCESS

    def test_witness_full_capture(self) -> None:
        """Witness captures full input/output."""
        prims = get_primitives()
        input_data = {"complex": [1, 2, 3], "nested": {"a": 1}}
        output_data = {"result": "success"}

        witness = prims.witness("capture_test", input_data, output_data)

        # Verify input is fully captured
        assert witness.input_data is not None
        assert "_type" in witness.input_data
        # Verify output is fully captured
        assert witness.output_data is not None
        assert "_type" in witness.output_data

    def test_witness_has_uuid(self) -> None:
        """Witness has unique ID."""
        prims = get_primitives()
        w1 = prims.witness("p1", {}, {})
        w2 = prims.witness("p2", {}, {})
        assert w1.witness_id != w2.witness_id

    def test_witness_has_timestamp(self) -> None:
        """Witness has creation timestamp."""
        prims = get_primitives()
        witness = prims.witness("p", {}, {})
        assert witness.created_at is not None


class TestSerialization:
    """Tests for witness serialization."""

    def test_serialize_primitives(self) -> None:
        """Serialize primitive types."""
        prims = get_primitives()
        assert prims._serialize(42) == {"_type": "int", "_value": 42}
        assert prims._serialize("hello") == {"_type": "str", "_value": "hello"}
        assert prims._serialize(True) == {"_type": "bool", "_value": True}
        assert prims._serialize(3.14) == {"_type": "float", "_value": 3.14}

    def test_serialize_none(self) -> None:
        """Serialize None."""
        prims = get_primitives()
        assert prims._serialize(None) == {"_type": "null", "_value": None}

    def test_serialize_dict(self) -> None:
        """Serialize dict."""
        prims = get_primitives()
        result = prims._serialize({"a": 1, "b": 2})
        assert result["_type"] == "dict"
        assert "_value" in result

    def test_serialize_list(self) -> None:
        """Serialize list."""
        prims = get_primitives()
        result = prims._serialize([1, 2, 3])
        assert result["_type"] == "list"
        assert len(result["_value"]) == 3

    def test_serialize_object(self) -> None:
        """Serialize object with __dict__."""
        prims = get_primitives()

        class TestObj:
            def __init__(self) -> None:
                self.x = 1
                self.y = 2

        result = prims._serialize(TestObj())
        assert result["_type"] == "TestObj"
        assert "_value" in result


class TestGetPrimitives:
    """Tests for get_primitives factory."""

    def test_returns_instance(self) -> None:
        """get_primitives returns L0Primitives instance."""
        prims = get_primitives()
        assert isinstance(prims, L0Primitives)
