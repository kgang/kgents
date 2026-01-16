"""
Decisions Service: Access to kg decide History for Self-Reflective OS.

Provides comprehensive access to decision history from multiple sources:
- Fusion results (symmetric supersession decisions)
- Witness marks with decision tags
- Git commit messages containing decision markers

Philosophy:
    "Every decision is a fusion of perspectives."
    "The witness marks the decision; the git records the implementation."

AGENTESE Paths (via DecisionsNode):
- self.decisions.list      - List all decisions
- self.decisions.search    - Search decisions
- self.decisions.get       - Get a specific decision
- self.decisions.for_file  - Decisions about a specific file

Usage:
    service = DecisionsService()
    decisions = await service.list_decisions(limit=100)
    matched = await service.search_decisions("LangChain")
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.fusion import FusionService
    from services.witness import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass(frozen=True)
class Decision:
    """
    A recorded decision from the kg decide system.

    Attributes:
        id: Unique decision ID
        topic: Decision topic/title
        kent_view: Kent's position
        kent_reasoning: Kent's reasoning
        claude_view: Claude's position
        claude_reasoning: Claude's reasoning
        synthesis: The synthesized decision
        why: Why this synthesis was chosen
        timestamp: When the decision was made
        witness_mark_id: Associated witness mark ID (if any)
        fusion_id: Associated fusion ID (if any)
        files_affected: Files mentioned in the decision
        tags: Decision tags/categories
    """

    id: str
    topic: str
    kent_view: str
    kent_reasoning: str
    claude_view: str
    claude_reasoning: str
    synthesis: str
    why: str
    timestamp: datetime
    witness_mark_id: str | None = None
    fusion_id: str | None = None
    files_affected: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "kent_view": self.kent_view,
            "kent_reasoning": self.kent_reasoning,
            "claude_view": self.claude_view,
            "claude_reasoning": self.claude_reasoning,
            "synthesis": self.synthesis,
            "why": self.why,
            "timestamp": self.timestamp.isoformat(),
            "witness_mark_id": self.witness_mark_id,
            "fusion_id": self.fusion_id,
            "files_affected": list(self.files_affected),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            topic=data["topic"],
            kent_view=data.get("kent_view", ""),
            kent_reasoning=data.get("kent_reasoning", ""),
            claude_view=data.get("claude_view", ""),
            claude_reasoning=data.get("claude_reasoning", ""),
            synthesis=data.get("synthesis", ""),
            why=data.get("why", ""),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if isinstance(data.get("timestamp"), str)
            else data.get("timestamp", datetime.now(timezone.utc)),
            witness_mark_id=data.get("witness_mark_id"),
            fusion_id=data.get("fusion_id"),
            files_affected=tuple(data.get("files_affected", [])),
            tags=tuple(data.get("tags", [])),
        )


@dataclass(frozen=True)
class QuickDecision:
    """
    A quick decision (fast mode) from kg decide --fast.

    Attributes:
        id: Unique decision ID
        topic: What was decided
        reasoning: Why
        timestamp: When
        witness_mark_id: Associated mark ID
    """

    id: str
    topic: str
    reasoning: str
    timestamp: datetime
    witness_mark_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "witness_mark_id": self.witness_mark_id,
        }


@dataclass
class DecisionSearchResult:
    """
    Result of a decision search.

    Attributes:
        decisions: Matching decisions
        total_count: Total matches (may exceed returned)
        query: The search query
    """

    decisions: list[Decision | QuickDecision]
    total_count: int
    query: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "decisions": [d.to_dict() for d in self.decisions],
            "total_count": self.total_count,
            "query": self.query,
        }


# =============================================================================
# Decisions Service
# =============================================================================


class DecisionsService:
    """
    Access to kg decide history.

    Aggregates decisions from multiple sources:
    1. FusionService (symmetric supersession decisions)
    2. WitnessPersistence (marks with decision tags)
    3. Git history (commit messages with decision patterns)

    Teaching:
        gotcha: Decisions are aggregated at query time, not pre-indexed.
                For large histories, consider caching.

        gotcha: Git-based decisions are inferred from commit message patterns
                like "Decision: X" or "kg decide". These are heuristic.

        gotcha: Quick decisions (--fast mode) only have topic/reasoning,
                not the full kent_view/claude_view dialectic.
    """

    def __init__(
        self,
        fusion_service: FusionService | None = None,
        witness: WitnessPersistence | None = None,
        repo_root: Path | None = None,
    ) -> None:
        """
        Initialize DecisionsService.

        Args:
            fusion_service: FusionService for symmetric supersession decisions
            witness: WitnessPersistence for witness marks
            repo_root: Root of git repository for git-based decisions
        """
        self._fusion = fusion_service
        self._witness = witness
        self._repo_root = repo_root or Path.cwd()

        # In-memory storage for standalone decisions
        self._decisions: dict[str, Decision] = {}
        self._quick_decisions: dict[str, QuickDecision] = {}

    async def list_decisions(
        self,
        limit: int = 100,
        offset: int = 0,
        include_quick: bool = True,
    ) -> list[Decision | QuickDecision]:
        """
        List all decisions.

        Args:
            limit: Maximum number of decisions
            offset: Starting offset for pagination
            include_quick: Include quick decisions (--fast mode)

        Returns:
            List of decisions ordered by timestamp (newest first)
        """
        all_decisions: list[Decision | QuickDecision] = []

        # Get from FusionService
        if self._fusion:
            for fusion_id, fusion in self._fusion._fusions.items():
                if fusion.synthesis:
                    decision = Decision(
                        id=str(fusion_id),
                        topic=f"{fusion.proposal_a.content} vs {fusion.proposal_b.content}",
                        kent_view=fusion.proposal_a.content
                        if fusion.proposal_a.agent.value == "kent"
                        else fusion.proposal_b.content,
                        kent_reasoning=fusion.proposal_a.reasoning
                        if fusion.proposal_a.agent.value == "kent"
                        else fusion.proposal_b.reasoning,
                        claude_view=fusion.proposal_a.content
                        if fusion.proposal_a.agent.value == "claude"
                        else fusion.proposal_b.content,
                        claude_reasoning=fusion.proposal_a.reasoning
                        if fusion.proposal_a.agent.value == "claude"
                        else fusion.proposal_b.reasoning,
                        synthesis=fusion.synthesis.content,
                        why=fusion.synthesis.reasoning,
                        timestamp=fusion.completed_at or fusion.started_at,
                        fusion_id=str(fusion_id),
                        tags=tuple(fusion.proposal_a.principles + fusion.proposal_b.principles),
                    )
                    all_decisions.append(decision)

        # Get from WitnessPersistence (marks tagged as decisions)
        if self._witness:
            try:
                # Try to get marks with decision-related tags
                marks = await self._witness.get_marks(
                    limit=limit * 2,  # Get more since we'll filter
                    tags=["decision", "decide", "kg-decide"],
                )
                for mark in marks:
                    # Parse decision info from mark
                    parsed_decision = self._parse_decision_from_mark(mark)
                    if parsed_decision:
                        all_decisions.append(parsed_decision)
            except Exception as e:
                logger.debug(f"Could not fetch witness marks: {e}")

        # Add in-memory decisions
        all_decisions.extend(self._decisions.values())

        # Add quick decisions if requested
        if include_quick:
            all_decisions.extend(self._quick_decisions.values())

        # Sort by timestamp (newest first)
        all_decisions.sort(key=lambda d: d.timestamp, reverse=True)

        # Apply pagination
        return all_decisions[offset : offset + limit]

    async def search_decisions(
        self,
        query: str,
        limit: int = 50,
    ) -> DecisionSearchResult:
        """
        Search decisions by query.

        Args:
            query: Search query (searches topic, synthesis, reasoning)
            limit: Maximum number of results

        Returns:
            DecisionSearchResult with matching decisions
        """
        all_decisions = await self.list_decisions(limit=1000, include_quick=True)

        query_lower = query.lower()
        matched = []

        for decision in all_decisions:
            # Check all searchable fields
            searchable = [
                decision.topic.lower(),
            ]

            if isinstance(decision, Decision):
                searchable.extend(
                    [
                        decision.synthesis.lower(),
                        decision.kent_view.lower(),
                        decision.kent_reasoning.lower(),
                        decision.claude_view.lower(),
                        decision.claude_reasoning.lower(),
                        decision.why.lower(),
                    ]
                )
            else:
                searchable.append(decision.reasoning.lower())

            if any(query_lower in s for s in searchable):
                matched.append(decision)

        return DecisionSearchResult(
            decisions=matched[:limit],
            total_count=len(matched),
            query=query,
        )

    async def get_decision(self, decision_id: str) -> Decision | QuickDecision | None:
        """
        Get a specific decision by ID.

        Args:
            decision_id: Decision ID

        Returns:
            Decision or None if not found
        """
        # Check in-memory storage
        if decision_id in self._decisions:
            return self._decisions[decision_id]
        if decision_id in self._quick_decisions:
            return self._quick_decisions[decision_id]

        # Check FusionService
        if self._fusion:
            from services.fusion.types import FusionId

            fusion = self._fusion.get_fusion(FusionId(decision_id))
            if fusion and fusion.synthesis:
                return Decision(
                    id=decision_id,
                    topic=f"{fusion.proposal_a.content} vs {fusion.proposal_b.content}",
                    kent_view=fusion.proposal_a.content
                    if fusion.proposal_a.agent.value == "kent"
                    else fusion.proposal_b.content,
                    kent_reasoning=fusion.proposal_a.reasoning
                    if fusion.proposal_a.agent.value == "kent"
                    else fusion.proposal_b.reasoning,
                    claude_view=fusion.proposal_a.content
                    if fusion.proposal_a.agent.value == "claude"
                    else fusion.proposal_b.content,
                    claude_reasoning=fusion.proposal_a.reasoning
                    if fusion.proposal_a.agent.value == "claude"
                    else fusion.proposal_b.reasoning,
                    synthesis=fusion.synthesis.content,
                    why=fusion.synthesis.reasoning,
                    timestamp=fusion.completed_at or fusion.started_at,
                    fusion_id=decision_id,
                )

        return None

    async def get_decisions_for_file(
        self,
        file_path: str,
        limit: int = 50,
    ) -> list[Decision | QuickDecision]:
        """
        Get decisions that mention or affect a specific file.

        Args:
            file_path: File path (relative or absolute)
            limit: Maximum number of results

        Returns:
            List of decisions affecting this file
        """
        all_decisions = await self.list_decisions(limit=1000, include_quick=True)

        # Normalize file path for matching
        normalized = file_path.replace("\\", "/").lower()
        if normalized.startswith("/"):
            # Try to make relative
            try:
                normalized = str(Path(file_path).relative_to(self._repo_root)).lower()
            except ValueError:
                pass

        matched: list[Decision | QuickDecision] = []
        for decision in all_decisions:
            # Check files_affected
            if isinstance(decision, Decision):
                for affected in decision.files_affected:
                    if normalized in affected.lower() or affected.lower() in normalized:
                        matched.append(decision)
                        break

            # Check if file is mentioned in topic/synthesis
            topic_lower = decision.topic.lower()
            if normalized in topic_lower or Path(file_path).name.lower() in topic_lower:
                if decision not in matched:
                    matched.append(decision)

        return matched[:limit]

    def record_decision(
        self,
        topic: str,
        kent_view: str,
        kent_reasoning: str,
        claude_view: str,
        claude_reasoning: str,
        synthesis: str,
        why: str,
        files_affected: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Decision:
        """
        Record a new decision (manual API for kg decide).

        Args:
            topic: Decision topic
            kent_view: Kent's position
            kent_reasoning: Kent's reasoning
            claude_view: Claude's position
            claude_reasoning: Claude's reasoning
            synthesis: The synthesized decision
            why: Why this synthesis
            files_affected: Files affected by this decision
            tags: Decision tags

        Returns:
            The recorded Decision
        """
        import uuid

        decision_id = f"dec-{uuid.uuid4().hex[:8]}"
        decision = Decision(
            id=decision_id,
            topic=topic,
            kent_view=kent_view,
            kent_reasoning=kent_reasoning,
            claude_view=claude_view,
            claude_reasoning=claude_reasoning,
            synthesis=synthesis,
            why=why,
            timestamp=datetime.now(timezone.utc),
            files_affected=tuple(files_affected or []),
            tags=tuple(tags or []),
        )
        self._decisions[decision_id] = decision
        return decision

    def record_quick_decision(
        self,
        topic: str,
        reasoning: str,
    ) -> QuickDecision:
        """
        Record a quick decision (kg decide --fast).

        Args:
            topic: What was decided
            reasoning: Why

        Returns:
            The recorded QuickDecision
        """
        import uuid

        decision_id = f"qdec-{uuid.uuid4().hex[:8]}"
        decision = QuickDecision(
            id=decision_id,
            topic=topic,
            reasoning=reasoning,
            timestamp=datetime.now(timezone.utc),
        )
        self._quick_decisions[decision_id] = decision
        return decision

    def _parse_decision_from_mark(self, mark: Any) -> Decision | QuickDecision | None:
        """
        Parse a Decision from a WitnessMark.

        Attempts to extract decision structure from mark metadata.
        """
        try:
            # Check if mark has decision metadata
            action = getattr(mark, "action", "") or ""
            reasoning = getattr(mark, "reasoning", "") or ""
            timestamp = getattr(mark, "timestamp", None) or datetime.now(timezone.utc)
            mark_id = getattr(mark, "mark_id", None) or getattr(mark, "id", "")

            # Look for decision pattern in action
            if "decide" in action.lower() or "decision" in action.lower():
                # Try to parse full decision from reasoning
                if "kent:" in reasoning.lower() and "claude:" in reasoning.lower():
                    # Full dialectic decision
                    parts = self._parse_dialectic(reasoning)
                    if parts:
                        return Decision(
                            id=f"mark-{mark_id}",
                            topic=action,
                            kent_view=parts.get("kent_view", ""),
                            kent_reasoning=parts.get("kent_reasoning", ""),
                            claude_view=parts.get("claude_view", ""),
                            claude_reasoning=parts.get("claude_reasoning", ""),
                            synthesis=parts.get("synthesis", ""),
                            why=parts.get("why", ""),
                            timestamp=timestamp,
                            witness_mark_id=str(mark_id),
                        )
                else:
                    # Quick decision
                    return QuickDecision(
                        id=f"mark-{mark_id}",
                        topic=action,
                        reasoning=reasoning,
                        timestamp=timestamp,
                        witness_mark_id=str(mark_id),
                    )
        except Exception as e:
            logger.debug(f"Failed to parse decision from mark: {e}")

        return None

    def _parse_dialectic(self, text: str) -> dict[str, str] | None:
        """
        Parse dialectic structure from text.

        Looks for patterns like:
        Kent: [view] because [reasoning]
        Claude: [view] because [reasoning]
        Synthesis: [synthesis]
        Why: [why]
        """
        result: dict[str, str] = {}

        patterns = [
            (
                r"Kent:\s*(.+?)(?:because|reasoning:)\s*(.+?)(?=Claude:|$)",
                "kent_view",
                "kent_reasoning",
            ),
            (
                r"Claude:\s*(.+?)(?:because|reasoning:)\s*(.+?)(?=Synthesis:|$)",
                "claude_view",
                "claude_reasoning",
            ),
            (r"Synthesis:\s*(.+?)(?=Why:|$)", "synthesis", None),
            (r"Why:\s*(.+?)$", "why", None),
        ]

        for pattern, key1, key2 in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                result[key1] = match.group(1).strip()
                if key2 and len(match.groups()) > 1:
                    result[key2] = match.group(2).strip()

        return result if result else None


# =============================================================================
# Factory Functions
# =============================================================================


_decisions_service: DecisionsService | None = None


def get_decisions_service(
    fusion_service: FusionService | None = None,
    witness: WitnessPersistence | None = None,
    repo_root: Path | None = None,
) -> DecisionsService:
    """
    Get or create the DecisionsService singleton.

    Args:
        fusion_service: FusionService (only used on first call)
        witness: WitnessPersistence (only used on first call)
        repo_root: Repository root (only used on first call)

    Returns:
        DecisionsService instance
    """
    global _decisions_service
    if _decisions_service is None:
        _decisions_service = DecisionsService(
            fusion_service=fusion_service,
            witness=witness,
            repo_root=repo_root,
        )
    return _decisions_service


def reset_decisions_service() -> None:
    """Reset the DecisionsService singleton (for testing)."""
    global _decisions_service
    _decisions_service = None


__all__ = [
    "Decision",
    "QuickDecision",
    "DecisionSearchResult",
    "DecisionsService",
    "get_decisions_service",
    "reset_decisions_service",
]
