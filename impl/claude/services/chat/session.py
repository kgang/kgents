"""
Chat Session: K-Block Semantics for Conversation Management.

Implements ChatSession with fork/merge/checkpoint/rewind operations.
Uses HARNESS_OPERAD laws for branching algebra.
Integrates FlowPolynomial for state management.

Philosophy:
    "The session is a K-Block. Branch, merge, rewind with algebraic laws."

See: spec/protocols/chat-web.md §1.2, §2.2
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar
from uuid import uuid4

from agents.f.polynomial import CHAT_POLYNOMIAL, FlowPolynomial
from agents.f.state import FlowState

from .context import Turn, WorkingContext
from .evidence import ChatEvidence, TurnResult
from .reward import PrincipleScore, constitutional_reward
from .witness import ChatMark, ChatPolicyTrace


def generate_session_id() -> str:
    """Generate unique session ID."""
    return f"session-{uuid4().hex[:12]}"


# =============================================================================
# Enums
# =============================================================================


class ChatState(Enum):
    """
    Chat state machine states (DEPRECATED: Use FlowState).

    This enum is kept for backward compatibility.
    Maps to FlowState with additional metadata flags.

    See: spec/protocols/chat-web.md §2.1
    """

    IDLE = "idle"  # → STREAMING (or DORMANT before first message)
    PROCESSING = "processing"  # → STREAMING (with metadata flag)
    AWAITING_TOOL = "awaiting_tool"  # → STREAMING (with is_awaiting_tool flag)
    BRANCHING = "branching"  # → BRANCHING
    COMPRESSING = "compressing"  # → STREAMING (with is_compressing flag)

    def to_flow_state(self) -> FlowState:
        """Convert ChatState to FlowState."""
        mapping = {
            ChatState.IDLE: FlowState.STREAMING,
            ChatState.PROCESSING: FlowState.STREAMING,
            ChatState.AWAITING_TOOL: FlowState.STREAMING,
            ChatState.BRANCHING: FlowState.BRANCHING,
            ChatState.COMPRESSING: FlowState.STREAMING,
        }
        return mapping[self]


class MergeStrategy(Enum):
    """
    Merge strategies for branch operations.

    See: spec/protocols/chat-web.md §4.4
    """

    SEQUENTIAL = "sequential"  # Append branch turns after main
    INTERLEAVE = "interleave"  # Merge by timestamp
    MANUAL = "manual"  # User selects turns


class BranchError(Exception):
    """Branch operation error."""

    pass


class InvalidAction(Exception):
    """Invalid action for current state."""

    pass


# =============================================================================
# SessionNode: Branch Metadata
# =============================================================================


@dataclass
class SessionNode:
    """
    Session node metadata for branching.

    See: spec/protocols/chat-web.md §4.1
    """

    # Identity
    id: str = field(default_factory=generate_session_id)

    # Branch metadata
    parent_id: str | None = None  # Fork source
    fork_point: int | None = None  # Turn number where fork occurred
    branch_name: str = "main"  # User-assigned label

    # State
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    turn_count: int = 0

    # Merge state
    is_merged: bool = False
    merged_into: str | None = None

    # Evidence
    evidence: ChatEvidence = field(default_factory=ChatEvidence)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "fork_point": self.fork_point,
            "branch_name": self.branch_name,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "turn_count": self.turn_count,
            "is_merged": self.is_merged,
            "merged_into": self.merged_into,
            "evidence": self.evidence.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionNode:
        """Create from dictionary."""
        return cls(
            id=data.get("id", generate_session_id()),
            parent_id=data.get("parent_id"),
            fork_point=data.get("fork_point"),
            branch_name=data.get("branch_name", "main"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            last_active=datetime.fromisoformat(data["last_active"])
            if data.get("last_active")
            else datetime.now(),
            turn_count=data.get("turn_count", 0),
            is_merged=data.get("is_merged", False),
            merged_into=data.get("merged_into"),
            evidence=ChatEvidence.from_dict(data["evidence"])
            if data.get("evidence")
            else ChatEvidence(),
        )


# =============================================================================
# ChatSession: K-Block-Based Conversation
# =============================================================================


@dataclass
class ChatSession:
    """
    Chat session with K-Block operations.

    Implements ChatKBlock pattern with fork/merge/checkpoint/rewind.
    Uses FlowPolynomial for state machine validation.

    Laws (HARNESS_OPERAD):
        merge(fork(s)) ≡ s                              # Fork-merge identity
        merge(merge(a, b), c) ≡ merge(a, merge(b, c))   # Merge associativity
        rewind(checkpoint(s)) ≡ s                       # Checkpoint identity

    See: spec/protocols/chat-web.md §1.2, §2.2
    """

    # Polynomial functor for state management
    polynomial: ClassVar[FlowPolynomial] = CHAT_POLYNOMIAL

    # Identity
    id: str = field(default_factory=generate_session_id)
    node: SessionNode = field(default_factory=SessionNode)

    # State (using FlowState now)
    _flow_state: FlowState = FlowState.DORMANT
    _awaiting_tool: bool = False
    _compressing: bool = False

    # Backward compatibility
    state: ChatState = ChatState.IDLE

    # Context
    context: WorkingContext = field(default_factory=WorkingContext)

    # Evidence
    evidence: ChatEvidence = field(default_factory=ChatEvidence)

    # PolicyTrace for witnessing turns
    policy_trace: ChatPolicyTrace = field(
        default_factory=lambda: ChatPolicyTrace(session_id="")
    )

    # Checkpoints
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    # Project association
    project_id: str | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def turns(self) -> list[Turn]:
        """Active turns in context."""
        return self.context.turns

    @property
    def turn_count(self) -> int:
        """Number of turns."""
        return len(self.turns)

    @property
    def context_size(self) -> int:
        """Current context size in tokens."""
        return self.context.token_count

    @property
    def flow_state(self) -> FlowState:
        """Get current FlowState."""
        return self._flow_state

    @property
    def awaiting_tool(self) -> bool:
        """Check if session is awaiting tool execution."""
        return self._awaiting_tool

    @property
    def is_compressing(self) -> bool:
        """Check if session is compressing context."""
        return self._compressing

    def _validate_action(self, action: str) -> None:
        """
        Validate action is allowed in current state.

        Args:
            action: Action to validate

        Raises:
            InvalidAction: If action is not valid in current state
        """
        valid = self.polynomial.directions(self._flow_state)
        if action not in valid:
            raise InvalidAction(
                f"Action '{action}' not valid in state {self._flow_state}. "
                f"Valid actions: {', '.join(sorted(valid))}"
            )

    def _transition(self, action: str) -> dict[str, Any]:
        """
        Execute state transition with validation.

        Args:
            action: Action to execute

        Returns:
            Output dict from transition

        Raises:
            InvalidAction: If action is not valid
        """
        self._validate_action(action)
        new_state, output = self.polynomial.transition(self._flow_state, action)
        self._flow_state = new_state

        # Update backward-compatible state
        if new_state == FlowState.STREAMING:
            if self._awaiting_tool:
                self.state = ChatState.AWAITING_TOOL
            elif self._compressing:
                self.state = ChatState.COMPRESSING
            else:
                self.state = ChatState.IDLE
        elif new_state == FlowState.BRANCHING:
            self.state = ChatState.BRANCHING
        elif new_state == FlowState.DORMANT:
            self.state = ChatState.IDLE

        return output

    def add_turn(
        self,
        user_message: str,
        assistant_response: str,
        tools_used: list[str] | None = None,
        turn_result: TurnResult | None = None,
    ) -> None:
        """
        Add a turn to the session.

        Transitions from DORMANT -> STREAMING on first message.
        Computes constitutional reward, creates ChatMark, updates PolicyTrace.

        Args:
            user_message: User's message
            assistant_response: Assistant's response
            tools_used: Optional list of tool names used in this turn
            turn_result: Optional turn result for evidence/reward computation
        """
        # Start session if dormant
        if self._flow_state == FlowState.DORMANT:
            self._transition("start")

        # Process message (always valid in STREAMING)
        if self._flow_state == FlowState.STREAMING:
            self._transition("message")

        # Create turn
        turn = Turn(
            turn_number=self.turn_count,
            user_message=user_message,
            assistant_response=assistant_response,
        )
        self.context.turns.append(turn)
        self.node.turn_count += 1
        self.node.last_active = datetime.now()

        # Compute constitutional reward
        if turn_result is None:
            # Create minimal turn result if not provided
            turn_result = TurnResult(
                response=assistant_response,
                tools=[{"name": tool} for tool in (tools_used or [])],
            )

        constitutional_scores = constitutional_reward(
            action="send_message",
            turn_result=turn_result,
            has_mutations=False,  # TODO: Track mutations when tool system integrated
        )

        # Create ChatMark
        mark = ChatMark(
            session_id=self.id,
            turn_number=turn.turn_number,
            user_message=user_message,
            assistant_response=assistant_response,
            tools_used=tuple(tools_used or []),
            constitutional_scores=constitutional_scores,
            evidence_snapshot=self.evidence.to_dict(),
            reasoning="",  # TODO: Capture reasoning when LLM integration added
        )

        # Add mark to policy trace (immutable append)
        self.policy_trace = self.policy_trace.add_mark(mark)

        # Update evidence based on constitutional scores
        # Use weighted_total as success indicator (>= 0.8 = success)
        total_score = constitutional_scores.weighted_total()
        success = total_score >= 7.5  # ~0.8 * 9.7 (max weighted score)

        # Update evidence with turn result
        turn_result_with_success = TurnResult(
            tools_passed=success,
            tools=turn_result.tools,
            user_corrected=turn_result.user_corrected,
            signals=turn_result.signals,
            response=assistant_response,
            stopping_suggestion=turn_result.stopping_suggestion,
        )
        self.evidence = self.evidence.update(turn_result_with_success)

    def get_constitutional_history(self) -> list[PrincipleScore]:
        """
        Get constitutional scores for all turns.

        Returns:
            List of PrincipleScore objects, one per turn
        """
        return [
            mark.constitutional_scores
            for mark in self.policy_trace.get_marks()
            if mark.constitutional_scores is not None
        ]

    def content_hash(self) -> str:
        """
        Deterministic hash of ordered turn content.

        Used for session equivalence checking.

        See: spec/protocols/chat-web.md §2.2
        """
        content = "|".join(
            f"{t.user_message}:{t.assistant_response}"
            for t in sorted(self.turns, key=lambda t: t.turn_number)
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def branch_topology(self) -> str:
        """
        Branch topology identifier.

        For equivalence checking.
        """
        return f"{self.node.parent_id}:{self.node.fork_point}"

    def equivalent_to(self, other: ChatSession) -> bool:
        """
        Check session equivalence under (≈).

        Two sessions are equivalent if:
        - ordered turn content is identical (content_hash)
        - branch topology is identical
        - evidence state is equal under EvidenceJoin

        Laws:
            s ≈ s                              # Reflexive
            s1 ≈ s2 ⟹ s2 ≈ s1                 # Symmetric
            s1 ≈ s2 ∧ s2 ≈ s3 ⟹ s1 ≈ s3      # Transitive

        See: spec/protocols/chat-web.md §2.2
        """
        return (
            self.content_hash() == other.content_hash()
            and self.branch_topology() == other.branch_topology()
            and self.evidence.join_equivalent(other.evidence)
        )

    def checkpoint(self) -> str:
        """
        Save conversation state.

        Returns:
            Checkpoint ID for future rewind
        """
        checkpoint_id = f"ckpt-{uuid4().hex[:12]}"
        checkpoint = {
            "id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "turn_count": self.turn_count,
            "context": self.context.to_dict(),
            "evidence": self.evidence.to_dict(),
        }
        self.checkpoints.append(checkpoint)
        return checkpoint_id

    def rewind(self, n: int) -> ChatSession:
        """
        Rewind n turns.

        Args:
            n: Number of turns to undo

        Returns:
            New ChatSession with n turns removed

        Law: rewind(checkpoint(s)) ≡ s
        """
        if n > self.turn_count:
            n = self.turn_count

        # Create new session with turns removed
        new_turns = self.turns[:-n] if n > 0 else self.turns

        new_context = WorkingContext(
            id=self.context.id,
            turns=new_turns,
            context_window=self.context.context_window,
            compress_at=self.context.compress_at,
            resume_at=self.context.resume_at,
            is_compressing=self.context.is_compressing,
            last_compression=self.context.last_compression,
            metadata=self.context.metadata,
        )

        return ChatSession(
            id=self.id,
            node=SessionNode(
                id=self.node.id,
                parent_id=self.node.parent_id,
                fork_point=self.node.fork_point,
                branch_name=self.node.branch_name,
                created_at=self.node.created_at,
                last_active=datetime.now(),
                turn_count=len(new_turns),
                is_merged=self.node.is_merged,
                merged_into=self.node.merged_into,
                evidence=self.evidence,
            ),
            state=self.state,
            context=new_context,
            evidence=self.evidence,
            checkpoints=self.checkpoints,
            project_id=self.project_id,
            metadata=self.metadata,
        )

    def fork(self, branch_name: str | None = None) -> tuple[ChatSession, ChatSession]:
        """
        Fork conversation into two branches.

        Note: Chat polynomial doesn't support branching action directly.
        Fork is a K-Block operation, not a flow transition.

        Args:
            branch_name: Name for the new branch

        Returns:
            Tuple of (left_branch, right_branch)

        Law: merge(fork(s)) ≡ s
        """
        if branch_name is None:
            branch_name = f"branch-{self.turn_count}"

        # Left branch (original)
        # Note: Fork is K-Block level, not flow state level
        left = self

        # Right branch (fork)
        right_node = SessionNode(
            parent_id=self.id,
            fork_point=self.turn_count,
            branch_name=branch_name,
            turn_count=self.turn_count,
            evidence=self.evidence,
        )

        right = ChatSession(
            id=generate_session_id(),
            node=right_node,
            _flow_state=FlowState.STREAMING,  # Start in STREAMING
            state=ChatState.IDLE,
            context=WorkingContext(
                turns=self.turns.copy(),
                context_window=self.context.context_window,
                compress_at=self.context.compress_at,
                resume_at=self.context.resume_at,
            ),
            evidence=self.evidence,
            project_id=self.project_id,
            metadata=self.metadata.copy(),
        )

        return (left, right)

    def merge(
        self, other: ChatSession, strategy: MergeStrategy = MergeStrategy.SEQUENTIAL
    ) -> ChatSession:
        """
        Merge another session into this one.

        Args:
            other: Session to merge
            strategy: Merge strategy to use

        Returns:
            New merged session

        Law: merge(merge(a, b), c) ≡ merge(a, merge(b, c))
        """
        if strategy == MergeStrategy.SEQUENTIAL:
            # Append other's turns after this session's turns
            merged_turns = self.turns + other.turns
        elif strategy == MergeStrategy.INTERLEAVE:
            # Merge by timestamp
            merged_turns = sorted(
                self.turns + other.turns, key=lambda t: t.started_at
            )
        else:
            # Manual merge - for now, just sequential
            merged_turns = self.turns + other.turns

        # Combine evidence using join
        # For now, use the prior with more observations
        if self.evidence.prior.alpha + self.evidence.prior.beta > other.evidence.prior.alpha + other.evidence.prior.beta:
            merged_evidence = self.evidence
        else:
            merged_evidence = other.evidence

        merged_context = WorkingContext(
            turns=merged_turns,
            context_window=self.context.context_window,
            compress_at=self.context.compress_at,
            resume_at=self.context.resume_at,
        )

        return ChatSession(
            id=generate_session_id(),
            node=SessionNode(
                parent_id=self.id,
                branch_name=f"{self.node.branch_name}+{other.node.branch_name}",
                turn_count=len(merged_turns),
                evidence=merged_evidence,
            ),
            state=ChatState.IDLE,
            context=merged_context,
            evidence=merged_evidence,
            project_id=self.project_id,
            metadata={**self.metadata, "merged_from": [self.id, other.id]},
        )

    def diff(self, other: ChatSession) -> dict[str, Any]:
        """
        Compare conversation states.

        Args:
            other: Session to compare with

        Returns:
            Diff object showing differences
        """
        # Simple diff for now
        return {
            "turn_count_diff": self.turn_count - other.turn_count,
            "content_hash_same": self.content_hash() == other.content_hash(),
            "evidence_equivalent": self.evidence.join_equivalent(other.evidence),
        }

    @classmethod
    def create(
        cls, project_id: str | None = None, branch_name: str = "main"
    ) -> ChatSession:
        """
        Create a new chat session.

        Session starts in DORMANT state, transitions to STREAMING on first message.

        Args:
            project_id: Optional project ID
            branch_name: Branch name (default "main")

        Returns:
            New ChatSession
        """
        session_id = generate_session_id()
        node = SessionNode(id=session_id, branch_name=branch_name)

        return cls(
            id=session_id,
            node=node,
            project_id=project_id,
            _flow_state=FlowState.DORMANT,
            state=ChatState.IDLE,
            policy_trace=ChatPolicyTrace(session_id=session_id),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "node": self.node.to_dict(),
            "state": self.state.value,
            "flow_state": self._flow_state.value,
            "awaiting_tool": self._awaiting_tool,
            "compressing": self._compressing,
            "context": self.context.to_dict(),
            "evidence": self.evidence.to_dict(),
            "policy_trace": self.policy_trace.to_dict(),
            "checkpoints": self.checkpoints,
            "project_id": self.project_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatSession:
        """Create from dictionary."""
        session_id = data.get("id", generate_session_id())
        return cls(
            id=session_id,
            node=SessionNode.from_dict(data["node"]) if data.get("node") else SessionNode(),
            state=ChatState(data.get("state", "idle")),
            _flow_state=FlowState(data.get("flow_state", "dormant")),
            _awaiting_tool=data.get("awaiting_tool", False),
            _compressing=data.get("compressing", False),
            context=WorkingContext.from_dict(data["context"])
            if data.get("context")
            else WorkingContext(),
            evidence=ChatEvidence.from_dict(data["evidence"])
            if data.get("evidence")
            else ChatEvidence(),
            policy_trace=ChatPolicyTrace.from_dict(data["policy_trace"])
            if data.get("policy_trace")
            else ChatPolicyTrace(session_id=session_id),
            checkpoints=data.get("checkpoints", []),
            project_id=data.get("project_id"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "BranchError",
    "ChatSession",
    "ChatState",
    "InvalidAction",
    "MergeStrategy",
    "SessionNode",
    "generate_session_id",
]
