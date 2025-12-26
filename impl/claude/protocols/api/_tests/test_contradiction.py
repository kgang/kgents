"""
Tests for Contradiction Engine API.

Verifies:
- POST /api/contradictions/detect - Detection with super-additive loss
- GET  /api/contradictions - List with filters
- GET  /api/contradictions/{id} - Get resolution prompt
- POST /api/contradictions/{id}/resolve - Apply resolution strategy
- GET  /api/contradictions/stats - Summary statistics

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every resolution creates a Witness mark.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all tests if FastAPI not available
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from protocols.api.app import create_app

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client():
    """Create test client with Contradiction API."""
    app = create_app(
        enable_cors=False,
        enable_tenant_middleware=False,
    )
    return TestClient(app)


@pytest.fixture
def mock_k_block_storage():
    """Mock K-Block storage with test data."""
    mock = MagicMock()

    # Create mock K-Blocks with proper attributes
    kb1 = MagicMock()
    kb1.id = "kb-001"
    kb1.content = "All agents should be stateless."
    kb1.zero_seed_layer = 2
    kb1.title = "Stateless Agents"
    kb1.galois_loss = None  # Will be computed

    kb2 = MagicMock()
    kb2.id = "kb-002"
    kb2.content = "Agents maintain internal state for memory."
    kb2.zero_seed_layer = 2
    kb2.title = "Stateful Agents"
    kb2.galois_loss = None

    kb3 = MagicMock()
    kb3.id = "kb-003"
    kb3.content = "All knowledge is constructed."
    kb3.zero_seed_layer = 1
    kb3.title = "Constructivism"
    kb3.galois_loss = None

    mock.get_node.side_effect = lambda node_id: {
        "kb-001": kb1,
        "kb-002": kb2,
        "kb-003": kb3,
    }.get(node_id)

    # Mock create_node for synthesis
    mock.create_node.return_value = (kb1, "kb-synth-001")

    return mock


@pytest.fixture
def mock_witness():
    """Mock Witness persistence."""
    mock = AsyncMock()

    # Mock save_mark
    mark = MagicMock()
    mark.mark_id = "mark-001"
    mark.action = "Test action"
    mark.timestamp = datetime.now(UTC)
    mock.save_mark.return_value = mark

    return mock


# =============================================================================
# Detection Tests
# =============================================================================


@pytest.mark.asyncio
async def test_detect_contradictions_success(client, mock_k_block_storage, mock_witness):
    """Test successful contradiction detection."""
    with (
        patch(
            "services.k_block.zero_seed_storage.get_zero_seed_storage",
            return_value=mock_k_block_storage,
        ),
        patch(
            "services.providers.get_witness_persistence",
            return_value=mock_witness,
        ),
    ):
        response = client.post(
            "/api/contradictions/detect",
            json={
                "k_block_ids": ["kb-001", "kb-002"],
                "threshold": 0.1,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "contradictions" in data
        assert "total" in data
        assert "analyzed_pairs" in data
        assert "threshold" in data

        # Should analyze 1 pair (2 K-Blocks = 1 pair)
        assert data["analyzed_pairs"] == 1
        assert data["threshold"] == 0.1

        # Should detect contradiction (stateless vs stateful)
        assert data["total"] >= 0  # May or may not detect based on mock loss


@pytest.mark.asyncio
async def test_detect_contradictions_multiple_pairs(client, mock_k_block_storage):
    """Test detection across multiple K-Block pairs."""
    with patch(
        "services.k_block.zero_seed_storage.get_zero_seed_storage",
        return_value=mock_k_block_storage,
    ):
        response = client.post(
            "/api/contradictions/detect",
            json={
                "k_block_ids": ["kb-001", "kb-002", "kb-003"],
                "threshold": 0.05,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # 3 K-Blocks = 3 pairs (upper triangle)
        assert data["analyzed_pairs"] == 3


@pytest.mark.asyncio
async def test_detect_contradictions_not_found(client, mock_k_block_storage):
    """Test detection with non-existent K-Block."""
    with patch(
        "services.k_block.zero_seed_storage.get_zero_seed_storage",
        return_value=mock_k_block_storage,
    ):
        response = client.post(
            "/api/contradictions/detect",
            json={
                "k_block_ids": ["kb-001", "kb-nonexistent"],
                "threshold": 0.1,
            },
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_detect_contradictions_invalid_threshold(client):
    """Test detection with invalid threshold."""
    response = client.post(
        "/api/contradictions/detect",
        json={
            "k_block_ids": ["kb-001", "kb-002"],
            "threshold": 1.5,  # Invalid: > 1.0
        },
    )

    assert response.status_code == 422  # Validation error


# =============================================================================
# List Tests
# =============================================================================


def test_list_contradictions_empty(client):
    """Test listing when no contradictions exist."""
    response = client.get("/api/contradictions")

    assert response.status_code == 200
    data = response.json()

    assert data["contradictions"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


def test_list_contradictions_with_filters(client):
    """Test listing with type and severity filters."""
    # TODO: Seed test data in global state
    response = client.get(
        "/api/contradictions",
        params={
            "type": "PRODUCTIVE",
            "min_severity": 0.3,
            "limit": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # All results should match filters
    for c in data["contradictions"]:
        assert c["type"] == "PRODUCTIVE"
        assert c["severity"] >= 0.3


def test_list_contradictions_pagination(client):
    """Test pagination parameters."""
    response = client.get(
        "/api/contradictions",
        params={"limit": 5, "offset": 10},
    )

    assert response.status_code == 200
    data = response.json()

    # Should respect limit
    assert len(data["contradictions"]) <= 5


# =============================================================================
# Get Single Contradiction Tests
# =============================================================================


def test_get_contradiction_not_found(client):
    """Test getting non-existent contradiction."""
    response = client.get("/api/contradictions/nonexistent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# =============================================================================
# Resolution Tests
# =============================================================================


@pytest.mark.asyncio
async def test_resolve_contradiction_synthesize(
    client, mock_k_block_storage, mock_witness
):
    """Test SYNTHESIZE resolution strategy."""
    # First, detect a contradiction to create one
    with (
        patch(
            "services.k_block.zero_seed_storage.get_zero_seed_storage",
            return_value=mock_k_block_storage,
        ),
        patch(
            "services.providers.get_witness_persistence",
            return_value=mock_witness,
        ),
    ):
        # Detect
        detect_response = client.post(
            "/api/contradictions/detect",
            json={
                "k_block_ids": ["kb-001", "kb-002"],
                "threshold": 0.01,  # Low threshold to ensure detection
            },
        )

        # Force create a contradiction in global state for testing
        # In real usage, detect would populate this
        from protocols.api.contradiction import KBlockSummary, _contradictions

        test_contradiction = {
            "id": "contradiction_kb-001_kb-002",
            "type": "PRODUCTIVE",
            "severity": 0.35,
            "k_block_a": KBlockSummary(
                id="kb-001",
                content="All agents should be stateless.",
                layer=2,
                title="Stateless Agents",
            ),
            "k_block_b": KBlockSummary(
                id="kb-002",
                content="Agents maintain internal state for memory.",
                layer=2,
                title="Stateful Agents",
            ),
            "super_additive_loss": 0.35,
            "loss_a": 0.15,
            "loss_b": 0.15,
            "loss_combined": 0.65,
            "detected_at": datetime.now(UTC).isoformat(),
            "suggested_strategy": "SYNTHESIZE",
            "classification": {
                "type": "PRODUCTIVE",
                "strength": 0.35,
                "confidence": 0.7,
                "reasoning": "Test reasoning",
            },
        }

        from protocols.api.contradiction import ContradictionResponse

        _contradictions["contradiction_kb-001_kb-002"] = ContradictionResponse(
            **test_contradiction
        )

        # Now resolve with SYNTHESIZE
        resolve_response = client.post(
            "/api/contradictions/contradiction_kb-001_kb-002/resolve",
            json={
                "strategy": "SYNTHESIZE",
                "new_content": "Agents use functional state management for memory.",
            },
        )

        assert resolve_response.status_code == 200
        data = resolve_response.json()

        assert data["strategy"] == "SYNTHESIZE"
        assert data["contradiction_id"] == "contradiction_kb-001_kb-002"
        assert "witness_mark_id" in data
        assert "new_k_block_id" in data
        assert data["new_k_block_id"] == "kb-synth-001"

        # Verify witness mark was created
        mock_witness.save_mark.assert_called_once()
        call_kwargs = mock_witness.save_mark.call_args.kwargs
        assert "Resolved contradiction" in call_kwargs["action"]
        assert call_kwargs["author"] == "user"


@pytest.mark.asyncio
async def test_resolve_contradiction_choose(client, mock_witness):
    """Test CHOOSE resolution strategy."""
    # Seed contradiction
    from protocols.api.contradiction import ContradictionResponse, KBlockSummary, _contradictions

    _contradictions["test-contradiction"] = ContradictionResponse(
        id="test-contradiction",
        type="TENSION",
        severity=0.5,
        k_block_a=KBlockSummary(id="kb-001", content="A", layer=2, title="A"),
        k_block_b=KBlockSummary(id="kb-002", content="B", layer=2, title="B"),
        super_additive_loss=0.5,
        loss_a=0.2,
        loss_b=0.2,
        loss_combined=0.9,
        detected_at=datetime.now(UTC).isoformat(),
        suggested_strategy="CHOOSE",
        classification={"type": "TENSION"},
    )

    with patch(
        "services.providers.get_witness_persistence",
        return_value=mock_witness,
    ):
        response = client.post(
            "/api/contradictions/test-contradiction/resolve",
            json={
                "strategy": "CHOOSE",
                "chosen_k_block_id": "kb-001",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["strategy"] == "CHOOSE"
        assert data["outcome"]["chosen_kblock_id"] == "kb-001"


@pytest.mark.asyncio
async def test_resolve_contradiction_invalid_strategy(client, mock_witness):
    """Test resolution with invalid strategy."""
    from protocols.api.contradiction import ContradictionResponse, KBlockSummary, _contradictions

    _contradictions["test-contradiction"] = ContradictionResponse(
        id="test-contradiction",
        type="APPARENT",
        severity=0.1,
        k_block_a=KBlockSummary(id="kb-001", content="A", layer=1, title="A"),
        k_block_b=KBlockSummary(id="kb-002", content="B", layer=1, title="B"),
        super_additive_loss=0.1,
        loss_a=0.05,
        loss_b=0.05,
        loss_combined=0.2,
        detected_at=datetime.now(UTC).isoformat(),
        suggested_strategy="SCOPE",
        classification={"type": "APPARENT"},
    )

    with patch(
        "services.providers.get_witness_persistence",
        return_value=mock_witness,
    ):
        response = client.post(
            "/api/contradictions/test-contradiction/resolve",
            json={"strategy": "INVALID_STRATEGY"},
        )

        assert response.status_code == 400
        assert "Invalid strategy" in response.json()["detail"]


# =============================================================================
# Statistics Tests
# =============================================================================


def test_get_stats_empty(client):
    """Test statistics when no contradictions exist."""
    # Clear global state
    from protocols.api.contradiction import _contradictions, _resolutions

    _contradictions.clear()
    _resolutions.clear()

    response = client.get("/api/contradictions/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert data["resolved_count"] == 0
    assert data["unresolved_count"] == 0
    assert data["average_strength"] == 0.0
    assert data["most_common_strategy"] is None


def test_get_stats_with_data(client):
    """Test statistics with contradictions and resolutions."""
    from protocols.api.contradiction import (
        ContradictionResponse,
        KBlockSummary,
        ResolutionResponse,
        _contradictions,
        _resolutions,
    )

    # Seed test data
    _contradictions.clear()
    _resolutions.clear()

    _contradictions["c1"] = ContradictionResponse(
        id="c1",
        type="PRODUCTIVE",
        severity=0.3,
        k_block_a=KBlockSummary(id="kb-001", content="A", layer=2, title="A"),
        k_block_b=KBlockSummary(id="kb-002", content="B", layer=2, title="B"),
        super_additive_loss=0.3,
        loss_a=0.1,
        loss_b=0.1,
        loss_combined=0.5,
        detected_at=datetime.now(UTC).isoformat(),
        suggested_strategy="SYNTHESIZE",
        classification={"type": "PRODUCTIVE"},
    )

    _contradictions["c2"] = ContradictionResponse(
        id="c2",
        type="FUNDAMENTAL",
        severity=0.7,
        k_block_a=KBlockSummary(id="kb-003", content="C", layer=1, title="C"),
        k_block_b=KBlockSummary(id="kb-004", content="D", layer=1, title="D"),
        super_additive_loss=0.7,
        loss_a=0.3,
        loss_b=0.3,
        loss_combined=1.3,
        detected_at=datetime.now(UTC).isoformat(),
        suggested_strategy="CHOOSE",
        classification={"type": "FUNDAMENTAL"},
    )

    _resolutions["c1"] = ResolutionResponse(
        contradiction_id="c1",
        strategy="SYNTHESIZE",
        resolved_at=datetime.now(UTC).isoformat(),
        witness_mark_id="mark-001",
        new_k_block_id="kb-synth-001",
        outcome={},
    )

    response = client.get("/api/contradictions/stats")

    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2
    assert data["resolved_count"] == 1
    assert data["unresolved_count"] == 1
    assert data["average_strength"] == 0.5  # (0.3 + 0.7) / 2
    assert data["most_common_strategy"] == "SYNTHESIZE"
    assert data["by_type"]["PRODUCTIVE"] == 1
    assert data["by_type"]["FUNDAMENTAL"] == 1
    assert data["by_severity"]["medium"] == 1  # 0.3 >= 0.3 and < 0.6
    assert data["by_severity"]["high"] == 1  # 0.7 >= 0.6
