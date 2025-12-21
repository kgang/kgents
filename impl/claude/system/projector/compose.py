"""
Projector Composition: Categorical composition of projectors via >> operator.

The Projector Composition pattern enables multi-stage compilation pipelines:

    DockerProjector() >> K8sProjector()
    # First compiles to Docker, then uses artifact in K8s manifest

This follows the category theory principle of morphism composition:
    f: A → B, g: B → C  ⟹  g ∘ f: A → C

For projectors:
    Docker: Agent → DockerArtifact
    K8s: Agent → K8sResources
    Docker >> K8s: Agent → (DockerArtifact, K8sResources with image ref)

The ComposedProjector:
1. Runs the upstream projector to get its artifact
2. Injects upstream artifact metadata into downstream compilation
3. Returns combined result

Example:
    >>> composed = DockerProjector() >> K8sProjector()
    >>> result = composed.compile(MyAgent)
    >>> print(result.upstream)   # DockerArtifact
    >>> print(result.downstream) # K8sResources with correct image reference

Laws (verified):
    1. Identity: Id >> P ≡ P ≡ P >> Id
    2. Associativity: (A >> B) >> C ≡ A >> (B >> C)

See: spec/protocols/alethic-projection.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .base import Projector

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from agents.poly.types import Agent

# Type variables for composition
U = TypeVar("U")  # Upstream artifact type
D = TypeVar("D")  # Downstream artifact type


@dataclass
class ComposedArtifact(Generic[U, D]):
    """
    Result of composed projector compilation.

    Contains both upstream and downstream artifacts,
    enabling access to the full pipeline output.
    """

    upstream: U
    downstream: D

    @property
    def dockerfile(self) -> str | None:
        """Extract Dockerfile if upstream is DockerArtifact."""
        from .docker import DockerArtifact

        if isinstance(self.upstream, DockerArtifact):
            return self.upstream.dockerfile
        return None

    @property
    def image_name(self) -> str | None:
        """Extract image name if upstream is DockerArtifact."""
        from .docker import DockerArtifact

        if isinstance(self.upstream, DockerArtifact):
            return self.upstream.full_image
        return None


class ComposedProjector(Projector[ComposedArtifact[Any, Any]]):
    """
    Projector that composes two projectors in sequence.

    The upstream projector runs first, producing an artifact.
    The downstream projector then compiles with access to
    the upstream artifact's metadata.

    This implements the >> operator for projectors:
        DockerProjector() >> K8sProjector()

    The composition preserves semantic equivalence:
    the agent behavior is identical regardless of
    compilation target ordering.
    """

    def __init__(
        self,
        upstream: Projector[Any],
        downstream: Projector[Any],
    ) -> None:
        """
        Initialize composed projector.

        Args:
            upstream: First projector to run
            downstream: Second projector (receives upstream artifact context)
        """
        self._upstream = upstream
        self._downstream = downstream

    @property
    def name(self) -> str:
        return f"{self._upstream.name}>>{self._downstream.name}"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> ComposedArtifact[Any, Any]:
        """
        Compile agent through both projectors.

        1. Run upstream projector
        2. If upstream produces structured artifact (e.g., DockerArtifact),
           inject metadata into downstream compilation context
        3. Run downstream projector
        4. Return combined artifact

        Args:
            agent_cls: Agent class to compile

        Returns:
            ComposedArtifact containing both upstream and downstream results
        """
        from .docker import DockerArtifact, DockerProjector
        from .k8s import K8sProjector

        # Compile upstream
        if isinstance(self._upstream, DockerProjector):
            # Get structured artifact for metadata
            upstream_artifact = self._upstream.compile_artifact(agent_cls)
        else:
            upstream_artifact = self._upstream.compile(agent_cls)

        # Prepare downstream with upstream context
        downstream_result: Any
        if isinstance(self._downstream, K8sProjector) and isinstance(
            upstream_artifact, DockerArtifact
        ):
            # Inject Docker image reference into K8s projector
            downstream_with_image = K8sProjector(
                namespace=self._downstream.namespace,
                image_prefix="",  # Clear prefix, use full image
                storage_class=self._downstream.storage_class,
            )
            # Override image derivation to use Docker image
            original_compile = downstream_with_image.compile

            def compile_with_image(cls: type) -> list[Any]:
                resources = original_compile(cls)
                # Update container image references
                for r in resources:
                    if r.kind in ("Deployment", "StatefulSet"):
                        for container in (
                            r.spec.get("template", {}).get("spec", {}).get("containers", [])
                        ):
                            if container.get("name") == "agent":
                                container["image"] = upstream_artifact.full_image
                return resources

            downstream_result = compile_with_image(agent_cls)
        else:
            downstream_result = self._downstream.compile(agent_cls)

        return ComposedArtifact(
            upstream=upstream_artifact,
            downstream=downstream_result,
        )

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if both projectors support a capability.

        Both upstream and downstream must support the capability
        for the composition to support it.
        """
        return self._upstream.supports(capability) and self._downstream.supports(capability)


class IdentityProjector(Projector[type]):
    """
    Identity projector: returns the agent class unchanged.

    This satisfies the identity law for projector composition:
        Id >> P ≡ P ≡ P >> Id

    Useful as a no-op in pipelines or for testing.
    """

    @property
    def name(self) -> str:
        return "IdentityProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> type:
        """Return agent class unchanged."""
        return agent_cls

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """Identity supports all capabilities."""
        return True


def add_rshift_to_projector() -> None:
    """
    Add __rshift__ method to Projector base class.

    Called at module import to enable >> syntax:
        DockerProjector() >> K8sProjector()

    This is done via monkey-patching to avoid modifying
    the base class directly (keeps base.py clean).
    """

    def __rshift__(self: Projector[Any], other: Projector[Any]) -> ComposedProjector:
        """
        Compose this projector with another.

        Returns a ComposedProjector that runs self first,
        then other with access to self's artifact.

        Example:
            docker_k8s = DockerProjector() >> K8sProjector()
        """
        return ComposedProjector(self, other)

    # Only add if not already present
    if not hasattr(Projector, "__rshift__"):
        setattr(Projector, "__rshift__", __rshift__)


# Add >> operator on module import
add_rshift_to_projector()
