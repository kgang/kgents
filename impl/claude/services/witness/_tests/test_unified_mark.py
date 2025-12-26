"""
Tests for Unified Mark Type with Domain Support.

Verifies:
- Mark immutability (frozen=True)
- Domain field works across all domains
- Serialization preserves domain
- Mark.create() factory
"""

import pytest
from datetime import datetime, timezone

from services.witness import (
    Mark,
    MarkId,
    Stimulus,
    Response,
    UmweltSnapshot,
    WitnessDomain,
    generate_mark_id,
)


class TestMarkDomain:
    """Tests for domain field on Mark."""

    def test_mark_default_domain(self) -> None:
        """Default domain is 'system'."""
        mark = Mark(origin="test")
        assert mark.domain == "system"

    def test_mark_navigation_domain(self) -> None:
        """Can create mark with navigation domain."""
        mark = Mark(
            origin="navigator",
            domain="navigation",
            stimulus=Stimulus(kind="route", content="Navigate to /chat"),
            response=Response(kind="navigation", content="Navigated to /chat"),
        )
        assert mark.domain == "navigation"
        assert mark.origin == "navigator"

    def test_mark_portal_domain(self) -> None:
        """Can create mark with portal domain."""
        mark = Mark(
            origin="context_perception",
            domain="portal",
            stimulus=Stimulus(kind="portal", content="Expand imports"),
            response=Response(kind="exploration", content="Expanded to depth 2"),
        )
        assert mark.domain == "portal"

    def test_mark_chat_domain(self) -> None:
        """Can create mark with chat domain."""
        mark = Mark(
            origin="chat_session",
            domain="chat",
            stimulus=Stimulus(kind="prompt", content="Hello"),
            response=Response(kind="text", content="Hi there!"),
        )
        assert mark.domain == "chat"

    def test_mark_edit_domain(self) -> None:
        """Can create mark with edit domain."""
        mark = Mark(
            origin="editor",
            domain="edit",
            stimulus=Stimulus(kind="kblock", content="Edit K-Block abc123"),
            response=Response(kind="mutation", content="K-Block updated"),
        )
        assert mark.domain == "edit"


class TestMarkImmutability:
    """Tests for Mark immutability (frozen=True)."""

    def test_mark_is_frozen(self) -> None:
        """Cannot modify Mark after creation."""
        mark = Mark(origin="test", domain="system")

        with pytest.raises(Exception):  # FrozenInstanceError
            mark.domain = "chat"  # type: ignore

    def test_with_link_preserves_domain(self) -> None:
        """with_link() preserves domain field."""
        from services.witness import MarkLink, LinkRelation

        mark1 = Mark(origin="test", domain="chat")
        mark2 = Mark(origin="test", domain="chat")

        link = MarkLink(source=mark1.id, target=mark2.id, relation=LinkRelation.CAUSES)
        mark2_linked = mark2.with_link(link)

        assert mark2_linked.domain == "chat"
        assert len(mark2_linked.links) == 1

    def test_with_proof_preserves_domain(self) -> None:
        """with_proof() preserves domain field."""
        from services.witness import Proof, EvidenceTier

        mark = Mark(origin="test", domain="portal")
        proof = Proof(
            data="User expanded to depth 3",
            warrant="Depth 3+ indicates deliberate exploration",
            claim="User is actively exploring",
            tier=EvidenceTier.EMPIRICAL,
        )

        mark_with_proof = mark.with_proof(proof)
        assert mark_with_proof.domain == "portal"
        assert mark_with_proof.proof == proof


class TestMarkSerialization:
    """Tests for Mark serialization with domain."""

    def test_to_dict_includes_domain(self) -> None:
        """to_dict() includes domain field."""
        mark = Mark(
            origin="chat",
            domain="chat",
            stimulus=Stimulus(kind="prompt", content="Test"),
            response=Response(kind="text", content="Response"),
        )

        data = mark.to_dict()
        assert "domain" in data
        assert data["domain"] == "chat"

    def test_from_dict_restores_domain(self) -> None:
        """from_dict() restores domain field."""
        mark = Mark(
            origin="portal",
            domain="portal",
            stimulus=Stimulus(kind="portal", content="Expand"),
        )

        data = mark.to_dict()
        restored = Mark.from_dict(data)

        assert restored.domain == "portal"
        assert restored.origin == "portal"

    def test_from_dict_defaults_domain(self) -> None:
        """from_dict() defaults domain to 'system' if missing."""
        data = {
            "id": "mark-abc123",
            "origin": "test",
            "stimulus": {"kind": "test", "content": "test", "source": "test", "metadata": {}},
            "response": {"kind": "test", "content": "test", "success": True, "metadata": {}},
            "umwelt": {
                "observer_id": "test",
                "role": "test",
                "capabilities": [],
                "perceptions": [],
                "trust_level": 0,
            },
            "links": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": None,
            "walk_id": None,
            "proof": None,
            "tags": [],
            "metadata": {},
            # No domain field
        }

        mark = Mark.from_dict(data)
        assert mark.domain == "system"  # Default

    def test_roundtrip_all_domains(self) -> None:
        """Roundtrip serialization works for all domain types."""
        domains = ["navigation", "portal", "chat", "edit", "system"]

        for domain in domains:
            mark = Mark(origin="test", domain=domain)
            data = mark.to_dict()
            restored = Mark.from_dict(data)

            assert restored.domain == domain


class TestMarkFactory:
    """Tests for Mark factory methods."""

    def test_from_thought_creates_mark(self) -> None:
        """from_thought() creates valid Mark."""
        mark = Mark.from_thought(
            content="File changed: test.py",
            source="filesystem",
            tags=("file", "change"),
        )

        assert mark.origin == "witness"  # Default
        assert mark.domain == "system"  # Default
        assert mark.response.content == "File changed: test.py"
        assert "file" in mark.tags

    def test_from_agentese_creates_mark(self) -> None:
        """from_agentese() creates valid Mark."""
        mark = Mark.from_agentese(
            path="self.chat",
            aspect="send",
            response_content="Message sent",
            origin="logos",
        )

        assert mark.origin == "logos"
        assert mark.domain == "system"  # Default
        assert mark.stimulus.kind == "agentese"
        assert "self.chat" in mark.stimulus.content


# =============================================================================
# Integration Tests
# =============================================================================


class TestMarkIntegration:
    """Integration tests for Mark across domains."""

    def test_multi_domain_marks(self) -> None:
        """Can create marks across multiple domains."""
        nav_mark = Mark(origin="nav", domain="navigation")
        portal_mark = Mark(origin="portal", domain="portal")
        chat_mark = Mark(origin="chat", domain="chat")
        edit_mark = Mark(origin="edit", domain="edit")

        marks = [nav_mark, portal_mark, chat_mark, edit_mark]
        domains = [m.domain for m in marks]

        assert set(domains) == {"navigation", "portal", "chat", "edit"}

    def test_mark_with_all_fields(self) -> None:
        """Can create mark with all fields populated."""
        from services.witness import Proof, EvidenceTier, NPhase

        mark = Mark(
            id=generate_mark_id(),
            origin="test",
            domain="chat",
            stimulus=Stimulus(
                kind="prompt",
                content="User message",
                source="user",
                metadata={"session_id": "sess-123"},
            ),
            response=Response(
                kind="text",
                content="Assistant response",
                success=True,
                metadata={"model": "claude-4"},
            ),
            umwelt=UmweltSnapshot(
                observer_id="user-123",
                role="developer",
                capabilities=frozenset({"read", "write"}),
                perceptions=frozenset({"code", "docs"}),
                trust_level=2,
            ),
            phase=NPhase.ACT,
            proof=Proof(
                data="User asked question",
                warrant="Question requires response",
                claim="Response was helpful",
                tier=EvidenceTier.EMPIRICAL,
            ),
            tags=("chat", "helpful"),
            metadata={"turn": 1},
        )

        # Verify all fields preserved
        assert mark.domain == "chat"
        assert mark.origin == "test"
        assert mark.phase == NPhase.ACT
        assert mark.proof is not None
        assert "chat" in mark.tags

        # Verify serialization
        data = mark.to_dict()
        restored = Mark.from_dict(data)
        assert restored.domain == mark.domain
        assert restored.origin == mark.origin
