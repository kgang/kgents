"""
Tests for API models.

Tests Pydantic request/response models for:
- Governance endpoints
- Dialogue endpoints
- Health checks
"""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from protocols.api.models import (
    DialogueRequest,
    DialogueResponse,
    GovernanceRequest,
    GovernanceResponse,
    HealthResponse,
)


class TestGovernanceModels:
    """Tests for governance request/response models."""

    def test_governance_request_minimal(self) -> None:
        """Test GovernanceRequest with minimal data."""
        req = GovernanceRequest(action="delete database")

        assert req.action == "delete database"
        assert req.context == {}
        assert req.budget == "dialogue"

    def test_governance_request_full(self) -> None:
        """Test GovernanceRequest with full data."""
        req = GovernanceRequest(
            action="deploy to production",
            context={"environment": "prod", "user": "alice"},
            budget="deep",
        )

        assert req.action == "deploy to production"
        assert req.context == {"environment": "prod", "user": "alice"}
        assert req.budget == "deep"

    def test_governance_request_from_dict(self) -> None:
        """Test GovernanceRequest from dict."""
        req = GovernanceRequest(
            action="rm -rf /tmp",
            context={"reason": "cleanup"},
        )

        assert req.action == "rm -rf /tmp"
        assert req.context == {"reason": "cleanup"}

    def test_governance_response_basic(self) -> None:
        """Test GovernanceResponse construction."""
        resp = GovernanceResponse(
            approved=True,
            reasoning="Operation aligns with minimalism",
            confidence=0.85,
            tokens_used=150,
            recommendation="approve",
        )

        assert resp.approved is True
        assert resp.reasoning == "Operation aligns with minimalism"
        assert resp.confidence == 0.85
        assert resp.tokens_used == 150
        assert resp.recommendation == "approve"
        assert resp.alternatives == []
        assert resp.principles == []

    def test_governance_response_with_alternatives(self) -> None:
        """Test GovernanceResponse with alternatives."""
        resp = GovernanceResponse(
            approved=False,
            reasoning="Too risky",
            confidence=0.9,
            tokens_used=200,
            recommendation="reject",
            alternatives=["Use soft delete", "Archive first"],
            principles=["Safety first", "Minimalism"],
        )

        assert resp.approved is False
        assert resp.alternatives == ["Use soft delete", "Archive first"]
        assert resp.principles == ["Safety first", "Minimalism"]

    def test_governance_response_confidence_bounds(self) -> None:
        """Test confidence is bounded 0.0 to 1.0."""
        # Valid confidence
        resp = GovernanceResponse(
            approved=True,
            reasoning="Good",
            confidence=0.5,
            tokens_used=100,
            recommendation="approve",
        )
        assert 0.0 <= resp.confidence <= 1.0

        # Edge cases
        resp_low = GovernanceResponse(
            approved=False,
            reasoning="Low",
            confidence=0.0,
            tokens_used=100,
            recommendation="reject",
        )
        assert resp_low.confidence == 0.0

        resp_high = GovernanceResponse(
            approved=True,
            reasoning="High",
            confidence=1.0,
            tokens_used=100,
            recommendation="approve",
        )
        assert resp_high.confidence == 1.0


class TestDialogueModels:
    """Tests for dialogue request/response models."""

    def test_dialogue_request_minimal(self) -> None:
        """Test DialogueRequest with minimal data."""
        req = DialogueRequest(prompt="What am I avoiding?")

        assert req.prompt == "What am I avoiding?"
        assert req.mode == "reflect"
        assert req.budget == "dialogue"

    def test_dialogue_request_full(self) -> None:
        """Test DialogueRequest with full data."""
        req = DialogueRequest(
            prompt="Challenge my thesis",
            mode="challenge",
            budget="deep",
        )

        assert req.prompt == "Challenge my thesis"
        assert req.mode == "challenge"
        assert req.budget == "deep"

    def test_dialogue_request_modes(self) -> None:
        """Test DialogueRequest with different modes."""
        modes = ["reflect", "advise", "challenge", "explore"]

        for mode in modes:
            req = DialogueRequest(prompt="Test", mode=mode)
            assert req.mode == mode

    def test_dialogue_response_basic(self) -> None:
        """Test DialogueResponse construction."""
        resp = DialogueResponse(
            response="You're avoiding the hard decision.",
            mode="reflect",
            eigenvectors={"aesthetic": 0.9},
            tokens_used=250,
        )

        assert resp.response == "You're avoiding the hard decision."
        assert resp.mode == "reflect"
        assert resp.eigenvectors == {"aesthetic": 0.9}
        assert resp.tokens_used == 250
        assert resp.referenced_preferences == []
        assert resp.referenced_patterns == []

    def test_dialogue_response_with_references(self) -> None:
        """Test DialogueResponse with preferences and patterns."""
        resp = DialogueResponse(
            response="Based on your preference for minimalism...",
            mode="advise",
            eigenvectors={"aesthetic": 0.9},
            tokens_used=300,
            referenced_preferences=["Prefer minimal solutions"],
            referenced_patterns=["Procrastination through perfectionism"],
        )

        assert resp.referenced_preferences == ["Prefer minimal solutions"]
        assert resp.referenced_patterns == ["Procrastination through perfectionism"]


class TestHealthModels:
    """Tests for health response model."""

    def test_health_response_ok(self) -> None:
        """Test HealthResponse for healthy service."""
        resp = HealthResponse(
            status="ok",
            version="v1",
            has_llm=True,
            components={
                "soul": "ok",
                "llm": "ok",
                "auth": "ok",
            },
        )

        assert resp.status == "ok"
        assert resp.version == "v1"
        assert resp.has_llm is True
        assert resp.components["soul"] == "ok"

    def test_health_response_degraded(self) -> None:
        """Test HealthResponse for degraded service."""
        resp = HealthResponse(
            status="degraded",
            version="v1",
            has_llm=False,
            components={
                "soul": "ok",
                "llm": "not_configured",
                "auth": "ok",
            },
        )

        assert resp.status == "degraded"
        assert resp.has_llm is False
        assert resp.components["llm"] == "not_configured"

    def test_health_response_error(self) -> None:
        """Test HealthResponse for error state."""
        resp = HealthResponse(
            status="error",
            version="v1",
            has_llm=False,
            components={
                "soul": "error: initialization failed",
                "llm": "unknown",
            },
        )

        assert resp.status == "error"
        assert "error" in resp.components["soul"]


class TestModelSerialization:
    """Tests for model serialization."""

    def test_governance_request_json(self) -> None:
        """Test GovernanceRequest JSON serialization."""
        req = GovernanceRequest(
            action="test",
            context={"key": "value"},
        )

        data = req.model_dump()
        assert data["action"] == "test"
        assert data["context"] == {"key": "value"}

    def test_dialogue_response_json(self) -> None:
        """Test DialogueResponse JSON serialization."""
        resp = DialogueResponse(
            response="Test response",
            mode="reflect",
            eigenvectors={"test": 1.0},
            tokens_used=100,
        )

        data = resp.model_dump()
        assert data["response"] == "Test response"
        assert data["mode"] == "reflect"
        assert data["tokens_used"] == 100
