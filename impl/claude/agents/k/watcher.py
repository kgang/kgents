"""
K-gent File Watcher: Ambient pair programming presence.

Watches your codebase and offers contextual insights based on
file changes, complexity growth, and coding patterns.

The Watcher integrates with K-gent soul for personality-infused suggestions.

Usage:
    from agents.k.watcher import KgentWatcher

    watcher = KgentWatcher(project_root="/path/to/project")
    await watcher.start()  # Start watching
    await watcher.stop()   # Stop watching

Philosophy: "K-gent as ambient pair programmer."
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Watchdog Protocol (for dependency injection / testing)
# =============================================================================


class FileEvent(Protocol):
    """Protocol for file system events."""

    src_path: str
    is_directory: bool
    event_type: str


@dataclass
class SimpleFileEvent:
    """Simple implementation of FileEvent for testing/fallback."""

    src_path: str
    is_directory: bool = False
    event_type: str = "modified"


# =============================================================================
# Heuristics Protocol
# =============================================================================


@dataclass
class HeuristicResult:
    """Result from a heuristic check."""

    triggered: bool
    message: str = ""
    severity: str = "info"  # info, warning, suggestion
    file_path: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class Heuristic(Protocol):
    """Protocol for watch heuristics."""

    name: str
    enabled: bool

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check if this heuristic applies to the given path."""
        ...

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Run the heuristic check and return result."""
        ...


# =============================================================================
# Built-in Heuristics
# =============================================================================


@dataclass
class ComplexityHeuristic:
    """
    Detects functions that are getting too complex.

    Triggers when a function exceeds the line threshold.
    """

    name: str = "complexity"
    enabled: bool = True
    max_function_lines: int = 30

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check Python files."""
        return path.endswith(".py") and not path.endswith("__init__.py")

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Check function lengths in the file."""
        if content is None:
            try:
                content = Path(path).read_text()
            except Exception:
                return HeuristicResult(triggered=False)

        # Simple heuristic: look for long functions
        # More sophisticated: use AST parsing
        lines = content.split("\n")
        in_function = False
        function_start = 0
        function_name = ""
        long_functions: list[tuple[str, int]] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                if in_function:
                    # Check previous function
                    length = i - function_start
                    if length > self.max_function_lines:
                        long_functions.append((function_name, length))
                # Start tracking new function
                in_function = True
                function_start = i
                # Extract function name
                if "def " in stripped:
                    function_name = stripped.split("def ")[1].split("(")[0]

        # Check the last function
        if in_function:
            length = len(lines) - function_start
            if length > self.max_function_lines:
                long_functions.append((function_name, length))

        if long_functions:
            names = ", ".join(f"`{n}` ({l} lines)" for n, l in long_functions[:2])
            return HeuristicResult(
                triggered=True,
                message=f"Getting complex: {names}. Consider splitting?",
                severity="suggestion",
                file_path=path,
                details={"functions": long_functions},
            )

        return HeuristicResult(triggered=False)


@dataclass
class NamingHeuristic:
    """
    Detects poor variable naming (single letters, unclear names).

    Triggers when single-letter variables are used outside comprehensions.
    """

    name: str = "naming"
    enabled: bool = True

    # Allowed single letters (common idioms)
    allowed_singles: set[str] = field(
        default_factory=lambda: {"i", "j", "k", "x", "y", "z", "e", "f", "_"}
    )

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check Python files."""
        return path.endswith(".py")

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Check for poor variable naming."""
        if content is None:
            try:
                content = Path(path).read_text()
            except Exception:
                return HeuristicResult(triggered=False)

        # Look for assignments like `x = ...` where x is single letter
        # Exclude comprehensions and lambda params
        import re

        suspicious: list[str] = []

        for line in content.split("\n"):
            # Skip comments and strings (rough heuristic)
            if line.strip().startswith("#"):
                continue

            # Look for simple assignments
            match = re.match(r"^\s*([a-z])\s*=\s*", line)
            if match:
                var = match.group(1)
                if var not in self.allowed_singles:
                    suspicious.append(var)

        if suspicious:
            vars_str = ", ".join(f"'{v}'" for v in list(set(suspicious))[:3])
            return HeuristicResult(
                triggered=True,
                message=f"Single-letter variables: {vars_str}. What do they represent?",
                severity="suggestion",
                file_path=path,
                details={"variables": suspicious},
            )

        return HeuristicResult(triggered=False)


@dataclass
class PatternHeuristic:
    """
    Detects common design patterns that might need naming.

    Triggers when code looks like a known pattern (Factory, Builder, etc.)
    """

    name: str = "patterns"
    enabled: bool = True

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check Python files."""
        return path.endswith(".py")

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Check for design patterns."""
        if content is None:
            try:
                content = Path(path).read_text()
            except Exception:
                return HeuristicResult(triggered=False)

        patterns_found: list[str] = []

        # Factory pattern indicators
        if "def create_" in content and "return " in content:
            if "class" not in content.split("def create_")[0][-50:]:
                patterns_found.append("Factory")

        # Builder pattern indicators
        if content.count("self._") > 3 and ".build(" in content:
            patterns_found.append("Builder")

        # Observer pattern indicators
        if "subscribe" in content.lower() and "notify" in content.lower():
            patterns_found.append("Observer")

        # Strategy pattern indicators
        if content.count("def execute(") > 1 or (
            "Protocol" in content and "def __call__" in content
        ):
            patterns_found.append("Strategy")

        if patterns_found:
            patterns_str = ", ".join(patterns_found)
            return HeuristicResult(
                triggered=True,
                message=f"This looks like a {patterns_str} pattern. Well-named?",
                severity="info",
                file_path=path,
                details={"patterns": patterns_found},
            )

        return HeuristicResult(triggered=False)


@dataclass
class TestsHeuristic:
    """
    Detects code that might need tests.

    Triggers when new public functions are added without corresponding tests.
    """

    name: str = "tests"
    enabled: bool = True

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check non-test Python files."""
        return path.endswith(".py") and "_tests" not in path and "test_" not in Path(path).name

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Check for untested code."""
        if content is None:
            try:
                content = Path(path).read_text()
            except Exception:
                return HeuristicResult(triggered=False)

        # Count public functions (not starting with _)
        import re

        public_funcs = re.findall(r"^def ([a-z][a-zA-Z0-9_]*)\(", content, re.MULTILINE)

        if not public_funcs:
            return HeuristicResult(triggered=False)

        # Check if corresponding test file exists
        path_obj = Path(path)
        test_dir = path_obj.parent / "_tests"
        test_file = test_dir / f"test_{path_obj.name}"

        if not test_file.exists():
            funcs_str = ", ".join(f"`{f}`" for f in public_funcs[:2])
            return HeuristicResult(
                triggered=True,
                message=f"New functions: {funcs_str}. Want me to suggest tests?",
                severity="suggestion",
                file_path=path,
                details={"functions": public_funcs, "test_file": str(test_file)},
            )

        return HeuristicResult(triggered=False)


@dataclass
class DocsHeuristic:
    """
    Detects undocumented public functions and classes.

    Triggers when public API lacks docstrings.
    """

    name: str = "docs"
    enabled: bool = True

    def matches(self, path: str, content: str | None = None) -> bool:
        """Check Python files."""
        return path.endswith(".py") and "__init__" not in path

    def check(self, path: str, content: str | None = None) -> HeuristicResult:
        """Check for missing docstrings."""
        if content is None:
            try:
                content = Path(path).read_text()
            except Exception:
                return HeuristicResult(triggered=False)

        # Simple heuristic: look for def not followed by docstring
        import re

        lines = content.split("\n")
        undocumented: list[str] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                # Check if next non-empty line is a docstring
                if "def _" in stripped or "def __" in stripped:
                    continue  # Private, skip

                # Extract function name
                if "def " in stripped:
                    func_name = stripped.split("def ")[1].split("(")[0]
                else:
                    continue

                # Look for docstring in next few lines
                has_docstring = False
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        has_docstring = True
                        break
                    if next_line and not next_line.startswith("#"):
                        break  # Non-empty, non-comment, non-docstring

                if not has_docstring:
                    undocumented.append(func_name)

        if undocumented:
            funcs_str = ", ".join(f"`{f}`" for f in undocumented[:2])
            return HeuristicResult(
                triggered=True,
                message=f"Undocumented: {funcs_str}. Brief docstring would help.",
                severity="suggestion",
                file_path=path,
                details={"functions": undocumented},
            )

        return HeuristicResult(triggered=False)


# =============================================================================
# Watcher Configuration
# =============================================================================


@dataclass
class WatcherConfig:
    """Configuration for the K-gent watcher."""

    # Paths to watch
    project_root: Path = field(default_factory=Path.cwd)
    recursive: bool = True

    # Debounce settings
    debounce_seconds: float = 0.5

    # Heuristic settings
    complexity_enabled: bool = True
    naming_enabled: bool = True
    patterns_enabled: bool = True
    tests_enabled: bool = True
    docs_enabled: bool = True

    # Filter settings
    ignored_patterns: list[str] = field(
        default_factory=lambda: [
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
            "*.egg-info",
            ".mypy_cache",
            ".pytest_cache",
            "node_modules",
            ".tox",
        ]
    )

    @classmethod
    def from_file(cls, path: Path) -> "WatcherConfig":
        """Load config from YAML file."""
        try:
            import yaml

            with open(path) as f:
                data = yaml.safe_load(f)

            return cls(
                project_root=Path(data.get("project_root", Path.cwd())),
                recursive=data.get("recursive", True),
                debounce_seconds=data.get("debounce_seconds", 0.5),
                complexity_enabled=data.get("heuristics", {}).get("complexity", True),
                naming_enabled=data.get("heuristics", {}).get("naming", True),
                patterns_enabled=data.get("heuristics", {}).get("patterns", True),
                tests_enabled=data.get("heuristics", {}).get("tests", True),
                docs_enabled=data.get("heuristics", {}).get("docs", True),
                ignored_patterns=data.get("ignored_patterns", cls.ignored_patterns),
            )
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            return cls()


# =============================================================================
# K-gent Watcher
# =============================================================================


@dataclass
class WatchNotification:
    """A notification from the watcher."""

    timestamp: datetime
    heuristic: str
    message: str
    severity: str
    file_path: str
    details: dict[str, Any] = field(default_factory=dict)


class KgentWatcher:
    """
    K-gent File Watcher: Ambient pair programming presence.

    Watches your codebase and offers contextual insights based on
    file changes, complexity growth, and coding patterns.
    """

    def __init__(
        self,
        config: WatcherConfig | None = None,
        project_root: Path | str | None = None,
    ) -> None:
        """
        Initialize the watcher.

        Args:
            config: Watcher configuration
            project_root: Override project root (convenience param)
        """
        self.config = config or WatcherConfig()
        if project_root:
            self.config.project_root = Path(project_root)

        # Initialize heuristics
        self._heuristics: list[Heuristic] = []
        self._init_heuristics()

        # State
        self._running = False
        self._observer: Any = None
        self._last_event_time: dict[str, float] = {}
        self._notifications: list[WatchNotification] = []
        self._callbacks: list[Callable[[WatchNotification], None]] = []

    def _init_heuristics(self) -> None:
        """Initialize enabled heuristics."""
        if self.config.complexity_enabled:
            self._heuristics.append(ComplexityHeuristic())
        if self.config.naming_enabled:
            self._heuristics.append(NamingHeuristic())
        if self.config.patterns_enabled:
            self._heuristics.append(PatternHeuristic())
        if self.config.tests_enabled:
            self._heuristics.append(TestsHeuristic())
        if self.config.docs_enabled:
            self._heuristics.append(DocsHeuristic())

    def subscribe(self, callback: Callable[[WatchNotification], None]) -> None:
        """Subscribe to notifications."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable[[WatchNotification], None]) -> None:
        """Unsubscribe from notifications."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        from fnmatch import fnmatch

        path_obj = Path(path)

        for pattern in self.config.ignored_patterns:
            if fnmatch(path_obj.name, pattern):
                return True
            if any(fnmatch(p, pattern) for p in path_obj.parts):
                return True

        return False

    def _is_debounced(self, path: str) -> bool:
        """Check if path change is within debounce window."""
        now = time.time()
        last = self._last_event_time.get(path, 0)

        if now - last < self.config.debounce_seconds:
            return True

        self._last_event_time[path] = now
        return False

    def _handle_file_change(self, path: str) -> None:
        """Handle a file change event."""
        if self._should_ignore(path):
            return

        if self._is_debounced(path):
            return

        # Read file content
        try:
            content = Path(path).read_text()
        except Exception:
            content = None

        # Run heuristics
        for heuristic in self._heuristics:
            if not heuristic.matches(path, content):
                continue

            result = heuristic.check(path, content)
            if result.triggered:
                notification = WatchNotification(
                    timestamp=datetime.now(timezone.utc),
                    heuristic=heuristic.name,
                    message=result.message,
                    severity=result.severity,
                    file_path=path,
                    details=result.details,
                )
                self._notifications.append(notification)

                # Notify subscribers
                for callback in self._callbacks:
                    try:
                        callback(notification)
                    except Exception as e:
                        logger.warning(f"Notification callback error: {e}")

    async def start(self) -> None:
        """Start watching for file changes."""
        if self._running:
            return

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class Handler(FileSystemEventHandler):
                def __init__(self, watcher: KgentWatcher) -> None:
                    self._watcher = watcher

                def on_modified(self, event: Any) -> None:
                    if event.is_directory:
                        return
                    self._watcher._handle_file_change(event.src_path)

                def on_created(self, event: Any) -> None:
                    if event.is_directory:
                        return
                    self._watcher._handle_file_change(event.src_path)

            self._observer = Observer()
            handler = Handler(self)
            self._observer.schedule(
                handler,
                str(self.config.project_root),
                recursive=self.config.recursive,
            )
            self._observer.start()
            self._running = True
            logger.info(f"Started watching: {self.config.project_root}")

        except ImportError:
            logger.warning(
                "watchdog not installed. Using polling fallback. Install with: pip install watchdog"
            )
            # Could implement polling fallback here
            self._running = True

    async def stop(self) -> None:
        """Stop watching for file changes."""
        if not self._running:
            return

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

        self._running = False
        logger.info("Stopped watching")

    @property
    def running(self) -> bool:
        """Check if watcher is running."""
        return self._running

    @property
    def notifications(self) -> list[WatchNotification]:
        """Get all notifications."""
        return self._notifications

    def recent_notifications(self, limit: int = 10) -> list[WatchNotification]:
        """Get recent notifications."""
        return self._notifications[-limit:]

    def clear_notifications(self) -> None:
        """Clear notification history."""
        self._notifications.clear()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core
    "KgentWatcher",
    "WatcherConfig",
    "WatchNotification",
    # Heuristics
    "Heuristic",
    "HeuristicResult",
    "ComplexityHeuristic",
    "NamingHeuristic",
    "PatternHeuristic",
    "TestsHeuristic",
    "DocsHeuristic",
]
