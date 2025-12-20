"""
PrincipleRef Token Implementation.

The PrincipleRef token represents references to design principles in the
kgents system. It links to the verification graph and provides navigation
to principle definitions.

Affordances:
- hover: Display principle summary and verification status
- click: Navigate to principle definition
- right-click: Context menu with view derivations, copy options

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 12.3, 12.4, 12.5
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
)

from .base import BaseMeaningToken


@dataclass(frozen=True)
class PrincipleInfo:
    """Information about a design principle.
    
    Attributes:
        number: Principle number (e.g., 1, 2, 3)
        title: Principle title
        summary: Brief summary
        verified: Whether principle is verified
        derivation_count: Number of derivations from this principle
    """

    number: int
    title: str = ""
    summary: str = ""
    verified: bool = False
    derivation_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "number": self.number,
            "title": self.title,
            "summary": self.summary,
            "verified": self.verified,
            "derivation_count": self.derivation_count,
        }


@dataclass(frozen=True)
class PrincipleHoverInfo:
    """Information displayed on principle hover.
    
    Attributes:
        ref: The principle reference (e.g., "P1")
        info: Principle information
    """

    ref: str
    info: PrincipleInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "info": self.info.to_dict(),
        }


@dataclass(frozen=True)
class PrincipleNavigationResult:
    """Result of navigating to a principle.
    
    Attributes:
        ref: The principle reference
        path: Path to principle definition
        info: Principle information
    """

    ref: str
    path: str
    info: PrincipleInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "path": self.path,
            "info": self.info.to_dict(),
        }


@dataclass(frozen=True)
class PrincipleContextMenuResult:
    """Result of showing context menu for a principle.
    
    Attributes:
        ref: The principle reference
        options: Available menu options
    """

    ref: str
    options: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "options": self.options,
        }


class PrincipleRefToken(BaseMeaningToken[str]):
    """Token representing a principle reference.
    
    PrincipleRef tokens link to design principles in the verification
    graph and provide navigation to principle definitions.
    
    Pattern: `[P1]`, `[P2]`, etc.
    
    Requirements: 12.3, 12.4, 12.5
    """

    # Pattern for principle references
    PATTERN = re.compile(r"\[P(\d+)\]")

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        number: int,
    ) -> None:
        """Initialize a PrincipleRef token.
        
        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            number: Principle number
        """
        self._source_text = source_text
        self._source_position = source_position
        self._number = number

    @classmethod
    def from_match(cls, match: re.Match[str]) -> PrincipleRefToken:
        """Create token from regex match."""
        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            number=int(match.group(1)),
        )

    @property
    def token_type(self) -> str:
        return "principle_ref"

    @property
    def source_text(self) -> str:
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        return self._source_position

    @property
    def number(self) -> int:
        return self._number

    @property
    def ref(self) -> str:
        return f"P{self._number}"

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer."""
        return [
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="world.principle.hover",
                enabled=True,
                description="View principle summary",
            ),
            Affordance(
                name="navigate",
                action=AffordanceAction.CLICK,
                handler="world.principle.navigate",
                enabled=True,
                description="Go to principle definition",
            ),
            Affordance(
                name="context_menu",
                action=AffordanceAction.RIGHT_CLICK,
                handler="world.principle.context_menu",
                enabled=True,
                description="Show principle options",
            ),
        ]

    async def project(self, target: str, observer: Observer) -> str:
        if target == "cli":
            return f"[magenta]{self._source_text}[/magenta]"
        elif target == "json":
            return {
                "type": "principle_ref",
                "number": self._number,
                "ref": self.ref,
                "source_text": self._source_text,
            }
        return self._source_text

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        if action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.CLICK:
            return await self._handle_navigate(observer)
        elif action == AffordanceAction.RIGHT_CLICK:
            return await self._handle_context_menu(observer)
        return None

    async def _handle_hover(self, observer: Observer) -> PrincipleHoverInfo:
        # Simulated principle info
        info = await self._get_principle_info()
        return PrincipleHoverInfo(ref=self.ref, info=info)

    async def _handle_navigate(self, observer: Observer) -> PrincipleNavigationResult:
        info = await self._get_principle_info()
        return PrincipleNavigationResult(
            ref=self.ref,
            path=f"spec/principles/P{self._number}.md",
            info=info,
        )

    async def _handle_context_menu(self, observer: Observer) -> PrincipleContextMenuResult:
        return PrincipleContextMenuResult(
            ref=self.ref,
            options=[
                {"action": "view_derivations", "label": "View Derivations", "enabled": True},
                {"action": "copy", "label": "Copy Reference", "enabled": True},
                {"action": "view_graph", "label": "View in Graph", "enabled": True},
            ],
        )

    async def _get_principle_info(self) -> PrincipleInfo:
        # Simulated - would query verification graph
        titles = {
            1: "Tasteful",
            2: "Curated",
            3: "Ethical",
            4: "Joy-Inducing",
            5: "Composable",
            6: "Heterarchical",
            7: "Generative",
        }
        return PrincipleInfo(
            number=self._number,
            title=titles.get(self._number, f"Principle {self._number}"),
            summary=f"Design principle {self._number}",
            verified=True,
            derivation_count=5,
        )

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update({"number": self._number, "ref": self.ref})
        return base


def create_principle_ref_token(
    text: str,
    position: tuple[int, int] | None = None,
) -> PrincipleRefToken | None:
    """Create a PrincipleRef token from text."""
    match = PrincipleRefToken.PATTERN.search(text)
    if match is None:
        return None
    token = PrincipleRefToken.from_match(match)
    if position is not None:
        return PrincipleRefToken(
            source_text=token.source_text,
            source_position=position,
            number=token.number,
        )
    return token


__all__ = [
    "PrincipleRefToken",
    "PrincipleInfo",
    "PrincipleHoverInfo",
    "PrincipleNavigationResult",
    "PrincipleContextMenuResult",
    "create_principle_ref_token",
]
