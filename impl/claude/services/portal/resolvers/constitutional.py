"""
ConstitutionalResolver: Resolver for constitutional: resources.

Resolves constitutional scores with radar visualization data.

Philosophy:
    "Every turn is evaluated. Every score is witnessed. Every principle matters."

See: spec/protocols/portal-resource-system.md §5.3
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..resolver import ResolvedResource
from ..uri import PortalURI

if TYPE_CHECKING:
    from services.chat.reward import PrincipleScore
    from services.chat.session import ChatSession


class ConstitutionalResolver:
    """
    Resolver for constitutional: resources.

    Handles:
    - constitutional:session-abc123           → Session aggregate scores
    - constitutional:session-abc123#turn-5    → Turn-specific scores

    Dependencies:
        session_store: Storage for ChatSession instances
    """

    resource_type = "constitutional"

    def __init__(self, session_store: Any = None) -> None:
        """
        Initialize ConstitutionalResolver.

        Args:
            session_store: Storage provider for chat sessions
        """
        self.session_store = session_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve constitutional scores with radar data.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with constitutional scores
        """
        session_id = uri.resource_path
        turn_number = self._parse_turn_number(uri.fragment) if uri.fragment else None

        # Fetch session
        session = await self._get_session(session_id)
        if session is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Constitutional Scores Not Found",
                preview=f"Session not found: {session_id}",
                content=None,
                actions=[],
                metadata={"error": "session_not_found"},
            )

        # Get scores for turn or aggregate
        if turn_number is not None:
            return self._resolve_turn_scores(uri, session, turn_number)
        else:
            return self._resolve_session_scores(uri, session)

    def _resolve_turn_scores(
        self, uri: PortalURI, session: ChatSession, turn_number: int
    ) -> ResolvedResource:
        """Resolve scores for a specific turn."""
        mark = session.policy_trace.get_mark(turn_number)
        if mark is None or mark.constitutional_scores is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Constitutional Scores Not Found",
                preview=f"No scores for turn {turn_number}",
                content=None,
                actions=[],
                metadata={"error": "scores_not_found"},
            )

        scores = mark.constitutional_scores
        weighted = scores.weighted_total()

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=f"Constitutional Scores: Turn {turn_number}",
            preview=f"Score: {weighted:.1f}",
            content={
                "scores": scores.to_dict(),
                "radar_data": self._to_radar_data(scores),
                "weighted_total": weighted,
                "turn_number": turn_number,
            },
            actions=["expand", "view_radar"],
            metadata={
                "session_id": session.id,
                "turn_number": turn_number,
                "weighted_total": weighted,
            },
        )

    def _resolve_session_scores(self, uri: PortalURI, session: ChatSession) -> ResolvedResource:
        """Resolve aggregate scores for entire session."""
        history = session.get_constitutional_history()

        if not history:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=True,
                title="Constitutional Scores",
                preview="No scores available",
                content={
                    "scores": None,
                    "radar_data": None,
                    "aggregate": None,
                },
                actions=["expand"],
                metadata={
                    "session_id": session.id,
                    "turn_count": session.turn_count,
                    "has_scores": False,
                },
            )

        # Aggregate scores across all turns
        aggregate = self._aggregate_scores(history)
        weighted = aggregate.weighted_total()

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title="Constitutional Scores",
            preview=f"Score: {weighted:.1f} (avg over {len(history)} turns)",
            content={
                "scores": aggregate.to_dict(),
                "radar_data": self._to_radar_data(aggregate),
                "weighted_total": weighted,
                "turn_count": len(history),
                "history": [s.to_dict() for s in history],
            },
            actions=["expand", "view_radar", "view_history"],
            metadata={
                "session_id": session.id,
                "turn_count": len(history),
                "weighted_total": weighted,
                "has_scores": True,
            },
        )

    def _aggregate_scores(self, history: list[PrincipleScore]) -> PrincipleScore:
        """Aggregate scores across multiple turns using mean."""
        from services.chat.reward import PrincipleScore

        if not history:
            return PrincipleScore()

        n = len(history)
        return PrincipleScore(
            tasteful=sum(s.tasteful for s in history) / n,
            curated=sum(s.curated for s in history) / n,
            ethical=sum(s.ethical for s in history) / n,
            joy_inducing=sum(s.joy_inducing for s in history) / n,
            composable=sum(s.composable for s in history) / n,
            heterarchical=sum(s.heterarchical for s in history) / n,
            generative=sum(s.generative for s in history) / n,
        )

    def _to_radar_data(self, scores: PrincipleScore) -> list[dict[str, Any]]:
        """Convert scores to radar chart data format."""
        return [
            {"axis": "Tasteful", "value": scores.tasteful},
            {"axis": "Curated", "value": scores.curated},
            {"axis": "Ethical", "value": scores.ethical},
            {"axis": "Joy-Inducing", "value": scores.joy_inducing},
            {"axis": "Composable", "value": scores.composable},
            {"axis": "Heterarchical", "value": scores.heterarchical},
            {"axis": "Generative", "value": scores.generative},
        ]

    async def _get_session(self, session_id: str) -> ChatSession | None:
        """Fetch session from storage."""
        if self.session_store is None:
            return None

        if hasattr(self.session_store, "get"):
            return await self.session_store.get(session_id)
        elif hasattr(self.session_store, "load"):
            return await self.session_store.load(session_id)
        else:
            return None

    def _parse_turn_number(self, fragment: str | None) -> int | None:
        """Parse turn number from fragment."""
        if not fragment:
            return None

        if fragment.startswith("turn-"):
            try:
                return int(fragment[5:])
            except ValueError:
                return None

        return None


__all__ = ["ConstitutionalResolver"]
