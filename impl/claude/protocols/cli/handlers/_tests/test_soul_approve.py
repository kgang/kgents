"""
Tests for soul_approve CLI handler.

Tests for `kgents soul approve` command - Pro Crown Jewel.

Tests verify:
1. cmd_soul_approve with --help
2. Approval checks with various actions
3. --json output mode
4. Verdict determination (WOULD APPROVE / WOULD NOT APPROVE)
5. Principle violations
6. Alternative suggestions
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ..soul_approve import (
    _print_help,
    _suggest_alternative,
    cmd_soul_approve,
    set_soul,
)

# === cmd_soul_approve Help Tests ===


class TestCmdSoulApproveHelp:
    """Tests for --help flag."""

    def test_help_flag_prints_help(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--help prints help and returns 0."""
        result = cmd_soul_approve(["--help"])

        assert result == 0
        captured = capsys.readouterr()
        assert "approve" in captured.out.lower()
        assert "kent" in captured.out.lower() or "principle" in captured.out.lower()

    def test_short_help_flag(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """-h prints help and returns 0."""
        result = cmd_soul_approve(["-h"])

        assert result == 0
        captured = capsys.readouterr()
        assert "approve" in captured.out.lower()


# === Error Handling Tests ===


class TestSoulApproveErrors:
    """Tests for error conditions."""

    def test_no_action_returns_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """No action description returns error."""
        result = cmd_soul_approve([])

        assert result == 2  # Error code 2 for errors
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "no" in captured.out.lower()

    def test_only_flags_returns_error(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Only flags without action returns error."""
        result = cmd_soul_approve(["--json"])

        assert result == 2
        captured = capsys.readouterr()
        assert "error" in captured.out.lower() or "no" in captured.out.lower()


# === Alternative Suggestions Tests ===


class TestSuggestAlternative:
    """Tests for _suggest_alternative function."""

    def test_suggest_alternative_for_delete_tests(self) -> None:
        """Suggests alternative for deleting tests."""
        result = _suggest_alternative("delete all tests", "minimal principle")

        assert "refactor" in result.lower() or "test" in result.lower()

    def test_suggest_alternative_for_skip_tests(self) -> None:
        """Suggests alternative for skipping tests."""
        result = _suggest_alternative("skip writing tests", "minimal principle")

        assert "minimal" in result.lower() or "test" in result.lower()

    def test_suggest_alternative_for_skip_docs(self) -> None:
        """Suggests alternative for skipping docs."""
        result = _suggest_alternative("skip documentation", "minimal principle")

        assert "comment" in result.lower() or "doc" in result.lower()

    def test_suggest_alternative_for_abstraction(self) -> None:
        """Suggests alternative for adding abstraction."""
        result = _suggest_alternative("add another abstraction layer", "")

        assert "abstraction" in result.lower() or "compress" in result.lower()

    def test_suggest_alternative_generic(self) -> None:
        """Provides generic alternative for unknown patterns."""
        result = _suggest_alternative("do something weird", "unknown reasoning")

        assert len(result) > 0  # Should always provide something


# === Integration Tests (with mock) ===


class TestSoulApproveIntegration:
    """Integration tests with mocked KgentSoul."""

    def test_approve_would_approve(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """soul approve returns 0 for approved actions."""
        # Mock intercept_deep to approve
        mock_result = AsyncMock()
        mock_result.recommendation = "approve"
        mock_result.reasoning = "Aligns with minimalism principle"
        mock_result.matching_principles = ["Aesthetic: Minimalism"]
        mock_result.confidence = 0.9

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["delete unused code"])
        finally:
            set_soul(None)  # Reset

        assert result == 0  # Would approve
        captured = capsys.readouterr()
        assert "WOULD APPROVE" in captured.out

    def test_approve_would_not_approve(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """soul approve returns 1 for rejected actions."""
        # Mock intercept_deep to reject
        mock_result = AsyncMock()
        mock_result.recommendation = "reject"
        mock_result.reasoning = "Violates quality principles"
        mock_result.matching_principles = ["Quality over speed"]
        mock_result.confidence = 0.8

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["skip all tests"])
        finally:
            set_soul(None)  # Reset

        assert result == 1  # Would not approve
        captured = capsys.readouterr()
        assert "WOULD NOT APPROVE" in captured.out

    def test_approve_shows_violations(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """soul approve shows principle violations."""
        # Mock intercept_deep to reject with violations
        mock_result = AsyncMock()
        mock_result.recommendation = "reject"
        mock_result.reasoning = "Multiple violations"
        mock_result.matching_principles = [
            "Aesthetic: Minimalism",
            "Gratitude: Sacred over utilitarian",
        ]
        mock_result.confidence = 0.9

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["add complex framework"])
        finally:
            set_soul(None)  # Reset

        assert result == 1
        captured = capsys.readouterr()
        assert "PRINCIPLE VIOLATIONS" in captured.out or "VIOLATION" in captured.out

    def test_approve_shows_alternative(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """soul approve shows alternative suggestion."""
        # Mock intercept_deep to reject
        mock_result = AsyncMock()
        mock_result.recommendation = "reject"
        mock_result.reasoning = "Not minimal enough"
        mock_result.matching_principles = ["Aesthetic: Minimalism"]
        mock_result.confidence = 0.85

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["delete all tests"])
        finally:
            set_soul(None)  # Reset

        assert result == 1
        captured = capsys.readouterr()
        assert "ALTERNATIVE" in captured.out

    def test_approve_escalate(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """soul approve handles escalate recommendation."""
        # Mock intercept_deep to escalate
        mock_result = AsyncMock()
        mock_result.recommendation = "escalate"
        mock_result.reasoning = "Requires human judgment"
        mock_result.matching_principles = ["SAFETY_OVERRIDE"]
        mock_result.confidence = 0.5

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["production database migration"])
        finally:
            set_soul(None)  # Reset

        assert result == 1  # Escalate treated as "would not approve"
        captured = capsys.readouterr()
        assert "WOULD NOT APPROVE" in captured.out

    def test_approve_json_mode(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--json flag outputs JSON."""
        import json

        # Mock intercept_deep
        mock_result = AsyncMock()
        mock_result.recommendation = "approve"
        mock_result.reasoning = "Good idea"
        mock_result.matching_principles = ["Test principle"]
        mock_result.confidence = 0.9

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["test action", "--json"])
        finally:
            set_soul(None)  # Reset

        assert result == 0
        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "command" in data
        assert data["command"] == "soul_approve"
        assert "result" in data
        assert "verdict" in data["result"]


# === Verdict Tests ===


class TestVerdicts:
    """Tests for verdict logic."""

    def test_approve_recommendation_gives_approve_verdict(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """approve recommendation → WOULD APPROVE verdict."""
        mock_result = AsyncMock()
        mock_result.recommendation = "approve"
        mock_result.reasoning = "Good"
        mock_result.matching_principles = []
        mock_result.confidence = 0.9

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["good action"])
        finally:
            set_soul(None)  # Reset

        assert result == 0

    def test_reject_recommendation_gives_reject_verdict(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """reject recommendation → WOULD NOT APPROVE verdict."""
        mock_result = AsyncMock()
        mock_result.recommendation = "reject"
        mock_result.reasoning = "Bad"
        mock_result.matching_principles = []
        mock_result.confidence = 0.8

        mock_soul = AsyncMock()
        mock_soul.intercept_deep = AsyncMock(return_value=mock_result)

        # Use set_soul to inject the mock
        set_soul(mock_soul)
        try:
            result = cmd_soul_approve(["bad action"])
        finally:
            set_soul(None)  # Reset

        assert result == 1
