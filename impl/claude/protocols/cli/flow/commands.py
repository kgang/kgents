"""
Flow CLI Commands - Command handlers for flow operations.

Commands:
- flow run <file> [input] - Execute flowfile
- flow validate <file> - Validate flowfile syntax and references
- flow explain <file> - Show human-readable explanation
- flow visualize <file> - ASCII graph visualization
- flow new "<intent>" - Generate flowfile from natural language
- flow from-history <id> - Extract flow from session history
- flow list - List saved flows
- flow save <file> --name=<id> - Save to registry

From docs/cli-integration-plan.md Part 4.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path


# =============================================================================
# Output Formatting
# =============================================================================


def format_flow_result_rich(result: dict) -> str:
    """Format FlowResult for rich terminal output."""
    lines = []

    # Status header
    status = result.get("status", "unknown")
    status_color = {
        "completed": "\033[92m",  # Green
        "failed": "\033[91m",  # Red
        "running": "\033[93m",  # Yellow
        "pending": "\033[90m",  # Gray
    }.get(status, "")
    reset = "\033[0m"

    lines.append("┌" + "─" * 60 + "┐")
    lines.append(f"│ Flow: {result.get('flow_name', '(unnamed)'):<52} │")
    lines.append(f"│ Status: {status_color}{status.upper():<50}{reset} │")
    lines.append("├" + "─" * 60 + "┤")

    # Step results
    step_results = result.get("step_results", [])
    if step_results:
        lines.append("│ Steps:                                                     │")
        for step in step_results:
            step_id = step.get("step_id", "?")
            step_status = step.get("status", "?")

            # Status indicator
            indicator = {
                "completed": "✓",
                "failed": "✗",
                "skipped": "○",
                "running": "◐",
                "pending": "·",
            }.get(step_status, "?")

            # Duration
            duration_ms = step.get("duration_ms")
            duration_str = f"{duration_ms:.0f}ms" if duration_ms else ""

            line = f"│   {indicator} [{step_id}] {step_status:<12} {duration_str:>10}"
            lines.append(f"{line:<61}│")

            # Error info
            if step.get("error"):
                error_line = f"│     → {step['error'][:50]}"
                lines.append(f"{error_line:<61}│")

    # Summary
    lines.append("├" + "─" * 60 + "┤")
    completed = result.get("completed_steps", 0)
    total = result.get("total_steps", 0)
    duration_ms = result.get("duration_ms")
    duration_str = f"{duration_ms:.0f}ms" if duration_ms else "?"

    lines.append(f"│ Completed: {completed}/{total} steps in {duration_str:<30}│")

    # Error message if failed
    if result.get("error"):
        lines.append("├" + "─" * 60 + "┤")
        lines.append(f"│ Error: {result['error'][:51]:<52} │")
        if result.get("failed_step"):
            lines.append(f"│ Failed at: [{result['failed_step']}]{'':>47}│")

    lines.append("└" + "─" * 60 + "┘")

    return "\n".join(lines)


def format_validation_result_rich(errors: list[str], path: str) -> str:
    """Format validation result for terminal output."""
    lines = []

    if not errors:
        lines.append("┌" + "─" * 60 + "┐")
        lines.append(f"│ ✓ Flowfile is valid: {path:<36} │")
        lines.append("└" + "─" * 60 + "┘")
    else:
        lines.append("┌" + "─" * 60 + "┐")
        lines.append(f"│ ✗ Validation failed: {path:<36} │")
        lines.append("├" + "─" * 60 + "┤")
        for i, error in enumerate(errors, 1):
            lines.append(f"│   {i}. {error[:54]:<54} │")
        lines.append("└" + "─" * 60 + "┘")

    return "\n".join(lines)


# =============================================================================
# Command Handlers
# =============================================================================


async def cmd_flow_run(args: list[str]) -> int:
    """Execute a flowfile."""
    from .parser import parse_flowfile
    from .engine import FlowEngine

    if not args:
        print("Usage: kgents flow run <flowfile> [input] [--var key=value ...]")
        return 1

    # Parse arguments
    flowfile_path = args[0]
    input_data = args[1] if len(args) > 1 and not args[1].startswith("--") else None
    variables: dict[str, str] = {}

    for arg in args[1:]:
        if arg.startswith("--var"):
            if "=" in arg:
                # --var=key=value
                rest = arg.split("=", 1)[1]
                if "=" in rest:
                    key, value = rest.split("=", 1)
                    variables[key] = value
        elif "=" in arg and not arg.startswith("--"):
            # key=value (positional after input)
            key, value = arg.split("=", 1)
            variables[key] = value

    # Check output format
    output_format = "rich"
    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg == "--json":
            output_format = "json"

    # Parse flowfile
    try:
        flowfile = parse_flowfile(flowfile_path)
    except Exception as e:
        print(f"Error parsing flowfile: {e}")
        return 1

    # Progress callback
    def progress(step_id: str, status: str) -> None:
        if output_format == "rich":
            indicator = {
                "running": "◐",
                "completed": "✓",
                "failed": "✗",
                "skipped": "○",
            }.get(status, "?")
            print(f"  {indicator} [{step_id}] {status}")

    # Execute
    engine = FlowEngine(progress_callback=progress)

    if output_format == "rich":
        print(f"Running flow: {flowfile.name or flowfile_path}")
        print()

    try:
        result = await engine.execute(flowfile, input_data, variables)
    except Exception as e:
        print(f"Error executing flow: {e}")
        return 1

    # Output result
    if output_format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print()
        print(format_flow_result_rich(result.to_dict()))

    return 0 if result.status.value == "completed" else 1


async def cmd_flow_validate(args: list[str]) -> int:
    """Validate a flowfile."""
    from .parser import parse_flowfile, validate_flowfile

    if not args:
        print("Usage: kgents flow validate <flowfile>")
        return 1

    flowfile_path = args[0]

    # Check output format
    output_format = "rich"
    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg == "--json":
            output_format = "json"

    # Parse flowfile
    try:
        flowfile = parse_flowfile(flowfile_path)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"valid": False, "errors": [str(e)]}))
        else:
            print(f"Error parsing flowfile: {e}")
        return 1

    # Validate
    errors = validate_flowfile(flowfile)

    if output_format == "json":
        print(
            json.dumps(
                {
                    "valid": len(errors) == 0,
                    "errors": errors,
                    "flow_name": flowfile.name,
                    "steps": len(flowfile.steps),
                }
            )
        )
    else:
        print(format_validation_result_rich(errors, flowfile_path))

    return 0 if not errors else 1


async def cmd_flow_explain(args: list[str]) -> int:
    """Explain a flowfile in human-readable form."""
    from .parser import parse_flowfile, explain_flow

    if not args:
        print("Usage: kgents flow explain <flowfile>")
        return 1

    flowfile_path = args[0]

    try:
        flowfile = parse_flowfile(flowfile_path)
    except Exception as e:
        print(f"Error parsing flowfile: {e}")
        return 1

    print(explain_flow(flowfile))
    return 0


async def cmd_flow_visualize(args: list[str]) -> int:
    """Visualize a flowfile as ASCII graph."""
    from .parser import parse_flowfile, visualize_flow

    if not args:
        print("Usage: kgents flow visualize <flowfile>")
        return 1

    flowfile_path = args[0]

    try:
        flowfile = parse_flowfile(flowfile_path)
    except Exception as e:
        print(f"Error parsing flowfile: {e}")
        return 1

    print(f"Flow: {flowfile.name or flowfile_path}")
    print()
    print(visualize_flow(flowfile))
    return 0


async def cmd_flow_new(args: list[str]) -> int:
    """Generate a flowfile from natural language intent."""
    if not args:
        print('Usage: kgents flow new "<intent>" [--output=<path>]')
        return 1

    intent = args[0]
    output_path = None

    for arg in args[1:]:
        if arg.startswith("--output="):
            output_path = arg.split("=", 1)[1]

    # Simple intent parsing (placeholder for J-gent integration)
    # Real implementation would use J-gent to classify intent

    steps = []
    name = "Generated Flow"

    # Parse common patterns
    intent_lower = intent.lower()

    if "parse" in intent_lower or "extract" in intent_lower:
        steps.append(
            {
                "id": "parse",
                "genus": "P-gent",
                "operation": "extract",
            }
        )
        name = "Parse Flow"

    if "judge" in intent_lower or "check" in intent_lower or "verify" in intent_lower:
        steps.append(
            {
                "id": "judge",
                "genus": "Bootstrap",
                "operation": "judge",
                "input": "from:parse" if steps else None,
                "args": {"principles": "spec/principles.md"},
            }
        )
        if "Parse" not in name:
            name = "Verification Flow"
        else:
            name = "Parse & Judge Flow"

    if "refine" in intent_lower or "fix" in intent_lower or "optimize" in intent_lower:
        steps.append(
            {
                "id": "refine",
                "genus": "R-gent",
                "operation": "optimize",
                "input": f"from:{steps[-1]['id']}" if steps else None,
                "condition": "judge.verdict != 'APPROVED'"
                if any(s["id"] == "judge" for s in steps)
                else None,
            }
        )
        name = name.replace(" Flow", "") + " & Refine Flow"

    if "watch" in intent_lower or "observe" in intent_lower:
        steps.append(
            {
                "id": "watch",
                "genus": "W-gent",
                "operation": "watch",
            }
        )
        name = "Watch Flow"

    if "test" in intent_lower or "fuzz" in intent_lower:
        steps.append(
            {
                "id": "test",
                "genus": "T-gent",
                "operation": "fuzz" if "fuzz" in intent_lower else "verify",
            }
        )
        name = "Test Flow"

    # Default step if no patterns matched
    if not steps:
        steps.append(
            {
                "id": "process",
                "genus": "J-gent",
                "operation": "compile",
                "args": {"intent": intent},
            }
        )
        name = "Intent Flow"

    # Build flowfile
    flowfile = {
        "version": "1.0",
        "name": name,
        "description": f"Generated from: {intent}",
        "input": {"type": "any"},
        "steps": steps,
        "on_error": {"strategy": "halt"},
    }

    # Output
    try:
        import yaml

        yaml_content = yaml.dump(flowfile, default_flow_style=False, sort_keys=False)
    except ImportError:
        yaml_content = json.dumps(flowfile, indent=2)

    if output_path:
        Path(output_path).write_text(yaml_content)
        print(f"Generated flowfile: {output_path}")
    else:
        print(yaml_content)

    return 0


async def cmd_flow_list(args: list[str]) -> int:
    """List saved flows in the registry."""
    # Look for .kgents/flows/ directory
    flows_dir = Path(".kgents/flows")

    if not flows_dir.exists():
        print("No saved flows found.")
        print('  Create a flow: kgents flow new "parse then judge"')
        print("  Save a flow:   kgents flow save review.yaml --name=review")
        return 0

    # List flows
    flows = list(flows_dir.glob("*.yaml")) + list(flows_dir.glob("*.yml"))

    if not flows:
        print("No saved flows found.")
        return 0

    print("Saved flows:")
    for flow_path in sorted(flows):
        name = flow_path.stem
        # Try to read description
        try:
            from .parser import parse_flowfile

            flowfile = parse_flowfile(flow_path)
            desc = flowfile.description or "(no description)"
            steps = len(flowfile.steps)
            print(f"  {name:<20} {steps} steps  {desc[:40]}")
        except Exception:
            print(f"  {name:<20} (error reading)")

    return 0


async def cmd_flow_save(args: list[str]) -> int:
    """Save a flowfile to the registry."""
    if not args:
        print("Usage: kgents flow save <flowfile> --name=<id>")
        return 1

    flowfile_path = args[0]
    name = None

    for arg in args[1:]:
        if arg.startswith("--name="):
            name = arg.split("=", 1)[1]

    if not name:
        # Use filename as name
        name = Path(flowfile_path).stem

    # Validate flowfile first
    try:
        from .parser import parse_flowfile, validate_flowfile

        flowfile = parse_flowfile(flowfile_path)
        errors = validate_flowfile(flowfile)
        if errors:
            print(f"Cannot save invalid flowfile: {errors[0]}")
            return 1
    except Exception as e:
        print(f"Error parsing flowfile: {e}")
        return 1

    # Create flows directory
    flows_dir = Path(".kgents/flows")
    flows_dir.mkdir(parents=True, exist_ok=True)

    # Copy flowfile
    dest_path = flows_dir / f"{name}.yaml"
    content = Path(flowfile_path).read_text()
    dest_path.write_text(content)

    print(f"Saved flow as: {name}")
    print(f"  Run with: kgents flow run .kgents/flows/{name}.yaml")

    return 0


# =============================================================================
# Main Command Handler
# =============================================================================


def cmd_flow(args: list[str]) -> int:
    """
    Main flow command handler.

    Dispatches to subcommands:
    - run, validate, explain, visualize, new, list, save
    """
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents flow - Flowfile engine for agent composition

USAGE:
  kgents flow <subcommand> [args...]

SUBCOMMANDS:
  run <file> [input]     Execute a flowfile
  validate <file>        Validate flowfile syntax
  explain <file>         Show human-readable explanation
  visualize <file>       ASCII graph visualization
  new "<intent>"         Generate flowfile from intent
  list                   List saved flows
  save <file> --name=ID  Save flowfile to registry

OPTIONS:
  --format=json          Output in JSON format
  --var key=value        Set variable value

EXAMPLES:
  kgents flow run review.yaml src/main.py
  kgents flow validate review.yaml
  kgents flow new "parse then judge"
  kgents flow explain review.yaml

For more: docs/cli-integration-plan.md
""")
        return 0

    subcommand = args[0]
    subargs = args[1:]

    handlers = {
        "run": cmd_flow_run,
        "validate": cmd_flow_validate,
        "explain": cmd_flow_explain,
        "visualize": cmd_flow_visualize,
        "new": cmd_flow_new,
        "list": cmd_flow_list,
        "save": cmd_flow_save,
    }

    handler = handlers.get(subcommand)
    if handler is None:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents flow --help' for available subcommands.")
        return 1

    return asyncio.run(handler(subargs))
