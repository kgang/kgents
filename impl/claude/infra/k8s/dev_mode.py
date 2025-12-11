"""
Dev Mode for K-Terrarium.

Live reload development experience: edit code, see changes immediately.

The tight loop:
    save file → container detects → hot reload → output visible
         ~1s            ~1s             ~1s

Implementation:
- Volume mount impl/claude/agents/ into dev pods
- File watcher (watchdog) triggers reload
- Streaming logs to terminal
- --attach for interactive debugging

Usage:
    kgents dev b-gent              # Start B-gent in dev mode
    kgents dev b-gent --attach     # Attach with interactive shell
    kgents dev --stop              # Stop dev mode for all agents
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable


class DevModeStatus(Enum):
    """Status of dev mode."""

    STARTING = auto()
    RUNNING = auto()
    RELOADING = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass
class DevModeConfig:
    """Configuration for dev mode."""

    namespace: str = "kgents-agents"
    watch_patterns: list[str] = field(default_factory=lambda: ["*.py"])
    reload_delay: float = 0.5  # Debounce delay in seconds
    log_tail_lines: int = 100
    source_path: Path = field(default_factory=lambda: Path("impl/claude/agents"))
    mount_path: str = "/app/agents"


@dataclass
class DevPodSpec:
    """Specification for a development pod."""

    genus: str
    name: str
    namespace: str
    source_path: Path
    mount_path: str
    image: str = "python:3.12-slim"
    cpu: str = "200m"  # More CPU for dev
    memory: str = "512Mi"  # More memory for dev
    entrypoint: str | None = None

    def to_deployment(self) -> dict[str, Any]:
        """Generate Kubernetes Deployment manifest with volume mount."""
        # Determine the host path for volume mounting
        host_path = str(self.source_path.resolve())

        # Build command that watches for changes
        reload_script = self._build_reload_script()

        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.genus.lower()}-gent-dev",
                "namespace": self.namespace,
                "labels": self._labels(),
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": self._labels()},
                "template": {
                    "metadata": {"labels": self._labels()},
                    "spec": {
                        "containers": [
                            {
                                "name": "dev",
                                "image": self.image,
                                "command": ["sh", "-c", reload_script],
                                "resources": {
                                    "limits": {
                                        "cpu": self.cpu,
                                        "memory": self.memory,
                                    },
                                    "requests": {
                                        "cpu": self._halve(self.cpu),
                                        "memory": self._halve(self.memory),
                                    },
                                },
                                "volumeMounts": [
                                    {
                                        "name": "source",
                                        "mountPath": self.mount_path,
                                    }
                                ],
                                "env": [
                                    {"name": "KGENTS_GENUS", "value": self.genus},
                                    {"name": "KGENTS_DEV_MODE", "value": "1"},
                                    {"name": "PYTHONDONTWRITEBYTECODE", "value": "1"},
                                    {"name": "PYTHONUNBUFFERED", "value": "1"},
                                ],
                                "stdin": True,
                                "tty": True,
                            }
                        ],
                        "volumes": [
                            {
                                "name": "source",
                                "hostPath": {
                                    "path": host_path,
                                    "type": "Directory",
                                },
                            }
                        ],
                        "restartPolicy": "Always",
                    },
                },
            },
        }

    def _build_reload_script(self) -> str:
        """Build the script that handles file watching and reloading."""
        entrypoint = self.entrypoint or f"agents.{self.genus.lower()}.main"

        # Simple watch-and-reload loop using inotifywait or polling
        # This works inside the container when source is mounted
        return f"""
set -e
echo "[dev] Starting {self.genus}-gent in dev mode..."
echo "[dev] Watching {self.mount_path} for changes..."

# Install watchdog if not present
pip install -q watchdog 2>/dev/null || true

# Create a simple watcher script
cat > /tmp/watcher.py << 'WATCHER'
import sys
import time
import subprocess
import importlib.util
from pathlib import Path

def run_agent():
    \"\"\"Run the agent module.\"\"\"
    print("[dev] Starting agent...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "{entrypoint}"],
        env={{**dict(__import__("os").environ), "PYTHONPATH": "{self.mount_path}"}},
    )
    return proc

def watch_files(path, callback, interval=1.0):
    \"\"\"Simple file watcher using mtime polling.\"\"\"
    last_mtimes = {{}}

    def scan():
        current = {{}}
        for p in Path(path).rglob("*.py"):
            try:
                current[str(p)] = p.stat().st_mtime
            except (OSError, IOError):
                pass
        return current

    last_mtimes = scan()

    while True:
        time.sleep(interval)
        current = scan()

        changed = []
        for f, mtime in current.items():
            if f not in last_mtimes or last_mtimes[f] != mtime:
                changed.append(f)

        if changed:
            print(f"[dev] Changed: {{', '.join(Path(f).name for f in changed)}}")
            callback()
            last_mtimes = current

proc = run_agent()

def reload():
    global proc
    if proc:
        print("[dev] Reloading...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    proc = run_agent()

try:
    watch_files("{self.mount_path}", reload)
except KeyboardInterrupt:
    print("[dev] Stopping...")
    if proc:
        proc.terminate()
WATCHER

PYTHONPATH="{self.mount_path}" python /tmp/watcher.py
"""

    def _labels(self) -> dict[str, str]:
        """Standard labels for dev mode resources."""
        return {
            "app.kubernetes.io/name": f"{self.genus.lower()}-gent-dev",
            "app.kubernetes.io/part-of": "kgents",
            "app.kubernetes.io/managed-by": "kgents-dev",
            "kgents.io/genus": self.genus,
            "kgents.io/mode": "dev",
        }

    def _halve(self, resource: str) -> str:
        """Halve a resource value for requests."""
        if resource.endswith("m"):
            return f"{int(resource[:-1]) // 2}m"
        if resource.endswith("Mi"):
            return f"{int(resource[:-2]) // 2}Mi"
        return resource


@dataclass
class DevModeResult:
    """Result of a dev mode operation."""

    success: bool
    message: str
    status: DevModeStatus = DevModeStatus.STOPPED
    pod_name: str = ""
    elapsed_seconds: float = 0.0


class DevMode:
    """
    Live reload development for K-Terrarium agents.

    Example:
        dev = DevMode()
        result = await dev.start("b-gent")
        # Edit impl/claude/agents/b/main.py
        # Changes are automatically reloaded

        await dev.stop("b-gent")
    """

    def __init__(
        self,
        config: DevModeConfig | None = None,
        on_progress: Callable[[str], None] | None = None,
    ):
        """
        Initialize dev mode.

        Args:
            config: Dev mode configuration
            on_progress: Progress callback
        """
        self.config = config or DevModeConfig()
        self._on_progress = on_progress or (lambda msg: None)
        self._active_dev_pods: dict[str, DevPodSpec] = {}

    async def start(
        self,
        genus: str,
        attach: bool = False,
        source_path: Path | None = None,
    ) -> DevModeResult:
        """
        Start an agent in dev mode with live reload.

        Args:
            genus: Agent genus (e.g., "B" or "b-gent")
            attach: Attach to container for interactive debugging
            source_path: Override source path to mount

        Returns:
            DevModeResult with status
        """
        start_time = time.perf_counter()

        # Normalize genus
        if genus.endswith("-gent"):
            genus = genus[:-5].upper()
        elif genus.endswith("gent"):
            genus = genus[:-4].upper()
        else:
            genus = genus.upper()

        self._on_progress(f"Starting {genus}-gent in dev mode...")

        # Verify cluster is running
        if not self._cluster_running():
            return DevModeResult(
                success=False,
                message="Cluster not running. Run 'kgents infra init' first.",
                status=DevModeStatus.ERROR,
            )

        # Build pod spec
        src_path = source_path or self.config.source_path
        spec = DevPodSpec(
            genus=genus,
            name=f"{genus.lower()}-gent-dev",
            namespace=self.config.namespace,
            source_path=src_path,
            mount_path=self.config.mount_path,
        )

        # Check if source directory exists
        agent_path = src_path / genus.lower()
        if not agent_path.exists():
            return DevModeResult(
                success=False,
                message=f"Agent directory not found: {agent_path}",
                status=DevModeStatus.ERROR,
            )

        # Generate and apply deployment
        deployment = spec.to_deployment()

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=json.dumps(deployment),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return DevModeResult(
                    success=False,
                    message=f"Failed to create dev pod: {result.stderr}",
                    status=DevModeStatus.ERROR,
                )

            self._active_dev_pods[genus] = spec
            self._on_progress(f"Dev pod created: {spec.name}")

            # Wait for pod to be ready
            self._on_progress("Waiting for pod to be ready...")
            ready = await self._wait_for_ready(spec)

            if not ready:
                return DevModeResult(
                    success=False,
                    message="Pod failed to start. Check 'kubectl get pods -n kgents-agents'",
                    status=DevModeStatus.ERROR,
                )

            elapsed = time.perf_counter() - start_time

            if attach:
                # Attach to pod for interactive debugging
                self._on_progress("Attaching to pod (Ctrl+C to detach)...")
                await self._attach_to_pod(spec)
                return DevModeResult(
                    success=True,
                    message="Detached from dev pod",
                    status=DevModeStatus.RUNNING,
                    pod_name=spec.name,
                    elapsed_seconds=elapsed,
                )
            else:
                # Start log streaming
                self._on_progress("Streaming logs (Ctrl+C to stop)...")
                await self._stream_logs(spec)

            return DevModeResult(
                success=True,
                message=f"{genus}-gent dev mode started",
                status=DevModeStatus.RUNNING,
                pod_name=spec.name,
                elapsed_seconds=elapsed,
            )

        except subprocess.TimeoutExpired:
            return DevModeResult(
                success=False,
                message="Timed out starting dev pod",
                status=DevModeStatus.ERROR,
            )
        except Exception as e:
            return DevModeResult(
                success=False,
                message=f"Failed to start dev mode: {e}",
                status=DevModeStatus.ERROR,
            )

    async def stop(self, genus: str | None = None) -> DevModeResult:
        """
        Stop dev mode for an agent or all agents.

        Args:
            genus: Agent genus to stop, or None to stop all

        Returns:
            DevModeResult with status
        """
        start_time = time.perf_counter()

        if genus:
            # Stop specific agent
            genus = genus.upper() if not genus.endswith("-gent") else genus[:-5].upper()
            pods_to_stop = [genus]
        else:
            # Stop all dev pods
            pods_to_stop = list(self._active_dev_pods.keys())
            if not pods_to_stop:
                # Check cluster for any dev pods
                result = subprocess.run(
                    [
                        "kubectl",
                        "get",
                        "deployments",
                        "-n",
                        self.config.namespace,
                        "-l",
                        "kgents.io/mode=dev",
                        "-o",
                        "jsonpath={.items[*].metadata.name}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    pods_to_stop = result.stdout.strip().split()

        if not pods_to_stop:
            return DevModeResult(
                success=True,
                message="No dev pods running",
                status=DevModeStatus.STOPPED,
            )

        stopped = []
        for g in pods_to_stop:
            pod_name = f"{g.lower()}-gent-dev" if not g.endswith("-dev") else g
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "delete",
                        "deployment",
                        pod_name,
                        "-n",
                        self.config.namespace,
                        "--ignore-not-found",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    stopped.append(pod_name)
                    self._active_dev_pods.pop(g.upper(), None)
                    self._on_progress(f"Stopped: {pod_name}")
            except Exception:
                pass

        elapsed = time.perf_counter() - start_time

        if stopped:
            return DevModeResult(
                success=True,
                message=f"Stopped {len(stopped)} dev pod(s): {', '.join(stopped)}",
                status=DevModeStatus.STOPPED,
                elapsed_seconds=elapsed,
            )
        else:
            return DevModeResult(
                success=True,
                message="No dev pods to stop",
                status=DevModeStatus.STOPPED,
            )

    async def status(self) -> list[dict[str, Any]]:
        """Get status of all dev pods."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    self.config.namespace,
                    "-l",
                    "kgents.io/mode=dev",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return []

            data = json.loads(result.stdout)
            pods = []

            for item in data.get("items", []):
                metadata = item.get("metadata", {})
                status = item.get("status", {})
                phase = status.get("phase", "Unknown")

                pods.append(
                    {
                        "name": metadata.get("name"),
                        "genus": metadata.get("labels", {}).get("kgents.io/genus"),
                        "phase": phase,
                        "ready": self._pod_ready(item),
                    }
                )

            return pods

        except Exception:
            return []

    def _cluster_running(self) -> bool:
        """Check if Kind cluster is running."""
        try:
            result = subprocess.run(
                ["kubectl", "get", "namespace", self.config.namespace],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _wait_for_ready(self, spec: DevPodSpec, timeout: int = 60) -> bool:
        """Wait for dev pod to be ready."""
        deadline = time.perf_counter() + timeout

        while time.perf_counter() < deadline:
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "wait",
                        "--for=condition=ready",
                        "pod",
                        "-l",
                        f"app.kubernetes.io/name={spec.name}",
                        "-n",
                        spec.namespace,
                        "--timeout=5s",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    return True

            except Exception:
                pass

            await asyncio.sleep(1)

        return False

    async def _stream_logs(self, spec: DevPodSpec) -> None:
        """Stream logs from the dev pod."""
        try:
            # Use kubectl logs -f for streaming
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "logs",
                "-f",
                "-l",
                f"app.kubernetes.io/name={spec.name}",
                "-n",
                spec.namespace,
                "--tail",
                str(self.config.log_tail_lines),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            if proc.stdout:
                async for line in proc.stdout:
                    print(line.decode("utf-8"), end="")

        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            pass

    async def _attach_to_pod(self, spec: DevPodSpec) -> None:
        """Attach to pod for interactive debugging."""
        try:
            # Get pod name
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-l",
                    f"app.kubernetes.io/name={spec.name}",
                    "-n",
                    spec.namespace,
                    "-o",
                    "jsonpath={.items[0].metadata.name}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0 or not result.stdout.strip():
                self._on_progress("Could not find pod to attach")
                return

            pod_name = result.stdout.strip()

            # Use os.system for interactive session
            os.system(f"kubectl exec -it {pod_name} -n {spec.namespace} -- /bin/sh")

        except Exception as e:
            self._on_progress(f"Failed to attach: {e}")

    def _pod_ready(self, pod_data: dict[str, Any]) -> bool:
        """Check if a pod is ready from its status data."""
        conditions = pod_data.get("status", {}).get("conditions", [])
        for cond in conditions:
            if cond.get("type") == "Ready" and cond.get("status") == "True":
                return True
        return False


def create_dev_mode(
    on_progress: Callable[[str], None] | None = None,
) -> DevMode:
    """Factory function to create DevMode instance."""
    return DevMode(on_progress=on_progress)
