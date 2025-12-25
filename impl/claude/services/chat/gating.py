"""
Pre-Execution Gating — Gate destructive operations before execution.

Philosophy:
"DESTRUCTIVE operations require APPROVAL before execution.
 Timeout = DENY (safe default)."

Differences from MutationAcknowledger:
- Runs BEFORE tool execution (not after)
- Timeout behavior is DENY (not accept)
- Only for DESTRUCTIVE tools (not all mutations)
- Blocks execution until user decides

See: spec/protocols/chat-web.md Part VII.2 (Transparency Levels)
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from .trust_manager import TrustManager, get_trust_manager

logger = logging.getLogger(__name__)


# =============================================================================
# Tool Classification
# =============================================================================


class ToolCategory(Enum):
    """Tool category for gating decisions."""

    READ = "read"  # Pure reads, no gating needed
    MUTATION = "mutation"  # Writes that can be undone, ack required
    DESTRUCTIVE = "destructive"  # Irrecoverable actions, approval required


# Tools that are pure reads (never need gating)
READ_TOOLS = {"Read", "Grep", "Glob", "WebFetch", "WebSearch"}

# Tools that can be destructive (context-dependent)
CONTEXT_DEPENDENT_TOOLS = {"Bash"}


def classify_tool(tool_name: str, tool_input: dict[str, Any]) -> ToolCategory:
    """
    Classify a tool as READ, MUTATION, or DESTRUCTIVE.

    Args:
        tool_name: Name of the tool (e.g., "Edit", "Bash")
        tool_input: Tool invocation parameters

    Returns:
        Tool category for gating logic
    """
    # READ tools never need gating
    if tool_name in READ_TOOLS:
        return ToolCategory.READ

    # Bash is context-dependent on command content
    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))

        # Destructive patterns
        destructive_patterns = [
            r"\brm\s+-rf\b",
            r"\bgit\s+push\s+--force\b",
            r"\bgit\s+reset\s+--hard\b",
            r"\bdocker\s+system\s+prune\b",
            r"\bnpm\s+uninstall\b",
        ]

        import re

        if any(re.search(pattern, command) for pattern in destructive_patterns):
            return ToolCategory.DESTRUCTIVE

        # Mutation patterns (non-destructive)
        mutation_patterns = [
            r"\bgit\s+commit\b",
            r"\bgit\s+push\b",
            r"\bgit\s+add\b",
            r"\bmkdir\b",
            r"\btouch\b",
            r"\bnpm\s+install\b",
        ]

        if any(re.search(pattern, command) for pattern in mutation_patterns):
            return ToolCategory.MUTATION

        # Default for Bash: read (e.g., ls, git status)
        return ToolCategory.READ

    # All other tools are mutations (Edit, Write, NotebookEdit)
    return ToolCategory.MUTATION


# =============================================================================
# Approval Request & Response
# =============================================================================


@dataclass
class ApprovalRequest:
    """
    Request for user approval before executing a tool.

    Sent to frontend as SSE event: pending_approval
    """

    request_id: str  # Unique identifier for this request
    tool_name: str
    tool_input: dict[str, Any]
    input_preview: str  # Human-readable preview (e.g., command text)
    is_destructive: bool
    timeout_seconds: int
    timestamp: str

    def to_dict(self) -> dict:
        """Serialize for SSE payload."""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "input_preview": self.input_preview,
            "is_destructive": self.is_destructive,
            "timeout_seconds": self.timeout_seconds,
            "timestamp": self.timestamp,
        }


@dataclass
class ApprovalResponse:
    """
    User's response to an approval request.

    Posted back from frontend via POST /api/chat/:id/approve-tool
    """

    request_id: str
    approved: bool
    always_allow: bool = False  # User chose "Always Allow This Tool"
    reason: Optional[str] = None  # Optional user comment


class ApprovalTimeout(Exception):
    """Raised when approval request times out."""

    pass


class ApprovalDenied(Exception):
    """Raised when user denies approval."""

    pass


# =============================================================================
# Pre-Execution Gate
# =============================================================================


class PreExecutionGate:
    """
    Pre-execution gating for destructive operations.

    Blocks tool execution until user approves or timeout expires.
    """

    def __init__(
        self,
        trust_manager: Optional[TrustManager] = None,
        timeout_seconds: int = 30,
    ):
        """
        Initialize pre-execution gate.

        Args:
            trust_manager: Trust manager for checking trust levels
            timeout_seconds: Default timeout for approval requests
        """
        self.trust_manager = trust_manager or get_trust_manager()
        self.timeout_seconds = timeout_seconds

        # Pending approval requests (request_id -> Future[ApprovalResponse])
        self._pending_approvals: dict[str, asyncio.Future] = {}

    async def should_gate(
        self,
        user_id: str,
        tool_name: str,
        tool_input: dict[str, Any],
    ) -> bool:
        """
        Check if tool execution should be gated (approval required).

        Args:
            user_id: User identifier
            tool_name: Tool name
            tool_input: Tool invocation parameters

        Returns:
            True if gating required, False if auto-approved
        """
        # Classify tool
        category = classify_tool(tool_name, tool_input)

        # READ tools never need gating
        if category == ToolCategory.READ:
            return False

        # Check trust manager for auto-approval
        needs_approval = self.trust_manager.should_gate(user_id, tool_name)

        return needs_approval

    async def request_approval(
        self,
        user_id: str,
        tool_name: str,
        tool_input: dict[str, Any],
        session_id: str,
        on_request: Optional[Callable[[ApprovalRequest], Any]] = None,
    ) -> ApprovalResponse:
        """
        Request approval from user before executing tool.

        Blocks until user responds or timeout expires.

        Args:
            user_id: User identifier
            tool_name: Tool name
            tool_input: Tool invocation parameters
            session_id: Chat session ID (for context)
            on_request: Optional callback to send request to frontend (SSE)

        Returns:
            Approval response

        Raises:
            ApprovalTimeout: If timeout expires (DEFAULT DENY)
            ApprovalDenied: If user denies approval
        """
        import uuid

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Build input preview
        input_preview = self._build_input_preview(tool_name, tool_input)

        # Classify tool
        category = classify_tool(tool_name, tool_input)
        is_destructive = category == ToolCategory.DESTRUCTIVE

        # Create request
        request = ApprovalRequest(
            request_id=request_id,
            tool_name=tool_name,
            tool_input=tool_input,
            input_preview=input_preview,
            is_destructive=is_destructive,
            timeout_seconds=self.timeout_seconds,
            timestamp=datetime.now().isoformat(),
        )

        # Create future for response
        future: asyncio.Future[ApprovalResponse] = asyncio.Future()
        self._pending_approvals[request_id] = future

        # Send request to frontend (via callback)
        if on_request:
            try:
                await on_request(request)
            except Exception as e:
                logger.error(f"Failed to send approval request: {e}")
                # Clean up future
                del self._pending_approvals[request_id]
                future.cancel()
                raise

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=self.timeout_seconds)

            # Record approval/denial in trust manager
            if response.approved:
                self.trust_manager.record_approval(
                    user_id=user_id,
                    tool_name=tool_name,
                    approved=True,
                    context=f"Pre-execution approval for {tool_name}",
                    session_id=session_id,
                )

                # Handle "Always Allow" option
                if response.always_allow:
                    self.trust_manager.escalate_trust(
                        user_id=user_id,
                        tool_name=tool_name,
                        context="User chose 'Always Allow' during pre-execution gate",
                        session_id=session_id,
                    )
                    logger.info(f"Escalated trust for {tool_name} to TRUSTED")

            else:
                self.trust_manager.record_approval(
                    user_id=user_id,
                    tool_name=tool_name,
                    approved=False,
                    context=f"Pre-execution denial for {tool_name}: {response.reason or 'No reason provided'}",
                    session_id=session_id,
                )
                raise ApprovalDenied(
                    f"User denied approval for {tool_name}: {response.reason or 'No reason provided'}"
                )

            return response

        except asyncio.TimeoutError:
            # Timeout = DENY (safe default for destructive operations)
            logger.warning(
                f"Approval request {request_id} timed out after {self.timeout_seconds}s (DENIED)"
            )

            # Record timeout denial
            self.trust_manager.record_approval(
                user_id=user_id,
                tool_name=tool_name,
                approved=False,
                context=f"Pre-execution timeout (auto-denied) for {tool_name}",
                session_id=session_id,
            )

            raise ApprovalTimeout(
                f"Approval request for {tool_name} timed out after {self.timeout_seconds}s (DENIED)"
            )

        finally:
            # Clean up pending request
            if request_id in self._pending_approvals:
                del self._pending_approvals[request_id]

    def respond_to_approval(
        self,
        request_id: str,
        approved: bool,
        always_allow: bool = False,
        reason: Optional[str] = None,
    ) -> None:
        """
        Respond to a pending approval request.

        Called by API endpoint when user submits approval decision.

        Args:
            request_id: Request identifier
            approved: True if approved, False if denied
            always_allow: True if user chose "Always Allow"
            reason: Optional reason for denial
        """
        if request_id not in self._pending_approvals:
            logger.warning(f"No pending approval request for {request_id}")
            return

        future = self._pending_approvals[request_id]

        response = ApprovalResponse(
            request_id=request_id,
            approved=approved,
            always_allow=always_allow,
            reason=reason,
        )

        future.set_result(response)

    def _build_input_preview(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """
        Build human-readable preview of tool input.

        Args:
            tool_name: Tool name
            tool_input: Tool parameters

        Returns:
            Preview string for UI
        """
        if tool_name == "Bash":
            command = str(tool_input.get("command", ""))
            # Truncate long commands
            if len(command) > 100:
                return command[:100] + "..."
            return command

        elif tool_name in {"Edit", "Write", "NotebookEdit"}:
            file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
            return str(file_path) if file_path else "Unknown file"

        else:
            # Generic preview
            return f"{tool_name} with {len(tool_input)} parameters"


# =============================================================================
# Singleton Instance
# =============================================================================

_gate: Optional[PreExecutionGate] = None


def get_pre_execution_gate() -> PreExecutionGate:
    """Get global pre-execution gate instance."""
    global _gate
    if _gate is None:
        _gate = PreExecutionGate()
    return _gate


__all__ = [
    "ToolCategory",
    "ApprovalRequest",
    "ApprovalResponse",
    "ApprovalTimeout",
    "ApprovalDenied",
    "PreExecutionGate",
    "get_pre_execution_gate",
    "classify_tool",
]
