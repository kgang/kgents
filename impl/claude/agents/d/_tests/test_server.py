"""
Test suite for D-gent Server.

Tests for server.py:
- StateValue model validation
- InMemoryStore operations (CRUD, versioning, checkpoints)
- Health endpoint
- State endpoints with namespace isolation
- Version conflict detection (optimistic concurrency)
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# --- Request/Response Model Tests ---


class TestStateValue:
    """Tests for StateValue model."""

    def test_minimal_state(self) -> None:
        """Test minimal state with just key and value."""
        from agents.d.server import StateValue

        state = StateValue(key="test_key", value={"data": 123})
        assert state.key == "test_key"
        assert state.value == {"data": 123}
        assert state.version == 1
        assert state.namespace == "default"

    def test_full_state(self) -> None:
        """Test state with all fields."""
        from agents.d.server import StateValue

        now = datetime.now().isoformat()
        state = StateValue(
            key="user:alice",
            value={"name": "Alice", "age": 30},
            version=5,
            namespace="users",
            created_at=now,
            updated_at=now,
        )
        assert state.key == "user:alice"
        assert state.value["name"] == "Alice"
        assert state.version == 5
        assert state.namespace == "users"


class TestPutRequest:
    """Tests for PutRequest model."""

    def test_value_only(self) -> None:
        """Test put with just value."""
        from agents.d.server import PutRequest

        request = PutRequest(value={"count": 42}, expected_version=None)
        assert request.value == {"count": 42}
        assert request.expected_version is None

    def test_with_expected_version(self) -> None:
        """Test put with CAS check."""
        from agents.d.server import PutRequest

        request = PutRequest(value={"count": 43}, expected_version=5)
        assert request.expected_version == 5


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_healthy_response(self) -> None:
        """Test healthy response structure."""
        from agents.d.server import HealthResponse

        response = HealthResponse(
            status="healthy",
            storage_type="in-memory",
            keys_stored=10,
            namespaces=["default", "users"],
            timestamp=datetime.now().isoformat(),
        )
        assert response.status == "healthy"
        assert response.keys_stored == 10
        assert len(response.namespaces) == 2


# --- InMemoryStore Tests ---


class TestInMemoryStore:
    """Tests for InMemoryStore."""

    def test_put_and_get(self) -> None:
        """Test basic put and get operations."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        state = store.put("key1", {"data": "value"})

        assert state.key == "key1"
        assert state.value == {"data": "value"}
        assert state.version == 1

        retrieved = store.get("key1")
        assert retrieved is not None
        assert retrieved.value == {"data": "value"}

    def test_get_nonexistent_returns_none(self) -> None:
        """Test get for nonexistent key returns None."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        assert store.get("nonexistent") is None

    def test_version_increments_on_update(self) -> None:
        """Test version increments on update."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        v1 = store.put("key", {"count": 1})
        assert v1.version == 1

        v2 = store.put("key", {"count": 2})
        assert v2.version == 2

        v3 = store.put("key", {"count": 3})
        assert v3.version == 3

    def test_cas_success(self) -> None:
        """Test CAS (Compare-And-Swap) succeeds with correct version."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("key", {"count": 1})

        # Update with correct expected version
        result = store.put("key", {"count": 2}, expected_version=1)
        assert result.version == 2
        assert result.value == {"count": 2}

    def test_cas_fails_on_version_mismatch(self) -> None:
        """Test CAS fails on version mismatch."""
        from agents.d.server import InMemoryStore, VersionConflictError

        store = InMemoryStore()
        store.put("key", {"count": 1})

        # Update with wrong expected version
        with pytest.raises(VersionConflictError) as exc_info:
            store.put("key", {"count": 2}, expected_version=5)

        assert "expected 5" in str(exc_info.value)
        assert "found 1" in str(exc_info.value)

    def test_cas_fails_for_new_key_with_nonzero_version(self) -> None:
        """Test CAS fails for new key with non-zero expected version."""
        from agents.d.server import InMemoryStore, VersionConflictError

        store = InMemoryStore()

        with pytest.raises(VersionConflictError):
            store.put("newkey", {"data": 1}, expected_version=1)

    def test_delete(self) -> None:
        """Test delete operation."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("key", {"data": 1})
        assert store.get("key") is not None

        deleted = store.delete("key")
        assert deleted is True
        assert store.get("key") is None

    def test_delete_nonexistent_returns_false(self) -> None:
        """Test delete of nonexistent key returns False."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        assert store.delete("nonexistent") is False

    def test_namespace_isolation(self) -> None:
        """Test namespace isolation."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("key", {"value": "default"}, namespace="default")
        store.put("key", {"value": "users"}, namespace="users")

        default_val = store.get("key", namespace="default")
        users_val = store.get("key", namespace="users")

        assert default_val is not None
        assert default_val.value == {"value": "default"}
        assert users_val is not None
        assert users_val.value == {"value": "users"}

    def test_list_keys(self) -> None:
        """Test listing keys in namespace."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("key1", {"data": 1})
        store.put("key2", {"data": 2})
        store.put("key3", {"data": 3})

        keys = store.list_keys()
        assert set(keys) == {"key1", "key2", "key3"}

    def test_list_namespaces(self) -> None:
        """Test listing namespaces."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("k1", {}, namespace="ns1")
        store.put("k2", {}, namespace="ns2")
        store.put("k3", {}, namespace="ns3")

        namespaces = store.list_namespaces()
        assert set(namespaces) == {"ns1", "ns2", "ns3"}

    def test_count(self) -> None:
        """Test counting keys."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("k1", {}, namespace="ns1")
        store.put("k2", {}, namespace="ns1")
        store.put("k3", {}, namespace="ns2")

        assert store.count(namespace="ns1") == 2
        assert store.count(namespace="ns2") == 1
        assert store.count() == 3  # Total


class TestInMemoryStoreCheckpoint:
    """Tests for checkpoint functionality."""

    def test_checkpoint_without_directory(self) -> None:
        """Test checkpoint works without checkpoint directory."""
        from agents.d.server import InMemoryStore

        store = InMemoryStore()
        store.put("key1", {"data": 1})
        store.put("key2", {"data": 2})

        checkpoint = store.checkpoint()
        assert checkpoint.namespace == "default"
        assert checkpoint.keys == 2
        assert checkpoint.path is None  # No directory configured
        assert len(checkpoint.checkpoint_id) == 16

    def test_checkpoint_with_directory(self) -> None:
        """Test checkpoint writes to directory."""
        from agents.d.server import InMemoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = InMemoryStore()
            store._checkpoint_dir = Path(tmpdir)

            store.put("key1", {"data": 1})
            store.put("key2", {"data": 2})

            checkpoint = store.checkpoint()
            assert checkpoint.path is not None
            assert Path(checkpoint.path).exists()

            # Verify checkpoint contents
            data = json.loads(Path(checkpoint.path).read_text())
            assert data["namespace"] == "default"
            assert "key1" in data["state"]
            assert "key2" in data["state"]

    def test_restore_from_checkpoint(self) -> None:
        """Test restoring state from checkpoint."""
        from agents.d.server import InMemoryStore

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and checkpoint initial store
            store1 = InMemoryStore()
            store1._checkpoint_dir = Path(tmpdir)
            store1.put("key1", {"data": 1})
            store1.put("key2", {"data": 2})
            store1.checkpoint()

            # Create new store pointing to same directory
            store2 = InMemoryStore()
            store2._checkpoint_dir = Path(tmpdir)
            store2._restore_from_checkpoint()

            # Verify restoration
            v1 = store2.get("key1")
            v2 = store2.get("key2")
            assert v1 is not None
            assert v1.value == {"data": 1}
            assert v2 is not None
            assert v2.value == {"data": 2}


# --- Server Endpoint Tests ---


class TestServerEndpoints:
    """Tests for server endpoints."""

    @pytest.fixture
    def app(self) -> Any:
        """Create test app."""
        from agents.d.server import create_app

        return create_app()

    @pytest.fixture
    def client(self, app: Any) -> Any:
        """Create test client."""
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_root_endpoint(self, client: Any) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "D-gent Server"
        assert "endpoints" in data
        assert "get_state" in data["endpoints"]

    def test_health_endpoint(self, client: Any) -> None:
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "storage_type" in data
        assert "keys_stored" in data
        assert "namespaces" in data


class TestStateEndpoints:
    """Tests for state CRUD endpoints."""

    @pytest.fixture
    def app(self) -> Any:
        """Create test app with fresh store."""
        # Reset global state for test isolation
        import agents.d.server as server_module
        from agents.d.server import ServerState, create_app

        server_module._state = ServerState()
        return create_app()

    @pytest.fixture
    def client(self, app: Any) -> Any:
        """Create test client."""
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_put_and_get_state(self, client: Any) -> None:
        """Test put and get state."""
        # Put state
        response = client.put(
            "/state/mykey",
            json={"value": {"count": 42}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "mykey"
        assert data["value"] == {"count": 42}
        assert data["version"] == 1

        # Get state
        response = client.get("/state/mykey")
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == {"count": 42}

    def test_get_nonexistent_returns_404(self, client: Any) -> None:
        """Test get nonexistent key returns 404."""
        response = client.get("/state/nonexistent")
        assert response.status_code == 404

    def test_delete_state(self, client: Any) -> None:
        """Test delete state."""
        # Put first
        client.put("/state/todelete", json={"value": "data"})

        # Delete
        response = client.delete("/state/todelete")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True

        # Verify gone
        response = client.get("/state/todelete")
        assert response.status_code == 404

    def test_delete_nonexistent_returns_404(self, client: Any) -> None:
        """Test delete nonexistent key returns 404."""
        response = client.delete("/state/nonexistent")
        assert response.status_code == 404

    def test_list_keys(self, client: Any) -> None:
        """Test list keys endpoint."""
        client.put("/state/key1", json={"value": 1})
        client.put("/state/key2", json={"value": 2})

        response = client.get("/keys")
        assert response.status_code == 200
        data = response.json()
        assert set(data["keys"]) == {"key1", "key2"}
        assert data["count"] == 2

    def test_namespace_isolation(self, client: Any) -> None:
        """Test namespace isolation via query param."""
        # Put in different namespaces
        client.put("/state/key?namespace=ns1", json={"value": "ns1_value"})
        client.put("/state/key?namespace=ns2", json={"value": "ns2_value"})

        # Get from each namespace
        response1 = client.get("/state/key?namespace=ns1")
        response2 = client.get("/state/key?namespace=ns2")

        assert response1.json()["value"] == "ns1_value"
        assert response2.json()["value"] == "ns2_value"


class TestVersionConflicts:
    """Tests for optimistic concurrency control."""

    @pytest.fixture
    def app(self) -> Any:
        """Create test app with fresh store."""
        import agents.d.server as server_module
        from agents.d.server import ServerState, create_app

        server_module._state = ServerState()
        return create_app()

    @pytest.fixture
    def client(self, app: Any) -> Any:
        """Create test client."""
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_cas_success(self, client: Any) -> None:
        """Test CAS succeeds with correct version."""
        # Create key
        client.put("/state/caskey", json={"value": {"v": 1}})

        # Update with correct version
        response = client.put(
            "/state/caskey",
            json={"value": {"v": 2}, "expected_version": 1},
        )
        assert response.status_code == 200
        assert response.json()["version"] == 2

    def test_cas_fails_on_conflict(self, client: Any) -> None:
        """Test CAS fails on version conflict."""
        # Create key
        client.put("/state/caskey", json={"value": {"v": 1}})

        # Update with wrong version
        response = client.put(
            "/state/caskey",
            json={"value": {"v": 2}, "expected_version": 5},
        )
        assert response.status_code == 409
        assert "conflict" in response.json()["detail"].lower()

    def test_cas_for_new_key_with_zero_version(self, client: Any) -> None:
        """Test CAS for new key works with version 0."""
        response = client.put(
            "/state/newkey",
            json={"value": {"data": 1}, "expected_version": 0},
        )
        assert response.status_code == 200
        assert response.json()["version"] == 1


class TestCheckpointEndpoint:
    """Tests for checkpoint endpoint."""

    @pytest.fixture
    def app(self) -> Any:
        """Create test app with fresh store."""
        import agents.d.server as server_module
        from agents.d.server import ServerState, create_app

        server_module._state = ServerState()
        return create_app()

    @pytest.fixture
    def client(self, app: Any) -> Any:
        """Create test client."""
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_checkpoint_creation(self, client: Any) -> None:
        """Test checkpoint creation."""
        # Add some state
        client.put("/state/key1", json={"value": 1})
        client.put("/state/key2", json={"value": 2})

        # Create checkpoint
        response = client.post("/checkpoint")
        assert response.status_code == 200
        data = response.json()
        assert data["namespace"] == "default"
        assert data["keys"] == 2
        assert len(data["checkpoint_id"]) == 16

    def test_checkpoint_respects_namespace(self, client: Any) -> None:
        """Test checkpoint respects namespace parameter."""
        # Add state to specific namespace
        client.put("/state/key?namespace=myns", json={"value": 1})

        # Checkpoint specific namespace
        response = client.post("/checkpoint?namespace=myns")
        assert response.status_code == 200
        data = response.json()
        assert data["namespace"] == "myns"
        assert data["keys"] == 1
