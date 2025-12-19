"""
Witness Event Sources (Watchers).

Each watcher is a FluxAgent that reacts to events from a specific source.
Watchers are event-driven, NOT timer-driven (meta.md: "Timer-driven loops create zombies").

Available Watchers:
- GitWatcher: React to git operations (commits, pushes, checkouts)
- FileSystemWatcher: React to file changes (placeholder)
- TestWatcher: React to pytest results (placeholder)
- AgenteseWatcher: React to cross-jewel events via SynergyBus (placeholder)
- CIWatcher: React to GitHub Actions events (placeholder)

See: docs/skills/data-bus-integration.md
"""

# Re-export GitEvent from polynomial (canonical location)
from services.witness.polynomial import GitEvent

from .git import (
    GitWatcher,
    WatcherState,
    WatcherStats,
    create_git_watcher,
)

__all__ = [
    "GitWatcher",
    "GitEvent",
    "WatcherState",
    "WatcherStats",
    "create_git_watcher",
]
