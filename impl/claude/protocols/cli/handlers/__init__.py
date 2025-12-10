"""
CLI Handlers - Lazy-loaded command implementations.

This package contains handlers for the Hollow Shell architecture.
Each handler is only imported when its command is invoked.

Structure:
- membrane.py: Membrane Protocol commands (topological perception)
- igent.py: I-gent integration (garden, whisper)
- init.py: Workspace initialization
- wipe.py: Database cleanup commands
- debug.py: Debug utilities

All handlers follow the signature:
    def cmd_<name>(args: list[str]) -> int
"""
