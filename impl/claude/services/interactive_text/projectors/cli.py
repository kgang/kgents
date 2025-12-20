"""
CLI Projection Functor.

This module implements the CLIProjectionFunctor that transforms meaning tokens
to Rich terminal markup. The functor supports density-parameterized output
for different display preferences.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 2.2, 2.4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from services.interactive_text.contracts import (
    Observer,
    ObserverDensity,
)
from services.interactive_text.projectors.base import (
    DENSITY_PARAMS,
    DensityParams,
    ProjectionFunctor,
)

# =============================================================================
# Rich Markup Types
# =============================================================================


@dataclass(frozen=True)
class RichMarkup:
    """Rich terminal markup representation.
    
    This is a structured representation of Rich markup that can be
    converted to actual Rich markup strings.
    
    Attributes:
        text: The text content
        style: Rich style string (e.g., "cyan", "bold red")
        children: Nested markup elements
    """

    text: str = ""
    style: str | None = None
    children: tuple["RichMarkup", ...] = ()

    def to_markup(self) -> str:
        """Convert to Rich markup string."""
        if self.children:
            inner = "".join(child.to_markup() for child in self.children)
        else:
            inner = self.text

        if self.style:
            return f"[{self.style}]{inner}[/{self.style}]"
        return inner

    def __str__(self) -> str:
        return self.to_markup()


# =============================================================================
# Token Protocol for CLI Projection
# =============================================================================


@runtime_checkable
class CLIProjectable(Protocol):
    """Protocol for tokens that can be projected to CLI."""

    @property
    def token_type(self) -> str:
        """Token type name."""
        ...

    @property
    def source_text(self) -> str:
        """Original source text."""
        ...

    @property
    def token_id(self) -> str:
        """Unique token identifier."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        ...


# =============================================================================
# CLI Projection Functor
# =============================================================================


class CLIProjectionFunctor(ProjectionFunctor[str]):
    """Project meaning tokens to Rich terminal markup.
    
    This functor transforms meaning tokens into Rich markup strings
    suitable for terminal display. It supports density-parameterized
    output for different display preferences.
    
    Token Type Mappings:
    - agentese_path: Cyan text with link-like styling
    - task_checkbox: Checkbox with status indicator
    - image: Dim text with image icon
    - code_block: Code block with syntax highlighting hint
    - principle_ref: Bold reference
    - requirement_ref: Italic reference
    
    Requirements: 2.2, 2.4
    """

    @property
    def target_name(self) -> str:
        return "cli"

    async def project_token(
        self,
        token: CLIProjectable,
        observer: Observer,
    ) -> str:
        """Project token to Rich markup string.
        
        Args:
            token: The meaning token to project
            observer: The observer receiving the projection
            
        Returns:
            Rich markup string representation
        """
        params = self.get_density_params(observer)

        # Get token-specific projection
        markup = self._project_by_type(token, params)

        return markup.to_markup()

    async def project_document(
        self,
        document: Any,
        observer: Observer,
    ) -> str:
        """Project document to Rich markup string.
        
        Args:
            document: The document to project
            observer: The observer receiving the projection
            
        Returns:
            Rich markup string representation of the document
        """
        params = self.get_density_params(observer)
        parts: list[str] = []

        # Handle document with tokens attribute
        tokens = getattr(document, "tokens", [])
        for token in tokens:
            parts.append(await self.project_token(token, observer))

        # Handle document with content attribute
        content = getattr(document, "content", "")
        if content and not tokens:
            parts.append(content)

        separator = "\n" if params.spacing >= 4 else " "
        return separator.join(parts)

    def _compose(
        self,
        projections: list[str],
        composition_type: str,
    ) -> str:
        """Compose Rich markup strings.
        
        Args:
            projections: List of Rich markup strings
            composition_type: "horizontal" or "vertical"
            
        Returns:
            Composed Rich markup string
        """
        if composition_type == "horizontal":
            return " ".join(projections)
        else:  # vertical
            return "\n".join(projections)

    def _project_by_type(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project token based on its type.
        
        Args:
            token: The token to project
            params: Density parameters
            
        Returns:
            RichMarkup representation
        """
        token_type = token.token_type
        source_text = token.source_text

        # Apply truncation if needed
        if params.truncate_length > 0 and len(source_text) > params.truncate_length:
            source_text = source_text[:params.truncate_length - 3] + "..."

        # Token-specific styling
        match token_type:
            case "agentese_path":
                return self._project_agentese_path(token, params)
            case "task_checkbox":
                return self._project_task_checkbox(token, params)
            case "image":
                return self._project_image(token, params)
            case "code_block":
                return self._project_code_block(token, params)
            case "principle_ref":
                return self._project_principle_ref(token, params)
            case "requirement_ref":
                return self._project_requirement_ref(token, params)
            case _:
                return RichMarkup(text=source_text)

    def _project_agentese_path(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project AGENTESE path token.
        
        AGENTESE paths are displayed in cyan to indicate they are
        interactive/navigable.
        """
        text = token.source_text

        # Extract path from backticks if present
        if text.startswith("`") and text.endswith("`"):
            path = text[1:-1]
        else:
            path = text

        if params.show_details:
            return RichMarkup(text=path, style="cyan underline")
        return RichMarkup(text=path, style="cyan")

    def _project_task_checkbox(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project task checkbox token.
        
        Task checkboxes show a checkbox indicator with the task description.
        """
        token_dict = token.to_dict()
        checked = token_dict.get("checked", False)
        description = token_dict.get("description", token.source_text)

        # Apply truncation to description
        if params.truncate_length > 0 and len(description) > params.truncate_length - 4:
            description = description[:params.truncate_length - 7] + "..."

        if checked:
            checkbox = "✓"
            style = "green"
        else:
            checkbox = " "
            style = "dim"

        return RichMarkup(
            children=(
                RichMarkup(text=f"[{checkbox}] ", style=style),
                RichMarkup(text=description),
            )
        )

    def _project_image(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project image token.
        
        Images are displayed with an icon and alt text since terminals
        cannot display actual images.
        """
        token_dict = token.to_dict()
        alt_text = token_dict.get("alt_text", "image")

        if params.truncate_length > 0 and len(alt_text) > params.truncate_length - 3:
            alt_text = alt_text[:params.truncate_length - 6] + "..."

        return RichMarkup(text=f"📷 {alt_text}", style="dim")

    def _project_code_block(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project code block token.
        
        Code blocks are displayed with syntax highlighting hints.
        """
        token_dict = token.to_dict()
        language = token_dict.get("language", "")
        code = token_dict.get("code", token.source_text)

        # Apply truncation
        if params.truncate_length > 0 and len(code) > params.truncate_length:
            code = code[:params.truncate_length - 3] + "..."

        if params.show_details and language:
            header = RichMarkup(text=f"```{language}", style="dim")
            content = RichMarkup(text=f"\n{code}\n", style="")
            footer = RichMarkup(text="```", style="dim")
            return RichMarkup(children=(header, content, footer))

        return RichMarkup(text=code, style="")

    def _project_principle_ref(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project principle reference token.
        
        Principle references are displayed in bold to indicate importance.
        """
        return RichMarkup(text=token.source_text, style="bold yellow")

    def _project_requirement_ref(
        self,
        token: CLIProjectable,
        params: DensityParams,
    ) -> RichMarkup:
        """Project requirement reference token.
        
        Requirement references are displayed in italic to indicate traceability.
        """
        return RichMarkup(text=token.source_text, style="italic magenta")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CLIProjectionFunctor",
    "RichMarkup",
]
