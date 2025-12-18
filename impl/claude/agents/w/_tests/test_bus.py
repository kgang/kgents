"""
Tests for W-gent Middleware Bus.

Tests verify:
- Basic message dispatch
- Interceptor ordering
- Message blocking
- Fallback handlers
- Agent registry
- Error handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from agents.w.bus import (
    AgentRegistry,
    BaseInterceptor,
    BlockingInterceptor,
    BusMessage,
    InterceptorResult,
    LoggingInterceptor,
    MessagePriority,
    MiddlewareBus,
    PassthroughInterceptor,
    create_bus,
)

# --- Test Agents ---


@dataclass
class EchoAgent:
    """Returns input unchanged."""

    name: str = "echo"

    async def invoke(self, input: Any) -> Any:
        return input


@dataclass
class DoubleAgent:
    """Doubles numeric input."""

    name: str = "double"

    async def invoke(self, input: int) -> int:
        return input * 2


@dataclass
class FailingAgent:
    """Always raises an exception."""

    name: str = "failing"

    async def invoke(self, input: Any) -> Any:
        raise ValueError("Intentional failure")


@dataclass
class AddPrefixAgent:
    """Adds prefix to string input."""

    prefix: str
    name: str = "prefix"

    async def invoke(self, input: str) -> str:
        return f"{self.prefix}{input}"


# --- Test Interceptors ---


class CountingInterceptor(BaseInterceptor):
    """Counts before/after calls."""

    def __init__(self, name: str = "counting", order: int = 100) -> None:
        super().__init__(name, order)
        self.before_count = 0
        self.after_count = 0

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        self.before_count += 1
        return msg

    async def after(self, msg: BusMessage[Any, Any], result: Any) -> InterceptorResult[Any]:
        self.after_count += 1
        return InterceptorResult(value=result)


class TransformInterceptor(BaseInterceptor):
    """Transforms payload in before hook."""

    def __init__(self, transform_fn: Any, name: str = "transform", order: int = 100) -> None:
        super().__init__(name, order)
        self._transform = transform_fn

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        msg.payload = self._transform(msg.payload)
        return msg


class ResultTransformInterceptor(BaseInterceptor):
    """Transforms result in after hook."""

    def __init__(self, transform_fn: Any, name: str = "result_transform", order: int = 100) -> None:
        super().__init__(name, order)
        self._transform = transform_fn

    async def after(self, msg: BusMessage[Any, Any], result: Any) -> InterceptorResult[Any]:
        return InterceptorResult(
            value=self._transform(result),
            modified=True,
        )


class MetadataInterceptor(BaseInterceptor):
    """Adds metadata to results."""

    def __init__(self, metadata: dict[str, Any], name: str = "metadata", order: int = 200) -> None:
        super().__init__(name, order)
        self._metadata = metadata

    async def after(self, msg: BusMessage[Any, Any], result: Any) -> InterceptorResult[Any]:
        return InterceptorResult(
            value=result,
            metadata=self._metadata.copy(),
        )


# --- BusMessage Tests ---


class TestBusMessage:
    """Tests for BusMessage dataclass."""

    def test_create_basic_message(self) -> None:
        """Test basic message creation."""
        msg: BusMessage[str, str] = BusMessage(source="cli", target="psi", payload="hello")

        assert msg.source == "cli"
        assert msg.target == "psi"
        assert msg.payload == "hello"
        assert not msg.blocked
        assert msg.block_reason is None
        assert msg.priority == MessagePriority.NORMAL

    def test_message_blocking(self) -> None:
        """Test message blocking mechanism."""
        msg: BusMessage[str, str] = BusMessage(source="cli", target="psi", payload="data")

        msg.block("Rate limited")

        assert msg.blocked
        assert msg.block_reason == "Rate limited"

    def test_message_context(self) -> None:
        """Test context setting and getting."""
        msg: BusMessage[int, str] = BusMessage(source="a", target="b", payload=42)

        msg.set_context("token_cost", 100)
        msg.set_context("user_id", "user-123")

        assert msg.get_context("token_cost") == 100
        assert msg.get_context("user_id") == "user-123"
        assert msg.get_context("missing") is None
        assert msg.get_context("missing", "default") == "default"

    def test_message_priority(self) -> None:
        """Test priority levels."""
        low: BusMessage[int, str] = BusMessage(
            source="a", target="b", payload=1, priority=MessagePriority.LOW
        )
        high: BusMessage[int, str] = BusMessage(
            source="a", target="b", payload=2, priority=MessagePriority.HIGH
        )
        critical: BusMessage[int, str] = BusMessage(
            source="a", target="b", payload=3, priority=MessagePriority.CRITICAL
        )

        assert low.priority.value < high.priority.value < critical.priority.value

    def test_message_unique_id(self) -> None:
        """Test that each message gets a unique ID."""
        msg1: BusMessage[int, str] = BusMessage(source="a", target="b", payload=1)
        msg2: BusMessage[int, str] = BusMessage(source="a", target="b", payload=1)

        # IDs should be different (timestamp-based)
        assert msg1.message_id != msg2.message_id


# --- AgentRegistry Tests ---


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    @pytest.fixture
    def registry(self) -> AgentRegistry:
        return AgentRegistry()

    def test_register_agent(self, registry: AgentRegistry) -> None:
        """Test agent registration."""
        echo = EchoAgent()
        registry.register("echo", echo)

        assert registry.get("echo") is echo
        assert "echo" in registry.list_agents()

    def test_unregister_agent(self, registry: AgentRegistry) -> None:
        """Test agent unregistration."""
        registry.register("echo", EchoAgent())

        assert registry.unregister("echo")
        assert registry.get("echo") is None
        assert "echo" not in registry.list_agents()

    def test_unregister_nonexistent(self, registry: AgentRegistry) -> None:
        """Test unregistering non-existent agent."""
        assert not registry.unregister("nonexistent")

    @pytest.mark.asyncio
    async def test_invoke_agent(self, registry: AgentRegistry) -> None:
        """Test invoking registered agent."""
        registry.register("double", DoubleAgent())

        result = await registry.invoke("double", 5)

        assert result == 10

    @pytest.mark.asyncio
    async def test_invoke_nonexistent(self, registry: AgentRegistry) -> None:
        """Test invoking non-existent agent raises KeyError."""
        with pytest.raises(KeyError, match="Agent not found"):
            await registry.invoke("nonexistent", "data")


# --- BaseInterceptor Tests ---


class TestBaseInterceptor:
    """Tests for BaseInterceptor."""

    @pytest.mark.asyncio
    async def test_passthrough_before(self) -> None:
        """Test default before passes through."""
        interceptor = PassthroughInterceptor()
        msg: BusMessage[str, str] = BusMessage(source="a", target="b", payload="test")

        result = await interceptor.before(msg)

        assert result is msg
        assert result.payload == "test"

    @pytest.mark.asyncio
    async def test_passthrough_after(self) -> None:
        """Test default after wraps unchanged."""
        interceptor = PassthroughInterceptor()
        msg: BusMessage[str, str] = BusMessage(source="a", target="b", payload="test")

        result = await interceptor.after(msg, "output")

        assert result.value == "output"
        assert not result.modified


# --- MiddlewareBus Tests ---


class TestMiddlewareBus:
    """Tests for MiddlewareBus."""

    @pytest.fixture
    def bus(self) -> MiddlewareBus:
        bus = MiddlewareBus()
        bus.registry.register("echo", EchoAgent())
        bus.registry.register("double", DoubleAgent())
        bus.registry.register("failing", FailingAgent())
        return bus

    @pytest.mark.asyncio
    async def test_basic_dispatch(self, bus: MiddlewareBus) -> None:
        """Test basic message dispatch."""
        result: Any = await bus.send("cli", "echo", "hello")

        assert result.value == "hello"
        assert not result.blocked

    @pytest.mark.asyncio
    async def test_dispatch_with_transform(self, bus: MiddlewareBus) -> None:
        """Test dispatch with computation."""
        result: Any = await bus.send("cli", "double", 7)

        assert result.value == 14
        assert not result.blocked

    @pytest.mark.asyncio
    async def test_dispatch_to_unknown_target(self, bus: MiddlewareBus) -> None:
        """Test dispatch to non-existent target."""
        result: Any = await bus.send("cli", "nonexistent", "data")

        assert result.blocked
        assert result.block_reason is not None
        assert "not found" in result.block_reason.lower()

    @pytest.mark.asyncio
    async def test_dispatch_with_failing_agent(self, bus: MiddlewareBus) -> None:
        """Test dispatch when agent throws."""
        result: Any = await bus.send("cli", "failing", "data")

        assert result.blocked
        assert result.block_reason is not None
        assert "Invocation failed" in result.block_reason
        assert "error" in result.metadata

    @pytest.mark.asyncio
    async def test_interceptor_ordering(self, bus: MiddlewareBus) -> None:
        """Test interceptors run in order."""
        order_log: list[str] = []

        class OrderTracker(BaseInterceptor):
            def __init__(self, name: str, order: int) -> None:
                super().__init__(name, order)

            async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
                order_log.append(f"{self.name}:before")
                return msg

            async def after(self, msg: BusMessage[Any, Any], result: Any) -> InterceptorResult[Any]:
                order_log.append(f"{self.name}:after")
                return InterceptorResult(value=result)

        # Register out of order
        bus.register_interceptor(OrderTracker("third", 300))
        bus.register_interceptor(OrderTracker("first", 100))
        bus.register_interceptor(OrderTracker("second", 200))

        await bus.send("cli", "echo", "test")

        # Before hooks in ascending order
        assert order_log[:3] == ["first:before", "second:before", "third:before"]
        # After hooks in descending order
        assert order_log[3:] == ["third:after", "second:after", "first:after"]

    @pytest.mark.asyncio
    async def test_blocking_interceptor(self, bus: MiddlewareBus) -> None:
        """Test interceptor blocking message."""
        blocker = BlockingInterceptor(
            name="blocker",
            predicate=lambda m: m.payload == "blocked",
            reason="Payload is 'blocked'",
            order=50,
        )
        bus.register_interceptor(blocker)

        result: Any = await bus.send("cli", "echo", "blocked")

        assert result.blocked
        assert result.block_reason == "Payload is 'blocked'"
        assert result.value is None

    @pytest.mark.asyncio
    async def test_fallback_on_block(self, bus: MiddlewareBus) -> None:
        """Test fallback handler when message is blocked."""
        blocker = BlockingInterceptor(
            name="blocker",
            predicate=lambda _: True,
            reason="Always blocked",
        )
        bus.register_interceptor(blocker)
        bus.register_fallback("echo", lambda msg: "fallback_value")

        result: Any = await bus.send("cli", "echo", "anything")

        assert result.blocked
        assert result.value == "fallback_value"

    @pytest.mark.asyncio
    async def test_payload_transformation(self, bus: MiddlewareBus) -> None:
        """Test interceptor transforming payload."""
        transformer = TransformInterceptor(
            transform_fn=lambda x: x * 2,
            name="double_input",
            order=50,
        )
        bus.register_interceptor(transformer)

        result: Any = await bus.send("cli", "double", 5)

        # Input 5 -> doubled to 10 -> doubled again by agent to 20
        assert result.value == 20

    @pytest.mark.asyncio
    async def test_result_transformation(self, bus: MiddlewareBus) -> None:
        """Test interceptor transforming result."""
        transformer = ResultTransformInterceptor(
            transform_fn=lambda x: x + 100,
            name="add_100",
            order=200,
        )
        bus.register_interceptor(transformer)

        result: Any = await bus.send("cli", "double", 5)

        # 5 -> 10 (doubled) -> 110 (add 100)
        assert result.value == 110

    @pytest.mark.asyncio
    async def test_metadata_collection(self, bus: MiddlewareBus) -> None:
        """Test metadata collected from interceptors."""
        meta1 = MetadataInterceptor({"token_cost": 50}, name="cost", order=100)
        meta2 = MetadataInterceptor({"safety_score": 0.95}, name="safety", order=200)

        bus.register_interceptor(meta1)
        bus.register_interceptor(meta2)

        result: Any = await bus.send("cli", "echo", "test")

        assert result.metadata["token_cost"] == 50
        assert result.metadata["safety_score"] == 0.95

    @pytest.mark.asyncio
    async def test_unregister_interceptor(self, bus: MiddlewareBus) -> None:
        """Test removing an interceptor."""
        counter = CountingInterceptor("counter")
        bus.register_interceptor(counter)

        await bus.send("cli", "echo", "test1")
        assert counter.before_count == 1

        bus.unregister_interceptor("counter")

        await bus.send("cli", "echo", "test2")
        assert counter.before_count == 1  # Not incremented

    @pytest.mark.asyncio
    async def test_dispatch_timing(self, bus: MiddlewareBus) -> None:
        """Test dispatch records duration."""
        result: Any = await bus.send("cli", "echo", "test")

        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_interceptors_run_list(self, bus: MiddlewareBus) -> None:
        """Test tracking which interceptors ran."""
        bus.register_interceptor(CountingInterceptor("counter1", order=100))
        bus.register_interceptor(CountingInterceptor("counter2", order=200))

        result: Any = await bus.send("cli", "echo", "test")

        assert "counter1:before" in result.interceptors_run
        assert "counter2:before" in result.interceptors_run
        assert "counter1:after" in result.interceptors_run
        assert "counter2:after" in result.interceptors_run

    def test_list_interceptors(self, bus: MiddlewareBus) -> None:
        """Test listing interceptors in order."""
        bus.register_interceptor(CountingInterceptor("third", order=300))
        bus.register_interceptor(CountingInterceptor("first", order=100))
        bus.register_interceptor(CountingInterceptor("second", order=200))

        names = bus.list_interceptors()

        assert names == ["first", "second", "third"]


# --- LoggingInterceptor Tests ---


class TestLoggingInterceptor:
    """Tests for LoggingInterceptor."""

    @pytest.mark.asyncio
    async def test_logging_records_messages(self) -> None:
        """Test logging interceptor records all messages."""
        bus = MiddlewareBus()
        bus.registry.register("echo", EchoAgent())

        logger = LoggingInterceptor()
        bus.register_interceptor(logger)

        await bus.send("cli", "echo", "test1")
        await bus.send("cli", "echo", "test2")

        # Should have 4 log entries (2 before + 2 after)
        assert len(logger.log) == 4

        # Check structure
        before_entries = [e for e in logger.log if e["phase"] == "before"]
        after_entries = [e for e in logger.log if e["phase"] == "after"]

        assert len(before_entries) == 2
        assert len(after_entries) == 2


# --- create_bus Tests ---


class TestCreateBus:
    """Tests for create_bus factory."""

    @pytest.mark.asyncio
    async def test_create_with_interceptors(self) -> None:
        """Test creating bus with interceptors."""
        counter1 = CountingInterceptor("c1", order=100)
        counter2 = CountingInterceptor("c2", order=200)

        bus = create_bus(counter1, counter2)
        bus.registry.register("echo", EchoAgent())

        await bus.send("cli", "echo", "test")

        assert counter1.before_count == 1
        assert counter2.before_count == 1


# --- Integration Tests ---


class TestBusIntegration:
    """Integration tests for the full bus flow."""

    @pytest.mark.asyncio
    async def test_multiple_agents_chain(self) -> None:
        """Test dispatching to multiple agents in sequence."""
        bus = MiddlewareBus()
        bus.registry.register("prefix", AddPrefixAgent(prefix="["))
        bus.registry.register("suffix", AddPrefixAgent(prefix="]"))

        # First dispatch
        result1: Any = await bus.send("cli", "prefix", "hello")
        assert result1.value == "[hello"

        # Second dispatch using first result
        result2: Any = await bus.send("cli", "suffix", result1.value)
        assert result2.value == "][hello"

    @pytest.mark.asyncio
    async def test_context_propagation(self) -> None:
        """Test context flows through interceptors."""
        bus = MiddlewareBus()
        bus.registry.register("echo", EchoAgent())

        class ContextWriter(BaseInterceptor):
            async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
                msg.set_context("written_by", "ContextWriter")
                return msg

        class ContextReader(BaseInterceptor):
            def __init__(self) -> None:
                super().__init__("reader", order=200)
                self.read_context: Any = None

            async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
                self.read_context = msg.get_context("written_by")
                return msg

        writer = ContextWriter("writer", order=100)
        reader = ContextReader()

        bus.register_interceptor(writer)
        bus.register_interceptor(reader)

        await bus.send("cli", "echo", "test")

        assert reader.read_context == "ContextWriter"

    @pytest.mark.asyncio
    async def test_full_interceptor_chain(self) -> None:
        """Test complete interceptor chain with all features."""
        bus = MiddlewareBus()
        bus.registry.register("double", DoubleAgent())

        # Safety check (blocks negative numbers)
        safety = BlockingInterceptor(
            name="safety",
            predicate=lambda m: m.payload < 0,
            reason="Negative numbers blocked",
            order=50,
        )

        # Token metering (adds cost metadata)
        metering = MetadataInterceptor(
            metadata={"token_cost": 10},
            name="metering",
            order=100,
        )

        # Logging
        logger = LoggingInterceptor()

        bus.register_interceptor(safety)
        bus.register_interceptor(metering)
        bus.register_interceptor(logger)

        # Positive number should succeed
        result: Any = await bus.send("cli", "double", 5)
        assert result.value == 10
        assert result.metadata.get("token_cost") == 10
        assert not result.blocked

        # Negative number should be blocked by safety
        result = await bus.send("cli", "double", -5)
        assert result.blocked
        assert result.block_reason is not None
        assert "Negative numbers blocked" in result.block_reason
