"""
Tests for Semaphore AGENTESE paths.

Tests for self.semaphore.* and world.purgatory.* paths.
These paths integrate the Agent Semaphore system with AGENTESE.

Tests verify:
1. self.semaphore.pending returns empty list without purgatory
2. self.semaphore.yield creates token when purgatory configured
3. self.semaphore.status returns token details
4. world.purgatory.list returns pending tokens
5. world.purgatory.resolve requires token_id and human_input
6. world.purgatory.cancel marks token as cancelled
7. world.purgatory.inspect returns full token details
8. world.purgatory.void_expired voids past-deadline tokens
9. Affordance filtering (admin vs non-admin)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, cast

import pytest

from agents.flux.semaphore import Purgatory, SemaphoreReason, SemaphoreToken
from bootstrap.umwelt import Umwelt

from ..self_ import (
    SelfContextResolver,
    SemaphoreNode,
    create_self_resolver,
)
from ..world import (
    PurgatoryNode,
    WorldContextResolver,
    create_world_resolver,
)

# === Test Fixtures ===


class MockDNA:
    """Mock DNA for testing."""

    def __init__(
        self,
        name: str = "test",
        archetype: str = "default",
        capabilities: tuple[str, ...] = (),
    ) -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities = capabilities


class MockUmwelt:
    """Mock Umwelt for testing."""

    def __init__(
        self,
        archetype: str = "default",
        name: str = "test",
        capabilities: tuple[str, ...] = (),
    ) -> None:
        self.dna = MockDNA(name=name, archetype=archetype, capabilities=capabilities)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}


@pytest.fixture
def observer() -> Umwelt[Any, Any]:
    """Default observer."""
    return cast(Umwelt[Any, Any], MockUmwelt())


@pytest.fixture
def admin_observer() -> Umwelt[Any, Any]:
    """Admin observer with full purgatory access."""
    return cast(Umwelt[Any, Any], MockUmwelt(archetype="admin", name="admin"))


@pytest.fixture
def developer_observer() -> Umwelt[Any, Any]:
    """Developer observer with full purgatory access."""
    return cast(Umwelt[Any, Any], MockUmwelt(archetype="developer", name="developer"))


@pytest.fixture
def poet_observer() -> Umwelt[Any, Any]:
    """Poet observer with limited purgatory access."""
    return cast(Umwelt[Any, Any], MockUmwelt(archetype="poet", name="poet"))


@pytest.fixture
def purgatory() -> Purgatory:
    """Fresh purgatory instance."""
    return Purgatory()


@pytest.fixture
def self_resolver(purgatory: Purgatory) -> SelfContextResolver:
    """Self context resolver with purgatory."""
    return create_self_resolver(purgatory=purgatory)


@pytest.fixture
def world_resolver(purgatory: Purgatory) -> WorldContextResolver:
    """World context resolver with purgatory."""
    return create_world_resolver(purgatory=purgatory)


# === self.semaphore.pending Tests ===


class TestSelfSemaphorePending:
    """Tests for self.semaphore.pending path."""

    @pytest.mark.asyncio
    async def test_pending_returns_empty_without_purgatory(
        self,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Without purgatory, pending returns empty list."""
        # Create resolver without purgatory
        resolver = create_self_resolver(purgatory=None)
        node = resolver.resolve("semaphore", [])

        result = await node._invoke_aspect("pending", observer)

        assert result == []

    @pytest.mark.asyncio
    async def test_pending_returns_empty_with_no_tokens(
        self,
        self_resolver: SelfContextResolver,
        observer: Umwelt[Any, Any],
    ) -> None:
        """With empty purgatory, pending returns empty list."""
        node = self_resolver.resolve("semaphore", [])

        result = await node._invoke_aspect("pending", observer)

        assert result == []

    @pytest.mark.asyncio
    async def test_pending_returns_pending_tokens(
        self,
        self_resolver: SelfContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Returns list of pending token summaries."""
        # Add tokens to purgatory
        token1: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-test1111",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Approve action 1?",
            options=["Yes", "No"],
            severity="warning",
        )
        token2: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-test2222",
            reason=SemaphoreReason.CONTEXT_REQUIRED,
            prompt="What environment?",
        )
        await purgatory.save(token1)
        await purgatory.save(token2)

        node = self_resolver.resolve("semaphore", [])
        result = await node._invoke_aspect("pending", observer)

        assert len(result) == 2
        ids = [t["id"] for t in result]
        assert "sem-test1111" in ids
        assert "sem-test2222" in ids

    @pytest.mark.asyncio
    async def test_pending_excludes_resolved_tokens(
        self,
        self_resolver: SelfContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Resolved tokens are not in pending list."""
        token: SemaphoreToken[Any] = SemaphoreToken(id="sem-test3333")
        await purgatory.save(token)
        await purgatory.resolve("sem-test3333", "resolved")

        node = self_resolver.resolve("semaphore", [])
        result = await node._invoke_aspect("pending", observer)

        assert len(result) == 0


# === self.semaphore.yield Tests ===


class TestSelfSemaphoreYield:
    """Tests for self.semaphore.yield path."""

    @pytest.mark.asyncio
    async def test_yield_without_purgatory_returns_error(
        self,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Without purgatory, yield returns error."""
        resolver = create_self_resolver(purgatory=None)
        node = resolver.resolve("semaphore", [])

        result = await node._invoke_aspect("yield", observer, prompt="Test?")

        assert "error" in result
        assert "not configured" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_yield_creates_token_with_purgatory(
        self,
        self_resolver: SelfContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
    ) -> None:
        """With purgatory, yield creates and saves token."""
        node = self_resolver.resolve("semaphore", [])

        result = await node._invoke_aspect(
            "yield",
            observer,
            reason="approval_needed",
            prompt="Approve this?",
            options=["Yes", "No"],
            severity="warning",
        )

        assert "token_id" in result
        assert result["status"] == "pending"
        assert result["reason"] == "approval_needed"
        assert result["prompt"] == "Approve this?"

        # Verify token is in purgatory
        token = purgatory.get(result["token_id"])
        assert token is not None
        assert token.prompt == "Approve this?"

    @pytest.mark.asyncio
    async def test_yield_with_deadline(
        self,
        self_resolver: SelfContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Yield with deadline creates token with deadline."""
        node = self_resolver.resolve("semaphore", [])
        future_deadline = (datetime.now() + timedelta(hours=1)).isoformat()

        result = await node._invoke_aspect(
            "yield",
            observer,
            prompt="Approve within 1 hour?",
            deadline=future_deadline,
        )

        token = purgatory.get(result["token_id"])
        assert token is not None
        assert token.deadline is not None


# === self.semaphore.status Tests ===


class TestSelfSemaphoreStatus:
    """Tests for self.semaphore.status path."""

    @pytest.mark.asyncio
    async def test_status_without_token_id_returns_error(
        self,
        self_resolver: SelfContextResolver,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Status without token_id returns error."""
        node = self_resolver.resolve("semaphore", [])

        result = await node._invoke_aspect("status", observer)

        assert "error" in result
        assert "token_id required" in result["error"]

    @pytest.mark.asyncio
    async def test_status_for_unknown_token(
        self,
        self_resolver: SelfContextResolver,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Status for unknown token returns error."""
        node = self_resolver.resolve("semaphore", [])

        result = await node._invoke_aspect(
            "status",
            observer,
            token_id="sem-nonexistent",
        )

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_status_returns_token_details(
        self,
        self_resolver: SelfContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Status returns full token details."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-test4444",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Approve?",
            severity="critical",
        )
        await purgatory.save(token)

        node = self_resolver.resolve("semaphore", [])
        result = await node._invoke_aspect(
            "status",
            observer,
            token_id="sem-test4444",
        )

        assert result["token_id"] == "sem-test4444"
        assert result["status"] == "pending"
        assert result["reason"] == "approval_needed"
        assert result["prompt"] == "Approve?"
        assert result["severity"] == "critical"


# === world.purgatory.list Tests ===


class TestWorldPurgatoryList:
    """Tests for world.purgatory.list path."""

    @pytest.mark.asyncio
    async def test_list_returns_empty_without_purgatory(
        self,
        observer: Umwelt[Any, Any],
    ) -> None:
        """Without purgatory, list returns empty."""
        resolver = create_world_resolver(purgatory=None)
        node = resolver.resolve("purgatory", [])

        result = await node._invoke_aspect("list", observer)

        assert result == []

    @pytest.mark.asyncio
    async def test_list_returns_pending_tokens(
        self,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """List returns all pending tokens."""
        token1: SemaphoreToken[Any] = SemaphoreToken(id="sem-world1")
        token2: SemaphoreToken[Any] = SemaphoreToken(id="sem-world2")
        await purgatory.save(token1)
        await purgatory.save(token2)

        node = world_resolver.resolve("purgatory", [])
        result = await node._invoke_aspect("list", admin_observer)

        assert len(result) == 2


# === world.purgatory.resolve Tests ===


class TestWorldPurgatoryResolve:
    """Tests for world.purgatory.resolve path."""

    @pytest.mark.asyncio
    async def test_resolve_requires_token_id(
        self,
        world_resolver: WorldContextResolver,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Resolve without token_id returns error."""
        node = world_resolver.resolve("purgatory", [])

        result = await node._invoke_aspect(
            "resolve",
            admin_observer,
            human_input="approved",
        )

        assert "error" in result
        assert "token_id required" in result["error"]

    @pytest.mark.asyncio
    async def test_resolve_requires_human_input(
        self,
        world_resolver: WorldContextResolver,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Resolve without human_input returns error."""
        node = world_resolver.resolve("purgatory", [])

        result = await node._invoke_aspect(
            "resolve",
            admin_observer,
            token_id="sem-test",
        )

        assert "error" in result
        assert "human_input required" in result["error"]

    @pytest.mark.asyncio
    async def test_resolve_returns_success(
        self,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Successful resolve returns status."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-resolve1",
            frozen_state=b"state",
        )
        await purgatory.save(token)

        node = world_resolver.resolve("purgatory", [])
        result = await node._invoke_aspect(
            "resolve",
            admin_observer,
            token_id="sem-resolve1",
            human_input="approved",
        )

        assert result["status"] == "resolved"
        assert result["token_id"] == "sem-resolve1"
        assert result["has_reentry"] is True

        # Verify token is no longer pending
        assert len(purgatory.list_pending()) == 0


# === world.purgatory.cancel Tests ===


class TestWorldPurgatoryCancel:
    """Tests for world.purgatory.cancel path."""

    @pytest.mark.asyncio
    async def test_cancel_requires_token_id(
        self,
        world_resolver: WorldContextResolver,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Cancel without token_id returns error."""
        node = world_resolver.resolve("purgatory", [])

        result = await node._invoke_aspect("cancel", admin_observer)

        assert "error" in result

    @pytest.mark.asyncio
    async def test_cancel_marks_token_cancelled(
        self,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Cancel marks token as cancelled."""
        token: SemaphoreToken[Any] = SemaphoreToken(id="sem-cancel1")
        await purgatory.save(token)

        node = world_resolver.resolve("purgatory", [])
        result = await node._invoke_aspect(
            "cancel",
            admin_observer,
            token_id="sem-cancel1",
        )

        assert result["status"] == "cancelled"
        assert token.is_cancelled


# === world.purgatory.inspect Tests ===


class TestWorldPurgatoryInspect:
    """Tests for world.purgatory.inspect path."""

    @pytest.mark.asyncio
    async def test_inspect_requires_token_id(
        self,
        world_resolver: WorldContextResolver,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Inspect without token_id returns error."""
        node = world_resolver.resolve("purgatory", [])

        result = await node._invoke_aspect("inspect", admin_observer)

        assert "error" in result

    @pytest.mark.asyncio
    async def test_inspect_returns_full_details(
        self,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Inspect returns full token details."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-inspect1",
            reason=SemaphoreReason.SENSITIVE_ACTION,
            prompt="Delete all records?",
            options=["Approve", "Reject"],
            severity="critical",
            escalation="manager@example.com",
        )
        await purgatory.save(token)

        node = world_resolver.resolve("purgatory", [])
        result = await node._invoke_aspect(
            "inspect",
            admin_observer,
            token_id="sem-inspect1",
        )

        assert result["token_id"] == "sem-inspect1"
        assert result["status"] == "pending"
        assert result["reason"] == "sensitive_action"
        assert result["prompt"] == "Delete all records?"
        assert result["options"] == ["Approve", "Reject"]
        assert result["severity"] == "critical"
        assert result["escalation"] == "manager@example.com"


# === world.purgatory.void_expired Tests ===


class TestWorldPurgatoryVoidExpired:
    """Tests for world.purgatory.void_expired path."""

    @pytest.mark.asyncio
    async def test_void_expired_without_purgatory(
        self,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Without purgatory, void_expired returns error."""
        resolver = create_world_resolver(purgatory=None)
        node = resolver.resolve("purgatory", [])

        result = await node._invoke_aspect("void_expired", admin_observer)

        assert "error" in result

    @pytest.mark.asyncio
    async def test_void_expired_voids_past_deadline_tokens(
        self,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Voids tokens with past deadlines."""
        # Token with past deadline
        past_deadline = datetime.now() - timedelta(hours=1)
        expired_token: SemaphoreToken[Any] = SemaphoreToken(
            id="sem-expired1",
            deadline=past_deadline,
        )
        # Token without deadline
        no_deadline_token: SemaphoreToken[Any] = SemaphoreToken(id="sem-nodeadline")
        await purgatory.save(expired_token)
        await purgatory.save(no_deadline_token)

        node = world_resolver.resolve("purgatory", [])
        result = await node._invoke_aspect("void_expired", admin_observer)

        assert result["status"] == "completed"
        assert result["voided_count"] == 1
        assert "sem-expired1" in result["voided_ids"]

        # Verify states
        assert expired_token.is_voided
        assert no_deadline_token.is_pending


# === Affordance Filtering Tests ===


class TestAffordanceFiltering:
    """Tests for affordance filtering based on archetype."""

    def test_admin_has_full_purgatory_access(self) -> None:
        """Admin archetype has all purgatory affordances."""
        node = PurgatoryNode()
        affordances = node._get_affordances_for_archetype("admin")

        assert "list" in affordances
        assert "resolve" in affordances
        assert "cancel" in affordances
        assert "inspect" in affordances
        assert "void_expired" in affordances

    def test_developer_has_full_purgatory_access(self) -> None:
        """Developer archetype has all purgatory affordances."""
        node = PurgatoryNode()
        affordances = node._get_affordances_for_archetype("developer")

        assert "list" in affordances
        assert "resolve" in affordances
        assert "cancel" in affordances
        assert "inspect" in affordances
        assert "void_expired" in affordances

    def test_poet_has_limited_purgatory_access(self) -> None:
        """Non-admin archetypes have read-only purgatory access."""
        node = PurgatoryNode()
        affordances = node._get_affordances_for_archetype("poet")

        assert "list" in affordances
        assert "inspect" in affordances
        assert "resolve" not in affordances
        assert "cancel" not in affordances
        assert "void_expired" not in affordances

    def test_default_has_limited_purgatory_access(self) -> None:
        """Default archetype has read-only purgatory access."""
        node = PurgatoryNode()
        affordances = node._get_affordances_for_archetype("default")

        assert "list" in affordances
        assert "inspect" in affordances
        assert "resolve" not in affordances

    def test_semaphore_node_affordances(self) -> None:
        """SemaphoreNode has consistent affordances for all archetypes."""
        node = SemaphoreNode()

        for archetype in ["admin", "developer", "poet", "default"]:
            affordances = node._get_affordances_for_archetype(archetype)
            assert "pending" in affordances
            assert "yield" in affordances
            assert "status" in affordances


# === Integration Tests ===


class TestSemaphorePathIntegration:
    """Integration tests for semaphore paths."""

    @pytest.mark.asyncio
    async def test_full_workflow_via_paths(
        self,
        self_resolver: SelfContextResolver,
        world_resolver: WorldContextResolver,
        purgatory: Purgatory,
        observer: Umwelt[Any, Any],
        admin_observer: Umwelt[Any, Any],
    ) -> None:
        """Complete workflow: yield -> list -> resolve."""
        # 1. Agent yields a semaphore via self.semaphore.yield
        self_node = self_resolver.resolve("semaphore", [])
        yield_result = await self_node._invoke_aspect(
            "yield",
            observer,
            reason="approval_needed",
            prompt="Proceed with operation?",
            options=["Approve", "Reject"],
            severity="warning",
        )

        assert "token_id" in yield_result
        token_id = yield_result["token_id"]

        # 2. Human lists pending via world.purgatory.list
        world_node = world_resolver.resolve("purgatory", [])
        list_result = await world_node._invoke_aspect("list", admin_observer)

        assert len(list_result) == 1
        assert list_result[0]["id"] == token_id

        # 3. Human inspects via world.purgatory.inspect
        inspect_result = await world_node._invoke_aspect(
            "inspect",
            admin_observer,
            token_id=token_id,
        )

        assert inspect_result["prompt"] == "Proceed with operation?"
        assert inspect_result["options"] == ["Approve", "Reject"]

        # 4. Human resolves via world.purgatory.resolve
        resolve_result = await world_node._invoke_aspect(
            "resolve",
            admin_observer,
            token_id=token_id,
            human_input="Approve",
        )

        assert resolve_result["status"] == "resolved"

        # 5. Verify no more pending
        final_list = await world_node._invoke_aspect("list", admin_observer)
        assert len(final_list) == 0
