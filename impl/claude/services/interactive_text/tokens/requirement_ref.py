"""
RequirementRef Token Implementation.

The RequirementRef token represents references to requirements in the
kgents system. It links to the verification graph and provides navigation
to requirement definitions with verification status.

Affordances:
- hover: Display requirement summary and verification status
- click: Navigate to requirement definition
- right-click: Context menu with view derivations, view tests options

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
class RequirementInfo:
    """Information about a requirement.
    
    Attributes:
        major: Major version number (e.g., 1 in R1.2)
        minor: Minor version number (e.g., 2 in R1.2), None if not specified
        title: Requirement title
        summary: Brief summary
        verified: Whether requirement is verified
        test_count: Number of tests for this requirement
        derivation_path: Path through verification graph
    """

    major: int
    minor: int | None = None
    title: str = ""
    summary: str = ""
    verified: bool = False
    test_count: int = 0
    derivation_path: str | None = None

    @property
    def ref(self) -> str:
        if self.minor is not None:
            return f"R{self.major}.{self.minor}"
        return f"R{self.major}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "major": self.major,
            "minor": self.minor,
            "ref": self.ref,
            "title": self.title,
            "summary": self.summary,
            "verified": self.verified,
            "test_count": self.test_count,
            "derivation_path": self.derivation_path,
        }


@dataclass(frozen=True)
class RequirementHoverInfo:
    """Information displayed on requirement hover.
    
    Attributes:
        ref: The requirement reference (e.g., "R1.2")
        info: Requirement information
    """

    ref: str
    info: RequirementInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "info": self.info.to_dict(),
        }


@dataclass(frozen=True)
class RequirementNavigationResult:
    """Result of navigating to a requirement.
    
    Attributes:
        ref: The requirement reference
        path: Path to requirement definition
        info: Requirement information
    """

    ref: str
    path: str
    info: RequirementInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "path": self.path,
            "info": self.info.to_dict(),
        }


@dataclass(frozen=True)
class RequirementContextMenuResult:
    """Result of showing context menu for a requirement.
    
    Attributes:
        ref: The requirement reference
        options: Available menu options
        verification_status: Current verification status
    """

    ref: str
    options: list[dict[str, Any]]
    verification_status: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ref": self.ref,
            "options": self.options,
            "verification_status": self.verification_status,
        }


class RequirementRefToken(BaseMeaningToken[str]):
    """Token representing a requirement reference.
    
    RequirementRef tokens link to requirements in the verification
    graph and provide navigation to requirement definitions with
    verification status.
    
    Pattern: `[R1]`, `[R1.2]`, etc.
    
    Requirements: 12.3, 12.4, 12.5
    """

    # Pattern for requirement references
    PATTERN = re.compile(r"\[R(\d+)(?:\.(\d+))?\]")

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        major: int,
        minor: int | None = None,
    ) -> None:
        """Initialize a RequirementRef token.
        
        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            major: Major version number
            minor: Minor version number (optional)
        """
        self._source_text = source_text
        self._source_position = source_position
        self._major = major
        self._minor = minor

    @classmethod
    def from_match(cls, match: re.Match[str]) -> RequirementRefToken:
        """Create token from regex match."""
        minor = int(match.group(2)) if match.group(2) else None
        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            major=int(match.group(1)),
            minor=minor,
        )

    @property
    def token_type(self) -> str:
        return "requirement_ref"

    @property
    def source_text(self) -> str:
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        return self._source_position

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> int | None:
        return self._minor

    @property
    def ref(self) -> str:
        if self._minor is not None:
            return f"R{self._major}.{self._minor}"
        return f"R{self._major}"

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer."""
        return [
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="world.requirement.hover",
                enabled=True,
                description="View requirement summary",
            ),
            Affordance(
                name="navigate",
                action=AffordanceAction.CLICK,
                handler="world.requirement.navigate",
                enabled=True,
                description="Go to requirement definition",
            ),
            Affordance(
                name="context_menu",
                action=AffordanceAction.RIGHT_CLICK,
                handler="world.requirement.context_menu",
                enabled=True,
                description="Show requirement options",
            ),
        ]

    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        if target == "cli":
            return f"[yellow]{self._source_text}[/yellow]"
        elif target == "json":
            return {
                "type": "requirement_ref",
                "major": self._major,
                "minor": self._minor,
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

    async def _handle_hover(self, observer: Observer) -> RequirementHoverInfo:
        info = await self._get_requirement_info()
        return RequirementHoverInfo(ref=self.ref, info=info)

    async def _handle_navigate(self, observer: Observer) -> RequirementNavigationResult:
        info = await self._get_requirement_info()
        return RequirementNavigationResult(
            ref=self.ref,
            path=f"spec/requirements/{self.ref}.md",
            info=info,
        )

    async def _handle_context_menu(self, observer: Observer) -> RequirementContextMenuResult:
        info = await self._get_requirement_info()
        return RequirementContextMenuResult(
            ref=self.ref,
            options=[
                {"action": "view_tests", "label": "View Tests", "enabled": True},
                {"action": "view_derivations", "label": "View Derivations", "enabled": True},
                {"action": "copy", "label": "Copy Reference", "enabled": True},
                {"action": "view_graph", "label": "View in Graph", "enabled": True},
            ],
            verification_status="verified" if info.verified else "pending",
        )

    async def _get_requirement_info(self) -> RequirementInfo:
        # Simulated - would query verification graph
        return RequirementInfo(
            major=self._major,
            minor=self._minor,
            title=f"Requirement {self.ref}",
            summary=f"Requirement {self.ref} specification",
            verified=True,
            test_count=3,
            derivation_path=f"P1 -> {self.ref}",
        )

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update({
            "major": self._major,
            "minor": self._minor,
            "ref": self.ref,
        })
        return base


def create_requirement_ref_token(
    text: str,
    position: tuple[int, int] | None = None,
) -> RequirementRefToken | None:
    """Create a RequirementRef token from text."""
    match = RequirementRefToken.PATTERN.search(text)
    if match is None:
        return None
    token = RequirementRefToken.from_match(match)
    if position is not None:
        return RequirementRefToken(
            source_text=token.source_text,
            source_position=position,
            major=token.major,
            minor=token.minor,
        )
    return token


__all__ = [
    "RequirementRefToken",
    "RequirementInfo",
    "RequirementHoverInfo",
    "RequirementNavigationResult",
    "RequirementContextMenuResult",
    "create_requirement_ref_token",
]
