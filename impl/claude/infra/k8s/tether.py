"""
Tether Protocol for K-Terrarium.

The debuggability crisis resolved: bidirectional stream with signal forwarding.

The Problem:
    - Developing against a cluster is painful
    - Ctrl+C kills the CLI client, but the agent keeps spinning
    - Tokens burn, state corrupts, no stack trace

The Solution: `kgents tether <agent_id>`
    - Local SIGINT → Pod SIGTERM
    - Pod stdout/stderr → Terminal (real-time)
    - Supports debugpy injection

Principle alignment: Transparent Infrastructure.
    The developer feels like the agent runs locally.

Usage:
    kgents tether b-gent           # Attach to B-gent
    kgents tether b-gent --debug   # Attach with debugpy on :5678
    # Ctrl+C now actually stops the agent
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable


class TetherState(Enum):
    """State of the tether connection."""

    DISCONNECTED = auto()
    CONNECTING = auto()
    ATTACHED = auto()
    FORWARDING = auto()
    DETACHING = auto()
    ERROR = auto()


@dataclass
class TetherConfig:
    """Configuration for tether protocol."""

    namespace: str = "kgents-agents"
    debug_port: int = 5678
    signal_timeout: float = 5.0  # Seconds to wait for signal delivery
    reconnect_delay: float = 1.0
    max_reconnects: int = 3


@dataclass
class TetherResult:
    """Result of a tether operation."""

    success: bool
    message: str
    state: TetherState = TetherState.DISCONNECTED
    pod_name: str = ""
    exit_code: int | None = None


@dataclass
class TetherSession:
    """Active tether session state."""

    agent_id: str
    pod_name: str
    container: str
    debug_enabled: bool = False
    debug_port: int = 5678
    state: TetherState = TetherState.DISCONNECTED
    process: asyncio.subprocess.Process | None = None


class TetherProtocol:
    """
    Bidirectional stream with signal forwarding.

    The tether makes the agent feel local:
    - Ctrl+C in terminal → SIGTERM in pod
    - stdout/stderr from pod → terminal in real-time
    - Optional debugpy injection for remote debugging

    Example:
        tether = TetherProtocol()
        await tether.attach("b-gent", debug=True)
        # Now Ctrl+C actually stops the agent
        # Debugger listening on localhost:5678
    """

    def __init__(
        self,
        config: TetherConfig | None = None,
        on_output: Callable[[str, str], None] | None = None,
        on_state_change: Callable[[TetherState], None] | None = None,
    ) -> None:
        """
        Initialize tether protocol.

        Args:
            config: Tether configuration
            on_output: Callback for output (stream: 'stdout'|'stderr', data: str)
            on_state_change: Callback for state changes
        """
        self.config = config or TetherConfig()
        self._on_output = on_output or self._default_output
        self._on_state_change = on_state_change or (lambda _: None)
        self._session: TetherSession | None = None
        self._original_sigint: Any = None
        self._port_forward_proc: asyncio.subprocess.Process | None = None

    async def attach(
        self,
        agent_id: str,
        debug: bool = False,
        debug_port: int | None = None,
    ) -> TetherResult:
        """
        Attach to a running agent.

        Establishes bidirectional stream:
        - Local SIGINT → Pod SIGTERM
        - Pod stdout/stderr → Terminal
        - Optional debugpy injection

        Args:
            agent_id: Agent identifier (e.g., "b-gent" or "B")
            debug: Enable debugpy injection
            debug_port: Debug port (default: 5678)

        Returns:
            TetherResult with session info
        """
        self._set_state(TetherState.CONNECTING)

        # Normalize agent_id
        agent_id = self._normalize_agent_id(agent_id)

        # Find pod for agent
        pod_info = await self._find_pod(agent_id)
        if not pod_info:
            return TetherResult(
                success=False,
                message=f"No pod found for agent: {agent_id}",
                state=TetherState.ERROR,
            )

        pod_name = pod_info["name"]
        container = pod_info.get("container", "agent")

        # Create session
        self._session = TetherSession(
            agent_id=agent_id,
            pod_name=pod_name,
            container=container,
            debug_enabled=debug,
            debug_port=debug_port or self.config.debug_port,
        )

        # Register signal handler
        self._register_signal_handler()

        # Optional: inject debugpy
        if debug:
            inject_result = await self._inject_debugpy(
                pod_name, self._session.debug_port
            )
            if not inject_result:
                print(
                    "[tether] Warning: Could not inject debugpy. "
                    "Continuing without debug support."
                )
            else:
                # Start port forward for debugpy
                await self._start_port_forward(pod_name, self._session.debug_port)
                print(
                    f"[tether] Debugger listening on localhost:{self._session.debug_port}"
                )

        self._set_state(TetherState.ATTACHED)
        print(f"[tether] Attached to {pod_name}")
        print("[tether] Ctrl+C will stop the agent")

        # Stream stdout/stderr
        try:
            await self._stream_logs(pod_name, container)
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            pass
        finally:
            await self.detach(graceful=False)

        return TetherResult(
            success=True,
            message=f"Detached from {pod_name}",
            state=TetherState.DISCONNECTED,
            pod_name=pod_name,
        )

    async def detach(self, graceful: bool = True) -> TetherResult:
        """
        Detach from the current session.

        Args:
            graceful: Send SIGTERM before detaching

        Returns:
            TetherResult
        """
        if not self._session:
            return TetherResult(
                success=True,
                message="Not attached",
                state=TetherState.DISCONNECTED,
            )

        self._set_state(TetherState.DETACHING)

        pod_name = self._session.pod_name

        # Restore signal handler
        self._restore_signal_handler()

        # Stop port forward if running
        if self._port_forward_proc:
            self._port_forward_proc.terminate()
            try:
                await asyncio.wait_for(self._port_forward_proc.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._port_forward_proc.kill()
            self._port_forward_proc = None

        # Kill log streaming process
        if self._session.process:
            self._session.process.terminate()
            try:
                await asyncio.wait_for(self._session.process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._session.process.kill()

        self._session = None
        self._set_state(TetherState.DISCONNECTED)

        return TetherResult(
            success=True,
            message=f"Detached from {pod_name}",
            state=TetherState.DISCONNECTED,
            pod_name=pod_name,
        )

    async def forward_signal(self, sig: int) -> bool:
        """
        Forward a signal to the tethered pod.

        Args:
            sig: Unix signal number (e.g., signal.SIGTERM)

        Returns:
            True if signal was forwarded successfully
        """
        if not self._session:
            return False

        self._set_state(TetherState.FORWARDING)

        pod_name = self._session.pod_name
        container = self._session.container

        sig_name = (
            signal.Signals(sig).name
            if sig in signal.Signals._value2member_map_
            else str(sig)
        )
        print(f"[tether] Forwarding {sig_name} to {pod_name}...")

        try:
            # Use kubectl exec to send signal
            # We send to PID 1 (the main process) via kill command
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "exec",
                pod_name,
                "-n",
                self.config.namespace,
                "-c",
                container,
                "--",
                "kill",
                f"-{sig}",
                "1",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.config.signal_timeout
            )

            if proc.returncode == 0:
                print(f"[tether] {sig_name} delivered")
                self._set_state(TetherState.ATTACHED)
                return True
            else:
                print(f"[tether] Failed to deliver signal: {stderr.decode()}")
                self._set_state(TetherState.ATTACHED)
                return False

        except asyncio.TimeoutError:
            print("[tether] Signal delivery timed out")
            self._set_state(TetherState.ATTACHED)
            return False
        except Exception as e:
            print(f"[tether] Error forwarding signal: {e}")
            self._set_state(TetherState.ATTACHED)
            return False

    async def send_input(self, data: bytes) -> bool:
        """
        Send input to the tethered pod's stdin.

        Args:
            data: Input data

        Returns:
            True if input was sent successfully
        """
        if not self._session or not self._session.process:
            return False

        if self._session.process.stdin:
            self._session.process.stdin.write(data)
            await self._session.process.stdin.drain()
            return True

        return False

    async def _find_pod(self, agent_id: str) -> dict[str, str] | None:
        """Find the pod for an agent."""
        # Try multiple label selectors
        selectors = [
            f"app.kubernetes.io/name={agent_id}",
            f"kgents.io/genus={agent_id.upper().replace('-GENT', '')}",
            f"app={agent_id}",
        ]

        for selector in selectors:
            try:
                result = await asyncio.create_subprocess_exec(
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    self.config.namespace,
                    "-l",
                    selector,
                    "-o",
                    "json",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, _ = await result.communicate()

                if result.returncode == 0:
                    data = json.loads(stdout.decode())
                    items = data.get("items", [])

                    # Find running pod
                    for item in items:
                        phase = item.get("status", {}).get("phase", "")
                        if phase == "Running":
                            metadata = item.get("metadata", {})
                            containers = item.get("spec", {}).get("containers", [])
                            container_name = (
                                containers[0]["name"] if containers else "agent"
                            )

                            return {
                                "name": metadata.get("name", ""),
                                "container": container_name,
                            }

            except Exception:
                continue

        return None

    async def _inject_debugpy(self, pod_name: str, port: int) -> bool:
        """Inject debugpy into the pod for remote debugging."""
        try:
            # Install debugpy if not present
            install_proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "exec",
                pod_name,
                "-n",
                self.config.namespace,
                "--",
                "pip",
                "install",
                "-q",
                "debugpy",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await asyncio.wait_for(install_proc.communicate(), timeout=30.0)

            # Start debugpy listener
            # Note: This runs in background on the pod
            debug_script = f"""
import debugpy
debugpy.listen(('0.0.0.0', {port}))
print('[debugpy] Waiting for debugger to attach on port {port}...')
"""
            inject_proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "exec",
                pod_name,
                "-n",
                self.config.namespace,
                "--",
                "python",
                "-c",
                debug_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Don't wait for completion - it runs in background
            await asyncio.sleep(1.0)

            return inject_proc.returncode is None  # Still running = success

        except Exception as e:
            print(f"[tether] debugpy injection failed: {e}")
            return False

    async def _start_port_forward(self, pod_name: str, port: int) -> None:
        """Start port forwarding for debugpy."""
        try:
            self._port_forward_proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "port-forward",
                pod_name,
                f"{port}:{port}",
                "-n",
                self.config.namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Give it a moment to establish
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[tether] Port forward failed: {e}")

    async def _stream_logs(self, pod_name: str, container: str) -> None:
        """Stream logs from the pod to the terminal."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "logs",
                "-f",
                pod_name,
                "-n",
                self.config.namespace,
                "-c",
                container,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            if self._session:
                self._session.process = proc

            if proc.stdout:
                async for line in proc.stdout:
                    self._on_output("stdout", line.decode())

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[tether] Log streaming error: {e}")

    def _register_signal_handler(self) -> None:
        """Register handler to forward signals to pod."""
        self._original_sigint = signal.getsignal(signal.SIGINT)

        def handler(signum: int, frame: Any) -> None:
            print()  # Newline after ^C
            asyncio.create_task(self._handle_interrupt(signum))

        signal.signal(signal.SIGINT, handler)

    def _restore_signal_handler(self) -> None:
        """Restore original signal handler."""
        if self._original_sigint:
            signal.signal(signal.SIGINT, self._original_sigint)
            self._original_sigint = None

    async def _handle_interrupt(self, signum: int) -> None:
        """Handle interrupt by forwarding to pod then detaching."""
        if self._session:
            # Forward SIGTERM to pod
            await self.forward_signal(signal.SIGTERM)

            # Give the pod time to shut down
            await asyncio.sleep(1.0)

            # Detach
            await self.detach(graceful=False)

        # Re-raise to exit
        raise KeyboardInterrupt()

    def _set_state(self, state: TetherState) -> None:
        """Update state and notify callback."""
        if self._session:
            self._session.state = state
        self._on_state_change(state)

    def _normalize_agent_id(self, agent_id: str) -> str:
        """Normalize agent ID to standard format."""
        agent_id = agent_id.lower()
        if not agent_id.endswith("-gent") and not agent_id.endswith("-dev"):
            agent_id = f"{agent_id}-gent"
        return agent_id

    def _default_output(self, stream: str, data: str) -> None:
        """Default output handler - print to terminal."""
        print(data, end="", flush=True)


def create_tether(
    on_output: Callable[[str, str], None] | None = None,
    on_state_change: Callable[[TetherState], None] | None = None,
) -> TetherProtocol:
    """Factory function to create TetherProtocol instance."""
    return TetherProtocol(on_output=on_output, on_state_change=on_state_change)
