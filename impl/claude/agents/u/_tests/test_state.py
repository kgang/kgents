"""
Test suite for D-gent Client (state.py).

Tests for DgentClient:
- Basic CRUD operations (get, put, delete)
- Optimistic concurrency control (CAS)
- Namespace isolation
- Error handling (connection errors, version conflicts)
- Health and checkpoint endpoints
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# --- StateValue Tests ---


class TestStateValue:
    """Tests for StateValue dataclass."""

    def test_state_value_creation(self) -> None:
        """Test StateValue holds all fields."""
        from agents.u.state import StateValue

        sv = StateValue(
            key="test:key",
            value={"count": 42},
            version=3,
            namespace="sessions",
            created_at="2025-12-12T10:00:00",
            updated_at="2025-12-12T11:00:00",
        )
        assert sv.key == "test:key"
        assert sv.value == {"count": 42}
        assert sv.version == 3
        assert sv.namespace == "sessions"


# --- DgentClient Tests ---


class TestDgentClientInit:
    """Tests for DgentClient initialization."""

    def test_default_url(self) -> None:
        """Test default URL from environment or localhost."""
        from agents.u.state import DgentClient

        client = DgentClient()
        assert "localhost:8081" in client.base_url or "DGENT_URL" in str(client.base_url)

    def test_custom_url(self) -> None:
        """Test custom URL."""
        from agents.u.state import DgentClient

        client = DgentClient(base_url="http://dgent.custom:9000")
        assert client.base_url == "http://dgent.custom:9000"

    def test_env_url(self) -> None:
        """Test URL from environment variable."""
        import os

        from agents.u.state import DgentClient

        with patch.dict(os.environ, {"DGENT_URL": "http://env-dgent:8081"}):
            client = DgentClient()
            assert client.base_url == "http://env-dgent:8081"


class TestDgentClientGet:
    """Tests for DgentClient.get()."""

    @pytest.mark.asyncio
    async def test_get_existing_key(self) -> None:
        """Test getting existing key returns StateValue."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "session:123",
            "value": {"step": 5},
            "version": 2,
            "namespace": "default",
            "created_at": "2025-12-12T10:00:00",
            "updated_at": "2025-12-12T11:00:00",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.get("session:123")

            assert result is not None
            assert result.key == "session:123"
            assert result.value == {"step": 5}
            assert result.version == 2

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self) -> None:
        """Test getting nonexistent key returns None."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.get("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_with_namespace(self) -> None:
        """Test get respects namespace parameter."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "key1",
            "value": {"ns": "users"},
            "version": 1,
            "namespace": "users",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            await client.get("key1", namespace="users")

            # Verify namespace was passed
            call_args = mock_client.get.call_args
            assert call_args[1]["params"]["namespace"] == "users"

    @pytest.mark.asyncio
    async def test_get_connection_error(self) -> None:
        """Test get raises DgentConnectionError on connection failure."""
        import httpx

        from agents.u.state import DgentClient, DgentConnectionError

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")

            with pytest.raises(DgentConnectionError) as exc_info:
                await client.get("key")

            assert "Cannot connect" in str(exc_info.value)


class TestDgentClientPut:
    """Tests for DgentClient.put()."""

    @pytest.mark.asyncio
    async def test_put_new_key(self) -> None:
        """Test putting new key."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "new:key",
            "value": {"data": 123},
            "version": 1,
            "namespace": "default",
            "created_at": "2025-12-12T12:00:00",
            "updated_at": "2025-12-12T12:00:00",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.put("new:key", {"data": 123})

            assert result.key == "new:key"
            assert result.version == 1

    @pytest.mark.asyncio
    async def test_put_with_cas(self) -> None:
        """Test put with CAS (expected_version)."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "cas:key",
            "value": {"count": 2},
            "version": 2,
            "namespace": "default",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.put("cas:key", {"count": 2}, expected_version=1)

            # Verify expected_version was passed
            call_args = mock_client.put.call_args
            assert call_args[1]["json"]["expected_version"] == 1

            assert result.version == 2

    @pytest.mark.asyncio
    async def test_put_version_conflict(self) -> None:
        """Test put raises VersionConflictError on conflict."""
        from agents.u.state import DgentClient, VersionConflictError

        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.json.return_value = {"detail": "Version conflict: expected 5, found 1"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.put.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")

            with pytest.raises(VersionConflictError) as exc_info:
                await client.put("key", {"data": 1}, expected_version=5)

            assert "conflict" in str(exc_info.value).lower()


class TestDgentClientDelete:
    """Tests for DgentClient.delete()."""

    @pytest.mark.asyncio
    async def test_delete_existing_key(self) -> None:
        """Test deleting existing key returns True."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.delete.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.delete("key")

            assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self) -> None:
        """Test deleting nonexistent key returns False."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.delete.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.delete("nonexistent")

            assert result is False


class TestDgentClientListKeys:
    """Tests for DgentClient.list_keys()."""

    @pytest.mark.asyncio
    async def test_list_keys(self) -> None:
        """Test listing keys in namespace."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "namespace": "default",
            "keys": ["key1", "key2", "key3"],
            "count": 3,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            keys = await client.list_keys()

            assert keys == ["key1", "key2", "key3"]


class TestDgentClientCheckpoint:
    """Tests for DgentClient.checkpoint()."""

    @pytest.mark.asyncio
    async def test_checkpoint(self) -> None:
        """Test triggering checkpoint."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "checkpoint_id": "abc123def456",
            "namespace": "default",
            "keys": 5,
            "timestamp": "2025-12-12T12:00:00",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.checkpoint()

            assert result["checkpoint_id"] == "abc123def456"
            assert result["keys"] == 5


class TestDgentClientHealth:
    """Tests for DgentClient.health()."""

    @pytest.mark.asyncio
    async def test_health(self) -> None:
        """Test health check."""
        from agents.u.state import DgentClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "storage_type": "checkpointed",
            "keys_stored": 10,
            "namespaces": ["default", "sessions"],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            client = DgentClient(base_url="http://test:8081")
            result = await client.health()

            assert result["status"] == "healthy"
            assert result["keys_stored"] == 10
