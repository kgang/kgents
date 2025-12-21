"""
Fail-Fast Audit Tests.

These tests enforce the fail-fast principle across Crown Jewels:
1. No silent exception swallowing (except: pass)
2. No DEBUG-level import failures for Crown Jewels
3. DI container warns on missing dependencies

See: plans/fail-fast-crown-jewel-audit.md

Run with: pytest services/_tests/test_fail_fast_audit.py -v
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

# Get the impl/claude directory
IMPL_CLAUDE = Path(__file__).parent.parent.parent


class TestNoSilentExceptionSwallowing:
    """Ensure no silent `except: pass` in services/."""

    # Files where silent catch is intentionally acceptable (document why!)
    ALLOWED_FILES = [
        "bus_wiring.py",  # Event subscription cleanup (expected failures)
    ]

    def test_no_except_pass_in_services(self):
        """Grep for 'except.*: pass' patterns in services/."""
        result = subprocess.run(
            [
                "grep",
                "-r",
                "-n",
                "--include=*.py",  # Only Python files
                "except.*:.*pass",
                str(IMPL_CLAUDE / "services"),
            ],
            capture_output=True,
            text=True,
        )

        # Filter out allowed files and this test file itself
        violations = [
            line
            for line in result.stdout.splitlines()
            if not any(f in line for f in self.ALLOWED_FILES)
            and "test_fail_fast_audit.py" not in line  # Exclude self
            and "# intentional-silent" not in line  # Escape hatch
        ]

        if violations:
            pytest.fail(
                "Silent exception swallowing found:\n"
                + "\n".join(violations)
                + "\n\nFix: Log the exception at WARNING level or re-raise."
            )


class TestDIProviderCompleteness:
    """Ensure DI providers are complete."""

    def test_audit_script_exists(self):
        """The DI audit script should exist."""
        script_path = IMPL_CLAUDE / "scripts" / "audit_di_providers.py"
        assert script_path.exists(), f"Missing: {script_path}"

    def test_all_dependencies_have_providers(self):
        """Run the DI audit script and check for missing providers."""
        script_path = IMPL_CLAUDE / "scripts" / "audit_di_providers.py"
        if not script_path.exists():
            pytest.skip("DI audit script not found")

        result = subprocess.run(
            ["python", str(script_path)],
            cwd=str(IMPL_CLAUDE),
            capture_output=True,
            text=True,
        )

        # Script should succeed
        if result.returncode != 0:
            pytest.fail(f"DI audit failed:\n{result.stderr}\n{result.stdout}")

        # Check for warnings about missing providers
        if "missing" in result.stdout.lower() or "missing" in result.stderr.lower():
            pytest.fail(f"Missing DI providers:\n{result.stdout}")


class TestImportLogging:
    """Ensure Crown Jewel imports are logged at visible level."""

    def test_no_debug_crown_jewel_imports(self):
        """Crown Jewel import failures should be WARNING, not DEBUG."""
        providers_path = IMPL_CLAUDE / "services" / "providers.py"
        content = providers_path.read_text()

        # Find all logger.debug calls related to node availability
        debug_node_pattern = r'logger\.debug\(f".*Node not available'
        matches = re.findall(debug_node_pattern, content)

        if matches:
            pytest.fail(
                "Crown Jewel import failures at DEBUG level:\n"
                + "\n".join(matches)
                + "\n\nFix: Change logger.debug to logger.warning for Crown Jewel nodes."
            )


class TestExceptionException:
    """Ensure Exception handling is visible."""

    def test_container_fails_fast_on_missing_required_deps(self):
        """DI container should fail fast on missing REQUIRED dependencies.

        Design decision (Enlightened Resolution):
        - REQUIRED deps (no default in __init__) → DependencyNotFoundError immediately
        - OPTIONAL deps (= None default) → skip gracefully, use default (DEBUG level)

        This is intentional for:
        - Required deps: Fail fast with actionable error message
        - Optional deps: Graceful degradation (e.g., SoulNode without LLM)
        """
        container_path = IMPL_CLAUDE / "protocols" / "agentese" / "container.py"
        content = container_path.read_text()

        # The container should raise DependencyNotFoundError for missing required deps
        assert "DependencyNotFoundError" in content, \
            "Container should define DependencyNotFoundError for missing required deps"

        # The error should include actionable guidance
        assert "Fix:" in content, \
            "Container error messages should include actionable Fix guidance"
