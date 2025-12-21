"""
JSON Projection Functor.

This module implements the JSONProjectionFunctor that transforms meaning tokens
to API-friendly JSON structures. This functor is used for programmatic access
to token data through REST APIs.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 2.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from services.interactive_text.contracts import (
    Affordance,
    Observer,
    ObserverDensity,
)
from services.interactive_text.projectors.base import (
    DENSITY_PARAMS,
    DensityParams,
    ProjectionFunctor,
)

# =============================================================================
# JSON Structure Types
# =============================================================================


@dataclass(frozen=True)
class JSONToken:
    """JSON representation of a meaning token.

    This is a structured representation suitable for API responses.

    Attributes:
        token_type: Type of the token
        token_id: Unique identifier
        source_text: Original source text
        source_position: (start, end) position in source
        data: Token-specific data
        affordances: Available affordances
        metadata: Additional metadata
    """

    token_type: str
    token_id: str
    source_text: str
    source_position: tuple[int, int]
    data: dict[str, Any] = field(default_factory=dict)
    affordances: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tokenType": self.token_type,
            "tokenId": self.token_id,
            "sourceText": self.source_text,
            "sourcePosition": {
                "start": self.source_position[0],
                "end": self.source_position[1],
            },
            "data": self.data,
            "affordances": list(self.affordances),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class JSONDocument:
    """JSON representation of a document.

    Attributes:
        tokens: List of token representations
        content: Original document content
        metadata: Document metadata
    """

    tokens: tuple[JSONToken, ...] = ()
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tokens": [t.to_dict() for t in self.tokens],
            "content": self.content,
            "metadata": self.metadata,
        }


# =============================================================================
# Token Protocol for JSON Projection
# =============================================================================


@runtime_checkable
class JSONProjectable(Protocol):
    """Protocol for tokens that can be projected to JSON."""

    @property
    def token_type(self) -> str:
        """Token type name."""
        ...

    @property
    def source_text(self) -> str:
        """Original source text."""
        ...

    @property
    def source_position(self) -> tuple[int, int]:
        """Source position (start, end)."""
        ...

    @property
    def token_id(self) -> str:
        """Unique token identifier."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        ...

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for observer."""
        ...


# =============================================================================
# JSON Projection Functor
# =============================================================================


class JSONProjectionFunctor(ProjectionFunctor[dict[str, Any]]):
    """Project meaning tokens to API-friendly JSON structures.

    This functor transforms meaning tokens into JSON-serializable
    dictionaries suitable for REST API responses. It includes all
    token data and available affordances.

    Requirements: 2.2
    """

    @property
    def target_name(self) -> str:
        return "json"

    async def project_token(
        self,
        token: JSONProjectable,
        observer: Observer,
    ) -> dict[str, Any]:
        """Project token to JSON dictionary.

        Args:
            token: The meaning token to project
            observer: The observer receiving the projection

        Returns:
            JSON-serializable dictionary
        """
        params = self.get_density_params(observer)

        # Get affordances for this observer
        affordances = await token.get_affordances(observer)

        # Get token-specific data
        token_data = self._extract_token_data(token, params)

        # Build JSON token
        json_token = JSONToken(
            token_type=token.token_type,
            token_id=token.token_id,
            source_text=token.source_text,
            source_position=token.source_position,
            data=token_data,
            affordances=tuple(a.to_dict() for a in affordances),
            metadata={
                "density": observer.density.value,
                "role": observer.role.value,
                "capabilities": list(observer.capabilities),
            },
        )

        return json_token.to_dict()

    async def project_document(
        self,
        document: Any,
        observer: Observer,
    ) -> dict[str, Any]:
        """Project document to JSON dictionary.

        Args:
            document: The document to project
            observer: The observer receiving the projection

        Returns:
            JSON-serializable dictionary
        """
        params = self.get_density_params(observer)
        tokens: list[JSONToken] = []

        # Handle document with tokens attribute
        doc_tokens = getattr(document, "tokens", [])
        for token in doc_tokens:
            token_dict = await self.project_token(token, observer)
            tokens.append(
                JSONToken(
                    token_type=token_dict["tokenType"],
                    token_id=token_dict["tokenId"],
                    source_text=token_dict["sourceText"],
                    source_position=(
                        token_dict["sourcePosition"]["start"],
                        token_dict["sourcePosition"]["end"],
                    ),
                    data=token_dict["data"],
                    affordances=tuple(token_dict["affordances"]),
                    metadata=token_dict["metadata"],
                )
            )

        # Get document content
        content = getattr(document, "content", "")

        json_doc = JSONDocument(
            tokens=tuple(tokens),
            content=content,
            metadata={
                "observer": observer.to_dict(),
                "density": observer.density.value,
            },
        )

        return json_doc.to_dict()

    def _compose(
        self,
        projections: list[dict[str, Any]],
        composition_type: str,
    ) -> dict[str, Any]:
        """Compose JSON projections.

        Args:
            projections: List of JSON dictionaries
            composition_type: "horizontal" or "vertical"

        Returns:
            Composed JSON dictionary
        """
        return {
            "compositionType": composition_type,
            "tokens": projections,
            "count": len(projections),
        }

    def _extract_token_data(
        self,
        token: JSONProjectable,
        params: DensityParams,
    ) -> dict[str, Any]:
        """Extract token-specific data.

        Args:
            token: The token to extract data from
            params: Density parameters

        Returns:
            Token-specific data dictionary
        """
        token_dict = token.to_dict()
        token_type = token.token_type

        # Extract type-specific fields
        match token_type:
            case "agentese_path":
                return {
                    "path": token_dict.get("path", token.source_text.strip("`")),
                    "exists": token_dict.get("exists", True),
                    "isGhost": not token_dict.get("exists", True),
                }
            case "task_checkbox":
                return {
                    "checked": token_dict.get("checked", False),
                    "description": token_dict.get("description", ""),
                }
            case "image":
                return {
                    "src": token_dict.get("src", ""),
                    "altText": token_dict.get("alt_text", ""),
                }
            case "code_block":
                return {
                    "language": token_dict.get("language", ""),
                    "code": token_dict.get("code", token.source_text),
                }
            case "principle_ref":
                return {
                    "principleNumber": token_dict.get("principle_number", 0),
                }
            case "requirement_ref":
                return {
                    "requirementId": token_dict.get("requirement_id", ""),
                    "major": token_dict.get("major", 0),
                    "minor": token_dict.get("minor"),
                }
            case _:
                return token_dict


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "JSONProjectionFunctor",
    "JSONToken",
    "JSONDocument",
]
