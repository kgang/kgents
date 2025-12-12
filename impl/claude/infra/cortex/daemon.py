"""
Cortex Daemon - The gRPC Server for the Glass Terminal.

This daemon hosts the Logos gRPC service, handling all CLI requests.
The CLI is hollow - all business logic lives here.

Usage:
    # Run directly
    python -m infra.cortex.daemon

    # Or via kgents CLI
    kgents infra daemon

Architecture:
    CLI (Glass) --> gRPC --> CortexDaemon (Logos service)
                                    |
                                    v
                            LifecycleManager
                            StorageProvider
                            BicameralMemory
                            PheromoneField
"""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from infra.cortex import CortexServicer
    from protocols.cli.instance_db.lifecycle import LifecycleManager

# Default gRPC port
DEFAULT_PORT = 50051


class CortexDaemon:
    """
    The Cortex daemon that hosts the Logos gRPC service.

    This is the living brain of kgents. The CLI is just glass in front of it.
    """

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        project_path: Path | None = None,
    ):
        self.port = port
        self.project_path = project_path
        self._server = None
        self._lifecycle_manager: LifecycleManager | None = None
        self._servicer: CortexServicer | None = None
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the daemon."""
        try:
            import grpc
            from protocols.proto.generated import add_LogosServicer_to_server
        except ImportError as e:
            print(f"Error: gRPC not available: {e}", file=sys.stderr)
            print("Install grpcio: pip install grpcio grpcio-tools", file=sys.stderr)
            return

        # Bootstrap the lifecycle
        print("[cortex] Bootstrapping lifecycle...")
        await self._bootstrap()

        # Create the servicer
        from infra.cortex import create_cortex_servicer

        self._servicer = create_cortex_servicer(
            lifecycle_state=self._lifecycle_manager.state
            if self._lifecycle_manager
            else None,
        )

        # Create the gRPC server
        self._server = grpc.aio.server()
        if self._server is None or self._servicer is None:
            print("[cortex] Failed to create server or servicer", file=sys.stderr)
            return

        add_LogosServicer_to_server(self._servicer, self._server)

        # Listen on port
        address = f"[::]:{self.port}"
        self._server.add_insecure_port(address)

        # Start the server
        await self._server.start()
        print(f"[cortex] Daemon started on port {self.port}")
        print(f"[cortex] Instance: {self._servicer._instance_id}")

        # Wait for shutdown
        await self._shutdown_event.wait()

        # Graceful shutdown
        print("[cortex] Shutting down...")
        await self._server.stop(grace=5.0)
        await self._shutdown()
        print("[cortex] Daemon stopped")

    async def _bootstrap(self) -> None:
        """Bootstrap the lifecycle manager."""
        try:
            from protocols.cli.instance_db.lifecycle import LifecycleManager

            self._lifecycle_manager = LifecycleManager()
            await self._lifecycle_manager.bootstrap(self.project_path)
            if self._lifecycle_manager.state is not None:
                print(
                    f"[cortex] Lifecycle bootstrapped: mode={self._lifecycle_manager.state.mode.value}"
                )
            else:
                print("[cortex] Lifecycle bootstrapped (no state)")
        except Exception as e:
            print(f"[cortex] Bootstrap warning: {e}", file=sys.stderr)
            self._lifecycle_manager = None

    async def _shutdown(self) -> None:
        """Shutdown the lifecycle manager."""
        if self._lifecycle_manager is not None:
            await self._lifecycle_manager.shutdown()
            self._lifecycle_manager = None

    def stop(self) -> None:
        """Signal the daemon to stop."""
        self._shutdown_event.set()


async def run_daemon(
    port: int = DEFAULT_PORT,
    project_path: Path | None = None,
) -> None:
    """
    Run the Cortex daemon.

    This is the main entry point for running the daemon.
    """
    daemon = CortexDaemon(port=port, project_path=project_path)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def handle_signal() -> None:
        print("\n[cortex] Received shutdown signal")
        daemon.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal)

    # Run the daemon
    await daemon.start()


def main() -> None:
    """Main entry point for the Cortex daemon."""
    import argparse

    parser = argparse.ArgumentParser(description="Cortex gRPC Daemon")
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--project",
        "-P",
        type=Path,
        default=None,
        help="Project path (default: auto-detect from cwd)",
    )

    args = parser.parse_args()

    # Auto-detect project path if not specified
    project_path = args.project
    if project_path is None:
        try:
            from protocols.cli.hollow import find_kgents_root

            project_path = find_kgents_root()
        except ImportError:
            pass

    # Run the daemon
    try:
        asyncio.run(run_daemon(port=args.port, project_path=project_path))
    except KeyboardInterrupt:
        print("\n[cortex] Interrupted")


if __name__ == "__main__":
    main()
