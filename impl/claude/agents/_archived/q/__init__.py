"""
Q-gent: Quartermaster - Resource Provisioning Agent

Q-gent provisions resources for other agents. It's the gatekeeper for dangerous operations.

Key Principle: Agents never directly request cluster resources. They ask Q-gent, who
decides whether/how to provision.

Operations:
- provision_job: Execute untrusted code in disposable containers
- provision_tool: Request tools (ffmpeg, etc.) in isolated containers
- scale_resources: Request resource limit changes
- provision_network: Request network access between agents

The "Disposable Dojo" Pattern:
- Spin up a disposable container
- Run code in isolation
- Return results
- Automatically delete after TTL

K-Terrarium Integration:
- Jobs run in kgents-ephemeral namespace
- LimitRange enforces resource caps
- TTL controller cleans up completed jobs
- NetworkPolicy default-deny for isolation
"""

from .job_builder import (
    # Types
    ExecutionRequest,
    ExecutionResult,
    ImageSpec,
    # Builder
    JobBuilder,
    JobConfig,
    JobPhase,
    JobSpec,
    JobStatus,
    ResourceLimits,
    # Convenience
    create_python_job,
    create_shell_job,
    default_resource_limits,
)
from .quartermaster import (
    # Types
    ProvisionError,
    ProvisionResult,
    # Quartermaster
    Quartermaster,
    # Factory
    create_quartermaster,
)

__all__ = [
    # Types
    "ExecutionRequest",
    "ExecutionResult",
    "ImageSpec",
    "JobConfig",
    "JobPhase",
    "JobSpec",
    "JobStatus",
    "ResourceLimits",
    # Builder
    "JobBuilder",
    # Convenience
    "create_python_job",
    "create_shell_job",
    "default_resource_limits",
    # Quartermaster
    "Quartermaster",
    "ProvisionError",
    "ProvisionResult",
    "create_quartermaster",
]
