"""
ChatOperad: Formal Composition Grammar for Chat.

Auto-generated from: spec/self/chat.md
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function

# =============================================================================
# Operations
# =============================================================================


def _listen_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a listen operation.

    Input → Understanding
    """

    def listen_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "listen",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"listen({agent_a.name})", listen_fn)


def _think_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a think operation.

    Understanding → Thoughts
    """

    def think_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "think",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"think({agent_a.name})", think_fn)


def _respond_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a respond operation.

    Thoughts → Response
    """

    def respond_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "respond",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"respond({agent_a.name})", respond_fn)


def _reflect_compose(
    agent_a: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a reflect operation.

    Exchange → Learnings
    """

    def reflect_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "reflect",
            "participants": [agent_a.name],
            "input": input,
        }

    return from_function(f"reflect({agent_a.name})", reflect_fn)


def _branch_compose(
    agent_a: PolyAgent[Any, Any, Any],
    agent_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a branch operation.

    Context × Options → Choice
    """

    def branch_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "branch",
            "participants": [agent_a.name, agent_b.name],
            "input": input,
        }

    return from_function(f"branch({agent_a.name, agent_b.name})", branch_fn)


# =============================================================================
# Laws
# =============================================================================


def _verify_turn_taking(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: listen before respond

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="turn_taking",
        status=LawStatus.PASSED,
        message="turn_taking verification pending implementation",
    )


def _verify_coherence(
    *agents: PolyAgent[Any, Any, Any],
    context: Any = None,
) -> LawVerification:
    """
    Verify: respond(t) relates to listen(i)

    TODO: Implement actual verification logic.
    """
    return LawVerification(
        law_name="coherence",
        status=LawStatus.PASSED,
        message="coherence verification pending implementation",
    )


# =============================================================================
# Operad Creation
# =============================================================================


def create_chat_operad() -> Operad:
    """
    Create the Chat Operad.

    Extends AGENT_OPERAD with chat-specific operations.
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add chat-specific operations
    ops["listen"] = Operation(
        name="listen",
        arity=1,
        signature="Input → Understanding",
        compose=_listen_compose,
        description="Listen to input",
    )
    ops["think"] = Operation(
        name="think",
        arity=1,
        signature="Understanding → Thoughts",
        compose=_think_compose,
        description="Process understanding",
    )
    ops["respond"] = Operation(
        name="respond",
        arity=1,
        signature="Thoughts → Response",
        compose=_respond_compose,
        description="Generate response",
    )
    ops["reflect"] = Operation(
        name="reflect",
        arity=1,
        signature="Exchange → Learnings",
        compose=_reflect_compose,
        description="Reflect on exchange",
    )
    ops["branch"] = Operation(
        name="branch",
        arity=2,
        signature="Context × Options → Choice",
        compose=_branch_compose,
        description="Branch conversation",
    )

    # Inherit universal laws and add chat-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="turn_taking",
            equation="listen before respond",
            verify=_verify_turn_taking,
            description="Respect turn order",
        ),
        Law(
            name="coherence",
            equation="respond(t) relates to listen(i)",
            verify=_verify_coherence,
            description="Responses are coherent",
        ),
    ]

    return Operad(
        name="ChatOperad",
        operations=ops,
        laws=laws,
        description="Composition grammar for Chat",
    )


# =============================================================================
# Global Operad Instance
# =============================================================================


CHAT_OPERAD = create_chat_operad()
"""
The Chat Operad.

Operations: 5
Laws: 2
Generated from: spec/self/chat.md
"""

# Register with the operad registry
OperadRegistry.register(CHAT_OPERAD)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "CHAT_OPERAD",
    "create_chat_operad",
]
