"""
Gallery Runner: The main execution engine for projection demos.

The Gallery class provides:
1. Full catalog rendering (show_all)
2. Single widget focus (show)
3. Category filtering (show_category)
4. Side-by-side comparison (compare_targets)
5. Benchmark mode (benchmark)
6. Interactive mode (TUI with navigation)

Usage:
    gallery = Gallery()

    # Show everything
    gallery.show_all(target=RenderTarget.CLI)

    # Focus on one widget
    gallery.show("agent_card_active", target=RenderTarget.TUI)

    # Category view
    gallery.show_category(PilotCategory.PRIMITIVES)

    # Compare targets
    gallery.compare_targets("glyph_active")
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from agents.i.reactive.widget import KgentsWidget, RenderTarget
from protocols.projection.gallery.overrides import (
    DEFAULT_OVERRIDES,
    GalleryOverrides,
    get_overrides_from_env,
    merge_overrides,
)
from protocols.projection.gallery.pilots import (
    PILOT_REGISTRY,
    Pilot,
    PilotCategory,
    get_pilots_by_category,
    get_pilots_by_tag,
)


@dataclass
class RenderResult:
    """Result of rendering a pilot."""

    pilot_name: str
    target: RenderTarget
    output: Any
    render_time_ms: float
    success: bool
    error: str | None = None


@dataclass
class BenchmarkResult:
    """Result of benchmarking a pilot across targets."""

    pilot_name: str
    renders_per_second: dict[str, float] = field(default_factory=dict)
    avg_render_ms: dict[str, float] = field(default_factory=dict)


class Gallery:
    """
    Main gallery executor for projection component demonstrations.

    The Gallery orchestrates pilot rendering across all targets,
    with full override support for developer iteration.
    """

    def __init__(self, overrides: GalleryOverrides | None = None) -> None:
        """
        Initialize gallery with optional overrides.

        If no overrides provided, reads from environment variables.
        """
        env_overrides = get_overrides_from_env()
        self.overrides = merge_overrides(env_overrides, overrides) if overrides else env_overrides

    def _get_target(self, target: RenderTarget | None) -> RenderTarget:
        """Get target from argument, overrides, or default to CLI."""
        if target is not None:
            return target
        if self.overrides.target is not None:
            return self.overrides.target
        return RenderTarget.CLI

    def _build_pilot_overrides(
        self, pilot_name: str, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Build override dict for a specific pilot."""
        result: dict[str, Any] = {}

        # Add global overrides
        if self.overrides.entropy is not None:
            result["entropy"] = self.overrides.entropy
        if self.overrides.seed is not None:
            result["seed"] = self.overrides.seed
        if self.overrides.time_ms is not None:
            result["time_ms"] = self.overrides.time_ms
        if self.overrides.phase is not None:
            result["phase"] = self.overrides.phase
        if self.overrides.style is not None:
            result["style"] = self.overrides.style
        if self.overrides.breathing is not None:
            result["breathing"] = self.overrides.breathing

        # Add widget-specific overrides
        widget_overrides = self.overrides.get_widget_override(pilot_name)
        result.update(widget_overrides)

        # Add extra overrides (highest precedence)
        if extra:
            result.update(extra)

        return result

    def render(
        self,
        pilot_name: str,
        target: RenderTarget | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> RenderResult:
        """
        Render a single pilot and return the result.

        Args:
            pilot_name: Name of the pilot to render
            target: Render target (uses gallery default if None)
            overrides: Extra overrides for this render

        Returns:
            RenderResult with output and timing
        """
        target = self._get_target(target)

        if pilot_name not in PILOT_REGISTRY:
            return RenderResult(
                pilot_name=pilot_name,
                target=target,
                output=None,
                render_time_ms=0,
                success=False,
                error=f"Unknown pilot: {pilot_name}",
            )

        pilot = PILOT_REGISTRY[pilot_name]
        pilot_overrides = self._build_pilot_overrides(pilot_name, overrides)

        try:
            start = time.perf_counter()
            output = pilot.render(target, pilot_overrides)
            elapsed_ms = (time.perf_counter() - start) * 1000

            return RenderResult(
                pilot_name=pilot_name,
                target=target,
                output=output,
                render_time_ms=elapsed_ms,
                success=True,
            )
        except Exception as e:
            return RenderResult(
                pilot_name=pilot_name,
                target=target,
                output=None,
                render_time_ms=0,
                success=False,
                error=str(e),
            )

    def show(
        self,
        pilot_name: str,
        target: RenderTarget | None = None,
        overrides: dict[str, Any] | None = None,
    ) -> str:
        """
        Render a pilot and return formatted output for display.

        Args:
            pilot_name: Name of the pilot to show
            target: Render target
            overrides: Extra overrides

        Returns:
            Formatted string output
        """
        result = self.render(pilot_name, target, overrides)

        if not result.success:
            return f"[ERROR] {result.error}"

        lines = []

        if self.overrides.verbose:
            pilot = PILOT_REGISTRY[pilot_name]
            lines.append(f"--- {pilot_name} ---")
            lines.append(f"Category: {pilot.category.name}")
            lines.append(f"Description: {pilot.description}")
            lines.append(f"Tags: {', '.join(pilot.tags)}")
            lines.append(f"Render time: {result.render_time_ms:.2f}ms")
            lines.append("")

        # Format output based on target
        if result.target == RenderTarget.JSON:
            lines.append(json.dumps(result.output, indent=2, default=str))
        else:
            lines.append(str(result.output))

        return "\n".join(lines)

    def show_all(self, target: RenderTarget | None = None) -> str:
        """
        Render all pilots and return formatted output.

        Groups pilots by category for better organization.
        """
        target = self._get_target(target)
        sections = []

        sections.append("=" * 70)
        sections.append("  PROJECTION COMPONENT GALLERY")
        sections.append(f"  Target: {target.name} | Pilots: {len(PILOT_REGISTRY)}")
        sections.append("=" * 70)
        sections.append("")

        # Group by category
        for category in PilotCategory:
            pilots = get_pilots_by_category(category)
            if not pilots:
                continue

            sections.append(f"### {category.name} ###")
            sections.append("-" * 40)

            for pilot in pilots:
                result = self.render(pilot.name, target)
                if result.success:
                    sections.append(f"\n[{pilot.name}] {pilot.description}")
                    if target == RenderTarget.JSON:
                        sections.append(json.dumps(result.output, indent=2, default=str))
                    else:
                        sections.append(str(result.output))
                else:
                    sections.append(f"\n[{pilot.name}] ERROR: {result.error}")

            sections.append("")

        return "\n".join(sections)

    def show_category(self, category: PilotCategory, target: RenderTarget | None = None) -> str:
        """Render all pilots in a specific category."""
        target = self._get_target(target)
        pilots = get_pilots_by_category(category)

        if not pilots:
            return f"No pilots in category: {category.name}"

        sections = []
        sections.append(f"### {category.name} ({len(pilots)} pilots) ###")
        sections.append("-" * 40)

        for pilot in pilots:
            result = self.render(pilot.name, target)
            if result.success:
                sections.append(f"\n[{pilot.name}] {pilot.description}")
                if target == RenderTarget.JSON:
                    sections.append(json.dumps(result.output, indent=2, default=str))
                else:
                    sections.append(str(result.output))
            else:
                sections.append(f"\n[{pilot.name}] ERROR: {result.error}")

        return "\n".join(sections)

    def compare_targets(self, pilot_name: str) -> str:
        """
        Render a pilot to all targets for side-by-side comparison.

        Useful for verifying cross-target consistency.
        """
        if pilot_name not in PILOT_REGISTRY:
            return f"Unknown pilot: {pilot_name}"

        pilot = PILOT_REGISTRY[pilot_name]
        sections = []

        sections.append("=" * 70)
        sections.append(f"  TARGET COMPARISON: {pilot_name}")
        sections.append(f"  {pilot.description}")
        sections.append("=" * 70)

        for target in RenderTarget:
            result = self.render(pilot_name, target)
            sections.append(f"\n### {target.name} ###")

            if result.success:
                sections.append(f"(Rendered in {result.render_time_ms:.2f}ms)")
                if target == RenderTarget.JSON:
                    sections.append(json.dumps(result.output, indent=2, default=str))
                else:
                    sections.append(str(result.output))
            else:
                sections.append(f"ERROR: {result.error}")

        return "\n".join(sections)

    def benchmark(
        self,
        pilot_names: list[str] | None = None,
        iterations: int = 100,
    ) -> list[BenchmarkResult]:
        """
        Benchmark render performance across pilots and targets.

        Args:
            pilot_names: Pilots to benchmark (all if None)
            iterations: Number of iterations per pilot/target

        Returns:
            List of BenchmarkResult with timing data
        """
        if pilot_names is None:
            pilot_names = list(PILOT_REGISTRY.keys())

        results = []

        for pilot_name in pilot_names:
            if pilot_name not in PILOT_REGISTRY:
                continue

            pilot = PILOT_REGISTRY[pilot_name]
            benchmark = BenchmarkResult(pilot_name=pilot_name)

            for target in RenderTarget:
                pilot_overrides = self._build_pilot_overrides(pilot_name)

                # Warm up
                pilot.render(target, pilot_overrides)

                # Benchmark
                start = time.perf_counter()
                for _ in range(iterations):
                    pilot.render(target, pilot_overrides)
                elapsed = time.perf_counter() - start

                rps = iterations / elapsed
                avg_ms = (elapsed / iterations) * 1000

                benchmark.renders_per_second[target.name] = rps
                benchmark.avg_render_ms[target.name] = avg_ms

            results.append(benchmark)

        return results

    def format_benchmarks(self, results: list[BenchmarkResult]) -> str:
        """Format benchmark results as a table."""
        lines = []
        lines.append("=" * 80)
        lines.append("  RENDER PERFORMANCE BENCHMARKS")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = f"{'Pilot':<30} {'CLI':>10} {'TUI':>10} {'MARIMO':>10} {'JSON':>10}"
        lines.append(header)
        lines.append("-" * 80)

        # Rows
        for result in results:
            row = f"{result.pilot_name:<30}"
            for target in ["CLI", "TUI", "MARIMO", "JSON"]:
                rps = result.renders_per_second.get(target, 0)
                row += f" {rps:>9.0f}"
            lines.append(row)

        lines.append("-" * 80)
        lines.append("  (renders per second)")

        return "\n".join(lines)

    def list_pilots(self) -> str:
        """List all available pilots with descriptions."""
        lines = []
        lines.append("Available Pilots:")
        lines.append("-" * 60)

        for category in PilotCategory:
            pilots = get_pilots_by_category(category)
            if not pilots:
                continue

            lines.append(f"\n{category.name}:")
            for pilot in pilots:
                tags = ", ".join(pilot.tags[:3])
                lines.append(f"  {pilot.name:<30} [{tags}]")

        return "\n".join(lines)

    def iter_renders(
        self, target: RenderTarget | None = None
    ) -> Iterator[tuple[Pilot, RenderResult]]:
        """
        Iterate over all pilots, yielding (pilot, result) pairs.

        Useful for custom rendering pipelines.
        """
        target = self._get_target(target)

        for pilot_name, pilot in PILOT_REGISTRY.items():
            result = self.render(pilot_name, target)
            yield pilot, result


def run_gallery(
    target: RenderTarget | None = None,
    pilot_name: str | None = None,
    category: PilotCategory | None = None,
    compare: bool = False,
    benchmark: bool = False,
    list_only: bool = False,
    overrides: GalleryOverrides | None = None,
) -> str:
    """
    High-level gallery runner function.

    Args:
        target: Render target
        pilot_name: Specific pilot to show
        category: Category filter
        compare: Enable target comparison mode
        benchmark: Run benchmarks
        list_only: Just list pilots
        overrides: Gallery overrides

    Returns:
        Formatted output string
    """
    gallery = Gallery(overrides)

    if list_only:
        return gallery.list_pilots()

    if benchmark:
        if pilot_name:
            results = gallery.benchmark([pilot_name])
        elif category:
            pilots = [p.name for p in get_pilots_by_category(category)]
            results = gallery.benchmark(pilots)
        else:
            results = gallery.benchmark()
        return gallery.format_benchmarks(results)

    if compare and pilot_name:
        return gallery.compare_targets(pilot_name)

    if pilot_name:
        return gallery.show(pilot_name, target)

    if category:
        return gallery.show_category(category, target)

    return gallery.show_all(target)
