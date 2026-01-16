"""
Chat Crystallizer: Automatic Evidence Capture for Significant Sessions.

Automatically crystallizes chat sessions when they reach significance thresholds,
creating witness marks and K-Blocks as "proof of exploration".

Philosophy:
    "Sufficiently long chats should automatically be captured as new documents/
     k-blocks/some type of proof of exploration."

Integration:
    - Every turn creates a witness mark (via kgent_bridge)
    - Significant sessions auto-crystallize to K-Blocks
    - Crystallization creates a witness mark for evidence trail
    - K-Blocks become searchable proof of exploration

See: spec/protocols/chat-web.md
See: spec/protocols/witness-primitives.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from services.k_block import KBlock, generate_kblock_id
from services.witness import (
    Evidence,
    EvidenceLevel,
    Mark,
    MarkStore,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
    get_mark_store,
)

if TYPE_CHECKING:
    from .session import ChatSession

logger = logging.getLogger(__name__)

# =============================================================================
# Crystallization Thresholds
# =============================================================================

# Minimum turns to consider for crystallization
CRYSTALLIZATION_TURN_THRESHOLD = 10

# Minimum total message length (user + assistant) to consider
CRYSTALLIZATION_LENGTH_THRESHOLD = 5000  # characters

# Significance indicators (tools used, code blocks, etc.)
SIGNIFICANCE_INDICATORS = {
    "tool_use": 5,  # Each tool invocation adds 5 points
    "code_block": 3,  # Code blocks suggest implementation
    "decision": 10,  # Explicit decisions recorded
    "artifact": 15,  # Artifacts created
}

# Minimum significance score to auto-crystallize
SIGNIFICANCE_THRESHOLD = 20


# =============================================================================
# Crystallization Result
# =============================================================================


@dataclass
class CrystallizationResult:
    """Result of crystallizing a chat session."""

    k_block_id: str
    mark_id: str
    evidence_id: str
    turn_count: int
    significance_score: float
    summary: str


# =============================================================================
# Chat Crystallizer
# =============================================================================


class ChatCrystallizer:
    """
    Automatic crystallization of significant chat sessions.

    Creates:
    - K-Block: The conversation as an exploration document
    - Witness Mark: Evidence trail for the crystallization
    - Evidence: Formal proof that exploration occurred

    Example:
        crystallizer = ChatCrystallizer()
        result = await crystallizer.maybe_crystallize(session)
        if result:
            print(f"Crystallized to K-Block {result.k_block_id}")
    """

    def __init__(self, mark_store: MarkStore | None = None):
        """
        Initialize crystallizer.

        Args:
            mark_store: Optional mark store (uses singleton if None)
        """
        self.mark_store = mark_store or get_mark_store()

    def compute_significance(self, session: ChatSession) -> float:
        """
        Compute significance score for a session.

        Considers:
        - Turn count (length of conversation)
        - Message length (depth of exploration)
        - Tools used (implementation activity)
        - Decisions made (captured via evidence)
        - Artifacts created

        Args:
            session: Chat session to evaluate

        Returns:
            Significance score (higher = more significant)
        """
        score = 0.0

        # Turn count contribution (logarithmic scaling)
        import math

        if session.turn_count >= CRYSTALLIZATION_TURN_THRESHOLD:
            score += math.log10(session.turn_count) * 10

        # Message length contribution
        total_length = sum(
            len(turn.user_message) + len(turn.assistant_response) for turn in session.turns
        )
        if total_length >= CRYSTALLIZATION_LENGTH_THRESHOLD:
            score += (total_length / 1000) * 2  # 2 points per 1000 chars

        # Tool usage
        tool_count = sum(len(turn.tools_used) for turn in session.turns if turn.tools_used)
        score += tool_count * SIGNIFICANCE_INDICATORS["tool_use"]

        # Evidence-based indicators
        # Count code blocks (approximate)
        code_blocks = sum(
            turn.user_message.count("```") + turn.assistant_response.count("```")
            for turn in session.turns
        )
        score += (code_blocks // 2) * SIGNIFICANCE_INDICATORS["code_block"]

        # Decisions from evidence (if tracked)
        if hasattr(session.evidence, "decisions_count"):
            score += session.evidence.decisions_count * SIGNIFICANCE_INDICATORS["decision"]

        return score

    def should_crystallize(self, session: ChatSession) -> tuple[bool, float, str]:
        """
        Determine if session should be auto-crystallized.

        Args:
            session: Chat session to evaluate

        Returns:
            Tuple of (should_crystallize, score, reason)
        """
        # Must meet minimum turn threshold
        if session.turn_count < CRYSTALLIZATION_TURN_THRESHOLD:
            return (
                False,
                0.0,
                f"Below turn threshold ({session.turn_count} < {CRYSTALLIZATION_TURN_THRESHOLD})",
            )

        # Compute significance
        score = self.compute_significance(session)

        # Check threshold
        if score >= SIGNIFICANCE_THRESHOLD:
            return True, score, f"Significant exploration (score: {score:.1f})"

        return (
            False,
            score,
            f"Below significance threshold ({score:.1f} < {SIGNIFICANCE_THRESHOLD})",
        )

    async def maybe_crystallize(self, session: ChatSession) -> CrystallizationResult | None:
        """
        Crystallize session if it meets significance thresholds.

        Creates:
        1. K-Block containing the conversation
        2. Witness mark for the crystallization
        3. Evidence record for proof of exploration

        Args:
            session: Chat session to potentially crystallize

        Returns:
            CrystallizationResult if crystallized, None otherwise
        """
        should_crystallize, score, reason = self.should_crystallize(session)

        if not should_crystallize:
            logger.debug(f"Session {session.id} not crystallized: {reason}")
            return None

        logger.info(f"Crystallizing session {session.id}: {reason}")

        # Create summary from session
        summary = self._generate_summary(session)

        # Create K-Block from conversation
        k_block = self._create_kblock(session, summary)

        # Store K-Block to cosmos (making it retrievable)
        await self._store_kblock(k_block, session.id)

        # Create Evidence record
        evidence = self._create_evidence(session, k_block, score)

        # Create witness mark
        mark = await self._create_witness_mark(session, k_block, evidence, score, summary)

        return CrystallizationResult(
            k_block_id=k_block.id,
            mark_id=mark.id,
            evidence_id=evidence.id,
            turn_count=session.turn_count,
            significance_score=score,
            summary=summary,
        )

    def _generate_summary(self, session: ChatSession) -> str:
        """Generate summary of session for K-Block title."""
        # Extract first user message as context
        if session.turns:
            first_message = session.turns[0].user_message[:100]
            return (
                f"Chat exploration: {first_message}..."
                if len(first_message) >= 100
                else f"Chat exploration: {first_message}"
            )
        return f"Chat session {session.id}"

    def _create_kblock(self, session: ChatSession, summary: str) -> KBlock:
        """
        Create K-Block from chat session.

        The K-Block content is a markdown rendering of the conversation,
        making it searchable and referenceable.
        """
        # Build markdown content
        lines = [
            f"# {summary}",
            "",
            f"**Session ID**: {session.id}",
            f"**Created**: {session.node.created_at.isoformat()}",
            f"**Turns**: {session.turn_count}",
            f"**Branch**: {session.node.branch_name}",
            "",
            "---",
            "",
        ]

        # Add conversation turns
        for turn in session.turns:
            lines.extend(
                [
                    f"## Turn {turn.turn_number}",
                    "",
                    f"**User**: {turn.user_message}",
                    "",
                    f"**Assistant**: {turn.assistant_response}",
                    "",
                ]
            )

            # Add tool usage if present
            if turn.tools_used:
                lines.append(f"*Tools used: {', '.join(turn.tools_used)}*")
                lines.append("")

            lines.append("---")
            lines.append("")

        content = "\n".join(lines)

        # Create K-Block
        k_block = KBlock(
            id=generate_kblock_id(),
            path=f"explorations/chat/{session.id}.md",
            content=content,
            base_content=content,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            not_ingested=False,  # This is a new document we're creating
            analysis_required=False,  # Already analyzed (it's a chat)
        )

        return k_block

    async def _store_kblock(self, k_block: KBlock, session_id: str) -> None:
        """
        Store K-Block to cosmos for retrieval.

        Args:
            k_block: The K-Block to store
            session_id: Chat session ID for logging

        This makes the crystallized conversation searchable and referenceable.
        """
        from services.k_block import get_cosmos

        cosmos = get_cosmos()

        # Commit K-Block content to cosmos
        # The cosmos handles versioning and append-only storage
        version_id = await cosmos.commit(
            path=k_block.path,
            content=k_block.content,
            actor="chat.crystallizer",
            reasoning=f"Crystallized chat session {session_id}",
        )

        logger.info(
            f"Stored K-Block {k_block.id} to cosmos at {k_block.path} (version: {version_id})"
        )

    def _create_evidence(
        self,
        session: ChatSession,
        k_block: KBlock,
        score: float,
    ) -> Evidence:
        """Create evidence record for crystallization."""
        from services.witness import compute_content_hash, generate_evidence_id

        return Evidence(
            id=generate_evidence_id(),
            target_spec=k_block.path,
            content_hash=compute_content_hash(k_block.content),
            level=EvidenceLevel.MARK,  # L0: Human attention via crystallization
            source_type="crystallization",
            created_at=datetime.now(),
            created_by="chat.crystallizer",
            metadata={
                "session_id": session.id,
                "turn_count": session.turn_count,
                "significance_score": score,
                "branch_name": session.node.branch_name,
                "k_block_id": k_block.id,
            },
        )

    async def _create_witness_mark(
        self,
        session: ChatSession,
        k_block: KBlock,
        evidence: Evidence,
        score: float,
        summary: str,
    ) -> Mark:
        """Create witness mark for crystallization event."""
        mark = Mark(
            id=generate_mark_id(),
            origin="chat.crystallizer",
            stimulus=Stimulus(
                kind="chat",
                content=f"Session {session.id} reached {session.turn_count} turns",
                source="chat.persistence",
                metadata={
                    "session_id": session.id,
                    "turn_count": session.turn_count,
                    "branch_name": session.node.branch_name,
                },
            ),
            response=Response(
                kind="crystallization",
                content=f"Crystallized to K-Block {k_block.id}",
                success=True,
                metadata={
                    "k_block_id": k_block.id,
                    "k_block_path": k_block.path,
                    "evidence_id": evidence.id,
                    "significance_score": score,
                },
            ),
            umwelt=UmweltSnapshot(
                observer_id="chat.crystallizer",
                role="crystallizer",
                capabilities=frozenset({"observe", "crystallize", "create_kblock"}),
                perceptions=frozenset({"session_turns", "significance", "evidence"}),
                trust_level=2,  # Suggestion level (auto-crystallize is a suggestion)
            ),
            timestamp=datetime.now(),
            proof=Proof.empirical(
                data=f"Session {session.id}: {session.turn_count} turns, score {score:.1f}",
                warrant="Significant exploration sessions should be preserved as K-Blocks",
                claim=f"This session warranted crystallization: {summary}",
                backing="CLAUDE.md: 'Evidence-driven development' + witness integration spec",
                principles=("evidence-driven", "exploration", "witness"),
            ),
            tags=("chat", "crystallization", "exploration-proof", "k-block"),
            metadata={
                "session_id": session.id,
                "k_block_id": k_block.id,
                "significance_score": score,
            },
        )

        # Store mark
        self.mark_store.append(mark)

        logger.info(
            f"Created witness mark {mark.id} for session {session.id} "
            f"crystallization to K-Block {k_block.id}"
        )

        return mark


__all__ = [
    "ChatCrystallizer",
    "CrystallizationResult",
    "CRYSTALLIZATION_TURN_THRESHOLD",
    "SIGNIFICANCE_THRESHOLD",
]
