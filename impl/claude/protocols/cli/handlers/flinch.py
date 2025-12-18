"""
Flinch Handler: Test failure analysis from accumulated algedonic signals.

Trust Loop Integration - Horizon 1.

The FlinchStore captures test failures to .kgents/ghost/test_flinches.jsonl.
This command surfaces that data for analysis.

Usage:
    kgents flinch              # Summarize recent test failures
    kgents flinch --patterns   # Show recurring failure patterns
    kgents flinch --hot        # Files with highest failure rate
    kgents flinch --recent N   # Show N most recent failures
    kgents flinch --since 1h   # Failures since 1 hour ago
    kgents flinch --traces     # Show failures with call trace correlation
    kgents flinch --turns      # Show Turn-gents panel (causal debugging)

Example:
    $ kgents flinch
    [FLINCH] Test Failure Summary
    Total: 820 failures recorded
    Last hour: 0
    Last 24h: 5

    Hot files:
      test_foo.py: 32 failures
      test_bar.py: 18 failures

    $ kgents flinch --patterns
    [FLINCH] Recurring Failure Patterns

    test_graph.py (32 failures)
      Most common: test_setup_fixture (28 times)
      Pattern: Setup phase failures suggest fixture issue

    $ kgents flinch --traces
    [FLINCH] Test Failure Analysis with Call Traces

    test_flux_agent.py::test_process_event (5 failures)
    ├─ Last failure: 2h ago
    ├─ Call trace at failure:
    │   FluxAgent.process
    │   └─ EventProcessor.validate
    │       └─ SchemaValidator.check  <-- EXCEPTION HERE
    ├─ Probable root cause: SchemaValidator.check
    └─ Related failures: test_schema_validation (same path)

Trust Signal: The system noticed patterns in your test failures.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def cmd_flinch(args: list[str]) -> int:
    """
    Analyze test failures from FlinchStore.

    Surfaces patterns from accumulated algedonic signals.
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    patterns_mode = "--patterns" in args
    hot_mode = "--hot" in args
    recent_mode = "--recent" in args
    traces_mode = "--traces" in args
    turns_mode = "--turns" in args

    if help_mode:
        print(__doc__)
        return 0

    # Handle turns mode (Turn-gents integration)
    if turns_mode:
        return _show_turns_panel()

    # Get project root (look for .kgents directory or HYDRATE.md)
    from protocols.cli.hollow import find_kgents_root

    project_root = find_kgents_root()
    if project_root is None:
        # Try to find the repo root by looking for HYDRATE.md
        current = Path.cwd()
        while current != current.parent:
            if (current / "HYDRATE.md").exists() or (current / ".kgents").exists():
                project_root = current
                break
            current = current.parent
        if project_root is None:
            project_root = Path.cwd()

    flinch_path = project_root / ".kgents" / "ghost" / "test_flinches.jsonl"

    if not flinch_path.exists():
        print("[FLINCH] No flinch data found")
        print(f"  Expected: {flinch_path}")
        print()
        print("Run tests with pytest to generate flinch data.")
        return 0

    if traces_mode:
        return _show_traces(flinch_path, project_root)
    elif patterns_mode:
        return _show_patterns(flinch_path)
    elif hot_mode:
        return _show_hot_files(flinch_path)
    elif recent_mode:
        # Get count from args
        try:
            idx = args.index("--recent")
            count = int(args[idx + 1]) if idx + 1 < len(args) else 10
        except (ValueError, IndexError):
            count = 10
        return _show_recent(flinch_path, count)
    else:
        return _show_summary(flinch_path)


def _show_summary(flinch_path: Path) -> int:
    """Show flinch summary."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    result = asyncio.run(collector.collect())

    if not result.success:
        print(f"[FLINCH] Error: {result.error}")
        return 1

    data = result.data

    print("[FLINCH] Test Failure Summary")
    print("=" * 40)
    print(f"Total failures: {data.get('total', 0)}")
    print(f"Last hour: {data.get('last_hour', 0)}")
    print(f"Last 24h: {data.get('last_24h', 0)}")
    print()

    hot_files = data.get("hot_files", [])
    if hot_files:
        print("Hot files (most failures):")
        for file_path, count in hot_files[:5]:
            print(f"  {file_path}: {count} failures")
        print()

    recurring = data.get("top_recurring", [])
    if recurring:
        print("Recurring failures:")
        for test, count in recurring[:5]:
            # Truncate long test names
            if len(test) > 60:
                test = "..." + test[-57:]
            print(f"  {test}: {count}x")
        print()

    # Trust signal
    last_hour = data.get("last_hour", 0)
    if last_hour > 0:
        print(f"[ALERT] {last_hour} failures in the last hour!")
    elif data.get("total", 0) > 0:
        print("[OK] No recent failures (last hour)")

    return 0


def _show_patterns(flinch_path: Path) -> int:
    """Show recurring failure patterns."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    patterns_data = collector.get_patterns()

    print("[FLINCH] Recurring Failure Patterns")
    print("=" * 40)
    print(f"Total flinches: {patterns_data.get('total_flinches', 0)}")
    print(f"Modules with failures: {patterns_data.get('total_modules_with_failures', 0)}")
    print()

    patterns = patterns_data.get("patterns", [])
    if not patterns:
        print("No recurring patterns detected (threshold: 3+ failures)")
        return 0

    print("Patterns (3+ failures):")
    print()

    for p in patterns[:10]:
        module = p["module"]
        total = p["total_failures"]
        most_common = p["most_common_test"]
        most_count = p["most_common_count"]

        print(f"  {module}")
        print(f"    Total failures: {total}")
        print(f"    Most common test: {most_common} ({most_count}x)")

        # Infer pattern type
        if "setup" in most_common.lower() or "fixture" in most_common.lower():
            print("    Pattern: Setup/fixture failures - check test infrastructure")
        elif "timeout" in most_common.lower():
            print("    Pattern: Timeout failures - check async handling")
        elif "stream" in most_common.lower() or "parse" in most_common.lower():
            print("    Pattern: Parsing failures - check input handling")
        print()

    return 0


def _show_hot_files(flinch_path: Path) -> int:
    """Show files with highest failure rate."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    hot_files = collector.get_hot_files(limit=20)

    print("[FLINCH] Hot Files (Most Failures)")
    print("=" * 40)

    if not hot_files:
        print("No failure data available")
        return 0

    # Calculate max for bar chart
    max_count = hot_files[0][1] if hot_files else 1

    for file_path, count in hot_files:
        # Visual bar
        bar_width = int((count / max_count) * 30)
        bar = "#" * bar_width

        # Truncate long paths
        if len(file_path) > 50:
            file_path = "..." + file_path[-47:]

        print(f"  {file_path}")
        print(f"    {count:4d} {bar}")

    print()
    print("Suggestion: Focus on the hottest files to reduce failure rate.")

    return 0


def _show_recent(flinch_path: Path, count: int) -> int:
    """Show N most recent failures."""
    print(f"[FLINCH] {count} Most Recent Failures")
    print("=" * 40)

    # Parse JSONL directly for recent entries
    flinches: list[dict[str, Any]] = []
    try:
        with open(flinch_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        flinches.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError as e:
        print(f"[ERROR] Failed to read flinch data: {e}")
        return 1

    # Sort by timestamp descending
    flinches.sort(key=lambda x: x.get("ts", 0), reverse=True)

    if not flinches:
        print("No failures recorded")
        return 0

    for flinch_entry in flinches[:count]:
        ts = flinch_entry.get("ts", 0)
        test = flinch_entry.get("test", "unknown")
        phase = flinch_entry.get("phase", "call")
        duration = flinch_entry.get("duration", 0)

        # Format timestamp with validation
        ts_str = "unknown"
        if isinstance(ts, (int, float)) and ts > 0:
            try:
                dt = datetime.fromtimestamp(ts)
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (OSError, ValueError):
                pass  # Invalid timestamp

        # Truncate long test names
        test_str = str(test) if test else "unknown"
        if len(test_str) > 70:
            test_str = "..." + test_str[-67:]

        # Validate duration is numeric
        try:
            duration_val = float(duration) if duration else 0.0
        except (TypeError, ValueError):
            duration_val = 0.0

        print(f"  [{ts_str}] {test_str}")
        print(f"    Phase: {phase}, Duration: {duration_val:.3f}s")
        print()

    return 0


def _show_traces(flinch_path: Path, project_root: Path) -> int:
    """
    Show failures with call trace correlation.

    Correlates test failures with static call graph analysis to identify
    common call paths and potential root causes.
    """
    print("[FLINCH] Test Failure Analysis with Call Traces")
    print("=" * 50)

    # Parse flinch data with error handling
    flinches: list[dict[str, Any]] = []
    try:
        with open(flinch_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        flinches.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError as e:
        print(f"[ERROR] Failed to read flinch data: {e}")
        return 1

    if not flinches:
        print("No failures recorded")
        return 0

    # Group by test (module::class::test_name)
    test_failures: dict[str, list[dict[str, Any]]] = {}
    for flinch in flinches:
        test = flinch.get("test", "unknown")
        if test not in test_failures:
            test_failures[test] = []
        test_failures[test].append(flinch)

    # Sort by failure count descending
    sorted_tests = sorted(test_failures.items(), key=lambda x: -len(x[1]))

    # Try to get trace data
    trace_available = False
    trace_provider = None
    try:
        from agents.i.data.trace_provider import get_trace_provider

        trace_provider = get_trace_provider()
        impl_path = project_root / "impl" / "claude"
        if impl_path.exists():
            trace_provider.set_base_path(str(impl_path))
        trace_available = True
    except ImportError:
        pass

    print()
    for test_name, failures in sorted_tests[:10]:  # Top 10 failing tests
        count = len(failures)
        print(f"{test_name} ({count} failure{'s' if count > 1 else ''})")

        # Get most recent failure
        recent = max(failures, key=lambda x: x.get("ts", 0))
        ts = recent.get("ts", 0)
        if ts:
            dt = datetime.fromtimestamp(ts)
            age_seconds = (datetime.now() - dt).total_seconds()
            if age_seconds < 3600:
                age_str = f"{int(age_seconds / 60)}m ago"
            elif age_seconds < 86400:
                age_str = f"{int(age_seconds / 3600)}h ago"
            else:
                age_str = f"{int(age_seconds / 86400)}d ago"
            print(f"├─ Last failure: {age_str}")
        else:
            print("├─ Last failure: unknown")

        # Extract test file/function for trace lookup
        if "::" in test_name:
            parts = test_name.split("::")
            # Try to find the test function in the call graph
            test_func = parts[-1] if len(parts) > 1 else ""

            if trace_available and trace_provider and test_func:
                # Look up callers of this test (with error handling)
                try:
                    callers = trace_provider.get_callers(test_func, depth=2)
                    if callers and len(callers) > 0:
                        print("├─ Call trace (static):")
                        _print_caller_tree(callers, test_func, "│  ")
                except (AttributeError, TypeError):
                    # Provider API mismatch or type error
                    pass  # Silent fallback - trace is optional
                except Exception:
                    # Unexpected error - continue without trace
                    pass

        # Check for stored traceback in flinch data
        if "traceback" in recent:
            tb = recent["traceback"]
            if isinstance(tb, list):
                print("├─ Call trace at failure:")
                for i, frame in enumerate(tb[-5:]):  # Last 5 frames
                    prefix = "│  └─" if i == len(tb[-5:]) - 1 else "│  ├─"
                    if isinstance(frame, dict):
                        func = frame.get("function", "?")
                        file_name = frame.get("file", "?")
                        line = frame.get("line", "?")
                        print(f"{prefix} {func} ({file_name}:{line})")
                    else:
                        print(f"{prefix} {frame}")

        # Find related failures (same module)
        if "::" in test_name:
            module = test_name.split("::")[0]
            related = [
                t for t in test_failures.keys() if t != test_name and t.startswith(module + "::")
            ]
            if related:
                print(f"└─ Related failures: {len(related)} in same module")
            else:
                print("└─ No related failures in module")
        else:
            print("└─")
        print()

    # Summary with trace stats
    if trace_available:
        print("─" * 50)
        print("[TRACE] Static analysis available for call correlation")
        print("  Use 'kgents trace' for detailed call graph exploration")

    return 0


def _print_caller_tree(graph: Any, target: str, prefix: str = "", depth: int = 0) -> None:
    """
    Print a caller tree from dependency graph.

    Args:
        graph: Dependency graph with get_dependencies method
        target: Target function to trace
        prefix: Line prefix for tree formatting
        depth: Current recursion depth (max 3)
    """
    if depth > 3:
        return

    # Validate inputs
    if graph is None or not target:
        return

    try:
        # Check for get_dependencies method
        get_deps = getattr(graph, "get_dependencies", None)
        if get_deps is None:
            return

        deps = get_deps(target)
        if deps is None:
            return

        deps_list = list(deps)[:5]  # Limit to 5 deps
        for i, dep in enumerate(deps_list):
            if not isinstance(dep, str):
                continue
            is_last = i == len(deps_list) - 1
            connector = "└─" if is_last else "├─"
            print(f"{prefix}{connector} {dep}")
            if depth < 2:
                new_prefix = prefix + ("   " if is_last else "│  ")
                _print_caller_tree(graph, dep, new_prefix, depth + 1)
    except TypeError:
        # deps not iterable
        pass
    except RecursionError:
        # Prevent infinite recursion from circular deps
        pass
    except Exception:
        # Unexpected error - fail silently (trace is optional)
        pass


def _show_turns_panel() -> int:
    """
    Show Turn-gents panel for causal debugging.

    Displays turn history with DAG visualization and statistics.
    This integrates Turn-gents into the test failure workflow.
    """
    from rich.console import Console

    console = Console()

    try:
        from protocols.cli.handlers.turns import _get_global_weave

        from agents.i.screens.turn_dag import TurnDAGConfig, TurnDAGRenderer

        weave = _get_global_weave()

        if len(weave) == 0:
            console.print("[TURNS] No turns recorded yet.")
            console.print()
            console.print(
                "[dim]Turns are recorded when agents are decorated with @Capability.TurnBased.[/]"
            )
            console.print()
            console.print("To enable Turn-gents:")
            console.print("  1. Decorate agents with @Capability.TurnBased")
            console.print("  2. Run agent interactions")
            console.print("  3. Use 'kg turns' or 'kg dag' to inspect")
            return 0

        # Render turn DAG
        config = TurnDAGConfig(show_thoughts=False)
        renderer = TurnDAGRenderer(weave=weave, config=config)

        console.print("[FLINCH] Turn-gents Panel")
        console.print("=" * 50)
        console.print()

        # Show DAG panel
        panel = renderer.render()
        console.print(panel)

        # Show stats
        stats = renderer.render_stats()
        console.print(stats)

        # Show compression info
        console.print()
        console.print("[bold cyan]Context Compression[/]")
        console.print("[dim]Turn-gents projects minimal causal context per agent.[/]")

        # Get agents and show compression ratios
        from weave import CausalCone

        cone = CausalCone(weave)
        agents = set()
        for event in weave.monoid.events:
            agents.add(event.source)

        for agent in sorted(agents)[:5]:  # Top 5 agents
            ratio = cone.compression_ratio(agent)
            cone_size = cone.cone_size(agent)
            console.print(
                f"  {agent}: {ratio:.1%} compression ({cone_size}/{len(weave)} events in cone)"
            )

        console.print()
        console.print("[dim]Use 'kg turns', 'kg dag', or 'kg pending' for more.[/]")

        return 0

    except ImportError as e:
        console.print(f"[TURNS] Module not available: {e}")
        return 1
    except Exception as e:
        console.print(f"[TURNS] Error: {e}")
        return 1
