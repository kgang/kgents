"""
Web Projection Functor.

This module implements the WebProjectionFunctor that transforms meaning tokens
to ReactElement specifications. The functor includes affordance wiring as
data attributes for client-side interaction handling.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 2.2, 2.4
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
# React Element Types
# =============================================================================


@dataclass(frozen=True)
class ReactElement:
    """Specification for a React element.

    This is a serializable representation of a React element that can
    be sent to the web client for rendering.

    Attributes:
        component: React component name (e.g., "AGENTESEPathToken")
        props: Component props
        children: Child elements
    """

    component: str
    props: dict[str, Any] = field(default_factory=dict)
    children: tuple["ReactElement | str", ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "component": self.component,
            "props": self.props,
        }

        if self.children:
            result["children"] = [
                child.to_dict() if isinstance(child, ReactElement) else child
                for child in self.children
            ]

        return result

    def with_props(self, **new_props: Any) -> ReactElement:
        """Create a new element with additional props."""
        return ReactElement(
            component=self.component,
            props={**self.props, **new_props},
            children=self.children,
        )

    def with_children(self, *children: "ReactElement | str") -> ReactElement:
        """Create a new element with children."""
        return ReactElement(
            component=self.component,
            props=self.props,
            children=children,
        )


# =============================================================================
# Token Protocol for Web Projection
# =============================================================================


@runtime_checkable
class WebProjectable(Protocol):
    """Protocol for tokens that can be projected to web."""

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

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for observer."""
        ...


# =============================================================================
# Web Projection Functor
# =============================================================================


class WebProjectionFunctor(ProjectionFunctor[ReactElement]):
    """Project meaning tokens to React element specifications.

    This functor transforms meaning tokens into ReactElement specifications
    that can be serialized and sent to a web client for rendering.
    Affordances are included as data attributes for client-side handling.

    Token Type Mappings:
    - agentese_path: AGENTESEPathToken component
    - task_checkbox: TaskCheckboxToken component
    - image: ImageToken component
    - code_block: CodeBlockToken component
    - principle_ref: PrincipleRefToken component
    - requirement_ref: RequirementRefToken component

    Requirements: 2.2, 2.4
    """

    @property
    def target_name(self) -> str:
        return "web"

    async def project_token(
        self,
        token: WebProjectable,
        observer: Observer,
    ) -> ReactElement:
        """Project token to React element specification.

        Args:
            token: The meaning token to project
            observer: The observer receiving the projection

        Returns:
            ReactElement specification
        """
        params = self.get_density_params(observer)

        # Get affordances for this observer
        affordances = await token.get_affordances(observer)

        # Build base props
        base_props = {
            "token": token.to_dict(),
            "tokenId": token.token_id,
            "tokenType": token.token_type,
            "affordances": [a.to_dict() for a in affordances],
            "observer": observer.to_dict(),
            "density": observer.density.value,
        }

        # Get token-specific element
        element = self._project_by_type(token, params, affordances)

        # Merge base props with token-specific props
        return element.with_props(**base_props)

    async def project_document(
        self,
        document: Any,
        observer: Observer,
    ) -> ReactElement:
        """Project document to React element specification.

        Args:
            document: The document to project
            observer: The observer receiving the projection

        Returns:
            ReactElement specification for the document
        """
        params = self.get_density_params(observer)
        children: list[ReactElement | str] = []

        # Handle document with tokens attribute
        tokens = getattr(document, "tokens", [])
        for token in tokens:
            children.append(await self.project_token(token, observer))

        # Handle document with content attribute
        content = getattr(document, "content", "")
        if content and not tokens:
            children.append(content)

        return ReactElement(
            component="InteractiveDocument",
            props={
                "density": observer.density.value,
                "spacing": params.spacing,
            },
            children=tuple(children),
        )

    def _compose(
        self,
        projections: list[ReactElement],
        composition_type: str,
    ) -> ReactElement:
        """Compose React elements.

        Args:
            projections: List of React elements
            composition_type: "horizontal" or "vertical"

        Returns:
            Composed React element
        """
        if composition_type == "horizontal":
            return ReactElement(
                component="HStack",
                props={"spacing": 4},
                children=tuple(projections),
            )
        else:  # vertical
            return ReactElement(
                component="VStack",
                props={"spacing": 4},
                children=tuple(projections),
            )

    def _project_by_type(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project token based on its type.

        Args:
            token: The token to project
            params: Density parameters
            affordances: Available affordances

        Returns:
            ReactElement specification
        """
        token_type = token.token_type

        match token_type:
            case "agentese_path":
                return self._project_agentese_path(token, params, affordances)
            case "task_checkbox":
                return self._project_task_checkbox(token, params, affordances)
            case "image":
                return self._project_image(token, params, affordances)
            case "code_block":
                return self._project_code_block(token, params, affordances)
            case "principle_ref":
                return self._project_principle_ref(token, params, affordances)
            case "requirement_ref":
                return self._project_requirement_ref(token, params, affordances)
            case _:
                return ReactElement(
                    component="TextToken",
                    props={"text": token.source_text},
                )

    def _project_agentese_path(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project AGENTESE path token to React element."""
        token_dict = token.to_dict()
        path = token_dict.get("path", token.source_text.strip("`"))
        exists = token_dict.get("exists", True)

        return ReactElement(
            component="AGENTESEPathToken",
            props={
                "path": path,
                "exists": exists,
                "isGhost": not exists,
                "showDetails": params.show_details,
                "data-affordance-hover": self._get_affordance_handler(affordances, "hover"),
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
                "data-affordance-right-click": self._get_affordance_handler(
                    affordances, "right-click"
                ),
                "data-affordance-drag": self._get_affordance_handler(affordances, "drag"),
            },
        )

    def _project_task_checkbox(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project task checkbox token to React element."""
        token_dict = token.to_dict()
        checked = token_dict.get("checked", False)
        description = token_dict.get("description", "")

        return ReactElement(
            component="TaskCheckboxToken",
            props={
                "checked": checked,
                "description": description,
                "showDetails": params.show_details,
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
                "data-affordance-hover": self._get_affordance_handler(affordances, "hover"),
            },
        )

    def _project_image(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project image token to React element."""
        token_dict = token.to_dict()
        src = token_dict.get("src", "")
        alt_text = token_dict.get("alt_text", "")

        return ReactElement(
            component="ImageToken",
            props={
                "src": src,
                "altText": alt_text,
                "showDetails": params.show_details,
                "data-affordance-hover": self._get_affordance_handler(affordances, "hover"),
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
                "data-affordance-drag": self._get_affordance_handler(affordances, "drag"),
            },
        )

    def _project_code_block(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project code block token to React element."""
        token_dict = token.to_dict()
        language = token_dict.get("language", "")
        code = token_dict.get("code", token.source_text)

        return ReactElement(
            component="CodeBlockToken",
            props={
                "language": language,
                "code": code,
                "showDetails": params.show_details,
                "fontSize": params.font_size,
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
                "data-affordance-double-click": self._get_affordance_handler(
                    affordances, "double-click"
                ),
            },
        )

    def _project_principle_ref(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project principle reference token to React element."""
        token_dict = token.to_dict()
        principle_number = token_dict.get("principle_number", 0)

        return ReactElement(
            component="PrincipleRefToken",
            props={
                "principleNumber": principle_number,
                "text": token.source_text,
                "showDetails": params.show_details,
                "data-affordance-hover": self._get_affordance_handler(affordances, "hover"),
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
            },
        )

    def _project_requirement_ref(
        self,
        token: WebProjectable,
        params: DensityParams,
        affordances: list[Affordance],
    ) -> ReactElement:
        """Project requirement reference token to React element."""
        token_dict = token.to_dict()
        requirement_id = token_dict.get("requirement_id", "")

        return ReactElement(
            component="RequirementRefToken",
            props={
                "requirementId": requirement_id,
                "text": token.source_text,
                "showDetails": params.show_details,
                "data-affordance-hover": self._get_affordance_handler(affordances, "hover"),
                "data-affordance-click": self._get_affordance_handler(affordances, "click"),
            },
        )

    def _get_affordance_handler(
        self,
        affordances: list[Affordance],
        action: str,
    ) -> str | None:
        """Get the handler for a specific affordance action.

        Args:
            affordances: List of available affordances
            action: The action to find handler for

        Returns:
            Handler string or None if not found
        """
        for affordance in affordances:
            if affordance.action.value == action and affordance.enabled:
                return affordance.handler
        return None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WebProjectionFunctor",
    "ReactElement",
]
