"""
Example 03: Witness Trace
=========================

DEMONSTRATES: How Marks compose into Traces for reasoning chains.

In kgents, every action leaves a Mark. Marks are immutable records of:
- WHAT triggered the action (stimulus)
- WHAT it produced (response)
- WHO observed it (umwelt)
- WHY it was done (proof/justification)

KEY CONCEPTS:
- Mark: The atomic unit of execution history (immutable)
- Trace: An immutable sequence of Marks
- Proof: Toulmin argumentation structure (data -> warrant -> claim)

Philosophy: "Every action leaves a mark. Every mark joins a trace."

RUN: cd impl/claude && uv run python ../../examples/03-witness-trace/main.py
"""

import sys
from datetime import datetime
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "impl" / "claude"))

from services.witness.mark import (
    EvidenceTier,
    Mark,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
)
from services.witness.trace import Trace


def main() -> None:
    print("Witness Trace: Building Reasoning Chains")
    print("=" * 50)

    # Create an umwelt (observer context)
    umwelt = UmweltSnapshot(
        observer_id="developer",
        role="developer",
        capabilities=frozenset({"read", "write", "execute"}),
        trust_level=2,  # SUGGESTION level
    )

    # === Create a sequence of Marks that form a reasoning chain ===

    # Mark 1: User asks a question
    mark1 = Mark(
        origin="user",
        domain="chat",
        stimulus=Stimulus.from_prompt("How do I add a new agent?"),
        response=Response(kind="received", content="Question received"),
        umwelt=umwelt,
        tags=("question", "agent"),
        proof=Proof.empirical(
            data="User typed question in chat",
            warrant="Chat input indicates intent to learn",
            claim="User wants to understand agent creation",
        ),
    )

    # Mark 2: System searches documentation
    mark2 = Mark(
        origin="brain",
        domain="system",
        stimulus=Stimulus(kind="search", content="agent creation", source="internal"),
        response=Response(
            kind="result",
            content="Found: docs/skills/polynomial-agent.md",
            success=True,
        ),
        umwelt=umwelt,
        tags=("search", "documentation"),
        proof=Proof.empirical(
            data="Searched docs/ for 'agent creation'",
            warrant="Documentation search finds relevant guides",
            claim="polynomial-agent.md is relevant",
            backing="File contains 'PolyAgent' definition",
        ),
    )

    # Mark 3: System formulates response
    mark3 = Mark(
        origin="soul",
        domain="chat",
        stimulus=Stimulus(kind="context", content="docs/skills/polynomial-agent.md"),
        response=Response(
            kind="answer",
            content="To add an agent, use PolyAgent with state machine...",
            success=True,
        ),
        umwelt=umwelt,
        tags=("response", "explanation"),
        proof=Proof.categorical(
            data="PolyAgent[S,A,B] is the agent protocol",
            warrant="The spec defines agent construction",
            claim="PolyAgent enables agent creation",
            principles=("composable", "generative"),
        ),
    )

    # === Build the Trace ===

    trace: Trace[Mark] = Trace()
    trace = trace.add(mark1)
    trace = trace.add(mark2)
    trace = trace.add(mark3)

    print(f"\nBuilt trace with {len(trace)} marks\n")

    # === Print the reasoning chain ===

    print("Reasoning Chain:")
    print("-" * 40)

    for i, mark in enumerate(trace, 1):
        proof = mark.proof
        print(f"\nStep {i}: [{mark.origin}] -> [{mark.domain}]")
        print(f"  Stimulus: {mark.stimulus.kind} - {mark.stimulus.content[:40]}...")
        print(f"  Response: {mark.response.kind} - {mark.response.content[:40]}...")

        if proof:
            print(f"  Proof ({proof.tier.name}):")
            print(f"    Data: {proof.data[:50]}...")
            print(f"    Warrant: {proof.warrant[:50]}...")
            print(f"    Claim: {proof.claim[:50]}...")
            print(f"    Confidence: {proof.qualifier}")

    # === Demonstrate Trace operations ===

    print("\n" + "=" * 50)
    print("Trace Operations")
    print("=" * 50)

    # Filter by domain
    chat_marks = trace.filter_by_domain("chat")
    print(f"\nChat marks: {len(chat_marks)}")

    # Filter by origin
    brain_marks = trace.filter_by_origin("brain")
    print(f"Brain marks: {len(brain_marks)}")

    # Get latest
    latest = trace.latest
    if latest:
        print(f"Latest mark: {latest.origin} -> {latest.response.kind}")

    # === Demonstrate Trace immutability ===

    print("\n" + "=" * 50)
    print("Immutability Check")
    print("=" * 50)

    original_len = len(trace)
    new_mark = Mark(origin="test", domain="test")

    # This returns a NEW trace, doesn't modify original
    new_trace = trace.add(new_mark)

    print(f"Original trace length: {original_len}")
    print(f"New trace length: {len(new_trace)}")
    print(f"Original unchanged: {len(trace) == original_len}")

    print("\nReasoning chain complete. Every action is witnessed.")


if __name__ == "__main__":
    main()
