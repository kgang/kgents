"""
Tests for FileEditGuard and file I/O primitives.

CLI v7 Phase 1: File I/O Primitives

Test categories (per test-patterns.md T-gent taxonomy):
- Type I (Unit): Contracts, guard creation, error types
- Type II (Integration): Read + Edit workflow
- Type III (Property): Cache behavior, edit consistency
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from services.conductor.contracts import (
    EditError,
    FileCacheEntry,
    FileEditRequest,
    FileReadRequest,
    FileWriteRequest,
)
from services.conductor.file_guard import (
    FileChangedError,
    FileEditGuard,
    FileGuardError,
    NotReadError,
    StringNotFoundError,
    StringNotUniqueError,
    get_file_guard,
    reset_file_guard,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_file() -> Path:
    """Create a temporary file with test content."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def foo():\n    return 'hello'\n\ndef bar():\n    return 'world'\n")
        return Path(f.name)


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def guard() -> FileEditGuard:
    """Create a fresh FileEditGuard for testing."""
    return FileEditGuard()


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset the singleton guard before each test."""
    reset_file_guard()


# =============================================================================
# Type I: Unit Tests - Contracts
# =============================================================================


class TestContracts:
    """Unit tests for contract data classes."""

    def test_file_read_request_defaults(self) -> None:
        """FileReadRequest has sensible defaults."""
        request = FileReadRequest(path="test.py")
        assert request.path == "test.py"
        assert request.encoding == "utf-8"
        assert request.start_line is None
        assert request.end_line is None

    def test_file_edit_request_required_fields(self) -> None:
        """FileEditRequest requires path, old_string, new_string."""
        request = FileEditRequest(
            path="test.py",
            old_string="foo",
            new_string="bar",
        )
        assert request.path == "test.py"
        assert request.old_string == "foo"
        assert request.new_string == "bar"
        assert request.replace_all is False

    def test_file_write_request_defaults(self) -> None:
        """FileWriteRequest has sensible defaults."""
        request = FileWriteRequest(path="test.py", content="print('hello')")
        assert request.encoding == "utf-8"
        assert request.create_dirs is True

    def test_file_cache_entry_freshness(self) -> None:
        """FileCacheEntry freshness check works."""
        from datetime import datetime, timedelta

        entry = FileCacheEntry(
            path="/test.py",
            content_hash="abc123",
            mtime=1234567890.0,
            cached_at=datetime.now() - timedelta(seconds=60),
            size=100,
            lines=10,
        )

        # Fresh within 5 minutes
        assert entry.is_fresh(max_age_seconds=300) is True

        # Stale after 30 seconds
        assert entry.is_fresh(max_age_seconds=30) is False

    def test_file_cache_entry_serialization(self) -> None:
        """FileCacheEntry can be serialized to dict."""
        from datetime import datetime

        entry = FileCacheEntry(
            path="/test.py",
            content_hash="abc123",
            mtime=1234567890.0,
            cached_at=datetime.now(),
            size=100,
            lines=10,
        )

        data = entry.to_dict()
        assert data["path"] == "/test.py"
        assert data["content_hash"] == "abc123"
        assert "cached_at" in data


class TestErrorTypes:
    """Unit tests for error types."""

    def test_not_read_error(self) -> None:
        """NotReadError provides helpful suggestion."""
        error = NotReadError("/path/to/file.py")
        assert error.error_type == EditError.NOT_READ
        assert "/path/to/file.py" in error.message
        assert "world.file.read" in error.suggestion

    def test_string_not_found_error(self) -> None:
        """StringNotFoundError provides helpful message."""
        error = StringNotFoundError("/file.py", "def missing_func")
        assert error.error_type == EditError.NOT_FOUND
        assert "def missing_func" in error.message

    def test_string_not_found_error_truncates_long_strings(self) -> None:
        """StringNotFoundError truncates very long old_string."""
        long_string = "x" * 100
        error = StringNotFoundError("/file.py", long_string)
        assert "..." in error.message
        assert len(error.message) < 200

    def test_string_not_unique_error(self) -> None:
        """StringNotUniqueError shows occurrence count."""
        error = StringNotUniqueError("/file.py", "return", 5)
        assert error.error_type == EditError.NOT_UNIQUE
        assert "5 times" in error.message
        assert "replace_all" in error.suggestion

    def test_file_changed_error(self) -> None:
        """FileChangedError suggests re-reading."""
        error = FileChangedError("/file.py")
        assert error.error_type == EditError.FILE_CHANGED
        assert "world.file.read" in error.suggestion


# =============================================================================
# Type I: Unit Tests - Guard Creation
# =============================================================================


class TestGuardCreation:
    """Unit tests for FileEditGuard creation."""

    def test_create_guard_with_defaults(self) -> None:
        """Guard creates with default configuration."""
        guard = FileEditGuard()
        assert guard.cache_ttl_seconds == 300.0
        assert guard.max_cached_files == 100

    def test_create_guard_with_custom_config(self) -> None:
        """Guard accepts custom configuration."""
        guard = FileEditGuard(
            cache_ttl_seconds=60.0,
            max_cached_files=10,
        )
        assert guard.cache_ttl_seconds == 60.0
        assert guard.max_cached_files == 10

    def test_singleton_accessor(self) -> None:
        """Singleton accessor returns same instance."""
        guard1 = get_file_guard()
        guard2 = get_file_guard()
        assert guard1 is guard2

    def test_singleton_reset(self) -> None:
        """Singleton can be reset."""
        guard1 = get_file_guard()
        reset_file_guard()
        guard2 = get_file_guard()
        assert guard1 is not guard2


# =============================================================================
# Type II: Integration Tests - Read Operations
# =============================================================================


class TestReadOperations:
    """Integration tests for file read operations."""

    @pytest.mark.asyncio
    async def test_read_file_returns_content(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Reading a file returns its content."""
        response = await guard.read_file(str(temp_file))

        assert response.path == str(temp_file)
        assert "def foo" in response.content
        assert response.size > 0
        assert response.lines > 0

    @pytest.mark.asyncio
    async def test_read_file_caches_entry(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Reading caches the file for subsequent edits."""
        await guard.read_file(str(temp_file))

        can_edit = await guard.can_edit(str(temp_file))
        assert can_edit is True

    @pytest.mark.asyncio
    async def test_read_file_not_found(self, guard: FileEditGuard) -> None:
        """Reading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            await guard.read_file("/nonexistent/file.py")

    @pytest.mark.asyncio
    async def test_read_file_with_string_path(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Read accepts string path directly."""
        response = await guard.read_file(str(temp_file))
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_read_file_with_request_object(
        self, temp_file: Path, guard: FileEditGuard
    ) -> None:
        """Read accepts FileReadRequest object."""
        request = FileReadRequest(path=str(temp_file))
        response = await guard.read_file(request)
        assert response.content is not None

    @pytest.mark.asyncio
    async def test_read_file_partial_range(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Read supports line range for partial reads."""
        request = FileReadRequest(
            path=str(temp_file),
            start_line=0,
            end_line=2,
        )
        response = await guard.read_file(request)

        assert response.truncated is True
        lines = response.content.split("\n")
        assert len(lines) == 2


# =============================================================================
# Type II: Integration Tests - Edit Operations
# =============================================================================


class TestEditOperations:
    """Integration tests for file edit operations."""

    @pytest.mark.asyncio
    async def test_edit_requires_prior_read(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit fails if file wasn't read first."""
        request = FileEditRequest(
            path=str(temp_file),
            old_string="def foo",
            new_string="def bar",
        )

        response = await guard.edit_file(request)

        assert response.success is False
        assert response.error == EditError.NOT_READ

    @pytest.mark.asyncio
    async def test_edit_after_read_succeeds(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit succeeds after reading the file."""
        # Read first
        await guard.read_file(str(temp_file))

        # Then edit
        request = FileEditRequest(
            path=str(temp_file),
            old_string="def foo",
            new_string="def renamed_foo",
        )
        response = await guard.edit_file(request)

        assert response.success is True
        assert response.replacements == 1

        # Verify the file was actually changed
        content = temp_file.read_text()
        assert "def renamed_foo" in content
        assert "def foo" not in content

    @pytest.mark.asyncio
    async def test_edit_string_not_found(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit fails if old_string not found."""
        await guard.read_file(str(temp_file))

        request = FileEditRequest(
            path=str(temp_file),
            old_string="nonexistent_function",
            new_string="replacement",
        )
        response = await guard.edit_file(request)

        assert response.success is False
        assert response.error == EditError.NOT_FOUND

    @pytest.mark.asyncio
    async def test_edit_string_not_unique(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit fails if old_string appears multiple times."""
        # Write file with duplicate pattern
        temp_file.write_text("return 1\nreturn 2\nreturn 3\n")
        await guard.read_file(str(temp_file))

        request = FileEditRequest(
            path=str(temp_file),
            old_string="return",
            new_string="yield",
        )
        response = await guard.edit_file(request)

        assert response.success is False
        assert response.error == EditError.NOT_UNIQUE

    @pytest.mark.asyncio
    async def test_edit_replace_all(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit with replace_all replaces all occurrences."""
        # Write file with duplicate pattern
        temp_file.write_text("return 1\nreturn 2\nreturn 3\n")
        await guard.read_file(str(temp_file))

        request = FileEditRequest(
            path=str(temp_file),
            old_string="return",
            new_string="yield",
            replace_all=True,
        )
        response = await guard.edit_file(request)

        assert response.success is True
        assert response.replacements == 3

        content = temp_file.read_text()
        assert content.count("yield") == 3
        assert content.count("return") == 0

    @pytest.mark.asyncio
    async def test_edit_generates_diff_preview(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit returns a diff preview."""
        await guard.read_file(str(temp_file))

        request = FileEditRequest(
            path=str(temp_file),
            old_string="def foo",
            new_string="def bar",
        )
        response = await guard.edit_file(request)

        assert response.success is True
        assert "-def foo" in response.diff_preview or "def foo" in response.diff_preview
        assert "+def bar" in response.diff_preview or "def bar" in response.diff_preview


# =============================================================================
# Type II: Integration Tests - Write Operations
# =============================================================================


class TestWriteOperations:
    """Integration tests for file write operations."""

    @pytest.mark.asyncio
    async def test_write_creates_new_file(self, temp_dir: Path, guard: FileEditGuard) -> None:
        """Write creates a new file."""
        new_file = temp_dir / "new_file.py"

        request = FileWriteRequest(
            path=str(new_file),
            content="print('hello world')",
        )
        response = await guard.write_file(request)

        assert response.success is True
        assert response.size == len("print('hello world')")
        assert new_file.exists()
        assert new_file.read_text() == "print('hello world')"

    @pytest.mark.asyncio
    async def test_write_creates_parent_dirs(self, temp_dir: Path, guard: FileEditGuard) -> None:
        """Write creates parent directories if needed."""
        nested_file = temp_dir / "a" / "b" / "c" / "file.py"

        request = FileWriteRequest(
            path=str(nested_file),
            content="# nested",
            create_dirs=True,
        )
        response = await guard.write_file(request)

        assert response.success is True
        assert nested_file.exists()


# =============================================================================
# Type III: Property Tests - Cache Behavior
# =============================================================================


class TestCacheBehavior:
    """Property tests for cache behavior."""

    @pytest.mark.asyncio
    async def test_cache_eviction_on_overflow(self, guard: FileEditGuard) -> None:
        """Cache evicts oldest entries when full."""
        guard.max_cached_files = 3

        # Create and read 5 files
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(5):
                f = Path(tmpdir) / f"file{i}.py"
                f.write_text(f"# file {i}")
                files.append(f)
                await guard.read_file(str(f))
                await asyncio.sleep(0.01)  # Ensure different cached_at times

            # Only 3 should be cached
            stats = guard.get_statistics()
            assert stats["cache_size"] == 3

    @pytest.mark.asyncio
    async def test_cache_invalidation(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Cache can be invalidated."""
        await guard.read_file(str(temp_file))
        assert await guard.can_edit(str(temp_file)) is True

        await guard.invalidate(str(temp_file))
        assert await guard.can_edit(str(temp_file)) is False

    @pytest.mark.asyncio
    async def test_cache_clear(self, guard: FileEditGuard) -> None:
        """Cache can be cleared entirely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                f = Path(tmpdir) / f"file{i}.py"
                f.write_text(f"# file {i}")
                await guard.read_file(str(f))

            stats = guard.get_statistics()
            assert stats["cache_size"] == 3

            count = await guard.clear_cache()
            assert count == 3

            stats = guard.get_statistics()
            assert stats["cache_size"] == 0


# =============================================================================
# Type III: Property Tests - File Changed Detection
# =============================================================================


class TestFileChangedDetection:
    """Property tests for detecting external file changes."""

    @pytest.mark.asyncio
    async def test_edit_fails_if_file_changed(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Edit fails if file was modified since read."""
        # Read the file
        await guard.read_file(str(temp_file))

        # Modify the file externally (simulating another process)
        import time

        time.sleep(0.01)  # Ensure different mtime
        temp_file.write_text("# completely different content")

        # Attempt edit
        request = FileEditRequest(
            path=str(temp_file),
            old_string="def foo",
            new_string="def bar",
        )
        response = await guard.edit_file(request)

        assert response.success is False
        assert response.error == EditError.FILE_CHANGED


# =============================================================================
# Type IV: Performance Tests
# =============================================================================


class TestPerformance:
    """Performance baseline tests."""

    @pytest.mark.asyncio
    async def test_read_performance(self, guard: FileEditGuard) -> None:
        """Read should complete in reasonable time."""
        import time

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Write 1000 lines
            for i in range(1000):
                f.write(f"# Line {i}\n")
            path = f.name

        start = time.time()
        await guard.read_file(path)
        elapsed = time.time() - start

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Read took {elapsed:.3f}s, expected < 0.1s"

    @pytest.mark.asyncio
    async def test_edit_performance(self, guard: FileEditGuard) -> None:
        """Edit should complete in reasonable time."""
        import time

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            for i in range(1000):
                f.write(f"def func_{i}():\n    pass\n")
            path = f.name

        await guard.read_file(path)

        request = FileEditRequest(
            path=path,
            old_string="def func_500",
            new_string="def renamed_500",
        )

        start = time.time()
        response = await guard.edit_file(request)
        elapsed = time.time() - start

        assert response.success is True
        # Should complete in under 100ms
        assert elapsed < 0.1, f"Edit took {elapsed:.3f}s, expected < 0.1s"


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for guard statistics."""

    @pytest.mark.asyncio
    async def test_statistics_tracking(self, temp_file: Path, guard: FileEditGuard) -> None:
        """Statistics are tracked correctly."""
        # Initial stats
        stats = guard.get_statistics()
        assert stats["reads"] == 0
        assert stats["edits"] == 0

        # After read
        await guard.read_file(str(temp_file))
        stats = guard.get_statistics()
        assert stats["reads"] == 1

        # After edit
        request = FileEditRequest(
            path=str(temp_file),
            old_string="def foo",
            new_string="def bar",
        )
        await guard.edit_file(request)
        stats = guard.get_statistics()
        assert stats["edits"] == 1
