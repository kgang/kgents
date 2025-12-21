"""
DockerProjector: Compiles agent Halo to Dockerfile.

The DockerProjector reads an agent's declarative capabilities (Halo)
and produces a Dockerfile for containerized deployment.

Capability Mapping:
| Capability  | Docker Feature                                    |
|-------------|---------------------------------------------------|
| @Stateful   | VOLUME mount at /var/lib/kgents/state             |
| @Soulful    | ENV KGENT_PERSONA=<persona>                       |
| @Observable | EXPOSE 9090/metrics                               |
| @Streamable | Multi-stage build, optimized layers              |
| @TurnBased  | VOLUME for weave file storage                     |

The Alethic Isomorphism:
    Same Halo + LocalProjector  → Runnable Python object
    Same Halo + K8sProjector    → K8s Manifests
    Same Halo + CLIProjector    → Executable shell script
    Same Halo + DockerProjector → Dockerfile
    All produce semantically equivalent agents.

Example:
    >>> @Capability.Stateful(schema=MyState)
    ... @Capability.Streamable(budget=5.0)
    ... class MyAgent(Agent[str, str]):
    ...     @property
    ...     def name(self): return "my-agent"
    ...     async def invoke(self, x): return x.upper()
    >>>
    >>> dockerfile = DockerProjector().compile(MyAgent)
    >>> print(dockerfile)  # Dockerfile content
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .base import Projector, UnsupportedCapabilityError

if TYPE_CHECKING:
    from agents.a.halo import CapabilityBase
    from agents.poly.types import Agent


@dataclass
class DockerArtifact:
    """
    Result of DockerProjector compilation.

    Contains both the Dockerfile content and metadata for
    downstream projectors (e.g., K8sProjector needs image name).
    """

    dockerfile: str
    image_name: str
    image_tag: str = "latest"
    exposed_ports: list[int] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)

    @property
    def full_image(self) -> str:
        """Full image reference: name:tag."""
        return f"{self.image_name}:{self.image_tag}"


@dataclass
class DockerProjector(Projector[str]):
    """
    Compiles agent Halo into Dockerfile.

    The DockerProjector reads capability decorators and produces
    a Dockerfile that realizes the same semantics in a container.

    Configuration:
        base_image: Python base image (default: python:3.11-slim)
        image_prefix: Image name prefix (default: kgents/)
        workdir: Container working directory (default: /app)
        state_dir: Directory for state persistence (default: /var/lib/kgents/state)

    Example:
        >>> @Capability.Stateful(schema=MyState)
        ... @Capability.Soulful(persona="kent")
        ... class MyAgent(Agent[str, str]): ...
        >>>
        >>> dockerfile = DockerProjector().compile(MyAgent)
        >>> print(dockerfile)
    """

    base_image: str = "python:3.11-slim"
    image_prefix: str = "kgents/"
    workdir: str = "/app"
    state_dir: str = "/var/lib/kgents/state"
    default_port: int = 8080
    metrics_port: int = 9090

    @property
    def name(self) -> str:
        return "DockerProjector"

    def compile(self, agent_cls: type["Agent[Any, Any]"]) -> str:
        """
        Compile agent class to Dockerfile.

        Reads the agent's Halo and produces a Dockerfile that:
        - Installs dependencies
        - Copies agent code
        - Exposes appropriate ports
        - Configures volumes for state
        - Sets up persona if @Soulful

        Args:
            agent_cls: The decorated agent class to compile

        Returns:
            Dockerfile content as string

        Raises:
            UnsupportedCapabilityError: If agent has unsupported capability
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
            "TurnBasedCapability",
        }

        for cap in halo:
            if type(cap).__name__ not in supported_type_names:
                raise UnsupportedCapabilityError(type(cap), self.name)

        # Extract capability details
        stateful_cap = _get_cap("StatefulCapability")
        soulful_cap = _get_cap("SoulfulCapability")
        observable_cap = _get_cap("ObservableCapability")
        streamable_cap = _get_cap("StreamableCapability")
        turnbased_cap = _get_cap("TurnBasedCapability")

        # Derive agent name
        agent_name = self._derive_image_name(agent_cls)
        module_name = agent_cls.__module__
        class_name = agent_cls.__name__

        # Build Dockerfile sections
        sections = []

        # Base image and metadata
        sections.append(self._generate_header(agent_name, class_name))

        # Dependencies (multi-stage if streamable for optimization)
        if streamable_cap is not None:
            sections.append(self._generate_multistage_deps())
        else:
            sections.append(self._generate_simple_deps())

        # Copy application code
        sections.append(self._generate_copy_app())

        # Environment variables
        env_vars = self._build_env_vars(
            agent_name=agent_name,
            module_name=module_name,
            class_name=class_name,
            soulful_cap=soulful_cap,
        )
        if env_vars:
            sections.append(self._generate_env(env_vars))

        # Expose ports
        ports = [self.default_port]
        if observable_cap is not None and getattr(observable_cap, "metrics", False):
            ports.append(self.metrics_port)
        sections.append(self._generate_expose(ports))

        # Volumes
        volumes = []
        if stateful_cap is not None:
            volumes.append(self.state_dir)
        if turnbased_cap is not None:
            volumes.append(f"{self.workdir}/weaves")
        if volumes:
            sections.append(self._generate_volumes(volumes))

        # Healthcheck
        sections.append(self._generate_healthcheck())

        # Entrypoint
        sections.append(self._generate_entrypoint(module_name, class_name))

        return "\n".join(sections)

    def compile_artifact(self, agent_cls: type["Agent[Any, Any]"]) -> DockerArtifact:
        """
        Compile to DockerArtifact for composition with other projectors.

        Returns structured artifact with metadata for downstream use.
        """
        from agents.a.halo import get_halo

        halo = get_halo(agent_cls)

        def _get_cap(cap_name: str) -> Any:
            for c in halo:
                if type(c).__name__ == cap_name:
                    return c
            return None

        dockerfile = self.compile(agent_cls)
        image_name = f"{self.image_prefix}{self._derive_image_name(agent_cls)}"

        # Collect ports
        ports = [self.default_port]
        if _get_cap("ObservableCapability") is not None:
            observable_cap = _get_cap("ObservableCapability")
            if getattr(observable_cap, "metrics", False):
                ports.append(self.metrics_port)

        # Collect volumes
        volumes = []
        if _get_cap("StatefulCapability") is not None:
            volumes.append(self.state_dir)
        if _get_cap("TurnBasedCapability") is not None:
            volumes.append(f"{self.workdir}/weaves")

        return DockerArtifact(
            dockerfile=dockerfile,
            image_name=image_name,
            exposed_ports=ports,
            volumes=volumes,
        )

    def _derive_image_name(self, agent_cls: type) -> str:
        """Convert CamelCase class name to kebab-case image name."""
        name = agent_cls.__name__
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("-")
            result.append(char.lower())
        return "".join(result)

    def _generate_header(self, agent_name: str, class_name: str) -> str:
        """Generate Dockerfile header with metadata."""
        return textwrap.dedent(f"""
            # Dockerfile for {class_name}
            # Generated by DockerProjector from kgents
            #
            # Build: docker build -t {self.image_prefix}{agent_name} .
            # Run:   docker run -p 8080:8080 {self.image_prefix}{agent_name}

            FROM {self.base_image}

            LABEL org.opencontainers.image.title="{agent_name}"
            LABEL org.opencontainers.image.description="kgents agent: {class_name}"
            LABEL org.opencontainers.image.source="https://github.com/kgents/kgents"

            WORKDIR {self.workdir}
        """).strip()

    def _generate_simple_deps(self) -> str:
        """Generate simple dependency installation."""
        return textwrap.dedent("""
            # Install dependencies
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt
        """).strip()

    def _generate_multistage_deps(self) -> str:
        """Generate multi-stage build for optimized layers."""
        return textwrap.dedent(f"""
            # Builder stage for dependencies
            FROM {self.base_image} AS builder

            WORKDIR /build
            COPY requirements.txt .
            RUN pip install --user --no-cache-dir -r requirements.txt

            # Final stage
            FROM {self.base_image}
            WORKDIR {self.workdir}

            # Copy installed dependencies from builder
            COPY --from=builder /root/.local /root/.local
            ENV PATH=/root/.local/bin:$PATH
        """).strip()

    def _generate_copy_app(self) -> str:
        """Generate application copy commands."""
        return textwrap.dedent("""
            # Copy application code
            COPY . .
        """).strip()

    def _build_env_vars(
        self,
        agent_name: str,
        module_name: str,
        class_name: str,
        soulful_cap: Any | None,
    ) -> dict[str, str]:
        """Build environment variables dict."""
        env = {
            "KGENTS_AGENT_NAME": agent_name,
            "KGENTS_AGENT_MODULE": module_name,
            "KGENTS_AGENT_CLASS": class_name,
            "PYTHONUNBUFFERED": "1",
        }

        if soulful_cap is not None:
            persona = getattr(soulful_cap, "persona", "default")
            mode = getattr(soulful_cap, "mode", "advisory")
            env["KGENT_PERSONA"] = persona
            env["KGENT_MODE"] = mode

        return env

    def _generate_env(self, env_vars: dict[str, str]) -> str:
        """Generate ENV instructions."""
        lines = ["# Environment variables"]
        for key, value in env_vars.items():
            lines.append(f'ENV {key}="{value}"')
        return "\n".join(lines)

    def _generate_expose(self, ports: list[int]) -> str:
        """Generate EXPOSE instructions."""
        lines = ["# Exposed ports"]
        for port in ports:
            lines.append(f"EXPOSE {port}")
        return "\n".join(lines)

    def _generate_volumes(self, volumes: list[str]) -> str:
        """Generate VOLUME instructions."""
        lines = ["# Persistent volumes"]
        for vol in volumes:
            lines.append(f"VOLUME {vol}")
        return "\n".join(lines)

    def _generate_healthcheck(self) -> str:
        """Generate HEALTHCHECK instruction."""
        return textwrap.dedent(f"""
            # Health check
            HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
                CMD curl -f http://localhost:{self.default_port}/health || exit 1
        """).strip()

    def _generate_entrypoint(self, module_name: str, class_name: str) -> str:
        """Generate entrypoint command."""
        return textwrap.dedent(f"""
            # Entrypoint
            CMD ["python", "-m", "uvicorn", "{module_name}:create_app", "--factory", "--host", "0.0.0.0", "--port", "{self.default_port}"]
        """).strip()

    def supports(self, capability: type["CapabilityBase"]) -> bool:
        """
        Check if DockerProjector supports a capability type.

        DockerProjector supports all five standard capabilities.

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
            TurnBasedCapability,
        )

        return capability in {
            StatefulCapability,
            SoulfulCapability,
            ObservableCapability,
            StreamableCapability,
            TurnBasedCapability,
        }
