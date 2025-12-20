#!/usr/bin/env python3
"""
Trust Levels: Earned, Never Granted

The Witness doesn't start with power—it earns trust through
observation and correct behavior. This is ethical AI design.

    "L0: READ_ONLY - Observe only
     L1: BOUNDED - Write to .kgents/ only
     L2: SUGGESTION - Propose changes, require confirmation
     L3: AUTONOMOUS - Full developer agency"

Run: python docs/examples/trust_levels.py
"""

import sys

sys.path.insert(0, "impl/claude")

from services.witness.polynomial import TrustLevel
from services.witness.trust import Level1Criteria, check_escalation

print("Witness Trust Levels: Earned Through Observation")
print("=" * 55)

# Show all trust levels
for level in TrustLevel:
    desc = {
        TrustLevel.READ_ONLY: "Observe and project, no modifications",
        TrustLevel.BOUNDED: "Write to .kgents/ directory only",
        TrustLevel.SUGGESTION: "Propose changes, require confirmation",
        TrustLevel.AUTONOMOUS: "Full Kent-equivalent developer agency",
    }[level]
    print(f"  L{level.value} {level.name:<12} - {desc}")

print()
print("Escalation Criteria (L0 -> L1):")
criteria = Level1Criteria()
print(f"  - Minimum observations: {criteria.min_observations}")
print(f"  - Minimum hours: {criteria.min_hours}")
print(f"  - Max false positive rate: {criteria.max_false_positive_rate:.0%}")

print()
print("The Philosophy:")
print("  Trust is earned through consistent, accurate observation.")
print("  The ghost doesn't haunt—it witnesses, then acts.")
