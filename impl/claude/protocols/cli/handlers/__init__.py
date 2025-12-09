"""
CLI Handlers - Lazy-loaded command implementations.

This package contains handlers for the Hollow Shell architecture.
Each handler is only imported when its command is invoked.

Structure:
- companions.py: Daily companion commands (pulse, ground, breathe, entropy)
- scientific.py: Scientific core commands (falsify, conjecture, rival, sublate, shadow)
- mirror.py: Mirror Protocol commands
- membrane.py: Membrane Protocol commands
- igent.py: I-gent integration (garden, whisper)
- debug.py: Debug utilities

All handlers follow the signature:
    def cmd_<name>(args: list[str]) -> int
"""
