"""
SpecToken: Base protocol and implementation for spec tokens.

Tokens are the atomic unit of interactive interface in the Living Spec system.
They provide:
1. Semantic recognition in markdown source
2. Observer-dependent affordances
3. Multi-surface rendering (CLI, Web, JSON)
4. Serialization for wire transfer

All tokens implement the SpecToken protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from ..contracts import Affordance, AffordanceAction, Observer

# -----------------------------------------------------------------------------
# Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class SpecToken(Protocol):
    """
    Protocol for all spec tokens.

    Tokens are semantic primitives that:
    1. Have a type and span in source
    2. Provide observer-dependent affordances
    3. Can render to multiple surfaces
    4. Serialize for wire transfer
    """

    @property
    def token_type(self) -> str:
        """Token type identifier (e.g., 'agentese_path', 'portal')."""
        ...

    @property
    def span(self) -> tuple[int, int]:
        """Character span (start, end) in source text."""
        ...

    @property
    def value(self) -> str:
        """The token's value/content."""
        ...

    def affordance(self, observer: Observer) -> Affordance | None:
        """Get primary affordance for this observer, if any."""
        ...

    def render(self, surface: str) -> str | dict[str, Any]:
        """
        Render token for a specific surface.

        Args:
            surface: Target surface ("cli", "web", "json", "markdown")

        Returns:
            Rendered content (string for cli/markdown, dict for web/json)
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        ...


# -----------------------------------------------------------------------------
# Base Implementation
# -----------------------------------------------------------------------------


@dataclass
class BaseSpecToken(ABC):
    """
    Abstract base class for spec tokens.

    Provides common functionality:
    - Span tracking
    - Value storage
    - Default serialization
    - Multi-surface render dispatch
    """

    _span: tuple[int, int]
    _value: str
    _metadata: dict[str, Any] = field(default_factory=dict)

    @property
    @abstractmethod
    def token_type(self) -> str:
        """Token type identifier."""
        ...

    @property
    def span(self) -> tuple[int, int]:
        """Character span in source."""
        return self._span

    @property
    def value(self) -> str:
        """Token value/content."""
        return self._value

    def affordance(self, observer: Observer) -> Affordance | None:
        """
        Get primary affordance for observer.

        Override in subclasses for specific behaviors.
        Default returns None (no interactive affordance).
        """
        return None

    def render(self, surface: str) -> str | dict[str, Any]:
        """
        Render token to target surface.

        Dispatches to surface-specific methods.
        """
        match surface:
            case "cli":
                return self._render_cli()
            case "web":
                return self._render_web()
            case "json":
                return self.to_dict()
            case "markdown":
                return self._render_markdown()
            case _:
                return self._render_cli()

    def _render_cli(self) -> str:
        """Render for CLI (Rich terminal)."""
        return self._value

    def _render_web(self) -> dict[str, Any]:
        """Render for web (React component props)."""
        return self.to_dict()

    def _render_markdown(self) -> str:
        """Render as markdown (roundtrip fidelity)."""
        return self._value

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        return {
            "token_type": self.token_type,
            "span": list(self._span),
            "value": self._value,
            "metadata": self._metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseSpecToken":
        """Deserialize from wire transfer."""
        raise NotImplementedError("Subclasses must implement from_dict")


# -----------------------------------------------------------------------------
# AGENTESE Path Token
# -----------------------------------------------------------------------------


@dataclass
class AGENTESEPathToken(BaseSpecToken):
    """
    Token for AGENTESE paths (e.g., `world.town.citizen`).

    Affordances:
    - Click: Navigate to path's habitat
    - Hover: Show polynomial state
    - Drag: Pre-fill REPL
    """

    @property
    def token_type(self) -> str:
        return "agentese_path"

    @property
    def path(self) -> str:
        """Extract AGENTESE path from value."""
        # Value is like "`world.town.citizen`" — strip backticks
        return self._value.strip("`")

    @property
    def context(self) -> str:
        """Extract context (world, self, concept, void, time)."""
        parts = self.path.split(".")
        return parts[0] if parts else ""

    def affordance(self, observer: Observer) -> Affordance | None:
        """Navigate to path's habitat on click."""
        if "navigate" not in observer.capabilities:
            return None

        return Affordance(
            action=AffordanceAction.NAVIGATE,
            label=f"Go to {self.path}",
            target=self.path,
            tooltip=f"Navigate to {self.path}",
        )

    def _render_cli(self) -> str:
        """Render with styling for CLI."""
        return f"[cyan]{self._value}[/cyan]"

    def _render_web(self) -> dict[str, Any]:
        """Render as React component props."""
        return {
            **self.to_dict(),
            "path": self.path,
            "context": self.context,
            "navigable": True,
        }


# -----------------------------------------------------------------------------
# Task Checkbox Token
# -----------------------------------------------------------------------------


@dataclass
class TaskCheckboxToken(BaseSpecToken):
    """
    Token for task checkboxes (e.g., `- [ ] Task` or `- [x] Done`).

    Affordances:
    - Click: Toggle checkbox state
    - Hover: Show verification status
    """

    @property
    def token_type(self) -> str:
        return "task_checkbox"

    @property
    def is_checked(self) -> bool:
        """Whether the checkbox is checked."""
        return "[x]" in self._value.lower()

    @property
    def task_text(self) -> str:
        """Extract task description text."""
        # Value is like "- [ ] Task description"
        # Remove "- [ ] " or "- [x] " prefix
        text = self._value
        for prefix in ["- [ ] ", "- [x] ", "- [X] "]:
            if text.startswith(prefix):
                return text[len(prefix) :]
        return text

    def affordance(self, observer: Observer) -> Affordance | None:
        """Toggle checkbox on click."""
        if "write" not in observer.capabilities:
            return None

        action = "Uncheck" if self.is_checked else "Check"
        return Affordance(
            action=AffordanceAction.TOGGLE,
            label=f"{action} task",
            target=None,
            tooltip=f"{action} this task (toggles in file)",
        )

    def _render_cli(self) -> str:
        """Render with checkbox for CLI."""
        check = "[green]✓[/green]" if self.is_checked else "[ ]"
        return f"{check} {self.task_text}"

    def _render_markdown(self) -> str:
        """Roundtrip-faithful markdown."""
        check = "x" if self.is_checked else " "
        return f"- [{check}] {self.task_text}"


# -----------------------------------------------------------------------------
# Code Block Token
# -----------------------------------------------------------------------------


@dataclass
class CodeBlockToken(BaseSpecToken):
    """
    Token for fenced code blocks.

    Affordances:
    - Edit: Inline modification
    - Run: Execute sandboxed (for supported languages)
    """

    @property
    def token_type(self) -> str:
        return "code_block"

    @property
    def language(self) -> str:
        """Extract language identifier."""
        return str(self._metadata.get("language", ""))

    @property
    def code(self) -> str:
        """Extract code content (without fences)."""
        lines = self._value.split("\n")
        if len(lines) >= 2:
            # Remove first (```lang) and last (```) lines
            return "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        return self._value

    def affordance(self, observer: Observer) -> Affordance | None:
        """Edit on click if writable."""
        if "write" not in observer.capabilities:
            return None

        return Affordance(
            action=AffordanceAction.EDIT,
            label="Edit code",
            target=None,
            tooltip="Edit this code block inline",
        )

    def _render_cli(self) -> str:
        """Render with syntax highlighting hint."""
        return f"[dim]```{self.language}[/dim]\n{self.code}\n[dim]```[/dim]"


# -----------------------------------------------------------------------------
# Image Token
# -----------------------------------------------------------------------------


@dataclass
class ImageToken(BaseSpecToken):
    """
    Token for image references (e.g., `![alt](path.png)`).

    Affordances:
    - Hover: AI-generated description
    - Click: Expand to full analysis
    - Drag: Add to K-gent context
    """

    @property
    def token_type(self) -> str:
        return "image"

    @property
    def alt_text(self) -> str:
        """Extract alt text."""
        return str(self._metadata.get("alt", ""))

    @property
    def src(self) -> str:
        """Extract image source path."""
        return str(self._metadata.get("src", ""))

    def affordance(self, observer: Observer) -> Affordance | None:
        """Expand on click."""
        return Affordance(
            action=AffordanceAction.EXPAND,
            label="View image",
            target=self.src,
            tooltip=self.alt_text or "View full image",
        )


# -----------------------------------------------------------------------------
# Principle Reference Token
# -----------------------------------------------------------------------------


@dataclass
class PrincipleRefToken(BaseSpecToken):
    """
    Token for principle references (e.g., `(AD-009)` or `(Tasteful)`).

    Affordances:
    - Hover: Show principle summary
    - Click: Navigate to principle
    """

    @property
    def token_type(self) -> str:
        return "principle_ref"

    @property
    def principle_id(self) -> str:
        """Extract principle identifier."""
        # Value is like "(AD-009)" or "(Tasteful)"
        return self._value.strip("()")

    def affordance(self, observer: Observer) -> Affordance | None:
        """Navigate to principle."""
        return Affordance(
            action=AffordanceAction.NAVIGATE,
            label=f"View {self.principle_id}",
            target=f"concept.principle.{self.principle_id}",
            tooltip=f"View principle: {self.principle_id}",
        )

    def _render_cli(self) -> str:
        """Render with styling."""
        return f"[yellow]{self._value}[/yellow]"


# -----------------------------------------------------------------------------
# Requirement Reference Token
# -----------------------------------------------------------------------------


@dataclass
class RequirementRefToken(BaseSpecToken):
    """
    Token for requirement references (e.g., `_Requirements: 7.1, 7.4_`).

    Affordances:
    - Hover: Show requirement text
    - Click: Open verification trace
    """

    @property
    def token_type(self) -> str:
        return "requirement_ref"

    @property
    def requirement_ids(self) -> list[str]:
        """Extract list of requirement IDs."""
        # Value is like "_Requirements: 7.1, 7.4_"
        text = self._value.strip("_")
        if text.startswith("Requirements:"):
            text = text[len("Requirements:") :].strip()
            return [r.strip() for r in text.split(",")]
        return []

    def affordance(self, observer: Observer) -> Affordance | None:
        """Navigate to verification trace."""
        if not self.requirement_ids:
            return None

        return Affordance(
            action=AffordanceAction.NAVIGATE,
            label="View requirements",
            target=f"concept.requirement.{self.requirement_ids[0]}",
            tooltip=f"Requirements: {', '.join(self.requirement_ids)}",
        )

    def _render_cli(self) -> str:
        """Render with styling."""
        return f"[magenta]{self._value}[/magenta]"
