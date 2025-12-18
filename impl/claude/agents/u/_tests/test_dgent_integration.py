"""
Integration tests for U-gent + D-gent sidecar pattern.

These tests verify the sidecar pattern works:
- U-gent stores execution context in D-gent
- State persists across client reconnects
- CAS prevents race conditions
- Namespace isolation for multi-tenant state

For actual integration testing with real D-gent server:
    pytest -m integration --dgent-url http://localhost:8081

AGENTESE: world.ugent.tests.integration
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestUgentDgentIntegration:
    """Integration tests for U-gent + D-gent sidecar."""

    @pytest.mark.asyncio
    async def test_ugent_stores_execution_context(self) -> None:
        """Test U-gent can store execution context in D-gent."""
        from agents.u.state import DgentClient

        # Simulate D-gent responses for a typical execution flow
        responses: list[MagicMock] = []

        # 1. Put execution context
        put_response = MagicMock()
        put_response.status_code = 200
        put_response.json.return_value = {
            "key": "execution:ugent-123",
            "value": {
                "prompt": "Deploy the application",
                "tool_name": "kubectl",
                "status": "pending",
            },
            "version": 1,
            "namespace": "executions",
            "created_at": "2025-12-12T12:00:00",
            "updated_at": "2025-12-12T12:00:00",
        }
        put_response.raise_for_status = MagicMock()
        responses.append(put_response)

        # 2. Update with result
        update_response = MagicMock()
        update_response.status_code = 200
        update_response.json.return_value = {
            "key": "execution:ugent-123",
            "value": {
                "prompt": "Deploy the application",
                "tool_name": "kubectl",
                "status": "completed",
                "result": {"deployed": True},
            },
            "version": 2,
            "namespace": "executions",
            "created_at": "2025-12-12T12:00:00",
            "updated_at": "2025-12-12T12:00:01",
        }
        update_response.raise_for_status = MagicMock()
        responses.append(update_response)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.side_effect = responses
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Store initial execution context
            result = await client.put(
                "execution:ugent-123",
                {
                    "prompt": "Deploy the application",
                    "tool_name": "kubectl",
                    "status": "pending",
                },
                namespace="executions",
            )
            assert result.version == 1
            assert result.value["status"] == "pending"

            # Update with result
            result = await client.put(
                "execution:ugent-123",
                {
                    "prompt": "Deploy the application",
                    "tool_name": "kubectl",
                    "status": "completed",
                    "result": {"deployed": True},
                },
                namespace="executions",
                expected_version=1,
            )
            assert result.version == 2
            assert result.value["status"] == "completed"

    @pytest.mark.asyncio
    async def test_state_survives_client_reconnect(self) -> None:
        """Test state persists across client instances."""
        from agents.u.state import DgentClient

        # Simulate getting previously stored state with a new client
        get_response = MagicMock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "key": "session:previous",
            "value": {"user": "alice", "step": 5},
            "version": 5,
            "namespace": "sessions",
            "created_at": "2025-12-12T10:00:00",
            "updated_at": "2025-12-12T11:00:00",
        }
        get_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = get_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            # Create "new" client (simulating pod restart or reconnection)
            client = DgentClient(base_url="http://localhost:8081")

            # State from previous session should still be accessible
            state = await client.get("session:previous", namespace="sessions")

            assert state is not None
            assert state.value["user"] == "alice"
            assert state.value["step"] == 5
            assert state.version == 5  # Preserves version history

    @pytest.mark.asyncio
    async def test_cas_prevents_race_conditions(self) -> None:
        """Test CAS prevents concurrent update conflicts."""
        from agents.u.state import DgentClient, VersionConflictError

        # Simulate conflict scenario
        conflict_response = MagicMock()
        conflict_response.status_code = 409
        conflict_response.json.return_value = {
            "detail": "Version conflict for executions/counter: expected 1, found 2"
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.return_value = conflict_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Attempt update with stale version (simulating race condition)
            with pytest.raises(VersionConflictError) as exc_info:
                await client.put(
                    "counter",
                    {"count": 10},
                    namespace="executions",
                    expected_version=1,  # Stale: actual version is 2
                )

            assert "conflict" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_namespace_isolation_for_multi_tenant(self) -> None:
        """Test namespace isolation for multi-tenant state."""
        from agents.u.state import DgentClient

        # Response for tenant-a
        tenant_a_response = MagicMock()
        tenant_a_response.status_code = 200
        tenant_a_response.json.return_value = {
            "key": "config",
            "value": {"max_tokens": 1000},
            "version": 1,
            "namespace": "tenant-a",
        }
        tenant_a_response.raise_for_status = MagicMock()

        # Response for tenant-b
        tenant_b_response = MagicMock()
        tenant_b_response.status_code = 200
        tenant_b_response.json.return_value = {
            "key": "config",
            "value": {"max_tokens": 5000},
            "version": 1,
            "namespace": "tenant-b",
        }
        tenant_b_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = [tenant_a_response, tenant_b_response]
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Each tenant has separate configuration
            config_a = await client.get("config", namespace="tenant-a")
            config_b = await client.get("config", namespace="tenant-b")

            assert config_a is not None
            assert config_b is not None
            assert config_a.value["max_tokens"] == 1000
            assert config_b.value["max_tokens"] == 5000
            assert config_a.namespace == "tenant-a"
            assert config_b.namespace == "tenant-b"


class TestUgentExecutionPersistence:
    """Tests for U-gent execution state persistence."""

    @pytest.mark.asyncio
    async def test_full_execution_lifecycle(self) -> None:
        """Test full lifecycle: create -> update -> complete -> retrieve."""
        from agents.u.state import DgentClient

        responses = []

        # 1. Create execution record
        create_resp = MagicMock()
        create_resp.status_code = 200
        create_resp.json.return_value = {
            "key": "exec:12345",
            "value": {"status": "created", "prompt": "test"},
            "version": 1,
            "namespace": "executions",
        }
        create_resp.raise_for_status = MagicMock()
        responses.append(("put", create_resp))

        # 2. Update to in-progress
        progress_resp = MagicMock()
        progress_resp.status_code = 200
        progress_resp.json.return_value = {
            "key": "exec:12345",
            "value": {"status": "in_progress", "prompt": "test", "started_at": "..."},
            "version": 2,
            "namespace": "executions",
        }
        progress_resp.raise_for_status = MagicMock()
        responses.append(("put", progress_resp))

        # 3. Complete execution
        complete_resp = MagicMock()
        complete_resp.status_code = 200
        complete_resp.json.return_value = {
            "key": "exec:12345",
            "value": {
                "status": "completed",
                "prompt": "test",
                "started_at": "...",
                "completed_at": "...",
                "result": {"success": True},
            },
            "version": 3,
            "namespace": "executions",
        }
        complete_resp.raise_for_status = MagicMock()
        responses.append(("put", complete_resp))

        # 4. Retrieve final state
        get_resp = MagicMock()
        get_resp.status_code = 200
        get_resp.json.return_value = {
            "key": "exec:12345",
            "value": {
                "status": "completed",
                "prompt": "test",
                "started_at": "...",
                "completed_at": "...",
                "result": {"success": True},
            },
            "version": 3,
            "namespace": "executions",
        }
        get_resp.raise_for_status = MagicMock()
        responses.append(("get", get_resp))

        put_responses = [r[1] for r in responses if r[0] == "put"]
        get_responses = [r[1] for r in responses if r[0] == "get"]

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.side_effect = put_responses
            mock_client.get.side_effect = get_responses
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Create
            state = await client.put(
                "exec:12345",
                {"status": "created", "prompt": "test"},
                namespace="executions",
            )
            assert state.version == 1

            # Progress
            state = await client.put(
                "exec:12345",
                {"status": "in_progress", "prompt": "test", "started_at": "..."},
                namespace="executions",
                expected_version=1,
            )
            assert state.version == 2

            # Complete
            state = await client.put(
                "exec:12345",
                {
                    "status": "completed",
                    "prompt": "test",
                    "started_at": "...",
                    "completed_at": "...",
                    "result": {"success": True},
                },
                namespace="executions",
                expected_version=2,
            )
            assert state.version == 3

            # Retrieve
            final = await client.get("exec:12345", namespace="executions")
            assert final is not None
            assert final.value["status"] == "completed"
            assert final.value["result"]["success"] is True


class TestDgentSidecarHealthPattern:
    """Tests for sidecar health monitoring pattern."""

    @pytest.mark.asyncio
    async def test_health_check_before_operations(self) -> None:
        """Test checking sidecar health before state operations."""
        from agents.u.state import DgentClient, DgentConnectionError

        health_response = MagicMock()
        health_response.status_code = 200
        health_response.json.return_value = {
            "status": "healthy",
            "storage_type": "checkpointed",
            "keys_stored": 42,
            "namespaces": ["default", "executions"],
            "timestamp": "2025-12-12T12:00:00",
        }
        health_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = health_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Check health first
            health = await client.health()
            assert health["status"] == "healthy"
            assert health["storage_type"] == "checkpointed"  # PVC attached
            assert "executions" in health["namespaces"]

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_sidecar_unavailable(self) -> None:
        """Test graceful handling when sidecar is unavailable."""
        import httpx

        from agents.u.state import DgentClient, DgentConnectionError

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Should raise specific error that can be caught and handled
            with pytest.raises(DgentConnectionError):
                await client.health()

            # U-gent can catch this and decide how to proceed
            # (e.g., log warning, continue without persistence, escalate)


class TestCheckpointDurability:
    """Tests for checkpoint-based durability."""

    @pytest.mark.asyncio
    async def test_trigger_checkpoint_after_critical_operation(self) -> None:
        """Test triggering checkpoint after critical state change."""
        from agents.u.state import DgentClient

        put_response = MagicMock()
        put_response.status_code = 200
        put_response.json.return_value = {
            "key": "critical:data",
            "value": {"important": True},
            "version": 1,
            "namespace": "default",
        }
        put_response.raise_for_status = MagicMock()

        checkpoint_response = MagicMock()
        checkpoint_response.status_code = 200
        checkpoint_response.json.return_value = {
            "checkpoint_id": "chk_abc123",
            "namespace": "default",
            "keys": 1,
            "timestamp": "2025-12-12T12:00:00",
            "path": "/data/state/default_chk_abc123.json",
        }
        checkpoint_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.return_value = put_response
            mock_client.post.return_value = checkpoint_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://localhost:8081")

            # Store critical data
            await client.put("critical:data", {"important": True})

            # Trigger checkpoint for durability
            checkpoint = await client.checkpoint()

            assert checkpoint["checkpoint_id"] == "chk_abc123"
            assert checkpoint["path"] is not None  # Written to PVC
