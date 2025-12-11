"""
Tests for T-gents Phase 5: Security & Permissions

Tests ABAC (Attribute-Based Access Control), short-lived tokens,
and audit logging for secure tool execution.

Test Coverage:
1. Permission classification (ABAC rules)
2. Short-lived token generation and validation
3. Token expiration and revocation
4. Audit logging
5. SecureToolExecutor integration
6. Permission denial scenarios
7. Custom permission rules
"""

import pytest
from agents.t.executor import SecureToolExecutor
from agents.t.permissions import (
    AgentContext,
    AuditLogger,
    PermissionClassifier,
    PermissionLevel,
    SecurityLevel,
    ToolCapabilities,
)
from agents.t.tool import Tool, ToolErrorType, ToolMeta

# --- Test Fixtures ---


class SimpleStringTool(Tool[str, str]):
    """Simple tool for testing (echoes input)."""

    meta = ToolMeta.minimal(
        name="echo_tool",
        description="Echoes input string",
        input_schema=str,
        output_schema=str,
    )

    async def invoke(self, input: str) -> str:
        return f"Echo: {input}"


class NetworkTool(Tool[str, str]):
    """Tool that requires network access."""

    meta = ToolMeta.minimal(
        name="network_tool",
        description="Requires network",
        input_schema=str,
        output_schema=str,
    )

    async def invoke(self, input: str) -> str:
        return f"Network result: {input}"


@pytest.fixture
def basic_context():
    """Basic agent context for testing."""
    return AgentContext(
        agent_id="test_agent",
        security_level=SecurityLevel.MEDIUM,
        allow_network=True,
        allow_file_access=True,
    )


@pytest.fixture
def high_security_context():
    """High security context (restrictive)."""
    return AgentContext(
        agent_id="secure_agent",
        security_level=SecurityLevel.HIGH,
        allow_network=False,
        allow_file_access=False,
        allow_code_execution=False,
    )


@pytest.fixture
def classifier():
    """Permission classifier instance."""
    return PermissionClassifier()


@pytest.fixture
def audit_logger():
    """Audit logger instance."""
    return AuditLogger()


# --- Permission Classification Tests ---


class TestPermissionClassifier:
    """Test ABAC permission classification."""

    def test_basic_permission_allowed(self, classifier, basic_context) -> None:
        """Test basic permission grant."""
        caps = ToolCapabilities(requires_network=False)
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.ALLOWED_AUDITED

    def test_network_permission_allowed(self, classifier, basic_context) -> None:
        """Test network permission when allowed."""
        caps = ToolCapabilities(requires_network=True)
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.ALLOWED_AUDITED

    def test_network_permission_denied(self, classifier, high_security_context) -> None:
        """Test network permission denied in high security."""
        caps = ToolCapabilities(requires_network=True)
        permission = classifier.classify(caps, high_security_context)
        assert permission == PermissionLevel.DENIED

    def test_file_write_denied_without_access(self, classifier) -> None:
        """Test file write denied when context forbids it."""
        caps = ToolCapabilities(requires_file_write=True)
        context = AgentContext(
            agent_id="test",
            allow_file_access=False,
        )
        permission = classifier.classify(caps, context)
        assert permission == PermissionLevel.DENIED

    def test_pii_access_denied_without_authorization(
        self, classifier, basic_context
    ) -> None:
        """Test PII access denied without authorization."""
        caps = ToolCapabilities(accesses_pii=True)
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.DENIED

    def test_pii_access_allowed_with_authorization(self, classifier) -> None:
        """Test PII access allowed when authorized."""
        caps = ToolCapabilities(accesses_pii=True)
        context = AgentContext(
            agent_id="test",
            pii_authorized=True,
        )
        permission = classifier.classify(caps, context)
        assert permission == PermissionLevel.ALLOWED_AUDITED

    def test_cost_budget_exceeded(self, classifier, basic_context) -> None:
        """Test permission denied when cost exceeds budget."""
        caps = ToolCapabilities(max_cost_usd=10.0)
        basic_context.max_cost_usd = 1.0
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.DENIED

    def test_user_approval_required(self, classifier) -> None:
        """Test restricted permission when user approval needed."""
        caps = ToolCapabilities(requires_user_approval=True)
        context = AgentContext(
            agent_id="test",
            user_present=False,
        )
        permission = classifier.classify(caps, context)
        assert permission == PermissionLevel.RESTRICTED

    def test_production_environment_always_audited(self, classifier) -> None:
        """Test production environment forces audit."""
        caps = ToolCapabilities()
        context = AgentContext(
            agent_id="test",
            environment="production",
        )
        permission = classifier.classify(caps, context)
        assert permission == PermissionLevel.ALLOWED_AUDITED

    def test_critical_security_blocks_risky_operations(self, classifier) -> None:
        """Test critical security blocks network/code execution."""
        caps = ToolCapabilities(requires_code_execution=True)
        context = AgentContext(
            agent_id="test",
            security_level=SecurityLevel.CRITICAL,
        )
        permission = classifier.classify(caps, context)
        assert permission == PermissionLevel.DENIED


# --- Custom Permission Rules Tests ---


class TestCustomPermissionRules:
    """Test custom permission rule addition."""

    def test_custom_rule_override(self, classifier, basic_context) -> None:
        """Test custom rule can override default classification."""

        def allow_all_in_dev(caps, ctx):
            if ctx.environment == "development":
                return PermissionLevel.ALLOWED
            return None

        classifier.add_rule(allow_all_in_dev)

        basic_context.environment = "development"
        caps = ToolCapabilities(requires_network=True)

        permission = classifier.classify(caps, basic_context)
        # Custom rule should return ALLOWED (not ALLOWED_AUDITED)
        assert permission == PermissionLevel.ALLOWED

    def test_multiple_custom_rules(self, classifier, basic_context) -> None:
        """Test multiple custom rules checked in order."""

        def deny_expensive(caps, ctx):
            if caps.max_cost_usd > 5.0:
                return PermissionLevel.DENIED
            return None

        def allow_readonly(caps, ctx):
            if not caps.requires_file_write:
                return PermissionLevel.ALLOWED
            return None

        classifier.add_rule(deny_expensive)
        classifier.add_rule(allow_readonly)

        # First rule should trigger
        caps = ToolCapabilities(max_cost_usd=10.0)
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.DENIED

        # Second rule should trigger
        caps = ToolCapabilities(requires_file_read=True)
        permission = classifier.classify(caps, basic_context)
        assert permission == PermissionLevel.ALLOWED


# --- Short-Lived Token Tests ---


class TestTemporaryToken:
    """Test short-lived token generation and validation."""

    def test_token_generation(self, classifier, basic_context) -> None:
        """Test token generation for allowed permission."""
        caps = ToolCapabilities()
        result = classifier.grant_temporary(
            tool_id="test_tool",
            capabilities=caps,
            context=basic_context,
            duration_seconds=900,
        )

        assert result.is_ok()
        token = result.value
        assert token.tool_id == "test_tool"
        assert token.context_id == basic_context.agent_id
        assert token.is_valid()

    def test_token_denied_for_denied_permission(
        self, classifier, high_security_context
    ):
        """Test token not granted when permission denied."""
        caps = ToolCapabilities(requires_network=True)
        result = classifier.grant_temporary(
            tool_id="network_tool",
            capabilities=caps,
            context=high_security_context,
        )

        assert result.is_err()
        assert "denied" in result.message.lower()

    def test_token_expiration(self, classifier, basic_context) -> None:
        """Test token expires after duration."""
        caps = ToolCapabilities()
        result = classifier.grant_temporary(
            tool_id="test_tool",
            capabilities=caps,
            context=basic_context,
            duration_seconds=0,  # Expires immediately
        )

        assert result.is_ok()
        token = result.value

        # Wait a moment for expiration
        import time

        time.sleep(0.1)

        assert not token.is_valid()

    def test_token_use_tracking(self, classifier, basic_context) -> None:
        """Test token use count tracking."""
        caps = ToolCapabilities()
        result = classifier.grant_temporary(
            tool_id="test_tool",
            capabilities=caps,
            context=basic_context,
        )

        token = result.value
        assert token.uses == 0

        # Use token
        use_result = token.use()
        assert use_result.is_ok()
        assert token.uses == 1

        # Use again
        use_result = token.use()
        assert use_result.is_ok()
        assert token.uses == 2

    def test_token_revocation(self, classifier, basic_context) -> None:
        """Test token can be revoked."""
        caps = ToolCapabilities()
        result = classifier.grant_temporary(
            tool_id="test_tool",
            capabilities=caps,
            context=basic_context,
        )

        token = result.value
        assert token.is_valid()

        # Revoke token
        token.revoke("Security incident")
        assert not token.is_valid()
        assert token.revoked
        assert token.revocation_reason == "Security incident"

        # Cannot use revoked token
        use_result = token.use()
        assert use_result.is_err()
        assert "revoked" in use_result.message.lower()

    def test_expired_token_use(self, classifier, basic_context) -> None:
        """Test cannot use expired token."""
        caps = ToolCapabilities()
        result = classifier.grant_temporary(
            tool_id="test_tool",
            capabilities=caps,
            context=basic_context,
            duration_seconds=-1,  # Already expired
        )

        token = result.value
        use_result = token.use()
        assert use_result.is_err()
        assert "expired" in use_result.message.lower()


# --- Audit Logging Tests ---


class TestAuditLogger:
    """Test audit logging functionality."""

    @pytest.mark.asyncio
    async def test_permission_check_logging(self, audit_logger, basic_context) -> None:
        """Test logging of permission checks."""
        await audit_logger.log_permission_check(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=basic_context,
            permission=PermissionLevel.ALLOWED_AUDITED,
        )

        logs = audit_logger.get_logs()
        assert len(logs) == 1
        assert logs[0].tool_id == "test_tool"
        assert logs[0].permission == PermissionLevel.ALLOWED_AUDITED

    @pytest.mark.asyncio
    async def test_execution_logging(self, audit_logger, basic_context) -> None:
        """Test logging of tool executions."""
        await audit_logger.log_execution(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=basic_context,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="test input",
            success=True,
            output_summary="test output",
            duration_ms=150.0,
        )

        logs = audit_logger.get_logs()
        assert len(logs) == 1
        log = logs[0]
        assert log.success
        assert log.input_summary == "test input"
        assert log.output_summary == "test output"
        assert log.duration_ms == 150.0

    @pytest.mark.asyncio
    async def test_failure_logging(self, audit_logger, basic_context) -> None:
        """Test logging of failed executions."""
        await audit_logger.log_execution(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=basic_context,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="test input",
            success=False,
            error="Network timeout",
        )

        logs = audit_logger.get_logs()
        assert len(logs) == 1
        log = logs[0]
        assert not log.success
        assert log.error == "Network timeout"
        assert log.flagged  # Should be flagged for review

    @pytest.mark.asyncio
    async def test_restricted_permission_flagged(
        self, audit_logger, basic_context
    ) -> None:
        """Test restricted permissions are flagged."""
        await audit_logger.log_execution(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=basic_context,
            permission=PermissionLevel.RESTRICTED,
            input_summary="test input",
            success=True,
        )

        logs = audit_logger.get_logs(flagged_only=True)
        assert len(logs) == 1
        assert logs[0].flagged
        assert "restricted" in logs[0].flag_reason.lower()

    @pytest.mark.asyncio
    async def test_log_filtering_by_tool(self, audit_logger, basic_context) -> None:
        """Test filtering logs by tool ID."""
        await audit_logger.log_execution(
            tool_id="tool_a",
            tool_name="Tool A",
            context=basic_context,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="input a",
            success=True,
        )

        await audit_logger.log_execution(
            tool_id="tool_b",
            tool_name="Tool B",
            context=basic_context,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="input b",
            success=True,
        )

        tool_a_logs = audit_logger.get_logs(tool_id="tool_a")
        assert len(tool_a_logs) == 1
        assert tool_a_logs[0].tool_id == "tool_a"

    @pytest.mark.asyncio
    async def test_log_filtering_by_context(self, audit_logger) -> None:
        """Test filtering logs by context ID."""
        context_a = AgentContext(agent_id="agent_a")
        context_b = AgentContext(agent_id="agent_b")

        await audit_logger.log_execution(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=context_a,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="input",
            success=True,
        )

        await audit_logger.log_execution(
            tool_id="test_tool",
            tool_name="Test Tool",
            context=context_b,
            permission=PermissionLevel.ALLOWED_AUDITED,
            input_summary="input",
            success=True,
        )

        context_a_logs = audit_logger.get_logs(context_id="agent_a")
        assert len(context_a_logs) == 1
        assert context_a_logs[0].context_id == "agent_a"


# --- SecureToolExecutor Integration Tests ---


class TestSecureToolExecutor:
    """Test secure tool executor with permissions."""

    @pytest.mark.asyncio
    async def test_execute_with_permission(self, basic_context) -> None:
        """Test successful execution with permission."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
        )

        result = await executor.execute("test input")
        assert result.is_ok()
        assert result.value == "Echo: test input"

    @pytest.mark.asyncio
    async def test_execute_denied_without_permission(
        self, high_security_context
    ) -> None:
        """Test execution denied without permission."""
        tool = NetworkTool()
        caps = ToolCapabilities(requires_network=True)

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=high_security_context,
        )

        result = await executor.execute("test input")
        assert result.is_err()
        assert result.error.error_type == ToolErrorType.PERMISSION
        assert "denied" in result.error.message.lower()

    @pytest.mark.asyncio
    async def test_execute_with_token(self, basic_context) -> None:
        """Test execution using short-lived token."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
        )

        # Request token
        token_result = await executor.request_permission(duration_seconds=60)
        assert token_result.is_ok()

        # Execute with token
        result = await executor.execute("test input")
        assert result.is_ok()
        assert result.value == "Echo: test input"

        # Token should be marked as used
        assert executor.token.uses == 1

    @pytest.mark.asyncio
    async def test_execute_with_expired_token(self, basic_context) -> None:
        """Test execution fails with expired token."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
        )

        # Request token with 0 duration (expires immediately)
        token_result = await executor.request_permission(duration_seconds=0)
        assert token_result.is_ok()

        # Wait for expiration
        import time

        time.sleep(0.1)

        # Execute should fail
        result = await executor.execute("test input")
        assert result.is_err()
        assert "expired" in result.error.message.lower()

    @pytest.mark.asyncio
    async def test_audit_log_created(self, basic_context) -> None:
        """Test audit log created for execution."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()
        audit_logger = AuditLogger()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
            audit_logger=audit_logger,
        )

        await executor.execute("test input")

        logs = audit_logger.get_logs()
        assert len(logs) >= 1  # At least execution log
        assert logs[-1].tool_id == tool.name
        assert logs[-1].success

    @pytest.mark.asyncio
    async def test_permission_status(self, basic_context) -> None:
        """Test getting permission status."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
        )

        status = executor.get_permission_status()
        assert status["permission"] == PermissionLevel.ALLOWED_AUDITED.value
        assert status["tool"] == tool.name
        assert status["token"] is None

        # Request token
        await executor.request_permission()
        status = executor.get_permission_status()
        assert status["token"] is not None
        assert status["token"]["valid"]


# --- Integration Tests ---


class TestSecurityIntegration:
    """Test full security integration scenarios."""

    @pytest.mark.asyncio
    async def test_production_workflow_with_audit(self) -> None:
        """Test complete production workflow with auditing."""
        tool = SimpleStringTool()
        caps = ToolCapabilities()
        context = AgentContext(
            agent_id="prod_agent",
            environment="production",
            security_level=SecurityLevel.MEDIUM,
        )
        audit_logger = AuditLogger()

        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=context,
            audit_logger=audit_logger,
        )

        # Request token
        token_result = await executor.request_permission(duration_seconds=300)
        assert token_result.is_ok()

        # Execute multiple times
        for i in range(3):
            result = await executor.execute(f"input {i}")
            assert result.is_ok()

        # Check audit trail
        logs = audit_logger.get_logs()
        assert len(logs) >= 4  # 1 permission check + 3 executions
        assert all(log.context_id == "prod_agent" for log in logs)

    @pytest.mark.asyncio
    async def test_security_escalation_scenario(self, basic_context) -> None:
        """Test security context change mid-execution."""
        tool = NetworkTool()
        caps = ToolCapabilities(requires_network=True)

        # Start with permissive context
        executor = SecureToolExecutor(
            tool=tool,
            capabilities=caps,
            context=basic_context,
        )

        result = await executor.execute("initial request")
        assert result.is_ok()

        # Change context to high security
        executor.context.security_level = SecurityLevel.HIGH
        executor.context.allow_network = False

        # New execution should be denied
        result = await executor.execute("escalated request")
        assert result.is_err()
        assert result.error.error_type == ToolErrorType.PERMISSION
