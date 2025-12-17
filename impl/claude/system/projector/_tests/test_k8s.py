"""
Tests for K8sProjector.

The K8sProjector compiles agent Halo (declarative capabilities)
into Kubernetes resource manifests.

Test Categories:
1. Plain agents (no capabilities) - minimal manifest set
2. Single capabilities - correct K8s resources generated
3. Multiple capabilities - all resources generated correctly
4. Manifest validity - proper K8s structure
5. Error handling - unsupported capabilities
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from agents.a.halo import (
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
)
from agents.poly.types import Agent
from system.projector import K8sProjector, K8sResource, manifests_to_yaml
from system.projector.base import InvalidNameError, UnsupportedCapabilityError

# ===========================================================================
# Test Fixtures: Agent Classes
# ===========================================================================


class PlainAgent(Agent[str, str]):
    """A plain agent with no capabilities."""

    @property
    def name(self) -> str:
        return "plain"

    async def invoke(self, input: str) -> str:
        return f"plain:{input}"


class EchoAgent(Agent[str, str]):
    """Simple echo agent for testing."""

    @property
    def name(self) -> str:
        return "echo"

    async def invoke(self, input: str) -> str:
        return f"echo:{input}"


@dataclass
class MyState:
    """Example state schema."""

    count: int = 0


@Capability.Stateful(schema=dict)
class StatefulDictAgent(Agent[str, str]):
    """Agent with dict state schema."""

    @property
    def name(self) -> str:
        return "stateful-dict"

    async def invoke(self, input: str) -> str:
        return f"stateful:{input}"


@Capability.Stateful(schema=MyState, backend="persistent")
class PersistentAgent(Agent[str, str]):
    """Agent with persistent storage."""

    @property
    def name(self) -> str:
        return "persistent"

    async def invoke(self, input: str) -> str:
        return input


@Capability.Soulful(persona="Kent")
class SoulfulAgent(Agent[str, str]):
    """Agent with K-gent personality."""

    @property
    def name(self) -> str:
        return "soulful"

    async def invoke(self, input: str) -> str:
        return f"soulful:{input}"


@Capability.Soulful(persona="TestBot", mode="strict")
class StrictSoulfulAgent(Agent[str, str]):
    """Agent with strict persona mode."""

    @property
    def name(self) -> str:
        return "strict-soulful"

    async def invoke(self, input: str) -> str:
        return f"strict:{input}"


@Capability.Observable(mirror=True, metrics=True)
class ObservableAgent(Agent[str, str]):
    """Agent with observability."""

    @property
    def name(self) -> str:
        return "observable"

    async def invoke(self, input: str) -> str:
        return f"observable:{input}"


@Capability.Observable(mirror=True, metrics=False)
class MirrorOnlyAgent(Agent[str, str]):
    """Agent with mirror but no metrics."""

    @property
    def name(self) -> str:
        return "mirror-only"

    async def invoke(self, input: str) -> str:
        return input


@Capability.Streamable(budget=5.0)
class StreamableAgent(Agent[str, str]):
    """Agent that can be lifted to Flux."""

    @property
    def name(self) -> str:
        return "streamable"

    async def invoke(self, input: str) -> str:
        return f"streamable:{input}"


@Capability.Streamable(budget=10.0, feedback=0.5)
class HighBudgetAgent(Agent[str, str]):
    """Agent with high entropy budget."""

    @property
    def name(self) -> str:
        return "high-budget"

    async def invoke(self, input: str) -> str:
        return input


@Capability.Stateful(schema=dict)
@Capability.Streamable(budget=5.0)
class StatefulStreamableAgent(Agent[str, str]):
    """Agent with state and streaming."""

    @property
    def name(self) -> str:
        return "stateful-streamable"

    async def invoke(self, input: str) -> str:
        return f"stateful-streamable:{input}"


@Capability.Stateful(schema=dict)
@Capability.Soulful(persona="Kent")
@Capability.Observable(mirror=True, metrics=True)
@Capability.Streamable(budget=10.0)
class FullStackAgent(Agent[str, str]):
    """Agent with all four capabilities."""

    @property
    def name(self) -> str:
        return "full-stack"

    async def invoke(self, input: str) -> str:
        return f"full-stack:{input}"


class CamelCaseAgent(Agent[str, str]):
    """Agent with CamelCase name for kebab-case conversion test."""

    @property
    def name(self) -> str:
        return "camel"

    async def invoke(self, input: str) -> str:
        return input


@dataclass(frozen=True)
class UnsupportedCapability(CapabilityBase):
    """A capability that K8sProjector doesn't support."""

    custom_field: str = "test"


@UnsupportedCapability(custom_field="bad")
class UnsupportedCapabilityAgent(Agent[str, str]):
    """Agent with unsupported capability."""

    @property
    def name(self) -> str:
        return "unsupported"

    async def invoke(self, input: str) -> str:
        return input


# ===========================================================================
# Test Class: K8sProjector Basic Functionality
# ===========================================================================


class TestK8sProjector:
    """Tests for K8sProjector functionality."""

    # -----------------------------------------------------------------------
    # Basic Properties
    # -----------------------------------------------------------------------

    def test_projector_name(self) -> None:
        """Projector has correct name."""
        projector = K8sProjector()
        assert projector.name == "K8sProjector"

    def test_projector_default_namespace(self) -> None:
        """Default namespace is kgents-agents."""
        projector = K8sProjector()
        assert projector.namespace == "kgents-agents"

    def test_projector_custom_namespace(self) -> None:
        """Projector accepts custom namespace."""
        projector = K8sProjector(namespace="production")
        assert projector.namespace == "production"

    def test_projector_custom_image_prefix(self) -> None:
        """Projector accepts custom image prefix."""
        projector = K8sProjector(image_prefix="myregistry/")
        assert projector.image_prefix == "myregistry/"

    def test_projector_supports_standard_capabilities(self) -> None:
        """K8sProjector supports all four standard capabilities."""
        projector = K8sProjector()

        assert projector.supports(StatefulCapability)
        assert projector.supports(SoulfulCapability)
        assert projector.supports(ObservableCapability)
        assert projector.supports(StreamableCapability)

    def test_projector_does_not_support_custom_capabilities(self) -> None:
        """K8sProjector rejects unknown capabilities."""
        projector = K8sProjector()
        assert not projector.supports(UnsupportedCapability)

    # -----------------------------------------------------------------------
    # Plain Agent Compilation
    # -----------------------------------------------------------------------

    def test_compile_plain_agent_returns_resources(self) -> None:
        """Agent without capabilities compiles to base resources."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        # Should have: Deployment, Service, ConfigMap
        kinds = {r.kind for r in resources}
        assert "Deployment" in kinds
        assert "Service" in kinds
        assert "ConfigMap" in kinds
        assert "StatefulSet" not in kinds  # No @Stateful

    def test_compile_plain_agent_correct_count(self) -> None:
        """Plain agent produces exactly 3 resources."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        assert len(resources) == 3  # Deployment, Service, ConfigMap

    # -----------------------------------------------------------------------
    # Name Derivation
    # -----------------------------------------------------------------------

    def test_name_derivation_kebab_case(self) -> None:
        """CamelCase class name converted to kebab-case."""
        projector = K8sProjector()
        resources = projector.compile(CamelCaseAgent)

        # Check deployment name
        deployment = next(r for r in resources if r.kind == "Deployment")
        assert deployment.metadata["name"] == "camel-case-agent"

    def test_name_in_all_resources(self) -> None:
        """Agent name appears in all resource names."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        for r in resources:
            assert "plain-agent" in r.metadata["name"]

    # -----------------------------------------------------------------------
    # Stateful Capability
    # -----------------------------------------------------------------------

    def test_compile_stateful_produces_statefulset(self) -> None:
        """@Stateful produces StatefulSet instead of Deployment."""
        projector = K8sProjector()
        resources = projector.compile(StatefulDictAgent)

        kinds = {r.kind for r in resources}
        assert "StatefulSet" in kinds
        assert "Deployment" not in kinds

    def test_compile_stateful_produces_pvc(self) -> None:
        """@Stateful produces PersistentVolumeClaim."""
        projector = K8sProjector()
        resources = projector.compile(StatefulDictAgent)

        kinds = {r.kind for r in resources}
        assert "PersistentVolumeClaim" in kinds

    def test_stateful_pvc_default_size(self) -> None:
        """PVC has default 1Gi storage."""
        projector = K8sProjector()
        resources = projector.compile(StatefulDictAgent)

        pvc = next(r for r in resources if r.kind == "PersistentVolumeClaim")
        assert pvc.spec["resources"]["requests"]["storage"] == "1Gi"

    def test_persistent_backend_larger_storage(self) -> None:
        """@Stateful(backend='persistent') uses larger PVC."""
        projector = K8sProjector()
        resources = projector.compile(PersistentAgent)

        pvc = next(r for r in resources if r.kind == "PersistentVolumeClaim")
        assert pvc.spec["resources"]["requests"]["storage"] == "10Gi"

    def test_statefulset_has_volume_mount(self) -> None:
        """StatefulSet container has volume mount."""
        projector = K8sProjector()
        resources = projector.compile(StatefulDictAgent)

        sts = next(r for r in resources if r.kind == "StatefulSet")
        container = sts.spec["template"]["spec"]["containers"][0]

        assert "volumeMounts" in container
        assert container["volumeMounts"][0]["mountPath"] == "/var/lib/kgents/state"

    def test_statefulset_references_pvc(self) -> None:
        """StatefulSet references PVC."""
        projector = K8sProjector()
        resources = projector.compile(StatefulDictAgent)

        sts = next(r for r in resources if r.kind == "StatefulSet")
        volumes = sts.spec["template"]["spec"]["volumes"]

        pvc_ref = volumes[0]["persistentVolumeClaim"]["claimName"]
        assert "state" in pvc_ref

    # -----------------------------------------------------------------------
    # Soulful Capability
    # -----------------------------------------------------------------------

    def test_compile_soulful_adds_sidecar(self) -> None:
        """@Soulful adds K-gent sidecar container."""
        projector = K8sProjector()
        resources = projector.compile(SoulfulAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]

        assert len(containers) == 2
        sidecar = next(c for c in containers if c["name"] == "kgent-sidecar")
        assert sidecar is not None

    def test_soulful_sidecar_has_persona_env(self) -> None:
        """K-gent sidecar has persona environment variable."""
        projector = K8sProjector()
        resources = projector.compile(SoulfulAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]
        sidecar = next(c for c in containers if c["name"] == "kgent-sidecar")

        env_names = {e["name"] for e in sidecar["env"]}
        assert "KGENT_PERSONA" in env_names

        persona_env = next(e for e in sidecar["env"] if e["name"] == "KGENT_PERSONA")
        assert persona_env["value"] == "Kent"

    def test_strict_soulful_mode_in_env(self) -> None:
        """@Soulful(mode='strict') reflected in sidecar env."""
        projector = K8sProjector()
        resources = projector.compile(StrictSoulfulAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]
        sidecar = next(c for c in containers if c["name"] == "kgent-sidecar")

        mode_env = next(e for e in sidecar["env"] if e["name"] == "KGENT_MODE")
        assert mode_env["value"] == "strict"

    def test_soulful_sidecar_has_port(self) -> None:
        """K-gent sidecar exposes port 8081."""
        projector = K8sProjector()
        resources = projector.compile(SoulfulAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]
        sidecar = next(c for c in containers if c["name"] == "kgent-sidecar")

        ports = {p["containerPort"] for p in sidecar["ports"]}
        assert 8081 in ports

    # -----------------------------------------------------------------------
    # Observable Capability
    # -----------------------------------------------------------------------

    def test_compile_observable_with_metrics_produces_service_monitor(self) -> None:
        """@Observable(metrics=True) produces ServiceMonitor."""
        projector = K8sProjector()
        resources = projector.compile(ObservableAgent)

        kinds = {r.kind for r in resources}
        assert "ServiceMonitor" in kinds

    def test_compile_observable_without_metrics_no_service_monitor(self) -> None:
        """@Observable(metrics=False) does not produce ServiceMonitor."""
        projector = K8sProjector()
        resources = projector.compile(MirrorOnlyAgent)

        kinds = {r.kind for r in resources}
        assert "ServiceMonitor" not in kinds

    def test_observable_service_has_metrics_port(self) -> None:
        """@Observable Service includes metrics port."""
        projector = K8sProjector()
        resources = projector.compile(ObservableAgent)

        service = next(r for r in resources if r.kind == "Service")
        port_names = {p["name"] for p in service.spec["ports"]}
        assert "metrics" in port_names

    def test_service_monitor_targets_service(self) -> None:
        """ServiceMonitor selector matches Service."""
        projector = K8sProjector()
        resources = projector.compile(ObservableAgent)

        service = next(r for r in resources if r.kind == "Service")
        sm = next(r for r in resources if r.kind == "ServiceMonitor")

        service_labels = service.metadata["labels"]
        sm_selector = sm.spec["selector"]["matchLabels"]

        assert "app.kubernetes.io/name" in sm_selector
        assert (
            sm_selector["app.kubernetes.io/name"]
            == service_labels["app.kubernetes.io/name"]
        )

    # -----------------------------------------------------------------------
    # Streamable Capability
    # -----------------------------------------------------------------------

    def test_compile_streamable_produces_hpa(self) -> None:
        """@Streamable produces HorizontalPodAutoscaler."""
        projector = K8sProjector()
        resources = projector.compile(StreamableAgent)

        kinds = {r.kind for r in resources}
        assert "HorizontalPodAutoscaler" in kinds

    def test_hpa_max_replicas_from_budget(self) -> None:
        """HPA maxReplicas derived from entropy budget."""
        projector = K8sProjector()
        resources = projector.compile(StreamableAgent)

        hpa = next(r for r in resources if r.kind == "HorizontalPodAutoscaler")
        # budget=5.0 -> maxReplicas = min(5*2, 10) = 10
        assert hpa.spec["maxReplicas"] == 10

    def test_high_budget_hpa_capped(self) -> None:
        """HPA maxReplicas capped at 10."""
        projector = K8sProjector()
        resources = projector.compile(HighBudgetAgent)

        hpa = next(r for r in resources if r.kind == "HorizontalPodAutoscaler")
        # budget=10.0 -> min(10*2, 10) = 10 (capped)
        assert hpa.spec["maxReplicas"] == 10

    def test_hpa_targets_correct_workload(self) -> None:
        """HPA targets Deployment for stateless agent."""
        projector = K8sProjector()
        resources = projector.compile(StreamableAgent)

        hpa = next(r for r in resources if r.kind == "HorizontalPodAutoscaler")
        assert hpa.spec["scaleTargetRef"]["kind"] == "Deployment"

    def test_stateful_streamable_hpa_targets_statefulset(self) -> None:
        """HPA targets StatefulSet for stateful agent."""
        projector = K8sProjector()
        resources = projector.compile(StatefulStreamableAgent)

        hpa = next(r for r in resources if r.kind == "HorizontalPodAutoscaler")
        assert hpa.spec["scaleTargetRef"]["kind"] == "StatefulSet"

    # -----------------------------------------------------------------------
    # Full Stack Compilation
    # -----------------------------------------------------------------------

    def test_full_stack_produces_all_resources(self) -> None:
        """All four capabilities produce all resource types."""
        projector = K8sProjector()
        resources = projector.compile(FullStackAgent)

        kinds = {r.kind for r in resources}
        assert "StatefulSet" in kinds  # @Stateful
        assert "PersistentVolumeClaim" in kinds  # @Stateful
        assert "ServiceMonitor" in kinds  # @Observable
        assert "HorizontalPodAutoscaler" in kinds  # @Streamable
        assert "Service" in kinds  # always
        assert "ConfigMap" in kinds  # always

    def test_full_stack_statefulset_has_sidecar(self) -> None:
        """Full stack StatefulSet includes K-gent sidecar."""
        projector = K8sProjector()
        resources = projector.compile(FullStackAgent)

        sts = next(r for r in resources if r.kind == "StatefulSet")
        containers = sts.spec["template"]["spec"]["containers"]

        assert len(containers) == 2
        container_names = {c["name"] for c in containers}
        assert "agent" in container_names
        assert "kgent-sidecar" in container_names

    def test_full_stack_resource_count(self) -> None:
        """Full stack produces correct number of resources."""
        projector = K8sProjector()
        resources = projector.compile(FullStackAgent)

        # StatefulSet, PVC, Service, ServiceMonitor, HPA, ConfigMap = 6
        assert len(resources) == 6

    # -----------------------------------------------------------------------
    # Error Handling
    # -----------------------------------------------------------------------

    def test_unsupported_capability_raises_error(self) -> None:
        """Agent with unsupported capability raises UnsupportedCapabilityError."""
        projector = K8sProjector()

        with pytest.raises(UnsupportedCapabilityError) as exc_info:
            projector.compile(UnsupportedCapabilityAgent)

        assert exc_info.value.projector == "K8sProjector"
        assert exc_info.value.capability == UnsupportedCapability


# ===========================================================================
# Test Class: K8sResource
# ===========================================================================


class TestK8sResource:
    """Tests for K8sResource dataclass."""

    def test_to_dict_basic(self) -> None:
        """K8sResource converts to dict correctly."""
        resource = K8sResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={"name": "test", "namespace": "default"},
            data={"key": "value"},
        )

        d = resource.to_dict()
        assert d["apiVersion"] == "v1"
        assert d["kind"] == "ConfigMap"
        assert d["metadata"]["name"] == "test"
        assert d["data"]["key"] == "value"

    def test_to_dict_excludes_empty_spec(self) -> None:
        """Empty spec not included in dict output."""
        resource = K8sResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={"name": "test"},
            data={"key": "value"},
        )

        d = resource.to_dict()
        assert "spec" not in d

    def test_to_dict_includes_spec_when_present(self) -> None:
        """Non-empty spec included in dict output."""
        resource = K8sResource(
            api_version="apps/v1",
            kind="Deployment",
            metadata={"name": "test"},
            spec={"replicas": 3},
        )

        d = resource.to_dict()
        assert "spec" in d
        assert d["spec"]["replicas"] == 3

    def test_to_yaml_produces_string(self) -> None:
        """K8sResource converts to YAML string."""
        resource = K8sResource(
            api_version="v1",
            kind="ConfigMap",
            metadata={"name": "test"},
            data={"key": "value"},
        )

        yaml_str = resource.to_yaml()
        assert "apiVersion: v1" in yaml_str or '"apiVersion": "v1"' in yaml_str
        assert "ConfigMap" in yaml_str


# ===========================================================================
# Test Class: Manifest Utilities
# ===========================================================================


class TestManifestUtilities:
    """Tests for manifest utility functions."""

    def test_manifests_to_yaml_single(self) -> None:
        """Single resource to YAML."""
        resources = [
            K8sResource(
                api_version="v1",
                kind="ConfigMap",
                metadata={"name": "test"},
                data={"key": "value"},
            )
        ]

        yaml_str = manifests_to_yaml(resources)
        assert "ConfigMap" in yaml_str

    def test_manifests_to_yaml_multiple(self) -> None:
        """Multiple resources separated by ---."""
        resources = [
            K8sResource(
                api_version="v1",
                kind="ConfigMap",
                metadata={"name": "cm1"},
                data={},
            ),
            K8sResource(
                api_version="v1",
                kind="Service",
                metadata={"name": "svc1"},
                spec={"ports": []},
            ),
        ]

        yaml_str = manifests_to_yaml(resources)
        assert "ConfigMap" in yaml_str
        assert "Service" in yaml_str
        # Default separator
        assert "---" in yaml_str

    def test_manifests_to_yaml_custom_separator(self) -> None:
        """Custom separator between manifests."""
        resources = [
            K8sResource(
                api_version="v1",
                kind="ConfigMap",
                metadata={"name": "cm1"},
            ),
            K8sResource(
                api_version="v1",
                kind="Service",
                metadata={"name": "svc1"},
            ),
        ]

        yaml_str = manifests_to_yaml(resources, separator="\n# ---\n")
        assert "# ---" in yaml_str


# ===========================================================================
# Test Class: Labels and Annotations
# ===========================================================================


class TestLabelsAndAnnotations:
    """Tests for K8s labels and annotations."""

    def test_standard_labels_present(self) -> None:
        """All resources have standard app.kubernetes.io labels."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        for r in resources:
            labels = r.metadata["labels"]
            assert "app.kubernetes.io/name" in labels
            assert "app.kubernetes.io/component" in labels
            assert "app.kubernetes.io/part-of" in labels
            assert "app.kubernetes.io/managed-by" in labels

    def test_kgents_label_present(self) -> None:
        """All resources have kgents.io/agent label."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        for r in resources:
            labels = r.metadata["labels"]
            assert "kgents.io/agent" in labels

    def test_part_of_is_kgents(self) -> None:
        """app.kubernetes.io/part-of is 'kgents'."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        for r in resources:
            assert r.metadata["labels"]["app.kubernetes.io/part-of"] == "kgents"

    def test_managed_by_is_projector(self) -> None:
        """app.kubernetes.io/managed-by is 'k8s-projector'."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        for r in resources:
            assert (
                r.metadata["labels"]["app.kubernetes.io/managed-by"] == "k8s-projector"
            )


# ===========================================================================
# Test Class: ConfigMap Configuration
# ===========================================================================


class TestConfigMap:
    """Tests for ConfigMap generation."""

    def test_configmap_contains_agent_name(self) -> None:
        """ConfigMap has AGENT_NAME data."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        cm = next(r for r in resources if r.kind == "ConfigMap")
        assert "AGENT_NAME" in cm.data

    def test_configmap_contains_capabilities(self) -> None:
        """ConfigMap has AGENT_CAPABILITIES data."""
        projector = K8sProjector()
        resources = projector.compile(FullStackAgent)

        cm = next(r for r in resources if r.kind == "ConfigMap")
        assert "AGENT_CAPABILITIES" in cm.data
        caps = cm.data["AGENT_CAPABILITIES"]
        assert "StatefulCapability" in caps
        assert "SoulfulCapability" in caps

    def test_configmap_contains_namespace(self) -> None:
        """ConfigMap has AGENT_NAMESPACE data."""
        projector = K8sProjector(namespace="production")
        resources = projector.compile(PlainAgent)

        cm = next(r for r in resources if r.kind == "ConfigMap")
        assert cm.data["AGENT_NAMESPACE"] == "production"


# ===========================================================================
# Test Class: Container Configuration
# ===========================================================================


class TestContainerConfiguration:
    """Tests for container spec configuration."""

    def test_main_container_has_probes(self) -> None:
        """Main container has liveness and readiness probes."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        container = deployment.spec["template"]["spec"]["containers"][0]

        assert "livenessProbe" in container
        assert "readinessProbe" in container

    def test_main_container_has_resources(self) -> None:
        """Main container has resource requests and limits."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        container = deployment.spec["template"]["spec"]["containers"][0]

        assert "resources" in container
        assert "requests" in container["resources"]
        assert "limits" in container["resources"]

    def test_main_container_has_config_env(self) -> None:
        """Main container loads ConfigMap as environment."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        container = deployment.spec["template"]["spec"]["containers"][0]

        assert "envFrom" in container
        config_ref = container["envFrom"][0]["configMapRef"]["name"]
        assert "config" in config_ref

    def test_custom_resource_limits(self) -> None:
        """Custom resource limits applied."""
        projector = K8sProjector(
            default_cpu_limit="1000m",
            default_memory_limit="1Gi",
        )
        resources = projector.compile(PlainAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        container = deployment.spec["template"]["spec"]["containers"][0]

        assert container["resources"]["limits"]["cpu"] == "1000m"
        assert container["resources"]["limits"]["memory"] == "1Gi"


# ===========================================================================
# Test Fixtures: Edge Case Agent Classes
# ===========================================================================


# Very long agent name (tests truncation)
class ThisIsAnExtremelyLongAgentNameThatExceedsSixtyThreeCharactersWhichIsTheMaximumAllowedByKubernetes(
    Agent[str, str]
):
    """Agent with very long name."""

    @property
    def name(self) -> str:
        return "long"

    async def invoke(self, input: str) -> str:
        return input


# Agent with underscores (common pattern that needs sanitization)
class Agent_With_Special123_Chars(Agent[str, str]):
    """Agent with underscores in name."""

    @property
    def name(self) -> str:
        return "special"

    async def invoke(self, input: str) -> str:
        return input


# Agent with underscore prefix (common pattern)
class _PrivateAgent(Agent[str, str]):
    """Agent with underscore prefix."""

    @property
    def name(self) -> str:
        return "private"

    async def invoke(self, input: str) -> str:
        return input


# Agent with leading/trailing special chars
class __DoubleUnderscoreAgent__(Agent[str, str]):
    """Agent with double underscores."""

    @property
    def name(self) -> str:
        return "double"

    async def invoke(self, input: str) -> str:
        return input


# Agent with only numbers after sanitization (valid)
class Agent123(Agent[str, str]):
    """Agent with numbers."""

    @property
    def name(self) -> str:
        return "numeric"

    async def invoke(self, input: str) -> str:
        return input


# ===========================================================================
# Test Class: RFC 1123 Name Validation Edge Cases
# ===========================================================================


class TestRFC1123NameValidation:
    """Tests for RFC 1123 name validation edge cases."""

    def test_long_name_truncated(self) -> None:
        """Very long agent names are truncated to 63 chars."""
        projector = K8sProjector()
        resources = projector.compile(
            ThisIsAnExtremelyLongAgentNameThatExceedsSixtyThreeCharactersWhichIsTheMaximumAllowedByKubernetes
        )

        deployment = next(r for r in resources if r.kind == "Deployment")
        name = deployment.metadata["name"]
        assert len(name) <= 63
        # Should not end with hyphen
        assert not name.endswith("-")

    def test_special_chars_sanitized(self) -> None:
        """Underscores are replaced with hyphens."""
        projector = K8sProjector()
        resources = projector.compile(Agent_With_Special123_Chars)

        deployment = next(r for r in resources if r.kind == "Deployment")
        name = deployment.metadata["name"]

        # Should not contain underscore
        assert "_" not in name
        # Should be valid RFC 1123 (lowercase alphanumeric with hyphens)
        assert name.islower() or name.replace("-", "").isalnum()

    def test_leading_underscore_stripped(self) -> None:
        """Leading underscores are stripped (they become leading hyphens then stripped)."""
        projector = K8sProjector()
        resources = projector.compile(_PrivateAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        name = deployment.metadata["name"]

        # Should not start with hyphen
        assert not name.startswith("-")

    def test_double_underscore_handled(self) -> None:
        """Double underscores are collapsed to single hyphen."""
        projector = K8sProjector()
        resources = projector.compile(__DoubleUnderscoreAgent__)

        deployment = next(r for r in resources if r.kind == "Deployment")
        name = deployment.metadata["name"]

        # Should not have double hyphens
        assert "--" not in name
        # Should not start or end with hyphen
        assert not name.startswith("-")
        assert not name.endswith("-")

    def test_numeric_suffix_preserved(self) -> None:
        """Numeric suffixes are preserved."""
        projector = K8sProjector()
        resources = projector.compile(Agent123)

        deployment = next(r for r in resources if r.kind == "Deployment")
        name = deployment.metadata["name"]

        assert "123" in name

    def test_all_resources_have_valid_names(self) -> None:
        """All generated resources have RFC 1123 valid names."""
        import re

        rfc1123 = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")

        projector = K8sProjector()
        resources = projector.compile(FullStackAgent)

        for r in resources:
            name = r.metadata["name"]
            # Names may have suffixes like "-config" or "-state"
            # but base should still be valid
            assert len(name) <= 63, f"Name too long: {name}"
            # For compound names, check they don't have invalid chars
            assert re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name), (
                f"Invalid name: {name}"
            )

    def test_namespace_rfc1123_validation(self) -> None:
        """Namespace is validated for RFC 1123 compliance."""
        # Valid namespace
        projector = K8sProjector(namespace="my-namespace-123")
        resources = projector.compile(PlainAgent)
        assert all(r.metadata["namespace"] == "my-namespace-123" for r in resources)

    def test_labels_dont_exceed_limits(self) -> None:
        """Label values don't exceed K8s limits (63 chars)."""
        projector = K8sProjector()
        # Use the long-named agent
        resources = projector.compile(
            ThisIsAnExtremelyLongAgentNameThatExceedsSixtyThreeCharactersWhichIsTheMaximumAllowedByKubernetes
        )

        for r in resources:
            for key, value in r.metadata["labels"].items():
                assert len(value) <= 63, f"Label value too long: {key}={value}"


# ===========================================================================
# Test Class: Empty Halo Edge Case
# ===========================================================================


class TestEmptyHalo:
    """Tests for agents with no capabilities (empty Halo)."""

    def test_empty_halo_produces_minimal_resources(self) -> None:
        """Agent with no capabilities produces minimal resource set."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        # Should have exactly: Deployment, Service, ConfigMap
        assert len(resources) == 3
        kinds = {r.kind for r in resources}
        assert kinds == {"Deployment", "Service", "ConfigMap"}

    def test_empty_halo_no_sidecar(self) -> None:
        """Agent without @Soulful has no K-gent sidecar."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]

        assert len(containers) == 1
        assert containers[0]["name"] == "agent"

    def test_empty_halo_configmap_shows_no_capabilities(self) -> None:
        """ConfigMap for plain agent shows empty capabilities."""
        projector = K8sProjector()
        resources = projector.compile(PlainAgent)

        cm = next(r for r in resources if r.kind == "ConfigMap")
        assert cm.data["AGENT_CAPABILITIES"] == ""
