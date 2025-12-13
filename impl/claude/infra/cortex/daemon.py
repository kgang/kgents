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
                            HolographicBuffer (Phase 5)
                            Purgatory (Phase 5)
"""

from __future__ import annotations

import asyncio
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.flux.semaphore import Purgatory
    from infra.cortex import CortexServicer
    from protocols.cli.instance_db.lifecycle import LifecycleManager
    from protocols.terrarium.mirror import HolographicBuffer

# Default gRPC port (50051 often used by Docker, so we use 50052)
DEFAULT_PORT = 50052


class CortexDaemon:
    """
    The Cortex daemon that hosts the Logos gRPC service.

    This is the living brain of kgents. The CLI is just glass in front of it.

    Phase 5 (Terrarium Integration):
    - HolographicBuffer: Shared mirror for observability
    - Purgatory: Shared waiting room for semaphore tokens
    - All FluxAgents created by the servicer can be attached to these
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

        # Phase 5: Terrarium integration
        self._buffer: "HolographicBuffer | None" = None
        self._purgatory: "Purgatory | None" = None

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
        """Bootstrap the lifecycle manager and terrarium infrastructure."""
        # Bootstrap lifecycle manager
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

        # Phase 5: Bootstrap terrarium infrastructure
        await self._bootstrap_terrarium()

    async def _bootstrap_terrarium(self) -> None:
        """Bootstrap the shared HolographicBuffer and Purgatory."""
        try:
            from agents.flux.semaphore import Purgatory
            from protocols.terrarium.mirror import HolographicBuffer

            # Create shared buffer for all observers
            self._buffer = HolographicBuffer(max_history=100)
            print("[cortex] HolographicBuffer initialized")

            # Create shared purgatory for semaphore tokens
            self._purgatory = Purgatory()

            # Wire purgatory emission to buffer
            self._purgatory._emit_pheromone = self._emit_purgatory_pheromone
            print("[cortex] Purgatory initialized and wired to buffer")

        except ImportError as e:
            print(f"[cortex] Terrarium not available: {e}", file=sys.stderr)
            self._buffer = None
            self._purgatory = None
        except Exception as e:
            print(f"[cortex] Terrarium bootstrap warning: {e}", file=sys.stderr)

    async def _emit_purgatory_pheromone(
        self, signal: str, data: dict[str, Any]
    ) -> None:
        """
        Emit purgatory signals to the HolographicBuffer.

        This allows observers to see semaphore events in real-time:
        - purgatory_ejected: Token ejected to purgatory
        - purgatory_resolved: Token resolved by human
        - purgatory_cancelled: Token cancelled
        - purgatory_voided: Token deadline expired
        """
        if self._buffer is None:
            return

        event = {
            "type": signal.replace(".", "_"),
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source": "cortex.purgatory",
        }

        try:
            await self._buffer.reflect(event)
        except Exception:
            # Best-effort: don't let emission failures affect control flow
            pass

    async def _shutdown(self) -> None:
        """Shutdown the lifecycle manager and terrarium infrastructure."""
        # Shutdown lifecycle manager
        if self._lifecycle_manager is not None:
            await self._lifecycle_manager.shutdown()
            self._lifecycle_manager = None

        # Shutdown terrarium infrastructure
        await self._shutdown_terrarium()

    async def _shutdown_terrarium(self) -> None:
        """Shutdown the HolographicBuffer and Purgatory."""
        if self._purgatory is not None:
            # Void any expired tokens before shutdown
            try:
                voided = await self._purgatory.void_expired()
                if voided:
                    print(f"[cortex] Voided {len(voided)} expired tokens on shutdown")
            except Exception:
                pass  # Best-effort cleanup
            self._purgatory = None

        if self._buffer is not None:
            self._buffer = None

        print("[cortex] Terrarium infrastructure shutdown")

    def stop(self) -> None:
        """Signal the daemon to stop."""
        self._shutdown_event.set()

    # Phase 5: Property accessors for terrarium infrastructure
    @property
    def buffer(self) -> "HolographicBuffer | None":
        """Get the shared HolographicBuffer for observer attachment."""
        return self._buffer

    @property
    def purgatory(self) -> "Purgatory | None":
        """Get the shared Purgatory for semaphore handling."""
        return self._purgatory


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
