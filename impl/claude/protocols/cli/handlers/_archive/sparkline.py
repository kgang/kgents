"""
Sparkline Handler: Render numbers as Unicode sparkline visualization.

Pure utility command - no agent dependencies, no LLM calls.

Usage:
    kgents sparkline 47 20 15 30 45    # → ▅▂▁▃▅
    kgents sparkline --height 2 1 2 3  # Double height (not implemented yet)
    echo "1,2,3,4" | kgents sparkline  # Piped input

Characters: ▁▂▃▄▅▆▇█ (8 levels)

AGENTESE Path: world.viz.sparkline
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Unicode sparkline characters (8 levels)
SPARK_CHARS = "▁▂▃▄▅▆▇█"


@dataclass
class SparklineResult:
    """Result of sparkline rendering."""

    values: list[float]
    rendered: str
    min_val: float
    max_val: float

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "values": self.values,
            "rendered": self.rendered,
            "min": self.min_val,
            "max": self.max_val,
            "count": len(self.values),
        }


def render_sparkline(values: list[float]) -> str:
    """
    Pure function: numbers -> sparkline string.

    Maps each value to one of 8 Unicode block characters based on
    its position in the min-max range.

    Args:
        values: List of numeric values

    Returns:
        Unicode sparkline string
    """
    if not values:
        return ""

    if len(values) == 1:
        return SPARK_CHARS[4]  # Middle height for single value

    min_v, max_v = min(values), max(values)
    span = max_v - min_v if max_v > min_v else 1

    return "".join(SPARK_CHARS[min(7, int((v - min_v) / span * 7.99))] for v in values)


def parse_numbers(args: list[str]) -> list[float]:
    """
    Parse numbers from arguments or stdin.

    Supports:
    - Space-separated: 1 2 3 4
    - Comma-separated: 1,2,3,4
    - Mixed: 1 2,3 4
    - Piped: echo "1 2 3" | kgents sparkline
    """
    numbers: list[float] = []

    # Check for piped input
    if not sys.stdin.isatty() and not args:
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            args = [stdin_data]

    for arg in args:
        # Skip flags
        if arg.startswith("-"):
            continue

        # Handle comma-separated values
        if "," in arg:
            parts = arg.split(",")
        else:
            parts = [arg]

        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                numbers.append(float(part))
            except ValueError:
                pass  # Skip non-numeric

    return numbers


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | SparklineResult",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, SparklineResult) else semantic
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for sparkline command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents sparkline 1 2 3 4 5           # → ▁▂▄▅█")
    print("  kgents sparkline 10 20 15 25 30      # → ▁▄▂▆█")
    print('  echo "5,10,3,8" | kgents sparkline   # → ▃█▁▆')
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: self.soul.tension >> world.viz.sparkline")
    print("  (Visualize tension severity as sparkline)")


def cmd_sparkline(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Render numbers as Unicode sparkline.

    AGENTESE Path: world.viz.sparkline

    This is a "sink" command - it produces terminal output and
    composes on the left only (receives data, doesn't emit structured output).

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("sparkline", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args

    # Filter out flags from args
    value_args = [a for a in args if not a.startswith("-")]

    # Parse numbers
    numbers = parse_numbers(value_args)

    if not numbers:
        _emit_output(
            "[SPARKLINE] Provide numbers to visualize\n"
            "  Example: kgents sparkline 1 2 3 4 5",
            {"error": "missing_input", "suggestion": "Provide numbers"},
            ctx,
        )
        return 1

    # Render sparkline
    rendered = render_sparkline(numbers)
    result = SparklineResult(
        values=numbers,
        rendered=rendered,
        min_val=min(numbers),
        max_val=max(numbers),
    )

    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        # Simple output: just the sparkline
        print(rendered)

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0


# =============================================================================
# Sparklinable Protocol (for pipeline composition)
# =============================================================================


def to_sparkline(data: "list[float] | dict[str, Any]") -> str:
    """
    Convert data to sparkline.

    Supports:
    - list[float]: Direct rendering
    - dict with 'values' key: Extract and render
    - dict with numeric values: Extract values and render
    """
    if isinstance(data, list):
        return render_sparkline(data)

    if isinstance(data, dict):
        if "values" in data and isinstance(data["values"], list):
            return render_sparkline([float(v) for v in data["values"]])

        # Try to extract numeric values from dict
        numeric_values = [v for v in data.values() if isinstance(v, int | float)]
        if numeric_values:
            return render_sparkline(numeric_values)

    return ""
