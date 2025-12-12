"""
Logos Resolver - Stateless AGENTESE → K8s translation.

This is NOT the Cortex. This is a thin translation layer that maps
AGENTESE paths to Kubernetes API calls. No state, no orchestration.

AGENTESE: world.cluster.logos

The Cortex Lobotomy (K8-Terrarium v2.0):
  - CortexServicer (1,217 lines) was a God Object violating Heterarchy
  - LogosResolver (~200 lines) is a stateless translation layer
  - Business logic moved to Agent Operator (Left Brain) and L-gent (Right Brain)

Design Principles:
  - NO STATE: Pure translation from AGENTESE paths to K8s API calls
  - NO ORCHESTRATION: Just mapping, no coordination logic
  - AFFORDANCE-AWARE: Returns handles that check observer permissions
  - LAZY REIFICATION: Pheromone intensity calculated on read (Passive Stigmergy)
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

# =============================================================================
# K8s Noun → AGENTESE Verb Ontology Mapping
# =============================================================================

ONTOLOGY_MAP: dict[tuple[str, str], dict[str, Any]] = {
    # World Context - External entities
    ("world", "cluster.workload"): {
        "api_group": "",
        "api_version": "v1",
        "kind": "Pod",
        "plural": "pods",
        "affordances": ["manifest", "witness", "terminate"],
    },
    ("world", "cluster.deployment"): {
        "api_group": "apps",
        "api_version": "v1",
        "kind": "Deployment",
        "plural": "deployments",
        "affordances": ["manifest", "scale", "rollback"],
    },
    ("world", "cluster.agent"): {
        "api_group": "kgents.io",
        "api_version": "v1",
        "kind": "Agent",
        "plural": "agents",
        "affordances": ["manifest", "scale", "terminate", "tether"],
    },
    # Void Context - Pheromones and entropy
    ("void", "pheromone"): {
        "api_group": "kgents.io",
        "api_version": "v1",
        "kind": "Pheromone",
        "plural": "pheromones",
        "affordances": ["sense", "emit", "witness"],
    },
    # Self Context - Memory and governance
    ("self", "memory.store"): {
        "api_group": "kgents.io",
        "api_version": "v1",
        "kind": "Memory",
        "plural": "memories",
        "affordances": ["manifest", "define", "compost"],
    },
    ("self", "governance.proposal"): {
        "api_group": "kgents.io",
        "api_version": "v1",
        "kind": "Proposal",
        "plural": "proposals",
        "affordances": ["define", "approve", "reject", "witness"],
    },
    ("self", "umwelt"): {
        "api_group": "kgents.io",
        "api_version": "v1",
        "kind": "Umwelt",
        "plural": "umwelts",
        "affordances": ["manifest", "refine"],
    },
    ("self", "memory.secret"): {
        "api_group": "",
        "api_version": "v1",
        "kind": "Secret",
        "plural": "secrets",
        "affordances": ["manifest", "define"],  # manifest only if owner
    },
    ("self", "memory.config"): {
        "api_group": "",
        "api_version": "v1",
        "kind": "ConfigMap",
        "plural": "configmaps",
        "affordances": ["manifest", "define", "refine"],
    },
    # Time Context - Events and traces
    ("time", "trace.witness"): {
        "api_group": "",
        "api_version": "v1",
        "kind": "Event",
        "plural": "events",
        "affordances": ["witness"],
    },
}


# =============================================================================
# Handle and Observer Protocols
# =============================================================================


@dataclass
class Handle:
    """
    A handle to a K8s resource with observer-specific affordances.

    This is what AGENTESE returns: not the resource itself, but a
    morphism that maps Observer → Interaction.

    The same handle yields different affordances to different observers.
    """

    resource: dict[str, Any]
    affordances: list[str]
    namespace: str = "kgents-agents"
    name: str | None = None

    def can(self, verb: str) -> bool:
        """Check if this handle affords the given verb."""
        return verb in self.affordances


class UmweltProtocol(Protocol):
    """Protocol for observer identity."""

    spiffe_id: str
    affordance_patterns: list[str]


# =============================================================================
# LogosResolver - Stateless AGENTESE → K8s Translation
# =============================================================================


class LogosResolver:
    """
    Stateless AGENTESE → K8s translation layer.

    This is the Logos for world.cluster.* context. It resolves
    AGENTESE paths to Kubernetes API handles.

    NO STATE. NO ORCHESTRATION. PURE TRANSLATION.

    Usage:
        resolver = LogosResolver()
        handle = await resolver.resolve("world.cluster.agent.my-agent", observer)
        if handle.can("manifest"):
            result = await resolver.invoke(handle, "manifest")
    """

    def __init__(self, namespace: str = "kgents-agents"):
        self.namespace = namespace
        self._kubectl_available: bool | None = None

    def parse_path(self, path: str) -> tuple[str, str, str | None, str | None]:
        """
        Parse AGENTESE path into components.

        Returns: (context, entity, name, aspect)

        Examples:
            "world.cluster.agent" → ("world", "cluster.agent", None, None)
            "world.cluster.agent.my-agent" → ("world", "cluster.agent", "my-agent", None)
            "world.cluster.agent.my-agent.manifest" → ("world", "cluster.agent", "my-agent", "manifest")
        """
        parts = path.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid AGENTESE path: {path}")

        context = parts[0]

        # Find the entity by matching against ontology (longest match first)
        for i in range(len(parts) - 1, 0, -1):
            candidate = ".".join(parts[1 : i + 1])
            if (context, candidate) in ONTOLOGY_MAP:
                entity = candidate
                remaining = parts[i + 1 :]
                name = remaining[0] if remaining else None
                aspect = remaining[1] if len(remaining) > 1 else None
                return (context, entity, name, aspect)

        # Fallback: assume parts[1] is entity
        entity = parts[1]
        name = parts[2] if len(parts) > 2 else None
        aspect = parts[3] if len(parts) > 3 else None
        return (context, entity, name, aspect)

    async def resolve(
        self,
        path: str,
        observer: UmweltProtocol | None = None,
    ) -> Handle:
        """
        Resolve AGENTESE path to K8s handle.

        Args:
            path: AGENTESE path (e.g., "world.cluster.agent.my-agent")
            observer: The observer's Umwelt (for affordance filtering)

        Returns:
            Handle with observer-appropriate affordances
        """
        context, entity, name, aspect = self.parse_path(path)

        # Look up in ontology
        key = (context, entity)
        if key not in ONTOLOGY_MAP:
            raise ValueError(f"Unknown AGENTESE entity: {context}.{entity}")

        resource = ONTOLOGY_MAP[key]

        # Filter affordances by observer permissions
        affordances = resource["affordances"].copy()
        if observer is not None:
            affordances = self._filter_affordances(affordances, observer, resource)

        return Handle(
            resource=resource,
            affordances=affordances,
            namespace=self.namespace,
            name=name,
        )

    def _filter_affordances(
        self,
        affordances: list[str],
        observer: UmweltProtocol,
        resource: dict[str, Any],
    ) -> list[str]:
        """
        Filter affordances based on observer's Umwelt.

        In a full implementation, this would check:
        1. Observer's affordance_patterns (glob matching)
        2. K8s RBAC permissions for observer's SPIFFE ID
        """
        if not hasattr(observer, "affordance_patterns"):
            return affordances

        # Check observer's affordance patterns
        filtered = []
        for aff in affordances:
            for pattern in observer.affordance_patterns:
                if self._matches_pattern(aff, pattern):
                    filtered.append(aff)
                    break
        return filtered if filtered else affordances

    def _matches_pattern(self, affordance: str, pattern: str) -> bool:
        """Simple pattern matching for affordances."""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return affordance.startswith(prefix) or affordance == prefix
        return affordance == pattern

    async def invoke(
        self,
        handle: Handle,
        aspect: str,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an aspect on a handle.

        This is where AGENTESE verbs become K8s API calls.
        """
        if not handle.can(aspect):
            raise PermissionError(f"Handle does not afford '{aspect}'")

        if aspect == "manifest":
            return await self._invoke_manifest(handle, **kwargs)
        elif aspect == "witness":
            return await self._invoke_witness(handle, **kwargs)
        elif aspect == "terminate":
            return await self._invoke_terminate(handle, **kwargs)
        elif aspect == "sense":
            return await self._invoke_sense(handle, **kwargs)
        elif aspect == "emit":
            return await self._invoke_emit(handle, **kwargs)
        elif aspect == "scale":
            return await self._invoke_scale(handle, **kwargs)
        else:
            raise NotImplementedError(f"Aspect '{aspect}' not implemented")

    # =========================================================================
    # Aspect Implementations
    # =========================================================================

    async def _invoke_manifest(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Get resource manifest (kubectl get)."""
        resource = handle.resource
        cmd = ["kubectl", "get"]

        if resource["api_group"]:
            cmd.append(f"{resource['plural']}.{resource['api_group']}")
        else:
            cmd.append(resource["plural"])

        if handle.name:
            cmd.append(handle.name)

        cmd.extend(["-n", handle.namespace, "-o", "json"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {"error": result.stderr}

        return dict(json.loads(result.stdout))

    async def _invoke_witness(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Get resource history/logs."""
        resource = handle.resource

        if resource["kind"] == "Pod" and handle.name:
            cmd = [
                "kubectl",
                "logs",
                handle.name,
                "-n",
                handle.namespace,
                "--tail=100",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "logs": result.stdout,
                "error": result.stderr if result.returncode else None,
            }

        # Default: return events for the resource
        return await self._get_events(handle)

    async def _get_events(self, handle: Handle) -> dict[str, Any]:
        """Get events for a resource."""
        field_selector = ""
        if handle.name:
            field_selector = f"--field-selector=involvedObject.name={handle.name}"

        cmd = ["kubectl", "get", "events", "-n", handle.namespace, "-o", "json"]
        if field_selector:
            cmd.append(field_selector)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {"events": [], "error": result.stderr}

        return dict(json.loads(result.stdout))

    async def _invoke_terminate(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Delete resource (kubectl delete)."""
        if not handle.name:
            raise ValueError("Cannot terminate without resource name")

        resource = handle.resource

        if resource["api_group"]:
            resource_type = f"{resource['plural']}.{resource['api_group']}"
        else:
            resource_type = resource["plural"]

        cmd = [
            "kubectl",
            "delete",
            resource_type,
            handle.name,
            "-n",
            handle.namespace,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "message": result.stdout or result.stderr,
        }

    async def _invoke_sense(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Sense pheromones (with calculated intensity).

        PASSIVE STIGMERGY: Intensity is calculated on read.
        """
        manifest = await self._invoke_manifest(handle, **kwargs)

        # Calculate current intensity for pheromones
        if handle.resource["kind"] == "Pheromone":
            items = manifest.get("items", [manifest] if "spec" in manifest else [])
            for item in items:
                spec = item.get("spec", {})
                metadata = item.get("metadata", {})
                item["calculated_intensity"] = self._calculate_pheromone_intensity(
                    spec, metadata
                )

        return manifest

    def _calculate_pheromone_intensity(
        self, spec: dict[str, Any], metadata: dict[str, Any]
    ) -> float:
        """Calculate pheromone intensity from decay function.

        PASSIVE STIGMERGY: No status.current_intensity stored.
        Formula: intensity(t) = initialIntensity * (0.5 ^ (elapsed / halfLife))
        """
        emitted_str = spec.get("emittedAt") or metadata.get("creationTimestamp")
        if not emitted_str:
            return float(spec.get("initialIntensity", spec.get("intensity", 1.0)))

        try:
            emitted_at = datetime.fromisoformat(emitted_str.replace("Z", "+00:00"))
            initial = spec.get("initialIntensity", spec.get("intensity", 1.0))
            half_life = spec.get("halfLifeMinutes", 10)

            # DREAM pheromones decay slower
            if spec.get("type") == "DREAM":
                half_life *= 2.0

            elapsed = (
                datetime.now(timezone.utc) - emitted_at.replace(tzinfo=timezone.utc)
            ).total_seconds() / 60
            return float(initial * (0.5 ** (elapsed / half_life)))
        except Exception:
            return float(spec.get("initialIntensity", spec.get("intensity", 1.0)))

    async def _invoke_emit(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Emit a pheromone (kubectl apply).

        PASSIVE STIGMERGY: Sets emittedAt timestamp for decay calculation.
        """
        pheromone_spec = kwargs.get("spec", {})
        name = kwargs.get("name", f"pheromone-{hash(str(pheromone_spec)) % 10000:04d}")

        manifest = {
            "apiVersion": "kgents.io/v1",
            "kind": "Pheromone",
            "metadata": {
                "name": name,
                "namespace": handle.namespace,
            },
            "spec": {
                "emittedAt": datetime.now(timezone.utc).isoformat() + "Z",
                "initialIntensity": pheromone_spec.get("intensity", 1.0),
                "halfLifeMinutes": pheromone_spec.get("halfLifeMinutes", 10),
                "type": pheromone_spec.get("type", "SIGNAL"),
                "source": pheromone_spec.get("source"),
                "target": pheromone_spec.get("target"),
                "payload": pheromone_spec.get("payload"),
            },
        }

        import tempfile

        import yaml

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(manifest, f)
            f.flush()

            cmd = ["kubectl", "apply", "-f", f.name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        return {
            "success": result.returncode == 0,
            "name": name,
            "message": result.stdout or result.stderr,
        }

    async def _invoke_scale(self, handle: Handle, **kwargs: Any) -> dict[str, Any]:
        """Scale a deployment or agent."""
        if not handle.name:
            raise ValueError("Cannot scale without resource name")

        replicas = kwargs.get("replicas", 1)
        resource = handle.resource

        if resource["api_group"]:
            resource_type = f"{resource['plural']}.{resource['api_group']}"
        else:
            resource_type = resource["plural"]

        cmd = [
            "kubectl",
            "scale",
            resource_type,
            handle.name,
            "-n",
            handle.namespace,
            f"--replicas={replicas}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "replicas": replicas,
            "message": result.stdout or result.stderr,
        }


# =============================================================================
# Factory Function
# =============================================================================


def create_logos_resolver(namespace: str = "kgents-agents") -> LogosResolver:
    """Create a LogosResolver instance."""
    return LogosResolver(namespace=namespace)
