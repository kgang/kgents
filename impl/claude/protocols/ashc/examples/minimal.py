"""
Minimal L0 Example

Demonstrates the simplest possible L0 program:
define x = 42; emit JSON x
"""

import asyncio

from protocols.ashc import L0Program


async def main() -> None:
    """Run minimal L0 program."""
    # Create program
    program = L0Program("minimal")

    # Define a value
    x = program.define("x", program.literal(42))

    # Emit it as JSON artifact
    program.emit("JSON", x)

    # Run
    result = await program.run()

    # Print results
    print(f"Program: {result.program_name}")
    print(f"Bindings: {result.bindings}")
    print(f"Artifacts: {result.artifacts}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")


if __name__ == "__main__":
    asyncio.run(main())
