#!/usr/bin/env python3
"""
zen-agents Demonstration

Shows the kgents architecture in action:
    1. Ground state initialization
    2. Judge validation
    3. Session creation pipeline
    4. Fix-based state detection
    5. Composition patterns

Run with: uv run python demo.py
"""

import asyncio
from pathlib import Path

from zen_agents.types import SessionConfig, SessionType, SessionState
from zen_agents.ground import zen_ground, ZenGround
from zen_agents.judge import zen_judge
from zen_agents.session.create import create_session
from zen_agents.session.detect import detect_state, DetectionResult
from pipelines.new_session import NewSessionPipeline, create_session_pipeline


async def demo_ground():
    """Demonstrate ZenGround - the empirical seed."""
    print("\n" + "=" * 60)
    print("1. ZENGROUND - The Empirical Seed")
    print("=" * 60)

    ground = ZenGround(discover_tmux=False)  # Don't actually call tmux
    state = await ground.invoke(None)

    print(f"\nGround state initialized:")
    print(f"  - Config layers: {len(state.config_cascade)}")
    print(f"  - Default session type: {state.default_session_type.value}")
    print(f"  - Max sessions: {state.max_sessions}")
    print(f"  - Auto discovery: {state.auto_discovery}")

    # Query specific aspects
    default_shell = None
    for layer in state.config_cascade:
        if "default_shell" in layer.values:
            default_shell = layer.values["default_shell"]
    print(f"  - Default shell: {default_shell}")

    return ground


async def demo_judge(ground: ZenGround):
    """Demonstrate ZenJudge - validation against principles."""
    print("\n" + "=" * 60)
    print("2. ZENJUDGE - Validation Against Principles")
    print("=" * 60)

    ground_state = await ground.invoke(None)
    judge = zen_judge.with_ground(ground_state)

    # Valid config
    valid_config = SessionConfig(
        name="my-claude-session",
        session_type=SessionType.CLAUDE,
        working_dir=str(Path.cwd()),
    )

    verdict = await judge.invoke(valid_config)
    print(f"\nValid config verdict:")
    print(f"  - Valid: {verdict.valid}")
    print(f"  - Issues: {verdict.issues or 'None'}")

    # Invalid config - bad name
    invalid_config = SessionConfig(
        name="bad name with spaces!",
        session_type=SessionType.CLAUDE,
    )

    verdict = await judge.invoke(invalid_config)
    print(f"\nInvalid config verdict:")
    print(f"  - Valid: {verdict.valid}")
    print(f"  - Issues: {verdict.issues}")
    print(f"  - Suggestions: {verdict.suggestions}")


async def demo_session_create():
    """Demonstrate SessionCreate - pure transformation."""
    print("\n" + "=" * 60)
    print("3. SESSIONCREATE - Pure Transformation")
    print("=" * 60)

    config = SessionConfig(
        name="demo-session",
        session_type=SessionType.SHELL,
        working_dir="/tmp",
        tags=["demo", "test"],
    )

    session = await create_session.invoke(config)

    print(f"\nSession created (pure transform):")
    print(f"  - ID: {session.id}")
    print(f"  - State: {session.state.value}")
    print(f"  - Type: {session.config.session_type.value}")
    print(f"  - Working dir: {session.config.working_dir}")
    print(f"  - tmux attached: {session.tmux is not None}")
    print(f"  - Started: {session.started_at}")

    return session


async def demo_state_detection(session):
    """Demonstrate Fix-based state detection."""
    print("\n" + "=" * 60)
    print("4. DETECT_STATE - Fix-Based Polling")
    print("=" * 60)

    # Add some fake output to the session
    from dataclasses import replace
    session_with_output = replace(
        session,
        output_lines=[
            "Starting process...",
            "Processing item 1",
            "Processing item 2",
            "Done!",
            "$ ",  # Shell prompt - indicates completion
        ]
    )

    result = await detect_state.invoke(session_with_output)

    print(f"\nDetection result (Fix-based):")
    print(f"  - State: {result.state.value}")
    print(f"  - Confidence: {result.confidence:.2f}")
    print(f"  - Iterations: {result.iterations}")
    print(f"  - Indicators: {result.indicators}")


async def demo_pipeline():
    """Demonstrate the composition pipeline."""
    print("\n" + "=" * 60)
    print("5. PIPELINE - Composition in Action")
    print("=" * 60)

    print("\nThe NewSessionPipeline composes:")
    print("  Judge → Create → Spawn → Detect")
    print("\nThis is equivalent to zenportal's SessionManager.create_session()")
    print("but with explicit, transparent composition.")

    # Show the pipeline structure
    pipeline = create_session_pipeline(tmux_prefix="demo")

    print(f"\nPipeline properties:")
    print(f"  - Name: {pipeline.name}")
    print(f"  - Genus: {pipeline.genus}")
    print(f"  - Purpose: {pipeline.purpose}")

    print("\nThe pipeline IS an agent:")
    print("  - Input type: SessionConfig")
    print("  - Output type: PipelineResult")
    print("  - Composable with other agents")

    # Note: Actually running would create real tmux sessions
    print("\n(Skipping actual execution to avoid creating tmux sessions)")


async def demo_bootstrap_mapping():
    """Show how bootstrap agents map to zen concepts."""
    print("\n" + "=" * 60)
    print("6. BOOTSTRAP MAPPING - The 7 Irreducible Agents")
    print("=" * 60)

    mappings = [
        ("Id", "Pass-through transforms (session → session)"),
        ("Compose", "Pipeline construction (Judge → Create → Spawn → Detect)"),
        ("Judge", "ZenJudge validates configs against 6 principles"),
        ("Ground", "ZenGround: config cascade + session state + tmux facts"),
        ("Contradict", "Detect conflicts (duplicate names, port clashes)"),
        ("Sublate", "Resolve conflicts (suggest alternative names)"),
        ("Fix", "State detection polling (iterate until stable)"),
    ]

    print("\nBootstrap → Zenportal mapping:")
    for agent, role in mappings:
        print(f"  {agent:12} → {role}")


async def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("ZEN-AGENTS DEMONSTRATION")
    print("Zenportal reimagined through kgents")
    print("=" * 60)

    # Run demos
    ground = await demo_ground()
    await demo_judge(ground)
    session = await demo_session_create()
    await demo_state_detection(session)
    await demo_pipeline()
    await demo_bootstrap_mapping()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("""
Key insights demonstrated:

1. SERVICES ARE AGENTS
   SessionManager → NewSessionPipeline
   Each service method is a composable morphism.

2. CONFIG IS GROUND
   3-tier cascade (config > portal > session) = ZenGround state
   The empirical seed from which all else derives.

3. POLLING IS FIX
   State detection via iteration until stable.
   The Y combinator made safe.

4. COMPOSITION IS PRIMARY
   Judge → Create → Spawn → Detect
   Complex behavior emerges from simple agent composition.

5. PRINCIPLES ARE JUDGE
   The 6 kgents principles embodied in ZenJudge.
   Validation ensures quality at every step.

This is the first iteration - imperfect but promising.
The architecture demonstrates that kgents can serve as
a foundation for real applications.
""")


if __name__ == "__main__":
    asyncio.run(main())
