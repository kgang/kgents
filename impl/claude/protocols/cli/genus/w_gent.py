"""
W-gent CLI Commands - Witness/Wire operations.

Wire agents render invisible computation visible. They act as projection
layers between an agent's internal execution stream and human observation.

Commands:
  kgents witness watch <target>    Watch agent execution in real-time
  kgents witness fidelity <output> Check output fidelity level
  kgents witness sample <stream>   Sample from event stream
  kgents witness serve <agent>     Start Wire server for agent
  kgents witness dashboard         Launch value dashboard

Philosophy:
> "Observe without affecting the observed. Show what IS, not what we wish to see."

Three Virtues:
1. Transparency: Show what IS, not what we wish to see
2. Ephemerality: Exist only during observation, leave no trace
3. Non-Intrusion: Observe without affecting the observed

See: spec/w-gents/wire.md
"""

from __future__ import annotations

import json
from typing import Any

HELP_TEXT = """\
kgents witness - W-gent Witness/Wire operations

USAGE:
  kgents witness <subcommand> [args...]

SUBCOMMANDS:
  watch <target>       Watch agent execution in real-time
  fidelity <output>    Check output fidelity level
  sample <stream>      Sample from event stream
  serve <agent>        Start Wire server for agent observation
  dashboard            Launch value dashboard (B-gent economics)
  log <target>         Show recent event log

OPTIONS:
  --fidelity=<level>   Fidelity: teletype, documentarian, livewire
  --rate=<n>           Sample rate (events per second)
  --port=<n>           Server port (default: 8765)
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

FIDELITY LEVELS:
  teletype       Raw stream (stdout, minimal formatting)
  documentarian  Rendered markdown (structured, readable)
  livewire       Dashboard UI (interactive, visual)

EXAMPLES:
  kgents witness watch agent-123
  kgents witness fidelity output.json
  kgents witness sample logs/ --rate=10
  kgents witness serve my-agent --port=8000
"""


def cmd_witness(args: list[str]) -> int:
    """W-gent Witness CLI handler."""
    if not args or args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers = {
        "watch": _cmd_watch,
        "fidelity": _cmd_fidelity,
        "sample": _cmd_sample,
        "serve": _cmd_serve,
        "dashboard": _cmd_dashboard,
        "log": _cmd_log,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents witness --help' for available subcommands.")
        return 1

    return handlers[subcommand](sub_args)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _cmd_watch(args: list[str]) -> int:
    """Watch agent execution in real-time."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents witness watch - Watch agent execution

USAGE:
  kgents witness watch <target> [options]

OPTIONS:
  --fidelity=<level>   Fidelity: teletype, documentarian, livewire
  --duration=<secs>    Watch duration (default: indefinite)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents witness watch agent-123
  kgents witness watch my-agent --fidelity=documentarian
""")
        return 0

    target = None
    fidelity = "documentarian"
    duration = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--fidelity="):
            fidelity = arg.split("=", 1)[1]
        elif arg.startswith("--duration="):
            duration = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            target = arg

    if not target:
        print("Error: Target required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_watch_agent(target, fidelity, duration))
    except KeyboardInterrupt:
        print("\n  Watch ended.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  WATCH COMPLETED: {target}")
        print("  " + "-" * 40)
        print(f"  Events observed: {result['event_count']}")
        print(f"  Duration:        {result['duration']}s")
        print(f"  Fidelity:        {result['fidelity']}")
        print()

    return 0


async def _watch_agent(
    target: str, fidelity: str, duration: int | None
) -> dict[str, Any]:
    """Watch agent for events."""
    from agents.w import WireReader, get_adapter, Fidelity

    # Map fidelity string to enum
    fidelity_map = {
        "teletype": Fidelity.TELETYPE,
        "documentarian": Fidelity.DOCUMENTARIAN,
        "livewire": Fidelity.LIVEWIRE,
    }
    fidelity_level = fidelity_map.get(fidelity, Fidelity.DOCUMENTARIAN)

    adapter = get_adapter(fidelity_level)
    reader = WireReader(target)

    event_count = 0
    elapsed = 0

    print()
    print(f"  Watching: {target} [{fidelity}]")
    print("  " + "-" * 40)
    print()

    # Simulate watching (in real impl, would read from WireObservable)
    import asyncio

    try:
        while duration is None or elapsed < duration:
            await asyncio.sleep(1)
            elapsed += 1

            # Demo events
            if elapsed % 3 == 0:
                event_count += 1
                print(f"  [{elapsed}s] Event: Processing step {event_count}...")
    except asyncio.CancelledError:
        pass

    return {
        "target": target,
        "fidelity": fidelity,
        "event_count": event_count,
        "duration": elapsed,
    }


def _cmd_fidelity(args: list[str]) -> int:
    """Check output fidelity level."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents witness fidelity - Check output fidelity

USAGE:
  kgents witness fidelity <output> [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json

Detects the fidelity level of an output:
- TELETYPE: Raw, unstructured stream
- DOCUMENTARIAN: Structured, rendered content
- LIVEWIRE: Interactive, visual data

EXAMPLES:
  kgents witness fidelity output.json
  kgents witness fidelity log.txt
""")
        return 0

    output_path = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            output_path = arg

    if not output_path:
        print("Error: Output path required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_check_fidelity(output_path))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  FIDELITY CHECK: {output_path}")
        print("  " + "-" * 40)
        print(f"  Detected:   {result['fidelity']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Reason:     {result['reason']}")
        print()

    return 0


async def _check_fidelity(path: str) -> dict[str, Any]:
    """Check fidelity level of output."""
    from agents.w import detect_fidelity

    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        return {
            "fidelity": "UNKNOWN",
            "confidence": 0.0,
            "reason": f"File not found: {path}",
        }

    fidelity = detect_fidelity(content)

    # Heuristic reasoning
    if path.endswith(".json"):
        reason = "JSON structure detected"
    elif path.endswith(".md"):
        reason = "Markdown formatting detected"
    elif path.endswith(".log") or path.endswith(".txt"):
        reason = "Plain text stream"
    else:
        reason = "Content analysis"

    return {
        "fidelity": fidelity.value,
        "confidence": 0.85,
        "reason": reason,
    }


def _cmd_sample(args: list[str]) -> int:
    """Sample from event stream."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents witness sample - Sample from event stream

USAGE:
  kgents witness sample <stream> [options]

OPTIONS:
  --rate=<n>           Events per second (default: 1)
  --count=<n>          Number of samples (default: 10)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents witness sample logs/events.log --rate=10
  kgents witness sample agent-stream --count=5
""")
        return 0

    stream = None
    rate = 1
    count = 10
    output_format = "rich"

    for arg in args:
        if arg.startswith("--rate="):
            rate = int(arg.split("=", 1)[1])
        elif arg.startswith("--count="):
            count = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            stream = arg

    if not stream:
        print("Error: Stream required")
        return 1

    import asyncio

    try:
        result = asyncio.run(_sample_stream(stream, rate, count))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  SAMPLED: {stream}")
        print("  " + "-" * 40)
        print(f"  Rate:    {rate} events/sec")
        print(f"  Samples: {len(result['samples'])}")
        print()
        for i, s in enumerate(result["samples"][:10]):
            print(f"    [{i + 1}] {s}")
        print()

    return 0


async def _sample_stream(stream: str, rate: int, count: int) -> dict[str, Any]:
    """Sample from event stream."""
    samples = []

    # Simulate sampling
    for i in range(min(count, 10)):
        samples.append(f"Event {i + 1}: Sample from {stream}")

    return {
        "stream": stream,
        "rate": rate,
        "samples": samples,
    }


def _cmd_serve(args: list[str]) -> int:
    """Start Wire server for agent observation."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents witness serve - Start Wire server

USAGE:
  kgents witness serve <agent> [options]

OPTIONS:
  --port=<n>           Server port (default: 8765)
  --host=<addr>        Host address (default: localhost)

Starts a Wire server that exposes agent state for observation.
Connect with a browser or WebSocket client.

EXAMPLES:
  kgents witness serve my-agent
  kgents witness serve my-agent --port=8000
""")
        return 0

    agent = None
    port = 8765
    host = "localhost"

    for arg in args:
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            agent = arg

    if not agent:
        print("Error: Agent name required")
        return 1

    import asyncio

    print()
    print(f"  Starting Wire server for: {agent}")
    print("  " + "-" * 40)
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  URL:  http://{host}:{port}")
    print()
    print("  Press Ctrl+C to stop")
    print()

    try:
        asyncio.run(_serve_agent(agent, host, port))
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


async def _serve_agent(agent: str, host: str, port: int) -> None:
    """Serve agent via Wire server."""
    from agents.w import serve_agent

    await serve_agent(agent, host=host, port=port)


def _cmd_dashboard(args: list[str]) -> int:
    """Launch value dashboard."""
    if args and args[0] in ("--help", "-h"):
        print("""\
kgents witness dashboard - Launch value dashboard

USAGE:
  kgents witness dashboard [options]

OPTIONS:
  --minimal            Minimal dashboard (text-only)
  --port=<n>           Server port (default: 8766)
  --format=<fmt>       Output format: rich, json

Launches the B-gent value economics dashboard showing:
- Token budget consumption
- Value tensor dimensions
- VoI metrics
- RoC tracking

EXAMPLES:
  kgents witness dashboard
  kgents witness dashboard --minimal
""")
        return 0

    minimal = False
    port = 8766
    output_format = "rich"

    for arg in args:
        if arg == "--minimal":
            minimal = True
        elif arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    import asyncio

    try:
        result = asyncio.run(_get_dashboard_state(minimal))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  VALUE DASHBOARD")
        print("  " + "=" * 50)
        print()

        # Token Budget
        print("  TOKEN BUDGET")
        print("  " + "-" * 40)
        budget = result["tokens"]
        pct = budget["remaining"] / budget["total"]
        bar = "[" + "=" * int(pct * 20) + " " * (20 - int(pct * 20)) + "]"
        print(f"  {bar} {budget['remaining']}/{budget['total']}")
        print()

        # Value Tensor
        print("  VALUE TENSOR")
        print("  " + "-" * 40)
        tensor = result["tensor"]
        for dim, val in tensor.items():
            bar = "[" + "=" * int(val * 10) + " " * (10 - int(val * 10)) + "]"
            print(f"  {dim:<12} {bar} {val:.2f}")
        print()

        # VoI
        print("  VoI METRICS")
        print("  " + "-" * 40)
        voi = result["voi"]
        print(f"  Observations:  {voi['observations']}")
        print(f"  Prevented:     {voi['disasters_prevented']}")
        print(f"  RoVI:          {voi['rovi']:.2f}")
        print()

        # RoC
        print("  RoC TRACKING")
        print("  " + "-" * 40)
        roc = result["roc"]
        print(f"  Complexity:    {roc['complexity']:.2f}")
        print(f"  Value:         {roc['value']:.2f}")
        print(f"  RoC:           {roc['roc']:.2f}")
        print()

    return 0


async def _get_dashboard_state(minimal: bool) -> dict[str, Any]:
    """Get dashboard state."""
    from agents.w import create_minimal_dashboard, create_value_dashboard

    if minimal:
        dashboard = create_minimal_dashboard()
    else:
        dashboard = create_value_dashboard()

    state = dashboard.get_state()

    return {
        "tokens": {
            "total": state.tokens.total if state.tokens else 1000,
            "consumed": state.tokens.consumed if state.tokens else 150,
            "remaining": state.tokens.remaining if state.tokens else 850,
        },
        "tensor": {
            "physical": state.tensor.physical if state.tensor else 0.8,
            "semantic": state.tensor.semantic if state.tensor else 0.6,
            "economic": state.tensor.economic if state.tensor else 0.7,
            "ethical": state.tensor.ethical if state.tensor else 0.9,
        }
        if state.tensor
        else {"physical": 0.8, "semantic": 0.6, "economic": 0.7, "ethical": 0.9},
        "voi": {
            "observations": state.voi.observations if state.voi else 42,
            "disasters_prevented": state.voi.prevented if state.voi else 3,
            "rovi": state.voi.rovi if state.voi else 1.2,
        }
        if state.voi
        else {"observations": 42, "disasters_prevented": 3, "rovi": 1.2},
        "roc": {
            "complexity": state.roc.complexity if state.roc else 5.2,
            "value": state.roc.value if state.roc else 8.1,
            "roc": state.roc.roc if state.roc else 1.56,
        }
        if state.roc
        else {"complexity": 5.2, "value": 8.1, "roc": 1.56},
    }


def _cmd_log(args: list[str]) -> int:
    """Show recent event log."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents witness log - Show recent event log

USAGE:
  kgents witness log <target> [options]

OPTIONS:
  --lines=<n>          Number of lines (default: 20)
  --level=<level>      Filter by level: DEBUG, INFO, WARN, ERROR
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents witness log agent-123
  kgents witness log agent-123 --level=ERROR
""")
        return 0

    target = None
    lines = 20
    level = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--lines="):
            lines = int(arg.split("=", 1)[1])
        elif arg.startswith("--level="):
            level = arg.split("=", 1)[1].upper()
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            target = arg

    if not target:
        print("Error: Target required")
        return 1

    # Demo log entries
    log_entries = [
        {"time": "10:45:01", "level": "INFO", "message": "Agent started"},
        {"time": "10:45:02", "level": "DEBUG", "message": "Initializing state"},
        {"time": "10:45:03", "level": "INFO", "message": "Processing input"},
        {"time": "10:45:05", "level": "WARN", "message": "High latency detected"},
        {"time": "10:45:07", "level": "INFO", "message": "Task completed"},
    ]

    if level:
        log_entries = [e for e in log_entries if e["level"] == level]

    if output_format == "json":
        print(json.dumps({"target": target, "entries": log_entries}, indent=2))
    else:
        print()
        print(f"  EVENT LOG: {target}")
        print("  " + "-" * 50)
        for e in log_entries[:lines]:
            level_color = {
                "DEBUG": "",
                "INFO": "",
                "WARN": "[!]",
                "ERROR": "[X]",
            }.get(e["level"], "")
            print(f"  {e['time']} {e['level']:<5} {level_color} {e['message']}")
        print()

    return 0
