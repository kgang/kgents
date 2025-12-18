"""
Kubernetes Infrastructure Collector

Collects topology and events from a Kubernetes cluster.

Features:
- Pods with status, labels, and metrics
- Services with endpoints and label selectors
- Deployments with replica status
- Pod-to-service connections via label matching
- Real-time event streaming

Requires: pip install kubernetes
Or: uv add kubernetes

@see plans/gestalt-live-infrastructure.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, AsyncIterator

from ..health import calculate_entity_health
from ..models import (
    InfraConnection,
    InfraConnectionKind,
    InfraEntity,
    InfraEntityKind,
    InfraEntityStatus,
    InfraEvent,
    InfraEventSeverity,
    InfraTopology,
)
from .base import BaseCollector, CollectorConfig

# Lazy import kubernetes to handle when it's not installed
if TYPE_CHECKING:
    from kubernetes import client as k8s_client
    from kubernetes.client import ApiClient


logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class KubernetesConfig(CollectorConfig):
    """Configuration for Kubernetes collector."""

    # Kubernetes connection
    kubeconfig: str | None = None  # Path to kubeconfig, None = in-cluster
    context: str | None = None  # Kubeconfig context to use

    # Namespace filtering (empty = all namespaces)
    namespaces: list[str] = field(default_factory=list)

    # What to collect
    collect_pods: bool = True
    collect_services: bool = True
    collect_deployments: bool = True
    collect_configmaps: bool = False
    collect_secrets: bool = False  # Be careful with secrets!

    # Metrics collection (requires metrics-server)
    collect_metrics: bool = True


# =============================================================================
# Status Mapping
# =============================================================================


def _pod_phase_to_status(phase: str) -> InfraEntityStatus:
    """Map Kubernetes pod phase to InfraEntityStatus."""
    return {
        "Running": InfraEntityStatus.RUNNING,
        "Pending": InfraEntityStatus.PENDING,
        "Succeeded": InfraEntityStatus.SUCCEEDED,
        "Failed": InfraEntityStatus.FAILED,
        "Unknown": InfraEntityStatus.UNKNOWN,
    }.get(phase, InfraEntityStatus.UNKNOWN)


def _container_state_to_status(state: dict) -> InfraEntityStatus:
    """Map container state to InfraEntityStatus."""
    if state.get("running"):
        return InfraEntityStatus.RUNNING
    elif state.get("waiting"):
        return InfraEntityStatus.PENDING
    elif state.get("terminated"):
        exit_code = state["terminated"].get("exitCode", -1)
        return InfraEntityStatus.SUCCEEDED if exit_code == 0 else InfraEntityStatus.FAILED
    return InfraEntityStatus.UNKNOWN


def _k8s_event_severity(event_type: str, reason: str) -> InfraEventSeverity:
    """Determine severity from Kubernetes event type and reason."""
    # Warning type is always at least WARNING
    if event_type == "Warning":
        # Some warnings are more severe
        if any(word in reason.lower() for word in ["failed", "error", "kill", "evict"]):
            return InfraEventSeverity.ERROR
        if any(word in reason.lower() for word in ["oom", "crash", "backoff"]):
            return InfraEventSeverity.CRITICAL
        return InfraEventSeverity.WARNING

    # Normal events
    return InfraEventSeverity.INFO


# =============================================================================
# Kubernetes Collector
# =============================================================================


class KubernetesCollector(BaseCollector):
    """
    Kubernetes cluster data collector.

    Collects pods, services, deployments, and events from a Kubernetes cluster.
    Builds connections based on label selectors (service → pods).

    Usage:
        config = KubernetesConfig(namespaces=["default", "kgents"])
        collector = KubernetesCollector(config)
        await collector.connect()

        topology = await collector.collect_topology()
        for entity in topology.entities:
            print(f"{entity.kind}: {entity.name} - {entity.status}")

        await collector.disconnect()
    """

    def __init__(self, config: KubernetesConfig | None = None):
        super().__init__(config or KubernetesConfig())
        self.config: KubernetesConfig = self.config
        self._api_client: ApiClient | None = None
        self._core_v1: k8s_client.CoreV1Api | None = None
        self._apps_v1: k8s_client.AppsV1Api | None = None
        self._watch_tasks: list[asyncio.Task] = []

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> None:
        """Connect to Kubernetes API."""
        try:
            from kubernetes import client as k8s_client, config as k8s_config
        except ImportError as e:
            raise ImportError(
                "kubernetes package not installed. Install with: uv add kubernetes"
            ) from e

        try:
            if self.config.kubeconfig:
                # Load from kubeconfig file
                k8s_config.load_kube_config(
                    config_file=self.config.kubeconfig,
                    context=self.config.context,
                )
            else:
                # Try in-cluster config first, fall back to kubeconfig
                try:
                    k8s_config.load_incluster_config()
                except k8s_config.ConfigException:
                    k8s_config.load_kube_config(context=self.config.context)

            self._api_client = k8s_client.ApiClient()
            self._core_v1 = k8s_client.CoreV1Api(self._api_client)
            self._apps_v1 = k8s_client.AppsV1Api(self._api_client)
            self._connected = True

            logger.info("Connected to Kubernetes cluster")

        except Exception as e:
            logger.error(f"Failed to connect to Kubernetes: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Kubernetes API."""
        # Cancel any watch tasks
        for task in self._watch_tasks:
            task.cancel()
        self._watch_tasks.clear()

        if self._api_client:
            self._api_client.close()
            self._api_client = None

        self._core_v1 = None
        self._apps_v1 = None
        self._connected = False

        logger.info("Disconnected from Kubernetes cluster")

    async def health_check(self) -> bool:
        """Check if Kubernetes API is accessible."""
        if not self._core_v1:
            return False

        try:
            # Simple health check - list namespaces (lightweight operation)
            await asyncio.to_thread(self._core_v1.list_namespace, limit=1)
            return True
        except Exception as e:
            logger.warning(f"Kubernetes health check failed: {e}")
            return False

    # =========================================================================
    # Topology Collection
    # =========================================================================

    async def collect_topology(self) -> InfraTopology:
        """Collect current Kubernetes topology."""
        if not self._core_v1 or not self._apps_v1:
            raise RuntimeError("Not connected to Kubernetes. Call connect() first.")

        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        # Collect all resource types in parallel
        tasks = []
        if self.config.collect_pods:
            tasks.append(self._collect_pods())
        if self.config.collect_services:
            tasks.append(self._collect_services())
        if self.config.collect_deployments:
            tasks.append(self._collect_deployments())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error collecting resources: {result}")
                continue
            if isinstance(result, tuple):
                resource_entities, resource_connections = result
                entities.extend(resource_entities)
                connections.extend(resource_connections)

        # Build service-to-pod connections based on label selectors
        if self.config.collect_services and self.config.collect_pods:
            selector_connections = self._build_selector_connections(entities)
            connections.extend(selector_connections)

        # Calculate health scores
        for entity in entities:
            entity.health = calculate_entity_health(entity)

        # Calculate positions
        self.calculate_positions(entities, connections)

        return InfraTopology(
            entities=entities,
            connections=connections,
            timestamp=datetime.now(timezone.utc),
        )

    async def _collect_pods(self) -> tuple[list[InfraEntity], list[InfraConnection]]:
        """Collect pod entities."""
        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        pods = await self._list_pods()

        for pod in pods.items:
            metadata = pod.metadata
            spec = pod.spec
            status = pod.status

            # Skip pods not in configured namespaces
            if self.config.namespaces and metadata.namespace not in self.config.namespaces:
                continue

            # Calculate restart count
            restart_count = 0
            if status.container_statuses:
                restart_count = sum(cs.restart_count for cs in status.container_statuses)

            # Get owner references from metadata (not spec)
            owner_refs = metadata.owner_references or []

            entity = InfraEntity(
                id=f"pod/{metadata.namespace}/{metadata.name}",
                kind=InfraEntityKind.POD,
                name=metadata.name,
                namespace=metadata.namespace,
                labels=dict(metadata.labels or {}),
                annotations=dict(metadata.annotations or {}),
                status=_pod_phase_to_status(status.phase),
                status_message=self._get_pod_status_message(status),
                created_at=metadata.creation_timestamp,
                owner_kind=owner_refs[0].kind if owner_refs else None,
                owner_name=owner_refs[0].name if owner_refs else None,
                custom_metrics={"restart_count": restart_count},
                source="kubernetes",
                source_data={
                    "node_name": spec.node_name,
                    "host_ip": status.host_ip,
                    "pod_ip": status.pod_ip,
                    "qos_class": status.qos_class,
                },
            )

            entities.append(entity)

            # Add connection to node if we have node info
            if spec.node_name:
                connections.append(
                    InfraConnection(
                        source_id=entity.id,
                        target_id=f"node/{spec.node_name}",
                        kind=InfraConnectionKind.NETWORK,
                    )
                )

        return entities, connections

    async def _collect_services(
        self,
    ) -> tuple[list[InfraEntity], list[InfraConnection]]:
        """Collect service entities."""
        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        services = await self._list_services()

        for svc in services.items:
            metadata = svc.metadata
            spec = svc.spec

            # Skip services not in configured namespaces
            if self.config.namespaces and metadata.namespace not in self.config.namespaces:
                continue

            entity = InfraEntity(
                id=f"service/{metadata.namespace}/{metadata.name}",
                kind=InfraEntityKind.SERVICE,
                name=metadata.name,
                namespace=metadata.namespace,
                labels=dict(metadata.labels or {}),
                annotations=dict(metadata.annotations or {}),
                status=InfraEntityStatus.RUNNING,  # Services are always "running"
                created_at=metadata.creation_timestamp,
                source="kubernetes",
                source_data={
                    "type": spec.type,
                    "cluster_ip": spec.cluster_ip,
                    "ports": [
                        {
                            "port": p.port,
                            "target_port": str(p.target_port),
                            "protocol": p.protocol,
                        }
                        for p in (spec.ports or [])
                    ],
                    "selector": dict(spec.selector or {}),
                },
            )

            entities.append(entity)

        return entities, connections

    async def _collect_deployments(
        self,
    ) -> tuple[list[InfraEntity], list[InfraConnection]]:
        """Collect deployment entities."""
        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        deployments = await self._list_deployments()

        for deploy in deployments.items:
            metadata = deploy.metadata
            spec = deploy.spec
            status = deploy.status

            # Skip deployments not in configured namespaces
            if self.config.namespaces and metadata.namespace not in self.config.namespaces:
                continue

            # Determine status based on replica counts
            desired = spec.replicas or 0
            ready = status.ready_replicas or 0
            available = status.available_replicas or 0

            if ready == desired and available == desired:
                deploy_status = InfraEntityStatus.RUNNING
            elif ready == 0:
                deploy_status = InfraEntityStatus.FAILED
            else:
                deploy_status = InfraEntityStatus.PENDING

            entity = InfraEntity(
                id=f"deployment/{metadata.namespace}/{metadata.name}",
                kind=InfraEntityKind.DEPLOYMENT,
                name=metadata.name,
                namespace=metadata.namespace,
                labels=dict(metadata.labels or {}),
                annotations=dict(metadata.annotations or {}),
                status=deploy_status,
                status_message=f"{ready}/{desired} ready",
                created_at=metadata.creation_timestamp,
                custom_metrics={
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "available_replicas": available,
                },
                source="kubernetes",
                source_data={
                    "strategy": spec.strategy.type if spec.strategy else None,
                    "selector": dict(spec.selector.match_labels or {}) if spec.selector else {},
                },
            )

            entities.append(entity)

        return entities, connections

    def _build_selector_connections(self, entities: list[InfraEntity]) -> list[InfraConnection]:
        """Build connections from services/deployments to pods via label selectors."""
        connections: list[InfraConnection] = []

        # Index pods by their labels for efficient matching
        pods_by_label: dict[tuple[str, str, str], list[InfraEntity]] = {}  # (ns, key, val) -> pods
        for entity in entities:
            if entity.kind == InfraEntityKind.POD:
                for key, val in entity.labels.items():
                    label_key = (entity.namespace or "", key, val)
                    if label_key not in pods_by_label:
                        pods_by_label[label_key] = []
                    pods_by_label[label_key].append(entity)

        # Match services to pods
        for entity in entities:
            if entity.kind == InfraEntityKind.SERVICE:
                selector = entity.source_data.get("selector", {})
                if not selector:
                    continue

                # Find pods matching ALL selector labels
                matching_pods: set[str] | None = None
                for key, val in selector.items():
                    label_key = (entity.namespace or "", key, val)
                    pod_ids = {p.id for p in pods_by_label.get(label_key, [])}

                    if matching_pods is None:
                        matching_pods = pod_ids
                    else:
                        matching_pods &= pod_ids

                # Create connections
                for pod_id in matching_pods or set():
                    connections.append(
                        InfraConnection(
                            source_id=entity.id,
                            target_id=pod_id,
                            kind=InfraConnectionKind.SELECTS,
                        )
                    )

        # Match deployments to pods
        for entity in entities:
            if entity.kind == InfraEntityKind.DEPLOYMENT:
                selector = entity.source_data.get("selector", {})
                if not selector:
                    continue

                # Find pods matching ALL selector labels
                matching_pods: set[str] | None = None
                for key, val in selector.items():
                    label_key = (entity.namespace or "", key, val)
                    pod_ids = {p.id for p in pods_by_label.get(label_key, [])}

                    if matching_pods is None:
                        matching_pods = pod_ids
                    else:
                        matching_pods &= pod_ids

                # Create OWNS connections for deployment->pod
                for pod_id in matching_pods or set():
                    connections.append(
                        InfraConnection(
                            source_id=entity.id,
                            target_id=pod_id,
                            kind=InfraConnectionKind.OWNS,
                        )
                    )

        return connections

    def _get_pod_status_message(self, status: Any) -> str | None:
        """Extract a status message from pod status."""
        # Check conditions for meaningful status
        if status.conditions:
            for condition in status.conditions:
                if condition.status != "True" and condition.message:
                    return condition.message

        # Check container statuses
        if status.container_statuses:
            for cs in status.container_statuses:
                if cs.state:
                    if cs.state.waiting and cs.state.waiting.reason:
                        return f"Waiting: {cs.state.waiting.reason}"
                    if cs.state.terminated and cs.state.terminated.reason:
                        return f"Terminated: {cs.state.terminated.reason}"

        return None

    # =========================================================================
    # Event Streaming
    # =========================================================================

    async def stream_events(self) -> AsyncIterator[InfraEvent]:
        """Stream Kubernetes events in real-time."""
        if not self._core_v1:
            raise RuntimeError("Not connected to Kubernetes. Call connect() first.")

        try:
            from kubernetes import watch
        except ImportError as e:
            raise ImportError(
                "kubernetes package not installed. Install with: uv add kubernetes"
            ) from e

        w = watch.Watch()

        try:
            # Watch events across namespaces (or specific ones)
            if self.config.namespaces:
                for ns in self.config.namespaces:
                    async for event in self._watch_namespace_events(w, ns):
                        yield event
            else:
                async for event in self._watch_all_events(w):
                    yield event
        finally:
            w.stop()

    async def _watch_all_events(self, w: Any) -> AsyncIterator[InfraEvent]:
        """Watch events across all namespaces."""

        # Run watch in thread since kubernetes client is synchronous
        def _watch():
            return w.stream(self._core_v1.list_event_for_all_namespaces)

        stream = await asyncio.to_thread(_watch)

        for event in stream:
            if not self._connected:
                break

            k8s_event = event["object"]
            yield self._convert_k8s_event(k8s_event)

    async def _watch_namespace_events(self, w: Any, namespace: str) -> AsyncIterator[InfraEvent]:
        """Watch events in a specific namespace."""

        def _watch():
            return w.stream(self._core_v1.list_namespaced_event, namespace=namespace)

        stream = await asyncio.to_thread(_watch)

        for event in stream:
            if not self._connected:
                break

            k8s_event = event["object"]
            yield self._convert_k8s_event(k8s_event)

    def _convert_k8s_event(self, k8s_event: Any) -> InfraEvent:
        """Convert Kubernetes event object to InfraEvent."""
        involved = k8s_event.involved_object
        source = k8s_event.source or {}

        # Map involved object kind to InfraEntityKind
        kind_map = {
            "Pod": InfraEntityKind.POD,
            "Service": InfraEntityKind.SERVICE,
            "Deployment": InfraEntityKind.DEPLOYMENT,
            "ReplicaSet": InfraEntityKind.DEPLOYMENT,  # Map to parent
            "Node": InfraEntityKind.NODE,
            "ConfigMap": InfraEntityKind.CONFIGMAP,
            "Secret": InfraEntityKind.SECRET,
            "PersistentVolumeClaim": InfraEntityKind.PVC,
        }
        entity_kind = kind_map.get(involved.kind, InfraEntityKind.CUSTOM)

        return InfraEvent(
            id=k8s_event.metadata.uid,
            type=k8s_event.type or "Normal",
            reason=k8s_event.reason or "Unknown",
            message=k8s_event.message or "",
            severity=_k8s_event_severity(k8s_event.type or "Normal", k8s_event.reason or ""),
            entity_id=f"{involved.kind.lower()}/{involved.namespace}/{involved.name}",
            entity_kind=entity_kind,
            entity_name=involved.name,
            entity_namespace=involved.namespace,
            timestamp=k8s_event.last_timestamp or datetime.now(timezone.utc),
            first_timestamp=k8s_event.first_timestamp,
            last_timestamp=k8s_event.last_timestamp,
            count=k8s_event.count or 1,
            source="kubernetes",
            source_component=source.component if hasattr(source, "component") else None,
            source_host=source.host if hasattr(source, "host") else None,
        )

    # =========================================================================
    # Kubernetes API Helpers (run in thread pool)
    # =========================================================================

    async def _list_pods(self) -> Any:
        """List pods (possibly filtered by namespace)."""
        if self.config.namespaces:
            # Collect from specific namespaces
            all_pods = type("obj", (object,), {"items": []})()
            for ns in self.config.namespaces:
                ns_pods = await asyncio.to_thread(self._core_v1.list_namespaced_pod, namespace=ns)
                all_pods.items.extend(ns_pods.items)
            return all_pods
        else:
            return await asyncio.to_thread(self._core_v1.list_pod_for_all_namespaces)

    async def _list_services(self) -> Any:
        """List services (possibly filtered by namespace)."""
        if self.config.namespaces:
            all_services = type("obj", (object,), {"items": []})()
            for ns in self.config.namespaces:
                ns_services = await asyncio.to_thread(
                    self._core_v1.list_namespaced_service, namespace=ns
                )
                all_services.items.extend(ns_services.items)
            return all_services
        else:
            return await asyncio.to_thread(self._core_v1.list_service_for_all_namespaces)

    async def _list_deployments(self) -> Any:
        """List deployments (possibly filtered by namespace)."""
        if self.config.namespaces:
            all_deployments = type("obj", (object,), {"items": []})()
            for ns in self.config.namespaces:
                ns_deployments = await asyncio.to_thread(
                    self._apps_v1.list_namespaced_deployment, namespace=ns
                )
                all_deployments.items.extend(ns_deployments.items)
            return all_deployments
        else:
            return await asyncio.to_thread(self._apps_v1.list_deployment_for_all_namespaces)


# =============================================================================
# Mock Collector for Development
# =============================================================================


class MockKubernetesCollector(BaseCollector):
    """
    Mock Kubernetes collector for development and testing.

    Generates realistic-looking topology without requiring an actual cluster.
    Useful for frontend development and testing.
    """

    def __init__(self, config: CollectorConfig | None = None):
        super().__init__(config or CollectorConfig())
        self._event_counter = 0

    async def connect(self) -> None:
        """Mock connection (always succeeds)."""
        self._connected = True
        logger.info("Mock Kubernetes collector connected")

    async def disconnect(self) -> None:
        """Mock disconnection."""
        self._connected = False
        logger.info("Mock Kubernetes collector disconnected")

    async def collect_topology(self) -> InfraTopology:
        """Generate mock topology."""
        import random

        entities: list[InfraEntity] = []
        connections: list[InfraConnection] = []

        namespaces = ["default", "kgents", "monitoring"]

        for ns in namespaces:
            # Generate pods
            pod_count = random.randint(3, 8)
            for i in range(pod_count):
                health = random.uniform(0.5, 1.0)
                status = (
                    InfraEntityStatus.RUNNING
                    if health > 0.7
                    else InfraEntityStatus.PENDING
                    if health > 0.5
                    else InfraEntityStatus.FAILED
                )

                pod = InfraEntity(
                    id=f"pod/{ns}/app-{i}",
                    kind=InfraEntityKind.POD,
                    name=f"app-{i}",
                    namespace=ns,
                    labels={"app": "demo", "version": "v1"},
                    status=status,
                    health=health,
                    cpu_percent=random.uniform(10, 80),
                    memory_bytes=random.randint(100_000_000, 500_000_000),
                    memory_limit=512_000_000,
                    custom_metrics={"restart_count": random.randint(0, 5)},
                    source="kubernetes",
                )
                entities.append(pod)

            # Generate services
            svc = InfraEntity(
                id=f"service/{ns}/app-svc",
                kind=InfraEntityKind.SERVICE,
                name="app-svc",
                namespace=ns,
                labels={"app": "demo"},
                status=InfraEntityStatus.RUNNING,
                health=1.0,
                source="kubernetes",
                source_data={"selector": {"app": "demo"}, "type": "ClusterIP"},
            )
            entities.append(svc)

            # Generate deployments
            deploy = InfraEntity(
                id=f"deployment/{ns}/app",
                kind=InfraEntityKind.DEPLOYMENT,
                name="app",
                namespace=ns,
                labels={"app": "demo"},
                status=InfraEntityStatus.RUNNING,
                health=0.95,
                custom_metrics={
                    "desired_replicas": pod_count,
                    "ready_replicas": pod_count - random.randint(0, 1),
                },
                source="kubernetes",
                source_data={"selector": {"app": "demo"}},
            )
            entities.append(deploy)

            # Create connections
            for pod in entities:
                if pod.kind == InfraEntityKind.POD and pod.namespace == ns:
                    # Service -> Pod
                    connections.append(
                        InfraConnection(
                            source_id=svc.id,
                            target_id=pod.id,
                            kind=InfraConnectionKind.SELECTS,
                        )
                    )
                    # Deployment -> Pod
                    connections.append(
                        InfraConnection(
                            source_id=deploy.id,
                            target_id=pod.id,
                            kind=InfraConnectionKind.OWNS,
                        )
                    )

        # Calculate positions
        self.calculate_positions(entities, connections)

        return InfraTopology(
            entities=entities,
            connections=connections,
            timestamp=datetime.now(timezone.utc),
        )

    async def stream_events(self) -> AsyncIterator[InfraEvent]:
        """Generate mock events."""
        import random

        reasons = ["Started", "Pulled", "Created", "Scheduled", "Killing", "BackOff"]
        namespaces = ["default", "kgents", "monitoring"]

        while self._connected:
            await asyncio.sleep(random.uniform(2, 8))

            self._event_counter += 1
            ns = random.choice(namespaces)
            reason = random.choice(reasons)

            severity = (
                InfraEventSeverity.WARNING
                if reason in ("Killing", "BackOff")
                else InfraEventSeverity.INFO
            )

            yield InfraEvent(
                id=f"mock-event-{self._event_counter}",
                type="Warning" if severity != InfraEventSeverity.INFO else "Normal",
                reason=reason,
                message=f"Mock event: {reason} for pod in {ns}",
                severity=severity,
                entity_id=f"pod/{ns}/app-0",
                entity_kind=InfraEntityKind.POD,
                entity_name="app-0",
                entity_namespace=ns,
                timestamp=datetime.now(timezone.utc),
                source="kubernetes-mock",
            )
