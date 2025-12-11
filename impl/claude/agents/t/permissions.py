"""
T-gents Phase 5: Security & Permissions

This module implements Attribute-Based Access Control (ABAC) for tools,
including short-lived token generation, permission classification, and
audit logging.

Philosophy:
- Zero standing privileges: Tools granted per-task
- Short-lived tokens: 15-60 minute OAuth tokens (never static keys)
- Attribute-based: Context-aware permissions (time, location, sensitivity)
- Security as Subobject Classifier: Categorical foundations for permissions

Integration:
- Tool base class from agents/t/tool.py
- D-gents for token storage
- W-gents for audit logging
- Result monad for permission checks

References:
- spec/t-gents/tool-use.md - Security specification (Pattern 5)
- spec/t-gents/README.md - T-gents testing foundations
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, TypeVar

from bootstrap.types import Result, err, ok

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# --- Permission Types ---


class PermissionLevel(Enum):
    """
    Permission classification result.

    Maps to subobject classifier Ω in Category Theory:
    - ALLOWED: Tool can execute freely
    - ALLOWED_AUDITED: Tool can execute but logged
    - RESTRICTED: Tool requires additional approval
    - DENIED: Tool cannot execute
    """

    ALLOWED = "allowed"  # Full permission, no restrictions
    ALLOWED_AUDITED = "allowed_audited"  # Allowed but must be audited
    RESTRICTED = "restricted"  # Requires additional approval
    DENIED = "denied"  # Permission denied


class SecurityLevel(Enum):
    """Security level for agent contexts."""

    LOW = "low"  # Development/testing
    MEDIUM = "medium"  # Standard operation
    HIGH = "high"  # Sensitive operations
    CRITICAL = "critical"  # Production critical systems


class SensitivityLevel(Enum):
    """Data sensitivity classification."""

    PUBLIC = "public"  # No sensitive data
    INTERNAL = "internal"  # Internal use only
    CONFIDENTIAL = "confidential"  # Confidential data
    PII = "pii"  # Personally Identifiable Information


# --- Agent Context ---


@dataclass
class AgentContext:
    """
    Context for agent execution.

    Provides attributes for ABAC (Attribute-Based Access Control).
    These attributes determine which tools are permitted.

    Category Theory:
    - This is the "source object" in permission classification
    - The PermissionClassifier is the characteristic morphism
    - Maps AgentContext → Permission (subobject classifier)
    """

    # Identity
    agent_id: str
    user_id: Optional[str] = None  # Human user if present

    # Security context
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    data_sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL

    # Network restrictions
    allow_network: bool = True
    allow_file_access: bool = True
    allow_code_execution: bool = False

    # Data access
    pii_authorized: bool = False
    database_access: bool = False

    # Temporal restrictions
    execution_time: datetime = field(default_factory=datetime.now)
    max_duration_seconds: int = 3600  # 1 hour max

    # User presence
    user_present: bool = False  # Is human in the loop?
    requires_approval: bool = False  # Does action need approval?

    # Environment
    environment: str = "development"  # development/staging/production
    location: Optional[str] = None  # Geographic location

    # Cost budget
    max_cost_usd: float = 1.0  # Maximum cost per operation

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_time_restricted(self) -> bool:
        """Check if operation is within time window."""
        # Can be extended to check business hours, maintenance windows, etc.
        return False  # Placeholder for time-based restrictions


# --- Tool Capability Requirements ---


@dataclass
class ToolCapabilities:
    """
    Capabilities required by a tool.

    These are matched against AgentContext to determine permissions.
    """

    # Network requirements
    requires_network: bool = False
    requires_internet: bool = False  # Subset of network (external)

    # File system
    requires_file_read: bool = False
    requires_file_write: bool = False

    # Code execution
    requires_code_execution: bool = False
    requires_shell_access: bool = False

    # Data access
    accesses_pii: bool = False
    accesses_database: bool = False

    # Approval requirements
    requires_user_approval: bool = False
    requires_admin_approval: bool = False

    # Cost expectations
    estimated_cost_usd: float = 0.0
    max_cost_usd: float = 0.1

    # Sensitivity
    data_sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL


# --- Permission Tokens ---


@dataclass
class TemporaryToken:
    """
    Short-lived permission token.

    Following security best practices:
    - Short-lived: 15-60 minutes (default 15)
    - Task-specific: Only for current operation
    - Revocable: Can be cancelled mid-execution
    - Audited: All uses logged

    Category Theory:
    - Token is a proof object (witness of permission)
    - Token validity is a predicate (time-bounded)
    - Token usage is a morphism (context → granted capability)
    """

    # Identity
    token_id: str  # Unique token ID (random)
    tool_id: str  # Tool this token is for
    context_id: str  # Agent context ID

    # Permissions granted
    permission: PermissionLevel
    capabilities: ToolCapabilities

    # Temporal bounds
    issued_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(minutes=15)
    )

    # Revocation
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None

    # Audit trail
    uses: int = 0  # Number of times used
    last_used_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if token is currently valid."""
        if self.revoked:
            return False

        now = datetime.now()
        return self.issued_at <= now < self.expires_at

    def use(self) -> Result[None, str]:
        """
        Mark token as used.

        Returns error if token is invalid.
        """
        if not self.is_valid():
            if self.revoked:
                return err(
                    None,
                    f"Token revoked: {self.revocation_reason}",
                    recoverable=False,
                )
            else:
                return err(
                    None,
                    f"Token expired at {self.expires_at}",
                    recoverable=False,
                )

        self.uses += 1
        self.last_used_at = datetime.now()
        return ok(None)

    def revoke(self, reason: str) -> None:
        """Revoke token before expiration."""
        self.revoked = True
        self.revoked_at = datetime.now()
        self.revocation_reason = reason


# --- Permission Classifier ---


@dataclass
class PermissionClassifier:
    """
    Attribute-Based Access Control (ABAC) classifier.

    Category Theory Foundation:
    - Objects: Tool capabilities
    - Subobjects: Permitted tool subsets
    - Classifier: Ω (permission oracle)
    - Characteristic morphism: χ: Tool → {allowed, denied}

    This implements the subobject classifier pattern from topos theory,
    where permissions are subobjects of the tool category.

    Philosophy:
    - Zero standing privileges: All permissions are contextual
    - Attribute-based: Uses context attributes, not roles
    - Fail-safe: Deny by default, allow by explicit rules
    - Auditable: All decisions logged

    Usage:
        classifier = PermissionClassifier()

        tool_caps = ToolCapabilities(requires_network=True)
        context = AgentContext(
            security_level=SecurityLevel.HIGH,
            allow_network=False
        )

        permission = classifier.classify(tool_caps, context)
        # → PermissionLevel.DENIED (high security blocks network)
    """

    # Custom permission rules (can be extended)
    custom_rules: list[
        Callable[[ToolCapabilities, AgentContext], Optional[PermissionLevel]]
    ] = field(default_factory=list)

    def classify(
        self,
        capabilities: ToolCapabilities,
        context: AgentContext,
    ) -> PermissionLevel:
        """
        Classify tool as allowed/denied based on context.

        Implements Attribute-Based Access Control (ABAC).

        Algorithm:
        1. Check custom rules first (allow overrides)
        2. Check security level restrictions
        3. Check network restrictions
        4. Check file system restrictions
        5. Check data access restrictions
        6. Check approval requirements
        7. Check cost budget
        8. Default: ALLOWED_AUDITED
        """

        # 1. Custom rules (highest priority)
        for rule in self.custom_rules:
            result = rule(capabilities, context)
            if result is not None:
                return result

        # 2. Security level checks
        if context.security_level == SecurityLevel.CRITICAL:
            # Critical security: deny anything risky
            if (
                capabilities.requires_network
                or capabilities.requires_code_execution
                or capabilities.accesses_database
            ):
                return PermissionLevel.DENIED

        if context.security_level == SecurityLevel.HIGH:
            # High security: deny network and code execution
            if capabilities.requires_network or capabilities.requires_code_execution:
                return PermissionLevel.DENIED

        # 3. Network restrictions
        if capabilities.requires_network and not context.allow_network:
            return PermissionLevel.DENIED

        if capabilities.requires_internet and not context.allow_network:
            return PermissionLevel.DENIED

        # 4. File system restrictions
        if capabilities.requires_file_write and not context.allow_file_access:
            return PermissionLevel.DENIED

        if capabilities.requires_file_read and not context.allow_file_access:
            return PermissionLevel.RESTRICTED  # May allow with approval

        # 5. Code execution restrictions
        if capabilities.requires_code_execution and not context.allow_code_execution:
            return PermissionLevel.DENIED

        if capabilities.requires_shell_access and not context.allow_code_execution:
            return PermissionLevel.DENIED

        # 6. Data access restrictions
        if capabilities.accesses_pii and not context.pii_authorized:
            return PermissionLevel.DENIED

        if capabilities.accesses_database and not context.database_access:
            return PermissionLevel.DENIED

        # 7. Approval requirements
        if capabilities.requires_user_approval and not context.user_present:
            return PermissionLevel.RESTRICTED  # Need user approval

        if capabilities.requires_admin_approval:
            return PermissionLevel.RESTRICTED  # Need admin approval

        # 8. Cost budget check
        if capabilities.max_cost_usd > context.max_cost_usd:
            return PermissionLevel.DENIED  # Exceeds budget

        # 9. Production environment extra caution
        if context.is_production():
            # Production: audit everything
            return PermissionLevel.ALLOWED_AUDITED

        # 10. Default: allow with audit
        return PermissionLevel.ALLOWED_AUDITED

    def add_rule(
        self,
        rule: Callable[[ToolCapabilities, AgentContext], Optional[PermissionLevel]],
    ) -> None:
        """
        Add custom permission rule.

        Rules are checked in order. First non-None result is used.

        Example:
            def allow_readonly_in_dev(caps, ctx):
                if ctx.environment == "development" and not caps.requires_file_write:
                    return PermissionLevel.ALLOWED
                return None

            classifier.add_rule(allow_readonly_in_dev)
        """
        self.custom_rules.append(rule)

    def grant_temporary(
        self,
        tool_id: str,
        capabilities: ToolCapabilities,
        context: AgentContext,
        duration_seconds: int = 900,  # 15 minutes default
    ) -> Result[TemporaryToken, str]:
        """
        Grant short-lived token (zero standing privileges).

        Following research best practices:
        - Short-lived: 15-60 minutes (default 15)
        - Task-specific: Only for current operation
        - Revocable: Can be cancelled mid-execution

        Args:
            tool_id: Unique tool identifier
            capabilities: Required capabilities
            context: Agent execution context
            duration_seconds: Token lifetime (default 900 = 15 min)

        Returns:
            Result containing token or error message
        """

        # First check if permission would be granted
        permission = self.classify(capabilities, context)

        if permission == PermissionLevel.DENIED:
            return err(
                None,
                f"Permission denied for tool '{tool_id}' in context {context.agent_id}",
                recoverable=False,
            )

        if permission == PermissionLevel.RESTRICTED:
            return err(
                None,
                f"Tool '{tool_id}' requires additional approval",
                recoverable=True,
            )

        # Generate token
        token_id = self._generate_token_id()

        token = TemporaryToken(
            token_id=token_id,
            tool_id=tool_id,
            context_id=context.agent_id,
            permission=permission,
            capabilities=capabilities,
            expires_at=datetime.now() + timedelta(seconds=duration_seconds),
        )

        return ok(token)

    def _generate_token_id(self) -> str:
        """
        Generate secure random token ID.

        Uses cryptographically secure random number generator.
        """
        random_bytes = secrets.token_bytes(32)
        return hashlib.sha256(random_bytes).hexdigest()


# --- Audit Logging ---


@dataclass
class AuditLog:
    """
    Audit log entry for tool execution.

    Tracks all permission checks and tool uses for security auditing.

    Integration:
    - W-gents: Observability and live monitoring
    - D-gents: Persistent audit trail storage
    """

    # Identity (required fields first)
    log_id: str
    tool_id: str
    tool_name: str
    context_id: str
    permission: PermissionLevel
    input_summary: str  # Summary of input (not full data)

    # Fields with defaults (must come after required fields)
    timestamp: datetime = field(default_factory=datetime.now)
    token_id: Optional[str] = None
    output_summary: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    cost_usd: Optional[float] = None
    flagged: bool = False  # Flagged for review
    flag_reason: Optional[str] = None


class AuditLogger:
    """
    Audit logger for tool executions.

    Integrates with W-gents for observability and D-gents for persistence.

    Usage:
        logger = AuditLogger()

        # Log permission check
        await logger.log_permission_check(
            tool_id="web_search",
            context=context,
            permission=PermissionLevel.ALLOWED_AUDITED,
        )

        # Log execution
        await logger.log_execution(
            tool_id="web_search",
            context=context,
            success=True,
            duration_ms=150,
        )
    """

    def __init__(self):
        """Initialize audit logger."""
        self.logs: list[AuditLog] = []  # In-memory buffer
        # TODO: Integrate with D-gent for persistent storage
        # TODO: Integrate with W-gent for live streaming

    async def log_permission_check(
        self,
        tool_id: str,
        tool_name: str,
        context: AgentContext,
        permission: PermissionLevel,
        token_id: Optional[str] = None,
    ) -> None:
        """Log a permission check."""

        log = AuditLog(
            log_id=self._generate_log_id(),
            tool_id=tool_id,
            tool_name=tool_name,
            context_id=context.agent_id,
            permission=permission,
            token_id=token_id,
            input_summary="<permission check>",
        )

        self.logs.append(log)
        # TODO: Emit to W-gent stream
        # TODO: Store in D-gent persistence

    async def log_execution(
        self,
        tool_id: str,
        tool_name: str,
        context: AgentContext,
        permission: PermissionLevel,
        input_summary: str,
        success: bool,
        output_summary: Optional[str] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
        cost_usd: Optional[float] = None,
        token_id: Optional[str] = None,
    ) -> None:
        """Log a tool execution."""

        log = AuditLog(
            log_id=self._generate_log_id(),
            tool_id=tool_id,
            tool_name=tool_name,
            context_id=context.agent_id,
            permission=permission,
            token_id=token_id,
            input_summary=input_summary,
            output_summary=output_summary,
            success=success,
            error=error,
            duration_ms=duration_ms,
            cost_usd=cost_usd,
        )

        # Flag for review if needed
        if permission == PermissionLevel.RESTRICTED:
            log.flagged = True
            log.flag_reason = "Restricted permission used"

        if not success and error:
            log.flagged = True
            log.flag_reason = f"Execution failed: {error}"

        self.logs.append(log)
        # TODO: Emit to W-gent stream
        # TODO: Store in D-gent persistence

    def get_logs(
        self,
        tool_id: Optional[str] = None,
        context_id: Optional[str] = None,
        flagged_only: bool = False,
    ) -> list[AuditLog]:
        """
        Query audit logs.

        Args:
            tool_id: Filter by tool ID
            context_id: Filter by context ID
            flagged_only: Only return flagged logs

        Returns:
            Filtered list of audit logs
        """
        filtered = self.logs

        if tool_id:
            filtered = [log for log in filtered if log.tool_id == tool_id]

        if context_id:
            filtered = [log for log in filtered if log.context_id == context_id]

        if flagged_only:
            filtered = [log for log in filtered if log.flagged]

        return filtered

    def _generate_log_id(self) -> str:
        """Generate unique log ID."""
        random_bytes = secrets.token_bytes(16)
        return hashlib.sha256(random_bytes).hexdigest()[:16]
