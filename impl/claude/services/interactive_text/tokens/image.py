"""
Image Token Implementation.

The Image token represents markdown images as first-class context that can
be analyzed by AI and used in agent conversations. It provides graceful
degradation when LLM services are unavailable.

Affordances:
- hover: Display AI-generated description (cached)
- click: Expand to full analysis panel
- drag: Add image to K-gent conversation context

Graceful Degradation:
When LLM is unavailable, images display without analysis and show
"requires connection" tooltip.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
)

from .base import BaseMeaningToken, filter_affordances_by_observer


@dataclass(frozen=True)
class ImageAnalysis:
    """AI-generated analysis of an image.
    
    Attributes:
        description: Natural language description
        extracted_text: Text extracted from image (OCR)
        tags: Semantic tags for the image
        cached: Whether this analysis is from cache
    """

    description: str
    extracted_text: str | None = None
    tags: tuple[str, ...] = ()
    cached: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "description": self.description,
            "extracted_text": self.extracted_text,
            "tags": list(self.tags),
            "cached": self.cached,
        }


@dataclass(frozen=True)
class ImageHoverInfo:
    """Information displayed on image hover.
    
    Attributes:
        alt_text: Image alt text
        path: Image path/URL
        analysis: AI analysis (if available)
        requires_connection: Whether LLM is needed but unavailable
    """

    alt_text: str
    path: str
    analysis: ImageAnalysis | None = None
    requires_connection: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "alt_text": self.alt_text,
            "path": self.path,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "requires_connection": self.requires_connection,
        }


@dataclass(frozen=True)
class ImageExpandResult:
    """Result of expanding an image to full analysis panel.
    
    Attributes:
        path: Image path/URL
        alt_text: Image alt text
        analysis: Full AI analysis
        annotations: User annotations on the image
    """

    path: str
    alt_text: str
    analysis: ImageAnalysis | None = None
    annotations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "alt_text": self.alt_text,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "annotations": self.annotations,
        }


@dataclass(frozen=True)
class ImageDragResult:
    """Result of dragging an image to chat context.
    
    Attributes:
        path: Image path/URL
        alt_text: Image alt text
        context_added: Whether image was added to context
    """

    path: str
    alt_text: str
    context_added: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "alt_text": self.alt_text,
            "context_added": self.context_added,
        }


class ImageToken(BaseMeaningToken[str]):
    """Token representing a markdown image.
    
    Image tokens are first-class context that can be analyzed by AI
    and used in agent conversations. They provide graceful degradation
    when LLM services are unavailable.
    
    Pattern: `![alt text](path/to/image.png)`
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    """

    # Pattern for markdown images
    PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    # Capabilities required for certain affordances
    REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
        "hover": frozenset(),  # Always available (degrades gracefully)
        "expand": frozenset(),  # Always available
        "drag_to_context": frozenset(),  # Always available
        "analyze": frozenset(["llm"]),  # Requires LLM
    }

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        alt_text: str,
        path: str,
        llm_available: bool = True,
    ) -> None:
        """Initialize an Image token.
        
        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            alt_text: Image alt text
            path: Image path/URL
            llm_available: Whether LLM service is available
        """
        self._source_text = source_text
        self._source_position = source_position
        self._alt_text = alt_text
        self._path = path
        self._llm_available = llm_available
        self._cached_analysis: ImageAnalysis | None = None

    @classmethod
    def from_match(
        cls,
        match: re.Match[str],
        llm_available: bool = True,
    ) -> ImageToken:
        """Create token from regex match.
        
        Args:
            match: Regex match object from pattern matching
            llm_available: Whether LLM service is available
            
        Returns:
            New ImageToken instance
        """
        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            alt_text=match.group(1),
            path=match.group(2),
            llm_available=llm_available,
        )

    @property
    def token_type(self) -> str:
        """Token type name from registry."""
        return "image"

    @property
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        return self._source_position

    @property
    def alt_text(self) -> str:
        """Image alt text."""
        return self._alt_text

    @property
    def path(self) -> str:
        """Image path/URL."""
        return self._path

    @property
    def llm_available(self) -> bool:
        """Whether LLM service is available."""
        return self._llm_available

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.
        
        Args:
            observer: The observer requesting affordances
            
        Returns:
            List of available affordances
        """
        definition = self.get_definition()

        # Use definition affordances if available, otherwise use defaults
        if definition is not None:
            affordances = list(definition.affordances)
        else:
            # Default affordances for image
            affordances = [
                Affordance(
                    name="hover",
                    action=AffordanceAction.HOVER,
                    handler="world.image.hover",
                    enabled=True,
                    description="View image description",
                ),
                Affordance(
                    name="expand",
                    action=AffordanceAction.CLICK,
                    handler="world.image.expand",
                    enabled=True,
                    description="Expand to full analysis",
                ),
                Affordance(
                    name="drag_to_context",
                    action=AffordanceAction.DRAG,
                    handler="world.image.add_to_context",
                    enabled=True,
                    description="Add to conversation context",
                ),
            ]

        # Filter by observer capabilities
        return filter_affordances_by_observer(
            tuple(affordances),
            observer,
            self.REQUIRED_CAPABILITIES,
        )

    async def project(self, target: str, observer: Observer) -> str:
        """Project token to target-specific rendering.
        
        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection
            
        Returns:
            Target-specific rendering of this token
        """
        if target == "cli":
            if self._alt_text:
                return f"[blue]🖼 {self._alt_text}[/blue]"
            return f"[blue]🖼 {self._path}[/blue]"

        elif target == "json":
            return {
                "type": "image",
                "alt_text": self._alt_text,
                "path": self._path,
                "llm_available": self._llm_available,
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
            
        Requirements: 7.2, 7.3, 7.4
        """
        if action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.CLICK:
            return await self._handle_expand(observer)
        elif action == AffordanceAction.DRAG:
            return await self._handle_drag(observer)
        else:
            return None

    async def _handle_hover(self, observer: Observer) -> ImageHoverInfo:
        """Handle hover action - display AI description.
        
        Requirements: 7.2, 7.5
        """
        # Check if LLM is available for analysis
        has_llm = "llm" in observer.capabilities and self._llm_available

        analysis = None
        requires_connection = False

        if has_llm:
            # Get or generate analysis
            analysis = await self._get_analysis()
        else:
            requires_connection = True

        return ImageHoverInfo(
            alt_text=self._alt_text,
            path=self._path,
            analysis=analysis,
            requires_connection=requires_connection,
        )

    async def _handle_expand(self, observer: Observer) -> ImageExpandResult:
        """Handle click action - expand to full analysis panel.
        
        Requirements: 7.3
        """
        has_llm = "llm" in observer.capabilities and self._llm_available

        analysis = None
        if has_llm:
            analysis = await self._get_analysis()

        return ImageExpandResult(
            path=self._path,
            alt_text=self._alt_text,
            analysis=analysis,
        )

    async def _handle_drag(self, observer: Observer) -> ImageDragResult:
        """Handle drag action - add to conversation context.
        
        Requirements: 7.4
        """
        # In full implementation, would invoke:
        # await logos.invoke("self.context.add_image", observer, path=self._path)

        return ImageDragResult(
            path=self._path,
            alt_text=self._alt_text,
            context_added=True,
        )

    async def _get_analysis(self) -> ImageAnalysis:
        """Get or generate AI analysis for this image.
        
        Returns cached analysis if available, otherwise generates new analysis.
        """
        if self._cached_analysis is not None:
            return ImageAnalysis(
                description=self._cached_analysis.description,
                extracted_text=self._cached_analysis.extracted_text,
                tags=self._cached_analysis.tags,
                cached=True,
            )

        # In full implementation, would invoke:
        # analysis = await logos.invoke("world.vision.analyze", path=self._path)

        # Simulated analysis
        description = f"Image at {self._path}"
        if self._alt_text:
            description = f"{self._alt_text}: {description}"

        return ImageAnalysis(
            description=description,
            tags=("image",),
            cached=False,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update({
            "alt_text": self._alt_text,
            "path": self._path,
            "llm_available": self._llm_available,
        })
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_image_token(
    text: str,
    position: tuple[int, int] | None = None,
    llm_available: bool = True,
) -> ImageToken | None:
    """Create an Image token from text.
    
    Args:
        text: Text that may contain a markdown image
        position: Optional (start, end) position override
        llm_available: Whether LLM service is available
        
    Returns:
        ImageToken if text matches pattern, None otherwise
    """
    match = ImageToken.PATTERN.search(text)
    if match is None:
        return None

    token = ImageToken.from_match(match, llm_available)

    # Override position if provided
    if position is not None:
        return ImageToken(
            source_text=token.source_text,
            source_position=position,
            alt_text=token.alt_text,
            path=token.path,
            llm_available=llm_available,
        )

    return token


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ImageToken",
    "ImageAnalysis",
    "ImageHoverInfo",
    "ImageExpandResult",
    "ImageDragResult",
    "create_image_token",
]
