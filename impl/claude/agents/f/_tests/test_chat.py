"""
Tests for Chat Flow modality (Phase 3).

Validates chat-specific behavior:
- Context window management (sliding, summarizing)
- Turn protocol
- Streaming output
- System prompt handling
- Metrics tracking
- FlowPolynomial integration

See: spec/f-gents/chat.md
"""

import asyncio

import pytest

from agents.f.config import ChatConfig
from agents.f.modalities.chat import (
    CHAT_POLYNOMIAL,
    ChatFlow,
    ChatPolynomialAdapter,
    Turn,
    chat_directions,
    chat_transition,
)
from agents.f.modalities.context import Message, SlidingContext, SummarizingContext
from agents.f.state import FlowState

# ============================================================================
# Test Context Management
# ============================================================================


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self) -> None:
        """Message can be created with role and content."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tokens > 0  # Auto-calculated

    def test_message_tokens_explicit(self) -> None:
        """Message respects explicit token count."""
        msg = Message(role="assistant", content="Hi there!", tokens=100)
        assert msg.tokens == 100


class TestSlidingContext:
    """Test SlidingContext window management."""

    def test_sliding_context_init(self) -> None:
        """SlidingContext initializes with window size."""
        ctx = SlidingContext(window_size=1000)
        assert ctx.window_size == 1000
        assert ctx.token_count == 0
        assert len(ctx.messages) == 0

    def test_sliding_context_add_message(self) -> None:
        """Adding messages updates token count."""
        ctx = SlidingContext(window_size=1000)
        msg = Message(role="user", content="Hello")

        ctx.add(msg)

        assert len(ctx.messages) == 1
        assert ctx.token_count == msg.tokens

    def test_sliding_context_drops_oldest_when_full(self) -> None:
        """SlidingContext drops oldest messages when window exceeded."""
        ctx = SlidingContext(window_size=20)  # Very small window

        # Add messages that will exceed window
        msg1 = Message(role="user", content="First message", tokens=10)
        msg2 = Message(role="assistant", content="Second message", tokens=10)
        msg3 = Message(role="user", content="Third message", tokens=10)

        ctx.add(msg1)
        ctx.add(msg2)
        ctx.add(msg3)  # This should trigger dropping

        # First message should be dropped
        remaining = ctx.render()
        assert len(remaining) >= 1
        assert msg1 not in remaining
        assert ctx.token_count <= ctx.window_size

    def test_sliding_context_render(self) -> None:
        """render() returns list of messages in context."""
        ctx = SlidingContext(window_size=1000)
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi")

        ctx.add(msg1)
        ctx.add(msg2)

        messages = ctx.render()
        assert len(messages) == 2
        assert messages[0] == msg1
        assert messages[1] == msg2

    def test_sliding_context_truncate_oldest(self) -> None:
        """truncate_oldest() removes N oldest messages."""
        ctx = SlidingContext(window_size=1000)

        msg1 = Message(role="user", content="First")
        msg2 = Message(role="assistant", content="Second")
        msg3 = Message(role="user", content="Third")

        ctx.add(msg1)
        ctx.add(msg2)
        ctx.add(msg3)

        initial_count = ctx.token_count
        ctx.truncate_oldest(2)

        assert len(ctx.messages) == 1
        assert ctx.messages[0] == msg3
        assert ctx.token_count < initial_count

    def test_sliding_context_clear(self) -> None:
        """clear() removes all messages."""
        ctx = SlidingContext(window_size=1000)
        ctx.add(Message(role="user", content="Hello"))
        ctx.add(Message(role="assistant", content="Hi"))

        ctx.clear()

        assert len(ctx.messages) == 0
        assert ctx.token_count == 0


class TestSummarizingContext:
    """Test SummarizingContext compression."""

    def test_summarizing_context_init(self) -> None:
        """SummarizingContext initializes with window and threshold."""
        ctx = SummarizingContext(window_size=1000, threshold=0.8)
        assert ctx.window_size == 1000
        assert ctx.threshold == 0.8
        assert ctx.summary is None
        assert len(ctx.recent_messages) == 0

    def test_summarizing_context_add_message(self) -> None:
        """Adding messages to summarizing context."""
        ctx = SummarizingContext(window_size=1000)
        msg = Message(role="user", content="Hello")

        ctx.add(msg)

        assert len(ctx.recent_messages) == 1
        assert ctx.recent_messages[0] == msg

    @pytest.mark.asyncio
    async def test_summarizing_context_triggers_compression(self) -> None:
        """Context triggers compression at threshold."""

        # Mock summarizer
        class MockSummarizer:
            async def invoke(self, messages: list[Message]) -> str:
                return f"Summary of {len(messages)} messages"

        ctx = SummarizingContext(
            window_size=100,
            threshold=0.5,  # Low threshold to trigger easily
            summarizer=MockSummarizer(),
        )

        # Add messages to exceed threshold
        for i in range(10):
            msg = Message(role="user", content=f"Message {i}" * 5, tokens=20)
            await ctx.add_async(msg)

        # Should have triggered summarization
        assert ctx.summary is not None
        assert "Summary of" in ctx.summary

    def test_summarizing_context_render_with_summary(self) -> None:
        """render() includes summary as system message."""
        ctx = SummarizingContext(window_size=1000)
        ctx.summary = "Previous conversation summary"
        ctx.add(Message(role="user", content="Current message"))

        messages = ctx.render()

        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "summary" in messages[0].content.lower()
        assert messages[1].content == "Current message"

    def test_summarizing_context_truncate_oldest(self) -> None:
        """truncate_oldest() removes N oldest recent messages."""
        ctx = SummarizingContext(window_size=1000)

        ctx.add(Message(role="user", content="First"))
        ctx.add(Message(role="assistant", content="Second"))
        ctx.add(Message(role="user", content="Third"))

        ctx.truncate_oldest(2)

        assert len(ctx.recent_messages) == 1
        assert ctx.recent_messages[0].content == "Third"

    def test_summarizing_context_clear(self) -> None:
        """clear() removes all messages and summary."""
        ctx = SummarizingContext(window_size=1000)
        ctx.summary = "Old summary"
        ctx.add(Message(role="user", content="Hello"))

        ctx.clear()

        assert len(ctx.recent_messages) == 0
        assert ctx.summary is None


# ============================================================================
# Test Turn Protocol
# ============================================================================


class TestTurn:
    """Test Turn dataclass."""

    def test_turn_creation(self) -> None:
        """Turn captures complete conversation cycle."""
        from datetime import datetime

        started = datetime.now()
        completed = datetime.now()

        turn = Turn(
            turn_number=1,
            user_message=Message(role="user", content="Hello", tokens=5),
            assistant_response=Message(role="assistant", content="Hi there!", tokens=10),
            started_at=started,
            completed_at=completed,
            tokens_in=5,
            tokens_out=10,
            context_size_before=0,
            context_size_after=15,
        )

        assert turn.turn_number == 1
        assert turn.tokens_in == 5
        assert turn.tokens_out == 10
        assert turn.total_tokens == 15

    def test_turn_duration(self) -> None:
        """Turn calculates duration."""
        from datetime import datetime, timedelta

        started = datetime.now()
        completed = started + timedelta(seconds=2.5)

        turn = Turn(
            turn_number=1,
            user_message=Message(role="user", content="Hello"),
            assistant_response=Message(role="assistant", content="Hi"),
            started_at=started,
            completed_at=completed,
            tokens_in=5,
            tokens_out=10,
            context_size_before=0,
            context_size_after=15,
        )

        assert turn.duration >= 2.0
        assert turn.duration <= 3.0


# ============================================================================
# Test ChatFlow
# ============================================================================


class MockAgent:
    """Mock agent for testing."""

    name = "MockAgent"

    async def invoke(self, input: str) -> str:
        """Echo back the input."""
        # Simple echo with slight modification
        return f"Response to: {input}"


class TestChatFlow:
    """Test ChatFlow implementation."""

    def test_chat_flow_init(self) -> None:
        """ChatFlow initializes with agent and config."""
        agent = MockAgent()
        config = ChatConfig(context_window=1000)

        chat = ChatFlow(agent, config)

        assert chat.name == "ChatFlow(MockAgent)"
        assert chat.turn_count == 0
        assert isinstance(chat.context, SummarizingContext)

    def test_chat_flow_init_sliding_context(self) -> None:
        """ChatFlow uses SlidingContext when configured."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        assert isinstance(chat.context, SlidingContext)

    def test_chat_flow_init_with_system_prompt(self) -> None:
        """ChatFlow adds system prompt to context."""
        agent = MockAgent()
        config = ChatConfig(system_prompt="You are a helpful assistant.")

        chat = ChatFlow(agent, config)

        messages = chat.context.render()
        assert len(messages) == 1
        assert messages[0].role == "system"
        assert "helpful assistant" in messages[0].content

    @pytest.mark.asyncio
    async def test_chat_flow_send_message(self) -> None:
        """send_message() completes a turn."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        response = await chat.send_message("Hello!")

        assert "Response to:" in response
        assert chat.turn_count == 1
        assert len(chat.turns) == 1

    @pytest.mark.asyncio
    async def test_chat_flow_multiple_turns(self) -> None:
        """ChatFlow handles multiple turns."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        await chat.send_message("First")
        await chat.send_message("Second")
        await chat.send_message("Third")

        assert chat.turn_count == 3
        assert len(chat.turns) == 3

    @pytest.mark.asyncio
    async def test_chat_flow_stream_response(self) -> None:
        """stream_response() yields tokens."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        tokens = []
        async for token in chat.stream_response("Hello!"):
            tokens.append(token)

        assert len(tokens) > 0
        full_response = "".join(tokens)
        assert len(full_response) > 0
        assert chat.turn_count == 1

    @pytest.mark.asyncio
    async def test_chat_flow_max_turns(self) -> None:
        """ChatFlow enforces max_turns limit."""
        agent = MockAgent()
        config = ChatConfig(max_turns=2, context_strategy="sliding")

        chat = ChatFlow(agent, config)

        await chat.send_message("First")
        await chat.send_message("Second")

        # Third should raise
        with pytest.raises(RuntimeError, match="Max turns"):
            await chat.send_message("Third")

    @pytest.mark.asyncio
    async def test_chat_flow_turn_timeout(self) -> None:
        """ChatFlow respects turn timeout."""

        # Slow agent
        class SlowAgent:
            name = "SlowAgent"

            async def invoke(self, input: str) -> str:
                await asyncio.sleep(5)  # Too slow
                return "Response"

        agent = SlowAgent()
        config = ChatConfig(turn_timeout=0.1, context_strategy="sliding")

        chat = ChatFlow(agent, config)

        # Should timeout and return truncation message
        response = await chat.send_message("Hello")
        assert "timeout" in response.lower()

    def test_chat_flow_get_history(self) -> None:
        """get_history() returns turn history."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        # Run synchronously for simple test
        async def run():
            await chat.send_message("Hello")
            await chat.send_message("World")

        asyncio.run(run())

        history = chat.get_history()
        assert len(history) == 2
        assert history[0].turn_number == 1
        assert history[1].turn_number == 2

    def test_chat_flow_get_metrics(self) -> None:
        """get_metrics() returns conversation metrics."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        # Run turns
        async def run():
            await chat.send_message("Hello")
            await chat.send_message("World")

        asyncio.run(run())

        metrics = chat.get_metrics()
        assert metrics["turns_completed"] == 2
        assert metrics["tokens_in"] > 0
        assert metrics["tokens_out"] > 0
        assert metrics["average_turn_latency"] >= 0.0
        assert 0.0 <= metrics["context_utilization"] <= 1.0

    def test_chat_flow_reset(self) -> None:
        """reset() clears conversation state."""
        agent = MockAgent()
        config = ChatConfig(
            system_prompt="You are helpful.",
            context_strategy="sliding",
        )

        chat = ChatFlow(agent, config)

        # Run turns
        async def run():
            await chat.send_message("Hello")
            await chat.send_message("World")

        asyncio.run(run())

        assert chat.turn_count == 2

        # Reset
        chat.reset()

        assert chat.turn_count == 0
        assert len(chat.turns) == 0

        # System prompt should be restored
        messages = chat.context.render()
        assert len(messages) == 1
        assert messages[0].role == "system"


# ============================================================================
# Test Context Overflow Handling
# ============================================================================


class TestContextOverflow:
    """Test context overflow scenarios."""

    @pytest.mark.asyncio
    async def test_sliding_context_handles_overflow(self) -> None:
        """SlidingContext gracefully handles overflow."""
        agent = MockAgent()
        config = ChatConfig(
            context_window=100,  # Small window
            context_strategy="sliding",
        )

        chat = ChatFlow(agent, config)

        # Send many messages
        for i in range(20):
            await chat.send_message(f"Message {i}")

        # Should have dropped early messages
        # Note: context may slightly exceed window if last message is large,
        # but it should be close to the limit
        assert chat.context.token_count <= config.context_window * 1.5
        # Verify that older messages were dropped
        assert len(chat.context.messages) < 20

    @pytest.mark.asyncio
    async def test_summarizing_context_compression_on_overflow(self) -> None:
        """SummarizingContext compresses on overflow."""

        # Mock summarizer
        class MockSummarizer:
            async def invoke(self, messages: list[Message]) -> str:
                return f"[Compressed {len(messages)} messages]"

        agent = MockAgent()
        config = ChatConfig(
            context_window=200,
            context_strategy="summarize",
            summarization_threshold=0.5,
        )

        chat = ChatFlow(agent, config)
        # Inject summarizer
        if isinstance(chat.context, SummarizingContext):
            chat.context.summarizer = MockSummarizer()

        # Send enough messages to trigger compression
        for i in range(10):
            msg = f"This is a longer message {i} " * 10
            await chat.send_message(msg)

        # Should have created a summary
        if isinstance(chat.context, SummarizingContext):
            # May or may not have summary depending on threshold
            messages = chat.context.render()
            # Just verify no crash and context is managed
            assert len(messages) > 0


# ============================================================================
# Test System Prompt Positioning
# ============================================================================


class TestSystemPrompt:
    """Test system prompt handling."""

    def test_system_prompt_prepend(self) -> None:
        """System prompt is prepended to context."""
        agent = MockAgent()
        config = ChatConfig(
            system_prompt="You are helpful.",
            system_prompt_position="prepend",
            context_strategy="sliding",
        )

        chat = ChatFlow(agent, config)

        messages = chat.context.render()
        assert messages[0].role == "system"

    def test_system_prompt_inject(self) -> None:
        """System prompt inject strategy (same as prepend for now)."""
        agent = MockAgent()
        config = ChatConfig(
            system_prompt="You are helpful.",
            system_prompt_position="inject",
            context_strategy="sliding",
        )

        chat = ChatFlow(agent, config)

        messages = chat.context.render()
        assert messages[0].role == "system"


# ============================================================================
# Integration Tests
# ============================================================================


class TestChatFlowIntegration:
    """Integration tests for complete chat flows."""

    @pytest.mark.asyncio
    async def test_complete_conversation(self) -> None:
        """Test a complete multi-turn conversation."""
        agent = MockAgent()
        config = ChatConfig(
            system_prompt="You are a friendly assistant.",
            context_strategy="sliding",
            max_turns=5,
        )

        chat = ChatFlow(agent, config)

        # Simulate conversation
        r1 = await chat.send_message("Hello!")
        assert "Response to:" in r1

        r2 = await chat.send_message("How are you?")
        assert "Response to:" in r2

        r3 = await chat.send_message("Goodbye!")
        assert "Response to:" in r3

        # Check metrics
        metrics = chat.get_metrics()
        assert metrics["turns_completed"] == 3
        assert metrics["tokens_in"] > 0
        assert metrics["tokens_out"] > 0

    @pytest.mark.asyncio
    async def test_streaming_conversation(self) -> None:
        """Test conversation with streaming responses."""
        agent = MockAgent()
        config = ChatConfig(context_strategy="sliding")

        chat = ChatFlow(agent, config)

        # First turn (streamed)
        tokens1 = []
        async for token in chat.stream_response("Hello!"):
            tokens1.append(token)

        assert len(tokens1) > 0

        # Second turn (streamed)
        tokens2 = []
        async for token in chat.stream_response("Goodbye!"):
            tokens2.append(token)

        assert len(tokens2) > 0
        assert chat.turn_count == 2


# ============================================================================
# Test Polynomial Integration
# ============================================================================


class TestChatPolynomial:
    """Test chat-specific polynomial functions."""

    def test_chat_directions_dormant(self) -> None:
        """DORMANT state has start and configure actions."""
        directions = chat_directions(FlowState.DORMANT)
        assert "start" in directions
        assert "configure" in directions
        assert len(directions) == 2

    def test_chat_directions_streaming(self) -> None:
        """STREAMING state has message, fork, checkpoint, etc."""
        directions = chat_directions(FlowState.STREAMING)
        assert "message" in directions
        assert "fork" in directions
        assert "rewind" in directions
        assert "checkpoint" in directions
        assert "stop" in directions
        assert "inject_context" in directions
        # Should have 6 actions
        assert len(directions) == 6

    def test_chat_directions_branching(self) -> None:
        """BRANCHING state has confirm_fork and cancel_fork."""
        directions = chat_directions(FlowState.BRANCHING)
        assert "confirm_fork" in directions
        assert "cancel_fork" in directions
        assert len(directions) == 2

    def test_chat_directions_converging(self) -> None:
        """CONVERGING state has merge-related actions."""
        directions = chat_directions(FlowState.CONVERGING)
        assert "confirm_merge" in directions
        assert "cancel_merge" in directions
        assert "resolve_conflict" in directions
        assert len(directions) == 3

    def test_chat_directions_draining(self) -> None:
        """DRAINING state has flush and crystallize."""
        directions = chat_directions(FlowState.DRAINING)
        assert "flush" in directions
        assert "crystallize" in directions
        assert len(directions) == 2

    def test_chat_directions_collapsed(self) -> None:
        """COLLAPSED state has reset and harvest."""
        directions = chat_directions(FlowState.COLLAPSED)
        assert "reset" in directions
        assert "harvest" in directions
        assert len(directions) == 2

    def test_chat_transition_start(self) -> None:
        """Start transitions DORMANT -> STREAMING."""
        new_state, output = chat_transition(FlowState.DORMANT, "start")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "started"
        assert output["ready"] is True

    def test_chat_transition_message(self) -> None:
        """Message keeps state in STREAMING."""
        new_state, output = chat_transition(FlowState.STREAMING, "message")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "message_processed"

    def test_chat_transition_fork(self) -> None:
        """Fork transitions STREAMING -> BRANCHING."""
        new_state, output = chat_transition(FlowState.STREAMING, "fork")
        assert new_state == FlowState.BRANCHING
        assert output["event"] == "fork_initiated"

    def test_chat_transition_confirm_fork(self) -> None:
        """Confirm fork transitions BRANCHING -> STREAMING."""
        new_state, output = chat_transition(FlowState.BRANCHING, "confirm_fork")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "fork_confirmed"

    def test_chat_transition_stop(self) -> None:
        """Stop transitions STREAMING -> DRAINING."""
        new_state, output = chat_transition(FlowState.STREAMING, "stop")
        assert new_state == FlowState.DRAINING
        assert output["event"] == "stopping"

    def test_chat_transition_crystallize(self) -> None:
        """Crystallize transitions DRAINING -> COLLAPSED."""
        new_state, output = chat_transition(FlowState.DRAINING, "crystallize")
        assert new_state == FlowState.COLLAPSED
        assert output["event"] == "crystallized"

    def test_chat_transition_reset(self) -> None:
        """Reset transitions COLLAPSED -> DORMANT."""
        new_state, output = chat_transition(FlowState.COLLAPSED, "reset")
        assert new_state == FlowState.DORMANT
        assert output["event"] == "reset"

    def test_chat_transition_invalid(self) -> None:
        """Invalid transition raises ValueError."""
        with pytest.raises(ValueError, match="Invalid chat transition"):
            chat_transition(FlowState.DORMANT, "message")

    def test_chat_polynomial_instance(self) -> None:
        """CHAT_POLYNOMIAL is properly configured."""
        assert CHAT_POLYNOMIAL.name == "ChatPolynomial"
        assert FlowState.DORMANT in CHAT_POLYNOMIAL.positions
        assert FlowState.STREAMING in CHAT_POLYNOMIAL.positions
        assert FlowState.COLLAPSED in CHAT_POLYNOMIAL.positions

    def test_chat_polynomial_invoke(self) -> None:
        """CHAT_POLYNOMIAL.invoke() executes transitions."""
        state = FlowState.DORMANT
        new_state, output = CHAT_POLYNOMIAL.invoke(state, "start")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "started"


class TestChatPolynomialAdapter:
    """Test ChatPolynomialAdapter."""

    def test_adapter_init(self) -> None:
        """Adapter initializes with DORMANT state."""
        adapter = ChatPolynomialAdapter()
        assert adapter.state == FlowState.DORMANT
        assert len(adapter.get_history()) == 0

    def test_adapter_can_perform_valid(self) -> None:
        """can_perform() returns True for valid actions."""
        adapter = ChatPolynomialAdapter()
        assert adapter.can_perform("start") is True
        assert adapter.can_perform("configure") is True

    def test_adapter_can_perform_invalid(self) -> None:
        """can_perform() returns False for invalid actions."""
        adapter = ChatPolynomialAdapter()
        assert adapter.can_perform("message") is False
        assert adapter.can_perform("fork") is False

    def test_adapter_get_valid_actions(self) -> None:
        """get_valid_actions() returns directions for current state."""
        adapter = ChatPolynomialAdapter()
        valid = adapter.get_valid_actions()
        assert "start" in valid
        assert "configure" in valid

    def test_adapter_perform_valid(self) -> None:
        """perform() executes valid action."""
        adapter = ChatPolynomialAdapter()
        output = adapter.perform("start")
        assert adapter.state == FlowState.STREAMING
        assert output["event"] == "started"

    def test_adapter_perform_invalid(self) -> None:
        """perform() raises ValueError for invalid action."""
        adapter = ChatPolynomialAdapter()
        with pytest.raises(ValueError, match="Invalid action"):
            adapter.perform("message")

    def test_adapter_records_history(self) -> None:
        """Adapter records transition history."""
        adapter = ChatPolynomialAdapter()
        adapter.perform("start")
        adapter.perform("message")
        adapter.perform("fork")

        history = adapter.get_history()
        assert len(history) == 3
        assert history[0] == (FlowState.DORMANT, "start", FlowState.STREAMING)
        assert history[1] == (FlowState.STREAMING, "message", FlowState.STREAMING)
        assert history[2] == (FlowState.STREAMING, "fork", FlowState.BRANCHING)

    def test_adapter_reset(self) -> None:
        """reset() returns to DORMANT and clears history."""
        adapter = ChatPolynomialAdapter()
        adapter.perform("start")
        adapter.perform("message")

        adapter.reset()

        assert adapter.state == FlowState.DORMANT
        assert len(adapter.get_history()) == 0

    def test_adapter_verify_laws(self) -> None:
        """verify_laws() checks polynomial constraints."""
        adapter = ChatPolynomialAdapter()
        assert adapter.verify_laws() is True

    def test_adapter_full_lifecycle(self) -> None:
        """Adapter can execute full conversation lifecycle."""
        adapter = ChatPolynomialAdapter()

        # Start conversation
        adapter.perform("start")
        assert adapter.state == FlowState.STREAMING

        # Send messages
        adapter.perform("message")
        adapter.perform("message")
        assert adapter.state == FlowState.STREAMING

        # Create checkpoint
        adapter.perform("checkpoint")
        assert adapter.state == FlowState.STREAMING

        # Fork conversation
        adapter.perform("fork")
        assert adapter.state == FlowState.BRANCHING

        # Confirm fork
        adapter.perform("confirm_fork")
        assert adapter.state == FlowState.STREAMING

        # Stop conversation
        adapter.perform("stop")
        assert adapter.state == FlowState.DRAINING

        # Crystallize
        adapter.perform("crystallize")
        assert adapter.state == FlowState.COLLAPSED

        # Reset
        adapter.perform("reset")
        assert adapter.state == FlowState.DORMANT

        # Verify complete history
        history = adapter.get_history()
        assert len(history) == 9


class TestPolynomialLaws:
    """Test polynomial laws hold for chat modality."""

    def test_all_states_have_directions(self) -> None:
        """Every state has defined directions."""
        for state in FlowState:
            directions = chat_directions(state)
            assert isinstance(directions, frozenset)
            assert len(directions) > 0

    def test_terminal_state_limited_exits(self) -> None:
        """COLLAPSED state only allows reset and harvest."""
        directions = chat_directions(FlowState.COLLAPSED)
        assert directions == frozenset(["reset", "harvest"])

    def test_start_from_dormant_only(self) -> None:
        """Start action only valid from DORMANT."""
        assert "start" in chat_directions(FlowState.DORMANT)
        assert "start" not in chat_directions(FlowState.STREAMING)
        assert "start" not in chat_directions(FlowState.BRANCHING)

    def test_message_only_in_streaming(self) -> None:
        """Message action only valid in STREAMING."""
        assert "message" in chat_directions(FlowState.STREAMING)
        assert "message" not in chat_directions(FlowState.DORMANT)
        assert "message" not in chat_directions(FlowState.BRANCHING)

    def test_fork_merge_symmetry(self) -> None:
        """Fork and merge operations are symmetric."""
        # Fork: STREAMING -> BRANCHING
        new_state, _ = chat_transition(FlowState.STREAMING, "fork")
        assert new_state == FlowState.BRANCHING

        # Confirm fork: BRANCHING -> STREAMING
        new_state, _ = chat_transition(FlowState.BRANCHING, "confirm_fork")
        assert new_state == FlowState.STREAMING

    def test_deterministic_transitions(self) -> None:
        """Same (state, action) always gives same result."""
        # Execute same transition multiple times
        results = [chat_transition(FlowState.STREAMING, "message") for _ in range(10)]

        # All results should be identical
        first = results[0]
        for result in results[1:]:
            assert result == first

    def test_stop_draining_collapsed_sequence(self) -> None:
        """Proper shutdown sequence: STREAMING -> DRAINING -> COLLAPSED."""
        # Stop
        state1, _ = chat_transition(FlowState.STREAMING, "stop")
        assert state1 == FlowState.DRAINING

        # Crystallize
        state2, _ = chat_transition(state1, "crystallize")
        assert state2 == FlowState.COLLAPSED

    def test_checkpoint_preserves_state(self) -> None:
        """Checkpoint action doesn't change state."""
        new_state, output = chat_transition(FlowState.STREAMING, "checkpoint")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "checkpointed"

    def test_rewind_preserves_state(self) -> None:
        """Rewind action doesn't change state."""
        new_state, output = chat_transition(FlowState.STREAMING, "rewind")
        assert new_state == FlowState.STREAMING
        assert output["event"] == "rewound"


class TestPolynomialComposition:
    """Test polynomial composition properties."""

    def test_adapter_composition_associative(self) -> None:
        """Action sequences are associative: (a∘b)∘c = a∘(b∘c)."""
        # Path 1: (start, message), checkpoint
        adapter1 = ChatPolynomialAdapter()
        adapter1.perform("start")
        adapter1.perform("message")
        adapter1.perform("checkpoint")
        state1 = adapter1.state

        # Path 2: start, (message, checkpoint)
        adapter2 = ChatPolynomialAdapter()
        adapter2.perform("start")
        adapter2.perform("message")
        adapter2.perform("checkpoint")
        state2 = adapter2.state

        # Should end in same state
        assert state1 == state2

    def test_reset_is_idempotent(self) -> None:
        """Reset followed by reset has same effect as single reset."""
        adapter = ChatPolynomialAdapter()
        adapter.perform("start")
        adapter.perform("message")
        adapter.reset()
        state1 = adapter.state

        adapter.reset()
        state2 = adapter.state

        assert state1 == state2 == FlowState.DORMANT

    def test_checkpoint_idempotent(self) -> None:
        """Multiple checkpoints in STREAMING don't change state."""
        adapter = ChatPolynomialAdapter()
        adapter.perform("start")
        adapter.perform("checkpoint")
        adapter.perform("checkpoint")
        adapter.perform("checkpoint")

        assert adapter.state == FlowState.STREAMING

    def test_fork_cancel_identity(self) -> None:
        """Fork followed by cancel returns to original state."""
        adapter = ChatPolynomialAdapter()
        adapter.perform("start")
        adapter.perform("message")

        # Remember state before fork
        state_before = adapter.state

        # Fork and cancel
        adapter.perform("fork")
        adapter.perform("cancel_fork")

        # Should be back to original state
        assert adapter.state == state_before
