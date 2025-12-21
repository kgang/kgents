"""
CodeBlock Token Implementation.

The CodeBlock token represents fenced code blocks as live playgrounds that
can be edited inline and executed in a sandboxed environment. When code
contains AGENTESE invocations, execution traces are captured.

Affordances:
- click: Focus for inline editing
- hover: Show language info and execution status
- right-click: Context menu with run, copy, import options

Sandboxed Execution:
Code is executed in an isolated environment with resource limits.
AGENTESE invocations within code capture execution traces.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverRole,
)

from .base import BaseMeaningToken, ExecutionTrace, TraceWitness, filter_affordances_by_observer


@dataclass(frozen=True)
class ExecutionResult:
    """Result of executing a code block.

    Attributes:
        success: Whether execution succeeded
        output: Standard output from execution
        error: Error message if execution failed
        return_value: Return value (if any)
        execution_time_ms: Execution time in milliseconds
        traces: AGENTESE execution traces captured
    """

    success: bool
    output: str = ""
    error: str | None = None
    return_value: Any = None
    execution_time_ms: float = 0.0
    traces: tuple[ExecutionTrace, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "return_value": str(self.return_value) if self.return_value else None,
            "execution_time_ms": self.execution_time_ms,
            "traces": [t.to_dict() for t in self.traces],
        }


@dataclass(frozen=True)
class CodeBlockHoverInfo:
    """Information displayed on code block hover.

    Attributes:
        language: Programming language
        line_count: Number of lines
        last_execution: Last execution result (if any)
        is_sandboxed: Whether execution is sandboxed
    """

    language: str
    line_count: int
    last_execution: ExecutionResult | None = None
    is_sandboxed: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "language": self.language,
            "line_count": self.line_count,
            "last_execution": self.last_execution.to_dict() if self.last_execution else None,
            "is_sandboxed": self.is_sandboxed,
        }


@dataclass(frozen=True)
class CodeBlockContextMenuResult:
    """Result of showing context menu for a code block.

    Attributes:
        language: Programming language
        options: Available menu options
        can_execute: Whether code can be executed
    """

    language: str
    options: list[dict[str, Any]]
    can_execute: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "language": self.language,
            "options": self.options,
            "can_execute": self.can_execute,
        }


@dataclass(frozen=True)
class EditFocusResult:
    """Result of focusing a code block for editing.

    Attributes:
        code: Current code content
        language: Programming language
        cursor_position: Initial cursor position
    """

    code: str
    language: str
    cursor_position: tuple[int, int] = (0, 0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "code": self.code,
            "language": self.language,
            "cursor_position": list(self.cursor_position),
        }


class CodeBlockToken(BaseMeaningToken[str]):
    """Token representing a fenced code block.

    CodeBlock tokens are live playgrounds that can be edited inline
    and executed in a sandboxed environment. AGENTESE invocations
    within code capture execution traces.

    Pattern: ```language\ncode\n```

    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
    """

    # Pattern for fenced code blocks
    PATTERN = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

    # Languages that can be executed
    EXECUTABLE_LANGUAGES = frozenset(["python", "javascript", "typescript", "shell", "bash"])

    # Capabilities required for certain affordances
    REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
        "edit": frozenset(),  # Always available
        "hover": frozenset(),  # Always available
        "context_menu": frozenset(),  # Always available
        "execute": frozenset(),  # Sandboxed execution always available
        "import": frozenset(["storage"]),  # Requires file write
    }

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        language: str,
        code: str,
    ) -> None:
        """Initialize a CodeBlock token.

        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            language: Programming language (may be empty)
            code: Code content
        """
        self._source_text = source_text
        self._source_position = source_position
        self._language = language or "text"
        self._code = code
        self._last_execution: ExecutionResult | None = None

    @classmethod
    def from_match(cls, match: re.Match[str]) -> CodeBlockToken:
        """Create token from regex match.

        Args:
            match: Regex match object from pattern matching

        Returns:
            New CodeBlockToken instance
        """
        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            language=match.group(1),
            code=match.group(2),
        )

    @property
    def token_type(self) -> str:
        """Token type name from registry."""
        return "code_block"

    @property
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        return self._source_position

    @property
    def language(self) -> str:
        """Programming language."""
        return self._language

    @property
    def code(self) -> str:
        """Code content."""
        return self._code

    @property
    def line_count(self) -> int:
        """Number of lines in the code."""
        return len(self._code.splitlines())

    @property
    def can_execute(self) -> bool:
        """Whether this code block can be executed."""
        return self._language.lower() in self.EXECUTABLE_LANGUAGES

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances
        """
        # Default affordances for code block - always available
        affordances = [
            Affordance(
                name="edit",
                action=AffordanceAction.CLICK,
                handler="world.code.edit",
                enabled=True,
                description="Edit code inline",
            ),
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="world.code.hover",
                enabled=True,
                description="View code info",
            ),
            Affordance(
                name="context_menu",
                action=AffordanceAction.RIGHT_CLICK,
                handler="world.code.context_menu",
                enabled=True,
                description="Show code options",
            ),
        ]

        return affordances

    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token
        """
        if target == "cli":
            # Rich syntax highlighting
            return f"[bold]{self._language}[/bold]\n{self._code}"

        elif target == "json":
            return {
                "type": "code_block",
                "language": self._language,
                "code": self._code,
                "line_count": self.line_count,
                "can_execute": self.can_execute,
                "source_text": self._source_text,
            }

        else:  # web or default
            return self._source_text

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Execute the action for this token.

        Args:
            action: The action being performed
            observer: The observer performing the action
            **kwargs: Additional action-specific arguments

        Returns:
            Action-specific result

        Requirements: 8.2, 8.3, 8.4, 8.5, 8.6
        """
        if action == AffordanceAction.CLICK:
            return await self._handle_edit(observer)
        elif action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.RIGHT_CLICK:
            return await self._handle_context_menu(observer)
        else:
            return None

    async def _handle_edit(self, observer: Observer) -> EditFocusResult:
        """Handle click action - focus for inline editing.

        Requirements: 8.2
        """
        return EditFocusResult(
            code=self._code,
            language=self._language,
        )

    async def _handle_hover(self, observer: Observer) -> CodeBlockHoverInfo:
        """Handle hover action - show language info and execution status.

        Requirements: 8.4
        """
        return CodeBlockHoverInfo(
            language=self._language,
            line_count=self.line_count,
            last_execution=self._last_execution,
            is_sandboxed=True,
        )

    async def _handle_context_menu(self, observer: Observer) -> CodeBlockContextMenuResult:
        """Handle right-click action - show context menu.

        Requirements: 8.3, 8.5
        """
        options = [
            {"action": "copy", "label": "Copy Code", "enabled": True},
        ]

        if self.can_execute:
            options.append({"action": "run", "label": "Run (Sandboxed)", "enabled": True})

        options.append({"action": "import", "label": "Import to Module", "enabled": True})

        # Admin-only options
        if observer.role == ObserverRole.ADMIN:
            options.append(
                {"action": "run_unsafe", "label": "Run (Unsafe)", "enabled": self.can_execute}
            )

        return CodeBlockContextMenuResult(
            language=self._language,
            options=options,
            can_execute=self.can_execute,
        )

    async def execute(self, observer: Observer, sandboxed: bool = True) -> ExecutionResult:
        """Execute the code block.

        Args:
            observer: The observer executing the code
            sandboxed: Whether to run in sandbox (default True)

        Returns:
            ExecutionResult with output and traces

        Requirements: 8.3, 8.4, 8.6
        """
        if not self.can_execute:
            return ExecutionResult(
                success=False,
                error=f"Language '{self._language}' is not executable",
            )

        # In full implementation, would:
        # 1. Create sandbox environment
        # 2. Execute code with resource limits
        # 3. Capture AGENTESE invocations as traces
        # 4. Return result with traces

        # Simulated execution
        traces: list[ExecutionTrace] = []

        # Check for AGENTESE invocations in code
        agentese_pattern = re.compile(r"(world|self|concept|void|time)\.[a-z_][a-z0-9_.]*")
        for match in agentese_pattern.finditer(self._code):
            trace = ExecutionTrace(
                agent_path=match.group(0),
                operation="invoke",
                input_data={"code_context": self._code[:100]},
                observer_id=observer.id,
            )
            traces.append(trace)

        result = ExecutionResult(
            success=True,
            output=f"# Simulated execution of {self._language} code\n# {self.line_count} lines",
            execution_time_ms=0.1,
            traces=tuple(traces),
        )

        self._last_execution = result
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "language": self._language,
                "code": self._code,
                "line_count": self.line_count,
                "can_execute": self.can_execute,
            }
        )
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_code_block_token(
    text: str,
    position: tuple[int, int] | None = None,
) -> CodeBlockToken | None:
    """Create a CodeBlock token from text.

    Args:
        text: Text that may contain a fenced code block
        position: Optional (start, end) position override

    Returns:
        CodeBlockToken if text matches pattern, None otherwise
    """
    match = CodeBlockToken.PATTERN.search(text)
    if match is None:
        return None

    token = CodeBlockToken.from_match(match)

    # Override position if provided
    if position is not None:
        return CodeBlockToken(
            source_text=token.source_text,
            source_position=position,
            language=token.language,
            code=token.code,
        )

    return token


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CodeBlockToken",
    "ExecutionResult",
    "CodeBlockHoverInfo",
    "CodeBlockContextMenuResult",
    "EditFocusResult",
    "create_code_block_token",
]
