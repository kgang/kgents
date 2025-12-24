#!/usr/bin/env python3
"""
Demo: Analysis Operad → Witness Mark Integration.

Shows how `kg analyze` automatically emits Witness marks for analysis results.

Usage:
    uv run python scripts/demo_analysis_witness.py
"""

import asyncio
from pathlib import Path


async def demo() -> None:
    """Demonstrate analysis → witness integration."""
    print("=" * 70)
    print("Analysis Operad → Witness Integration Demo")
    print("=" * 70)
    print()

    # Import the handler
    from protocols.cli.handlers.analyze import cmd_analyze

    # Target a small spec for demo
    spec_path = "spec/theory/analysis-operad.md"

    if not Path(spec_path).exists():
        print(f"Error: {spec_path} not found")
        print("This demo requires the analysis-operad spec")
        return

    print(f"Analyzing: {spec_path}")
    print()
    print("This will:")
    print("1. Run full 4-mode analysis (structural)")
    print("2. Emit a Witness mark with results")
    print("3. Show the mark in recent marks")
    print()
    input("Press Enter to continue...")
    print()

    # Run analysis with witness emission (default)
    print("Step 1: Running analysis...")
    print("-" * 70)
    result = await cmd_analyze([spec_path, "--structural"])
    print()

    if result != 0:
        print(f"Analysis completed with issues (exit code: {result})")
    else:
        print("Analysis completed successfully")
    print()

    # Show recent marks
    print("Step 2: Checking recent Witness marks...")
    print("-" * 70)
    from protocols.cli.handlers.witness.marks import _cmd_show_async

    await _cmd_show_async(["--limit", "3", "-v"])
    print()

    print("=" * 70)
    print("Demo complete!")
    print()
    print("The analysis result is now captured in Witness memory.")
    print("You can retrieve it later with:")
    print("  kg witness show --grep 'analysis-operad'")
    print("  kg witness show --tag analysis")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())
