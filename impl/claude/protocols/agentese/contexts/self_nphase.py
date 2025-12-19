"""
AGENTESE Self N-Phase Context: Session Phase Management

The self.session context provides access to N-Phase session management:
- self.session.create - Create a new N-Phase session
- self.session.list - List all sessions
- self.session.{id}.manifest - Get session details
- self.session.{id}.advance - Advance phase (UNDERSTAND→ACT→REFLECT)
- self.session.{id}.checkpoint - Create checkpoint for rollback
- self.session.{id}.restore - Restore from checkpoint
- self.session.{id}.handle.create - Add AGENTESE handle
- self.session.{id}.handle.list - List handles
- self.session.{id}.ledger - Get phase transition audit trail
- self.session.{id}.detect - Detect phase signal from LLM output
- self.session.{id}.entropy - Record entropy expenditure

N-Phase tracks the SENSE→ACT→REFLECT cycle for coding sessions,
with checkpoints for safe experimentation and rollback.

AGENTESE: self.session.*

Principle Alignment:
- Composable: Phases compose into cycles
- Ethical: Checkpoint/restore enables safe experimentation
- Joy-Inducing: Phase detection reduces cognitive load
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)

# N-Phase session affordances
NPHASE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "create",
    "list",
    "advance",
    "checkpoint",
    "restore",
    "handle",
    "ledger",
    "detect",
    "entropy",
)


@node(
    "self.session",
    description="N-Phase session management - UNDERSTAND→ACT→REFLECT cycle",
    singleton=True,
)
@dataclass
class NPhaseNode(BaseLogosNode):
    """
    self.session - N-Phase session interface.

    Provides phase-aware session management:
    - Create sessions with 3-phase cycle tracking
    - Advance phases with auto-checkpoint
    - Detect phase transitions from LLM output
    - Handle acquisition for AGENTESE paths
    """

    _handle: str = "self.session"

    # Phase detector (lazy-loaded)
    _detector: Any = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_detector(self) -> Any:
        """Lazy-load phase detector."""
        if self._detector is None:
            try:
                from protocols.nphase.detector import PhaseDetector

                self._detector = PhaseDetector()
            except ImportError:
                logger.warning("PhaseDetector not available")
        return self._detector

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """N-Phase affordances available to all archetypes."""
        return NPHASE_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View N-Phase session status."""
        try:
            from protocols.nphase.session import list_sessions

            sessions = list_sessions()
            return BasicRendering(
                summary="N-Phase Sessions",
                content=(
                    f"Active sessions: {len(sessions)}\n"
                    "Phase cycle: UNDERSTAND → ACT → REFLECT → (repeat)\n\n"
                    "Use create to start a new session, advance to progress phases."
                ),
                metadata={
                    "affordances": list(NPHASE_AFFORDANCES),
                    "active_sessions": len(sessions),
                    "phases": ["UNDERSTAND", "ACT", "REFLECT"],
                },
            )
        except ImportError:
            return BasicRendering(
                summary="N-Phase Sessions",
                content="N-Phase module not available.",
                metadata={"error": "nphase not installed"},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle nphase-specific aspects."""
        match aspect:
            case "create":
                return await self._create_session(observer, **kwargs)
            case "list":
                return await self._list_sessions(observer, **kwargs)
            case "advance":
                return await self._advance_phase(observer, **kwargs)
            case "checkpoint":
                return await self._create_checkpoint(observer, **kwargs)
            case "restore":
                return await self._restore_checkpoint(observer, **kwargs)
            case "handle":
                # Handle sub-aspect: handle.create, handle.list
                sub_aspect = kwargs.pop("sub_aspect", "list")
                if sub_aspect == "create":
                    return await self._add_handle(observer, **kwargs)
                else:
                    return await self._list_handles(observer, **kwargs)
            case "ledger":
                return await self._get_ledger(observer, **kwargs)
            case "detect":
                return await self._detect_phase(observer, **kwargs)
            case "entropy":
                return await self._spend_entropy(observer, **kwargs)
            case "archive":
                return await self._delete_session(observer, **kwargs)
            case "checkpoints":
                return await self._list_checkpoints(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Create a new N-Phase session",
        examples=["self.session.create[title='Feature Implementation']"],
    )
    async def _create_session(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new N-Phase session.

        Args:
            title: Session title (optional)
            metadata: Additional metadata dict (optional)

        Returns:
            Session details with id, current_phase, etc.
        """
        title = kwargs.get("title", "")
        metadata = kwargs.get("metadata", {})

        try:
            from protocols.nphase.session import create_session

            session = create_session(title=title, metadata=metadata)
            summary = session.summary()

            return {
                "id": summary["id"],
                "title": summary["title"],
                "current_phase": summary["current_phase"],
                "cycle_count": summary["cycle_count"],
                "checkpoint_count": summary["checkpoint_count"],
                "handle_count": summary["handle_count"],
                "ledger_count": summary["ledger_count"],
                "entropy_spent": summary["entropy_spent"],
                "created_at": summary["created_at"],
                "last_touched": summary["last_touched"],
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="List all N-Phase sessions",
        examples=["self.session.list", "self.session.list[limit=10]"],
    )
    async def _list_sessions(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List all N-Phase sessions.

        Args:
            limit: Max sessions to return (default: 20)
            offset: Pagination offset (default: 0)

        Returns:
            List of sessions with total count
        """
        limit = kwargs.get("limit", 20)
        offset = kwargs.get("offset", 0)

        try:
            from protocols.nphase.session import list_sessions

            sessions = list_sessions()
            total = len(sessions)
            paginated = sessions[offset : offset + limit]

            return {
                "sessions": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "current_phase": s.current_phase.name,
                        "cycle_count": s.cycle_count,
                        "checkpoint_count": len(s.checkpoints),
                        "handle_count": len(s.handles),
                        "ledger_count": len(s.ledger),
                        "entropy_spent": s.entropy_spent,
                        "created_at": s.created_at.isoformat(),
                        "last_touched": s.last_touched.isoformat(),
                    }
                    for s in paginated
                ],
                "total": total,
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}", "sessions": [], "total": 0}
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return {"error": str(e), "sessions": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="Get session details by ID",
        examples=["self.session.{id}.manifest"],
    )
    async def _get_session(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get session details (called via manifest for specific session)."""
        session_id = kwargs.get("session_id")
        if not session_id:
            return {"error": "session_id required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            summary = session.summary()
            return {
                "id": summary["id"],
                "title": summary["title"],
                "current_phase": summary["current_phase"],
                "cycle_count": summary["cycle_count"],
                "checkpoint_count": summary["checkpoint_count"],
                "handle_count": summary["handle_count"],
                "ledger_count": summary["ledger_count"],
                "entropy_spent": summary["entropy_spent"],
                "created_at": summary["created_at"],
                "last_touched": summary["last_touched"],
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Delete an N-Phase session",
        examples=["self.session.{id}.archive"],
    )
    async def _delete_session(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Delete a session."""
        session_id = kwargs.get("session_id")
        if not session_id:
            return {"error": "session_id required"}

        try:
            from protocols.nphase.session import delete_session

            if not delete_session(session_id):
                return {"error": "Session not found"}

            return {"deleted": True, "session_id": session_id}
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Advance session to next phase",
        examples=["self.session.{id}.advance", "self.session.{id}.advance[target_phase='ACT']"],
    )
    async def _advance_phase(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Advance session to next phase.

        Args:
            session_id: Target session ID
            target_phase: Target phase (UNDERSTAND, ACT, REFLECT). If None, advances to next.
            payload: Reason or context for transition
            auto_checkpoint: Create checkpoint before advancing (default: True)

        Returns:
            Transition details with from_phase, to_phase, cycle_count
        """
        session_id = kwargs.get("session_id")
        target_phase_str = kwargs.get("target_phase")
        payload = kwargs.get("payload")
        auto_checkpoint = kwargs.get("auto_checkpoint", True)

        if not session_id:
            return {"error": "session_id required"}

        try:
            from protocols.nphase.operad import NPhase
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            # Parse target phase
            target = None
            if target_phase_str:
                try:
                    target = NPhase[target_phase_str.upper()]
                except KeyError:
                    return {
                        "error": f"Invalid phase: {target_phase_str}. Valid: UNDERSTAND, ACT, REFLECT"
                    }

            from_phase = session.current_phase

            # Auto-checkpoint if requested
            checkpoint_id = None
            if auto_checkpoint:
                cp = session.checkpoint({"trigger": "advance", "reason": "phase_boundary"})
                checkpoint_id = cp.id

            try:
                entry = session.advance_phase(
                    target=target,
                    payload=payload,
                    auto_checkpoint=False,  # Already did it
                )
            except ValueError as e:
                return {"error": str(e)}

            return {
                "from_phase": from_phase.name,
                "to_phase": entry.to_phase.name,
                "cycle_count": entry.cycle_count,
                "checkpoint_id": checkpoint_id,
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            logger.error(f"Failed to advance phase: {e}")
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Create a checkpoint for rollback",
        examples=["self.session.{id}.checkpoint[metadata={'reason': 'before risky op'}]"],
    )
    async def _create_checkpoint(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a checkpoint at current state.

        Args:
            session_id: Target session ID
            metadata: Checkpoint metadata dict

        Returns:
            Checkpoint details with id, phase, cycle_count
        """
        session_id = kwargs.get("session_id")
        metadata = kwargs.get("metadata", {})

        if not session_id:
            return {"error": "session_id required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            cp = session.checkpoint(metadata)

            return {
                "id": cp.id,
                "session_id": session_id,
                "phase": cp.phase.name,
                "cycle_count": cp.cycle_count,
                "handle_count": len(cp.handles),
                "created_at": cp.created_at.isoformat(),
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Restore session from checkpoint",
        examples=["self.session.{id}.restore[checkpoint_id='abc123']"],
    )
    async def _restore_checkpoint(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Restore session from checkpoint.

        Args:
            session_id: Target session ID
            checkpoint_id: Checkpoint ID to restore

        Returns:
            Restored session state
        """
        session_id = kwargs.get("session_id")
        checkpoint_id = kwargs.get("checkpoint_id")

        if not session_id:
            return {"error": "session_id required"}
        if not checkpoint_id:
            return {"error": "checkpoint_id required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            try:
                session.restore(checkpoint_id)
            except ValueError as e:
                return {"error": str(e)}

            summary = session.summary()
            return {
                "id": summary["id"],
                "title": summary["title"],
                "current_phase": summary["current_phase"],
                "cycle_count": summary["cycle_count"],
                "checkpoint_count": summary["checkpoint_count"],
                "handle_count": summary["handle_count"],
                "ledger_count": summary["ledger_count"],
                "entropy_spent": summary["entropy_spent"],
                "created_at": summary["created_at"],
                "last_touched": summary["last_touched"],
                "restored_from": checkpoint_id,
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Add an AGENTESE handle to session",
        examples=["self.session.{id}.handle.create[path='world.file.manifest', content={...}]"],
    )
    async def _add_handle(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add an AGENTESE handle to the session.

        Args:
            session_id: Target session ID
            path: AGENTESE path
            content: Handle content

        Returns:
            Handle details with path, phase, created_at
        """
        session_id = kwargs.get("session_id")
        path = kwargs.get("path")
        content = kwargs.get("content")

        if not session_id:
            return {"error": "session_id required"}
        if not path:
            return {"error": "path required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            handle = session.add_handle(path, content)

            return {
                "path": handle.path,
                "phase": handle.phase.name,
                "created_at": handle.created_at.isoformat(),
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="List handles for a session",
        examples=[
            "self.session.{id}.handle.list",
            "self.session.{id}.handle.list[phase='UNDERSTAND']",
        ],
    )
    async def _list_handles(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List handles for a session.

        Args:
            session_id: Target session ID
            phase: Filter by phase (optional)

        Returns:
            List of handles with total count
        """
        session_id = kwargs.get("session_id")
        phase_str = kwargs.get("phase")

        if not session_id:
            return {"error": "session_id required", "handles": [], "total": 0}

        try:
            from protocols.nphase.operad import NPhase
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found", "handles": [], "total": 0}

            if phase_str:
                try:
                    target_phase = NPhase[phase_str.upper()]
                    handles = session.get_handles_for_phase(target_phase)
                except KeyError:
                    return {"error": f"Invalid phase: {phase_str}", "handles": [], "total": 0}
            else:
                handles = session.handles

            return {
                "handles": [
                    {
                        "path": h.path,
                        "phase": h.phase.name,
                        "content": h.content,
                        "created_at": h.created_at.isoformat(),
                    }
                    for h in handles
                ],
                "total": len(handles),
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}", "handles": [], "total": 0}
        except Exception as e:
            return {"error": str(e), "handles": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="List checkpoints for a session",
        examples=["self.session.{id}.checkpoints"],
    )
    async def _list_checkpoints(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """List checkpoints for a session."""
        session_id = kwargs.get("session_id")

        if not session_id:
            return {"error": "session_id required", "checkpoints": [], "total": 0}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found", "checkpoints": [], "total": 0}

            return {
                "checkpoints": [cp.to_dict() for cp in session.checkpoints],
                "total": len(session.checkpoints),
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}", "checkpoints": [], "total": 0}
        except Exception as e:
            return {"error": str(e), "checkpoints": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session")],
        help="Get phase transition ledger",
        examples=["self.session.{id}.ledger"],
    )
    async def _get_ledger(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get phase transition ledger (audit trail).

        Args:
            session_id: Target session ID

        Returns:
            List of ledger entries with total count
        """
        session_id = kwargs.get("session_id")

        if not session_id:
            return {"error": "session_id required", "ledger": [], "total": 0}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found", "ledger": [], "total": 0}

            return {
                "ledger": [entry.to_dict() for entry in session.ledger],
                "total": len(session.ledger),
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}", "ledger": [], "total": 0}
        except Exception as e:
            return {"error": str(e), "ledger": [], "total": 0}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("llm_output")],
        help="Detect phase signal from LLM output",
        examples=[
            "self.session.{id}.detect[output='Research complete. ⟿[ACT]', auto_advance=true]"
        ],
    )
    async def _detect_phase(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Detect phase signal from LLM output.

        Args:
            session_id: Target session ID
            output: LLM output to analyze
            auto_advance: Auto-advance if high confidence signal (default: False)

        Returns:
            Detection result with action, target_phase, confidence
        """
        session_id = kwargs.get("session_id")
        output = kwargs.get("output")
        auto_advance = kwargs.get("auto_advance", False)

        if not session_id:
            return {"error": "session_id required"}
        if not output:
            return {"error": "output required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            detector = self._get_detector()
            if detector is None:
                return {"error": "Phase detector not available"}

            signal = detector.detect(output, session.current_phase)
            auto_advanced = False

            # Auto-advance if requested and signal is high confidence
            if auto_advance and signal.should_auto_advance and signal.target_phase:
                try:
                    session.advance_phase(signal.target_phase, payload="auto-detected")
                    auto_advanced = True
                except ValueError:
                    pass  # Invalid transition

            return {
                "action": signal.action.name,
                "target_phase": signal.target_phase.name if signal.target_phase else None,
                "confidence": signal.confidence,
                "reason": signal.reason,
                "auto_advanced": auto_advanced,
                "current_phase": session.current_phase.name,
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session")],
        help="Record entropy expenditure",
        examples=["self.session.{id}.entropy[category='llm', amount=100]"],
    )
    async def _spend_entropy(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Record entropy expenditure.

        Args:
            session_id: Target session ID
            category: Entropy category (e.g., 'llm', 'io')
            amount: Amount to spend

        Returns:
            Updated entropy totals
        """
        session_id = kwargs.get("session_id")
        category = kwargs.get("category")
        amount = kwargs.get("amount")

        if not session_id:
            return {"error": "session_id required"}
        if not category:
            return {"error": "category required"}
        if amount is None:
            return {"error": "amount required"}

        try:
            from protocols.nphase.session import get_session

            session = get_session(session_id)
            if not session:
                return {"error": "Session not found"}

            session.spend_entropy(category, float(amount))

            return {
                "category": category,
                "amount": amount,
                "total": session.entropy_spent,
            }
        except ImportError as e:
            return {"error": f"N-Phase module not available: {e}"}
        except Exception as e:
            return {"error": str(e)}


# Factory function
def create_nphase_node() -> NPhaseNode:
    """Create an NPhaseNode instance."""
    return NPhaseNode()


__all__ = [
    "NPhaseNode",
    "NPHASE_AFFORDANCES",
    "create_nphase_node",
]
