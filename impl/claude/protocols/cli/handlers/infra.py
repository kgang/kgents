"""
Infra Handler: K-Terrarium cluster lifecycle management.

K-Terrarium transforms kgents from Python processes into a Kubernetes-native
agent ecosystem where isolation is physics, not policy.

Usage:
    kgents infra init       # Create Kind cluster (idempotent)
    kgents infra status     # Show cluster state
    kgents infra stop       # Pause cluster (docker pause)
    kgents infra start      # Resume cluster
    kgents infra destroy    # Remove cluster (--force to skip confirm)
    kgents infra deploy     # Deploy ping-agent POC (Phase 1)

Example:
    $ kgents infra init
    Creating cluster 'kgents-local'...
    Applying base manifests...
    Cluster ready in 45.2s

    $ kgents infra status
    Cluster: kgents-local (RUNNING)
    Namespaces: kgents-agents, kgents-ephemeral
    Agents: 1 running

    $ kgents infra stop
    Pausing cluster...
    Cluster paused.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable


def cmd_infra(args: list[str]) -> int:
    """
    Manage K-Terrarium infrastructure.

    Dispatches to subcommands: init, status, stop, start, destroy, deploy.
    """
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers: dict[str, Callable[[list[str]], int]] = {
        "init": _cmd_init,
        "status": _cmd_status,
        "stop": _cmd_stop,
        "start": _cmd_start,
        "destroy": _cmd_destroy,
        "deploy": _cmd_deploy,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Available: init, status, stop, start, destroy, deploy")
        return 1

    return handlers[subcommand](sub_args)


def _cmd_init(args: list[str]) -> int:
    """Create or verify the K-Terrarium cluster."""
    from infra.k8s import ClusterConfig, KindCluster, detect_terrarium_mode

    # Check prerequisites first
    detection = detect_terrarium_mode()
    if not detection.docker_available:
        print("Docker not available. Please start Docker Desktop.")
        return 1

    if detection.kind_path is None:
        print("Kind not installed.")
        print("Install from: https://kind.sigs.k8s.io/docs/user/quick-start/")
        return 1

    # Create cluster with progress callback
    def on_progress(msg: str) -> None:
        print(f"  {msg}")

    cluster = KindCluster(on_progress=on_progress)

    print("K-Terrarium Init")
    print("=" * 40)

    result = cluster.create()

    if result.success:
        print(f"\n{result.message}")
        print(f"Elapsed: {result.elapsed_seconds:.1f}s")
        return 0
    else:
        print(f"\nFailed: {result.message}")
        return 1


def _cmd_status(args: list[str]) -> int:
    """Show cluster status."""
    from infra.k8s import ClusterStatus, KindCluster, detect_terrarium_mode

    detection = detect_terrarium_mode()

    print("K-Terrarium Status")
    print("=" * 40)

    # Environment check
    print(f"Docker: {'available' if detection.docker_available else 'not available'}")
    print(f"Kind:   {detection.kind_path or 'not installed'}")
    print(f"Kubectl: {detection.kubectl_path or 'not installed'}")

    if not detection.can_create_cluster:
        print(f"\nCluster: NOT AVAILABLE ({detection.error})")
        return 0

    # Cluster status
    cluster = KindCluster()
    status = cluster.status()

    status_str = {
        ClusterStatus.RUNNING: "RUNNING",
        ClusterStatus.PAUSED: "PAUSED",
        ClusterStatus.STOPPED: "STOPPED",
        ClusterStatus.NOT_FOUND: "NOT FOUND",
        ClusterStatus.ERROR: "ERROR",
    }.get(status, "UNKNOWN")

    print(f"\nCluster: kgents-local ({status_str})")

    if status == ClusterStatus.RUNNING:
        # Show pods if running
        _show_pods()

    return 0


def _cmd_stop(args: list[str]) -> int:
    """Pause the cluster."""
    from infra.k8s import KindCluster

    def on_progress(msg: str) -> None:
        print(f"  {msg}")

    cluster = KindCluster(on_progress=on_progress)
    result = cluster.pause()

    if result.success:
        print(result.message)
        return 0
    else:
        print(f"Failed: {result.message}")
        return 1


def _cmd_start(args: list[str]) -> int:
    """Resume a paused cluster."""
    from infra.k8s import KindCluster

    def on_progress(msg: str) -> None:
        print(f"  {msg}")

    cluster = KindCluster(on_progress=on_progress)
    result = cluster.unpause()

    if result.success:
        print(result.message)
        return 0
    else:
        print(f"Failed: {result.message}")
        return 1


def _cmd_destroy(args: list[str]) -> int:
    """Destroy the cluster."""
    from infra.k8s import KindCluster

    force = "--force" in args

    if not force:
        print("This will destroy the kgents-local cluster.")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != "y":
            print("Cancelled.")
            return 0

    def on_progress(msg: str) -> None:
        print(f"  {msg}")

    cluster = KindCluster(on_progress=on_progress)
    result = cluster.destroy()

    if result.success:
        print(result.message)
        return 0
    else:
        print(f"Failed: {result.message}")
        return 1


def _cmd_deploy(args: list[str]) -> int:
    """
    Deploy the ping-agent POC.

    Steps:
    1. Build the ping-agent image
    2. Load it into Kind
    3. Apply the manifest
    """
    from infra.k8s import ClusterStatus, KindCluster

    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("Cluster not running. Run 'kgents infra init' first.")
        return 1

    # Paths
    images_dir = Path(__file__).parent.parent.parent.parent.parent / "images"
    ping_agent_dir = images_dir / "ping-agent"
    manifests_dir = (
        Path(__file__).parent.parent.parent.parent / "infra" / "k8s" / "manifests"
    )

    print("K-Terrarium Deploy: ping-agent")
    print("=" * 40)

    # Step 1: Build image
    print("\n[1/3] Building ping-agent image...")
    result = subprocess.run(
        ["docker", "build", "-t", "kgents/ping-agent:latest", str(ping_agent_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return 1
    print("  Image built successfully")

    # Step 2: Load into Kind
    print("\n[2/3] Loading image into Kind cluster...")
    result = subprocess.run(
        [
            "kind",
            "load",
            "docker-image",
            "kgents/ping-agent:latest",
            "--name",
            "kgents-local",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Load failed: {result.stderr}")
        return 1
    print("  Image loaded into cluster")

    # Step 3: Apply manifest
    print("\n[3/3] Applying ping-agent manifest...")
    manifest_path = manifests_dir / "ping-agent.yaml"
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(manifest_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Apply failed: {result.stderr}")
        return 1
    print("  Manifest applied")

    # Wait for pod to be ready
    print("\nWaiting for pod to be ready...")
    result = subprocess.run(
        [
            "kubectl",
            "wait",
            "--for=condition=ready",
            "pod",
            "-l",
            "app.kubernetes.io/name=ping-agent",
            "-n",
            "kgents-agents",
            "--timeout=60s",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Pod not ready: {result.stderr}")
        print("\nDebug: kubectl get pods -n kgents-agents")
        _show_pods()
        return 1

    print("\nping-agent deployed successfully!")
    print("\nTest it:")
    print(
        "  kubectl exec -it -n kgents-agents deploy/ping-agent -- curl localhost:8080/ping"
    )
    print("  kubectl logs -n kgents-agents deploy/ping-agent")

    return 0


def _show_pods() -> None:
    """Show pods in kgents namespaces."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "kgents-agents", "-o", "wide"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        print("\nPods in kgents-agents:")
        print(result.stdout)

    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "kgents-ephemeral", "-o", "wide"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        print("\nPods in kgents-ephemeral:")
        print(result.stdout)
