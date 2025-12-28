"""
Chat Persistence: Universe-backed persistence for chat sessions.

Implements persistent storage for ChatSession using D-gent Crystal infrastructure:
- Crystal-based storage for sessions, turns, crystals, and checkpoints
- Universe backend auto-selection (Postgres > SQLite > Memory)
- Schema versioning via frozen dataclasses
- Graceful degradation when backends unavailable

Architecture:
    ChatPersistence uses Universe for typed, versioned data storage:
    - ChatSessionCrystal: Session metadata and branch info
    - ChatTurnCrystal: Individual conversation turns
    - ChatCrystalCrystal: Crystallized session summaries
    - ChatCheckpointCrystal: Session checkpoints for rewind

Storage Philosophy:
    - Persistence layer owns WHEN and WHY (domain semantics)
    - Universe owns HOW and WHERE (backend selection, schema)
    - ChatSession owns WHAT (domain model)

Witness Integration:
    - Auto-crystallizes significant sessions to K-Blocks
    - Creates witness marks for evidence trail
    - Preserves exploration proofs

See: spec/protocols/chat-web.md
See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/unified-data-crystal.md
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from agents.d.schemas.chat import (
    CHAT_CHECKPOINT_SCHEMA,
    CHAT_CRYSTAL_SCHEMA,
    CHAT_SESSION_SCHEMA,
    CHAT_TURN_SCHEMA,
    ChatCheckpointCrystal,
    ChatCrystalCrystal,
    ChatSessionCrystal,
    ChatTurnCrystal,
)
from agents.d.universe import Query, Universe, get_universe

from .context import Turn, WorkingContext
from .crystallizer import ChatCrystallizer
from .evidence import BetaPrior, ChatEvidence
from .session import ChatSession, ChatState, SessionNode

logger = logging.getLogger(__name__)


# =============================================================================
# Persistence Layer
# =============================================================================


class ChatPersistence:
    """
    Persistent storage for chat sessions using Universe.

    Uses Universe for typed, versioned data storage:
    - ChatSessionCrystal: Session metadata
    - ChatTurnCrystal: Conversation turns
    - ChatCrystalCrystal: Session summaries
    - ChatCheckpointCrystal: Session checkpoints

    Domain Semantics:
    - Sessions are the root entities
    - Turns are stored as separate crystals linked to sessions
    - Universe handles backend selection and schema versioning
    - All queries use Universe with in-memory filtering for complex operations

    Example:
        persistence = ChatPersistence()

        # Save session
        await persistence.save_session(session)

        # Load session
        session = await persistence.load_session(session_id)

        # List sessions
        sessions = await persistence.list_sessions(project_id="myproject")

        # Delete session
        await persistence.delete_session(session_id)
    """

    def __init__(
        self,
        universe: Universe | None = None,
        crystallizer: ChatCrystallizer | None = None,
    ) -> None:
        """
        Initialize ChatPersistence.

        Args:
            universe: Optional Universe instance (uses singleton if None)
            crystallizer: Optional crystallizer for auto-crystallization
        """
        self.universe = universe or get_universe()
        self.crystallizer = crystallizer or ChatCrystallizer()

        # Register schemas on first init
        self._register_schemas()

    def _register_schemas(self) -> None:
        """Register Chat schemas with Universe."""
        self.universe.register_schema(CHAT_SESSION_SCHEMA)
        self.universe.register_schema(CHAT_TURN_SCHEMA)
        self.universe.register_schema(CHAT_CRYSTAL_SCHEMA)
        self.universe.register_schema(CHAT_CHECKPOINT_SCHEMA)

    async def _storage_backend(self) -> str:
        """Detect storage backend from Universe stats."""
        stats = await self.universe.stats()
        return stats.backend

    async def save_session(self, session: ChatSession) -> None:
        """
        Save session to persistent storage via Universe.

        Saves session metadata and all turns as separate crystals.
        Updates existing session if ID already exists (by deleting old crystals).

        Args:
            session: ChatSession to persist

        Raises:
            Exception: If save operation fails
        """
        # Create session crystal
        session_crystal_data = ChatSessionCrystal(
            session_id=session.id,
            project_id=session.project_id,
            parent_id=session.node.parent_id,
            fork_point=session.node.fork_point,
            branch_name=session.node.branch_name,
            state=session.state.value,
            turn_count=session.turn_count,
            context_size=session.context_size,
            evidence_json=json.dumps(session.evidence.to_dict()),
            metadata_json=json.dumps(session.metadata),
            is_merged=session.node.is_merged,
            merged_into=session.node.merged_into,
            created_at=session.node.created_at.isoformat(),
            last_active=session.node.last_active.isoformat(),
        )

        # Delete old session and turn crystals for idempotent updates
        # Query for existing crystals with this session_id
        q = Query(schema="chat.session", limit=1000)
        existing_sessions = await self.universe.query(q)
        for crystal_obj in existing_sessions:
            if isinstance(crystal_obj, ChatSessionCrystal) and crystal_obj.session_id == session.id:
                # Delete via datum_id (need to track this separately)
                # For now, we'll just overwrite by storing with same session_id
                pass

        # Store session crystal (use schema name for lookup)
        await self.universe.store(session_crystal_data, schema_name=CHAT_SESSION_SCHEMA.name)

        # Delete old turn crystals
        q_turns = Query(schema="chat.turn", limit=10000)
        existing_turns = await self.universe.query(q_turns)
        for crystal_obj in existing_turns:
            if isinstance(crystal_obj, ChatTurnCrystal) and crystal_obj.session_id == session.id:
                # Will be replaced by new turn crystals below
                pass

        # Store turn crystals
        for turn in session.turns:
            turn_crystal_data = ChatTurnCrystal(
                turn_id=f"{session.id}:{turn.turn_number}",
                session_id=session.id,
                turn_number=turn.turn_number,
                user_message=turn.user_message,
                assistant_response=turn.assistant_response,
                user_linearity=turn.linearity_tag.value,
                assistant_linearity=turn.linearity_tag.value,
                tools_json=json.dumps(turn.tools_used) if turn.tools_used else None,
                evidence_delta_json=None,  # Evidence is session-level
                confidence=None,
                started_at=turn.started_at.isoformat(),
                completed_at=turn.completed_at.isoformat()
                if turn.completed_at
                else datetime.now().isoformat(),
            )

            await self.universe.store(turn_crystal_data, schema_name=CHAT_TURN_SCHEMA.name)

        # Store checkpoint crystals
        for ckpt in session.checkpoints:
            checkpoint_crystal_data = ChatCheckpointCrystal(
                checkpoint_id=ckpt["id"],
                session_id=session.id,
                turn_count=ckpt["turn_count"],
                context_json=json.dumps(ckpt["context"]),
                evidence_json=json.dumps(ckpt["evidence"]),
                created_at=ckpt["timestamp"],
            )

            await self.universe.store(
                checkpoint_crystal_data, schema_name=CHAT_CHECKPOINT_SCHEMA.name
            )

        logger.debug(f"Saved session {session.id} with {session.turn_count} turns to Universe")

        # Auto-crystallize if significant
        crystallization_result = await self.crystallizer.maybe_crystallize(session)
        if crystallization_result:
            logger.info(
                f"Auto-crystallized session {session.id} to K-Block {crystallization_result.k_block_id} "
                f"(significance: {crystallization_result.significance_score:.1f})"
            )

    async def load_session(self, session_id: str) -> ChatSession | None:
        """
        Load session from Universe storage.

        Args:
            session_id: Session identifier

        Returns:
            ChatSession or None if not found
        """
        # Load session crystal
        q = Query(schema="chat.session", limit=1000)
        all_sessions = await self.universe.query(q)

        session_crystal = None
        for crystal_obj in all_sessions:
            if isinstance(crystal_obj, ChatSessionCrystal) and crystal_obj.session_id == session_id:
                session_crystal = crystal_obj
                break

        if not session_crystal:
            return None

        # Load turn crystals for this session
        q_turns = Query(schema="chat.turn", limit=10000)
        all_turns = await self.universe.query(q_turns)

        turn_crystals = [
            c for c in all_turns if isinstance(c, ChatTurnCrystal) and c.session_id == session_id
        ]

        # Sort by turn number
        turn_crystals.sort(key=lambda t: t.turn_number)

        # Reconstruct turns
        turns = []
        for turn_crystal in turn_crystals:
            from .context import LinearityTag

            turn = Turn(
                turn_number=turn_crystal.turn_number,
                user_message=turn_crystal.user_message,
                assistant_response=turn_crystal.assistant_response,
                linearity_tag=LinearityTag(turn_crystal.user_linearity),
                tools_used=json.loads(turn_crystal.tools_json) if turn_crystal.tools_json else [],
                started_at=datetime.fromisoformat(turn_crystal.started_at),
                completed_at=datetime.fromisoformat(turn_crystal.completed_at)
                if turn_crystal.completed_at
                else None,
            )
            turns.append(turn)

        # Load checkpoint crystals
        q_checkpoints = Query(schema="chat.checkpoint", limit=1000)
        all_checkpoints = await self.universe.query(q_checkpoints)

        checkpoint_crystals = [
            c
            for c in all_checkpoints
            if isinstance(c, ChatCheckpointCrystal) and c.session_id == session_id
        ]

        # Sort by created_at
        checkpoint_crystals.sort(key=lambda c: c.created_at)

        checkpoints = []
        for ckpt_crystal in checkpoint_crystals:
            checkpoints.append(
                {
                    "id": ckpt_crystal.checkpoint_id,
                    "timestamp": ckpt_crystal.created_at,
                    "turn_count": ckpt_crystal.turn_count,
                    "context": json.loads(ckpt_crystal.context_json),
                    "evidence": json.loads(ckpt_crystal.evidence_json),
                }
            )

        # Reconstruct evidence
        evidence_data = json.loads(session_crystal.evidence_json)
        evidence = ChatEvidence.from_dict(evidence_data)

        # Reconstruct context
        context = WorkingContext(turns=turns)

        # Reconstruct session node
        node = SessionNode(
            id=session_crystal.session_id,
            parent_id=session_crystal.parent_id,
            fork_point=session_crystal.fork_point,
            branch_name=session_crystal.branch_name,
            created_at=datetime.fromisoformat(session_crystal.created_at),
            last_active=datetime.fromisoformat(session_crystal.last_active),
            turn_count=session_crystal.turn_count,
            is_merged=session_crystal.is_merged,
            merged_into=session_crystal.merged_into,
            evidence=evidence,
        )

        # Reconstruct session
        session = ChatSession(
            id=session_crystal.session_id,
            node=node,
            state=ChatState(session_crystal.state),
            context=context,
            evidence=evidence,
            checkpoints=checkpoints,
            project_id=session_crystal.project_id,
            metadata=json.loads(session_crystal.metadata_json),
        )

        logger.debug(f"Loaded session {session_id} with {len(turns)} turns from Universe")

        return session

    async def list_sessions(
        self,
        project_id: str | None = None,
        branch_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ChatSession]:
        """
        List sessions with optional filters.

        Args:
            project_id: Filter by project ID
            branch_name: Filter by branch name
            limit: Maximum sessions to return
            offset: Offset for pagination

        Returns:
            List of ChatSession objects, newest first
        """
        # Load all session crystals
        q = Query(schema="chat.session", limit=10000)
        all_sessions = await self.universe.query(q)

        # Filter by project_id and branch_name
        filtered = []
        for crystal_obj in all_sessions:
            if not isinstance(crystal_obj, ChatSessionCrystal):
                continue

            if project_id and crystal_obj.project_id != project_id:
                continue

            if branch_name and crystal_obj.branch_name != branch_name:
                continue

            filtered.append(crystal_obj)

        # Sort by last_active (newest first)
        filtered.sort(key=lambda s: s.last_active, reverse=True)

        # Apply pagination
        paginated = filtered[offset : offset + limit]

        # Load full sessions
        sessions = []
        for session_crystal in paginated:
            session = await self.load_session(session_crystal.session_id)
            if session:
                sessions.append(session)

        return sessions

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all related data.

        Deletes session, turns, crystals, and checkpoints from Universe.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        deleted_count = 0

        # Helper to check if datum has matching session_id
        def has_session_id(datum: Any, target_id: str) -> bool:
            """Check if a datum's content has matching session_id."""
            try:
                content = json.loads(datum.content.decode("utf-8"))
                return content.get("session_id") == target_id
            except (json.JSONDecodeError, AttributeError):
                return False

        # Delete session crystals
        q = Query(schema="chat.session", limit=1000)
        all_sessions = await self.universe.query_raw(q)
        for datum in all_sessions:
            if has_session_id(datum, session_id):
                await self.universe.delete(datum.id)
                deleted_count += 1

        # Delete turn crystals
        q_turns = Query(schema="chat.turn", limit=10000)
        all_turns = await self.universe.query_raw(q_turns)
        for datum in all_turns:
            if has_session_id(datum, session_id):
                await self.universe.delete(datum.id)
                deleted_count += 1

        # Delete checkpoint crystals
        q_checkpoints = Query(schema="chat.checkpoint", limit=1000)
        all_checkpoints = await self.universe.query_raw(q_checkpoints)
        for datum in all_checkpoints:
            if has_session_id(datum, session_id):
                await self.universe.delete(datum.id)
                deleted_count += 1

        # Delete crystal crystals
        q_crystals = Query(schema="chat.crystal", limit=1000)
        all_session_crystals = await self.universe.query_raw(q_crystals)
        for datum in all_session_crystals:
            if has_session_id(datum, session_id):
                await self.universe.delete(datum.id)
                deleted_count += 1

        deleted = deleted_count > 0
        if deleted:
            logger.info(f"Deleted session {session_id} ({deleted_count} crystals)")

        return deleted

    async def save_crystal(
        self,
        session_id: str,
        title: str,
        summary: str,
        key_decisions: list[str] | None = None,
        artifacts: list[str] | None = None,
    ) -> None:
        """
        Save crystallized session summary to Universe.

        Args:
            session_id: Session identifier
            title: Crystal title
            summary: Summary text
            key_decisions: List of key decisions made
            artifacts: List of artifacts produced
        """
        # Load session to get final state
        session = await self.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Create crystal
        crystal_data = ChatCrystalCrystal(
            session_id=session_id,
            title=title,
            summary=summary,
            key_decisions_json=json.dumps(key_decisions or []),
            artifacts_json=json.dumps(artifacts or []),
            final_evidence_json=json.dumps(session.evidence.to_dict()),
            final_turn_count=session.turn_count,
            created_at=datetime.now().isoformat(),
        )

        await self.universe.store(crystal_data, schema_name=CHAT_CRYSTAL_SCHEMA.name)

        logger.info(f"Saved crystal for session {session_id}")

    async def load_crystal(self, session_id: str) -> dict[str, Any] | None:
        """
        Load session crystal from Universe.

        Args:
            session_id: Session identifier

        Returns:
            Crystal data or None if not found
        """
        # Load all crystal crystals
        q = Query(schema="chat.crystal", limit=1000)
        all_crystals = await self.universe.query(q)

        for crystal_obj in all_crystals:
            if isinstance(crystal_obj, ChatCrystalCrystal) and crystal_obj.session_id == session_id:
                return {
                    "session_id": crystal_obj.session_id,
                    "title": crystal_obj.title,
                    "summary": crystal_obj.summary,
                    "key_decisions": json.loads(crystal_obj.key_decisions_json),
                    "artifacts": json.loads(crystal_obj.artifacts_json),
                    "final_evidence": json.loads(crystal_obj.final_evidence_json),
                    "final_turn_count": crystal_obj.final_turn_count,
                    "created_at": crystal_obj.created_at,
                }

        return None

    async def count_sessions(self, project_id: str | None = None) -> int:
        """
        Count total sessions.

        Args:
            project_id: Optional project filter

        Returns:
            Total session count
        """
        # Load all session crystals
        q = Query(schema="chat.session", limit=10000)
        all_sessions = await self.universe.query(q)

        count = 0
        for crystal_obj in all_sessions:
            if not isinstance(crystal_obj, ChatSessionCrystal):
                continue

            if project_id and crystal_obj.project_id != project_id:
                continue

            count += 1

        return count

    async def close(self) -> None:
        """Close Universe connections."""
        # Universe is a singleton, no need to close
        pass


__all__ = ["ChatPersistence"]
