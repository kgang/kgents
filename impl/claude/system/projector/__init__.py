"""
Projector: Categorical Compiler for the Alethic Architecture.

The Projector compiles agent Nucleus + Halo into target-specific artifacts.

Different Projectors produce different targets:
- LocalProjector → Runnable Python Agent
- K8sProjector → List of K8s resource manifests
- CLIProjector → Executable shell script
- DockerProjector → Dockerfile

The same @Stateful declaration produces different implementations:
| Capability | LocalProjector   | K8sProjector      | CLIProjector     | DockerProjector  |
|------------|------------------|-------------------|------------------|------------------|
| @Stateful  | StatefulAdapter  | StatefulSet + PVC | JSON file        | VOLUME mount     |
| @Soulful   | SoulfulAdapter   | K-gent sidecar    | Banner persona   | ENV vars         |
| @Observable| Pre-attached     | ServiceMonitor    | stderr metrics   | EXPOSE 9090      |
| @Streamable| FluxAgent        | HPA + autoscaling | SSE output       | Multi-stage      |
| @TurnBased | TurnBasedAdapter | ConfigMap         | Weave file       | VOLUME mount     |

Projector Composition:
    DockerProjector() >> K8sProjector()  # Dockerfile → K8s manifests with image ref

See: spec/protocols/alethic-projection.md
"""

from .base import (
    CompilationError,
    InvalidNameError,
    Projector,
    ProjectorError,
    UnsupportedCapabilityError,
)
from .cli import CLIProjector

# Import compose module to add >> operator to Projector base class
from .compose import ComposedArtifact, ComposedProjector, IdentityProjector
from .docker import DockerArtifact, DockerProjector
from .k8s import K8sProjector, K8sResource, manifests_to_yaml
from .local import LocalProjector
from .marimo import MarimoArtifact, MarimoProjector
from .wasm import WASMArtifact, WASMProjector

__all__ = [
    # Base
    "Projector",
    "ProjectorError",
    "CompilationError",
    "InvalidNameError",
    "UnsupportedCapabilityError",
    # Local
    "LocalProjector",
    # K8s
    "K8sProjector",
    "K8sResource",
    "manifests_to_yaml",
    # CLI
    "CLIProjector",
    # Docker
    "DockerProjector",
    "DockerArtifact",
    # WASM
    "WASMProjector",
    "WASMArtifact",
    # Marimo
    "MarimoProjector",
    "MarimoArtifact",
    # Composition
    "ComposedProjector",
    "ComposedArtifact",
    "IdentityProjector",
]
