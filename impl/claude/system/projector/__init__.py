"""
Projector: Categorical Compiler for the Alethic Architecture.

The Projector compiles agent Nucleus + Halo into target-specific artifacts.

Different Projectors produce different targets:
- LocalProjector → Runnable Python Agent
- K8sProjector → List of K8s resource manifests

The same @Stateful declaration produces different implementations:
| Capability | LocalProjector          | K8sProjector         |
|------------|-------------------------|----------------------|
| @Stateful  | VolatileAgent/SQLite    | StatefulSet + PVC    |
| @Soulful   | In-process KgentAgent   | K-gent sidecar       |
| @Observable| Pre-attached mirror     | ServiceMonitor       |
| @Streamable| asyncio FluxAgent       | HPA + autoscaling    |

See: plans/architecture/alethic.md
"""

from .base import (
    CompilationError,
    InvalidNameError,
    Projector,
    ProjectorError,
    UnsupportedCapabilityError,
)
from .k8s import K8sProjector, K8sResource, manifests_to_yaml
from .local import LocalProjector

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
]
