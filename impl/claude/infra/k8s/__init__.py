"""
K8s infrastructure for K-Terrarium.

Provides Kind cluster lifecycle management with graceful degradation
for environments without Kubernetes tooling.

K-Terrarium transforms kgents from Python processes sharing a filesystem
into a Kubernetes-native agent ecosystem where:

- Isolation is physics (container boundaries)
- Economics are enforced (ResourceQuotas)
- Topology is invariant (DNS service discovery)
- Failures are contained (Pod-level blast radius)

Usage:
    from infra.k8s import KindCluster, detect_terrarium_mode

    # Check environment
    detection = detect_terrarium_mode()
    if detection.can_create_cluster:
        cluster = KindCluster()
        result = cluster.create()
        print(f"Cluster ready in {result.elapsed_seconds:.1f}s")

Graceful Degradation:
    The K-Terrarium is opt-in. When Docker/Kind are not available,
    existing bare-metal mode continues to work.
"""

from .cluster import (
    ClusterConfig,
    ClusterResult,
    ClusterStatus,
    KindCluster,
)
from .detection import (
    TerrariumCapability,
    TerrariumDetection,
    detect_terrarium_mode,
    get_cluster_container_name,
    is_cluster_container_paused,
    is_cluster_container_running,
)
from .dev_mode import (
    DevMode,
    DevModeConfig,
    DevModeResult,
    DevModeStatus,
    DevPodSpec,
    create_dev_mode,
)
from .exceptions import (
    ClusterNotFoundError,
    ClusterOperationError,
    DockerNotFoundError,
    EntrypointInvalidError,
    ImageNotFoundError,
    KindNotFoundError,
    KubectlNotFoundError,
    TerrariumError,
)
from .operator import (
    AgentOperator,
    AgentPhase,
    AgentSpec,
    DeployMode,
    ReconcileResult,
    ValidationResult,
    create_operator,
)
from .spec_to_crd import (
    AgentSpecDefinition,
    GeneratorResult,
    SpecParser,
    SpecToCRDGenerator,
    install_git_hook,
)

__all__ = [
    # Cluster Management
    "KindCluster",
    "ClusterConfig",
    "ClusterResult",
    "ClusterStatus",
    # Detection
    "detect_terrarium_mode",
    "TerrariumDetection",
    "TerrariumCapability",
    "get_cluster_container_name",
    "is_cluster_container_paused",
    "is_cluster_container_running",
    # Exceptions
    "TerrariumError",
    "KindNotFoundError",
    "DockerNotFoundError",
    "ClusterNotFoundError",
    "ClusterOperationError",
    "KubectlNotFoundError",
    "ImageNotFoundError",
    "EntrypointInvalidError",
    # Operator
    "AgentOperator",
    "AgentPhase",
    "AgentSpec",
    "DeployMode",
    "ReconcileResult",
    "ValidationResult",
    "create_operator",
    # Spec-to-CRD
    "AgentSpecDefinition",
    "GeneratorResult",
    "SpecParser",
    "SpecToCRDGenerator",
    "install_git_hook",
    # Dev Mode
    "DevMode",
    "DevModeConfig",
    "DevModeResult",
    "DevModeStatus",
    "DevPodSpec",
    "create_dev_mode",
]
