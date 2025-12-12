"""
Agent Operator for K-Terrarium.

Watches Agent CRDs and reconciles Deployments. Runs in-cluster mirroring
the Kubernetes control plane pattern.

Reconciliation Loop:
1. Watch for Agent CRD changes
2. Compare desired state (CRD) vs actual state (Deployment)
3. Create/Update/Delete resources as needed
4. Update Agent status

Design Decisions:
- Uses kopf for operator framework (lightweight, pure Python)
- Falls back to kubectl for environments without kopf
- Generates Deployment + Service from Agent spec
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

from .exceptions import ClusterOperationError, ImageNotFoundError


class AgentPhase(Enum):
    """Agent lifecycle phases."""

    PENDING = "Pending"
    RUNNING = "Running"
    DEGRADED = "Degraded"
    FAILED = "Failed"
    TERMINATING = "Terminating"


class DeployMode(Enum):
    """How to deploy the agent."""

    FULL = "full"  # Real agent with code
    PLACEHOLDER = "placeholder"  # Sleep container for testing infra
    DRY_RUN = "dry_run"  # Don't actually deploy


@dataclass
class ValidationResult:
    """Result of spec validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class AgentSpec:
    """Parsed Agent CRD spec."""

    name: str
    namespace: str
    genus: str
    image: str = "python:3.12-slim"
    replicas: int = 1
    cpu: str = "100m"
    memory: str = "256Mi"
    sidecar_enabled: bool = True
    sidecar_image: str = "python:3.12-slim"
    entrypoint: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    allow_egress: bool = False
    allowed_peers: list[str] = field(default_factory=list)
    deploy_mode: DeployMode = DeployMode.PLACEHOLDER  # Safe default

    def validate(self, check_image: bool = False) -> ValidationResult:
        """
        Validate spec before deployment.

        Args:
            check_image: If True, verify image exists in Docker/Kind cluster.

        Returns ValidationResult with errors/warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Required fields
        if not self.genus:
            errors.append("genus is required")
        if not self.name:
            errors.append("name is required")

        # Image validation
        if self.image == "python:3.12-slim" and self.deploy_mode == DeployMode.FULL:
            warnings.append(
                "Using base Python image without agent code. "
                "Set deploy_mode=PLACEHOLDER or provide custom image."
            )

        # Check image exists (when requested and in FULL mode)
        if check_image and self.deploy_mode == DeployMode.FULL:
            image_result = self._check_image_exists()
            if image_result:
                errors.append(image_result)

        # Entrypoint validation
        if self.deploy_mode == DeployMode.FULL and not self.entrypoint:
            warnings.append(
                f"No entrypoint specified. Will try agents.{self.genus.lower()}.main"
            )

        # Validate entrypoint module exists (for custom images with kgents code)
        if self.deploy_mode == DeployMode.FULL and self.entrypoint:
            entrypoint_result = self._check_entrypoint()
            if entrypoint_result:
                warnings.append(entrypoint_result)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_image_exists(self) -> str | None:
        """
        Check if the image exists locally or in Kind cluster.

        Returns error message if not found, None if OK.
        """
        # Skip for common base images (they'll be pulled)
        base_images = {
            "python:3.12-slim",
            "python:3.11-slim",
            "python:3.12",
            "python:3.11",
            "alpine:latest",
            "busybox:latest",
        }
        if self.image in base_images:
            return None

        # Check if it's a kgents image that should be built
        if self.image.startswith("kgents/"):
            # Check if image exists locally
            result = subprocess.run(
                ["docker", "images", "-q", self.image],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if not result.stdout.strip():
                return (
                    f"Image '{self.image}' not found locally. "
                    f"Build it first with: docker build -t {self.image} <path>"
                )

            # Check if loaded into Kind
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "kgents-local-control-plane",
                    "crictl",
                    "images",
                    "-q",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Note: This is a heuristic - crictl output format varies
            # The main check is local Docker image existence
        return None

    def _check_entrypoint(self) -> str | None:
        """
        Check if entrypoint module likely exists.

        Returns warning message if not found, None if OK.
        """
        if not self.entrypoint:
            return None

        # Convert module path to file path
        # e.g., agents.b.main -> impl/claude/agents/b/main.py
        parts = self.entrypoint.split(".")
        if parts[0] == "agents" and len(parts) >= 2:
            # Check in impl/claude/agents/
            module_path = Path("impl/claude") / "/".join(parts[:-1]) / f"{parts[-1]}.py"
            if not module_path.exists():
                # Also check for __main__.py
                package_path = Path("impl/claude") / "/".join(parts)
                main_file = package_path / "__main__.py"
                if not main_file.exists():
                    return f"Entrypoint module '{self.entrypoint}' not found at {module_path}"
        return None

    @classmethod
    def from_crd(cls, manifest: dict[str, Any]) -> "AgentSpec":
        """Parse AgentSpec from CRD manifest."""
        metadata = manifest.get("metadata", {})
        spec = manifest.get("spec", {})
        resources = spec.get("resources", {})
        sidecar = spec.get("sidecar", {})
        network = spec.get("networkPolicy", {})

        return cls(
            name=metadata.get("name", ""),
            namespace=metadata.get("namespace", "kgents-agents"),
            genus=spec.get("genus", ""),
            image=spec.get("image", "python:3.12-slim"),
            replicas=spec.get("replicas", 1),
            cpu=resources.get("cpu", "100m"),
            memory=resources.get("memory", "256Mi"),
            sidecar_enabled=sidecar.get("enabled", True),
            sidecar_image=sidecar.get("image", "python:3.12-slim"),
            entrypoint=spec.get("entrypoint"),
            config=spec.get("config", {}),
            allow_egress=network.get("allowEgress", False),
            allowed_peers=network.get("allowedPeers", []),
        )

    def to_deployment(self) -> dict[str, Any]:
        """Generate Kubernetes Deployment from spec."""
        containers = [
            {
                "name": "logic",
                "image": self.image,
                "command": self._build_command(),
                "resources": {
                    "limits": {"cpu": self.cpu, "memory": self.memory},
                    "requests": {
                        "cpu": self._halve_resource(self.cpu),
                        "memory": self._halve_resource(self.memory),
                    },
                },
                "volumeMounts": [{"name": "state", "mountPath": "/state"}],
                "env": self._build_env(),
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "readOnlyRootFilesystem": True,
                    "allowPrivilegeEscalation": False,
                    "capabilities": {"drop": ["ALL"]},
                },
            }
        ]

        if self.sidecar_enabled:
            containers.append(
                {
                    "name": "d-gent",
                    "image": self.sidecar_image,
                    "command": ["python", "-m", "agents.d.sidecar"],
                    "resources": {
                        "limits": {"cpu": "50m", "memory": "128Mi"},
                        "requests": {"cpu": "25m", "memory": "64Mi"},
                    },
                    "volumeMounts": [{"name": "state", "mountPath": "/state"}],
                    "securityContext": {
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "readOnlyRootFilesystem": False,  # Sidecar writes state
                        "allowPrivilegeEscalation": False,
                    },
                }
            )

        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.genus.lower()}-gent",
                "namespace": self.namespace,
                "labels": self._labels(),
                # Note: ownerReferences would require Agent CRD to exist first
                # with a valid UID. For standalone deployment, we skip this.
            },
            "spec": {
                "replicas": self.replicas,
                "selector": {"matchLabels": self._labels()},
                "template": {
                    "metadata": {"labels": self._labels()},
                    "spec": {
                        "containers": containers,
                        "volumes": [{"name": "state", "emptyDir": {}}],
                        "securityContext": {"fsGroup": 1000},
                        "restartPolicy": "Always",
                    },
                },
            },
        }

    def to_service(self) -> dict[str, Any]:
        """Generate Kubernetes Service for the agent."""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.genus.lower()}-gent",
                "namespace": self.namespace,
                "labels": self._labels(),
            },
            "spec": {
                "selector": self._labels(),
                "ports": [{"port": 8080, "targetPort": 8080, "name": "http"}],
                "type": "ClusterIP",
            },
        }

    def to_network_policy(self) -> dict[str, Any] | None:
        """Generate NetworkPolicy if restrictions are defined."""
        if self.allow_egress and not self.allowed_peers:
            return None  # No restrictions needed

        egress: list[dict[str, Any]] = []
        if self.allow_egress:
            egress.append({})  # Allow all egress
        elif self.allowed_peers:
            # Only allow traffic to specific peers
            egress.append(
                {
                    "to": [
                        {"podSelector": {"matchLabels": {"kgents.io/genus": peer}}}
                        for peer in self.allowed_peers
                    ]
                }
            )

        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{self.genus.lower()}-gent-policy",
                "namespace": self.namespace,
            },
            "spec": {
                "podSelector": {"matchLabels": self._labels()},
                "policyTypes": ["Egress"],
                "egress": egress if egress else [],
            },
        }

    def _labels(self) -> dict[str, str]:
        """Standard labels for all resources."""
        return {
            "app.kubernetes.io/name": f"{self.genus.lower()}-gent",
            "app.kubernetes.io/part-of": "kgents",
            "app.kubernetes.io/managed-by": "agent-operator",
            "kgents.io/genus": self.genus,
        }

    def _build_command(self) -> list[str]:
        """Build container command based on deploy mode."""
        if self.deploy_mode == DeployMode.PLACEHOLDER:
            # Sleep indefinitely - placeholder for infra testing
            # This prevents CrashLoopBackOff when no real agent code exists
            return [
                "sh",
                "-c",
                f"echo '{self.genus}-gent placeholder running' && sleep infinity",
            ]

        if self.entrypoint:
            return ["python", "-m", self.entrypoint]
        return ["python", "-m", f"agents.{self.genus.lower()}.main"]

    def _build_env(self) -> list[dict[str, str]]:
        """Build environment variables."""
        env = [
            {"name": "KGENTS_GENUS", "value": self.genus},
            {"name": "KGENTS_STATE_PATH", "value": "/state"},
        ]
        for key, value in self.config.items():
            env.append({"name": f"KGENTS_{key.upper()}", "value": str(value)})
        return env

    def _halve_resource(self, resource: str) -> str:
        """Halve a resource value for requests."""
        if resource.endswith("m"):
            return f"{int(resource[:-1]) // 2}m"
        if resource.endswith("Mi"):
            return f"{int(resource[:-2]) // 2}Mi"
        if resource.endswith("Gi"):
            # Convert to Mi and halve
            return f"{int(resource[:-2]) * 512}Mi"
        return resource


@dataclass
class ReconcileResult:
    """Result of a reconciliation operation."""

    success: bool
    message: str
    phase: AgentPhase = AgentPhase.PENDING
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)


class AgentOperator:
    """
    Kubernetes Operator for Agent CRDs.

    Watches Agent resources and ensures corresponding Deployments exist.

    Example:
        operator = AgentOperator()

        # Reconcile a single agent
        result = await operator.reconcile_agent(agent_spec)

        # Start watch loop (blocking)
        await operator.run()
    """

    def __init__(
        self,
        namespace: str = "kgents-agents",
        on_progress: Callable[[str], None] | None = None,
    ):
        self.namespace = namespace
        self._on_progress = on_progress or (lambda msg: None)
        self._manifests_dir = Path(__file__).parent / "manifests"

    async def reconcile_agent(
        self, spec: AgentSpec, check_image: bool = True
    ) -> ReconcileResult:
        """
        Reconcile a single Agent CRD to its desired state.

        Creates or updates Deployment, Service, and NetworkPolicy.

        Args:
            spec: Agent specification to deploy.
            check_image: Validate image exists before deploying (prevents CrashLoopBackOff).
        """
        self._on_progress(f"Reconciling {spec.genus}-gent...")

        # Validate spec first (with image check for FULL mode)
        validation = spec.validate(check_image=check_image)
        if not validation.valid:
            return ReconcileResult(
                success=False,
                message=f"Validation failed: {', '.join(validation.errors)}",
                phase=AgentPhase.FAILED,
            )

        # Report warnings
        for warning in validation.warnings:
            self._on_progress(f"Warning: {warning}")

        # Handle dry-run mode
        if spec.deploy_mode == DeployMode.DRY_RUN:
            deployment = spec.to_deployment()
            import json

            self._on_progress("Dry-run mode - not applying resources")
            return ReconcileResult(
                success=True,
                message=f"Dry-run: would create deployment for {spec.genus}-gent",
                phase=AgentPhase.PENDING,
            )

        # Report placeholder mode
        if spec.deploy_mode == DeployMode.PLACEHOLDER:
            self._on_progress(
                "Deploying in PLACEHOLDER mode (sleep container, no agent code)"
            )

        created: list[str] = []
        updated: list[str] = []

        try:
            # Generate manifests
            deployment = spec.to_deployment()
            service = spec.to_service()
            network_policy = spec.to_network_policy()

            # Apply deployment
            dep_result = await self._apply_resource(deployment)
            if dep_result == "created":
                created.append(f"deployment/{spec.genus.lower()}-gent")
            elif dep_result == "configured":
                updated.append(f"deployment/{spec.genus.lower()}-gent")

            # Apply service
            svc_result = await self._apply_resource(service)
            if svc_result == "created":
                created.append(f"service/{spec.genus.lower()}-gent")
            elif svc_result == "configured":
                updated.append(f"service/{spec.genus.lower()}-gent")

            # Apply network policy if defined
            if network_policy:
                np_result = await self._apply_resource(network_policy)
                if np_result == "created":
                    created.append(f"networkpolicy/{spec.genus.lower()}-gent-policy")
                elif np_result == "configured":
                    updated.append(f"networkpolicy/{spec.genus.lower()}-gent-policy")

            # Update CRD status
            await self._update_status(spec, AgentPhase.RUNNING)

            return ReconcileResult(
                success=True,
                message=f"Reconciled {spec.genus}-gent successfully",
                phase=AgentPhase.RUNNING,
                created=created,
                updated=updated,
            )

        except Exception as e:
            await self._update_status(spec, AgentPhase.FAILED, str(e))
            return ReconcileResult(
                success=False,
                message=f"Failed to reconcile: {e}",
                phase=AgentPhase.FAILED,
            )

    async def delete_agent(self, spec: AgentSpec) -> ReconcileResult:
        """Delete all resources for an agent."""
        self._on_progress(f"Deleting {spec.genus}-gent...")
        deleted = []

        resources = [
            ("deployment", f"{spec.genus.lower()}-gent"),
            ("service", f"{spec.genus.lower()}-gent"),
            ("networkpolicy", f"{spec.genus.lower()}-gent-policy"),
        ]

        for kind, name in resources:
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "delete",
                        kind,
                        name,
                        "-n",
                        spec.namespace,
                        "--ignore-not-found",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if "deleted" in result.stdout.lower():
                    deleted.append(f"{kind}/{name}")
            except Exception:
                pass

        return ReconcileResult(
            success=True,
            message=f"Deleted {spec.genus}-gent",
            phase=AgentPhase.TERMINATING,
            deleted=deleted,
        )

    async def cleanup_failed_deployments(
        self, namespace: str | None = None
    ) -> list[str]:
        """
        Auto-cleanup deployments in CrashLoopBackOff or ImagePullBackOff.

        Returns list of cleaned up deployment names.
        """
        ns = namespace or self.namespace
        cleaned: list[str] = []

        try:
            # Get pods with problem statuses
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    ns,
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return cleaned

            pods = json.loads(result.stdout)
            failed_deployments: set[str] = set()

            for pod in pods.get("items", []):
                status = pod.get("status", {})
                container_statuses = status.get("containerStatuses", [])

                for cs in container_statuses:
                    waiting = cs.get("waiting", {})
                    reason = waiting.get("reason", "")

                    if reason in (
                        "CrashLoopBackOff",
                        "ImagePullBackOff",
                        "ErrImagePull",
                        "InvalidImageName",
                    ):
                        # Get the deployment name from labels
                        labels = pod.get("metadata", {}).get("labels", {})
                        app_name = labels.get("app.kubernetes.io/name")
                        if app_name:
                            failed_deployments.add(app_name)
                            self._on_progress(
                                f"Found failed pod: {app_name} ({reason})"
                            )

            # Delete failed deployments
            for deploy_name in failed_deployments:
                try:
                    result = subprocess.run(
                        [
                            "kubectl",
                            "delete",
                            "deployment",
                            deploy_name,
                            "-n",
                            ns,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        cleaned.append(deploy_name)
                        self._on_progress(f"Cleaned up: {deploy_name}")
                except Exception:
                    pass

        except Exception as e:
            self._on_progress(f"Cleanup error: {e}")

        return cleaned

    async def list_agents(self) -> list[AgentSpec]:
        """List all Agent CRDs in the namespace."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "agents.kgents.io",
                    "-n",
                    self.namespace,
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
            return [AgentSpec.from_crd(item) for item in data.get("items", [])]

        except Exception:
            return []

    async def apply_crd(self) -> bool:
        """Apply the Agent CRD definition to the cluster."""
        crd_path = self._manifests_dir / "agent-crd.yaml"
        if not crd_path.exists():
            return False

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(crd_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _apply_resource(self, manifest: dict[str, Any]) -> str:
        """Apply a resource and return 'created', 'configured', or 'unchanged'."""
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", "-", "-o", "name"],
                input=json.dumps(manifest),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise ClusterOperationError("apply", result.stderr)

            # Parse kubectl output to determine if created or configured
            # Output is like "deployment.apps/b-gent created" or "configured"
            output = result.stderr.lower()
            if "created" in output:
                return "created"
            if "configured" in output:
                return "configured"
            return "unchanged"

        except subprocess.TimeoutExpired:
            raise ClusterOperationError("apply", "kubectl apply timed out")

    async def _update_status(
        self,
        spec: AgentSpec,
        phase: AgentPhase,
        message: str = "",
    ) -> None:
        """Update the Agent CRD status subresource."""
        status: dict[str, Any] = {
            "phase": phase.value,
            "observedGeneration": 1,  # Would get from CRD
        }

        if message:
            status["conditions"] = [
                {
                    "type": "Ready" if phase == AgentPhase.RUNNING else "Failed",
                    "status": "True" if phase == AgentPhase.RUNNING else "False",
                    "reason": phase.value,
                    "message": message,
                }
            ]

        status_patch = {"status": status}

        try:
            subprocess.run(
                [
                    "kubectl",
                    "patch",
                    "agent",
                    spec.name,
                    "-n",
                    spec.namespace,
                    "--type=merge",
                    "--subresource=status",
                    "-p",
                    json.dumps(status_patch),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception:
            pass  # Status update is best-effort


def create_operator(
    namespace: str = "kgents-agents",
    on_progress: Callable[[str], None] | None = None,
) -> AgentOperator:
    """Factory function for AgentOperator."""
    return AgentOperator(namespace=namespace, on_progress=on_progress)


async def apply_agent_from_file(path: Path) -> ReconcileResult:
    """Apply an Agent CRD from a YAML file."""
    import yaml

    with open(path) as f:
        manifest = yaml.safe_load(f)

    spec = AgentSpec.from_crd(manifest)
    operator = create_operator()
    return await operator.reconcile_agent(spec)
