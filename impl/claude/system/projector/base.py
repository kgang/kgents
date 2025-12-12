"""
Projector Protocol: The interface for categorical compilation.

A Projector reads an agent's Halo (declared capabilities) and compiles
the agent to a target-specific artifact.

The key insight: same Nucleus + Halo, different targets.
- LocalProjector → Runnable Python object
- K8sProjector → Kubernetes manifests

This is the Alethic Architecture's answer to "how do we deploy?"
without coupling the agent to infrastructure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from bootstrap.types import Agent

# The target artifact type produced by compilation
Target = TypeVar("Target")


class ProjectorError(Exception):
    """Base error for projector operations."""

    pass


class UnsupportedCapabilityError(ProjectorError):
    """Raised when a projector doesn't support a capability."""

    def __init__(self, capability: type, projector: str) -> None:
        self.capability = capability
        self.projector = projector

        # Build helpful error message with suggestions
        supported_map = {
            "LocalProjector": ["@Stateful", "@Soulful", "@Observable", "@Streamable"],
            "K8sProjector": ["@Stateful", "@Soulful", "@Observable", "@Streamable"],
        }
        supported = supported_map.get(projector, [])
        suggestion = (
            f" Supported capabilities: {', '.join(supported)}." if supported else ""
        )

        super().__init__(
            f"Projector '{projector}' does not support capability "
            f"'{capability.__name__}'.{suggestion}"
        )


class CompilationError(ProjectorError):
    """Raised when compilation fails."""

    def __init__(self, agent_cls: type, reason: str) -> None:
        self.agent_cls = agent_cls
        self.reason = reason
        super().__init__(f"Failed to compile '{agent_cls.__name__}': {reason}")


class InvalidNameError(ProjectorError):
    """Raised when an agent name is invalid for the target environment."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason
        super().__init__(f"Invalid name '{name}': {reason}")


class Projector(ABC, Generic[Target]):
    """
    Abstract base for categorical compilers.

    A Projector reads an agent's Halo (capability declarations) and
    produces target-specific artifacts.

    The Projector Protocol:
    - compile(agent_cls) → Target: Transform agent class to target
    - supports(capability) → bool: Check capability support

    Different projectors:
    - LocalProjector: Produces runnable Python agents
    - K8sProjector: Produces Kubernetes manifest lists

    The Guarantee:
    An agent compiled by different projectors behaves identically
    (same semantics), even though the implementation differs.

    Example:
        >>> @Capability.Stateful(schema=MyState)
        ... @Capability.Streamable(budget=5.0)
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> local = LocalProjector().compile(MyAgent)
        >>> # local is FluxAgent wrapping Symbiont wrapping MyAgent
        >>>
        >>> k8s = K8sProjector().compile(MyAgent)
        >>> # k8s is [StatefulSet, PVC, Deployment, HPA, ...]
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable projector name."""
        ...

    @abstractmethod
    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> Target:
        """
        Compile agent class to target artifact.

        Reads the agent's Halo (via @Capability decorators) and produces
        target-specific compilation.

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Target artifact (depends on projector type)

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
            CompilationError: If compilation fails
        """
        ...

    @abstractmethod
    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if this projector supports a capability type.

        Args:
            capability: The capability type to check

        Returns:
            True if capability is supported
        """
        ...
