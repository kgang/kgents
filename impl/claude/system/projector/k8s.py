"""
K8sProjector: Compiles agent Halo to Kubernetes manifests.

The K8sProjector reads an agent's declarative capabilities (Halo)
and produces Kubernetes resource manifests for deployment.

Capability Mapping:
| Capability  | K8s Resources                                     |
|-------------|---------------------------------------------------|
| @Stateful   | StatefulSet + PersistentVolumeClaim               |
| @Soulful    | K-gent sidecar container in pod spec              |
| @Observable | ServiceMonitor (Prometheus) + Service             |
| @Streamable | HorizontalPodAutoscaler                           |

The Alethic Isomorphism:
    Same Halo + LocalProjector  → Runnable Python
    Same Halo + K8sProjector    → K8s Manifests
    Both produce semantically equivalent agents.

Example:
    >>> @Capability.Stateful(schema=MyState)
    ... @Capability.Streamable(budget=5.0)
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> manifests = K8sProjector().compile(MyAgent)
    >>> # manifests is [StatefulSet, PVC, Service, HPA, ...]
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .base import (
    CompilationError,
    InvalidNameError,
    Projector,
    UnsupportedCapabilityError,
)

# RFC 1123 subdomain name pattern (K8s resource names)
# - lowercase alphanumeric or hyphens
# - start with alphanumeric
# - max 63 chars
_RFC1123_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
_MAX_K8S_NAME_LENGTH = 63

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from agents.poly.types import Agent


@dataclass
class K8sResource:
    """
    Represents a Kubernetes resource manifest.

    Provides a typed wrapper around the raw manifest dict
    with convenience methods for serialization.
    """

    api_version: str
    kind: str
    metadata: dict[str, Any]
    spec: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)  # For ConfigMap/Secret

    def to_dict(self) -> dict[str, Any]:
        """Convert to K8s manifest dict."""
        result: dict[str, Any] = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata,
        }
        if self.spec:
            result["spec"] = self.spec
        if self.data:
            result["data"] = self.data
        return result

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        try:
            import yaml

            result: str = yaml.dump(self.to_dict(), default_flow_style=False)
            return result
        except ImportError:
            # Fallback to basic formatting
            import json

            return json.dumps(self.to_dict(), indent=2)


@dataclass
class K8sProjector(Projector[list[K8sResource]]):
    """
    Compiles agent Halo into Kubernetes manifests.

    The K8sProjector reads capability decorators and produces
    K8s resources that realize the same semantics in a cluster.

    Capability → Resource Mapping:
    - @Stateful → StatefulSet + PVC (persistent storage)
    - @Soulful  → K-gent sidecar container (persona governance)
    - @Observable → ServiceMonitor + Service (Prometheus metrics)
    - @Streamable → HorizontalPodAutoscaler (scale on load)

    Configuration:
        namespace: Target namespace for resources (default: kgents-agents)
        image_prefix: Docker image prefix (default: kgents/)
        storage_class: StorageClass for PVCs (default: standard)

    Example:
        >>> @Capability.Stateful(schema=MyState)
        ... @Capability.Soulful(persona="kent")
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> manifests = K8sProjector(namespace="production").compile(MyAgent)
        >>> for m in manifests:
        ...     print(m.to_yaml())
    """

    namespace: str = "kgents-agents"
    image_prefix: str = "kgents/"
    storage_class: str = "standard"
    default_cpu_request: str = "100m"
    default_cpu_limit: str = "500m"
    default_memory_request: str = "256Mi"
    default_memory_limit: str = "512Mi"
    default_replicas: int = 1

    @property
    def name(self) -> str:
        return "K8sProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> list[K8sResource]:
        """
        Compile agent class to K8s manifests.

        Reads the agent's Halo and produces appropriate K8s resources.

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            List of K8sResource manifests

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
            CompilationError: If compilation fails
        """
        from agents.a.halo import get_halo

        # Helper functions for capability lookup by name
        halo = get_halo(agent_cls)

        def _has_cap(cap_name: str) -> bool:
            return any(type(c).__name__ == cap_name for c in halo)

        def _get_cap(cap_name: str) -> Any:
            for c in halo:
                if type(c).__name__ == cap_name:
                    return c
            return None

        # Validate capabilities
        supported_type_names = {
            "StatefulCapability",
            "SoulfulCapability",
            "ObservableCapability",
            "StreamableCapability",
        }

        for cap in halo:
            if type(cap).__name__ not in supported_type_names:
                raise UnsupportedCapabilityError(type(cap), self.name)

        # Derive agent name from class
        agent_name = self._derive_agent_name(agent_cls)

        # Build resources based on capabilities
        resources: list[K8sResource] = []

        # Base labels for all resources
        base_labels = self._base_labels(agent_name)

        # Determine if we need StatefulSet or Deployment
        is_stateful = _has_cap("StatefulCapability")
        stateful_cap = _get_cap("StatefulCapability") if is_stateful else None

        # Check other capabilities
        soulful_cap = _get_cap("SoulfulCapability")
        observable_cap = _get_cap("ObservableCapability")
        streamable_cap = _get_cap("StreamableCapability")

        # 1. Create workload (StatefulSet or Deployment)
        if is_stateful:
            resources.append(
                self._create_statefulset(agent_name, base_labels, stateful_cap, soulful_cap)
            )
            resources.append(self._create_pvc(agent_name, base_labels, stateful_cap))
        else:
            resources.append(self._create_deployment(agent_name, base_labels, soulful_cap))

        # 2. Create Service (always needed)
        resources.append(self._create_service(agent_name, base_labels, observable_cap))

        # 3. Create ServiceMonitor if @Observable
        if observable_cap is not None and observable_cap.metrics:
            resources.append(self._create_service_monitor(agent_name, base_labels))

        # 4. Create HPA if @Streamable
        if streamable_cap is not None:
            resources.append(self._create_hpa(agent_name, base_labels, streamable_cap, is_stateful))

        # 5. Create ConfigMap for agent config
        resources.append(self._create_configmap(agent_name, base_labels, halo))

        return resources

    def _derive_agent_name(self, agent_cls: type) -> str:
        """
        Derive RFC 1123 compliant K8s name from agent class.

        Converts CamelCase to kebab-case, sanitizes special characters,
        and validates length/format constraints.

        Raises:
            InvalidNameError: If name cannot be made RFC 1123 compliant
        """
        # Convert CamelCase to kebab-case
        name = agent_cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        raw_name = "".join(result)

        # Sanitize: replace invalid chars with hyphens, collapse multiple hyphens
        sanitized = re.sub(r"[^a-z0-9-]", "-", raw_name)
        sanitized = re.sub(r"-+", "-", sanitized)

        # Strip leading/trailing hyphens
        sanitized = sanitized.strip("-")

        # Handle empty result
        if not sanitized:
            raise InvalidNameError(name, "Agent name produces empty K8s name after sanitization")

        # Truncate if too long, but ensure we don't end with a hyphen
        if len(sanitized) > _MAX_K8S_NAME_LENGTH:
            sanitized = sanitized[:_MAX_K8S_NAME_LENGTH].rstrip("-")

        # Final validation
        if not _RFC1123_PATTERN.match(sanitized):
            raise InvalidNameError(
                name,
                f"Name '{sanitized}' is not RFC 1123 compliant "
                "(must be lowercase alphanumeric with hyphens, 1-63 chars, "
                "start and end with alphanumeric)",
            )

        return sanitized

    def _base_labels(self, agent_name: str) -> dict[str, str]:
        """
        Standard K8s labels for all resources.

        Label values are truncated to 63 chars per K8s limits.
        """
        # Label values must be <= 63 chars
        truncated_name = agent_name[:63]
        return {
            "app.kubernetes.io/name": truncated_name,
            "app.kubernetes.io/component": "agent",
            "app.kubernetes.io/part-of": "kgents",
            "app.kubernetes.io/managed-by": "k8s-projector",
            "kgents.io/agent": truncated_name,
        }

    def _create_deployment(
        self,
        agent_name: str,
        labels: dict[str, str],
        soulful_cap: Any | None,
    ) -> K8sResource:
        """Create Deployment for stateless agents."""
        containers = [self._main_container(agent_name)]

        # Add K-gent sidecar if @Soulful
        if soulful_cap is not None:
            containers.append(self._kgent_sidecar(soulful_cap))

        return K8sResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={
                "name": agent_name,
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "replicas": self.default_replicas,
                "selector": {"matchLabels": {"app.kubernetes.io/name": agent_name}},
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "containers": containers,
                    },
                },
            },
        )

    def _create_statefulset(
        self,
        agent_name: str,
        labels: dict[str, str],
        stateful_cap: Any,
        soulful_cap: Any | None,
    ) -> K8sResource:
        """Create StatefulSet for stateful agents."""
        containers = [self._main_container(agent_name, with_volume=True)]

        # Add K-gent sidecar if @Soulful
        if soulful_cap is not None:
            containers.append(self._kgent_sidecar(soulful_cap))

        return K8sResource(
            api_version="apps/v1",
            kind="StatefulSet",
            metadata={
                "name": agent_name,
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "replicas": self.default_replicas,
                "serviceName": agent_name,
                "selector": {"matchLabels": {"app.kubernetes.io/name": agent_name}},
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "containers": containers,
                        "volumes": [
                            {
                                "name": "agent-state",
                                "persistentVolumeClaim": {
                                    "claimName": f"{agent_name}-state",
                                },
                            }
                        ],
                    },
                },
            },
        )

    def _create_pvc(
        self,
        agent_name: str,
        labels: dict[str, str],
        stateful_cap: Any,
    ) -> K8sResource:
        """Create PersistentVolumeClaim for stateful agents."""
        # Derive storage size from backend hint or default
        storage_size = "1Gi"
        if hasattr(stateful_cap, "backend") and stateful_cap.backend == "persistent":
            storage_size = "10Gi"

        return K8sResource(
            api_version="v1",
            kind="PersistentVolumeClaim",
            metadata={
                "name": f"{agent_name}-state",
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "accessModes": ["ReadWriteOnce"],
                "storageClassName": self.storage_class,
                "resources": {
                    "requests": {"storage": storage_size},
                },
            },
        )

    def _create_service(
        self,
        agent_name: str,
        labels: dict[str, str],
        observable_cap: Any | None,
    ) -> K8sResource:
        """Create Service for the agent."""
        ports = [
            {
                "name": "http",
                "port": 8080,
                "targetPort": 8080,
                "protocol": "TCP",
            }
        ]

        # Add metrics port if @Observable
        if observable_cap is not None and observable_cap.metrics:
            ports.append(
                {
                    "name": "metrics",
                    "port": 9090,
                    "targetPort": 9090,
                    "protocol": "TCP",
                }
            )

        return K8sResource(
            api_version="v1",
            kind="Service",
            metadata={
                "name": agent_name,
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "type": "ClusterIP",
                "ports": ports,
                "selector": {"app.kubernetes.io/name": agent_name},
            },
        )

    def _create_service_monitor(
        self,
        agent_name: str,
        labels: dict[str, str],
    ) -> K8sResource:
        """Create Prometheus ServiceMonitor for observable agents."""
        return K8sResource(
            api_version="monitoring.coreos.com/v1",
            kind="ServiceMonitor",
            metadata={
                "name": agent_name,
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "selector": {
                    "matchLabels": {"app.kubernetes.io/name": agent_name},
                },
                "endpoints": [
                    {
                        "port": "metrics",
                        "interval": "15s",
                        "path": "/metrics",
                    }
                ],
                "namespaceSelector": {
                    "matchNames": [self.namespace],
                },
            },
        )

    def _create_hpa(
        self,
        agent_name: str,
        labels: dict[str, str],
        streamable_cap: Any,
        is_stateful: bool,
    ) -> K8sResource:
        """Create HorizontalPodAutoscaler for streamable agents."""
        # Map entropy budget to scaling behavior
        # Higher budget → more aggressive scaling
        budget = streamable_cap.budget if hasattr(streamable_cap, "budget") else 5.0
        max_replicas = min(int(budget * 2), 10)

        return K8sResource(
            api_version="autoscaling/v2",
            kind="HorizontalPodAutoscaler",
            metadata={
                "name": agent_name,
                "namespace": self.namespace,
                "labels": labels,
            },
            spec={
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "StatefulSet" if is_stateful else "Deployment",
                    "name": agent_name,
                },
                "minReplicas": 1,
                "maxReplicas": max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70,
                            },
                        },
                    }
                ],
            },
        )

    def _create_configmap(
        self,
        agent_name: str,
        labels: dict[str, str],
        halo: Any,
    ) -> K8sResource:
        """Create ConfigMap with agent configuration."""
        # Serialize capabilities to config
        capabilities = [type(c).__name__ for c in halo]

        return K8sResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={
                "name": f"{agent_name}-config",
                "namespace": self.namespace,
                "labels": labels,
            },
            data={
                "AGENT_NAME": agent_name,
                "AGENT_CAPABILITIES": ",".join(capabilities),
                "AGENT_NAMESPACE": self.namespace,
            },
        )

    def _main_container(
        self,
        agent_name: str,
        with_volume: bool = False,
    ) -> dict[str, Any]:
        """Build main container spec."""
        container: dict[str, Any] = {
            "name": "agent",
            "image": f"{self.image_prefix}{agent_name}:latest",
            "ports": [
                {"name": "http", "containerPort": 8080},
                {"name": "metrics", "containerPort": 9090},
            ],
            "envFrom": [
                {"configMapRef": {"name": f"{agent_name}-config"}},
            ],
            "resources": {
                "requests": {
                    "cpu": self.default_cpu_request,
                    "memory": self.default_memory_request,
                },
                "limits": {
                    "cpu": self.default_cpu_limit,
                    "memory": self.default_memory_limit,
                },
            },
            "livenessProbe": {
                "httpGet": {"path": "/health", "port": 8080},
                "initialDelaySeconds": 10,
                "periodSeconds": 10,
            },
            "readinessProbe": {
                "httpGet": {"path": "/ready", "port": 8080},
                "initialDelaySeconds": 5,
                "periodSeconds": 5,
            },
        }

        if with_volume:
            container["volumeMounts"] = [
                {
                    "name": "agent-state",
                    "mountPath": "/var/lib/kgents/state",
                }
            ]

        return container

    def _kgent_sidecar(self, soulful_cap: Any) -> dict[str, Any]:
        """Build K-gent sidecar container for persona governance."""
        persona = soulful_cap.persona if hasattr(soulful_cap, "persona") else "default"
        mode = soulful_cap.mode if hasattr(soulful_cap, "mode") else "advisory"

        return {
            "name": "kgent-sidecar",
            "image": f"{self.image_prefix}kgent:latest",
            "env": [
                {"name": "KGENT_PERSONA", "value": persona},
                {"name": "KGENT_MODE", "value": mode},
                {"name": "KGENT_AGENT_PORT", "value": "8080"},
            ],
            "ports": [
                {"name": "kgent", "containerPort": 8081},
            ],
            "resources": {
                "requests": {"cpu": "50m", "memory": "128Mi"},
                "limits": {"cpu": "200m", "memory": "256Mi"},
            },
        }

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if K8sProjector supports a capability type.

        K8sProjector supports all four standard capabilities.

        Args:
            capability: The capability type to check

        Returns:
            True if capability is supported
        """
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
        )

        return capability in {
            StatefulCapability,
            SoulfulCapability,
            ObservableCapability,
            StreamableCapability,
        }


def manifests_to_yaml(resources: list[K8sResource], separator: str = "---\n") -> str:
    """
    Convert list of K8sResource to multi-document YAML.

    Args:
        resources: List of K8s resources
        separator: Document separator (default: ---)

    Returns:
        YAML string with all manifests
    """
    return separator.join(r.to_yaml() for r in resources)
