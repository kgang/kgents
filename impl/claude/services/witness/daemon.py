"""
Witness Daemon: Background Process for Continuous Observation.

The Witness daemon runs as a background process, watching for git events
and communicating with the AGENTESE gateway to capture thoughts.

Architecture:
    kg witness start
        └── spawns subprocess: python -m services.witness.daemon
            └── writes PID to ~/.kgents/witness.pid
            └── starts GitWatcher
            └── sends thoughts to AGENTESE gateway
            └── listens for SIGTERM to gracefully stop

Integration:
    - PID file: ~/.kgents/witness.pid
    - Logs: ~/.kgents/witness.log
    - Gateway: http://localhost:8000/agentese/self/witness/capture

Key Principle (from crown-jewel-patterns.md):
    "Container Owns Workflow" - The daemon owns the GitWatcher lifecycle.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging before other imports
LOG_DIR = Path.home() / ".kgents"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "witness.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("witness.daemon")


# =============================================================================
# PID File Management
# =============================================================================


@dataclass
class DaemonConfig:
    """Configuration for the witness daemon."""

    pid_file: Path = field(default_factory=lambda: Path.home() / ".kgents" / "witness.pid")
    gateway_url: str = field(
        default_factory=lambda: os.environ.get("KGENTS_GATEWAY_URL", "http://localhost:8000")
    )
    poll_interval: float = 5.0
    repo_path: Path | None = None


def read_pid_file(pid_file: Path) -> int | None:
    """Read PID from file, return None if not exists or invalid."""
    if not pid_file.exists():
        return None
    try:
        pid = int(pid_file.read_text().strip())
        return pid
    except (ValueError, OSError):
        return None


def write_pid_file(pid_file: Path, pid: int) -> None:
    """Write PID to file."""
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(pid))
    logger.info(f"PID file written: {pid_file} (PID: {pid})")


def remove_pid_file(pid_file: Path) -> None:
    """Remove PID file if it exists."""
    if pid_file.exists():
        pid_file.unlink()
        logger.info(f"PID file removed: {pid_file}")


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running."""
    try:
        os.kill(pid, 0)  # Signal 0 checks existence without killing
        return True
    except OSError:
        return False


def check_daemon_status(config: DaemonConfig | None = None) -> tuple[bool, int | None]:
    """
    Check if the daemon is running.

    Returns:
        (is_running, pid) tuple
    """
    if config is None:
        config = DaemonConfig()

    pid = read_pid_file(config.pid_file)
    if pid is None:
        return False, None

    if is_process_running(pid):
        return True, pid

    # Stale PID file - process no longer running
    remove_pid_file(config.pid_file)
    return False, None


# =============================================================================
# Daemon Process
# =============================================================================


class WitnessDaemon:
    """
    Background daemon for witness observation.

    Manages:
    - GitWatcher lifecycle
    - AGENTESE gateway communication
    - Signal handling for graceful shutdown
    """

    def __init__(self, config: DaemonConfig | None = None) -> None:
        self.config = config or DaemonConfig()
        self._stop_event = asyncio.Event()
        self._watcher: Any = None  # GitWatcher
        self._running = False

        # Stats
        self.started_at: datetime | None = None
        self.thoughts_sent: int = 0
        self.errors: int = 0

    async def start(self) -> None:
        """Start the daemon and begin watching."""
        if self._running:
            logger.warning("Daemon already running")
            return

        # Write PID file
        write_pid_file(self.config.pid_file, os.getpid())

        # Setup signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_signal)

        self._running = True
        self.started_at = datetime.now()

        logger.info(f"Witness daemon starting (PID: {os.getpid()})")
        logger.info(f"Gateway: {self.config.gateway_url}")
        logger.info(f"Repo: {self.config.repo_path or 'current directory'}")

        try:
            await self._run()
        finally:
            await self._cleanup()

    async def _run(self) -> None:
        """Main daemon loop."""
        from services.witness.polynomial import GitEvent, Thought
        from services.witness.watchers.git import create_git_watcher

        # Create GitWatcher
        self._watcher = create_git_watcher(
            repo_path=self.config.repo_path,
            poll_interval=self.config.poll_interval,
        )

        # Start watching
        await self._watcher.start()
        logger.info("GitWatcher started")

        # Process events until stop signal
        while not self._stop_event.is_set():
            try:
                events = await asyncio.wait_for(
                    self._watcher._check_changes(),
                    timeout=self.config.poll_interval,
                )

                for event in events:
                    thought = self._event_to_thought(event)
                    await self._send_thought(thought)
                    logger.info(f"Captured: {thought.content[:60]}...")

            except asyncio.TimeoutError:
                pass  # Normal timeout, check stop event
            except Exception as e:
                logger.error(f"Error in watch loop: {e}")
                self.errors += 1
                await asyncio.sleep(1.0)  # Brief pause on error

    def _event_to_thought(self, event: Any) -> Any:
        """Convert a GitEvent to a Thought."""
        from services.witness.polynomial import Thought

        tags: tuple[str, ...]
        if event.event_type == "commit":
            content = f"Noticed commit {event.sha[:8]}: {event.message or 'no message'}"
            tags = ("git", "commit")
        elif event.event_type == "checkout":
            content = f"Switched to branch {event.branch}"
            tags = ("git", "checkout")
        elif event.event_type == "push":
            content = f"Pushed to {event.branch}"
            tags = ("git", "push")
        elif event.event_type == "merge":
            content = f"Merged into {event.branch}"
            tags = ("git", "merge")
        else:
            content = f"Git event: {event.event_type}"
            tags = ("git",)

        return Thought(
            content=content,
            source="git",
            tags=tags,
        )

    async def _send_thought(self, thought: Any) -> None:
        """Send a thought to the AGENTESE gateway."""
        try:
            import httpx

            url = f"{self.config.gateway_url}/agentese/self/witness/capture"
            payload = {
                "content": thought.content,
                "source": thought.source,
                "tags": list(thought.tags),
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    self.thoughts_sent += 1
                    logger.debug(f"Thought sent successfully: {thought.content[:40]}")
                else:
                    logger.warning(f"Gateway responded with {response.status_code}")
                    self.errors += 1

        except ImportError:
            # httpx not available, log locally
            logger.info(f"[LOCAL] Thought: {thought.content}")
            self.thoughts_sent += 1
        except Exception as e:
            logger.error(f"Failed to send thought: {e}")
            self.errors += 1

    def _handle_signal(self) -> None:
        """Handle shutdown signals."""
        logger.info("Received shutdown signal")
        self._stop_event.set()

    async def _cleanup(self) -> None:
        """Cleanup resources on shutdown."""
        logger.info("Daemon shutting down...")

        # Stop watcher
        if self._watcher:
            await self._watcher.stop()
            logger.info("GitWatcher stopped")

        # Remove PID file
        remove_pid_file(self.config.pid_file)

        self._running = False

        # Log final stats
        uptime = (datetime.now() - self.started_at).total_seconds() if self.started_at else 0
        logger.info(
            f"Daemon stopped. Uptime: {uptime:.1f}s, "
            f"Thoughts: {self.thoughts_sent}, Errors: {self.errors}"
        )

    @property
    def is_running(self) -> bool:
        """Check if daemon is running."""
        return self._running


# =============================================================================
# Control Functions (for CLI integration)
# =============================================================================


def start_daemon(config: DaemonConfig | None = None) -> int:
    """
    Start the witness daemon in a background process.

    Returns:
        PID of the spawned daemon process
    """
    import subprocess

    if config is None:
        config = DaemonConfig()

    # Check if already running
    is_running, existing_pid = check_daemon_status(config)
    if is_running:
        logger.info(f"Daemon already running (PID: {existing_pid})")
        return existing_pid  # type: ignore

    # Spawn daemon as subprocess
    env = os.environ.copy()
    if config.repo_path:
        env["KGENTS_WITNESS_REPO"] = str(config.repo_path)

    # Run the daemon module
    proc = subprocess.Popen(
        [sys.executable, "-m", "services.witness.daemon"],
        start_new_session=True,  # Detach from parent
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
        cwd=str(config.repo_path) if config.repo_path else None,
    )

    # Wait briefly for PID file to be written
    import time

    for _ in range(10):
        pid = read_pid_file(config.pid_file)
        if pid is not None:
            return pid
        time.sleep(0.1)

    # Return subprocess PID as fallback
    return proc.pid


def stop_daemon(config: DaemonConfig | None = None) -> bool:
    """
    Stop the witness daemon.

    Returns:
        True if daemon was stopped, False if not running
    """
    if config is None:
        config = DaemonConfig()

    is_running, pid = check_daemon_status(config)
    if not is_running or pid is None:
        logger.info("Daemon not running")
        return False

    # Send SIGTERM
    try:
        os.kill(pid, signal.SIGTERM)
        logger.info(f"Sent SIGTERM to PID {pid}")

        # Wait for process to exit
        import time

        for _ in range(50):  # 5 seconds timeout
            if not is_process_running(pid):
                break
            time.sleep(0.1)

        # Force kill if still running
        if is_process_running(pid):
            logger.warning(f"Process {pid} didn't exit gracefully, sending SIGKILL")
            os.kill(pid, signal.SIGKILL)

        # Cleanup PID file
        remove_pid_file(config.pid_file)
        return True

    except OSError as e:
        logger.error(f"Failed to stop daemon: {e}")
        return False


def get_daemon_status(config: DaemonConfig | None = None) -> dict[str, Any]:
    """
    Get daemon status information.

    Returns:
        Dict with status information
    """
    if config is None:
        config = DaemonConfig()

    is_running, pid = check_daemon_status(config)

    return {
        "running": is_running,
        "pid": pid,
        "pid_file": str(config.pid_file),
        "log_file": str(LOG_FILE),
        "gateway_url": config.gateway_url,
    }


# =============================================================================
# Main Entry Point
# =============================================================================


async def main() -> None:
    """Main entry point for daemon process."""
    # Get repo path from environment if set
    repo_path_str = os.environ.get("KGENTS_WITNESS_REPO")
    repo_path = Path(repo_path_str) if repo_path_str else None

    config = DaemonConfig(repo_path=repo_path)
    daemon = WitnessDaemon(config)
    await daemon.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by keyboard")
    except Exception as e:
        logger.error(f"Daemon crashed: {e}")
        sys.exit(1)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WitnessDaemon",
    "DaemonConfig",
    "start_daemon",
    "stop_daemon",
    "check_daemon_status",
    "get_daemon_status",
    "read_pid_file",
    "write_pid_file",
    "remove_pid_file",
    "is_process_running",
]
