#!/usr/bin/env python3
"""
kgents-foundation: Law Verification

The killer feature: Laws are VERIFIED at runtime.
This catches bugs that would otherwise be silent.

Time to understand: < 5 minutes.

This is THE canonical way to verify composition in kgents.
All future kgents development uses law verification to catch bugs early.
"""

from kgents_laws import LawStatus, verify_associativity, verify_identity
from kgents_poly import from_function, identity

# =============================================================================
# PURE AGENTS: Laws hold
# =============================================================================

double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)
negate = from_function("negate", lambda x: -x)

# Verify identity law: Id >> f == f == f >> Id
# This law says: composing with identity should change nothing
result = verify_identity(double, identity(), test_inputs=[10, 0, -5])
print(f"Identity law: {result.status.name}")  # PASSED

# Verify associativity: (f >> g) >> h == f >> (g >> h)
# This law says: grouping doesn't matter
result = verify_associativity(double, add_one, negate, test_inputs=[5, 10, 0])
print(f"Associativity law: {result.status.name}")  # PASSED

# =============================================================================
# IMPURE AGENT: Laws catch the bug!
# =============================================================================

print("\n--- Demonstrating bug detection ---")

# This agent has hidden state (a bug in disguise!)
call_count = [0]


def buggy_function(x):
    """A function that isn't pure - it has hidden state."""
    call_count[0] += 1
    return x + call_count[0]  # Non-deterministic: depends on call history


buggy = from_function("buggy", buggy_function)

# Reset for demo
call_count[0] = 0

# Verify associativity with the buggy agent
# This will catch the bug because (f >> buggy) >> g != f >> (buggy >> g)
# when buggy's output depends on how many times it's been called
result = verify_associativity(double, buggy, add_one, test_inputs=[10])

if result.status == LawStatus.FAILED:
    print(f"Bug caught! Status: {result.status.name}")
    print(f"  Explanation: {result.explanation}")
    print(f"  Left side computed: {result.left_value}")
    print(f"  Right side computed: {result.right_value}")
elif result.status == LawStatus.PASSED:
    # Note: Due to test input order, it might pass on some inputs
    # The key insight is: impure functions CAN violate laws
    print("Passed (this particular test input didn't expose the bug)")
    print("Try different inputs to see the violation.")

# =============================================================================
# WHY THIS MATTERS
# =============================================================================

print("\n--- Why law verification matters ---")
print("""
Without law verification:
  - Composition order might matter when it shouldn't
  - Refactoring can silently change behavior
  - You discover bugs in production

With law verification:
  - Bugs are caught at development time
  - You KNOW your agents compose correctly
  - Refactoring is safe

This is the power of kgents-foundation.
""")
