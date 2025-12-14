"""
Soul Approve Handler: Would Kent approve this action?

K-gent Soul Approve is a Pro Crown Jewel that acts as ethical conscience.
Uses KgentSoul.intercept_deep() to check if an action aligns with Kent's values.

This is different from the YIELD governance approve - this is philosophical/ethical approval.

Usage:
    kgents soul approve "delete all tests"
    kgents soul approve "add another abstraction layer"
    kgents soul approve "ship without documentation" --json

The approval check returns:
- verdict: WOULD APPROVE / WOULD NOT APPROVE
- reasoning: Why this aligns or violates principles
- violations: List of principle violations (if any)
- alternative: Suggested alternative approach (if rejected)

This is Pro-only because it requires deep LLM reasoning using intercept_deep().

Note: This command is under the 'soul' namespace to avoid conflicting with
      the Turn-gents YIELD approval command (kgents approve).
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for soul approve command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents soul approve "delete this unused code"')
    print('  kgents soul approve "add comprehensive logging"')
    print('  kgents soul approve "skip writing tests"')
    print()
    print("PHILOSOPHY:")
    print("  This is your ethical conscience - Kent's values as a second opinion.")
    print("  It doesn't enforce - it advises based on principles.")
    print("  Use it to check yourself before questionable decisions.")


def cmd_soul_approve(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    K-gent Soul Approve: Check if Kent would approve an action.

    Usage:
        kgents soul approve "action description" [--json]

    Returns:
        0 if would approve, 1 if would not approve, 2 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("soul_approve", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Extract action description (everything that's not a flag)
    action_parts: list[str] = []
    for arg in args:
        if arg.startswith("-"):
            continue
        action_parts.append(arg)

    if not action_parts:
        _emit_output(
            "[SOUL:APPROVE] X Error: No action description provided\n"
            'Usage: kgents soul approve "action description"',
            {"error": "No action description provided"},
            ctx,
        )
        return 2

    action = " ".join(action_parts)

    # Run async handler
    return asyncio.run(_async_soul_approve(action, json_mode, ctx))


async def _async_soul_approve(
    action: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of soul approve command."""
    try:
        from agents.k import KgentSoul

        # Get soul instance
        soul = _get_soul()

        # Check approval using intercept_deep()
        result = await _check_approval(soul, action)

        # Determine exit code based on verdict
        exit_code = 0 if result["verdict"] == "WOULD APPROVE" else 1

        # Output
        semantic = {
            "command": "soul_approve",
            "action": action,
            "result": result,
        }

        if json_mode:
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                "[SOUL:APPROVE] Governance Check",
                "",
                f"Action: {action}",
                "",
            ]

            # Verdict with icon
            if result["verdict"] == "WOULD APPROVE":
                lines.append("✓ VERDICT: WOULD APPROVE")
            else:
                lines.append("✗ VERDICT: WOULD NOT APPROVE")

            lines.extend(
                [
                    "",
                    "REASONING:",
                    f"  {result['reasoning']}",
                    "",
                ]
            )

            # Show violations if any
            if result["violations"]:
                lines.append("PRINCIPLE VIOLATIONS:")
                for violation in result["violations"]:
                    lines.append(f"  • {violation}")
                lines.append("")

            # Show alternative if suggested
            if result["alternative"]:
                lines.append("ALTERNATIVE SUGGESTION:")
                lines.append(f"  {result['alternative']}")
                lines.append("")

            # Show confidence
            confidence = result.get("confidence", 0.5)
            lines.append(f"Confidence: {confidence:.0%}")

            _emit_output("\n".join(lines), semantic, ctx)

        return exit_code

    except ImportError as e:
        _emit_output(
            f"[SOUL:APPROVE] X K-gent module not available: {e}",
            {"error": f"K-gent module not available: {e}"},
            ctx,
        )
        return 2
    except Exception as e:
        _emit_output(
            f"[SOUL:APPROVE] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 2


async def _check_approval(
    soul: Any,
    action: str,
) -> dict[str, Any]:
    """
    Check if action would be approved using K-gent intercept_deep().

    Creates a SemaphoreToken-like object and uses intercept_deep() for governance.
    """

    # Create a mock semaphore token
    class MockToken:
        def __init__(self, prompt: str):
            self.id = "soul-approve-check"
            self.prompt = prompt
            self.reason = "Checking if this action aligns with Kent's principles"
            self.severity = 0.5

    token = MockToken(action)

    # Use intercept_deep() for governance check
    intercept_result = await soul.intercept_deep(token)

    # Map intercept result to approval verdict
    verdict = "WOULD NOT APPROVE"  # Default to rejection
    violations: list[str] = []
    alternative = ""

    if intercept_result.recommendation == "approve":
        verdict = "WOULD APPROVE"
    elif intercept_result.recommendation == "reject":
        verdict = "WOULD NOT APPROVE"
        violations = intercept_result.matching_principles
        # Generate alternative suggestion
        alternative = _suggest_alternative(action, intercept_result.reasoning)
    else:  # escalate
        verdict = "WOULD NOT APPROVE"
        violations = ["REQUIRES_HUMAN_JUDGMENT"]
        alternative = "This requires deeper consideration beyond automated checks."

    return {
        "verdict": verdict,
        "reasoning": intercept_result.reasoning or "No reasoning provided",
        "violations": violations,
        "alternative": alternative,
        "confidence": intercept_result.confidence,
    }


def _suggest_alternative(action: str, reasoning: str) -> str:
    """
    Generate an alternative suggestion based on the action and reasoning.

    This is a simple heuristic - in a future version, could use LLM.
    """
    action_lower = action.lower()

    # Heuristic suggestions based on common patterns
    if "delete" in action_lower or "remove" in action_lower:
        if "test" in action_lower:
            return "Instead of deleting tests, refactor them to be more focused."
        return "Instead of deleting, deprecate or move to archive."

    if "skip" in action_lower:
        if "test" in action_lower:
            return "Write minimal tests for critical paths only."
        if "doc" in action_lower:
            return "Write inline comments at minimum, defer full docs."
        return "Consider: what's the minimum viable version?"

    if "add" in action_lower and "abstraction" in action_lower:
        return "Ask: does this abstraction compress complexity or just move it?"

    if "logging" in action_lower or "print" in action_lower:
        return "Use structured logging sparingly, only for essential state changes."

    # Generic alternative based on reasoning
    if "minimal" in reasoning.lower():
        return "Take the most minimal approach that solves the problem."
    if "abstract" in reasoning.lower():
        return "Express this as a morphism or functor instead."

    return "Reconsider whether this action is necessary."


# Module-level soul instance (singleton for CLI session)
_soul_instance: Any = None


def _get_soul() -> Any:
    """
    Get or create the K-gent Soul instance.

    Resolution order:
    1. Try to get from lifecycle state (shared across CLI session)
    2. Fall back to module-level singleton (in-memory)
    """
    from agents.k import KgentSoul

    global _soul_instance

    # Try to get from lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state

        lifecycle_state = get_lifecycle_state()
        if lifecycle_state is not None:
            soul = getattr(lifecycle_state, "soul", None)
            if soul is not None:
                return soul
    except ImportError:
        pass

    # Fall back to module-level singleton
    if _soul_instance is None:
        _soul_instance = KgentSoul()
    return _soul_instance


def set_soul(soul: Any) -> None:
    """Set the module-level soul instance."""
    global _soul_instance
    _soul_instance = soul


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
