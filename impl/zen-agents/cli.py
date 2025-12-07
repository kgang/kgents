#!/usr/bin/env python
"""CLI entry point for zen-agents.

Usage:
    zen-agents          # Launch TUI
    zen-agents demo     # Run demo
    zen-agents --help   # Show help
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="zen-agents",
        description="Agent-based terminal session management",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["demo", "ui"],
        default="ui",
        help="Command to run (default: ui)",
    )
    parser.add_argument(
        "--section",
        help="Demo section to run (with demo command)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_sections",
        help="List demo sections",
    )

    args = parser.parse_args()

    if args.command == "demo":
        # Import and run demo
        from demo import main as demo_main
        # Re-construct argv for demo
        demo_argv = ["demo.py"]
        if args.list_sections:
            demo_argv.append("--list")
        if args.section:
            demo_argv.extend(["--section", args.section])
        sys.argv = demo_argv
        demo_main()
    else:
        # Launch UI
        from zen_agents.ui import main as ui_main
        ui_main()


if __name__ == "__main__":
    main()
