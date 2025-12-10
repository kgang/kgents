"""
Sympathetic Errors - Error messages that help, not just fail.

Philosophy:
    "An error message is a conversation, not a wall."

    Good error messages:
    1. Acknowledge what went wrong (honest)
    2. Explain why it matters (context)
    3. Suggest what to do next (helpful)
    4. Maintain warmth (joy-inducing)

This module embodies the Ethical + Joy-Inducing principles:
- Transparency about limitations (Ethical)
- Personality in error handling (Joy-Inducing)

From docs/cli-integration-plan.md Part 5 (Sympathetic Errors).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# =============================================================================
# Error Categories
# =============================================================================


class ErrorCategory(Enum):
    """Categories of errors with different personas."""

    # User errors (gentle, helpful)
    INPUT = "input"  # Bad input format, missing args
    SYNTAX = "syntax"  # Malformed commands, YAML, etc.
    NOT_FOUND = "not_found"  # Missing files, agents, etc.

    # System errors (apologetic, actionable)
    INTERNAL = "internal"  # Bugs, unexpected states
    TIMEOUT = "timeout"  # Operations took too long
    RESOURCE = "resource"  # Out of memory, disk, etc.

    # External errors (informative, patient)
    NETWORK = "network"  # API failures, connectivity
    DEPENDENCY = "dependency"  # Missing packages, versions
    PERMISSION = "permission"  # Access denied

    # Philosophical errors (contemplative)
    UNDECIDABLE = "undecidable"  # Cannot determine correct action
    PARADOX = "paradox"  # Contradictory requirements


# =============================================================================
# Sympathetic Error
# =============================================================================


@dataclass
class SympatheticError:
    """
    An error that helps, not just fails.

    Attributes:
        category: The type of error
        what: What went wrong (past tense, honest)
        why: Why it matters (context)
        how: How to fix it (actionable steps)
        see_also: Related commands or docs
        technical: Technical details (for --verbose)
        personality: Optional personality/warmth

    Example:
        SympatheticError(
            category=ErrorCategory.NOT_FOUND,
            what="I couldn't find the agent 'archimedes'",
            why="The catalog search returned no matches",
            how=[
                "Check the spelling: kgents find 'archimedes'",
                "List all agents: kgents library list --type=agent",
                "Create it: kgents new agent 'Archimedes'",
            ],
            see_also=["kgents find --help", "kgents library --help"],
            personality="Agents are like friends—sometimes we forget their exact names.",
        )
    """

    category: ErrorCategory
    what: str
    why: str = ""
    how: list[str] | None = None
    see_also: list[str] | None = None
    technical: str | None = None
    personality: str | None = None

    def render(self, verbose: bool = False, use_color: bool = True) -> str:
        """Render the error as a helpful message."""
        lines = []

        # Header with category indicator
        category_icons = {
            ErrorCategory.INPUT: "?",
            ErrorCategory.SYNTAX: "~",
            ErrorCategory.NOT_FOUND: "x",
            ErrorCategory.INTERNAL: "!",
            ErrorCategory.TIMEOUT: "...",
            ErrorCategory.RESOURCE: "^",
            ErrorCategory.NETWORK: "@",
            ErrorCategory.DEPENDENCY: "*",
            ErrorCategory.PERMISSION: "#",
            ErrorCategory.UNDECIDABLE: "?!",
            ErrorCategory.PARADOX: "<!>",
        }
        icon = category_icons.get(self.category, "!")

        # The "what" - always shown
        lines.append(f"[{icon}] {self.what}")

        # The "why" - context
        if self.why:
            lines.append("")
            lines.append(f"    {self.why}")

        # The "how" - actionable steps
        if self.how:
            lines.append("")
            lines.append("    Try:")
            for step in self.how:
                lines.append(f"      {step}")

        # See also
        if self.see_also:
            lines.append("")
            lines.append("    See also:")
            for ref in self.see_also:
                lines.append(f"      {ref}")

        # Personality (warmth)
        if self.personality:
            lines.append("")
            lines.append(f"    ({self.personality})")

        # Technical details (verbose only)
        if verbose and self.technical:
            lines.append("")
            lines.append("    Technical:")
            for tech_line in self.technical.split("\n"):
                lines.append(f"      {tech_line}")

        return "\n".join(lines)


# =============================================================================
# Error Factory Functions
# =============================================================================


def file_not_found(path: str, suggestions: list[str] | None = None) -> SympatheticError:
    """Create a sympathetic 'file not found' error."""
    how = suggestions or [
        f"Check the path exists: ls {path}",
        "Use tab-completion for paths",
    ]
    return SympatheticError(
        category=ErrorCategory.NOT_FOUND,
        what=f"I couldn't find '{path}'",
        why="The file or directory doesn't exist at that path.",
        how=how,
        personality="Paths are tricky—even experienced developers double-check them.",
    )


def agent_not_found(name: str) -> SympatheticError:
    """Create a sympathetic 'agent not found' error."""
    return SympatheticError(
        category=ErrorCategory.NOT_FOUND,
        what=f"I couldn't find an agent named '{name}'",
        why="No agent with that name is registered in the catalog.",
        how=[
            f"Search for similar: kgents find '{name}'",
            "List all agents: kgents find '' --type=agent",
            f"Create it: kgents new agent '{name}'",
        ],
        see_also=["kgents find --help"],
        personality="Agents are like friends—sometimes we forget their exact names.",
    )


def command_not_found(
    cmd: str, suggestions: list[str] | None = None
) -> SympatheticError:
    """Create a sympathetic 'command not found' error."""
    how = ["kgents --help  # See all commands"]
    if suggestions:
        how = [f"kgents {s}  # Did you mean?" for s in suggestions[:3]] + how

    return SympatheticError(
        category=ErrorCategory.NOT_FOUND,
        what=f"'{cmd}' isn't a kgents command",
        why="I couldn't match this to any registered command.",
        how=how,
        personality="The CLI learns new tricks sometimes—check the help for recent additions.",
    )


def invalid_syntax(
    what: str, expected: str, got: str, example: str | None = None
) -> SympatheticError:
    """Create a sympathetic syntax error."""
    how = [f"Expected: {expected}"]
    if example:
        how.append(f"Example: {example}")

    return SympatheticError(
        category=ErrorCategory.SYNTAX,
        what=f"I couldn't parse {what}",
        why=f"Got '{got}' but expected {expected}.",
        how=how,
        technical=f"Parse error at: {got}",
        personality="Syntax is picky. Even a misplaced comma can trip things up.",
    )


def missing_argument(arg_name: str, command: str) -> SympatheticError:
    """Create a sympathetic 'missing argument' error."""
    return SympatheticError(
        category=ErrorCategory.INPUT,
        what=f"The '{command}' command needs a {arg_name}",
        why="This argument is required but wasn't provided.",
        how=[
            f"kgents {command} <{arg_name}>",
            f"kgents {command} --help  # See usage",
        ],
        personality="Arguments are like ingredients—some dishes just need them all.",
    )


def timeout_error(operation: str, duration_ms: int) -> SympatheticError:
    """Create a sympathetic timeout error."""
    seconds = duration_ms / 1000
    return SympatheticError(
        category=ErrorCategory.TIMEOUT,
        what=f"'{operation}' took too long ({seconds:.1f}s)",
        why="The operation exceeded its time budget and was cancelled.",
        how=[
            "--budget=high  # Allow more time",
            "Try a smaller input",
            "Check if external services are slow",
        ],
        technical=f"Timeout after {duration_ms}ms",
        personality="Patience is a virtue, but so is knowing when to stop waiting.",
    )


def internal_error(what: str, technical_details: str) -> SympatheticError:
    """Create a sympathetic internal error (bug)."""
    return SympatheticError(
        category=ErrorCategory.INTERNAL,
        what=f"Something unexpected happened: {what}",
        why="This looks like a bug. Sorry about that.",
        how=[
            "Try the operation again",
            "If it persists, please report it:",
            "  https://github.com/kgents/kgents/issues",
        ],
        technical=technical_details,
        personality="Even well-tested code has surprises. We'll fix it.",
    )


def principle_violation(principle: str, description: str) -> SympatheticError:
    """Create a sympathetic principle violation error."""
    return SympatheticError(
        category=ErrorCategory.PARADOX,
        what=f"This violates the '{principle}' principle",
        why=description,
        how=[
            "kgents principles  # Review the 7 principles",
            "Reconsider the design to align with principles",
        ],
        see_also=["spec/principles.md"],
        personality="Principles exist to guide, not to constrain. What would alignment look like?",
    )


def undecidable(question: str, options: list[str]) -> SympatheticError:
    """Create a sympathetic 'undecidable' error."""
    return SympatheticError(
        category=ErrorCategory.UNDECIDABLE,
        what=f"I can't decide: {question}",
        why="Multiple valid options exist and I need human judgment.",
        how=[f"  {i + 1}. {opt}" for i, opt in enumerate(options)],
        personality="Some choices require wisdom beyond algorithms. What feels right to you?",
    )


# =============================================================================
# Exception Integration
# =============================================================================


class KgentsError(Exception):
    """Base exception that carries sympathetic error info."""

    def __init__(self, sympathetic: SympatheticError):
        self.sympathetic = sympathetic
        super().__init__(sympathetic.what)


def handle_exception(exc: Exception, verbose: bool = False) -> str:
    """
    Convert any exception to a sympathetic message.

    If it's a KgentsError, use its sympathetic info.
    Otherwise, wrap it in a generic internal error.
    """
    if isinstance(exc, KgentsError):
        return exc.sympathetic.render(verbose=verbose)

    if isinstance(exc, FileNotFoundError):
        return file_not_found(str(exc.filename or exc)).render(verbose=verbose)

    if isinstance(exc, TimeoutError):
        return timeout_error(str(exc), 0).render(verbose=verbose)

    if isinstance(exc, KeyboardInterrupt):
        return "[...] Interrupted. No worries—nothing was left in a bad state."

    # Generic internal error
    return internal_error(
        str(exc),
        technical_details=f"{type(exc).__name__}: {exc}",
    ).render(verbose=verbose)
