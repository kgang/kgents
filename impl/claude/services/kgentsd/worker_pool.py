"""
Worker Pool Manager for kgentsd Daemon.

Provides multi-processing and multi-threading support for concurrent
command execution, balancing CPU-bound and I/O-bound workloads.

Architecture:
    ProcessPool: For CPU-bound tasks (LLM inference, crystallization)
    ThreadPool:  For I/O-bound tasks (database, file operations)
    AsyncPool:   For async operations (socket I/O, event streaming)

Key Design Decisions:
1. Process pool uses multiprocessing for true parallelism (GIL bypass)
2. Thread pool for I/O where async isn't appropriate
3. Graceful degradation if pools can't be created
4. Pool sizes scale with CPU count but cap for stability

"Container Owns Workflow" - The daemon owns all pool lifecycles.

See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

import asyncio
import logging
import multiprocessing as mp
import os
import queue
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, TypeVar

logger = logging.getLogger("kgentsd.workers")

T = TypeVar("T")


# =============================================================================
# Configuration
# =============================================================================


class TaskType(Enum):
    """Task classification for pool routing."""
    CPU_BOUND = auto()   # LLM, crystallization, heavy computation
    IO_BOUND = auto()    # Database, file I/O, network
    ASYNC = auto()       # Async coroutines (no pool, runs in event loop)


@dataclass
class PoolConfig:
    """Configuration for worker pools."""

    # Process pool for CPU-bound work
    max_processes: int = field(default_factory=lambda: min(mp.cpu_count(), 4))

    # Thread pool for I/O-bound work
    max_threads: int = field(default_factory=lambda: min(mp.cpu_count() * 2, 16))

    # Task queue limits
    max_queue_size: int = 100

    # Timeouts
    task_timeout: float = 300.0  # 5 minutes default
    shutdown_timeout: float = 30.0  # 30 seconds for graceful shutdown

    # Pool warmup (pre-create workers)
    warmup_workers: bool = True

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_processes < 1:
            self.max_processes = 1
        if self.max_threads < 1:
            self.max_threads = 1


# =============================================================================
# Task Wrappers
# =============================================================================


@dataclass
class Task:
    """A task to be executed by a worker pool."""

    id: str
    func: Callable[..., T]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    task_type: TaskType = TaskType.IO_BOUND
    timeout: float | None = None

    def __post_init__(self) -> None:
        if self.timeout is None:
            self.timeout = 300.0


@dataclass
class TaskResult:
    """Result of a task execution."""

    task_id: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: int = 0


# =============================================================================
# Process Pool Wrapper
# =============================================================================


def _run_in_process(func: Callable[..., T], args: tuple[Any, ...], kwargs: dict[str, Any]) -> T:
    """
    Wrapper function for process pool execution.

    This function runs in a separate process and must be picklable.
    """
    return func(*args, **kwargs)


class ProcessPoolManager:
    """
    Manages a pool of worker processes for CPU-bound tasks.

    Uses multiprocessing.ProcessPoolExecutor for true parallelism,
    bypassing the GIL for compute-intensive operations.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self._executor: ProcessPoolExecutor | None = None
        self._lock = threading.Lock()
        self._active_tasks: dict[str, asyncio.Future[Any]] = {}

    def start(self) -> None:
        """Start the process pool."""
        with self._lock:
            if self._executor is None:
                try:
                    self._executor = ProcessPoolExecutor(
                        max_workers=self.max_workers,
                        mp_context=mp.get_context("spawn"),  # Safer for macOS
                    )
                    logger.info(f"Process pool started with {self.max_workers} workers")
                except Exception as e:
                    logger.warning(f"Could not start process pool: {e}")
                    # Will fall back to thread pool

    def stop(self, wait: bool = True, timeout: float = 30.0) -> None:
        """Stop the process pool gracefully."""
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None
                logger.info("Process pool stopped")

    async def submit(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout: float = 300.0,
        **kwargs: Any,
    ) -> T:
        """
        Submit a CPU-bound task to the process pool.

        The function must be picklable (defined at module level, no closures).
        """
        if self._executor is None:
            # Fallback to running in thread if no process pool
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                timeout=timeout,
            )

        loop = asyncio.get_event_loop()

        # Submit to process pool
        future = loop.run_in_executor(
            self._executor,
            _run_in_process,
            func,
            args,
            kwargs,
        )

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Process task timed out after {timeout}s")
            raise

    @property
    def is_running(self) -> bool:
        """Check if pool is running."""
        return self._executor is not None


# =============================================================================
# Thread Pool Wrapper
# =============================================================================


class ThreadPoolManager:
    """
    Manages a pool of worker threads for I/O-bound tasks.

    Uses concurrent.futures.ThreadPoolExecutor for operations
    that are I/O-bound but not async (e.g., synchronous libraries).
    """

    def __init__(self, max_workers: int = 8) -> None:
        self.max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the thread pool."""
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix="kgentsd-worker",
                )
                logger.info(f"Thread pool started with {self.max_workers} workers")

    def stop(self, wait: bool = True, timeout: float = 30.0) -> None:
        """Stop the thread pool gracefully."""
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None
                logger.info("Thread pool stopped")

    async def submit(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout: float = 300.0,
        **kwargs: Any,
    ) -> T:
        """Submit an I/O-bound task to the thread pool."""
        if self._executor is None:
            self.start()

        loop = asyncio.get_event_loop()

        # Wrap the function call
        def wrapped() -> T:
            return func(*args, **kwargs)

        future = loop.run_in_executor(self._executor, wrapped)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Thread task timed out after {timeout}s")
            raise

    def submit_sync(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Submit synchronously and wait for result."""
        if self._executor is None:
            self.start()

        # After start(), executor is guaranteed to be non-None
        assert self._executor is not None
        future = self._executor.submit(func, *args, **kwargs)
        return future.result()

    @property
    def is_running(self) -> bool:
        """Check if pool is running."""
        return self._executor is not None


# =============================================================================
# Unified Worker Pool Manager
# =============================================================================


class WorkerPoolManager:
    """
    Unified manager for all worker pools.

    Provides a single interface for submitting tasks, automatically
    routing to the appropriate pool based on task type.

    Usage:
        async with WorkerPoolManager() as pool:
            # CPU-bound work (process pool)
            result = await pool.cpu_bound(expensive_computation, arg1, arg2)

            # I/O-bound work (thread pool)
            result = await pool.io_bound(database_query, query="...")

            # Async work (event loop)
            result = await pool.async_task(async_function())
    """

    def __init__(self, config: PoolConfig | None = None) -> None:
        self.config = config or PoolConfig()

        self._process_pool = ProcessPoolManager(self.config.max_processes)
        self._thread_pool = ThreadPoolManager(self.config.max_threads)

        self._started = False
        self._stats = {
            "cpu_tasks": 0,
            "io_tasks": 0,
            "async_tasks": 0,
            "errors": 0,
        }

    async def start(self) -> None:
        """Start all worker pools."""
        if self._started:
            return

        self._thread_pool.start()
        self._process_pool.start()

        self._started = True
        logger.info(
            f"Worker pools started: processes={self.config.max_processes}, "
            f"threads={self.config.max_threads}"
        )

    async def stop(self) -> None:
        """Stop all worker pools gracefully."""
        if not self._started:
            return

        self._process_pool.stop(wait=True, timeout=self.config.shutdown_timeout)
        self._thread_pool.stop(wait=True, timeout=self.config.shutdown_timeout)

        self._started = False
        logger.info("Worker pools stopped")
        logger.info(f"Pool stats: {self._stats}")

    async def __aenter__(self) -> WorkerPoolManager:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    async def cpu_bound(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute a CPU-bound task in the process pool.

        Use for: LLM inference, crystallization, heavy computation.

        Note: func must be picklable (module-level function, no closures).
        """
        self._stats["cpu_tasks"] += 1
        timeout = timeout or self.config.task_timeout

        try:
            return await self._process_pool.submit(func, *args, timeout=timeout, **kwargs)
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"CPU-bound task failed: {e}")
            raise

    async def io_bound(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute an I/O-bound task in the thread pool.

        Use for: Database queries, file I/O, synchronous network calls.
        """
        self._stats["io_tasks"] += 1
        timeout = timeout or self.config.task_timeout

        try:
            return await self._thread_pool.submit(func, *args, timeout=timeout, **kwargs)
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"I/O-bound task failed: {e}")
            raise

    async def async_task(
        self,
        coro: Awaitable[T],
        timeout: float | None = None,
    ) -> T:
        """
        Execute an async task directly in the event loop.

        Use for: Async I/O, async network calls, event streaming.
        """
        self._stats["async_tasks"] += 1
        timeout = timeout or self.config.task_timeout

        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Async task failed: {e}")
            raise

    def sync_io_bound(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute an I/O-bound task synchronously.

        Use when: Already in sync context but need thread pool benefits.
        """
        self._stats["io_tasks"] += 1
        return self._thread_pool.submit_sync(func, *args, **kwargs)

    @property
    def stats(self) -> dict[str, int]:
        """Get pool statistics."""
        return dict(self._stats)

    @property
    def is_running(self) -> bool:
        """Check if pools are running."""
        return self._started


# =============================================================================
# Singleton Instance
# =============================================================================


_global_pool: WorkerPoolManager | None = None
_pool_lock = threading.Lock()


def get_worker_pool() -> WorkerPoolManager:
    """
    Get the global worker pool manager.

    Creates one if not exists. Thread-safe.
    """
    global _global_pool

    with _pool_lock:
        if _global_pool is None:
            _global_pool = WorkerPoolManager()

    return _global_pool


async def start_worker_pools(config: PoolConfig | None = None) -> WorkerPoolManager:
    """Start the global worker pools with optional custom config."""
    global _global_pool

    with _pool_lock:
        if _global_pool is None:
            _global_pool = WorkerPoolManager(config)

    await _global_pool.start()
    return _global_pool


async def stop_worker_pools() -> None:
    """Stop the global worker pools."""
    global _global_pool

    if _global_pool is not None:
        await _global_pool.stop()
        _global_pool = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TaskType",
    "PoolConfig",
    "Task",
    "TaskResult",
    "ProcessPoolManager",
    "ThreadPoolManager",
    "WorkerPoolManager",
    "get_worker_pool",
    "start_worker_pools",
    "stop_worker_pools",
]
