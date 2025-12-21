"""
Tests for DockerProjector.

Verifies:
- Dockerfile generation from agent Halo
- Capability-to-Docker feature mappings
- Projector composition via >>
"""

import pytest

from agents.a.halo import Capability
from agents.poly.types import Agent
from system.projector import (
    ComposedArtifact,
    DockerArtifact,
    DockerProjector,
    K8sProjector,
)


# Test agent fixtures
@Capability.Stateful(schema=dict)
class StatefulTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "stateful-test"

    async def invoke(self, x):
        return x.upper()


@Capability.Observable(metrics=True)
class ObservableTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "observable-test"

    async def invoke(self, x):
        return x.upper()


@Capability.Soulful(persona="kent", mode="strict")
class SoulfulTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "soulful-test"

    async def invoke(self, x):
        return x.upper()


@Capability.Streamable(budget=5.0)
class StreamableTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "streamable-test"

    async def invoke(self, x):
        return x.upper()


@Capability.Stateful(schema=dict)
@Capability.Observable(metrics=True)
@Capability.Soulful(persona="kent")
@Capability.Streamable(budget=3.0)
class FullStackTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "full-stack-test"

    async def invoke(self, x):
        return x.upper()


class PlainTestAgent(Agent[str, str]):
    @property
    def name(self):
        return "plain-test"

    async def invoke(self, x):
        return x.upper()


class TestDockerProjector:
    """Tests for DockerProjector basic functionality."""

    def test_projector_name(self):
        """DockerProjector has correct name."""
        projector = DockerProjector()
        assert projector.name == "DockerProjector"

    def test_projector_default_configuration(self):
        """DockerProjector has sensible defaults."""
        projector = DockerProjector()
        assert projector.base_image == "python:3.11-slim"
        assert projector.image_prefix == "kgents/"
        assert projector.workdir == "/app"
        assert projector.default_port == 8080
        assert projector.metrics_port == 9090

    def test_projector_custom_configuration(self):
        """DockerProjector accepts custom configuration."""
        projector = DockerProjector(
            base_image="python:3.12",
            image_prefix="myorg/",
            workdir="/opt/app",
        )
        assert projector.base_image == "python:3.12"
        assert projector.image_prefix == "myorg/"
        assert projector.workdir == "/opt/app"

    def test_projector_supports_standard_capabilities(self):
        """DockerProjector supports all standard capabilities."""
        from agents.a.halo import (
            ObservableCapability,
            SoulfulCapability,
            StatefulCapability,
            StreamableCapability,
            TurnBasedCapability,
        )

        projector = DockerProjector()
        assert projector.supports(StatefulCapability)
        assert projector.supports(SoulfulCapability)
        assert projector.supports(ObservableCapability)
        assert projector.supports(StreamableCapability)
        assert projector.supports(TurnBasedCapability)


class TestDockerfileGeneration:
    """Tests for Dockerfile content generation."""

    def test_compile_produces_dockerfile_string(self):
        """compile() returns Dockerfile as string."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert isinstance(dockerfile, str)
        assert len(dockerfile) > 0

    def test_dockerfile_has_from_instruction(self):
        """Dockerfile includes FROM base image."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "FROM python:3.11-slim" in dockerfile

    def test_dockerfile_has_workdir(self):
        """Dockerfile sets WORKDIR."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "WORKDIR /app" in dockerfile

    def test_dockerfile_has_copy_instruction(self):
        """Dockerfile copies application code."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "COPY" in dockerfile

    def test_dockerfile_has_entrypoint(self):
        """Dockerfile has CMD/ENTRYPOINT."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "CMD" in dockerfile or "ENTRYPOINT" in dockerfile

    def test_dockerfile_has_expose(self):
        """Dockerfile exposes default port."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "EXPOSE 8080" in dockerfile

    def test_dockerfile_has_healthcheck(self):
        """Dockerfile includes HEALTHCHECK."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "HEALTHCHECK" in dockerfile

    def test_dockerfile_has_labels(self):
        """Dockerfile includes OCI labels."""
        projector = DockerProjector()
        dockerfile = projector.compile(PlainTestAgent)
        assert "LABEL" in dockerfile
        assert "org.opencontainers" in dockerfile


class TestCapabilityMappings:
    """Tests for capability-to-Docker mappings."""

    def test_stateful_produces_volume(self):
        """@Stateful produces VOLUME instruction."""
        projector = DockerProjector()
        dockerfile = projector.compile(StatefulTestAgent)
        assert "VOLUME" in dockerfile
        assert "/var/lib/kgents/state" in dockerfile

    def test_observable_exposes_metrics_port(self):
        """@Observable with metrics=True exposes 9090."""
        projector = DockerProjector()
        dockerfile = projector.compile(ObservableTestAgent)
        assert "EXPOSE 9090" in dockerfile

    def test_soulful_sets_persona_env(self):
        """@Soulful sets KGENT_PERSONA environment variable."""
        projector = DockerProjector()
        dockerfile = projector.compile(SoulfulTestAgent)
        assert 'ENV KGENT_PERSONA="kent"' in dockerfile
        assert 'ENV KGENT_MODE="strict"' in dockerfile

    def test_streamable_uses_multistage(self):
        """@Streamable uses multi-stage build."""
        projector = DockerProjector()
        dockerfile = projector.compile(StreamableTestAgent)
        assert "AS builder" in dockerfile

    def test_full_stack_includes_all_features(self):
        """Full stack agent includes all capability features."""
        projector = DockerProjector()
        dockerfile = projector.compile(FullStackTestAgent)

        # Stateful
        assert "VOLUME" in dockerfile

        # Observable
        assert "EXPOSE 9090" in dockerfile

        # Soulful
        assert "KGENT_PERSONA" in dockerfile

        # Streamable
        assert "AS builder" in dockerfile


class TestDockerArtifact:
    """Tests for DockerArtifact structured output."""

    def test_compile_artifact_returns_structured(self):
        """compile_artifact() returns DockerArtifact."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(PlainTestAgent)
        assert isinstance(artifact, DockerArtifact)

    def test_artifact_has_dockerfile(self):
        """DockerArtifact contains Dockerfile content."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(PlainTestAgent)
        assert isinstance(artifact.dockerfile, str)
        assert len(artifact.dockerfile) > 0

    def test_artifact_has_image_name(self):
        """DockerArtifact has image name with prefix."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(PlainTestAgent)
        assert artifact.image_name == "kgents/plain-test-agent"

    def test_artifact_full_image_includes_tag(self):
        """full_image property includes tag."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(PlainTestAgent)
        assert artifact.full_image == "kgents/plain-test-agent:latest"

    def test_artifact_exposed_ports(self):
        """DockerArtifact tracks exposed ports."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(ObservableTestAgent)
        assert 8080 in artifact.exposed_ports
        assert 9090 in artifact.exposed_ports

    def test_artifact_volumes(self):
        """DockerArtifact tracks volumes."""
        projector = DockerProjector()
        artifact = projector.compile_artifact(StatefulTestAgent)
        assert "/var/lib/kgents/state" in artifact.volumes


class TestProjectorComposition:
    """Tests for projector composition via >> operator."""

    def test_rshift_creates_composed_projector(self):
        """>> operator creates ComposedProjector."""
        from system.projector import ComposedProjector

        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        assert isinstance(composed, ComposedProjector)

    def test_composed_projector_name(self):
        """ComposedProjector has combined name."""
        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        assert composed.name == "DockerProjector>>K8sProjector"

    def test_composed_compile_returns_composed_artifact(self):
        """Composed compile() returns ComposedArtifact."""
        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        result = composed.compile(PlainTestAgent)
        assert isinstance(result, ComposedArtifact)

    def test_composed_artifact_has_upstream(self):
        """ComposedArtifact includes upstream artifact."""
        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        result = composed.compile(PlainTestAgent)
        assert isinstance(result.upstream, DockerArtifact)

    def test_composed_artifact_has_downstream(self):
        """ComposedArtifact includes downstream artifact."""
        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        result = composed.compile(PlainTestAgent)
        assert isinstance(result.downstream, list)
        assert len(result.downstream) > 0

    def test_k8s_manifests_use_docker_image(self):
        """K8s manifests reference Docker image from upstream."""
        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        result = composed.compile(PlainTestAgent)

        # Find the workload resource
        for resource in result.downstream:
            if resource.kind in ("Deployment", "StatefulSet"):
                containers = resource.spec.get("template", {}).get("spec", {}).get("containers", [])
                for container in containers:
                    if container.get("name") == "agent":
                        assert container["image"] == result.upstream.full_image


class TestIdentityProjector:
    """Tests for identity projector composition law."""

    def test_identity_returns_class_unchanged(self):
        """IdentityProjector returns agent class."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        result = identity.compile(PlainTestAgent)
        assert result is PlainTestAgent

    def test_identity_composition_left(self):
        """Id >> P behaves like P."""
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        docker = DockerProjector()
        composed = identity >> docker

        # Should produce DockerArtifact (via compose) with upstream = class
        result = composed.compile(PlainTestAgent)
        assert result.upstream is PlainTestAgent
        assert isinstance(result.downstream, str)  # Dockerfile string

    def test_identity_supports_all_capabilities(self):
        """IdentityProjector supports all capabilities."""
        from agents.a.halo import StatefulCapability
        from system.projector import IdentityProjector

        identity = IdentityProjector()
        assert identity.supports(StatefulCapability)


class TestComposedProjectorSupports:
    """Tests for composed projector capability support."""

    def test_composed_supports_intersection(self):
        """Composed projector supports intersection of capabilities."""
        from agents.a.halo import StatefulCapability

        docker = DockerProjector()
        k8s = K8sProjector()
        composed = docker >> k8s

        # Both support Stateful
        assert composed.supports(StatefulCapability)
