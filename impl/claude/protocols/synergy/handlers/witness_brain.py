"""
Witness to Brain Handler: Auto-capture thoughts and git events as Brain crystals.

When Witness captures a thought or detects significant git activity,
this handler automatically creates a memory crystal in Brain.

"The ghost is not a haunting—it's a witnessing that becomes a doing."

This enables:
- Automatic memory persistence from daemon observations
- Git activity → learning capture pipeline
- Cross-session continuity of witnessed insights
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..events import SynergyEvent, SynergyEventType, SynergyResult
from .base import BaseSynergyHandler


class WitnessToBrainHandler(BaseSynergyHandler):
    """
    Handler that captures Witness events to Brain as memory crystals.

    Supports two event types:
    1. WITNESS_THOUGHT_CAPTURED → Create crystal from thought content
    2. WITNESS_GIT_COMMIT → Create crystal from significant commit

    The crystal content includes:
    - Source and tags from the observation
    - Timestamp for historical tracking
    - Confidence level for filtering
    """

    SUPPORTED_EVENTS = {
        SynergyEventType.WITNESS_THOUGHT_CAPTURED,
        SynergyEventType.WITNESS_GIT_COMMIT,
    }

    def __init__(self, auto_capture: bool = True) -> None:
        """
        Initialize the handler.

        Args:
            auto_capture: If True, automatically captures to Brain.
                         If False, just logs (useful for testing).
        """
        super().__init__()
        self._auto_capture = auto_capture

    @property
    def name(self) -> str:
        return "WitnessToBrainHandler"

    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """Handle Witness events (thought captured or git commit)."""
        if event.event_type not in self.SUPPORTED_EVENTS:
            return self.skip(f"Not handling {event.event_type.value}")

        # Route to appropriate handler
        if event.event_type == SynergyEventType.WITNESS_THOUGHT_CAPTURED:
            return await self._handle_thought_captured(event)
        elif event.event_type == SynergyEventType.WITNESS_GIT_COMMIT:
            return await self._handle_git_commit(event)

        return self.skip(f"Unknown event type: {event.event_type.value}")

    async def _handle_thought_captured(self, event: SynergyEvent) -> SynergyResult:
        """Handle thought captured event → create memory crystal."""
        payload = event.payload
        content = payload.get("content", "")
        source = payload.get("source", "unknown")
        tags = payload.get("tags", [])
        confidence = payload.get("confidence", 1.0)

        # Skip low-confidence thoughts (below threshold)
        if confidence < 0.5:
            return self.skip(f"Low confidence thought: {confidence:.2f}")

        # Create crystal content
        crystal_content = self._create_thought_crystal_content(
            content=content,
            source=source,
            tags=tags,
            confidence=confidence,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture thought: {content[:50]}...")
            return self.success(
                message="Dry run - would capture thought to Brain",
                metadata={
                    "content_preview": content[:100],
                    "source": source,
                    "tags": tags,
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(
                content=crystal_content,
                concept_id=f"witness-thought-{event.source_id}",
            )
            self._logger.info(f"Captured thought to Brain: {crystal_id}")
            return self.success(
                message="Thought captured to Brain as crystal",
                artifact_id=crystal_id,
                metadata={
                    "content_preview": content[:100],
                    "source": source,
                    "tags": tags,
                },
            )
        except Exception as e:
            self._logger.warning(f"Failed to capture thought to Brain: {e}")
            # Graceful degradation: don't fail, just log
            return self.skip(f"Brain unavailable: {e}")

    async def _handle_git_commit(self, event: SynergyEvent) -> SynergyResult:
        """Handle git commit event → create memory crystal for significant commits."""
        payload = event.payload
        message = payload.get("message", "")
        author_email = payload.get("author_email", "unknown")
        files_changed = payload.get("files_changed", 0)
        insertions = payload.get("insertions", 0)
        deletions = payload.get("deletions", 0)

        # Only capture significant commits (more than a few changes)
        total_changes = insertions + deletions
        if files_changed < 3 and total_changes < 50:
            return self.skip(f"Minor commit: {files_changed} files, {total_changes} changes")

        # Create crystal content
        crystal_content = self._create_commit_crystal_content(
            commit_hash=event.source_id,
            message=message,
            author_email=author_email,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
            timestamp=event.timestamp,
        )

        if not self._auto_capture:
            self._logger.info(f"Would capture commit: {event.source_id[:8]}")
            return self.success(
                message="Dry run - would capture commit to Brain",
                metadata={
                    "commit_hash": event.source_id,
                    "message_preview": message[:100],
                },
            )

        # Actually capture to Brain
        try:
            crystal_id = await self._capture_to_brain(
                content=crystal_content,
                concept_id=f"witness-commit-{event.source_id[:8]}",
            )
            self._logger.info(f"Captured commit to Brain: {crystal_id}")
            return self.success(
                message="Git commit captured to Brain as crystal",
                artifact_id=crystal_id,
                metadata={
                    "commit_hash": event.source_id,
                    "message_preview": message[:100],
                    "files_changed": files_changed,
                },
            )
        except Exception as e:
            self._logger.warning(f"Failed to capture commit to Brain: {e}")
            return self.skip(f"Brain unavailable: {e}")

    def _create_thought_crystal_content(
        self,
        content: str,
        source: str,
        tags: list[str],
        confidence: float,
        timestamp: datetime,
    ) -> str:
        """Create the content for a thought crystal."""
        tags_str = ", ".join(tags) if tags else "none"

        return f"""Witness Observation

Captured: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Source: {source}
Tags: {tags_str}
Confidence: {confidence:.0%}

---

{content}

---

This observation was automatically captured by the Witness daemon.
Use this for:
- Pattern recognition across sessions
- Learning from repeated observations
- Contextual awareness in future work
"""

    def _create_commit_crystal_content(
        self,
        commit_hash: str,
        message: str,
        author_email: str,
        files_changed: int,
        insertions: int,
        deletions: int,
        timestamp: datetime,
    ) -> str:
        """Create the content for a git commit crystal."""
        return f"""Git Commit Observed

Commit: {commit_hash[:8]}
Author: {author_email}
Date: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Message:
{message}

Statistics:
- Files changed: {files_changed}
- Insertions: +{insertions}
- Deletions: -{deletions}
- Net change: {insertions - deletions:+d}

---

This commit was automatically observed by the Witness daemon.
Significant commits are captured for:
- Development history tracking
- Pattern analysis across sessions
- Learning from code evolution
"""

    async def _capture_to_brain(
        self,
        content: str,
        concept_id: str,
    ) -> str:
        """Capture content to Brain and return crystal ID."""
        # Import here to avoid circular imports and allow graceful degradation
        try:
            from protocols.agentese import create_brain_logos
            from protocols.agentese.node import Observer
        except ImportError as e:
            raise RuntimeError(f"Brain logos not available: {e}") from e

        # Create a minimal logos for capture
        logos = create_brain_logos(embedder_type="auto")
        observer = Observer.guest()

        result = await logos.invoke(
            "self.memory.capture",
            observer,
            content=content,
            concept_id=concept_id,
        )

        # Return the concept ID
        returned_id: str = str(result.get("concept_id", concept_id))
        return returned_id


__all__ = ["WitnessToBrainHandler"]
