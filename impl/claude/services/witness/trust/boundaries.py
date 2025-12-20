"""
BoundaryChecker: Forbidden Actions That Should Never Be Autonomous.

"Some things should NEVER be autonomous, period. This is not negotiable."
"'Daring' doesn't mean 'reckless'."

These boundaries are hardcoded, not configurable. Even at Level 3 (AUTONOMOUS),
the Witness cannot perform these actions.

Categories:
- Destructive Git Operations: Force push to main, hard reset
- Filesystem Destruction: rm -rf dangerous paths
- Database Destruction: DROP, DELETE FROM
- Production Access: kubectl delete, docker rm
- Credential Access: Reading secrets, tokens
- Financial Operations: Stripe, PayPal
- External Publication: npm publish, pip upload

See: plans/kgentsd-trust-system.md (Design Decisions §3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Forbidden Action Patterns
# =============================================================================

# Hardcoded forbidden patterns - NOT configurable
FORBIDDEN_ACTIONS: frozenset[str] = frozenset(
    {
        # === Destructive Git Operations ===
        "git push --force",
        "git push -f",
        "git push --force-with-lease origin main",
        "git push --force-with-lease origin master",
        "git push --force origin main",
        "git push --force origin master",
        "git push -f origin main",
        "git push -f origin master",
        "git reset --hard",
        "git clean -fdx",
        "git checkout -- .",  # Discard all changes
        # === Filesystem Destruction ===
        "rm -rf /",
        "rm -rf ~",
        "rm -rf .",
        "rm -rf /*",
        "rm -rf ~/*",
        "rm -rf ./*",
        "sudo rm",
        "chmod -R 777",
        "chown -R",
        # === Database Destruction ===
        "DROP DATABASE",
        "DROP TABLE",
        "DROP SCHEMA",
        "DELETE FROM",  # Without WHERE is dangerous
        "TRUNCATE TABLE",
        # === Production Access ===
        "kubectl delete namespace",
        "kubectl delete deployment",
        "kubectl delete pod --all",
        "docker rm -f",
        "docker system prune -af",
        "docker volume prune -f",
        "terraform destroy",
        # === Credential Access ===
        "cat ~/.ssh",
        "cat ~/.aws",
        "cat ~/.config/gcloud",
        "vault token",
        "vault read",
        "aws secretsmanager",
        "gcloud secrets",
        "cat .env",
        "cat credentials",
        # === Financial Operations ===
        "stripe",
        "paypal",
        "braintree",
        "square",
        # === External Publication ===
        "npm publish",
        "pip upload",
        "twine upload",
        "docker push",
        "cargo publish",
        "gem push",
        # === Bypass Safety ===
        "--no-verify",
        "--skip-checks",
        "--force-yes",
        "-y --force",
    }
)


# Additional patterns that require substring matching
FORBIDDEN_SUBSTRINGS: frozenset[str] = frozenset(
    {
        "force push",
        "force-push",
        "hard reset",
        "drop database",
        "drop table",
        "delete namespace",
        "secrets read",
        "token create",
        "api_key",
        "apikey",
        "secret_key",
        "secretkey",
        "private_key",
        "privatekey",
        "password=",
        "passwd=",
    }
)


# =============================================================================
# Boundary Violation
# =============================================================================


@dataclass
class BoundaryViolation:
    """A detected boundary violation."""

    action: str
    pattern: str
    reason: str
    category: str
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# BoundaryChecker Class
# =============================================================================


class BoundaryChecker:
    """
    Checks actions against forbidden boundaries.

    All checks are case-insensitive.
    This is a hard stop - no trust level can bypass these.

    Example:
        checker = BoundaryChecker()

        # Force push is forbidden
        violation = checker.check("git push --force origin main")
        assert violation is not None
        assert violation.category == "git"

        # Normal push is allowed
        violation = checker.check("git push origin main")
        assert violation is None
    """

    def __init__(
        self,
        forbidden_actions: frozenset[str] | None = None,
        forbidden_substrings: frozenset[str] | None = None,
    ) -> None:
        """
        Initialize boundary checker.

        Args:
            forbidden_actions: Override default forbidden actions (for testing)
            forbidden_substrings: Override default substrings (for testing)
        """
        self.forbidden_actions = forbidden_actions or FORBIDDEN_ACTIONS
        self.forbidden_substrings = forbidden_substrings or FORBIDDEN_SUBSTRINGS

    def check(self, action: str) -> BoundaryViolation | None:
        """
        Check if an action violates boundaries.

        Args:
            action: The action string to check

        Returns:
            BoundaryViolation if forbidden, None if allowed
        """
        action_lower = action.lower()

        # Check exact matches (normalized)
        for pattern in self.forbidden_actions:
            if pattern.lower() in action_lower:
                return BoundaryViolation(
                    action=action,
                    pattern=pattern,
                    reason=f"Matches forbidden pattern: {pattern}",
                    category=self._categorize(pattern),
                )

        # Check substrings
        for substring in self.forbidden_substrings:
            if substring.lower() in action_lower:
                return BoundaryViolation(
                    action=action,
                    pattern=substring,
                    reason=f"Contains forbidden substring: {substring}",
                    category=self._categorize(substring),
                )

        return None

    def is_allowed(self, action: str) -> bool:
        """Quick check if action is allowed."""
        return self.check(action) is None

    def _categorize(self, pattern: str) -> str:
        """Categorize a forbidden pattern."""
        pattern_lower = pattern.lower()

        # Check most specific patterns first
        if "git" in pattern_lower or "reset" in pattern_lower:
            return "git"
        elif "rm" in pattern_lower or "chmod" in pattern_lower or "chown" in pattern_lower:
            return "filesystem"
        # Infrastructure before database (kubectl delete is infra, not db)
        elif any(k in pattern_lower for k in ["kubectl", "docker", "terraform"]):
            return "infrastructure"
        elif any(k in pattern_lower for k in ["drop", "truncate"]) or (
            "delete" in pattern_lower and "from" in pattern_lower
        ):
            return "database"
        # Credentials - include ssh, env, cat patterns
        elif any(
            k in pattern_lower
            for k in [
                "secret",
                "token",
                "key",
                "password",
                "credential",
                "vault",
                "aws",
                "gcloud",
                "ssh",
                ".env",
                "cat ",
            ]
        ):
            return "credentials"
        elif any(k in pattern_lower for k in ["stripe", "paypal", "braintree", "square"]):
            return "financial"
        elif any(k in pattern_lower for k in ["publish", "upload", "push"]):
            return "publication"
        else:
            return "other"


__all__ = [
    "BoundaryChecker",
    "BoundaryViolation",
    "FORBIDDEN_ACTIONS",
    "FORBIDDEN_SUBSTRINGS",
]
