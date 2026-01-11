"""
kg dev — Run frontend and backend together with hot reload.

A unified development command that spins up:
- Backend API: uvicorn on port 8000 with --reload
- Frontend: Vite dev server on port 3000

"Tasteful > feature-complete"
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


def find_impl_root() -> Path:
    """Find the impl/claude directory."""
    # Walk up from current file to find impl/claude
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists() and current.name == "claude":
            return current
        current = current.parent

    # Fallback: try from cwd
    cwd = Path.cwd()
    if (cwd / "impl" / "claude").exists():
        return cwd / "impl" / "claude"
    if cwd.name == "claude" and (cwd / "pyproject.toml").exists():
        return cwd

    raise RuntimeError("Cannot find impl/claude directory")


def cmd_dev(args: list[str]) -> int:
    """
    Run frontend and backend together.

    Usage:
        kg dev              # Run both frontend and backend
        kg dev --backend    # Run only backend
        kg dev --frontend   # Run only frontend
        kg dev --help       # Show this help
    """
    if "--help" in args or "-h" in args:
        print(__doc__)
        print(
            """
Usage:
    kg dev              Run both frontend and backend
    kg dev --backend    Run only backend (uvicorn on :8000)
    kg dev --frontend   Run only frontend (vite on :3000)
    kg dev --no-color   Disable colored output prefixes

Environment:
    KGENTS_DEV_BACKEND_PORT   Backend port (default: 8000)
    KGENTS_DEV_FRONTEND_PORT  Frontend port (default: 3000)
"""
        )
        return 0

    backend_only = "--backend" in args or "-b" in args
    frontend_only = "--frontend" in args or "-f" in args
    no_color = "--no-color" in args

    if backend_only and frontend_only:
        print("Error: Cannot specify both --backend and --frontend")
        return 1

    try:
        impl_root = find_impl_root()
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1

    web_dir = impl_root / "web"
    if not web_dir.exists():
        print(f"Error: Frontend directory not found: {web_dir}")
        return 1

    # Port configuration
    backend_port = os.environ.get("KGENTS_DEV_BACKEND_PORT", "8000")
    frontend_port = os.environ.get("KGENTS_DEV_FRONTEND_PORT", "3000")

    # Color prefixes for output
    if no_color:
        backend_prefix = "[backend] "
        frontend_prefix = "[frontend] "
    else:
        backend_prefix = "\033[36m[backend]\033[0m "  # Cyan
        frontend_prefix = "\033[35m[frontend]\033[0m "  # Magenta

    processes: list[subprocess.Popen[str]] = []

    def cleanup(signum: int | None = None, frame: object = None) -> NoReturn:
        """Clean up child processes on exit."""
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
            except Exception:
                pass
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("🚀 Starting kgents development servers...")
    print()

    try:
        # Start backend
        if not frontend_only:
            print(f"{backend_prefix}Starting uvicorn on port {backend_port}...")
            backend_cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "protocols.api.app:create_app",
                "--factory",
                "--reload",
                "--port",
                backend_port,
                "--host",
                "0.0.0.0",
            ]
            backend_proc = subprocess.Popen(
                backend_cmd,
                cwd=impl_root,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            processes.append(backend_proc)

        # Start frontend
        if not backend_only:
            # Check if node_modules exists
            if not (web_dir / "node_modules").exists():
                print(f"{frontend_prefix}Installing dependencies (npm install)...")
                install_result = subprocess.run(
                    ["npm", "install"],
                    cwd=web_dir,
                    capture_output=True,
                    text=True,
                )
                if install_result.returncode != 0:
                    print(f"{frontend_prefix}npm install failed:")
                    print(install_result.stderr)
                    cleanup()

            print(f"{frontend_prefix}Starting Vite on port {frontend_port}...")
            frontend_cmd = ["npm", "run", "dev", "--", "--port", frontend_port]
            frontend_proc = subprocess.Popen(
                frontend_cmd,
                cwd=web_dir,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            processes.append(frontend_proc)

        # Print summary
        print()
        if not frontend_only:
            print(f"  📦 Backend:  http://localhost:{backend_port}")
        if not backend_only:
            print(f"  🌐 Frontend: http://localhost:{frontend_port}")
        print()
        print("Press Ctrl+C to stop all servers")
        print()

        # Wait for processes
        while processes:
            for proc in processes[:]:
                retcode = proc.poll()
                if retcode is not None:
                    # Process exited
                    if retcode != 0:
                        print(f"\n⚠️  Process exited with code {retcode}")
                    processes.remove(proc)
                    # If one dies, kill the others
                    if processes:
                        print("Stopping remaining servers...")
                        cleanup()

            # Small sleep to avoid busy loop
            import time

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        cleanup()
    except Exception as e:
        print(f"Error: {e}")
        cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(cmd_dev(sys.argv[1:]))
