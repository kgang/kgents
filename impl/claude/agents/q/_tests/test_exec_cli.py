"""
Tests for Q-gent CLI exec handler.
"""

from __future__ import annotations

import pytest
from protocols.cli.handlers.exec import _parse_args


class TestParseArgs:
    """Tests for argument parsing."""

    def test_code_flag(self):
        """Parse --code argument."""
        result = _parse_args(["--code", "print('hello')"])

        assert result["code"] == "print('hello')"

    def test_file_flag(self):
        """Parse --file argument."""
        result = _parse_args(["--file", "script.py"])

        assert result["file"] == "script.py"

    def test_lang_flag(self):
        """Parse --lang argument."""
        result = _parse_args(["--lang", "shell"])

        assert result["lang"] == "shell"

    def test_timeout_flag(self):
        """Parse --timeout argument."""
        result = _parse_args(["--timeout", "60"])

        assert result["timeout"] == 60

    def test_timeout_invalid(self):
        """Invalid timeout returns error."""
        result = _parse_args(["--timeout", "invalid"])

        assert "error" in result
        assert "Invalid timeout" in result["error"]

    def test_cpu_flag(self):
        """Parse --cpu argument."""
        result = _parse_args(["--cpu", "200m"])

        assert result["cpu"] == "200m"

    def test_memory_flag(self):
        """Parse --memory argument."""
        result = _parse_args(["--memory", "256Mi"])

        assert result["memory"] == "256Mi"

    def test_network_flag(self):
        """Parse --network flag."""
        result = _parse_args(["--network"])

        assert result["network"] is True

    def test_dry_run_flag(self):
        """Parse --dry-run flag."""
        result = _parse_args(["--dry-run"])

        assert result["dry_run"] is True

    def test_combined_flags(self):
        """Parse multiple flags together."""
        result = _parse_args(
            [
                "--code",
                "print('hello')",
                "--lang",
                "python",
                "--timeout",
                "30",
                "--cpu",
                "100m",
                "--memory",
                "128Mi",
                "--network",
                "--dry-run",
            ]
        )

        assert result["code"] == "print('hello')"
        assert result["lang"] == "python"
        assert result["timeout"] == 30
        assert result["cpu"] == "100m"
        assert result["memory"] == "128Mi"
        assert result["network"] is True
        assert result["dry_run"] is True

    def test_bare_code(self):
        """Bare argument treated as code."""
        result = _parse_args(["print('hello')"])

        assert result["code"] == "print('hello')"

    def test_missing_value_code(self):
        """Missing value for --code returns error."""
        result = _parse_args(["--code"])

        assert "error" in result

    def test_missing_value_file(self):
        """Missing value for --file returns error."""
        result = _parse_args(["--file"])

        assert "error" in result

    def test_missing_value_lang(self):
        """Missing value for --lang returns error."""
        result = _parse_args(["--lang"])

        assert "error" in result
