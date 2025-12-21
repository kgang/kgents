"""
Bootstrap Example

Demonstrates using L0 with bootstrap stubs to compile from spec.
This is how L0 runs before AGENTESE Logos exists.
"""

import asyncio

from protocols.ashc import (
    L0Program,
    ground_manifest_stub,
    judge_spec_stub,
)


async def main() -> None:
    """Run bootstrap example."""
    program = L0Program("bootstrap_ground_judge")

    # Step 1: Get ground manifest (persona seed)
    ground = program.define(
        "ground",
        program.call(ground_manifest_stub),
    )

    # Step 2: Judge the ground (pass-through in bootstrap)
    judged = program.define(
        "judged",
        program.call(judge_spec_stub, spec=ground),
    )

    # Emit IR
    program.emit("IR", judged)

    # Witness the ground -> judge transformation
    program.witness("ground_to_judge", ground, judged)

    # Run
    result = await program.run()

    # Print results
    print(f"Program: {result.program_name}")
    print()
    print("Ground manifest:")
    for key, value in result.bindings["ground"].items():
        print(f"  {key}: {value}")
    print()
    print("Judged result:")
    for key, value in result.bindings["judged"].items():
        print(f"  {key}: {value}")
    print()
    print(f"Artifacts emitted: {len(result.artifacts)}")
    print(f"Witnesses captured: {len(result.witnesses)}")
    print()
    print("Witness details:")
    for w in result.witnesses:
        print(f"  {w.pass_name}: {w.agent_path}")


if __name__ == "__main__":
    asyncio.run(main())
