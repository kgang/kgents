"""
zen-agents UI: Textual TUI for agent-based session management.

Built on kgents bootstrap agents, this UI provides:
- ZenAgentsApp: Main application with agent-injected services
- MainScreen: Session list + output view
- Agent pipelines for all user actions
"""

from .app import ZenAgentsApp, main

__all__ = ["ZenAgentsApp", "main"]
