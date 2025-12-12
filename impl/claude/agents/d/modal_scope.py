"""
ModalScope: Git-like branching for context exploration.

The ModalScope enables comonadic branching of conversation context,
allowing agents to explore speculative paths without polluting the
main context. Key operations:

- branch(): Create an isolated child scope (duplicate + diverge)
- merge(): Integrate branch back into parent
- discard(): Compost the branch, returning entropy budget

Category Theory: This is the comonadic duplicate() made persistent.
When we duplicate a context, we get a context of contexts—each position
becomes its own explorable branch.

AGENTESE Integration:
    void.entropy.sip → branch_name=... → ModalScope.branch()
    void.entropy.pour → action=merge → ModalScope.merge()
    void.entropy.pour → action=discard → ModalScope.discard()

Phase 2.2 Implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

from .context_window import ContextWindow, TurnRole


class MergeStrategy(str, Enum):
    """Strategy for merging a branch back into parent scope."""

    SUMMARIZE = "summarize"  # Compress branch to a summary turn
    CHERRY_PICK = "cherry_pick"  # Select specific turns to keep
    SQUASH = "squash"  # Single turn with key decisions
    REBASE = "rebase"  # Replay child turns on current state


@dataclass
class MergeResult:
    """Result of a scope merge operation."""

    success: bool
    merged_turns: int = 0
    summary: str | None = None
    strategy: MergeStrategy = MergeStrategy.SUMMARIZE
    error: str | None = None
    tokens_added: int = 0

    @property
    def is_error(self) -> bool:
        return not self.success or self.error is not None


@dataclass
class DiscardResult:
    """Result of a scope discard operation."""

    success: bool
    discarded_turns: int = 0
    entropy_returned: float = 0.0
    error: str | None = None


@dataclass
class ModalScope:
    """
    Git-like branching for context exploration.

    The ModalScope wraps a ContextWindow and provides branching semantics
    that leverage the comonadic structure. Each branch is isolated—changes
    in a branch don't affect the parent until merged.

    Example:
        # Create root scope
        root = ModalScope.create_root(max_tokens=8000)
        root.window.append(TurnRole.USER, "Let's explore two approaches")

        # Branch for option A
        branch_a = root.branch("option-a", budget=0.1)
        branch_a.window.append(TurnRole.ASSISTANT, "Option A: Use recursion...")

        # Branch for option B
        branch_b = root.branch("option-b", budget=0.1)
        branch_b.window.append(TurnRole.ASSISTANT, "Option B: Use iteration...")

        # Decide and merge option A
        result = root.merge(branch_a, strategy=MergeStrategy.SUMMARIZE)

        # Discard option B
        root.discard(branch_b)

    Attributes:
        scope_id: Unique identifier for this scope (format: parent_id:branch_name)
        parent_scope: ID of the parent scope (None for root)
        branch_name: Human-readable name for this branch
        created_at: When the scope was created
        window: The branched ContextWindow
        entropy_budget: Fraction of parent tokens allowed for exploration
        merge_strategy: Default strategy for merging this scope
        commit_message: Optional message describing branch purpose
    """

    scope_id: str
    parent_scope: str | None
    branch_name: str
    created_at: datetime

    # The branched context window
    window: ContextWindow

    # Entropy budget (limits how much the branch can grow)
    entropy_budget: float = 0.1  # 10% of parent context by default

    # Merge settings
    merge_strategy: MergeStrategy = MergeStrategy.SUMMARIZE
    commit_message: str | None = None

    # Internal tracking
    _children: dict[str, "ModalScope"] = field(default_factory=dict)
    _is_merged: bool = False
    _is_discarded: bool = False
    _parent_token_count: int = 0  # For budget calculation

    @classmethod
    def create_root(
        cls,
        max_tokens: int = 100_000,
        initial_system: str | None = None,
    ) -> "ModalScope":
        """
        Create a root scope (the main conversation context).

        Args:
            max_tokens: Maximum token budget for the window
            initial_system: Optional system message

        Returns:
            Root ModalScope with fresh ContextWindow
        """
        from .context_window import create_context_window

        window = create_context_window(
            max_tokens=max_tokens,
            initial_system=initial_system,
        )

        return cls(
            scope_id=f"root-{uuid4().hex[:8]}",
            parent_scope=None,
            branch_name="main",
            created_at=datetime.now(UTC),
            window=window,
            entropy_budget=1.0,  # Root has full budget
        )

    def branch(
        self,
        name: str,
        budget: float = 0.05,
        strategy: MergeStrategy = MergeStrategy.SUMMARIZE,
        commit_message: str | None = None,
    ) -> "ModalScope":
        """
        Create a child scope (duplicate + diverge).

        The child scope gets a copy of the current context window
        and can evolve independently. Changes in the child don't
        affect the parent until explicitly merged.

        Args:
            name: Human-readable branch name
            budget: Fraction of parent tokens allowed (default 5%)
            strategy: Default merge strategy for this branch
            commit_message: Optional message describing branch purpose

        Returns:
            New child ModalScope with isolated ContextWindow

        Raises:
            ValueError: If scope is already merged/discarded
            ValueError: If branch name already exists
        """
        if self._is_merged:
            raise ValueError(f"Cannot branch from merged scope {self.scope_id}")
        if self._is_discarded:
            raise ValueError(f"Cannot branch from discarded scope {self.scope_id}")
        if name in self._children:
            raise ValueError(f"Branch '{name}' already exists in {self.scope_id}")

        # Budget enforcement
        if budget <= 0 or budget > 1.0:
            raise ValueError(f"Budget must be in (0, 1.0], got {budget}")

        # Create isolated copy of window
        child_window = ContextWindow.from_dict(self.window.to_dict())

        child = ModalScope(
            scope_id=f"{self.scope_id}:{name}",
            parent_scope=self.scope_id,
            branch_name=name,
            created_at=datetime.now(UTC),
            window=child_window,
            entropy_budget=budget,
            merge_strategy=strategy,
            commit_message=commit_message,
            _parent_token_count=self.window.total_tokens,
        )

        self._children[name] = child
        return child

    def merge(
        self,
        child: "ModalScope",
        strategy: MergeStrategy | None = None,
    ) -> MergeResult:
        """
        Merge a child branch back into this scope.

        Different strategies handle the merge differently:
        - SUMMARIZE: Compress child's new turns to a summary
        - CHERRY_PICK: Keep only specified turns (requires turns_to_keep kwarg)
        - SQUASH: Create single turn with key decisions
        - REBASE: Replay child turns on current state

        Args:
            child: The child scope to merge
            strategy: Override the child's default merge strategy

        Returns:
            MergeResult with details of the merge operation
        """
        # Validate merge is allowed
        if child.parent_scope != self.scope_id:
            return MergeResult(
                success=False,
                error=f"Cannot merge: {child.scope_id} is not a child of {self.scope_id}",
            )

        if child._is_merged:
            return MergeResult(
                success=False,
                error=f"Scope {child.scope_id} was already merged",
            )

        if child._is_discarded:
            return MergeResult(
                success=False,
                error=f"Scope {child.scope_id} was discarded",
            )

        effective_strategy = strategy or child.merge_strategy

        # Get turns added in the child scope
        parent_turn_count = len(
            [t for t in self.window.all_turns()]
        )  # Parent's turns at branch time
        child_turns = child.window.all_turns()
        new_turns = child_turns[parent_turn_count:]

        if not new_turns:
            child._is_merged = True
            # Remove from children even if empty
            if child.branch_name in self._children:
                del self._children[child.branch_name]
            return MergeResult(
                success=True,
                merged_turns=0,
                summary="No new turns to merge",
                strategy=effective_strategy,
            )

        # Execute strategy
        if effective_strategy == MergeStrategy.SUMMARIZE:
            return self._merge_summarize(child, new_turns)
        elif effective_strategy == MergeStrategy.SQUASH:
            return self._merge_squash(child, new_turns)
        elif effective_strategy == MergeStrategy.REBASE:
            return self._merge_rebase(child, new_turns)
        elif effective_strategy == MergeStrategy.CHERRY_PICK:
            # For now, cherry-pick merges all (requires enhancement)
            return self._merge_rebase(child, new_turns)

        return MergeResult(
            success=False,
            error=f"Unknown strategy: {effective_strategy}",
        )

    def _merge_summarize(
        self,
        child: "ModalScope",
        new_turns: list[Any],
    ) -> MergeResult:
        """Merge by summarizing new turns into a single summary."""
        # Create summary of the branch exploration
        turn_summaries = []
        for turn in new_turns:
            role = turn.role.value if hasattr(turn.role, "value") else str(turn.role)
            content_preview = (
                turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
            )
            turn_summaries.append(f"[{role}] {content_preview}")

        branch_summary = f"[Branch Summary: {child.branch_name}]\n"
        if child.commit_message:
            branch_summary += f"Purpose: {child.commit_message}\n"
        branch_summary += f"Exploration ({len(new_turns)} turns):\n"
        branch_summary += "\n".join(turn_summaries)

        # Add summary as a system turn
        self.window.append(TurnRole.SYSTEM, branch_summary)

        child._is_merged = True
        if child.branch_name in self._children:
            del self._children[child.branch_name]

        return MergeResult(
            success=True,
            merged_turns=len(new_turns),
            summary=branch_summary,
            strategy=MergeStrategy.SUMMARIZE,
            tokens_added=len(branch_summary) // 4,
        )

    def _merge_squash(
        self,
        child: "ModalScope",
        new_turns: list[Any],
    ) -> MergeResult:
        """Merge by squashing all new turns into one."""
        # Extract key decisions (assistant turns)
        decisions = []
        for turn in new_turns:
            if turn.role == TurnRole.ASSISTANT:
                decisions.append(turn.content)

        squashed_content = f"[Squashed from {child.branch_name}]\n"
        if child.commit_message:
            squashed_content += f"Purpose: {child.commit_message}\n"
        squashed_content += "Key outputs:\n" + "\n---\n".join(decisions[:3])  # Max 3

        self.window.append(TurnRole.ASSISTANT, squashed_content)

        child._is_merged = True
        if child.branch_name in self._children:
            del self._children[child.branch_name]

        return MergeResult(
            success=True,
            merged_turns=len(new_turns),
            summary=squashed_content,
            strategy=MergeStrategy.SQUASH,
            tokens_added=len(squashed_content) // 4,
        )

    def _merge_rebase(
        self,
        child: "ModalScope",
        new_turns: list[Any],
    ) -> MergeResult:
        """Merge by replaying turns onto current state."""
        tokens_added = 0

        for turn in new_turns:
            new_turn = self.window.append(turn.role, turn.content, turn.metadata)
            tokens_added += new_turn.token_estimate

        child._is_merged = True
        if child.branch_name in self._children:
            del self._children[child.branch_name]

        return MergeResult(
            success=True,
            merged_turns=len(new_turns),
            summary=f"Rebased {len(new_turns)} turns",
            strategy=MergeStrategy.REBASE,
            tokens_added=tokens_added,
        )

    def discard(self, child: "ModalScope") -> DiscardResult:
        """
        Discard a branch, composting its contents.

        The branch's information is lost, but the entropy cost
        is returned to the parent's available budget.

        AGENTESE: void.entropy.pour action=discard

        Args:
            child: The child scope to discard

        Returns:
            DiscardResult with details
        """
        if child.parent_scope != self.scope_id:
            return DiscardResult(
                success=False,
                error=f"Cannot discard: {child.scope_id} is not a child of {self.scope_id}",
            )

        if child._is_merged:
            return DiscardResult(
                success=False,
                error=f"Scope {child.scope_id} was already merged, cannot discard",
            )

        if child._is_discarded:
            return DiscardResult(
                success=False,
                error=f"Scope {child.scope_id} was already discarded",
            )

        # Calculate entropy returned
        child_tokens = child.window.total_tokens
        parent_tokens = max(1, self.window.total_tokens)  # Avoid div by zero
        entropy_returned = child.entropy_budget * (child_tokens / parent_tokens)

        # Count turns that will be lost
        parent_turn_count = len(self.window.all_turns())
        child_turn_count = len(child.window.all_turns())
        discarded_turns = child_turn_count - parent_turn_count

        # Mark as discarded
        child._is_discarded = True
        if child.branch_name in self._children:
            del self._children[child.branch_name]

        return DiscardResult(
            success=True,
            discarded_turns=max(0, discarded_turns),
            entropy_returned=entropy_returned,
        )

    # === Budget Enforcement ===

    @property
    def budget_remaining(self) -> float:
        """
        Remaining budget as fraction of initial budget.

        Returns 0 if over budget, otherwise fraction remaining.
        A fresh branch with no growth returns 1.0 (full budget).
        """
        if self.entropy_budget <= 0:
            return 0.0

        if self._parent_token_count == 0:
            return self.entropy_budget  # Root or no parent context

        current_tokens = self.window.total_tokens
        allowed_growth = int(self._parent_token_count * self.entropy_budget)
        growth = max(0, current_tokens - self._parent_token_count)

        # No growth yet means full budget remaining
        if growth == 0:
            return 1.0

        if allowed_growth == 0:
            return 0.0

        return max(0.0, 1.0 - (growth / allowed_growth))

    @property
    def is_over_budget(self) -> bool:
        """True if branch has exceeded its entropy budget."""
        return self.budget_remaining <= 0

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining before hitting budget limit."""
        if self._parent_token_count == 0:
            return self.window.max_tokens - self.window.total_tokens

        allowed_growth = int(self._parent_token_count * self.entropy_budget)
        growth = max(0, self.window.total_tokens - self._parent_token_count)
        return max(0, allowed_growth - growth)

    # === State Queries ===

    @property
    def is_root(self) -> bool:
        """True if this is the root scope."""
        return self.parent_scope is None

    @property
    def is_active(self) -> bool:
        """True if scope can still receive turns."""
        return not self._is_merged and not self._is_discarded

    @property
    def children(self) -> list["ModalScope"]:
        """List of active child scopes."""
        return list(self._children.values())

    @property
    def depth(self) -> int:
        """Nesting depth of this scope (root = 0)."""
        return self.scope_id.count(":")

    def get_child(self, name: str) -> "ModalScope | None":
        """Get a child scope by name."""
        return self._children.get(name)

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Serialize scope to dict."""
        return {
            "scope_id": self.scope_id,
            "parent_scope": self.parent_scope,
            "branch_name": self.branch_name,
            "created_at": self.created_at.isoformat(),
            "window": self.window.to_dict(),
            "entropy_budget": self.entropy_budget,
            "merge_strategy": self.merge_strategy.value,
            "commit_message": self.commit_message,
            "is_merged": self._is_merged,
            "is_discarded": self._is_discarded,
            "parent_token_count": self._parent_token_count,
            "children": {
                name: child.to_dict() for name, child in self._children.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModalScope":
        """Deserialize scope from dict."""
        scope = cls(
            scope_id=data["scope_id"],
            parent_scope=data.get("parent_scope"),
            branch_name=data["branch_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            window=ContextWindow.from_dict(data["window"]),
            entropy_budget=data.get("entropy_budget", 0.1),
            merge_strategy=MergeStrategy(data.get("merge_strategy", "summarize")),
            commit_message=data.get("commit_message"),
            _is_merged=data.get("is_merged", False),
            _is_discarded=data.get("is_discarded", False),
            _parent_token_count=data.get("parent_token_count", 0),
        )

        # Restore children recursively
        for name, child_data in data.get("children", {}).items():
            scope._children[name] = cls.from_dict(child_data)

        return scope

    def __repr__(self) -> str:
        status = (
            "active"
            if self.is_active
            else ("merged" if self._is_merged else "discarded")
        )
        return f"<ModalScope {self.scope_id} [{status}] turns={len(self.window)} children={len(self._children)}>"
