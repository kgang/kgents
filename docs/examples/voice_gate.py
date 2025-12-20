#!/usr/bin/env python3
"""
Voice Gate: Anti-Sausage Protocol

Kent's vision gets diluted through LLM processing. Each session
smooths the rough edges. The VoiceGate preserves authentic voice.

    "Did I smooth anything that should stay rough?"
    "Did I add words Kent wouldn't use?"

Run: python docs/examples/voice_gate.py
"""

import sys

sys.path.insert(0, "impl/claude")

from services.witness.voice_gate import VoiceAction, VoiceGate

gate = VoiceGate()

# Test phrases against voice rules
test_cases = [
    # Good: Direct, opinionated, Kent's voice
    ("Tasteful > feature-complete", "authentic"),
    ("The noun is a lie", "authentic"),
    # Bad: Hedging, corporate, diluted
    ("I think maybe we could consider", "hedging"),
    ("Going forward, we should leverage", "corporate"),
    ("Let me be clear and transparent", "filler"),
    # Voice anchors should pass
    ("The Mirror Test: Does K-gent feel like me?", "anchor"),
]

print("Voice Gate: Preserving Kent's Voice")
print("=" * 50)

for text, expected in test_cases:
    result = gate.check(text)
    if result.violations:
        action = result.violations[0].action.name
        status = f"{action}"
    else:
        status = "OK"

    marker = "OK" if status == "OK" else "XX"
    print(f"  [{marker}] {text[:40]:<40} -> {status}")

print()
print("Voice Anchors (quote, don't summarize):")
for anchor in list(gate.anchors)[:3]:
    print(f'  - "{anchor}"')
