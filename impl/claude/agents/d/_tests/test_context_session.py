"""
Tests for Context Protocol components: PromptBuilder, ComponentRenderer, ContextSession.

These tests verify the Context Protocol spec implementation:
- PromptBuilder assembles prompts with eigenvector injection
- ComponentRenderer produces React-ready props
- ContextSession manages polynomial state transitions
"""

from __future__ import annotations

import pytest
from agents.d.component_renderer import (
    ComponentRenderer,
    ContextProps,
    ContextStatus,
    MessageProps,
    create_component_renderer,
    render_for_frontend,
    render_minimal,
)
from agents.d.context_session import (
    ContextInput,
    ContextOutput,
    ContextSession,
    ContextState,
    create_context_session,
    from_messages,
)
from agents.d.context_window import (
    ContextWindow,
    TurnRole,
    create_context_window,
)
from agents.d.linearity import ResourceClass
from agents.d.prompt_builder import (
    PromptBuilder,
    build_builder_prompt,
    build_citizen_prompt,
    build_kgent_prompt,
    create_prompt_builder,
    render_eigenvectors_6d,
    render_eigenvectors_7d,
)

# =============================================================================
# PromptBuilder Tests
# =============================================================================


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_create_prompt_builder(self) -> None:
        """Test factory function."""
        builder = create_prompt_builder()
        assert builder is not None
        assert "kgent" in builder.system_templates
        assert "builder" in builder.system_templates
        assert "citizen" in builder.system_templates

    def test_build_kgent_prompt_basic(self) -> None:
        """Test K-gent prompt without eigenvectors."""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("kgent")
        assert "K-gent" in prompt
        assert "Kent's AI persona" in prompt

    def test_build_kgent_prompt_with_eigenvectors(self) -> None:
        """Test K-gent prompt with eigenvectors."""
        eigenvectors = {
            "aesthetic": 0.15,
            "categorical": 0.92,
            "gratitude": 0.78,
            "heterarchy": 0.88,
            "generativity": 0.90,
            "joy": 0.75,
        }
        prompt = build_kgent_prompt(eigenvectors)
        assert "Personality Coordinates" in prompt
        assert "Aesthetic" in prompt
        assert "minimalist" in prompt.lower()  # value 0.15 → strongly minimalist

    def test_build_kgent_prompt_with_constraints(self) -> None:
        """Test K-gent prompt with constraints."""
        constraints = ["Be concise", "No emojis"]
        prompt = build_kgent_prompt({}, constraints)
        assert "Constraints" in prompt
        assert "Be concise" in prompt
        assert "No emojis" in prompt

    def test_build_builder_prompt(self) -> None:
        """Test Builder prompt with specialty."""
        eigenvectors = {"warmth": 0.7, "creativity": 0.9}
        prompt = build_builder_prompt(eigenvectors, specialty="Scout")
        assert "Builder" in prompt
        assert "Scout" in prompt
        assert "Personality Coordinates" in prompt

    def test_build_citizen_prompt(self) -> None:
        """Test Citizen prompt with name."""
        eigenvectors = {"warmth": 0.8, "trust": 0.6}
        prompt = build_citizen_prompt(eigenvectors, name="Alice")
        assert "Citizen" in prompt
        assert "Alice" in prompt

    def test_render_eigenvectors_6d(self) -> None:
        """Test 6D eigenvector rendering."""
        eigenvectors = {"aesthetic": 0.15, "joy": 0.75}
        rendered = render_eigenvectors_6d(eigenvectors)
        assert "Aesthetic" in rendered
        assert "Joy" in rendered
        assert "minimalist" in rendered.lower()  # 0.15 → minimalist
        assert "playful" in rendered.lower()  # 0.75 → playful

    def test_render_eigenvectors_7d(self) -> None:
        """Test 7D eigenvector rendering."""
        eigenvectors = {"warmth": 0.8, "curiosity": 0.3}
        rendered = render_eigenvectors_7d(eigenvectors)
        assert "Warmth" in rendered
        assert "Curiosity" in rendered
        assert "warm" in rendered.lower()  # 0.8 → warm
        assert "incurious" in rendered.lower()  # 0.3 → incurious

    def test_custom_template(self) -> None:
        """Test adding custom template."""
        builder = PromptBuilder()
        builder.add_template("custom", "Custom template: {persona}")
        prompt = builder.build_system_prompt("custom")
        assert "Custom template:" in prompt

    def test_default_template_fallback(self) -> None:
        """Test fallback to default template."""
        builder = PromptBuilder()
        prompt = builder.build_system_prompt("unknown_type")
        assert "AI assistant" in prompt


# =============================================================================
# ComponentRenderer Tests
# =============================================================================


class TestComponentRenderer:
    """Tests for ComponentRenderer."""

    def test_create_renderer(self) -> None:
        """Test factory function."""
        renderer = create_component_renderer()
        assert renderer is not None
        assert renderer.hide_system_messages is True

    def test_render_empty_window(self) -> None:
        """Test rendering empty context."""
        renderer = ComponentRenderer()
        window = ContextWindow()
        props = renderer.render_chat(window)
        assert props.messages == []
        assert props.pressure == 0.0
        assert props.status == ContextStatus.READY
        assert props.can_send is True

    def test_render_with_messages(self) -> None:
        """Test rendering context with messages."""
        renderer = ComponentRenderer()
        window = ContextWindow()
        window.append(TurnRole.USER, "Hello!")
        window.append(TurnRole.ASSISTANT, "Hi there!")

        props = renderer.render_chat(window)
        assert len(props.messages) == 2
        assert props.messages[0].role == "user"
        assert props.messages[0].content == "Hello!"
        assert props.messages[1].role == "assistant"
        assert props.messages[1].content == "Hi there!"

    def test_hide_system_messages(self) -> None:
        """Test that system messages are hidden by default."""
        renderer = ComponentRenderer(hide_system_messages=True)
        window = ContextWindow()
        window.append(TurnRole.SYSTEM, "System prompt")
        window.append(TurnRole.USER, "Hello!")

        props = renderer.render_chat(window)
        assert len(props.messages) == 1
        assert props.messages[0].role == "user"

    def test_show_system_messages(self) -> None:
        """Test showing system messages."""
        renderer = ComponentRenderer(hide_system_messages=False)
        window = ContextWindow()
        window.append(TurnRole.SYSTEM, "System prompt")
        window.append(TurnRole.USER, "Hello!")

        props = renderer.render_chat(window)
        assert len(props.messages) == 2
        assert props.messages[0].role == "system"

    def test_truncate_long_content(self) -> None:
        """Test content truncation."""
        renderer = ComponentRenderer(max_content_length=10)
        window = ContextWindow()
        window.append(
            TurnRole.USER, "This is a very long message that exceeds the limit"
        )

        props = renderer.render_chat(window)
        assert props.messages[0].content == "This is a ..."

    def test_status_override(self) -> None:
        """Test status override."""
        renderer = ComponentRenderer()
        window = ContextWindow()
        window.append(TurnRole.USER, "Hello")

        props = renderer.render_chat(window, status_override=ContextStatus.THINKING)
        assert props.status == ContextStatus.THINKING
        assert props.can_send is False

    def test_render_for_frontend_function(self) -> None:
        """Test convenience function."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Test")

        result = render_for_frontend(window)
        assert "messages" in result
        assert "pressure" in result
        assert "status" in result
        assert "canSend" in result

    def test_render_minimal(self) -> None:
        """Test minimal rendering."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Test")

        result = render_minimal(window)
        assert "messages" in result
        assert "pressure" in result
        assert "status" not in result

    def test_to_dict_serialization(self) -> None:
        """Test props serialization."""
        renderer = ComponentRenderer()
        window = ContextWindow()
        window.append(TurnRole.USER, "Test")

        props = renderer.render_chat(window)
        data = props.to_dict()

        assert isinstance(data, dict)
        assert "messages" in data
        assert "pressure" in data
        assert "canSend" in data  # camelCase for JS


# =============================================================================
# ContextSession Tests
# =============================================================================


class TestContextSession:
    """Tests for ContextSession polynomial state machine."""

    def test_create_session(self) -> None:
        """Test session creation."""
        session = ContextSession()
        assert session.state == ContextState.EMPTY
        assert session.pressure == 0.0

    def test_create_session_with_system(self) -> None:
        """Test session creation with initial system message."""
        session = create_context_session(initial_system="You are helpful.")
        assert session.state == ContextState.ACCUMULATING
        assert len(session.window) == 1

    def test_add_user_turn_transitions_state(self) -> None:
        """Test that adding user turn transitions from EMPTY to ACCUMULATING."""
        session = ContextSession()
        assert session.state == ContextState.EMPTY

        output = session.add_user_turn("Hello!")
        assert output.success
        assert session.state == ContextState.ACCUMULATING  # type: ignore[comparison-overlap]
        assert output.turn is not None
        assert output.turn.content == "Hello!"

    def test_add_assistant_turn(self) -> None:
        """Test adding assistant turn."""
        session = ContextSession()
        session.add_user_turn("Hello!")

        output = session.add_assistant_turn("Hi there!")
        assert output.success
        assert output.turn is not None
        assert output.turn.role == TurnRole.ASSISTANT

    def test_add_system_message(self) -> None:
        """Test adding system message."""
        session = ContextSession()
        output = session.add_system_message("Be helpful.")

        assert output.success
        assert output.turn is not None  # For mypy
        # System messages should be REQUIRED by default
        rc = session.window.get_resource_class(output.turn)
        assert rc == ResourceClass.REQUIRED

    def test_clear_resets_state(self) -> None:
        """Test that clear returns to EMPTY state."""
        session = ContextSession()
        session.add_user_turn("Hello")
        session.add_assistant_turn("Hi")
        assert session.state == ContextState.ACCUMULATING

        output = session.clear()
        assert output.success
        assert session.state == ContextState.EMPTY  # type: ignore[comparison-overlap]
        assert len(session.window) == 0

    @pytest.mark.asyncio
    async def test_compress(self) -> None:
        """Test compression."""
        session = ContextSession(max_tokens=100)
        # Add many turns to trigger pressure
        for i in range(20):
            session.add_user_turn(f"Message {i} " * 10)
            session.add_assistant_turn(f"Response {i} " * 10)

        original_tokens = session.window.total_tokens
        output = await session.compress(target_pressure=0.3)

        assert output.compressed
        assert session.state == ContextState.COMPRESSED
        assert session.window.total_tokens < original_tokens

    def test_build_prompt(self) -> None:
        """Test prompt building."""
        session = ContextSession()
        session.add_user_turn("Hello")

        prompt = session.build_prompt(
            agent_type="kgent",
            eigenvectors={"aesthetic": 0.15},
        )
        assert "K-gent" in prompt
        assert "Aesthetic" in prompt

    def test_render(self) -> None:
        """Test rendering for frontend."""
        session = ContextSession()
        session.add_user_turn("Hello!")
        session.add_assistant_turn("Hi!")

        props = session.render()
        assert len(props.messages) == 2
        assert props.status == ContextStatus.READY
        assert props.can_send is True

    def test_get_messages_for_llm(self) -> None:
        """Test getting messages for LLM API."""
        session = ContextSession()
        session.add_user_turn("Hello!")
        session.add_assistant_turn("Hi!")

        messages = session.get_messages_for_llm()
        assert len(messages) == 2
        assert messages[0] == {"role": "user", "content": "Hello!"}
        assert messages[1] == {"role": "assistant", "content": "Hi!"}

    def test_serialization(self) -> None:
        """Test session serialization."""
        session = ContextSession()
        session.add_user_turn("Hello!")
        session.add_assistant_turn("Hi!")

        data = session.to_dict()
        restored = ContextSession.from_dict(data)

        assert restored.state == session.state
        assert len(restored.window) == len(session.window)

    def test_from_messages_factory(self) -> None:
        """Test creating session from message list."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
        ]
        session = from_messages(messages)

        assert len(session.window) == 3
        assert session.state == ContextState.ACCUMULATING


# =============================================================================
# State Machine Polynomial Tests
# =============================================================================


class TestContextPolynomial:
    """Tests for polynomial state transitions."""

    def test_valid_transitions_from_empty(self) -> None:
        """Test valid inputs for EMPTY state."""
        session = ContextSession()
        assert session.state == ContextState.EMPTY

        # user_turn is valid from EMPTY
        output = session.add_user_turn("Hello")
        assert output.success

        # Reset
        session.clear()

        # system is valid from EMPTY
        output = session.add_system_message("System")
        assert output.success

    def test_invalid_assistant_from_empty(self) -> None:
        """Test that assistant turn is invalid from EMPTY (no error, but check logic)."""
        session = ContextSession()
        # Actually, our implementation allows assistant_turn from EMPTY
        # because VALID_DIRECTIONS[EMPTY] = {"user_turn", "system"}
        output = session.add_assistant_turn("Hello")
        assert not output.success
        assert output.error is not None and "Invalid input" in output.error

    def test_all_inputs_valid_from_accumulating(self) -> None:
        """Test that all turn types are valid from ACCUMULATING."""
        session = ContextSession()
        session.add_user_turn("Start")
        assert session.state == ContextState.ACCUMULATING

        output = session.add_assistant_turn("Response")
        assert output.success

        output = session.add_user_turn("Another")
        assert output.success

        output = session.add_system_message("System")
        assert output.success


# =============================================================================
# Integration Tests
# =============================================================================


class TestContextProtocolIntegration:
    """Integration tests for the full Context Protocol."""

    def test_full_dialogue_flow(self) -> None:
        """Test complete dialogue flow with prompt building and rendering."""
        # Create session with system prompt
        session = create_context_session(
            initial_system="You are K-gent, Kent's AI persona."
        )

        # Simulate dialogue
        session.add_user_turn("What can you help me with?")

        # Build prompt for LLM (backend only)
        prompt = session.build_prompt(
            agent_type="kgent",
            eigenvectors={"aesthetic": 0.15, "joy": 0.75},
            constraints=["Be concise"],
        )
        assert "K-gent" in prompt
        assert "Aesthetic" in prompt
        assert "concise" in prompt

        # Add simulated response
        session.add_assistant_turn("I can help with software engineering tasks.")

        # Render for frontend
        props = session.render()
        # System message hidden by default
        assert len(props.messages) == 2
        assert props.messages[0].role == "user"
        assert props.messages[1].role == "assistant"
        assert props.can_send is True

    def test_builder_workshop_flow(self) -> None:
        """Test Builder workshop dialogue flow."""
        session = ContextSession()
        session.add_system_message("You are a Scout builder. Explore possibilities.")

        session.add_user_turn("Let's design a new feature.")

        prompt = session.build_prompt(
            agent_type="builder",
            eigenvectors={"warmth": 0.7, "creativity": 0.9},
            specialty="Scout",
        )
        assert "Builder" in prompt
        assert "Scout" in prompt
        assert "creativity" in prompt.lower()

        session.add_assistant_turn("Great! Let me explore some options...")

        props = session.render()
        assert len(props.messages) == 2  # system hidden

    def test_props_json_serializable(self) -> None:
        """Test that props can be JSON serialized."""
        import json

        session = ContextSession()
        session.add_user_turn("Test message")
        session.add_assistant_turn("Test response")

        props = session.render()
        data = props.to_dict()

        # Should not raise
        json_str = json.dumps(data)
        assert "messages" in json_str
        assert "pressure" in json_str
