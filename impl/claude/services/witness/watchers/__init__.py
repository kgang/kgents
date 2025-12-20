"""
Witness Event Sources (Watchers).

Each watcher is a FluxAgent that reacts to events from a specific source.
Watchers are event-driven, NOT timer-driven (meta.md: "Timer-driven loops create zombies").

Available Watchers:
- GitWatcher: React to git operations (commits, pushes, checkouts)
- FileSystemWatcher: React to file changes (create, modify, delete)
- TestWatcher: React to pytest results (pass, fail, skip, session)
- AgenteseWatcher: React to cross-jewel events via SynergyBus (placeholder)
- CIWatcher: React to GitHub Actions events (placeholder)

See: docs/skills/data-bus-integration.md
"""

# Re-export event types from polynomial (canonical location)
from services.witness.polynomial import FileEvent, GitEvent, TestEvent

# Base classes
from .base import BaseWatcher, WatcherState, WatcherStats

# Concrete watchers
from .filesystem import (
    Debouncer,
    FileSystemConfig,
    FileSystemWatcher,
    PatternMatcher,
    create_filesystem_watcher,
)
from .git import (
    GitWatcher,
    create_git_watcher,
)
from .test_watcher import (
    TestWatcher,
    TestWatcherConfig,
    TestWatcherPlugin,
    create_test_plugin,
    create_test_watcher,
)

__all__ = [
    # Base
    "BaseWatcher",
    "WatcherState",
    "WatcherStats",
    # Git
    "GitWatcher",
    "GitEvent",
    "create_git_watcher",
    # FileSystem
    "FileSystemWatcher",
    "FileSystemConfig",
    "FileEvent",
    "PatternMatcher",
    "Debouncer",
    "create_filesystem_watcher",
    # Test
    "TestWatcher",
    "TestWatcherConfig",
    "TestWatcherPlugin",
    "TestEvent",
    "create_test_watcher",
    "create_test_plugin",
]
