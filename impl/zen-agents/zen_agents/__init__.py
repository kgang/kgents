"""
zen-agents: A contemplative TUI for managing parallel AI sessions.

Built on the 7 bootstrap agents:
- Every iteration is Fix
- Every conflict is Contradict
- Every pipeline is Compose
- Every validation is Judge
- Every fact is Ground

Usage:
    # As a CLI
    python -m zen_agents

    # As a library
    from zen_agents import ZenAgentsApp
    app = ZenAgentsApp()
    app.run()
"""

# kgents-runtime is installed via uv workspace, providing:
# - bootstrap (Agent, compose, Judge, Fix, etc.)
# - runtime (ClaudeCLIRuntime, LLMAgent, etc.)
# - agents (a, b, c, h, k genera)
# See kgents_bridge.py for convenient re-exports

from .app import ZenAgentsApp
from .models import Session, SessionState, SessionType, NewSessionConfig
from .services import SessionManager, StateRefresher, TmuxService

__version__ = "0.1.0"

__all__ = [
    "ZenAgentsApp",
    "Session",
    "SessionState",
    "SessionType",
    "NewSessionConfig",
    "SessionManager",
    "StateRefresher",
    "TmuxService",
]
