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
    kgents infra apply <agent>  # Deploy agent via CRD (Phase 3)
    kgents infra crd        # Install all kgents CRDs
    kgents infra crd --list # List installed CRDs
    kgents infra cleanup    # Auto-cleanup failed deployments

CRDs (Custom Resource Definitions):
    agents.kgents.io      - Agent deployment specification
    pheromones.kgents.io  - Stigmergic coordination (decay over time)
    memories.kgents.io    - Persistent state management
    umwelts.kgents.io     - Observer context (AGENTESE)
    proposals.kgents.io   - Risk-aware change governance (T-gent integration)

Apply Options:
    kgents infra apply b-gent           # PLACEHOLDER mode (safe, no image needed)
    kgents infra apply b-gent --dry-run # Preview manifests without deploying
    kgents infra apply b-gent --full    # FULL mode (requires built image)

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

    $ kgents infra cleanup
    Checking kgents-agents...
    Cleaned up 2 deployment(s):
      - b-gent
      - q-gent
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from infra.k8s import DeployMode


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
        "apply": _cmd_apply,
        "crd": _cmd_crd,
        "cleanup": _cmd_cleanup,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print(
            "Available: init, status, stop, start, destroy, deploy, apply, crd, cleanup"
        )
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


def _cmd_crd(args: list[str]) -> int:
    """
    Install all kgents CRD definitions.

    CRDs installed (5 total):
    - agents.kgents.io      (Agent deployment spec)
    - pheromones.kgents.io  (Stigmergic coordination - decay over time)
    - memories.kgents.io    (Persistent state management)
    - umwelts.kgents.io     (Observer context - AGENTESE)
    - proposals.kgents.io   (Risk-aware change governance)

    Usage:
        kgents infra crd           # Install all CRDs
        kgents infra crd --apply   # Alias for install
        kgents infra crd --list    # List installed CRDs
        kgents infra crd --verify  # Verify CRD health
    """
    from infra.k8s import ClusterStatus, KindCluster, create_operator

    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("Cluster not running. Run 'kgents infra init' first.")
        return 1

    # Handle --list flag
    if "--list" in args:
        return _list_crds()

    # Handle --verify flag
    if "--verify" in args:
        return _verify_crds()

    print("Installing kgents CRDs...")
    print("=" * 40)

    import asyncio

    # Install Agent CRD via operator
    print("\n[1/5] Installing agents.kgents.io...")
    operator = create_operator()
    agent_success = asyncio.run(operator.apply_crd())
    if agent_success:
        print("  agents.kgents.io installed")
    else:
        print("  Failed to install agents.kgents.io")

    # Install new CRDs from crds/ directory
    crds_dir = Path(__file__).parent.parent.parent.parent / "infra" / "k8s" / "crds"

    # All 4 additional CRDs (5 total including agent)
    crd_files = [
        ("pheromones.kgents.io", "pheromone-crd.yaml"),
        ("memories.kgents.io", "memory-crd.yaml"),
        ("umwelts.kgents.io", "umwelt-crd.yaml"),
        ("proposals.kgents.io", "proposal-crd.yaml"),
    ]

    all_success = agent_success
    for i, (crd_name, filename) in enumerate(crd_files, start=2):
        print(f"\n[{i}/5] Installing {crd_name}...")
        crd_path = crds_dir / filename

        if not crd_path.exists():
            print(f"  CRD file not found: {crd_path}")
            all_success = False
            continue

        result = subprocess.run(
            ["kubectl", "apply", "-f", str(crd_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"  {crd_name} installed")
        else:
            print(f"  Failed: {result.stderr.strip()}")
            all_success = False

    print("\n" + "=" * 40)
    if all_success:
        print("All 5 CRDs installed successfully.")
        print("\nVerify with:")
        print("  kubectl get crd | grep kgents")
        print("\nWatch resources:")
        print("  kubectl get pheromones -n kgents-agents --watch")
        print("  kubectl get proposals -n kgents-agents --watch")
        return 0
    else:
        print("Some CRDs failed to install. Check errors above.")
        return 1


def _verify_crds() -> int:
    """Verify all kgents CRDs are healthy and properly installed."""
    expected_crds = [
        "agents.kgents.io",
        "pheromones.kgents.io",
        "memories.kgents.io",
        "umwelts.kgents.io",
        "proposals.kgents.io",
    ]

    print("Verifying kgents CRDs...")
    print("=" * 40)

    result = subprocess.run(
        ["kubectl", "get", "crd", "-o", "json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Failed to query CRDs: {result.stderr}")
        return 1

    import json

    try:
        crd_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse CRD response")
        return 1

    installed = {
        item["metadata"]["name"]
        for item in crd_data.get("items", [])
        if "kgents.io" in item["metadata"]["name"]
    }

    all_healthy = True
    for crd in expected_crds:
        if crd in installed:
            # Check if CRD is established
            status_result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "crd",
                    crd,
                    "-o",
                    "jsonpath={.status.conditions[?(@.type=='Established')].status}",
                ],
                capture_output=True,
                text=True,
            )
            established = status_result.stdout.strip() == "True"
            if established:
                print(f"  {crd}: HEALTHY")
            else:
                print(f"  {crd}: DEGRADED (not established)")
                all_healthy = False
        else:
            print(f"  {crd}: MISSING")
            all_healthy = False

    print("\n" + "=" * 40)
    if all_healthy:
        print("All CRDs healthy.")
        return 0
    else:
        print("Some CRDs need attention. Run 'kgents infra crd' to install.")
        return 1


def _list_crds() -> int:
    """List installed kgents CRDs."""
    result = subprocess.run(
        ["kubectl", "get", "crd", "-o", "name"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Failed to list CRDs: {result.stderr}")
        return 1

    kgents_crds = [
        line.replace("customresourcedefinition.apiextensions.k8s.io/", "")
        for line in result.stdout.strip().split("\n")
        if "kgents.io" in line
    ]

    if kgents_crds:
        print("Installed kgents CRDs:")
        for crd in sorted(kgents_crds):
            print(f"  - {crd}")
    else:
        print("No kgents CRDs installed.")
        print("Run 'kgents infra crd' to install.")

    return 0


def _cmd_apply(args: list[str]) -> int:
    """
    Deploy an agent via CRD.

    Usage:
        kgents infra apply b-gent              # Deploy B-gent (placeholder mode)
        kgents infra apply b-gent --dry-run    # Preview without deploying
        kgents infra apply b-gent --full       # Deploy with real agent code
        kgents infra apply b-gent.yaml         # Deploy from file
        kgents infra apply --all               # Deploy all from spec/agents/
    """
    import asyncio

    from infra.k8s import (
        ClusterStatus,
        DeployMode,
        KindCluster,
        create_operator,
    )

    # Parse flags
    dry_run = "--dry-run" in args
    full_mode = "--full" in args
    remaining_args = [a for a in args if not a.startswith("--")]

    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("Cluster not running. Run 'kgents infra init' first.")
        return 1

    if not remaining_args:
        print("Usage: kgents infra apply <agent|file|--all> [--dry-run] [--full]")
        print()
        print("Options:")
        print("  --dry-run    Preview manifests without deploying")
        print("  --full       Deploy with real agent code (requires built image)")
        print("               Default is PLACEHOLDER mode (sleep container)")
        print()
        print("Examples:")
        print("  kgents infra apply b-gent           # Placeholder mode (safe)")
        print("  kgents infra apply b-gent --dry-run # Preview only")
        print("  kgents infra apply b-gent --full    # Real agent (needs image)")
        print("  kgents infra apply my-agent.yaml")
        print("  kgents infra apply --all")
        return 1

    target = remaining_args[0]

    # Determine deploy mode
    if dry_run:
        deploy_mode = DeployMode.DRY_RUN
    elif full_mode:
        deploy_mode = DeployMode.FULL
    else:
        deploy_mode = DeployMode.PLACEHOLDER

    # Ensure CRD is installed first
    operator = create_operator(on_progress=lambda msg: print(f"  {msg}"))
    asyncio.run(operator.apply_crd())

    if target == "--all":
        # Generate and apply all agents from spec/
        return _apply_all_agents(deploy_mode)
    elif target.endswith(".yaml") or target.endswith(".yml"):
        # Apply from file
        return _apply_from_file(Path(target), deploy_mode)
    else:
        # Apply single agent by name
        return _apply_agent_by_name(target, deploy_mode)


def _apply_all_agents(deploy_mode: "DeployMode") -> int:
    """Generate CRDs from specs and apply all."""
    from infra.k8s import DeployMode, SpecToCRDGenerator

    print("Generating CRDs from spec/agents/...")

    generator = SpecToCRDGenerator()
    result = generator.generate_all()

    if not result.success:
        print(f"Generation failed: {result.message}")
        for error in result.errors:
            print(f"  {error}")
        return 1

    if not result.generated:
        print("No agent specs found in spec/agents/")
        return 0

    print(f"Generated {len(result.generated)} CRDs")

    # Apply each generated CRD
    for crd_path in result.generated:
        print(f"\nApplying {crd_path.name}...")
        apply_result = subprocess.run(
            ["kubectl", "apply", "-f", str(crd_path)],
            capture_output=True,
            text=True,
        )
        if apply_result.returncode != 0:
            print(f"  Failed: {apply_result.stderr}")
        else:
            print(f"  Applied: {apply_result.stdout.strip()}")

    return 0


def _apply_from_file(path: Path, deploy_mode: "DeployMode") -> int:
    """Apply an Agent CRD from a YAML file."""
    import asyncio

    if not path.exists():
        print(f"File not found: {path}")
        return 1

    print(f"Applying {path}...")
    print(f"  Mode: {deploy_mode.value}")

    from infra.k8s import apply_agent_from_file

    # Note: apply_agent_from_file would need to be updated to accept deploy_mode
    result = asyncio.run(apply_agent_from_file(path))

    if result.success:
        print(f"Success: {result.message}")
        if result.created:
            print(f"  Created: {', '.join(result.created)}")
        if result.updated:
            print(f"  Updated: {', '.join(result.updated)}")
        return 0
    else:
        print(f"Failed: {result.message}")
        return 1


def _apply_agent_by_name(name: str, deploy_mode: "DeployMode") -> int:
    """Apply an agent by genus name (e.g., 'b-gent' or 'B')."""
    import asyncio

    from infra.k8s import AgentSpec, DeployMode, create_operator

    # Normalize name
    if name.endswith("-gent"):
        genus = name[:-5].upper()
    elif name.endswith("gent"):
        genus = name[:-4].upper()
    else:
        genus = name.upper()

    # Handle special case
    if genus.lower() == "psi":
        genus = "Psi"

    print(f"Deploying {genus}-gent...")
    print(f"  Mode: {deploy_mode.value}")

    # Create minimal spec with deploy mode
    spec = AgentSpec(
        name=f"{genus.lower()}-gent",
        namespace="kgents-agents",
        genus=genus,
        deploy_mode=deploy_mode,
    )

    # Check for spec file with more details
    spec_file = Path(f"spec/agents/{genus.lower()}-gent.md")
    if spec_file.exists():
        from infra.k8s import SpecParser

        parser = SpecParser()
        parsed = parser.parse_file(spec_file)
        if parsed:
            spec = AgentSpec(
                name=f"{parsed.genus.lower()}-gent",
                namespace="kgents-agents",
                genus=parsed.genus,
                image=parsed.image,
                replicas=parsed.replicas,
                cpu=parsed.cpu,
                memory=parsed.memory,
                sidecar_enabled=parsed.sidecar_enabled,
                entrypoint=parsed.entrypoint,
                config=parsed.config,
                allow_egress=parsed.allow_egress,
                allowed_peers=parsed.allowed_peers,
                deploy_mode=deploy_mode,
            )
            print(f"  Loaded config from {spec_file}")

    # Pre-deploy validation with warnings
    validation = spec.validate(check_image=True)
    if validation.warnings:
        print("\nWarnings:")
        for warning in validation.warnings:
            print(f"  ⚠ {warning}")

    if not validation.valid:
        print("\nPre-deploy validation failed:")
        for error in validation.errors:
            print(f"  ✗ {error}")
        print("\nHint: Use --dry-run to preview without deploying")
        print("      Use PLACEHOLDER mode (default) to test infra without real images")
        return 1

    operator = create_operator(on_progress=lambda msg: print(f"  {msg}"))
    result = asyncio.run(operator.reconcile_agent(spec))

    if result.success:
        print(f"\nSuccess: {result.message}")
        if result.created:
            print(f"  Created: {', '.join(result.created)}")
        if result.updated:
            print(f"  Updated: {', '.join(result.updated)}")

        if deploy_mode == DeployMode.PLACEHOLDER:
            print("\nNote: Deployed in PLACEHOLDER mode (sleep container)")
            print("  Use --full to deploy with real agent code")

        print("\nCheck status:")
        print(f"  kubectl get pods -n kgents-agents -l kgents.io/genus={genus}")
        return 0
    else:
        print(f"\nFailed: {result.message}")
        # Suggest cleanup if deployment might be stuck
        print("\nIf pods are stuck in CrashLoopBackOff, run:")
        print("  kgents infra cleanup")
        return 1


def _cmd_cleanup(args: list[str]) -> int:
    """
    Cleanup failed deployments (CrashLoopBackOff, ImagePullBackOff).

    Usage:
        kgents infra cleanup              # Cleanup kgents-agents namespace
        kgents infra cleanup --all        # Cleanup all kgents namespaces
        kgents infra cleanup --dry-run    # Show what would be cleaned
    """
    import asyncio

    from infra.k8s import ClusterStatus, KindCluster, create_operator

    dry_run = "--dry-run" in args
    all_ns = "--all" in args

    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("Cluster not running.")
        return 1

    namespaces = ["kgents-agents"]
    if all_ns:
        namespaces.append("kgents-ephemeral")

    print("K-Terrarium Cleanup")
    print("=" * 40)

    if dry_run:
        print("(dry-run mode - no changes will be made)\n")

    total_cleaned: list[str] = []

    for ns in namespaces:
        print(f"\nChecking {ns}...")
        operator = create_operator(
            namespace=ns, on_progress=lambda msg: print(f"  {msg}")
        )

        if dry_run:
            # Just report, don't delete
            import subprocess

            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", ns, "-o", "wide"],
                capture_output=True,
                text=True,
            )
            if (
                "CrashLoopBackOff" in result.stdout
                or "ImagePullBackOff" in result.stdout
            ):
                print("  Would clean up pods in error state")
        else:
            cleaned = asyncio.run(operator.cleanup_failed_deployments())
            total_cleaned.extend(cleaned)

    if not dry_run:
        if total_cleaned:
            print(f"\nCleaned up {len(total_cleaned)} deployment(s):")
            for name in total_cleaned:
                print(f"  - {name}")
        else:
            print("\nNo failed deployments found.")

    return 0
