"""
Tests for BoundaryChecker: Forbidden Actions.

Verifies:
- Forbidden action patterns are detected
- Substring matching works
- Category classification
- Normal actions pass through
"""

import pytest

from services.witness.trust.boundaries import (
    FORBIDDEN_ACTIONS,
    FORBIDDEN_SUBSTRINGS,
    BoundaryChecker,
    BoundaryViolation,
)


class TestBoundaryChecker:
    """Tests for BoundaryChecker."""

    @pytest.fixture
    def checker(self) -> BoundaryChecker:
        """Create a boundary checker for testing."""
        return BoundaryChecker()

    # =========================================================================
    # Git Operations
    # =========================================================================

    def test_force_push_forbidden(self, checker: BoundaryChecker) -> None:
        """Force push to main is forbidden."""
        violation = checker.check("git push --force origin main")

        assert violation is not None
        assert violation.category == "git"
        assert "force" in violation.pattern.lower()

    def test_force_push_short_flag_forbidden(self, checker: BoundaryChecker) -> None:
        """Force push with -f is forbidden."""
        violation = checker.check("git push -f origin main")

        assert violation is not None
        assert violation.category == "git"

    def test_normal_push_allowed(self, checker: BoundaryChecker) -> None:
        """Normal push is allowed."""
        violation = checker.check("git push origin feature-branch")

        assert violation is None

    def test_hard_reset_forbidden(self, checker: BoundaryChecker) -> None:
        """Hard reset is forbidden."""
        violation = checker.check("git reset --hard HEAD~5")

        assert violation is not None
        assert violation.category == "git"

    def test_soft_reset_allowed(self, checker: BoundaryChecker) -> None:
        """Soft reset is allowed."""
        violation = checker.check("git reset --soft HEAD~1")

        assert violation is None

    # =========================================================================
    # Filesystem Operations
    # =========================================================================

    def test_rm_rf_root_forbidden(self, checker: BoundaryChecker) -> None:
        """rm -rf / is forbidden."""
        violation = checker.check("rm -rf /")

        assert violation is not None
        assert violation.category == "filesystem"

    def test_rm_rf_home_forbidden(self, checker: BoundaryChecker) -> None:
        """rm -rf ~ is forbidden."""
        violation = checker.check("rm -rf ~")

        assert violation is not None

    def test_sudo_rm_forbidden(self, checker: BoundaryChecker) -> None:
        """sudo rm is forbidden."""
        violation = checker.check("sudo rm -rf /var/log")

        assert violation is not None
        assert violation.category == "filesystem"

    def test_normal_rm_allowed(self, checker: BoundaryChecker) -> None:
        """Normal rm is allowed."""
        violation = checker.check("rm temp_file.txt")

        assert violation is None

    # =========================================================================
    # Database Operations
    # =========================================================================

    def test_drop_database_forbidden(self, checker: BoundaryChecker) -> None:
        """DROP DATABASE is forbidden."""
        violation = checker.check("DROP DATABASE production")

        assert violation is not None
        assert violation.category == "database"

    def test_drop_table_forbidden(self, checker: BoundaryChecker) -> None:
        """DROP TABLE is forbidden."""
        violation = checker.check("DROP TABLE users")

        assert violation is not None

    def test_delete_from_forbidden(self, checker: BoundaryChecker) -> None:
        """DELETE FROM is forbidden."""
        violation = checker.check("DELETE FROM users")

        assert violation is not None
        assert violation.category == "database"

    def test_select_allowed(self, checker: BoundaryChecker) -> None:
        """SELECT is allowed."""
        violation = checker.check("SELECT * FROM users WHERE id = 1")

        assert violation is None

    # =========================================================================
    # Infrastructure Operations
    # =========================================================================

    def test_kubectl_delete_namespace_forbidden(self, checker: BoundaryChecker) -> None:
        """kubectl delete namespace is forbidden."""
        violation = checker.check("kubectl delete namespace production")

        assert violation is not None
        assert violation.category == "infrastructure"

    def test_terraform_destroy_forbidden(self, checker: BoundaryChecker) -> None:
        """terraform destroy is forbidden."""
        violation = checker.check("terraform destroy -auto-approve")

        assert violation is not None

    def test_kubectl_get_allowed(self, checker: BoundaryChecker) -> None:
        """kubectl get is allowed."""
        violation = checker.check("kubectl get pods")

        assert violation is None

    # =========================================================================
    # Credential Operations
    # =========================================================================

    def test_cat_ssh_forbidden(self, checker: BoundaryChecker) -> None:
        """Reading SSH keys is forbidden."""
        violation = checker.check("cat ~/.ssh/id_rsa")

        assert violation is not None
        assert violation.category == "credentials"

    def test_vault_read_forbidden(self, checker: BoundaryChecker) -> None:
        """Vault read is forbidden."""
        violation = checker.check("vault read secret/production")

        assert violation is not None
        assert violation.category == "credentials"

    def test_cat_env_forbidden(self, checker: BoundaryChecker) -> None:
        """Reading .env is forbidden."""
        violation = checker.check("cat .env")

        assert violation is not None
        assert violation.category == "credentials"

    # =========================================================================
    # Financial Operations
    # =========================================================================

    def test_stripe_forbidden(self, checker: BoundaryChecker) -> None:
        """Stripe operations are forbidden."""
        violation = checker.check("stripe charges create --amount 1000")

        assert violation is not None
        assert violation.category == "financial"

    # =========================================================================
    # Publication Operations
    # =========================================================================

    def test_npm_publish_forbidden(self, checker: BoundaryChecker) -> None:
        """npm publish is forbidden."""
        violation = checker.check("npm publish --access public")

        assert violation is not None
        assert violation.category == "publication"

    def test_docker_push_forbidden(self, checker: BoundaryChecker) -> None:
        """docker push is forbidden."""
        violation = checker.check("docker push myimage:latest")

        assert violation is not None

    # =========================================================================
    # Substring Matching
    # =========================================================================

    def test_substring_force_push(self, checker: BoundaryChecker) -> None:
        """Substring matching catches 'force push'."""
        violation = checker.check("I want to force push this branch")

        assert violation is not None
        assert "force push" in violation.pattern.lower()

    def test_substring_api_key(self, checker: BoundaryChecker) -> None:
        """Substring matching catches 'api_key'."""
        violation = checker.check("export MY_API_KEY=secret123")

        assert violation is not None

    def test_substring_password(self, checker: BoundaryChecker) -> None:
        """Substring matching catches 'password='."""
        violation = checker.check("mysql -u root -ppassword=mysecret")

        assert violation is not None

    # =========================================================================
    # Case Insensitivity
    # =========================================================================

    def test_case_insensitive_drop_database(self, checker: BoundaryChecker) -> None:
        """Case insensitive matching for DROP DATABASE."""
        violation = checker.check("drop database production")
        assert violation is not None

        violation = checker.check("DrOp DaTaBaSe production")
        assert violation is not None

    # =========================================================================
    # is_allowed
    # =========================================================================

    def test_is_allowed_true(self, checker: BoundaryChecker) -> None:
        """is_allowed returns True for allowed actions."""
        assert checker.is_allowed("git commit -m 'fix: typo'")
        assert checker.is_allowed("pytest tests/")
        assert checker.is_allowed("npm install lodash")

    def test_is_allowed_false(self, checker: BoundaryChecker) -> None:
        """is_allowed returns False for forbidden actions."""
        assert not checker.is_allowed("git push --force")
        assert not checker.is_allowed("DROP TABLE users")
        assert not checker.is_allowed("npm publish")


class TestForbiddenActionsCompleteness:
    """Ensure FORBIDDEN_ACTIONS has expected entries."""

    def test_contains_git_operations(self) -> None:
        """FORBIDDEN_ACTIONS contains git operations."""
        git_patterns = [p for p in FORBIDDEN_ACTIONS if "git" in p.lower()]
        assert len(git_patterns) >= 5  # At least 5 git patterns

    def test_contains_filesystem_operations(self) -> None:
        """FORBIDDEN_ACTIONS contains filesystem operations."""
        fs_patterns = [p for p in FORBIDDEN_ACTIONS if "rm" in p.lower() or "chmod" in p.lower()]
        assert len(fs_patterns) >= 3

    def test_contains_database_operations(self) -> None:
        """FORBIDDEN_ACTIONS contains database operations."""
        db_patterns = [
            p
            for p in FORBIDDEN_ACTIONS
            if any(k in p.upper() for k in ["DROP", "DELETE", "TRUNCATE"])
        ]
        assert len(db_patterns) >= 3

    def test_contains_credential_patterns(self) -> None:
        """FORBIDDEN_ACTIONS contains credential patterns."""
        cred_patterns = [
            p
            for p in FORBIDDEN_ACTIONS
            if any(k in p.lower() for k in ["ssh", "vault", "aws", "env"])
        ]
        assert len(cred_patterns) >= 3
