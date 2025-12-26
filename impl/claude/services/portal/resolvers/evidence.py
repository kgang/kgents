"""
EvidenceResolver: Resolver for evidence: resources.

Resolves Evidence bundles with Bayesian confidence.

Philosophy:
    "Evidence accumulates. Confidence emerges. Stopping is principled."

See: spec/protocols/portal-resource-system.md §5.6
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..resolver import ResolvedResource
from ..uri import PortalURI

if TYPE_CHECKING:
    from services.chat.evidence import ChatEvidence
    from services.chat.session import ChatSession


class EvidenceResolver:
    """
    Resolver for evidence: resources.

    Handles:
    - evidence:session-abc123    → Evidence bundle with Bayesian state

    Dependencies:
        session_store: Storage for ChatSession instances
    """

    resource_type = "evidence"

    def __init__(self, session_store: Any = None) -> None:
        """
        Initialize EvidenceResolver.

        Args:
            session_store: Storage provider for chat sessions
        """
        self.session_store = session_store

    def can_resolve(self, uri: PortalURI) -> bool:
        """Check if this resolver can handle the URI."""
        return uri.resource_type == self.resource_type

    async def resolve(self, uri: PortalURI, observer: Any = None) -> ResolvedResource:
        """
        Resolve Evidence bundle.

        Args:
            uri: Parsed portal URI
            observer: Optional observer for access control

        Returns:
            ResolvedResource with evidence data
        """
        session_id = uri.resource_path

        # Fetch session
        session = await self._get_session(session_id)
        if session is None:
            return ResolvedResource(
                uri=uri.render(),
                resource_type=self.resource_type,
                exists=False,
                title="Evidence Not Found",
                preview=f"Session not found: {session_id}",
                content=None,
                actions=[],
                metadata={"error": "session_not_found"},
            )

        evidence = session.evidence
        return self._resolve_evidence(uri, evidence, session_id)

    def _resolve_evidence(
        self, uri: PortalURI, evidence: ChatEvidence, session_id: str
    ) -> ResolvedResource:
        """Resolve Evidence to resource."""
        confidence_pct = int(evidence.confidence * 100)
        observations = evidence.prior.alpha + evidence.prior.beta - 2  # Subtract initial priors

        return ResolvedResource(
            uri=uri.render(),
            resource_type=self.resource_type,
            exists=True,
            title=f"Evidence: {session_id}",
            preview=f"Confidence: {confidence_pct}%",
            content={
                "prior": {
                    "alpha": evidence.prior.alpha,
                    "beta": evidence.prior.beta,
                    "mean": evidence.prior.mean(),
                    "variance": evidence.prior.variance(),
                },
                "confidence": evidence.confidence,
                "should_stop": evidence.should_stop,
                "observations": observations,
                "tools_succeeded": evidence.tools_succeeded,
                "tools_failed": evidence.tools_failed,
                "ashc_equivalence": evidence.ashc_equivalence,
            },
            actions=["expand", "view_posterior"],
            metadata={
                "session_id": session_id,
                "confidence": evidence.confidence,
                "should_stop": evidence.should_stop,
                "observations": observations,
            },
        )

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


__all__ = ["EvidenceResolver"]
