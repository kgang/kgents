"""Tests for K-gent file watcher."""

import tempfile
from pathlib import Path

import pytest
from agents.k.watcher import (
    ComplexityHeuristic,
    DocsHeuristic,
    HeuristicResult,
    KgentWatcher,
    NamingHeuristic,
    PatternHeuristic,
    TestsHeuristic,
    WatcherConfig,
    WatchNotification,
)


class TestComplexityHeuristic:
    """Tests for the complexity heuristic."""

    def test_matches_python_files(self) -> None:
        """Matches Python files."""
        h = ComplexityHeuristic()
        assert h.matches("foo.py") is True
        assert h.matches("foo.txt") is False
        assert h.matches("__init__.py") is False  # Skipped

    def test_triggers_on_long_function(self) -> None:
        """Triggers when function exceeds line threshold."""
        h = ComplexityHeuristic(max_function_lines=5)
        content = """
def short_func():
    return 1

def long_func():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    return a + b + c + d + e + f + g
"""
        result = h.check("test.py", content)
        assert result.triggered is True
        assert "long_func" in result.message
        assert "lines" in result.message

    def test_no_trigger_on_short_functions(self) -> None:
        """Does not trigger on short functions."""
        h = ComplexityHeuristic(max_function_lines=10)
        content = """
def func_a():
    return 1

def func_b():
    return 2
"""
        result = h.check("test.py", content)
        assert result.triggered is False


class TestNamingHeuristic:
    """Tests for the naming heuristic."""

    def test_matches_python_files(self) -> None:
        """Matches Python files."""
        h = NamingHeuristic()
        assert h.matches("foo.py") is True
        assert h.matches("foo.txt") is False

    def test_triggers_on_bad_names(self) -> None:
        """Triggers on single-letter variables not in allowed set."""
        h = NamingHeuristic()
        content = """
a = 1
b = 2
c = 3
"""
        result = h.check("test.py", content)
        assert result.triggered is True
        assert any(c in result.message for c in ["'a'", "'b'", "'c'"])

    def test_allows_common_idioms(self) -> None:
        """Does not trigger on common idioms like i, j, k."""
        h = NamingHeuristic()
        content = """
for i in range(10):
    for j in range(10):
        pass
"""
        # The heuristic only catches assignments, not loop vars
        result = h.check("test.py", content)
        assert result.triggered is False

    def test_ignores_underscore(self) -> None:
        """Underscore is allowed as unused variable."""
        h = NamingHeuristic()
        content = """
_ = some_function()
"""
        result = h.check("test.py", content)
        assert result.triggered is False


class TestPatternHeuristic:
    """Tests for the pattern detection heuristic."""

    def test_matches_python_files(self) -> None:
        """Matches Python files."""
        h = PatternHeuristic()
        assert h.matches("foo.py") is True
        assert h.matches("foo.txt") is False

    def test_detects_factory_pattern(self) -> None:
        """Detects Factory pattern indicators."""
        h = PatternHeuristic()
        content = """
def create_widget(config):
    return Widget(config)
"""
        result = h.check("test.py", content)
        assert result.triggered is True
        assert "Factory" in result.message

    def test_detects_observer_pattern(self) -> None:
        """Detects Observer pattern indicators."""
        h = PatternHeuristic()
        content = """
class Publisher:
    def subscribe(self, callback):
        self._callbacks.append(callback)

    def notify(self, event):
        for cb in self._callbacks:
            cb(event)
"""
        result = h.check("test.py", content)
        assert result.triggered is True
        assert "Observer" in result.message


class TestTestsHeuristic:
    """Tests for the tests heuristic."""

    def test_matches_non_test_files(self) -> None:
        """Matches non-test Python files."""
        h = TestsHeuristic()
        assert h.matches("module.py") is True
        assert h.matches("test_module.py") is False
        assert h.matches("module/_tests/test_foo.py") is False

    def test_suggests_tests_for_public_functions(self) -> None:
        """Suggests tests when public functions exist without test file."""
        h = TestsHeuristic()
        content = """
def public_function():
    return 42

def another_public():
    pass
"""
        # Create temp file to test
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "module.py"
            path.write_text(content)

            result = h.check(str(path), content)
            assert result.triggered is True
            assert (
                "public_function" in result.message
                or "another_public" in result.message
            )


class TestDocsHeuristic:
    """Tests for the docs heuristic."""

    def test_matches_python_files(self) -> None:
        """Matches Python files."""
        h = DocsHeuristic()
        assert h.matches("module.py") is True
        assert h.matches("__init__.py") is False

    def test_detects_undocumented_functions(self) -> None:
        """Detects public functions without docstrings."""
        h = DocsHeuristic()
        content = """
def documented_func():
    \"\"\"This has a docstring.\"\"\"
    return 1

def undocumented_func():
    return 2
"""
        result = h.check("test.py", content)
        assert result.triggered is True
        assert "undocumented_func" in result.message

    def test_ignores_private_functions(self) -> None:
        """Private functions don't need docstrings."""
        h = DocsHeuristic()
        content = """
def _private_func():
    return 1

def __dunder_func__():
    return 2
"""
        result = h.check("test.py", content)
        assert result.triggered is False


class TestWatcherConfig:
    """Tests for WatcherConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = WatcherConfig()
        assert config.recursive is True
        assert config.debounce_seconds > 0
        assert config.complexity_enabled is True
        assert config.naming_enabled is True

    def test_ignored_patterns(self) -> None:
        """Ignored patterns are set."""
        config = WatcherConfig()
        assert "__pycache__" in config.ignored_patterns
        assert ".git" in config.ignored_patterns


class TestKgentWatcher:
    """Tests for the KgentWatcher class."""

    def test_init_with_config(self) -> None:
        """Watcher initializes with config."""
        config = WatcherConfig(recursive=False)
        watcher = KgentWatcher(config=config)
        assert watcher.config.recursive is False

    def test_init_with_project_root(self) -> None:
        """Watcher initializes with project root."""
        watcher = KgentWatcher(project_root="/tmp")
        assert watcher.config.project_root == Path("/tmp")

    def test_subscribe_unsubscribe(self) -> None:
        """Can subscribe and unsubscribe callbacks."""
        watcher = KgentWatcher()
        notifications: list[WatchNotification] = []

        def callback(n: WatchNotification) -> None:
            notifications.append(n)

        watcher.subscribe(callback)
        assert callback in watcher._callbacks

        watcher.unsubscribe(callback)
        assert callback not in watcher._callbacks

    def test_should_ignore(self) -> None:
        """Ignores files matching patterns."""
        watcher = KgentWatcher()

        # Should ignore
        assert watcher._should_ignore("foo.pyc") is True
        assert watcher._should_ignore("/path/to/__pycache__/foo.py") is True
        assert watcher._should_ignore("/path/to/.git/config") is True

        # Should not ignore
        assert watcher._should_ignore("module.py") is False

    def test_is_debounced(self) -> None:
        """Debouncing works."""
        watcher = KgentWatcher()
        watcher.config.debounce_seconds = 0.1

        # First call is not debounced
        assert watcher._is_debounced("foo.py") is False

        # Immediate second call is debounced
        assert watcher._is_debounced("foo.py") is True

    def test_handle_file_change_triggers_heuristics(self) -> None:
        """File changes trigger heuristics and emit notifications."""
        watcher = KgentWatcher()
        notifications: list[WatchNotification] = []

        def callback(n: WatchNotification) -> None:
            notifications.append(n)

        watcher.subscribe(callback)

        # Create a file with an undocumented function
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "module.py"
            path.write_text(
                """
def undocumented_function():
    return 42
"""
            )

            watcher._handle_file_change(str(path))

            # Should have triggered docs heuristic (and possibly tests)
            assert len(notifications) > 0
            assert any(n.heuristic == "docs" for n in notifications)

    @pytest.mark.asyncio
    async def test_start_stop(self) -> None:
        """Can start and stop the watcher."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WatcherConfig(project_root=Path(tmpdir))
            watcher = KgentWatcher(config=config)

            await watcher.start()
            assert watcher.running is True

            await watcher.stop()
            assert watcher.running is False

    def test_recent_notifications(self) -> None:
        """Can get recent notifications."""
        watcher = KgentWatcher()

        # Add some notifications
        from datetime import datetime, timezone

        for i in range(15):
            watcher._notifications.append(
                WatchNotification(
                    timestamp=datetime.now(timezone.utc),
                    heuristic="test",
                    message=f"Message {i}",
                    severity="info",
                    file_path=f"file_{i}.py",
                )
            )

        recent = watcher.recent_notifications(limit=5)
        assert len(recent) == 5
        # Should be the last 5
        assert recent[0].message == "Message 10"

    def test_clear_notifications(self) -> None:
        """Can clear notifications."""
        watcher = KgentWatcher()

        from datetime import datetime, timezone

        watcher._notifications.append(
            WatchNotification(
                timestamp=datetime.now(timezone.utc),
                heuristic="test",
                message="Test",
                severity="info",
                file_path="test.py",
            )
        )

        assert len(watcher.notifications) == 1
        watcher.clear_notifications()
        assert len(watcher.notifications) == 0


class TestHeuristicResult:
    """Tests for HeuristicResult dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        result = HeuristicResult(triggered=False)
        assert result.triggered is False
        assert result.message == ""
        assert result.severity == "info"

    def test_triggered_result(self) -> None:
        """Triggered result has message."""
        result = HeuristicResult(
            triggered=True,
            message="Function too complex",
            severity="suggestion",
        )
        assert result.triggered is True
        assert "complex" in result.message
