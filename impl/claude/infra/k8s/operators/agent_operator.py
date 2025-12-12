"""Agent Operator - Reconcile Agent CRs to Deployments.

The agent operator manages the lifecycle of Agent CRs:
1. On CREATE: Generate Deployment + Service + NetworkPolicy + Memory CR
2. On UPDATE: Reconcile changes (rolling update)
3. On DELETE: Cleanup resources (respecting memory retention)
4. On TIMER: Run cognitive probes for health checks

This makes agents first-class K8s citizens:
    kubectl get agents --watch

Principle alignment:
- C-gent (Composability): Agent CR is a single source of truth
- T-gent (Testing): PLACEHOLDER mode prevents CrashLoopBackOff
- E-gent (Thermodynamics): Cognitive probes detect degradation
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

# Import the existing AgentSpec and related classes
from ..operator import (
    AgentPhase,
    AgentSpec,
    DeployMode,
    ReconcileResult,
)

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
COGNITIVE_PROBE_INTERVAL = 30.0  # seconds
MEMORY_CREATE_DELAY = 5.0  # Wait for deployment before creating memory


def parse_agent_spec(
    spec: dict[str, Any],
    meta: dict[str, Any],
) -> AgentSpec:
    """Parse CRD spec into AgentSpec dataclass."""
    resources = spec.get("resources", {})
    limits = resources.get("limits", {})
    requests = resources.get("requests", {})
    symbiont = spec.get("symbiont", {})
    memory_config = symbiont.get("memory", {})
    network = spec.get("networkPolicy", {})

    # Map deployMode string to enum
    deploy_mode_str = spec.get("deployMode", "PLACEHOLDER")
    deploy_mode = {
        "FULL": DeployMode.FULL,
        "PLACEHOLDER": DeployMode.PLACEHOLDER,
        "DRY_RUN": DeployMode.DRY_RUN,
    }.get(deploy_mode_str, DeployMode.PLACEHOLDER)

    return AgentSpec(
        name=meta.get("name", ""),
        namespace=meta.get("namespace", "kgents-agents"),
        genus=spec.get("genus", ""),
        image=spec.get("image", "python:3.12-slim"),
        replicas=spec.get("replicas", 1),
        cpu=limits.get("cpu", "500m"),
        memory=limits.get("memory", "512Mi"),
        sidecar_enabled=memory_config.get("enabled", True),
        sidecar_image="python:3.12-slim",
        entrypoint=spec.get("entrypoint"),
        config=spec.get("config", {}),
        allow_egress=network.get("allowEgress", False),
        allowed_peers=network.get("allowedPeers", []),
        deploy_mode=deploy_mode,
    )


def generate_memory_cr(
    agent_name: str,
    namespace: str,
    genus: str,
    memory_config: dict[str, Any],
    owner_uid: str,
) -> dict[str, Any]:
    """Generate a Memory CR for the agent."""
    return {
        "apiVersion": "kgents.io/v1",
        "kind": "Memory",
        "metadata": {
            "name": f"{agent_name}-memory",
            "namespace": namespace,
            "labels": {
                "app.kubernetes.io/part-of": "kgents",
                "app.kubernetes.io/managed-by": "agent-operator",
                "kgents.io/genus": genus,
                "kgents.io/owner": agent_name,
            },
            "ownerReferences": [
                {
                    "apiVersion": "kgents.io/v1",
                    "kind": "Agent",
                    "name": agent_name,
                    "uid": owner_uid,
                    "controller": True,
                    "blockOwnerDeletion": memory_config.get("retentionPolicy")
                    == "DELETE",
                }
            ],
        },
        "spec": {
            "owner": f"{genus}-gent",
            "type": memory_config.get("type", "BICAMERAL"),
            "size": memory_config.get("size", "256Mi"),
            "retention_policy": memory_config.get("retentionPolicy", "COMPOST"),
        },
    }


# ============================================================================
# Kopf Handlers (only registered if kopf is available)
# ============================================================================

if KOPF_AVAILABLE:

    @kopf.on.create("kgents.io", "v1", "agents")  # type: ignore[arg-type]
    async def on_agent_create(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Create Deployment, Service, NetworkPolicy, and Memory CR for new Agent."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        uid = meta.get("uid", "")
        genus = spec.get("genus", "UNKNOWN")

        logger.info(f"Creating agent: {name} (genus={genus})")

        # Parse spec
        agent_spec = parse_agent_spec(spec, meta)

        # Validate spec
        validation = agent_spec.validate(
            check_image=False
        )  # Skip image check in operator
        if not validation.valid:
            logger.error(f"Agent validation failed: {validation.errors}")
            patch.status["phase"] = AgentPhase.FAILED.value
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "ValidationFailed",
                    "message": ", ".join(validation.errors),
                    "lastTransitionTime": datetime.now(timezone.utc).isoformat(),
                }
            ]
            return {"created": False, "error": validation.errors}

        # Log warnings
        for warning in validation.warnings:
            logger.warning(f"Agent {name}: {warning}")

        # Handle DRY_RUN mode
        if agent_spec.deploy_mode == DeployMode.DRY_RUN:
            logger.info(f"Agent {name} in DRY_RUN mode - skipping deployment")
            patch.status["phase"] = AgentPhase.PENDING.value
            return {"created": False, "mode": "dry_run"}

        created_resources: list[str] = []
        apps_api = client.AppsV1Api()
        core_api = client.CoreV1Api()
        networking_api = client.NetworkingV1Api()
        custom_api = client.CustomObjectsApi()

        try:
            # 1. Create Deployment
            deployment = agent_spec.to_deployment()
            # Add owner reference
            deployment["metadata"]["ownerReferences"] = [
                {
                    "apiVersion": "kgents.io/v1",
                    "kind": "Agent",
                    "name": name,
                    "uid": uid,
                    "controller": True,
                    "blockOwnerDeletion": True,
                }
            ]

            try:
                apps_api.create_namespaced_deployment(
                    namespace=namespace,
                    body=deployment,
                )
                created_resources.append(f"deployment/{deployment['metadata']['name']}")
                logger.info(f"Created deployment: {deployment['metadata']['name']}")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(
                        f"Deployment already exists: {deployment['metadata']['name']}"
                    )
                else:
                    raise

            # 2. Create Service
            service = agent_spec.to_service()
            service["metadata"]["ownerReferences"] = [
                {
                    "apiVersion": "kgents.io/v1",
                    "kind": "Agent",
                    "name": name,
                    "uid": uid,
                    "controller": True,
                    "blockOwnerDeletion": True,
                }
            ]

            try:
                core_api.create_namespaced_service(
                    namespace=namespace,
                    body=service,
                )
                created_resources.append(f"service/{service['metadata']['name']}")
                logger.info(f"Created service: {service['metadata']['name']}")
            except ApiException as e:
                if e.status == 409:
                    logger.info(
                        f"Service already exists: {service['metadata']['name']}"
                    )
                else:
                    raise

            # 3. Create NetworkPolicy (if needed)
            network_policy = agent_spec.to_network_policy()
            if network_policy:
                network_policy["metadata"]["ownerReferences"] = [
                    {
                        "apiVersion": "kgents.io/v1",
                        "kind": "Agent",
                        "name": name,
                        "uid": uid,
                        "controller": True,
                        "blockOwnerDeletion": True,
                    }
                ]

                try:
                    networking_api.create_namespaced_network_policy(
                        namespace=namespace,
                        body=network_policy,
                    )
                    created_resources.append(
                        f"networkpolicy/{network_policy['metadata']['name']}"
                    )
                    logger.info(
                        f"Created network policy: {network_policy['metadata']['name']}"
                    )
                except ApiException as e:
                    if e.status == 409:
                        logger.info(
                            f"NetworkPolicy already exists: {network_policy['metadata']['name']}"
                        )
                    else:
                        raise

            # 4. Create Memory CR (if enabled)
            symbiont = spec.get("symbiont", {})
            memory_config = symbiont.get("memory", {})
            if memory_config.get("enabled", True):
                memory_cr = generate_memory_cr(
                    agent_name=name,
                    namespace=namespace,
                    genus=genus,
                    memory_config=memory_config,
                    owner_uid=uid,
                )

                try:
                    custom_api.create_namespaced_custom_object(
                        group="kgents.io",
                        version="v1",
                        namespace=namespace,
                        plural="memories",
                        body=memory_cr,
                    )
                    created_resources.append(f"memory/{memory_cr['metadata']['name']}")
                    logger.info(f"Created memory: {memory_cr['metadata']['name']}")
                except ApiException as e:
                    if e.status == 409:
                        logger.info(
                            f"Memory already exists: {memory_cr['metadata']['name']}"
                        )
                    else:
                        raise

            # Update status
            now = datetime.now(timezone.utc).isoformat()
            patch.status["phase"] = AgentPhase.PENDING.value
            patch.status["observedGeneration"] = meta.get("generation", 1)
            patch.status["deployment"] = f"{genus.lower()}-gent"
            patch.status["service"] = f"{genus.lower()}-gent"
            if memory_config.get("enabled", True):
                patch.status["memory"] = f"{name}-memory"
            patch.status["cognitiveHealth"] = "UNKNOWN"
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "DeploymentCreated",
                    "message": "Waiting for pods to be ready",
                    "lastTransitionTime": now,
                }
            ]

            logger.info(f"Agent {name} created successfully: {created_resources}")
            return {"created": True, "resources": created_resources}

        except Exception as e:
            logger.error(f"Failed to create agent {name}: {e}")
            patch.status["phase"] = AgentPhase.FAILED.value
            patch.status["conditions"] = [
                {
                    "type": "Ready",
                    "status": "False",
                    "reason": "CreationFailed",
                    "message": str(e),
                    "lastTransitionTime": datetime.now(timezone.utc).isoformat(),
                }
            ]
            raise kopf.PermanentError(f"Failed to create agent: {e}")

    @kopf.on.update("kgents.io", "v1", "agents")  # type: ignore[arg-type]
    async def on_agent_update(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        diff: kopf.Diff,
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Update Deployment when Agent spec changes."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        genus = spec.get("genus", "UNKNOWN")

        logger.info(f"Updating agent: {name}")

        # Parse spec
        agent_spec = parse_agent_spec(spec, meta)

        # Validate
        validation = agent_spec.validate(check_image=False)
        if not validation.valid:
            logger.error(f"Agent validation failed: {validation.errors}")
            return {"updated": False, "error": validation.errors}

        apps_api = client.AppsV1Api()

        try:
            # Update Deployment
            deployment = agent_spec.to_deployment()
            deployment_name = f"{genus.lower()}-gent"

            apps_api.patch_namespaced_deployment(
                name=deployment_name,
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

            logger.info(f"Agent {name} updated successfully")
            return {"updated": True}

        except ApiException as e:
            if e.status == 404:
                # Deployment doesn't exist - create it
                logger.warning(f"Deployment not found for agent {name}, creating...")
                return {"updated": False, "recreate_needed": True}
            raise

    @kopf.on.delete("kgents.io", "v1", "agents")  # type: ignore[arg-type]
    async def on_agent_delete(
        spec: dict[str, Any],
        meta: dict[str, Any],
        **_: Any,
    ) -> dict[str, Any]:
        """Clean up resources when Agent is deleted.

        Note: Resources with ownerReferences are garbage collected automatically.
        This handler is for logging and any custom cleanup.
        """
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        genus = spec.get("genus", "UNKNOWN")

        logger.info(f"Deleting agent: {name} (genus={genus})")

        # Check memory retention policy
        symbiont = spec.get("symbiont", {})
        memory_config = symbiont.get("memory", {})
        retention = memory_config.get("retentionPolicy", "COMPOST")

        if retention == "RETAIN":
            logger.info(f"Memory for agent {name} will be retained (policy: RETAIN)")
        elif retention == "COMPOST":
            logger.info(
                f"Memory for agent {name} marked for composting (policy: COMPOST)"
            )
            # Update Memory CR status to COMPOSTING
            custom_api = client.CustomObjectsApi()
            try:
                custom_api.patch_namespaced_custom_object_status(
                    group="kgents.io",
                    version="v1",
                    namespace=namespace,
                    plural="memories",
                    name=f"{name}-memory",
                    body={"status": {"phase": "COMPOSTING"}},
                )
            except ApiException:
                pass  # Memory may not exist or already deleted
        else:
            logger.info(f"Memory for agent {name} will be deleted (policy: DELETE)")

        return {"deleted": True, "memory_retention": retention}

    @kopf.timer("kgents.io", "v1", "agents", interval=COGNITIVE_PROBE_INTERVAL)  # type: ignore[arg-type]
    async def cognitive_health_check(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any] | None:
        """Periodically check cognitive health of agents.

        Uses SCU (Standard Cognitive Unit) probes for LLM-based agents.
        """
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        genus = spec.get("genus", "UNKNOWN")
        current_phase = status.get("phase", "Pending")

        # Skip if not running
        if current_phase != AgentPhase.RUNNING.value:
            return None

        # Check if cognitive probes are enabled
        health_config = spec.get("health", {})
        health_type = health_config.get("type", "HTTP")

        if health_type != "COGNITIVE_PROBE":
            return None

        apps_api = client.AppsV1Api()

        try:
            # Get deployment status
            deployment_name = f"{genus.lower()}-gent"
            deployment = apps_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )

            ready_replicas = deployment.status.ready_replicas or 0
            desired_replicas = deployment.spec.replicas or 1

            now = datetime.now(timezone.utc).isoformat()

            if ready_replicas >= desired_replicas:
                # All replicas ready - mark as healthy
                # TODO: Actually run SCU probe against agent endpoint
                patch.status["phase"] = AgentPhase.RUNNING.value
                patch.status["readyReplicas"] = ready_replicas
                patch.status["cognitiveHealth"] = "HEALTHY"
                patch.status["lastProbeTime"] = now
                patch.status["conditions"] = [
                    {
                        "type": "Ready",
                        "status": "True",
                        "reason": "AllReplicasReady",
                        "message": f"{ready_replicas}/{desired_replicas} replicas ready",
                        "lastTransitionTime": now,
                    }
                ]
                return {"health": "HEALTHY", "ready": ready_replicas}
            elif ready_replicas > 0:
                # Partially ready - degraded
                patch.status["phase"] = AgentPhase.DEGRADED.value
                patch.status["readyReplicas"] = ready_replicas
                patch.status["cognitiveHealth"] = "DEGRADED"
                patch.status["lastProbeTime"] = now
                return {"health": "DEGRADED", "ready": ready_replicas}
            else:
                # No ready replicas
                patch.status["readyReplicas"] = 0
                patch.status["cognitiveHealth"] = "UNRESPONSIVE"
                patch.status["lastProbeTime"] = now
                return {"health": "UNRESPONSIVE", "ready": 0}

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Deployment not found for agent {name}")
                patch.status["cognitiveHealth"] = "UNKNOWN"
                return {"health": "UNKNOWN", "error": "deployment_not_found"}
            raise

    @kopf.on.field("kgents.io", "v1", "agents", field="spec.replicas")  # type: ignore[arg-type]
    async def on_replicas_change(
        old: int | None,
        new: int | None,
        meta: dict[str, Any],
        spec: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> None:
        """Handle replica count changes (scaling)."""
        name = meta["name"]
        namespace = meta.get("namespace", "kgents-agents")
        genus = spec.get("genus", "UNKNOWN")

        old_count = old or 1
        new_count = new or 1

        if old_count == new_count:
            return

        logger.info(f"Scaling agent {name}: {old_count} -> {new_count}")

        apps_api = client.AppsV1Api()
        deployment_name = f"{genus.lower()}-gent"

        try:
            apps_api.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"replicas": new_count}},
            )
            logger.info(f"Scaled deployment {deployment_name} to {new_count}")
        except ApiException as e:
            logger.error(f"Failed to scale agent {name}: {e}")


# ============================================================================
# Standalone Functions (for testing without K8s)
# ============================================================================


class MockAgent:
    """In-memory agent for testing without K8s."""

    def __init__(
        self,
        name: str,
        genus: str,
        namespace: str = "kgents-agents",
        replicas: int = 1,
        deploy_mode: DeployMode = DeployMode.PLACEHOLDER,
    ) -> None:
        self.name = name
        self.genus = genus
        self.namespace = namespace
        self.replicas = replicas
        self.deploy_mode = deploy_mode
        self.phase = AgentPhase.PENDING
        self.cognitive_health = "UNKNOWN"
        self.ready_replicas = 0
        self.created_at = datetime.now(timezone.utc)
        self.memory_cr: str | None = None
        self.deployment: str | None = None
        self.service: str | None = None

    def reconcile(self) -> ReconcileResult:
        """Simulate reconciliation."""
        if self.deploy_mode == DeployMode.DRY_RUN:
            return ReconcileResult(
                success=True,
                message="Dry-run mode",
                phase=AgentPhase.PENDING,
            )

        # Simulate deployment creation
        self.deployment = f"{self.genus.lower()}-gent"
        self.service = f"{self.genus.lower()}-gent"
        self.memory_cr = f"{self.name}-memory"
        self.phase = AgentPhase.RUNNING
        self.ready_replicas = self.replicas
        self.cognitive_health = "HEALTHY"

        return ReconcileResult(
            success=True,
            message=f"Reconciled {self.name}",
            phase=AgentPhase.RUNNING,
            created=[
                f"deployment/{self.deployment}",
                f"service/{self.service}",
                f"memory/{self.memory_cr}",
            ],
        )

    def scale(self, replicas: int) -> None:
        """Simulate scaling."""
        self.replicas = replicas
        self.ready_replicas = replicas

    def delete(self) -> None:
        """Simulate deletion."""
        self.phase = AgentPhase.TERMINATING


class MockAgentRegistry:
    """In-memory agent registry for testing without K8s."""

    def __init__(self) -> None:
        self._agents: dict[str, MockAgent] = {}

    def create(
        self,
        name: str,
        genus: str,
        **kwargs: Any,
    ) -> MockAgent:
        """Create a new agent."""
        agent = MockAgent(name, genus, **kwargs)
        result = agent.reconcile()
        if result.success:
            self._agents[name] = agent
            logger.info(f"Created agent: {name} ({genus})")
        return agent

    def get(self, name: str) -> MockAgent | None:
        """Get an agent by name."""
        return self._agents.get(name)

    def list(self) -> list[MockAgent]:
        """List all agents."""
        return list(self._agents.values())

    def delete(self, name: str) -> bool:
        """Delete an agent."""
        if name in self._agents:
            self._agents[name].delete()
            del self._agents[name]
            logger.info(f"Deleted agent: {name}")
            return True
        return False

    def scale(self, name: str, replicas: int) -> bool:
        """Scale an agent."""
        agent = self._agents.get(name)
        if agent:
            agent.scale(replicas)
            logger.info(f"Scaled agent {name} to {replicas}")
            return True
        return False


# Global mock registry for testing
_mock_registry: MockAgentRegistry | None = None


def get_mock_registry() -> MockAgentRegistry:
    """Get or create the global mock agent registry."""
    global _mock_registry
    if _mock_registry is None:
        _mock_registry = MockAgentRegistry()
    return _mock_registry


def reset_mock_registry() -> None:
    """Reset the global mock registry (for testing)."""
    global _mock_registry
    _mock_registry = None
