"""
MCP Resources - Expose K8s cluster state as MCP resources.

Phase E of K8gents operationalization. Allows Claude Code to query:
- kgents://agents           -> List Agent CRs
- kgents://agents/{name}    -> Agent status
- kgents://pheromones       -> Active pheromones
- kgents://cluster/status   -> Cluster health

MCP Resources are read-only data sources identified by URIs.
Unlike tools, resources are passive (read) rather than active (write).

AGENTESE: world.k8s.resources
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MCPResource:
    """MCP Resource definition."""

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
        }


@dataclass
class MCPResourceContent:
    """Content returned from a resource."""

    uri: str
    content: str
    mime_type: str = "application/json"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "mimeType": self.mime_type,
            "text": self.content,
        }


@dataclass
class K8sConfig:
    """Kubernetes connection configuration."""

    namespace: str = "kgents-agents"
    kubeconfig: str | None = None
    context: str | None = None

    @classmethod
    def from_env(cls) -> K8sConfig:
        """Create config from environment."""
        import os

        return cls(
            namespace=os.environ.get("KGENTS_NAMESPACE", "kgents-agents"),
            kubeconfig=os.environ.get("KUBECONFIG"),
            context=os.environ.get("KGENTS_K8S_CONTEXT"),
        )


class K8sResourceProvider:
    """
    Kubernetes resource provider for MCP.

    Queries the K8s cluster for agent and pheromone state.
    Uses kubectl for simplicity (no kubernetes-client dependency).
    """

    def __init__(self, config: K8sConfig | None = None) -> None:
        self.config = config or K8sConfig.from_env()
        self._kubectl_available: bool | None = None

    def _kubectl_cmd(self) -> list[str]:
        """Build base kubectl command with config."""
        cmd = ["kubectl"]
        if self.config.kubeconfig:
            cmd.extend(["--kubeconfig", self.config.kubeconfig])
        if self.config.context:
            cmd.extend(["--context", self.config.context])
        return cmd

    def _run_kubectl(self, *args: str, timeout: int = 10) -> dict[str, Any] | None:
        """Run kubectl command and return parsed JSON output."""
        if self._kubectl_available is False:
            return None

        cmd = self._kubectl_cmd() + list(args) + ["-o", "json"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                logger.warning(f"kubectl failed: {result.stderr}")
                return None

            self._kubectl_available = True
            return dict(json.loads(result.stdout))

        except FileNotFoundError:
            logger.warning("kubectl not found")
            self._kubectl_available = False
            return None
        except subprocess.TimeoutExpired:
            logger.warning("kubectl timed out")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"kubectl output parse error: {e}")
            return None

    def _run_kubectl_text(self, *args: str, timeout: int = 10) -> str | None:
        """Run kubectl command and return raw text output."""
        if self._kubectl_available is False:
            return None

        cmd = self._kubectl_cmd() + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return None
            self._kubectl_available = True
            return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

    def list_resources(self) -> list[MCPResource]:
        """Return list of available resources."""
        return [
            MCPResource(
                uri="kgents://agents",
                name="Agent CRs",
                description="List all Agent custom resources in the cluster",
            ),
            MCPResource(
                uri="kgents://pheromones",
                name="Pheromones",
                description="List active pheromone signals between agents",
            ),
            MCPResource(
                uri="kgents://cluster/status",
                name="Cluster Status",
                description="Overall kgents cluster health and status",
            ),
        ]

    def list_resource_templates(self) -> list[dict[str, Any]]:
        """Return resource templates for dynamic URIs."""
        return [
            {
                "uriTemplate": "kgents://agents/{name}",
                "name": "Agent Details",
                "description": "Get detailed status for a specific agent",
                "mimeType": "application/json",
            }
        ]

    async def read_resource(self, uri: str) -> MCPResourceContent:
        """Read resource content by URI."""
        # Parse URI
        if not uri.startswith("kgents://"):
            return MCPResourceContent(
                uri=uri,
                content=json.dumps({"error": f"Unknown URI scheme: {uri}"}),
            )

        path = uri[len("kgents://") :]

        # Route to handler
        if path == "agents":
            return await self._read_agents()
        elif path.startswith("agents/"):
            agent_name = path[len("agents/") :]
            return await self._read_agent(agent_name)
        elif path == "pheromones":
            return await self._read_pheromones()
        elif path == "cluster/status":
            return await self._read_cluster_status()
        else:
            return MCPResourceContent(
                uri=uri,
                content=json.dumps({"error": f"Unknown resource: {path}"}),
            )

    async def _read_agents(self) -> MCPResourceContent:
        """List all Agent CRs."""
        # Try to get Agent CRs
        result = self._run_kubectl(
            "get", "agents.kgents.io", "-n", self.config.namespace
        )

        if result is None:
            # Fallback: get pods with kgents labels
            result = self._run_kubectl(
                "get",
                "pods",
                "-n",
                self.config.namespace,
                "-l",
                "app.kubernetes.io/part-of=kgents",
            )

        if result is None:
            return MCPResourceContent(
                uri="kgents://agents",
                content=json.dumps(
                    {
                        "error": "Cannot connect to cluster",
                        "hint": "Is kubectl configured? Is the cluster running?",
                    }
                ),
            )

        # Extract agent info
        agents = []
        items = result.get("items", [])
        for item in items:
            metadata = item.get("metadata", {})
            status = item.get("status", {})
            spec = item.get("spec", {})

            agent_info = {
                "name": metadata.get("name"),
                "namespace": metadata.get("namespace"),
                "phase": status.get("phase", "Unknown"),
                "ready": status.get("ready", False),
                "genus": spec.get("genus") or metadata.get("labels", {}).get("genus"),
                "created": metadata.get("creationTimestamp"),
            }

            # If this is a pod (fallback), extract from labels
            if "containerStatuses" in status:
                agent_info["phase"] = (
                    "Running"
                    if status.get("phase") == "Running"
                    else status.get("phase")
                )
                agent_info["ready"] = all(
                    cs.get("ready", False) for cs in status.get("containerStatuses", [])
                )

            agents.append(agent_info)

        return MCPResourceContent(
            uri="kgents://agents",
            content=json.dumps(
                {
                    "agents": agents,
                    "count": len(agents),
                    "namespace": self.config.namespace,
                },
                indent=2,
            ),
        )

    async def _read_agent(self, name: str) -> MCPResourceContent:
        """Get detailed status for a specific agent."""
        uri = f"kgents://agents/{name}"

        # Try Agent CR first
        result = self._run_kubectl(
            "get", f"agents.kgents.io/{name}", "-n", self.config.namespace
        )

        if result is None:
            # Fallback: try to get pod
            result = self._run_kubectl(
                "get", f"pod/{name}", "-n", self.config.namespace
            )

        if result is None:
            # Try deployment
            result = self._run_kubectl(
                "get", f"deployment/{name}", "-n", self.config.namespace
            )

        if result is None:
            return MCPResourceContent(
                uri=uri,
                content=json.dumps(
                    {
                        "error": f"Agent not found: {name}",
                        "namespace": self.config.namespace,
                    }
                ),
            )

        # Extract relevant info
        metadata = result.get("metadata", {})
        status = result.get("status", {})
        spec = result.get("spec", {})

        agent_detail = {
            "name": metadata.get("name"),
            "namespace": metadata.get("namespace"),
            "kind": result.get("kind"),
            "phase": status.get("phase"),
            "ready": status.get("ready"),
            "conditions": status.get("conditions", []),
            "created": metadata.get("creationTimestamp"),
            "labels": metadata.get("labels", {}),
            "annotations": metadata.get("annotations", {}),
        }

        # Add spec details for Agent CR
        if result.get("kind") == "Agent":
            agent_detail.update(
                {
                    "genus": spec.get("genus"),
                    "deployMode": spec.get("deployMode"),
                    "replicas": spec.get("replicas"),
                    "resources": spec.get("resources"),
                    "image": spec.get("image"),
                }
            )

        return MCPResourceContent(
            uri=uri,
            content=json.dumps(agent_detail, indent=2),
        )

    async def _read_pheromones(self) -> MCPResourceContent:
        """List active pheromone signals.

        PASSIVE STIGMERGY (v2.0): Intensity is calculated on read using the
        decay function, not stored in status.
        """
        # Try to get Pheromone CRs
        result = self._run_kubectl(
            "get", "pheromones.kgents.io", "-n", self.config.namespace
        )

        if result is None:
            # Pheromones might be stored in ConfigMaps (legacy)
            result = self._run_kubectl(
                "get",
                "configmaps",
                "-n",
                self.config.namespace,
                "-l",
                "kgents.io/type=pheromone",
            )

        pheromones = []
        if result and "items" in result:
            for item in result["items"]:
                metadata = item.get("metadata", {})
                spec = item.get("spec", {})
                data = item.get("data", {})

                # Calculate current intensity (Passive Stigmergy)
                current_intensity = self._calculate_pheromone_intensity(spec, metadata)

                pheromone = {
                    "name": metadata.get("name"),
                    "type": spec.get("type") or data.get("type", "unknown"),
                    "source": spec.get("source") or data.get("source"),
                    "target": spec.get("target") or data.get("target"),
                    # Current intensity calculated on read
                    "intensity": current_intensity,
                    # Also include decay parameters for transparency
                    "initialIntensity": spec.get(
                        "initialIntensity", spec.get("intensity")
                    ),
                    "halfLifeMinutes": spec.get("halfLifeMinutes"),
                    "emittedAt": spec.get("emittedAt"),
                    "created": metadata.get("creationTimestamp"),
                    "phase": item.get("status", {}).get("phase", "ACTIVE"),
                }
                pheromones.append(pheromone)

        return MCPResourceContent(
            uri="kgents://pheromones",
            content=json.dumps(
                {
                    "pheromones": pheromones,
                    "count": len(pheromones),
                    "namespace": self.config.namespace,
                    "note": "Intensity calculated on read (Passive Stigmergy v2.0)",
                },
                indent=2,
            ),
        )

    def _calculate_pheromone_intensity(
        self,
        spec: dict[str, Any],
        metadata: dict[str, Any],
    ) -> float:
        """Calculate current pheromone intensity from decay parameters.

        PASSIVE STIGMERGY: This mirrors the operator's calculate_intensity()
        function. Intensity is derived from stored parameters, not status.

        Formula: intensity(t) = initialIntensity * (0.5 ^ (elapsed / halfLife))
        """
        from datetime import datetime

        # Get emission time (prefer emittedAt, fallback to creationTimestamp)
        emitted_str = spec.get("emittedAt") or metadata.get("creationTimestamp")

        # Handle legacy pheromones without emittedAt
        if not emitted_str:
            return float(spec.get("intensity", spec.get("initialIntensity", 1.0)))

        try:
            emitted_at = datetime.fromisoformat(emitted_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return float(spec.get("initialIntensity", spec.get("intensity", 1.0)))

        # Get decay parameters
        initial = spec.get("initialIntensity", spec.get("intensity", 1.0))
        half_life = spec.get("halfLifeMinutes", 10.0)

        # Legacy conversion: decay_rate to half_life
        if "decay_rate" in spec and "halfLifeMinutes" not in spec:
            decay_rate = spec["decay_rate"]
            if decay_rate > 0:
                half_life = 0.693 / decay_rate  # ln(2) / decay_rate

        # Apply type-specific multiplier for DREAM pheromones
        pheromone_type = spec.get("type", "STATE")
        if pheromone_type == "DREAM":
            half_life *= 2.0  # DREAM pheromones last twice as long

        # Calculate elapsed time
        from datetime import timezone as tz

        now = datetime.now(tz.utc)
        elapsed_minutes = (
            now - emitted_at.replace(tzinfo=tz.utc)
        ).total_seconds() / 60.0

        # Exponential decay: intensity = initial * (0.5 ^ (elapsed / half_life))
        intensity = float(initial) * (0.5 ** (elapsed_minutes / half_life))

        return float(round(max(0.0, min(1.0, intensity)), 4))

    async def _read_cluster_status(self) -> MCPResourceContent:
        """Get overall cluster health."""
        status: dict[str, Any] = {
            "healthy": True,
            "namespace": self.config.namespace,
            "components": {},
            "issues": [],
        }

        # Check namespace exists
        ns_result = self._run_kubectl("get", "namespace", self.config.namespace)
        if ns_result is None:
            status["healthy"] = False
            status["issues"].append(f"Namespace '{self.config.namespace}' not found")
            return MCPResourceContent(
                uri="kgents://cluster/status",
                content=json.dumps(status, indent=2),
            )

        # Get pods
        pods_result = self._run_kubectl("get", "pods", "-n", self.config.namespace)
        if pods_result:
            pods = pods_result.get("items", [])
            running = sum(
                1 for p in pods if p.get("status", {}).get("phase") == "Running"
            )
            total = len(pods)
            status["components"]["pods"] = {
                "running": running,
                "total": total,
                "healthy": running == total,
            }
            if running < total:
                status["healthy"] = False
                status["issues"].append(f"{total - running} pod(s) not running")

        # Check operator
        operator_result = self._run_kubectl(
            "get",
            "deployment/kgents-operator",
            "-n",
            self.config.namespace,
        )
        if operator_result:
            op_status = operator_result.get("status", {})
            ready = op_status.get("readyReplicas", 0)
            desired = op_status.get("replicas", 1)
            status["components"]["operator"] = {
                "ready": ready,
                "desired": desired,
                "healthy": ready >= desired,
            }
            if ready < desired:
                status["healthy"] = False
                status["issues"].append("Operator not ready")

        # Check L-gent
        lgent_result = self._run_kubectl(
            "get",
            "deployment/l-gent",
            "-n",
            self.config.namespace,
        )
        if lgent_result:
            lg_status = lgent_result.get("status", {})
            ready = lg_status.get("readyReplicas", 0)
            desired = lg_status.get("replicas", 1)
            status["components"]["l-gent"] = {
                "ready": ready,
                "desired": desired,
                "healthy": ready >= desired,
            }
            if ready < desired:
                status["healthy"] = False
                status["issues"].append("L-gent not ready")

        # Check CRDs
        crd_result = self._run_kubectl_text("get", "crd", "agents.kgents.io")
        status["components"]["agent_crd"] = {
            "installed": crd_result is not None,
        }

        return MCPResourceContent(
            uri="kgents://cluster/status",
            content=json.dumps(status, indent=2),
        )


# Global provider instance
_provider: K8sResourceProvider | None = None


def get_provider() -> K8sResourceProvider:
    """Get or create the K8s resource provider."""
    global _provider
    if _provider is None:
        _provider = K8sResourceProvider()
    return _provider


# Exported resources for registration
KGENTS_RESOURCES = [
    MCPResource(
        uri="kgents://agents",
        name="Agent CRs",
        description="List all Agent custom resources in the kgents cluster",
    ),
    MCPResource(
        uri="kgents://pheromones",
        name="Pheromones",
        description="List active pheromone signals between agents",
    ),
    MCPResource(
        uri="kgents://cluster/status",
        name="Cluster Status",
        description="Overall kgents cluster health and status",
    ),
]

KGENTS_RESOURCE_TEMPLATES = [
    {
        "uriTemplate": "kgents://agents/{name}",
        "name": "Agent Details",
        "description": "Get detailed status for a specific agent by name",
        "mimeType": "application/json",
    }
]
