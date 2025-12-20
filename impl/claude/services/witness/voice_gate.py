"""
VoiceGate: Anti-Sausage Runtime Enforcement.

The VoiceGate is the runtime enforcer of Kent's authentic voice. It checks
outputs against voice anchors and denylists corporate-speak patterns that
would dilute the persona.

Philosophy:
    "Kent's vision gets diluted through LLM processing. Each session smooths
    the rough edges. This gate preserves the authentic voice."

    Voice Anchors (quote, don't paraphrase):
    - "Daring, bold, creative, opinionated but not gaudy"
    - "The Mirror Test: Does K-gent feel like me on my best day?"
    - "Tasteful > feature-complete"
    - "The persona is a garden, not a museum"
    - "Depth over breadth"

Laws:
- Law 1 (Output Gating): All external outputs should pass VoiceGate
- Law 2 (Denylist Blocking): Corporate-speak patterns block or warn
- Law 3 (Anchor Tracking): Voice anchor references are tracked
- Law 4 (Transformable): Violations can suggest transformations

See: CLAUDE.md (Anti-Sausage Protocol)
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Voice Anchors (The Authentic Voice)
# =============================================================================

VOICE_ANCHORS: tuple[str, ...] = (
    "Daring, bold, creative, opinionated but not gaudy",
    "The Mirror Test",
    "Tasteful > feature-complete",
    "The persona is a garden, not a museum",
    "Depth over breadth",
)

# =============================================================================
# Denylist Patterns (Corporate Speak to Avoid)
# =============================================================================

# These patterns indicate voice dilution - corporate speak that smooths
# Kent's rough edges. They should trigger warnings or blocks.
DENYLIST_PATTERNS: tuple[str, ...] = (
    r"\bleverage\b",  # Corporate buzzword
    r"\bsynergy\b",  # The quintessential corporate-speak
    r"\bsynergies\b",  # Plural form
    r"\bactionable\b",  # Management-speak
    r"\bmoving forward\b",  # Hedge phrase
    r"\bholistic\b",  # Vague corporate
    r"\bat the end of the day\b",  # Cliche
    r"\bparadigm shift\b",  # Overused jargon
    r"\bdrilling? down\b",  # Management-speak
    r"\bcircle back\b",  # Corporate action item
    r"\blow-hanging fruit\b",  # Lazy metaphor
    r"\bbest practices\b",  # Anti-opinion (defer to consensus)
    r"\bstakeholders?\b",  # Corporate distancing
    r"\bimpactful\b",  # Non-word made corporate
    r"\btouch base\b",  # Sports metaphor abuse
    r"\boptimize\b",  # Often vague (optimize what?)
)

# These patterns indicate hedging that dilutes opinionated stance
HEDGE_PATTERNS: tuple[str, ...] = (
    r"\bperhaps\b",  # Weakening
    r"\bmaybe\b",  # Hedging (sometimes ok, often weak)
    r"\bcould potentially\b",  # Double hedge
    r"\bmight be able to\b",  # Triple hedge
    r"\bit seems like\b",  # Distancing from opinion
    r"\bone might argue\b",  # Academic hedge
)

# =============================================================================
# Voice Action Types
# =============================================================================


class VoiceAction(Enum):
    """Action to take on voice rule match."""

    PASS = auto()  # Explicitly passed (anchor referenced, etc.)
    WARN = auto()  # Warning issued, output allowed
    BLOCK = auto()  # Output blocked until fixed
    TRANSFORM = auto()  # Suggest transformation


# =============================================================================
# Voice Rule
# =============================================================================


@dataclass(frozen=True)
class VoiceRule:
    """
    A rule for voice checking.

    Rules match patterns in text and trigger actions.

    Example:
        >>> rule = VoiceRule(
        ...     pattern=r"\\bleverage\\b",
        ...     action=VoiceAction.WARN,
        ...     reason="Corporate buzzword dilutes authentic voice",
        ...     suggestion="Use 'use' or 'apply' instead",
        ... )
    """

    pattern: str  # Regex pattern to match
    action: VoiceAction  # What to do on match
    reason: str = ""  # Why this pattern is flagged
    suggestion: str = ""  # How to fix (for TRANSFORM)
    category: str = "denylist"  # "denylist", "hedge", "custom"

    @property
    def compiled(self) -> re.Pattern[str]:
        """Get compiled regex pattern."""
        return re.compile(self.pattern, re.IGNORECASE)

    def matches(self, text: str) -> list[str]:
        """Find all matches in text."""
        return self.compiled.findall(text)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern": self.pattern,
            "action": self.action.name,
            "reason": self.reason,
            "suggestion": self.suggestion,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceRule:
        """Create from dictionary."""
        return cls(
            pattern=data["pattern"],
            action=VoiceAction[data.get("action", "WARN")],
            reason=data.get("reason", ""),
            suggestion=data.get("suggestion", ""),
            category=data.get("category", "denylist"),
        )


# =============================================================================
# Voice Violation
# =============================================================================


@dataclass(frozen=True)
class VoiceViolation:
    """
    A detected voice violation.

    Captures what was found, where, and what to do about it.
    """

    rule: VoiceRule
    match: str  # The matched text
    context: str = ""  # Surrounding context (if available)
    position: int = -1  # Position in text (-1 if unknown)

    @property
    def action(self) -> VoiceAction:
        """Get the action for this violation."""
        return self.rule.action

    @property
    def is_blocking(self) -> bool:
        """Check if this violation blocks output."""
        return self.rule.action == VoiceAction.BLOCK

    @property
    def is_warning(self) -> bool:
        """Check if this is a warning."""
        return self.rule.action == VoiceAction.WARN

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule": self.rule.to_dict(),
            "match": self.match,
            "context": self.context,
            "position": self.position,
        }


# =============================================================================
# Voice Check Result
# =============================================================================


@dataclass(frozen=True)
class VoiceCheckResult:
    """
    Result of checking text against voice rules.

    Law 1: All external outputs should pass VoiceGate.
    Law 3: Anchor references are tracked.
    """

    passed: bool  # Did the check pass (no BLOCK violations)?
    violations: tuple[VoiceViolation, ...] = ()  # All violations
    warnings: tuple[VoiceViolation, ...] = ()  # WARN-level only
    anchors_referenced: tuple[str, ...] = ()  # Voice anchors found
    checked_at: datetime = field(default_factory=datetime.now)

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were found."""
        return len(self.warnings) > 0

    @property
    def blocking_count(self) -> int:
        """Count of blocking violations."""
        return sum(1 for v in self.violations if v.is_blocking)

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len(self.warnings)

    @property
    def anchor_count(self) -> int:
        """Count of anchor references."""
        return len(self.anchors_referenced)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": [w.to_dict() for w in self.warnings],
            "anchors_referenced": list(self.anchors_referenced),
            "checked_at": self.checked_at.isoformat(),
        }


# =============================================================================
# VoiceGate: The Core Primitive
# =============================================================================


@dataclass
class VoiceGate:
    """
    Runtime Anti-Sausage enforcement.

    Laws:
    - Law 1 (Output Gating): All external outputs should pass
    - Law 2 (Denylist Blocking): Corporate-speak patterns block/warn
    - Law 3 (Anchor Tracking): Voice anchor references are tracked
    - Law 4 (Transformable): Violations can suggest transformations

    The VoiceGate checks text against voice rules and reports violations.
    It's the runtime enforcement of the Anti-Sausage Protocol.

    Example:
        >>> gate = VoiceGate()
        >>> result = gate.check("We need to leverage synergies")
        >>> result.passed  # False - blocked by "leverage" and "synergies"

        >>> result = gate.check("Tasteful > feature-complete is our mantra")
        >>> result.anchors_referenced  # ("Tasteful > feature-complete",)
    """

    # Voice anchors to track (quote, don't paraphrase)
    anchors: tuple[str, ...] = VOICE_ANCHORS

    # Denylist patterns (corporate speak to avoid)
    denylist: tuple[str, ...] = DENYLIST_PATTERNS

    # Hedge patterns (weakening language)
    hedge_patterns: tuple[str, ...] = HEDGE_PATTERNS

    # Custom rules
    rules: list[VoiceRule] = field(default_factory=list)

    # Configuration
    block_denylist: bool = False  # If True, denylist matches BLOCK; else WARN
    block_hedges: bool = False  # If True, hedge matches BLOCK; else WARN
    track_anchors: bool = True  # Track anchor references
    context_window: int = 50  # Characters of context around matches

    # Stats
    _check_count: int = field(default=0, repr=False)
    _violation_count: int = field(default=0, repr=False)
    _anchor_count: int = field(default=0, repr=False)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def strict(cls) -> VoiceGate:
        """Create a strict VoiceGate that blocks denylist matches."""
        return cls(block_denylist=True, block_hedges=True)

    @classmethod
    def permissive(cls) -> VoiceGate:
        """Create a permissive VoiceGate that only warns."""
        return cls(block_denylist=False, block_hedges=False)

    @classmethod
    def with_custom_rules(cls, rules: list[VoiceRule]) -> VoiceGate:
        """Create with custom rules added."""
        return cls(rules=rules)

    # =========================================================================
    # Core Check (Laws 1-3)
    # =========================================================================

    def check(self, text: str) -> VoiceCheckResult:
        """
        Check text against voice rules.

        Law 1: All external outputs should pass.
        Law 2: Denylist patterns block or warn.
        Law 3: Anchor references are tracked.

        Args:
            text: The text to check

        Returns:
            VoiceCheckResult with violations, warnings, and anchors
        """
        self._check_count += 1

        violations: list[VoiceViolation] = []
        warnings: list[VoiceViolation] = []
        anchors_found: list[str] = []

        # Check denylist patterns (Law 2)
        action = VoiceAction.BLOCK if self.block_denylist else VoiceAction.WARN
        for pattern in self.denylist:
            rule = VoiceRule(
                pattern=pattern,
                action=action,
                reason="Corporate-speak dilutes authentic voice",
                category="denylist",
            )
            for match in rule.matches(text):
                violation = VoiceViolation(
                    rule=rule,
                    match=match,
                    context=self._get_context(text, match),
                )
                violations.append(violation)
                if violation.is_warning:
                    warnings.append(violation)

        # Check hedge patterns
        hedge_action = VoiceAction.BLOCK if self.block_hedges else VoiceAction.WARN
        for pattern in self.hedge_patterns:
            rule = VoiceRule(
                pattern=pattern,
                action=hedge_action,
                reason="Hedging weakens opinionated stance",
                category="hedge",
            )
            for match in rule.matches(text):
                violation = VoiceViolation(
                    rule=rule,
                    match=match,
                    context=self._get_context(text, match),
                )
                violations.append(violation)
                if violation.is_warning:
                    warnings.append(violation)

        # Check custom rules
        for rule in self.rules:
            for match in rule.matches(text):
                violation = VoiceViolation(
                    rule=rule,
                    match=match,
                    context=self._get_context(text, match),
                )
                violations.append(violation)
                if violation.is_warning:
                    warnings.append(violation)

        # Track anchor references (Law 3)
        if self.track_anchors:
            for anchor in self.anchors:
                # Case-insensitive search for anchor (or key phrase)
                key_phrase = anchor.split(",")[0] if "," in anchor else anchor
                if key_phrase.lower() in text.lower():
                    anchors_found.append(anchor)
                    self._anchor_count += 1

        self._violation_count += len(violations)

        # Determine if passed (no BLOCK violations)
        passed = not any(v.is_blocking for v in violations)

        return VoiceCheckResult(
            passed=passed,
            violations=tuple(violations),
            warnings=tuple(warnings),
            anchors_referenced=tuple(anchors_found),
        )

    def _get_context(self, text: str, match: str) -> str:
        """Get surrounding context for a match."""
        pos = text.lower().find(match.lower())
        if pos == -1:
            return ""

        start = max(0, pos - self.context_window)
        end = min(len(text), pos + len(match) + self.context_window)

        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def is_clean(self, text: str) -> bool:
        """Quick check if text passes with no violations."""
        return self.check(text).passed

    def has_corporate_speak(self, text: str) -> bool:
        """Check if text contains any denylist patterns."""
        for pattern in self.denylist:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def has_hedging(self, text: str) -> bool:
        """Check if text contains hedging language."""
        for pattern in self.hedge_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def references_anchor(self, text: str) -> str | None:
        """Check if text references any voice anchor. Returns first match."""
        for anchor in self.anchors:
            key_phrase = anchor.split(",")[0] if "," in anchor else anchor
            if key_phrase.lower() in text.lower():
                return anchor
        return None

    # =========================================================================
    # Rule Management
    # =========================================================================

    def add_rule(self, rule: VoiceRule) -> None:
        """Add a custom rule."""
        self.rules.append(rule)

    def add_denylist_pattern(
        self,
        pattern: str,
        reason: str = "Custom denylist pattern",
    ) -> None:
        """Add a pattern to the denylist."""
        self.rules.append(
            VoiceRule(
                pattern=pattern,
                action=VoiceAction.BLOCK if self.block_denylist else VoiceAction.WARN,
                reason=reason,
                category="denylist",
            )
        )

    # =========================================================================
    # Transform Support (Law 4)
    # =========================================================================

    def suggest_transforms(self, text: str) -> list[tuple[str, str, str]]:
        """
        Suggest transformations for violations.

        Law 4: Violations can suggest transformations.

        Returns list of (original, suggestion, reason) tuples.
        """
        result = self.check(text)
        transforms: list[tuple[str, str, str]] = []

        for violation in result.violations:
            if violation.rule.suggestion:
                transforms.append(
                    (violation.match, violation.rule.suggestion, violation.rule.reason)
                )

        return transforms

    # =========================================================================
    # Stats
    # =========================================================================

    @property
    def stats(self) -> dict[str, int]:
        """Get check statistics."""
        return {
            "check_count": self._check_count,
            "violation_count": self._violation_count,
            "anchor_count": self._anchor_count,
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._check_count = 0
        self._violation_count = 0
        self._anchor_count = 0

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anchors": list(self.anchors),
            "denylist": list(self.denylist),
            "hedge_patterns": list(self.hedge_patterns),
            "rules": [r.to_dict() for r in self.rules],
            "block_denylist": self.block_denylist,
            "block_hedges": self.block_hedges,
            "track_anchors": self.track_anchors,
            "context_window": self.context_window,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceGate:
        """Create from dictionary."""
        return cls(
            anchors=tuple(data.get("anchors", VOICE_ANCHORS)),
            denylist=tuple(data.get("denylist", DENYLIST_PATTERNS)),
            hedge_patterns=tuple(data.get("hedge_patterns", HEDGE_PATTERNS)),
            rules=[VoiceRule.from_dict(r) for r in data.get("rules", [])],
            block_denylist=data.get("block_denylist", False),
            block_hedges=data.get("block_hedges", False),
            track_anchors=data.get("track_anchors", True),
            context_window=data.get("context_window", 50),
        )


# =============================================================================
# Global Instance
# =============================================================================

_global_voice_gate: VoiceGate | None = None


def get_voice_gate() -> VoiceGate:
    """Get the global voice gate."""
    global _global_voice_gate
    if _global_voice_gate is None:
        _global_voice_gate = VoiceGate()
    return _global_voice_gate


def set_voice_gate(gate: VoiceGate) -> None:
    """Set the global voice gate."""
    global _global_voice_gate
    _global_voice_gate = gate


def reset_voice_gate() -> None:
    """Reset the global voice gate (for testing)."""
    global _global_voice_gate
    _global_voice_gate = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Constants
    "VOICE_ANCHORS",
    "DENYLIST_PATTERNS",
    "HEDGE_PATTERNS",
    # Types
    "VoiceAction",
    "VoiceRule",
    "VoiceViolation",
    "VoiceCheckResult",
    # Core
    "VoiceGate",
    # Global
    "get_voice_gate",
    "set_voice_gate",
    "reset_voice_gate",
]
