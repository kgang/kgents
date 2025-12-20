"""
Token Registry: Single Source of Truth for Token Definitions.

The TokenRegistry implements AD-011 (Registry as Single Source of Truth)
for meaning token definitions. All token types are registered here and
discovered through pattern matching.

Key Responsibilities:
- Register token type definitions
- Recognize tokens in text through pattern matching
- Provide token definitions by name
- Maintain priority ordering for overlapping patterns

See: .kiro/specs/meaning-token-frontend/design.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from .contracts import (
    Affordance,
    AffordanceAction,
    TokenDefinition,
    TokenPattern,
)


@dataclass
class TokenMatch:
    """A token match found in text.

    Attributes:
        definition: The token definition that matched
        match: The regex match object
        start: Start position in source text
        end: End position in source text
    """

    definition: TokenDefinition
    match: re.Match[str]
    start: int
    end: int

    @property
    def text(self) -> str:
        """The matched text."""
        return self.match.group(0)

    @property
    def groups(self) -> tuple[str | None, ...]:
        """Captured groups from the match."""
        return self.match.groups()


class TokenRegistry:
    """Single source of truth for token definitions (AD-011).

    The TokenRegistry maintains all registered token types and provides
    pattern matching to recognize tokens in text. It is designed as a
    class with class-level storage to act as a singleton registry.

    Usage:
        # Register a token type
        TokenRegistry.register(my_token_definition)

        # Get a token definition
        defn = TokenRegistry.get("agentese_path")

        # Recognize tokens in text
        matches = TokenRegistry.recognize("Check `world.town.citizen`")
    """

    _tokens: ClassVar[dict[str, TokenDefinition]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def register(cls, definition: TokenDefinition) -> None:
        """Register a token type.

        Args:
            definition: The token definition to register

        Raises:
            ValueError: If a token with the same name is already registered
        """
        if definition.name in cls._tokens:
            raise ValueError(f"Token '{definition.name}' is already registered")
        cls._tokens[definition.name] = definition

    @classmethod
    def register_or_replace(cls, definition: TokenDefinition) -> None:
        """Register a token type, replacing if it exists.

        Args:
            definition: The token definition to register
        """
        cls._tokens[definition.name] = definition

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a token type.

        Args:
            name: Name of the token to unregister

        Returns:
            True if the token was unregistered, False if not found
        """
        if name in cls._tokens:
            del cls._tokens[name]
            return True
        return False

    @classmethod
    def get(cls, name: str) -> TokenDefinition | None:
        """Get token definition by name.

        Args:
            name: Name of the token type

        Returns:
            The token definition, or None if not found
        """
        cls._ensure_initialized()
        return cls._tokens.get(name)

    @classmethod
    def get_all(cls) -> dict[str, TokenDefinition]:
        """Get all registered token definitions.

        Returns:
            Dictionary of all token definitions by name
        """
        cls._ensure_initialized()
        return dict(cls._tokens)

    @classmethod
    def recognize(cls, text: str) -> list[TokenMatch]:
        """Find all tokens in text, ordered by position then priority.

        Args:
            text: The text to search for tokens

        Returns:
            List of token matches, ordered by position then priority (descending)
        """
        cls._ensure_initialized()
        matches: list[TokenMatch] = []

        for defn in cls._tokens.values():
            for match in defn.pattern.regex.finditer(text):
                matches.append(
                    TokenMatch(
                        definition=defn,
                        match=match,
                        start=match.start(),
                        end=match.end(),
                    )
                )

        # Sort by position first, then by priority (descending)
        return sorted(matches, key=lambda x: (x.start, -x.definition.pattern.priority))

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tokens. Useful for testing."""
        cls._tokens.clear()
        cls._initialized = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure core tokens are registered."""
        if not cls._initialized:
            cls._register_core_tokens()
            cls._initialized = True

    @classmethod
    def _register_core_tokens(cls) -> None:
        """Register the six core token types."""
        # Only register if not already present
        for defn in CORE_TOKEN_DEFINITIONS:
            if defn.name not in cls._tokens:
                cls._tokens[defn.name] = defn


# =============================================================================
# Core Token Definitions
# =============================================================================

CORE_TOKEN_DEFINITIONS: list[TokenDefinition] = [
    # 1. AGENTESE Path Token
    TokenDefinition(
        name="agentese_path",
        pattern=TokenPattern(
            name="agentese_path",
            regex=re.compile(r"`((?:world|self|concept|void|time)\.[a-z_][a-z0-9_.]*)`"),
            priority=10,
        ),
        affordances=(
            Affordance(
                name="hover",
                action=AffordanceAction.HOVER,
                handler="self.document.token.hover",
                description="Display polynomial state (current position, valid transitions)",
            ),
            Affordance(
                name="navigate",
                action=AffordanceAction.CLICK,
                handler="self.document.token.navigate",
                description="Navigate to the path's Habitat",
            ),
            Affordance(
                name="context_menu",
                action=AffordanceAction.RIGHT_CLICK,
                handler="self.document.token.menu",
                description="Show context menu with invoke, view source, copy options",
            ),
            Affordance(
                name="drag_to_repl",
                action=AffordanceAction.DRAG,
                handler="self.document.token.drag",
                description="Pre-fill the path for invocation in REPL",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.agentese_path",
            "web": "services.interactive_text.projectors.web.AGENTESEPathToken",
            "json": "services.interactive_text.projectors.json.agentese_path",
        },
        description="Portal to the agent system via AGENTESE protocol",
    ),
    # 2. Task Checkbox Token
    TokenDefinition(
        name="task_checkbox",
        pattern=TokenPattern(
            name="task_checkbox",
            regex=re.compile(r"- \[([ xX])\] (.+?)(?:\n|$)", re.MULTILINE),
            priority=10,
        ),
        affordances=(
            Affordance(
                name="toggle",
                action=AffordanceAction.CLICK,
                handler="self.document.task.toggle",
                description="Toggle task state and persist to source file",
            ),
            Affordance(
                name="view_trace",
                action=AffordanceAction.HOVER,
                handler="self.document.task.trace",
                description="View verification trace for this task",
            ),
            Affordance(
                name="view_changes",
                action=AffordanceAction.DOUBLE_CLICK,
                handler="self.document.task.diff",
                description="View git diff for task changes",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.task_checkbox",
            "web": "services.interactive_text.projectors.web.TaskCheckboxToken",
            "json": "services.interactive_text.projectors.json.task_checkbox",
        },
        description="Proof of completion with trace witness capture",
    ),
    # 3. Image Token
    TokenDefinition(
        name="image",
        pattern=TokenPattern(
            name="image",
            regex=re.compile(r"!\[([^\]]*)\]\(([^)]+)\)"),
            priority=5,
        ),
        affordances=(
            Affordance(
                name="hover_description",
                action=AffordanceAction.HOVER,
                handler="self.document.image.describe",
                description="Display AI-generated description (cached)",
            ),
            Affordance(
                name="expand",
                action=AffordanceAction.CLICK,
                handler="self.document.image.expand",
                description="Expand to full analysis panel",
            ),
            Affordance(
                name="add_to_context",
                action=AffordanceAction.DRAG,
                handler="self.document.image.context",
                description="Add image to K-gent conversation context",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.image",
            "web": "services.interactive_text.projectors.web.ImageToken",
            "json": "services.interactive_text.projectors.json.image",
        },
        description="Multimodal context with AI analysis",
    ),
    # 4. Code Block Token
    TokenDefinition(
        name="code_block",
        pattern=TokenPattern(
            name="code_block",
            regex=re.compile(r"```(\w*)\n(.*?)```", re.DOTALL),
            priority=5,
        ),
        affordances=(
            Affordance(
                name="edit",
                action=AffordanceAction.CLICK,
                handler="self.document.code.edit",
                description="Enable inline editing with syntax highlighting",
            ),
            Affordance(
                name="run",
                action=AffordanceAction.DOUBLE_CLICK,
                handler="self.document.code.run",
                description="Execute in sandboxed environment",
            ),
            Affordance(
                name="import",
                action=AffordanceAction.DRAG,
                handler="self.document.code.import",
                description="Import content into current module",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.code_block",
            "web": "services.interactive_text.projectors.web.CodeBlockToken",
            "json": "services.interactive_text.projectors.json.code_block",
        },
        description="Executable action with sandboxed execution",
    ),
    # 5. Principle Reference Token
    TokenDefinition(
        name="principle_ref",
        pattern=TokenPattern(
            name="principle_ref",
            regex=re.compile(r"\[P(\d+)\]"),
            priority=8,
        ),
        affordances=(
            Affordance(
                name="view_principle",
                action=AffordanceAction.HOVER,
                handler="self.document.principle.view",
                description="Display principle text and derivation path",
            ),
            Affordance(
                name="navigate_principle",
                action=AffordanceAction.CLICK,
                handler="self.document.principle.navigate",
                description="Navigate to principle definition",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.principle_ref",
            "web": "services.interactive_text.projectors.web.PrincipleRefToken",
            "json": "services.interactive_text.projectors.json.principle_ref",
        },
        description="Anchor to design principles",
    ),
    # 6. Requirement Reference Token
    TokenDefinition(
        name="requirement_ref",
        pattern=TokenPattern(
            name="requirement_ref",
            regex=re.compile(r"\[R(\d+(?:\.\d+)?)\]"),
            priority=8,
        ),
        affordances=(
            Affordance(
                name="view_requirement",
                action=AffordanceAction.HOVER,
                handler="self.document.requirement.view",
                description="Display requirement text and verification status",
            ),
            Affordance(
                name="navigate_requirement",
                action=AffordanceAction.CLICK,
                handler="self.document.requirement.navigate",
                description="Navigate to requirement definition",
            ),
            Affordance(
                name="view_verification",
                action=AffordanceAction.RIGHT_CLICK,
                handler="self.document.requirement.verification",
                description="View verification graph for this requirement",
            ),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.requirement_ref",
            "web": "services.interactive_text.projectors.web.RequirementRefToken",
            "json": "services.interactive_text.projectors.json.requirement_ref",
        },
        description="Trace to requirements with verification status",
    ),
]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TokenRegistry",
    "TokenMatch",
    "CORE_TOKEN_DEFINITIONS",
]
