"""
Exec Handler: Q-gent disposable code execution.

Execute code in ephemeral containers via Q-gent (Quartermaster).

Usage:
    kgents exec --code "print('hello')"    # Python code
    kgents exec --code "echo world" --lang shell  # Shell script
    kgents exec --file script.py           # Execute file
    kgents exec --dry-run --code "..."     # Show job spec without executing

Options:
    --code CODE      Code to execute (required unless --file)
    --file PATH      File to execute (reads and executes content)
    --lang LANG      Language: python (default) or shell
    --timeout SEC    Execution timeout (default: 30)
    --cpu LIMIT      CPU limit (default: 100m)
    --memory LIMIT   Memory limit (default: 128Mi)
    --network        Allow network access (disabled by default)
    --dry-run        Show job spec without executing

Example:
    $ kgents exec --code "print('Hello from K-Terrarium!')"
    Provisioning job in SUBPROCESS mode...
    Hello from K-Terrarium!

    $ kgents exec --code "import sys; print(sys.version)"
    3.12.0 (main, Oct  2 2023, 12:00:00) [Clang 15.0.0]

    $ kgents exec --file my_script.py --timeout 60
    [script output]
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any


def cmd_exec(args: list[str]) -> int:
    """Execute code in ephemeral container via Q-gent."""
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    # Parse args manually (avoiding argparse for hollow shell pattern)
    options = _parse_args(args)

    if options.get("error"):
        print(f"Error: {options['error']}")
        return 1

    code = options.get("code")
    file_path = options.get("file")

    # Get code from file if specified
    if file_path:
        try:
            code = Path(file_path).read_text()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    elif not code:
        print("Error: Either --code or --file is required")
        return 1

    # Run async
    return asyncio.run(_run_exec(code, options))


async def _run_exec(code: str, options: dict[str, Any]) -> int:
    """Run execution via Q-gent."""
    # Import here for lazy loading
    try:
        from agents.q import ExecutionRequest, create_quartermaster
    except ImportError as e:
        print(f"Q-gent not available: {e}")
        print("Make sure agents.q is properly installed")
        return 1

    def on_progress(msg: str) -> None:
        print(msg)

    # Create Q-gent
    q = create_quartermaster(
        fallback=True,  # Allow subprocess fallback
        dry_run=options.get("dry_run", False),
        on_progress=on_progress,
    )

    # Build request
    request = ExecutionRequest(
        code=code,
        language=options.get("lang", "python"),
        timeout_seconds=options.get("timeout", 30),
        cpu_limit=options.get("cpu", "100m"),
        memory_limit=options.get("memory", "128Mi"),
        network_access=options.get("network", False),
    )

    # Execute
    result = await q.provision_job(request)

    if result.output:
        print(result.output, end="" if result.output.endswith("\n") else "\n")

    if result.error:
        print(f"Error: {result.error}", file=sys.stderr)

    return 0 if result.success else 1


def _parse_args(args: list[str]) -> dict[str, Any]:
    """Parse command line arguments manually."""
    options: dict[str, Any] = {}
    i = 0

    while i < len(args):
        arg = args[i]

        if arg == "--code":
            if i + 1 >= len(args):
                options["error"] = "--code requires a value"
                return options
            options["code"] = args[i + 1]
            i += 2
        elif arg == "--file":
            if i + 1 >= len(args):
                options["error"] = "--file requires a value"
                return options
            options["file"] = args[i + 1]
            i += 2
        elif arg == "--lang":
            if i + 1 >= len(args):
                options["error"] = "--lang requires a value"
                return options
            options["lang"] = args[i + 1]
            i += 2
        elif arg == "--timeout":
            if i + 1 >= len(args):
                options["error"] = "--timeout requires a value"
                return options
            try:
                options["timeout"] = int(args[i + 1])
            except ValueError:
                options["error"] = f"Invalid timeout: {args[i + 1]}"
                return options
            i += 2
        elif arg == "--cpu":
            if i + 1 >= len(args):
                options["error"] = "--cpu requires a value"
                return options
            options["cpu"] = args[i + 1]
            i += 2
        elif arg == "--memory":
            if i + 1 >= len(args):
                options["error"] = "--memory requires a value"
                return options
            options["memory"] = args[i + 1]
            i += 2
        elif arg == "--network":
            options["network"] = True
            i += 1
        elif arg == "--dry-run":
            options["dry_run"] = True
            i += 1
        else:
            # Treat as code if no flag (convenience)
            if "code" not in options:
                options["code"] = arg
            i += 1

    return options
