"""
Daemon Handler: Cortex daemon lifecycle management with Mac launchd integration.

The Cortex daemon is the living brain of kgents. The CLI (Glass Terminal) is just
a hollow shell in front of it. This handler manages the daemon lifecycle.

Usage:
    kgents daemon start     # Start the Cortex daemon
    kgents daemon stop      # Stop the Cortex daemon
    kgents daemon status    # Show daemon status
    kgents daemon restart   # Restart the daemon
    kgents daemon install   # Install launchd service (Mac only, auto-start on login)
    kgents daemon uninstall # Remove launchd service
    kgents daemon logs      # Show daemon logs

Architecture:
    Mac launchd:
        ~/Library/LaunchAgents/io.kgents.cortex.plist

        The plist configures launchd to:
        - Start the daemon on user login
        - Keep it running (restart on crash)
        - Log stdout/stderr to ~/Library/Logs/kgents/

    Manual mode:
        Run the daemon in foreground (useful for development):
        kgents daemon start --foreground

Principle alignment:
    - Transparent Infrastructure: The daemon communicates what it's doing
    - Graceful Degradation: Works without launchd (manual mode)
    - Joy-Inducing: Simple commands, clear feedback
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

# Constants
PLIST_LABEL = "io.kgents.cortex"
PLIST_FILENAME = f"{PLIST_LABEL}.plist"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
LOGS_DIR = Path.home() / "Library" / "Logs" / "kgents"
# 50051 is commonly used by Docker gRPC services, so we use 50052
DEFAULT_PORT = 50052


def cmd_daemon(args: list[str]) -> int:
    """
    Manage the Cortex daemon lifecycle.

    Dispatches to subcommands: start, stop, status, restart, install, uninstall, logs.
    """
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers: dict[str, Callable[[list[str]], int]] = {
        "start": _cmd_start,
        "stop": _cmd_stop,
        "status": _cmd_status,
        "restart": _cmd_restart,
        "install": _cmd_install,
        "uninstall": _cmd_uninstall,
        "logs": _cmd_logs,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Available: start, stop, status, restart, install, uninstall, logs")
        return 1

    return handlers[subcommand](sub_args)


def _cmd_start(args: list[str]) -> int:
    """Start the Cortex daemon."""
    foreground = "--foreground" in args or "-f" in args
    port = _parse_port(args)

    # Check if already running
    status = _get_daemon_status()
    if status["running"]:
        print(f"Daemon already running (PID {status['pid']})")
        return 0

    if foreground:
        # Run in foreground (blocks)
        print(f"Starting Cortex daemon on port {port} (foreground mode)...")
        return _run_foreground(port)
    else:
        # Check if launchd service is installed
        if _is_launchd_installed():
            print("Starting daemon via launchd...")
            return _launchctl("start", PLIST_LABEL)
        else:
            # Start manually in background
            print(f"Starting daemon on port {port}...")
            return _start_background(port)


def _cmd_stop(args: list[str]) -> int:
    """Stop the Cortex daemon."""
    status = _get_daemon_status()

    if not status["running"]:
        print("Daemon not running.")
        return 0

    if _is_launchd_installed():
        print("Stopping daemon via launchd...")
        return _launchctl("stop", PLIST_LABEL)
    else:
        # Kill by PID
        pid = status.get("pid")
        if pid:
            print(f"Stopping daemon (PID {pid})...")
            try:
                os.kill(pid, signal.SIGTERM)
                print("Daemon stopped.")
                return 0
            except ProcessLookupError:
                print("Daemon already stopped.")
                return 0
            except PermissionError:
                print(f"Permission denied to stop PID {pid}")
                return 1
        else:
            print("Cannot determine daemon PID.")
            return 1


def _cmd_status(args: list[str]) -> int:
    """Show daemon status."""
    print("Cortex Daemon Status")
    print("=" * 40)

    status = _get_daemon_status()

    # Daemon status
    if status["running"]:
        print("Status:  RUNNING")
        print(f"PID:     {status.get('pid', 'unknown')}")
    else:
        print("Status:  STOPPED")

    # Port
    print(f"Port:    {DEFAULT_PORT}")

    # Launchd status
    if sys.platform == "darwin":
        if _is_launchd_installed():
            print("Launchd: INSTALLED (auto-start on login)")
        else:
            print("Launchd: NOT INSTALLED")
            print("         Run 'kgents daemon install' to enable auto-start")

    # Health check (if running)
    if status["running"]:
        health = _check_health()
        if health["healthy"]:
            print("\nHealth:  OK")
            if health.get("instance_id"):
                print(f"Instance: {health['instance_id']}")
        else:
            print(f"\nHealth:  DEGRADED ({health.get('error', 'unknown')})")

    return 0


def _cmd_restart(args: list[str]) -> int:
    """Restart the Cortex daemon."""
    print("Restarting daemon...")
    _cmd_stop([])
    import time

    time.sleep(1)
    return _cmd_start(args)


def _cmd_install(args: list[str]) -> int:
    """Install launchd service for auto-start on Mac."""
    if sys.platform != "darwin":
        print("Launchd is only available on macOS.")
        print("On Linux, use systemd instead (not yet implemented).")
        return 1

    if _is_launchd_installed():
        print("Launchd service already installed.")
        print(f"  {LAUNCH_AGENTS_DIR / PLIST_FILENAME}")
        return 0

    print("Installing launchd service...")

    # Ensure directories exist
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate plist
    plist_content = _generate_plist()
    plist_path = LAUNCH_AGENTS_DIR / PLIST_FILENAME

    try:
        plist_path.write_text(plist_content)
        print(f"  Created: {plist_path}")
    except PermissionError:
        print(f"  Permission denied: {plist_path}")
        return 1

    # Load the service
    result = _launchctl("load", str(plist_path))
    if result == 0:
        print("\nLaunchd service installed.")
        print("  The daemon will auto-start on login.")
        print(f"  Logs: {LOGS_DIR}")
        print("\nTo start now:")
        print("  kgents daemon start")
    return result


def _cmd_uninstall(args: list[str]) -> int:
    """Remove launchd service."""
    if sys.platform != "darwin":
        print("Launchd is only available on macOS.")
        return 1

    plist_path = LAUNCH_AGENTS_DIR / PLIST_FILENAME

    if not plist_path.exists():
        print("Launchd service not installed.")
        return 0

    print("Uninstalling launchd service...")

    # Stop the service first
    _launchctl("stop", PLIST_LABEL)

    # Unload the service
    _launchctl("unload", str(plist_path))

    # Remove the plist
    try:
        plist_path.unlink()
        print(f"  Removed: {plist_path}")
    except FileNotFoundError:
        pass
    except PermissionError:
        print(f"  Permission denied: {plist_path}")
        return 1

    print("\nLaunchd service uninstalled.")
    print("  The daemon will no longer auto-start on login.")
    return 0


def _cmd_logs(args: list[str]) -> int:
    """Show daemon logs."""
    follow = "-f" in args or "--follow" in args
    lines = _parse_lines(args, default=50)

    stdout_log = LOGS_DIR / "cortex.stdout.log"
    stderr_log = LOGS_DIR / "cortex.stderr.log"

    if not stdout_log.exists() and not stderr_log.exists():
        print("No logs found.")
        print(f"  Expected at: {LOGS_DIR}")
        return 0

    if follow:
        # Use tail -f
        cmd = ["tail", "-f"]
        if stdout_log.exists():
            cmd.append(str(stdout_log))
        if stderr_log.exists():
            cmd.append(str(stderr_log))

        print("Following logs (Ctrl+C to stop)...")
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print()
        return 0
    else:
        # Show recent logs
        print("Cortex Daemon Logs")
        print("=" * 40)

        if stdout_log.exists():
            print(f"\n[stdout] {stdout_log}")
            result = subprocess.run(
                ["tail", f"-{lines}", str(stdout_log)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout)

        if stderr_log.exists():
            print(f"\n[stderr] {stderr_log}")
            result = subprocess.run(
                ["tail", f"-{lines}", str(stderr_log)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print(result.stdout)

        return 0


# Helper functions


def _get_daemon_status() -> dict[str, Any]:
    """Get the current daemon status."""
    # Try to find the daemon process
    try:
        result = subprocess.run(
            ["pgrep", "-f", "infra.cortex.daemon"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            return {"running": True, "pid": int(pids[0])}
    except FileNotFoundError:
        pass

    # Fallback: check if port is in use
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{DEFAULT_PORT}", "-t"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split("\n")
            return {"running": True, "pid": int(pids[0])}
    except FileNotFoundError:
        pass

    return {"running": False}


def _check_health() -> dict[str, Any]:
    """Check daemon health via gRPC."""
    try:
        import asyncio

        import grpc

        from protocols.proto.generated import LogosStub, StatusRequest

        async def check() -> dict[str, Any]:
            channel = grpc.aio.insecure_channel(f"localhost:{DEFAULT_PORT}")
            stub = LogosStub(channel)  # type: ignore[no-untyped-call]
            try:
                response = await asyncio.wait_for(
                    stub.GetStatus(StatusRequest(verbose=False)),
                    timeout=2.0,
                )
                await channel.close()
                return {
                    "healthy": True,
                    "instance_id": response.instance_id,
                }
            except Exception as e:
                await channel.close()
                return {"healthy": False, "error": str(e)}

        return asyncio.run(check())
    except ImportError:
        return {"healthy": False, "error": "gRPC not available"}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


def _is_launchd_installed() -> bool:
    """Check if launchd service is installed."""
    plist_path = LAUNCH_AGENTS_DIR / PLIST_FILENAME
    return plist_path.exists()


def _launchctl(action: str, target: str) -> int:
    """Run a launchctl command."""
    result = subprocess.run(
        ["launchctl", action, target],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and result.stderr:
        print(f"  launchctl {action}: {result.stderr.strip()}")
    return result.returncode


def _generate_plist() -> str:
    """Generate the launchd plist XML."""
    # Find the Python interpreter
    python_path = sys.executable

    # Find the kgents root
    try:
        from protocols.cli.hollow import find_kgents_root

        kgents_root = find_kgents_root()
        if kgents_root is not None:
            impl_path = kgents_root / "impl" / "claude"
        else:
            impl_path = Path(__file__).parent.parent.parent.parent
    except Exception:
        impl_path = Path(__file__).parent.parent.parent.parent

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>infra.cortex.daemon</string>
        <string>--port</string>
        <string>{DEFAULT_PORT}</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{impl_path}</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>{impl_path}</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>{LOGS_DIR / "cortex.stdout.log"}</string>

    <key>StandardErrorPath</key>
    <string>{LOGS_DIR / "cortex.stderr.log"}</string>

    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
"""


def _run_foreground(port: int) -> int:
    """Run the daemon in foreground mode."""
    try:
        import sys

        from infra.cortex.daemon import main

        sys.argv = ["daemon", "--port", str(port)]
        main()
        return 0
    except KeyboardInterrupt:
        print("\nDaemon stopped.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _start_background(port: int) -> int:
    """Start the daemon in background mode (without launchd)."""
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Find the impl path
    try:
        from protocols.cli.hollow import find_kgents_root

        kgents_root = find_kgents_root()
        if kgents_root is not None:
            impl_path = kgents_root / "impl" / "claude"
        else:
            impl_path = Path(__file__).parent.parent.parent.parent
    except Exception:
        impl_path = Path(__file__).parent.parent.parent.parent

    stdout_log = LOGS_DIR / "cortex.stdout.log"
    stderr_log = LOGS_DIR / "cortex.stderr.log"

    with open(stdout_log, "a") as stdout_f, open(stderr_log, "a") as stderr_f:
        process = subprocess.Popen(
            [sys.executable, "-m", "infra.cortex.daemon", "--port", str(port)],
            cwd=str(impl_path),
            env={**os.environ, "PYTHONPATH": str(impl_path)},
            stdout=stdout_f,
            stderr=stderr_f,
            start_new_session=True,
        )

    print(f"Daemon started (PID {process.pid})")
    print(f"Logs: {LOGS_DIR}")
    return 0


def _parse_port(args: list[str], default: int = DEFAULT_PORT) -> int:
    """Parse --port argument."""
    for i, arg in enumerate(args):
        if arg in ("--port", "-p") and i + 1 < len(args):
            try:
                return int(args[i + 1])
            except ValueError:
                pass
    return default


def _parse_lines(args: list[str], default: int = 50) -> int:
    """Parse --lines or -n argument."""
    for i, arg in enumerate(args):
        if arg in ("--lines", "-n") and i + 1 < len(args):
            try:
                return int(args[i + 1])
            except ValueError:
                pass
    return default
