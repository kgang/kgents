#!/usr/bin/env python3
"""
Witness This Session: Capture reasoning traces for decisions made NOW.

This script dogfoods the Witness/Fusion system by using it to trace
decisions happening in the current conversation.

Usage:
    uv run python scripts/witness_this_session.py

The Insight:
    "The proof IS the decision. The mark IS the witness."
    - We use the system to witness its own creation
    - Meta-level dogfooding validates the architecture
"""

import asyncio
from datetime import UTC, datetime

# =============================================================================
# The Decision Being Witnessed
# =============================================================================

DECISION_CONTEXT = """
Session: 2025-12-21
Question: "Is it too early to start capturing reasoning traces and decision proofs?"
Answer: No—the infrastructure exists. Dogfood it now.
"""

KENT_PROPOSAL = {
    "agent": "kent",
    "content": "Start capturing reasoning traces now, using the system we're building",
    "reasoning": "Dogfooding validates architecture. Meta-level proof that the system works.",
    "principles": ["generative", "joy-inducing", "composable"],
}

CLAUDE_PROPOSAL = {
    "agent": "claude",
    "content": "The Mark/Fusion infrastructure already exists—use it immediately",
    "reasoning": "mark.py has reasoning field, Fusion service records thoughts, providers wired",
    "principles": ["composable", "tasteful"],
}

SYNTHESIS = {
    "content": "Create witness_this_session.py to capture decisions as they happen",
    "reasoning": "Proves the system works by using it; creates first real reasoning trace",
    "incorporates_from_a": "Immediate action on dogfooding",
    "incorporates_from_b": "Leveraging existing infrastructure",
    "transcends": "Not just talking about it, but doing it",
}


async def witness_decision() -> None:
    """Capture this decision using the Fusion system."""
    from services.fusion import FusionService, Proposal, Synthesis as SynthesisType
    from services.witness.persistence import WitnessPersistence
    from services.witness.polynomial import Thought

    print("=" * 60)
    print("WITNESSING THIS SESSION")
    print("=" * 60)
    print(DECISION_CONTEXT)
    print()

    # Try to get real persistence, fall back to in-memory
    try:
        from services.providers import get_witness_persistence

        witness = await get_witness_persistence()
        print("[+] Using PostgreSQL witness persistence")
    except Exception as e:
        print(f"[!] Falling back to in-memory: {e}")
        witness = None

    # Create fusion service
    fusion = FusionService(witness=witness)

    # Create proposals
    kent = fusion.propose(**KENT_PROPOSAL)
    claude = fusion.propose(**CLAUDE_PROPOSAL)

    print(f"[+] Kent's proposal: {kent.id}")
    print(f"    Content: {kent.content}")
    print(f"    Reasoning: {kent.reasoning}")
    print()

    print(f"[+] Claude's proposal: {claude.id}")
    print(f"    Content: {claude.content}")
    print(f"    Reasoning: {claude.reasoning}")
    print()

    # Create synthesis
    result = await fusion.simple_fuse(
        kent,
        claude,
        synthesis_content=SYNTHESIS["content"],
        synthesis_reasoning=SYNTHESIS["reasoning"],
        incorporates_from_a=SYNTHESIS["incorporates_from_a"],
        incorporates_from_b=SYNTHESIS["incorporates_from_b"],
        transcends=SYNTHESIS["transcends"],
    )

    print(f"[+] Fusion result: {result.id}")
    print(f"    Status: {result.status.value}")
    print(f"    Synthesis: {result.synthesis.content if result.synthesis else 'None'}")
    print(f"    Is genuine fusion: {result.is_genuine_fusion}")
    print()

    # Record as thought if witness available
    if witness:
        thought = Thought(
            content=f"Decision witnessed: {SYNTHESIS['content']}",
            source="fusion.system",
            tags=("meta", "dogfood", "witness-session"),
            timestamp=datetime.now(UTC),
        )
        await witness.save_thought(thought)
        print("[+] Thought saved to witness store")

    print("=" * 60)
    print("WITNESS COMPLETE")
    print("=" * 60)
    print()
    print("This decision is now part of the reasoning trace.")
    print("The system witnessed its own creation.")
    print()
    print('"The proof IS the decision."')


if __name__ == "__main__":
    asyncio.run(witness_decision())
