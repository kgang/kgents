"""AgentServer Operator - Reconcile AgentServer CRs to Terrarium Deployments.

The AgentServer operator manages the lifecycle of Terrarium gateways:
1. On CREATE: Generate Deployment + Service + ConfigMap
2. On UPDATE: Reconcile changes (rolling update)
3. On DELETE: Cleanup resources
4. On TIMER: Update agent registry, health checks

This makes Terrarium a first-class K8s citizen:
    kubectl get agentservers --watch

Exit Criteria (Phase 4):
    kubectl apply -f agentserver.yaml → deploys working terrarium

Principle alignment:
- Tasteful: Single CR deploys complete observability stack
- Ethical: Observation respects agent metabolism
- Joy-inducing: Real-time visibility into agent ecosystem
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

# kopf is the K8s operator framework
# In production: pip install kopf kubernetes
# For testing without K8s: we provide mock implementations
try:
    import kopf
    from kubernetes import client
    from kubernetes.client.rest import ApiException

    KOPF_AVAILABLE = True
except ImportError:
    KOPF_AVAILABLE = False
    kopf = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Reconciliation configuration
AGENT_REGISTRY_INTERVAL = 30.0  # seconds
HEALTH_CHECK_INTERVAL = 15.0


class AgentServerPhase(str, Enum):
    """AgentServer lifecycle phases."""

    PENDING = "Pending"
    DEPLOYING = "Deploying"
    RUNNING = "Running"
    DEGRADED = "Degraded"
    FAILED = "Failed"


@dataclass
class AgentServerSpec:
    """Parsed AgentServer specification."""

    name: str
    namespace: str

    # Gateway config
    gateway_image: str = "kgents/terrarium:latest"
    gateway_replicas: int = 1
    gateway_port: int = 8080
    gateway_cpu_limit: str = "500m"
    gateway_memory_limit: str = "512Mi"

    # Mirror config
    mirror_max_history: int = 100
    mirror_broadcast_timeout: str = "100ms"
    mirror_buffer_size: int = 100

    # Agent registry
    auto_discover: bool = True
    genus_filter: list[str] = field(default_factory=list)

    # Widgets
    widgets_enabled: bool = True
    density_field_enabled: bool = True

    # Pheromones
    pheromones_enabled: bool = True
    pheromones_forward_to_mirror: bool = True

    # Semaphores (Phase 5)
    semaphores_enabled: bool = True
    purgatory_endpoint: bool = True

    # Auth
    observe_requires_auth: bool = False
    perturb_requires_auth: bool = True
    rbac_integration: bool = True

    # Service
    service_type: str = "ClusterIP"
    service_annotations: dict[str, str] = field(default_factory=dict)

    # Metrics
    metrics_enabled: bool = True
    metrics_port: int = 9090

    def to_deployment(self) -> dict[str, Any]:
        """Generate Deployment manifest."""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.name}-terrarium",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": f"{self.name}-terrarium",
                    "app.kubernetes.io/component": "gateway",
                    "app.kubernetes.io/part-of": "kgents",
                    "app.kubernetes.io/managed-by": "agentserver-operator",
                    "kgents.io/agentserver": self.name,
                },
            },
            "spec": {
                "replicas": self.gateway_replicas,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": f"{self.name}-terrarium",
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": f"{self.name}-terrarium",
                            "app.kubernetes.io/component": "gateway",
                            "kgents.io/agentserver": self.name,
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "terrarium",
                                "image": self.gateway_image,
                                "ports": [
                                    {
                                        "name": "http",
                                        "containerPort": self.gateway_port,
                                        "protocol": "TCP",
                                    },
                                    {
                                        "name": "metrics",
                                        "containerPort": self.metrics_port,
                                        "protocol": "TCP",
                                    },
                                ],
                                "env": self._build_env_vars(),
                                "envFrom": [
                                    {
                                        "configMapRef": {
                                            "name": f"{self.name}-terrarium-config",
                                        }
                                    }
                                ],
                                "resources": {
                                    "limits": {
                                        "cpu": self.gateway_cpu_limit,
                                        "memory": self.gateway_memory_limit,
                                    },
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "256Mi",
                                    },
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": self.gateway_port,
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": self.gateway_port,
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ],
                        "serviceAccountName": f"{self.name}-terrarium",
                    },
                },
            },
        }

    def _build_env_vars(self) -> list[dict[str, Any]]:
        """Build environment variables for the container."""
        return [
            {"name": "TERRARIUM_PORT", "value": str(self.gateway_port)},
            {"name": "TERRARIUM_METRICS_PORT", "value": str(self.metrics_port)},
            {
                "name": "TERRARIUM_AUTO_DISCOVER",
                "value": str(self.auto_discover).lower(),
            },
            {
                "name": "TERRARIUM_SEMAPHORES_ENABLED",
                "value": str(self.semaphores_enabled).lower(),
            },
            {
                "name": "TERRARIUM_PURGATORY_ENDPOINT",
                "value": str(self.purgatory_endpoint).lower(),
            },
            {
                "name": "TERRARIUM_OBSERVE_AUTH",
                "value": str(self.observe_requires_auth).lower(),
            },
            {
                "name": "TERRARIUM_PERTURB_AUTH",
                "value": str(self.perturb_requires_auth).lower(),
            },
        ]

    def to_service(self) -> dict[str, Any]:
        """Generate Service manifest."""
        spec: dict[str, Any] = {
            "type": self.service_type,
            "ports": [
                {
                    "name": "http",
                    "port": 80,
                    "targetPort": self.gateway_port,
                    "protocol": "TCP",
                },
            ],
            "selector": {
                "app.kubernetes.io/name": f"{self.name}-terrarium",
            },
        }

        if self.metrics_enabled:
            spec["ports"].append(
                {
                    "name": "metrics",
                    "port": self.metrics_port,
                    "targetPort": self.metrics_port,
                    "protocol": "TCP",
                }
            )

        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.name}-terrarium",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": f"{self.name}-terrarium",
                    "app.kubernetes.io/component": "gateway",
                    "app.kubernetes.io/part-of": "kgents",
                    "kgents.io/agentserver": self.name,
                },
                "annotations": self.service_annotations,
            },
            "spec": spec,
        }

    def to_configmap(self) -> dict[str, Any]:
        """Generate ConfigMap manifest."""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.name}-terrarium-config",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": f"{self.name}-terrarium",
                    "app.kubernetes.io/part-of": "kgents",
                    "kgents.io/agentserver": self.name,
                },
            },
            "data": {
                "MIRROR_MAX_HISTORY": str(self.mirror_max_history),
                "MIRROR_BROADCAST_TIMEOUT": self.mirror_broadcast_timeout,
                "MIRROR_BUFFER_SIZE": str(self.mirror_buffer_size),
                "WIDGETS_ENABLED": str(self.widgets_enabled).lower(),
                "DENSITY_FIELD_ENABLED": str(self.density_field_enabled).lower(),
                "PHEROMONES_ENABLED": str(self.pheromones_enabled).lower(),
                "PHEROMONES_FORWARD": str(self.pheromones_forward_to_mirror).lower(),
                "GENUS_FILTER": ",".join(self.genus_filter)
                if self.genus_filter
                else "",
                "RBAC_INTEGRATION": str(self.rbac_integration).lower(),
            },
        }

    def to_service_account(self) -> dict[str, Any]:
        """Generate ServiceAccount manifest."""
        return {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.name}-terrarium",
                "namespace": self.namespace,
                "labels": {
                    "app.kubernetes.io/name": f"{self.name}-terrarium",
                    "app.kubernetes.io/part-of": "kgents",
                    "kgents.io/agentserver": self.name,
                },
            },
        }

    def to_cluster_role_binding(self) -> dict[str, Any]:
        """Generate ClusterRoleBinding for agent discovery."""
        return {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": f"{self.namespace}-{self.name}-terrarium",
                "labels": {
                    "app.kubernetes.io/part-of": "kgents",
                    "kgents.io/agentserver": self.name,
                },
            },
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "kgents-agent-reader",
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": f"{self.name}-terrarium",
                    "namespace": self.namespace,
                }
            ],
        }


def parse_agentserver_spec(
    spec: dict[str, Any],
    meta: dict[str, Any],
) -> AgentServerSpec:
    """Parse CRD spec into AgentServerSpec dataclass."""
    gateway = spec.get("gateway", {})
    mirror = spec.get("mirror", {})
    agents = spec.get("agents", {})
    widgets = spec.get("widgets", {})
    pheromones = spec.get("pheromones", {})
    semaphores = spec.get("semaphores", {})
    auth = spec.get("auth", {})
    service = spec.get("service", {})
    metrics = spec.get("metrics", {})

    gateway_resources = gateway.get("resources", {})
    gateway_limits = gateway_resources.get("limits", {})

    widgets_density = widgets.get("densityField", {})

    return AgentServerSpec(
        name=meta.get("name", ""),
        namespace=meta.get("namespace", "kgents-system"),
        # Gateway
        gateway_image=gateway.get("image", "kgents/terrarium:latest"),
        gateway_replicas=gateway.get("replicas", 1),
        gateway_port=gateway.get("port", 8080),
        gateway_cpu_limit=gateway_limits.get("cpu", "500m"),
        gateway_memory_limit=gateway_limits.get("memory", "512Mi"),
        # Mirror
        mirror_max_history=mirror.get("maxHistory", 100),
        mirror_broadcast_timeout=mirror.get("broadcastTimeout", "100ms"),
        mirror_buffer_size=mirror.get("bufferSize", 100),
        # Agents
        auto_discover=agents.get("autoDiscover", True),
        genus_filter=agents.get("genusFilter", []),
        # Widgets
        widgets_enabled=widgets.get("enabled", True),
        density_field_enabled=widgets_density.get("enabled", True),
        # Pheromones
        pheromones_enabled=pheromones.get("enabled", True),
        pheromones_forward_to_mirror=pheromones.get("forwardToMirror", True),
        # Semaphores
        semaphores_enabled=semaphores.get("enabled", True),
        purgatory_endpoint=semaphores.get("purgatoryEndpoint", True),
        # Auth
        observe_requires_auth=auth.get("observeRequiresAuth", False),
        perturb_requires_auth=auth.get("perturbRequiresAuth", True),
        rbac_integration=auth.get("rbacIntegration", True),
        # Service
        service_type=service.get("type", "ClusterIP"),
        service_annotations=service.get("annotations", {}),
        # Metrics
        metrics_enabled=metrics.get("enabled", True),
        metrics_port=metrics.get("port", 9090),
    )


# ============================================================================
# Kopf Handlers (only registered if kopf is available)
# ============================================================================

if KOPF_AVAILABLE:

    @kopf.on.create("kgents.io", "v1", "agentservers")  # type: ignore[arg-type]
    async def on_agentserver_create(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Create Deployment, Service, and ConfigMap for new AgentServer."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-system")
        uid = meta.get("uid", "")

        logger.info(f"Creating AgentServer: {name}")

        # Parse spec
        server_spec = parse_agentserver_spec(spec, meta)

        created_resources: list[str] = []
        apps_api = client.AppsV1Api()
        core_api = client.CoreV1Api()
        rbac_api = client.RbacAuthorizationV1Api()

        owner_ref = {
            "apiVersion": "kgents.io/v1",
            "kind": "AgentServer",
            "name": name,
            "uid": uid,
            "controller": True,
            "blockOwnerDeletion": True,
        }

        try:
            # 1. Create ServiceAccount
            sa = server_spec.to_service_account()
            sa["metadata"]["ownerReferences"] = [owner_ref]
            try:
                core_api.create_namespaced_service_account(
                    namespace=namespace,
                    body=sa,
                )
                created_resources.append(f"serviceaccount/{sa['metadata']['name']}")
                logger.info(f"Created ServiceAccount: {sa['metadata']['name']}")
            except ApiException as e:
                if e.status != 409:
                    raise

            # 2. Create ConfigMap
            configmap = server_spec.to_configmap()
            configmap["metadata"]["ownerReferences"] = [owner_ref]
            try:
                core_api.create_namespaced_config_map(
                    namespace=namespace,
                    body=configmap,
                )
                created_resources.append(f"configmap/{configmap['metadata']['name']}")
                logger.info(f"Created ConfigMap: {configmap['metadata']['name']}")
            except ApiException as e:
                if e.status != 409:
                    raise

            # 3. Create Deployment
            deployment = server_spec.to_deployment()
            deployment["metadata"]["ownerReferences"] = [owner_ref]
            try:
                apps_api.create_namespaced_deployment(
                    namespace=namespace,
                    body=deployment,
                )
                created_resources.append(f"deployment/{deployment['metadata']['name']}")
                logger.info(f"Created Deployment: {deployment['metadata']['name']}")
            except ApiException as e:
                if e.status != 409:
                    raise

            # 4. Create Service
            service = server_spec.to_service()
            service["metadata"]["ownerReferences"] = [owner_ref]
            try:
                core_api.create_namespaced_service(
                    namespace=namespace,
                    body=service,
                )
                created_resources.append(f"service/{service['metadata']['name']}")
                logger.info(f"Created Service: {service['metadata']['name']}")
            except ApiException as e:
                if e.status != 409:
                    raise

            # 5. Create ClusterRoleBinding (if auto-discover)
            if server_spec.auto_discover:
                crb = server_spec.to_cluster_role_binding()
                # ClusterRoleBinding is cluster-scoped, can't use ownerRef
                try:
                    rbac_api.create_cluster_role_binding(body=crb)
                    created_resources.append(
                        f"clusterrolebinding/{crb['metadata']['name']}"
                    )
                    logger.info(
                        f"Created ClusterRoleBinding: {crb['metadata']['name']}"
                    )
                except ApiException as e:
                    if e.status != 409:
                        raise

            # Update status
            now = datetime.now(timezone.utc).isoformat()
            patch.status["phase"] = AgentServerPhase.DEPLOYING.value
            patch.status["observedGeneration"] = meta.get("generation", 1)
            patch.status["deployment"] = f"{name}-terrarium"
            patch.status["service"] = f"{name}-terrarium"
            patch.status["endpoint"] = (
                f"http://{name}-terrarium.{namespace}.svc.cluster.local"
            )
            patch.status["registeredAgents"] = 0
            patch.status["activeObservers"] = 0
            patch.status["pendingSemaphores"] = 0
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "DeploymentCreated",
                    "message": "Waiting for pods to be ready",
                    "lastTransitionTime": now,
                }
            ]

            logger.info(f"AgentServer {name} created: {created_resources}")
            return {"created": True, "resources": created_resources}

        except Exception as e:
            logger.error(f"Failed to create AgentServer {name}: {e}")
            patch.status["phase"] = AgentServerPhase.FAILED.value
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "CreationFailed",
                    "message": str(e),
                    "lastTransitionTime": datetime.now(timezone.utc).isoformat(),
                }
            ]
            raise kopf.PermanentError(f"Failed to create AgentServer: {e}")

    @kopf.on.update("kgents.io", "v1", "agentservers")  # type: ignore[arg-type]
    async def on_agentserver_update(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        diff: kopf.Diff,
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Update Deployment when AgentServer spec changes."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-system")

        logger.info(f"Updating AgentServer: {name}")

        server_spec = parse_agentserver_spec(spec, meta)
        apps_api = client.AppsV1Api()
        core_api = client.CoreV1Api()

        try:
            # Update ConfigMap
            configmap = server_spec.to_configmap()
            core_api.patch_namespaced_config_map(
                name=f"{name}-terrarium-config",
                namespace=namespace,
                body=configmap,
            )

            # Update Deployment
            deployment = server_spec.to_deployment()
            apps_api.patch_namespaced_deployment(
                name=f"{name}-terrarium",
                namespace=namespace,
                body=deployment,
            )

            patch.status["observedGeneration"] = meta.get("generation", 1)
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "DeploymentUpdating",
                    "message": "Rolling update in progress",
                    "lastTransitionTime": datetime.now(timezone.utc).isoformat(),
                }
            ]

            logger.info(f"AgentServer {name} updated")
            return {"updated": True}

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Resources not found for AgentServer {name}")
                return {"updated": False, "recreate_needed": True}
            raise

    @kopf.on.delete("kgents.io", "v1", "agentservers")  # type: ignore[arg-type]
    async def on_agentserver_delete(
        spec: dict[str, Any],
        meta: dict[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        """Clean up resources when AgentServer is deleted."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-system")

        logger.info(f"Deleting AgentServer: {name}")

        # ClusterRoleBinding needs manual cleanup
        rbac_api = client.RbacAuthorizationV1Api()
        try:
            rbac_api.delete_cluster_role_binding(name=f"{namespace}-{name}-terrarium")
            logger.info(f"Deleted ClusterRoleBinding: {namespace}-{name}-terrarium")
        except ApiException:
            pass  # May not exist

        return {"deleted": True}

    @kopf.timer("kgents.io", "v1", "agentservers", interval=HEALTH_CHECK_INTERVAL)  # type: ignore[arg-type]
    async def agentserver_health_check(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any] | None:
        """Periodically check AgentServer health."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-system")
        current_phase = status.get("phase", "Pending")

        if current_phase == AgentServerPhase.FAILED.value:
            return None

        apps_api = client.AppsV1Api()

        try:
            deployment = apps_api.read_namespaced_deployment(
                name=f"{name}-terrarium",
                namespace=namespace,
            )

            ready_replicas = deployment.status.ready_replicas or 0
            desired_replicas = deployment.spec.replicas or 1

            now = datetime.now(timezone.utc).isoformat()

            if ready_replicas >= desired_replicas:
                patch.status["phase"] = AgentServerPhase.RUNNING.value
                patch.status["readyReplicas"] = ready_replicas
                patch.status["lastHeartbeat"] = now
                patch.status["conditions"] = [
                    {
                        "type": "Ready",
                        "status": "True",
                        "reason": "AllReplicasReady",
                        "message": f"{ready_replicas}/{desired_replicas} replicas ready",
                        "lastTransitionTime": now,
                    }
                ]
                return {"health": "RUNNING", "ready": ready_replicas}
            elif ready_replicas > 0:
                patch.status["phase"] = AgentServerPhase.DEGRADED.value
                patch.status["readyReplicas"] = ready_replicas
                return {"health": "DEGRADED", "ready": ready_replicas}
            else:
                patch.status["readyReplicas"] = 0
                return {"health": "NOT_READY", "ready": 0}

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Deployment not found for AgentServer {name}")
                return {"health": "UNKNOWN", "error": "deployment_not_found"}
            raise


# ============================================================================
# Standalone Functions (for testing without K8s)
# ============================================================================


@dataclass
class MockAgentServer:
    """In-memory AgentServer for testing without K8s."""

    name: str
    namespace: str = "kgents-system"
    replicas: int = 1
    phase: AgentServerPhase = AgentServerPhase.PENDING
    ready_replicas: int = 0
    registered_agents: int = 0
    active_observers: int = 0
    pending_semaphores: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def reconcile(self) -> dict[str, Any]:
        """Simulate reconciliation."""
        self.phase = AgentServerPhase.RUNNING
        self.ready_replicas = self.replicas
        return {
            "success": True,
            "resources": [
                f"deployment/{self.name}-terrarium",
                f"service/{self.name}-terrarium",
                f"configmap/{self.name}-terrarium-config",
            ],
        }

    def scale(self, replicas: int) -> None:
        """Simulate scaling."""
        self.replicas = replicas
        self.ready_replicas = replicas

    def register_agent(self) -> None:
        """Simulate agent registration."""
        self.registered_agents += 1

    def add_observer(self) -> None:
        """Simulate observer connection."""
        self.active_observers += 1

    def add_semaphore(self) -> None:
        """Simulate semaphore ejection."""
        self.pending_semaphores += 1

    def resolve_semaphore(self) -> None:
        """Simulate semaphore resolution."""
        if self.pending_semaphores > 0:
            self.pending_semaphores -= 1


class MockAgentServerRegistry:
    """In-memory AgentServer registry for testing."""

    def __init__(self) -> None:
        self._servers: dict[str, MockAgentServer] = {}

    def create(
        self,
        name: str,
        namespace: str = "kgents-system",
        **kwargs: Any,
    ) -> MockAgentServer:
        """Create a new AgentServer."""
        server = MockAgentServer(name=name, namespace=namespace, **kwargs)
        server.reconcile()
        self._servers[f"{namespace}/{name}"] = server
        logger.info(f"Created AgentServer: {name}")
        return server

    def get(
        self, name: str, namespace: str = "kgents-system"
    ) -> MockAgentServer | None:
        """Get an AgentServer by name."""
        return self._servers.get(f"{namespace}/{name}")

    def list(self) -> list[MockAgentServer]:
        """List all AgentServers."""
        return list(self._servers.values())

    def delete(self, name: str, namespace: str = "kgents-system") -> bool:
        """Delete an AgentServer."""
        key = f"{namespace}/{name}"
        if key in self._servers:
            del self._servers[key]
            logger.info(f"Deleted AgentServer: {name}")
            return True
        return False


# Global mock registry for testing
_mock_registry: MockAgentServerRegistry | None = None


def get_mock_registry() -> MockAgentServerRegistry:
    """Get or create the global mock AgentServer registry."""
    global _mock_registry
    if _mock_registry is None:
        _mock_registry = MockAgentServerRegistry()
    return _mock_registry


def reset_mock_registry() -> None:
    """Reset the global mock registry (for testing)."""
    global _mock_registry
    _mock_registry = None
