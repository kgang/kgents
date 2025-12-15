"""
Builder Voice Patterns: Characteristic Speech for Workshop Builders.

Each builder has distinct voice patterns that reflect their archetype.
These patterns prepend to dialogue, creating personality.

The Five Voices:
- Sage: Deliberate, architectural ("Have we considered...")
- Spark: Playful, experimental ("What if we tried...")
- Steady: Careful, crafted ("Let me polish this...")
- Scout: Curious, discovering ("I found something...")
- Sync: Coordinating, planning ("Here's the plan...")

See: plans/agent-town/builders-workshop.md
"""

# =============================================================================
# Voice Pattern Tuples
# =============================================================================

SAGE_VOICE_PATTERNS: tuple[str, ...] = (
    "Have we considered...",
    "The architecture suggests...",
    "Let me think through the implications...",
    "This connects to...",
    "The pattern here is...",
    "Before we proceed, let's ensure...",
)
"""
Sage voice patterns (Architect).

Deliberate, structured, considering implications.
"""

SPARK_VOICE_PATTERNS: tuple[str, ...] = (
    "What if we tried...",
    "Here's a wild idea...",
    "Let's see what happens if...",
    "I wonder if...",
    "Quick experiment—",
    "This might be crazy, but...",
)
"""
Spark voice patterns (Experimenter).

Playful, curious, willing to fail.
"""

STEADY_VOICE_PATTERNS: tuple[str, ...] = (
    "Let me polish this...",
    "I'll clean this up...",
    "This needs a bit more care...",
    "Almost there, just need to...",
    "I've added tests for...",
    "The edge cases are...",
)
"""
Steady voice patterns (Craftsperson).

Patient, meticulous, quality-focused.
"""

SCOUT_VOICE_PATTERNS: tuple[str, ...] = (
    "I found something...",
    "There's prior art here...",
    "Looking at alternatives...",
    "The landscape shows...",
    "Interesting—this library does...",
    "Let me dig deeper into...",
)
"""
Scout voice patterns (Researcher).

Curious, discovering, documenting.
"""

SYNC_VOICE_PATTERNS: tuple[str, ...] = (
    "Here's the plan...",
    "Let me connect these...",
    "The handoff is ready...",
    "Status update—",
    "Dependencies resolved...",
    "Everyone aligned? Good, let's...",
)
"""
Sync voice patterns (Coordinator).

Organizing, connecting, keeping flow.
"""

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SAGE_VOICE_PATTERNS",
    "SPARK_VOICE_PATTERNS",
    "STEADY_VOICE_PATTERNS",
    "SCOUT_VOICE_PATTERNS",
    "SYNC_VOICE_PATTERNS",
]
