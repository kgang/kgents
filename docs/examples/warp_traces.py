#!/usr/bin/env python3
"""
WARP Traces: Time-Aware Witnessing

The Witness doesn't just observe—it remembers the shape of time.
TraceNodes capture causality. Walks capture intent across time.

    "Every action leaves a trace. Traces form walks.
     Walks encode the dance of stimulus and response."

Run: python docs/examples/warp_traces.py
"""

import sys

sys.path.insert(0, "impl/claude")

from services.witness import (
    LinkRelation,
    NPhase,
    Response,
    Stimulus,
    TraceLink,
    TraceNode,
    generate_trace_id,
)

# Create a chain of traces (sense -> act)
t1 = TraceNode(
    origin="user",
    stimulus=Stimulus(kind="prompt", content="What is composition?"),
)

t2 = TraceNode(
    origin="witness",
    stimulus=Stimulus(kind="prompt", content="Responding..."),
    response=Response(kind="text", content="Composition is morphism wiring."),
    links=(
        TraceLink(
            source=t1.id, target=generate_trace_id(), relation=LinkRelation.CONTINUES
        ),
    ),
)

print("WARP Traces: Capturing Causality")
print("=" * 45)

print(f"\nTrace 1 (origin: {t1.origin})")
print(f"  ID: {t1.id[:20]}...")
print(f"  Stimulus: {t1.stimulus.content}")

print(f"\nTrace 2 (origin: {t2.origin})")
print(f"  ID: {t2.id[:20]}...")
print(f"  Response: {t2.response.content}")
print(f"  Links: CONTINUES from {t2.links[0].source[:20]}...")

print("\nThe Causality Chain:")
print("  [user prompt] --> [witness response]")
print("  (Traces encode the dance of stimulus and response)")
