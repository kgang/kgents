"""
Composition Example

Demonstrates f >> g composition pattern.
"""

import asyncio

from protocols.ashc import L0Program


async def main() -> None:
    """Run composition example."""
    program = L0Program("compose_example")

    # Define functions
    def add_one(n: int) -> int:
        return n + 1

    def double(n: int) -> int:
        return n * 2

    def square(n: int) -> int:
        return n**2

    # Chain: 5 -> +1 -> *2 -> ^2
    # (5 + 1) * 2 = 12, 12^2 = 144
    x = program.define("x", program.literal(5))
    y = program.define("y", program.call(add_one, n=x))
    z = program.define("z", program.call(double, n=y))
    result_val = program.define("result", program.call(square, n=z))

    # Emit result
    program.emit("RESULT", result_val)

    # Witness the transformation chain
    program.witness("add_then_double", x, z)
    program.witness("full_pipeline", x, result_val)

    # Run
    result = await program.run()

    # Print results
    print(f"Program: {result.program_name}")
    print(f"Input: {result.bindings['x']}")
    print(f"After +1: {result.bindings['y']}")
    print(f"After *2: {result.bindings['z']}")
    print(f"Final (^2): {result.bindings['result']}")
    print(f"Artifacts: {len(result.artifacts)}")
    print(f"Witnesses: {len(result.witnesses)}")


if __name__ == "__main__":
    asyncio.run(main())
