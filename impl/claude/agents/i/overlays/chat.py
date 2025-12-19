"""
Agent-Human Q&A Chat Panel - Ask agents about their reasoning.

The chat panel enables direct communication with agents about their
decisions, enabling users to ask "Why did you do X?" and receive
explanations grounded in the agent's actual turn history.

Features:
- Natural language questions
- Responses reference actual turns
- Clickable links to navigate to turns
- Chat history persists in session
- Suggested questions based on context

Usage:
    # In Cockpit:
    panel = AgentChatPanel(agent_id="A-gent")
    response = await panel.ask("Why did you choose this approach?")

Keybindings:
    ?       - Open chat from Cockpit
    Enter   - Send question
    Esc     - Close chat
    Ctrl+L  - Clear history
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Input, Static

if TYPE_CHECKING:
    pass


class MessageRole(Enum):
    """Role of the message sender."""

    USER = auto()
    AGENT = auto()
    SYSTEM = auto()


@dataclass
class ChatMessage:
    """A single message in the chat."""

    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    turn_refs: list[str] = field(default_factory=list)  # Referenced turn IDs

    def format_for_display(self) -> str:
        """Format message for display with role indicator."""
        time_str = self.timestamp.strftime("%H:%M")
        role_prefix = {
            MessageRole.USER: "[#8ac4e8]You[/]",
            MessageRole.AGENT: "[#7bc275]Agent[/]",
            MessageRole.SYSTEM: "[#6a6560]System[/]",
        }
        return f"[{time_str}] {role_prefix[self.role]}: {self.content}"


@dataclass
class ExplanationContext:
    """Context gathered for generating explanations."""

    recent_turns: list[dict[str, Any]]  # Recent turn data
    causal_cone: list[str]  # Turn IDs in causal cone
    current_state: dict[str, Any]  # Current agent state
    focus_turn_id: str | None = None  # Turn being asked about


class AgentChatPanel(ModalScreen[None]):
    """
    Modal chat panel for asking agents about their behavior.

    Opens as an overlay from the Cockpit view. Users can ask
    natural language questions and receive explanations that
    reference the agent's actual turn history.
    """

    CSS = """
    AgentChatPanel {
        align: center middle;
    }

    AgentChatPanel #chat-container {
        width: 80;
        height: 30;
        background: #252525;
        border: solid #4a4a5c;
        padding: 1;
    }

    AgentChatPanel #chat-header {
        height: 2;
        background: #2a2a2a;
        color: #f5f0e6;
        text-style: bold;
        padding: 0 1;
        border-bottom: solid #4a4a5c;
    }

    AgentChatPanel #messages-area {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }

    AgentChatPanel .message {
        margin-bottom: 1;
    }

    AgentChatPanel .message-user {
        color: #8ac4e8;
    }

    AgentChatPanel .message-agent {
        color: #7bc275;
    }

    AgentChatPanel .message-system {
        color: #6a6560;
    }

    AgentChatPanel #input-area {
        height: 3;
        dock: bottom;
        padding: 1;
        border-top: solid #4a4a5c;
    }

    AgentChatPanel #question-input {
        width: 100%;
    }

    AgentChatPanel #suggestions-area {
        height: 4;
        padding: 0 1;
        color: #6a6560;
    }

    AgentChatPanel .turn-link {
        color: #e6a352;
        text-style: underline;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("ctrl+l", "clear", "Clear", show=True),
    ]

    # Reactive properties
    agent_name: reactive[str] = reactive("")

    def __init__(
        self,
        agent_id: str,
        agent_name: str = "",
        on_turn_link_click: Callable[[str], None] | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the chat panel.

        Args:
            agent_id: ID of the agent to chat with
            agent_name: Display name of the agent
            on_turn_link_click: Callback when user clicks a turn link
        """
        super().__init__(name=name, id=id, classes=classes)
        self.agent_id = agent_id
        self.agent_name = agent_name or agent_id
        self._on_turn_link_click = on_turn_link_click
        self._messages: list[ChatMessage] = []
        self._explanation_context: ExplanationContext | None = None

        # Add welcome message
        self._add_system_message(
            f"Chat with {self.agent_name}. Ask about decisions, actions, or state."
        )

    def compose(self) -> ComposeResult:
        """Compose the chat panel."""
        with Container(id="chat-container"):
            yield Static(
                f"[bold]Chat with {self.agent_name}[/]  │  Ask about reasoning and decisions",
                id="chat-header",
            )

            # Suggestions area
            yield Static(
                "[dim]Try: 'Why did you...?' │ 'What was your reasoning?' │ "
                "'Explain the last action'[/]",
                id="suggestions-area",
            )

            # Messages area
            with Vertical(id="messages-area"):
                for msg in self._messages:
                    yield self._render_message(msg)

            # Input area
            with Container(id="input-area"):
                yield Input(
                    placeholder="Ask a question about the agent's behavior...",
                    id="question-input",
                )

        yield Footer()

    def _render_message(self, msg: ChatMessage) -> Static:
        """Render a single message."""
        css_class = {
            MessageRole.USER: "message message-user",
            MessageRole.AGENT: "message message-agent",
            MessageRole.SYSTEM: "message message-system",
        }[msg.role]

        content = msg.format_for_display()

        # Add turn links if present
        if msg.turn_refs:
            refs = " ".join(f"[[{ref}]]" for ref in msg.turn_refs[:3])
            content += f"\n  [#e6a352]Referenced turns: {refs}[/]"

        return Static(content, classes=css_class)

    def _add_message(
        self, role: MessageRole, content: str, turn_refs: list[str] | None = None
    ) -> None:
        """Add a message to the chat."""
        msg = ChatMessage(
            role=role,
            content=content,
            turn_refs=turn_refs or [],
        )
        self._messages.append(msg)
        self._refresh_messages()

    def _add_system_message(self, content: str) -> None:
        """Add a system message."""
        self._add_message(MessageRole.SYSTEM, content)

    def _add_user_message(self, content: str) -> None:
        """Add a user message."""
        self._add_message(MessageRole.USER, content)

    def _add_agent_message(self, content: str, turn_refs: list[str] | None = None) -> None:
        """Add an agent message."""
        self._add_message(MessageRole.AGENT, content, turn_refs)

    def _refresh_messages(self) -> None:
        """Refresh the messages display."""
        # Skip if not mounted yet (messages will be rendered in compose())
        if not self.is_mounted:
            return

        try:
            messages_area = self.query_one("#messages-area", Vertical)
            messages_area.remove_children()
            for msg in self._messages:
                messages_area.mount(self._render_message(msg))
            # Scroll to bottom
            messages_area.scroll_end()
        except Exception:
            # Widget not ready yet
            pass

    async def ask(self, question: str) -> str:
        """
        Ask the agent a question about its behavior.

        Args:
            question: Natural language question

        Returns:
            Agent's response
        """
        # Add user message
        self._add_user_message(question)

        # Build explanation context
        context = await self._build_explanation_context()

        # Generate response (mock for now - in production, this would call the agent)
        response, turn_refs = await self._generate_response(question, context)

        # Add agent response
        self._add_agent_message(response, turn_refs)

        return response

    async def _build_explanation_context(self) -> ExplanationContext:
        """
        Build context for generating explanations.

        Gathers relevant turns and state information.
        """
        # In production, this would query the actual agent/weave
        return ExplanationContext(
            recent_turns=[
                {"id": "turn-001", "type": "ACTION", "content": "Searched database"},
                {"id": "turn-002", "type": "THOUGHT", "content": "Considering options"},
                {"id": "turn-003", "type": "SPEECH", "content": "Found 3 results"},
            ],
            causal_cone=["turn-001", "turn-002", "turn-003"],
            current_state={"mode": "DELIBERATING", "confidence": 0.85},
        )

    async def _generate_response(
        self,
        question: str,
        context: ExplanationContext,
    ) -> tuple[str, list[str]]:
        """
        Generate a response to the user's question.

        In production, this would use the agent's model to generate
        an explanation grounded in the turn history.

        Args:
            question: User's question
            context: Explanation context

        Returns:
            Tuple of (response text, referenced turn IDs)
        """
        # Analyze question type
        question_lower = question.lower()

        if "why" in question_lower:
            response = (
                "I chose this approach because my analysis (turn-002) indicated "
                "it would be most effective. The database search (turn-001) provided "
                "the necessary context for this decision."
            )
            refs = ["turn-001", "turn-002"]

        elif "what" in question_lower and "reasoning" in question_lower:
            response = (
                f"My reasoning process involved: 1) Gathering context via search, "
                f"2) Evaluating the results, 3) Formulating a response. "
                f"Current confidence: {context.current_state.get('confidence', 0.5):.0%}"
            )
            refs = ["turn-001", "turn-002", "turn-003"]

        elif "explain" in question_lower:
            recent = context.recent_turns[-1] if context.recent_turns else {}
            response = (
                f"The last action was: {recent.get('content', 'unknown')}. "
                f"This was a {recent.get('type', 'ACTION')} turn aimed at "
                f"progressing toward the goal."
            )
            refs = [recent.get("id", "turn-003")] if recent else []

        elif "state" in question_lower or "mode" in question_lower:
            response = (
                f"Currently in {context.current_state.get('mode', 'UNKNOWN')} mode "
                f"with {context.current_state.get('confidence', 0.5):.0%} confidence. "
                f"Ready to proceed with next action."
            )
            refs = []

        else:
            response = (
                "I can explain my reasoning, decisions, or current state. "
                "Try asking 'Why did you...?', 'What was your reasoning?', "
                "or 'Explain the last action'."
            )
            refs = []

        return response, refs

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle question submission."""
        question = event.value.strip()
        if question:
            # Clear input
            event.input.value = ""
            # Process question
            self.run_worker(self.ask(question))

    def action_close(self) -> None:
        """Close the chat panel."""
        self.dismiss()

    def action_clear(self) -> None:
        """Clear chat history."""
        self._messages = []
        self._add_system_message(
            f"Chat with {self.agent_name}. Ask about decisions, actions, or state."
        )
        self._refresh_messages()

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def get_messages(self) -> list[ChatMessage]:
        """Get all chat messages."""
        return self._messages.copy()

    def set_context(self, context: ExplanationContext) -> None:
        """Set the explanation context."""
        self._explanation_context = context

    def suggest_questions(self, turn_id: str | None = None) -> list[str]:
        """
        Get suggested questions based on context.

        Args:
            turn_id: Optional specific turn to ask about

        Returns:
            List of suggested questions
        """
        suggestions = [
            "Why did you choose this approach?",
            "What was your reasoning process?",
            "Explain the last action",
            "What is your current state?",
        ]

        if turn_id:
            suggestions.insert(0, f"Explain turn {turn_id}")

        return suggestions


__all__ = [
    "AgentChatPanel",
    "ChatMessage",
    "MessageRole",
    "ExplanationContext",
]
