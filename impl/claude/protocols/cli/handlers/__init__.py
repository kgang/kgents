"""
CLI Handlers - Lazy-loaded command implementations.

This package contains handlers for the Hollow Shell architecture.
Each handler is only imported when its command is invoked.

Structure:
- a_gent.py: Alethic Architecture CLI (inspect, manifest, run)
- membrane.py: Membrane Protocol commands (topological perception)
- igent.py: I-gent integration (garden, whisper)
- init.py: Workspace initialization
- wipe.py: Database cleanup commands
- debug.py: Debug utilities
- ghost.py: Living Filesystem projection (DevEx V4 Phase 2)
- flinch.py: Test failure analysis (Trust Loop Integration)
- infra.py: K-Terrarium infrastructure (K8s cluster, CRDs)
- daemon.py: Cortex daemon lifecycle (start/stop/status, Mac launchd)
- soul.py: K-gent Digital Soul (Middleware of Consciousness)
- semaphore.py: Agent Semaphores (Rodizio Pattern)
- prompt.py: Evergreen Prompt System (Wave 6 Living CLI)

All handlers follow the signature:
    def cmd_<name>(args: list[str]) -> int
"""
