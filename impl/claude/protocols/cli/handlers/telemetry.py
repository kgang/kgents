"""
Telemetry Handler: OpenTelemetry observability for AGENTESE.

Part of the kgents CLI. Provides commands for managing telemetry
configuration, viewing traces, and checking telemetry status.

Usage:
    kgents telemetry status           # Show telemetry configuration and status
    kgents telemetry traces           # List recent traces (JSON exporter)
    kgents telemetry traces --limit 5 # Limit number of traces shown
    kgents telemetry metrics          # Show metrics summary
    kgents telemetry config           # Generate sample config file
    kgents telemetry enable           # Enable telemetry
    kgents telemetry disable          # Disable telemetry
    kgents telemetry --help           # Show help

Example:
    kgents telemetry status
    [TELEMETRY] OK ENABLED | exporter:json | traces:42 | sampling:100%
"""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for telemetry command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  status        Show telemetry configuration and status")
    print("  traces        List recent traces (for JSON exporter)")
    print("  metrics       Show metrics summary")
    print("  config        Generate sample configuration file")
    print("  enable        Enable telemetry")
    print("  disable       Disable telemetry")
    print()
    print("OPTIONS:")
    print("  --json        Output as JSON")
    print("  --limit N     Limit number of traces (default: 10)")
    print("  --help, -h    Show this help")


def cmd_telemetry(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the telemetry command.

    Args:
        args: Command-line arguments (after the command name)
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("telemetry", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Parse limit
    limit = 10
    for i, arg in enumerate(args):
        if arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass

    # Get subcommand (first non-flag argument)
    subcommand: str | None = None
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg == "--limit":
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        subcommand = arg
        break

    # Default to status if no subcommand
    if subcommand is None:
        subcommand = "status"

    # Dispatch to subcommand handler
    if subcommand == "status":
        return _handle_status(json_mode, ctx)
    elif subcommand == "traces":
        return _handle_traces(limit, json_mode, ctx)
    elif subcommand == "metrics":
        return _handle_metrics(json_mode, ctx)
    elif subcommand == "config":
        return _handle_config(ctx)
    elif subcommand == "enable":
        return _handle_enable(ctx)
    elif subcommand == "disable":
        return _handle_disable(ctx)
    else:
        _emit_output(
            f"[TELEMETRY] Unknown subcommand: {subcommand}",
            {"error": f"Unknown subcommand: {subcommand}"},
            ctx,
        )
        _print_help()
        return 1


def _handle_status(json_mode: bool, ctx: "InvocationContext | None") -> int:
    """Show telemetry configuration and status."""
    try:
        from protocols.agentese.exporters import (
            TelemetryConfig,
            is_telemetry_configured,
        )
        from protocols.agentese.telemetry_config import (
            DEFAULT_CONFIG_PATH,
            DEFAULT_TRACE_PATH,
            load_telemetry_config,
        )

        # Load configuration
        try:
            config = load_telemetry_config()
        except Exception:
            config = TelemetryConfig()

        # Determine exporter type
        if config.otlp_endpoint:
            exporter = "otlp"
            endpoint = config.otlp_endpoint
        elif config.jaeger_host:
            exporter = "jaeger"
            endpoint = f"{config.jaeger_host}:{config.jaeger_port}"
        elif config.local_json_path:
            exporter = "json"
            endpoint = config.local_json_path
        elif config.console_export:
            exporter = "console"
            endpoint = "stdout"
        else:
            exporter = "none"
            endpoint = None

        # Count traces if using JSON exporter
        trace_count = 0
        if config.local_json_path:
            trace_path = Path(config.local_json_path).expanduser()
            if trace_path.exists():
                trace_count = len(list(trace_path.glob("*.json")))

        # Check if configured
        is_configured = is_telemetry_configured()

        # Build result
        result = {
            "configured": is_configured,
            "exporter": exporter,
            "endpoint": endpoint,
            "sampling_rate": config.sampling_rate,
            "trace_count": trace_count,
            "service_name": config.service_name,
            "environment": config.deployment_environment,
            "config_file": str(DEFAULT_CONFIG_PATH),
            "config_exists": DEFAULT_CONFIG_PATH.exists(),
        }

        if json_mode:
            _emit_output(json_module.dumps(result, indent=2), result, ctx)
        else:
            status_icon = "OK" if is_configured else "!"
            status_text = "ENABLED" if is_configured else "NOT CONFIGURED"

            line = f"[TELEMETRY] {status_icon} {status_text}"
            line += f" | exporter:{exporter}"

            if endpoint:
                # Truncate long paths
                display_endpoint = str(endpoint)
                if len(display_endpoint) > 30:
                    display_endpoint = "..." + display_endpoint[-27:]
                line += f" | endpoint:{display_endpoint}"

            if trace_count > 0:
                line += f" | traces:{trace_count}"

            line += f" | sampling:{int(config.sampling_rate * 100)}%"

            _emit_output(line, result, ctx)

            # Show config file status
            if DEFAULT_CONFIG_PATH.exists():
                _emit_output(f"  Config: {DEFAULT_CONFIG_PATH}", {}, ctx)
            else:
                _emit_output(
                    "  Config: Not found (using defaults)",
                    {},
                    ctx,
                )
                _emit_output(
                    "  Run 'kgents telemetry config' to generate a config file",
                    {},
                    ctx,
                )

        return 0

    except ImportError as e:
        _emit_output(
            f"[TELEMETRY] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _handle_traces(
    limit: int,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """List recent traces from JSON exporter."""
    try:
        from protocols.agentese.exporters import TelemetryConfig
        from protocols.agentese.telemetry_config import (
            DEFAULT_TRACE_PATH,
            load_telemetry_config,
        )

        # Load configuration
        try:
            config = load_telemetry_config()
        except Exception:
            config = TelemetryConfig()

        # Get trace path
        if config.local_json_path:
            trace_path = Path(config.local_json_path).expanduser()
        else:
            trace_path = DEFAULT_TRACE_PATH

        if not trace_path.exists():
            _emit_output(
                f"[TELEMETRY] No traces found at {trace_path}",
                {"traces": [], "path": str(trace_path)},
                ctx,
            )
            return 0

        # List trace files (sorted by modification time, newest first)
        trace_files = sorted(
            trace_path.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:limit]

        if not trace_files:
            _emit_output(
                f"[TELEMETRY] No traces found at {trace_path}",
                {"traces": [], "path": str(trace_path)},
                ctx,
            )
            return 0

        # Parse and display traces
        traces = []
        for trace_file in trace_files:
            try:
                data = json_module.loads(trace_file.read_text())
                spans = data.get("spans", [])

                trace_info = {
                    "file": trace_file.name,
                    "trace_id": data.get("trace_id", "unknown")[:16] + "...",
                    "timestamp": data.get("timestamp", "unknown"),
                    "span_count": len(spans),
                    "spans": [],
                }

                # Extract span info
                for span in spans[:5]:  # Show first 5 spans per trace
                    path = span.get("attributes", {}).get("agentese.path", span["name"])
                    status = span.get("status", {}).get("code", "OK")
                    trace_info["spans"].append({"path": path, "status": status})

                traces.append(trace_info)

            except (json_module.JSONDecodeError, KeyError):
                continue

        result = {"traces": traces, "path": str(trace_path), "count": len(traces)}

        if json_mode:
            _emit_output(json_module.dumps(result, indent=2), result, ctx)
        else:
            _emit_output(
                f"[TELEMETRY] Recent traces ({len(traces)} shown):",
                result,
                ctx,
            )
            _emit_output(f"  Path: {trace_path}", {}, ctx)
            _emit_output("", {}, ctx)

            for trace in traces:
                _emit_output(
                    f"  {trace['file']}:",
                    {"trace": trace},
                    ctx,
                )
                _emit_output(
                    f"    Trace: {trace['trace_id']} | Spans: {trace['span_count']}",
                    {},
                    ctx,
                )
                for span in trace["spans"]:
                    status_icon = "OK" if span["status"] == "OK" else "X"
                    _emit_output(
                        f"      {status_icon} {span['path']}",
                        {},
                        ctx,
                    )
                _emit_output("", {}, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[TELEMETRY] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _handle_metrics(json_mode: bool, ctx: "InvocationContext | None") -> int:
    """Show metrics summary."""
    try:
        from protocols.agentese.metrics import get_metrics_summary

        summary = get_metrics_summary()

        if json_mode:
            _emit_output(json_module.dumps(summary, indent=2), summary, ctx)
        else:
            _emit_output("[TELEMETRY] Metrics Summary:", summary, ctx)
            _emit_output("", {}, ctx)

            # Totals
            _emit_output(
                f"  Total invocations: {summary['total_invocations']:,}",
                {},
                ctx,
            )
            _emit_output(
                f"  Total errors: {summary['total_errors']:,} ({summary['error_rate']:.1%})",
                {},
                ctx,
            )
            _emit_output(
                f"  Avg duration: {summary['avg_duration_s'] * 1000:.1f}ms",
                {},
                ctx,
            )

            # Tokens
            _emit_output(
                f"  Tokens in: {summary['total_tokens_in']:,}",
                {},
                ctx,
            )
            _emit_output(
                f"  Tokens out: {summary['total_tokens_out']:,}",
                {},
                ctx,
            )

            # By context
            if summary["invocations_by_context"]:
                _emit_output("\n  By context:", {}, ctx)
                for context, count in sorted(
                    summary["invocations_by_context"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                ):
                    _emit_output(f"    {context}: {count:,}", {}, ctx)

            # Top paths
            if summary["top_paths"]:
                _emit_output("\n  Top paths:", {}, ctx)
                for path, count in list(summary["top_paths"].items())[:5]:
                    # Truncate long paths
                    display_path = path if len(path) <= 40 else "..." + path[-37:]
                    _emit_output(f"    {display_path}: {count:,}", {}, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[TELEMETRY] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _handle_config(ctx: "InvocationContext | None") -> int:
    """Generate sample configuration file."""
    try:
        from protocols.agentese.telemetry_config import (
            DEFAULT_CONFIG_PATH,
            generate_sample_config,
        )

        # Check if config already exists
        if DEFAULT_CONFIG_PATH.exists():
            _emit_output(
                f"[TELEMETRY] Config already exists: {DEFAULT_CONFIG_PATH}",
                {"exists": True, "path": str(DEFAULT_CONFIG_PATH)},
                ctx,
            )
            _emit_output(
                "  Use 'cat' to view or manually edit the file",
                {},
                ctx,
            )
            return 0

        # Generate config
        sample = generate_sample_config(DEFAULT_CONFIG_PATH)

        _emit_output(
            f"[TELEMETRY] Config generated: {DEFAULT_CONFIG_PATH}",
            {"generated": True, "path": str(DEFAULT_CONFIG_PATH)},
            ctx,
        )
        _emit_output("", {}, ctx)
        _emit_output("  Preview:", {}, ctx)
        for line in sample.split("\n")[:15]:
            _emit_output(f"    {line}", {}, ctx)
        _emit_output("    ...", {}, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[TELEMETRY] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _handle_enable(ctx: "InvocationContext | None") -> int:
    """Enable telemetry."""
    try:
        from protocols.agentese.telemetry_config import (
            DEFAULT_CONFIG_PATH,
            setup_telemetry,
        )

        # If no config exists, create one with defaults
        if not DEFAULT_CONFIG_PATH.exists():
            from protocols.agentese.telemetry_config import generate_sample_config

            generate_sample_config(DEFAULT_CONFIG_PATH)
            _emit_output(
                f"[TELEMETRY] Created config: {DEFAULT_CONFIG_PATH}",
                {"created": True},
                ctx,
            )

        # Set up telemetry
        if setup_telemetry(force=True):
            _emit_output(
                "[TELEMETRY] OK Enabled",
                {"enabled": True},
                ctx,
            )
        else:
            _emit_output(
                "[TELEMETRY] Already enabled",
                {"enabled": True, "was_already": True},
                ctx,
            )

        return 0

    except ImportError as e:
        _emit_output(
            f"[TELEMETRY] X Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


def _handle_disable(ctx: "InvocationContext | None") -> int:
    """Disable telemetry."""
    try:
        import os

        os.environ["KGENTS_TELEMETRY_ENABLED"] = "false"

        _emit_output(
            "[TELEMETRY] Disabled (set KGENTS_TELEMETRY_ENABLED=false)",
            {"disabled": True},
            ctx,
        )
        _emit_output(
            "  Note: This only affects the current process.",
            {},
            ctx,
        )
        _emit_output(
            "  To disable permanently, set 'enabled: false' in ~/.kgents/telemetry.yaml",
            {},
            ctx,
        )

        return 0

    except Exception as e:
        _emit_output(
            f"[TELEMETRY] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


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
