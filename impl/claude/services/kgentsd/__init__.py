"""
kgentsd: The Daemon Infrastructure for kgents.

This module provides the background daemon that:
- Watches for events (git, filesystem, tests, CI)
- Routes events through workflows
- Manages trust escalation
- Provides CLI and TUI interfaces

The daemon is infrastructure. The witness is semantics.
Witness primitives (Mark, Grant, Scope, Playbook) remain in services/witness/.
"""

from .cli import main
from .daemon import (
    DEFAULT_WATCHERS,
    WATCHER_TYPES,
    DaemonConfig,
    WitnessDaemon,
    check_daemon_status,
    create_watcher,
    event_to_thought,
    get_daemon_status,
    start_daemon,
    stop_daemon,
)
from .invoke import JewelInvoker, create_invoker
from .pipeline import Pipeline, PipelineRunner, Step
from .reactor import Event, Reaction, WitnessReactor
from .schedule import WitnessScheduler, create_scheduler
from .trust_persistence import TrustPersistence
from .workflows import WORKFLOW_REGISTRY, WorkflowTemplate

__all__ = [
    # CLI
    "main",
    # Daemon
    "DaemonConfig",
    "WitnessDaemon",
    "WATCHER_TYPES",
    "DEFAULT_WATCHERS",
    "check_daemon_status",
    "get_daemon_status",
    "start_daemon",
    "stop_daemon",
    "create_watcher",
    "event_to_thought",
    # Pipeline
    "Pipeline",
    "PipelineRunner",
    "Step",
    # Invoke
    "JewelInvoker",
    "create_invoker",
    # Reactor
    "Event",
    "Reaction",
    "WitnessReactor",
    # Schedule
    "WitnessScheduler",
    "create_scheduler",
    # Workflows
    "WORKFLOW_REGISTRY",
    "WorkflowTemplate",
    # Trust
    "TrustPersistence",
]
