"""
AGENTESE Self Voice Context: Anti-Sausage Voice Gate.

Voice-related nodes for self.voice.gate.* paths:
- VoiceGateNode: Runtime Anti-Sausage enforcement

This node provides AGENTESE access to the VoiceGate primitive for
runtime voice checking and anchor tracking.

AGENTESE Paths:
    self.voice.gate.manifest  - Show gate configuration and stats
    self.voice.gate.check     - Check text for voice violations
    self.voice.gate.report    - Get detailed violation report

See: services/witness/voice_gate.py
See: CLAUDE.md (Anti-Sausage Protocol)
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# VoiceGateNode: AGENTESE Interface to VoiceGate
# =============================================================================


# VoiceGate affordances
VOICE_GATE_AFFORDANCES: tuple[str, ...] = ("manifest", "check", "report")


@node(
    "self.voice.gate",
    description="Anti-Sausage voice gate for runtime output checking",
)
@dataclass
class VoiceGateNode(BaseLogosNode):
    """
    self.voice.gate - Runtime Anti-Sausage enforcement.

    The VoiceGate checks outputs against voice rules and reports violations.
    It's the runtime enforcement of the Anti-Sausage Protocol from CLAUDE.md.

    Laws (from voice_gate.py):
    - Law 1 (Output Gating): All external outputs should pass VoiceGate
    - Law 2 (Denylist Blocking): Corporate-speak patterns block or warn
    - Law 3 (Anchor Tracking): Voice anchor references are tracked
    - Law 4 (Transformable): Violations can suggest transformations

    AGENTESE: self.voice.gate.*
    """

    _handle: str = "self.voice.gate"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Voice gate affordances available to all archetypes."""
        return VOICE_GATE_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Show voice gate configuration and cumulative stats.

        Returns:
            Gate configuration, anchor list, and stats
        """
        from services.witness.voice_gate import VOICE_ANCHORS, VoiceGate

        # Get or create gate
        gate = VoiceGate()

        manifest_data = {
            "path": self.handle,
            "description": "Anti-Sausage voice gate",
            "anchors": list(VOICE_ANCHORS),
            "denylist_count": len(gate.denylist),
            "hedge_pattern_count": len(gate.hedge_patterns),
            "block_denylist": gate.block_denylist,
            "block_hedges": gate.block_hedges,
            "stats": {
                "checks": gate._check_count,
                "violations": gate._violation_count,
                "anchors_tracked": gate._anchor_count,
            },
            "laws": [
                "Law 1: All external outputs should pass VoiceGate",
                "Law 2: Corporate-speak patterns block or warn",
                "Law 3: Voice anchor references are tracked",
                "Law 4: Violations can suggest transformations",
            ],
        }

        return BasicRendering(
            summary="Voice Gate (Anti-Sausage)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle VoiceGate-specific aspects."""
        match aspect:
            case "check":
                return self._check_text(**kwargs)
            case "report":
                return self._report_text(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Check text for voice violations",
    )
    def _check_text(
        self,
        text: str = "",
        strict: bool = False,
    ) -> dict[str, Any]:
        """
        Check text against voice rules.

        Args:
            text: The text to check for voice violations
            strict: If True, use strict mode (blocks denylist matches)

        Returns:
            VoiceCheckResult with pass/fail, violations, and anchors
        """
        from services.witness.voice_gate import VoiceGate

        # Create gate with appropriate strictness
        gate = VoiceGate.strict() if strict else VoiceGate.permissive()

        # Check the text
        result = gate.check(text)

        return {
            "passed": result.passed,
            "blocking_count": result.blocking_count,
            "warning_count": result.warning_count,
            "anchors_referenced": list(result.anchors_referenced),
            "violations": [v.to_dict() for v in result.violations],
            "warnings": [w.to_dict() for w in result.warnings],
            "checked_at": result.checked_at.isoformat(),
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Get detailed violation report with suggestions",
    )
    def _report_text(
        self,
        text: str = "",
    ) -> dict[str, Any]:
        """
        Get detailed violation report with transformation suggestions.

        Args:
            text: The text to analyze

        Returns:
            Detailed report with violations and suggested fixes
        """
        from services.witness.voice_gate import VoiceGate

        gate = VoiceGate()
        result = gate.check(text)

        # Build detailed report
        report_items = []
        for violation in result.violations:
            item = {
                "match": violation.match,
                "category": violation.rule.category,
                "action": violation.action.name,
                "reason": violation.rule.reason,
                "suggestion": violation.rule.suggestion,
                "context": violation.context,
            }
            report_items.append(item)

        return {
            "text_length": len(text),
            "passed": result.passed,
            "summary": {
                "blocking": result.blocking_count,
                "warnings": result.warning_count,
                "anchors": result.anchor_count,
            },
            "violations": report_items,
            "anchors_found": list(result.anchors_referenced),
            "anti_sausage_score": self._calculate_score(result),
        }

    # ==========================================================================
    # Public Interface (for direct calls / testing)
    # ==========================================================================

    def check(self, text: str, strict: bool = False) -> BasicRendering:
        """
        Check text against voice rules (public API).

        Args:
            text: The text to check for voice violations
            strict: If True, use strict mode (blocks denylist matches)

        Returns:
            BasicRendering with check results
        """
        data = self._check_text(text=text, strict=strict)
        return BasicRendering(
            summary="✓ Voice Check: PASSED" if data["passed"] else "✗ Voice Check: BLOCKED",
            content=self._format_check_cli(data),
            metadata=data,
        )

    def report(self, text: str) -> BasicRendering:
        """
        Get detailed violation report (public API).

        Args:
            text: The text to analyze

        Returns:
            BasicRendering with detailed report
        """
        data = self._report_text(text=text)
        return BasicRendering(
            summary=f"Voice Analysis Report (Score: {data['anti_sausage_score']:.0%})",
            content=self._format_report_cli(data),
            metadata=data,
        )

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Voice Gate (Anti-Sausage)",
            "=" * 40,
            "",
            "Anchors (quote, don't paraphrase):",
        ]
        for anchor in data["anchors"]:
            lines.append(f"  • {anchor}")

        lines.extend(
            [
                "",
                f"Denylist patterns: {data['denylist_count']}",
                f"Hedge patterns: {data['hedge_pattern_count']}",
                f"Block denylist: {data['block_denylist']}",
                f"Block hedges: {data['block_hedges']}",
            ]
        )

        return "\n".join(lines)

    def _format_check_cli(self, data: dict[str, Any]) -> str:
        """Format check result for CLI output."""
        status = "PASSED" if data["passed"] else "BLOCKED"
        emoji = "✓" if data["passed"] else "✗"

        lines = [
            f"{emoji} Voice Check: {status}",
            "",
        ]

        if data["anchors_referenced"]:
            lines.append("Anchors referenced:")
            for anchor in data["anchors_referenced"]:
                lines.append(f"  • {anchor}")
            lines.append("")

        if data["violations"]:
            lines.append("Violations:")
            for v in data["violations"]:
                action = v["rule"]["action"]
                match = v["match"]
                lines.append(f"  [{action}] '{match}'")

        if data["warnings"]:
            lines.append("")
            lines.append("Warnings:")
            for w in data["warnings"]:
                match = w["match"]
                lines.append(f"  ⚠ '{match}'")

        return "\n".join(lines)

    def _format_report_cli(self, data: dict[str, Any]) -> str:
        """Format detailed report for CLI output."""
        lines = [
            "Voice Analysis Report",
            "=" * 40,
            "",
            f"Text length: {data['text_length']} characters",
            f"Anti-Sausage Score: {data['anti_sausage_score']:.0%}",
            "",
        ]

        summary = data["summary"]
        lines.extend(
            [
                "Summary:",
                f"  • Blocking violations: {summary['blocking']}",
                f"  • Warnings: {summary['warnings']}",
                f"  • Anchors referenced: {summary['anchors']}",
                "",
            ]
        )

        if data["violations"]:
            lines.append("Violations (with suggestions):")
            for v in data["violations"]:
                lines.append(f"  [{v['action']}] '{v['match']}'")
                if v["reason"]:
                    lines.append(f"      Reason: {v['reason']}")
                if v["suggestion"]:
                    lines.append(f"      Suggestion: {v['suggestion']}")
            lines.append("")

        if data["anchors_found"]:
            lines.append("Anchors found (good!):")
            for anchor in data["anchors_found"]:
                lines.append(f"  ✓ {anchor}")

        return "\n".join(lines)

    def _calculate_score(self, result: Any) -> float:
        """
        Calculate Anti-Sausage score.

        Score is 1.0 if no violations and has anchors.
        Decreases with violations, increases with anchors.
        """
        base_score = 1.0

        # Deduct for violations
        base_score -= result.blocking_count * 0.2
        base_score -= result.warning_count * 0.05

        # Bonus for anchors
        base_score += result.anchor_count * 0.1

        # Clamp to [0.0, 1.0]
        clamped: float = max(0.0, min(1.0, base_score))
        return clamped


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "VoiceGateNode",
]
