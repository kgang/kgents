"""
Infra: The System Driver Layer for kgents.

This package provides infrastructure-as-code for kgents, acting as the
foundational substrate upon which D-gents (semantics) operate.

Derived from spec/principles.md and spec/bootstrap.md:
- Ground (⊥): XDG paths, infrastructure.yaml, environment
- Fix (μ): Lifecycle bootstrap until stable
- Judge (⊢): Mode detection, health checks, graceful degradation

Philosophy:
- Infrastructure stores bytes; D-gents provide meaning
- Infrastructure is eventually consistent; D-gents add transactions
- Infrastructure is stateless substrate; D-gents are stateful agents
- Infrastructure predicts and forgets; D-gents remember and witness

The Three Hemispheres:
- Left (Relational): ACID, exact, deterministic (the Bookkeeper)
- Right (Semantic): Approximate, vector, probabilistic (the Poet)
- Corpus Callosum (Synapse): Signal routing between hemispheres

Key Abstractions:
- Synapse: Event bus decoupling agent intent from storage mechanism
- Mycelium: CRDT-based local-first state (no central coordinator)
- Lethe: Cryptographic amnesia (forget data, keep statistics)
- Dreamer: Maintenance as sleep (REM cycles for optimization)

Usage:
    from infra import bootstrap, Synapse, StorageProvider

    # Bootstrap the cortex
    cortex = await bootstrap(project_path="/my/project")

    # Fire signals through the synapse
    await cortex.synapse.fire(StateChanged(key="user", value=state))

    # Access storage (Left Hemisphere)
    await cortex.storage.relational.execute("SELECT ...")

    # Access semantics (Right Hemisphere via D-gent adapter)
    from agents.d import UnifiedMemory
    memory = UnifiedMemory.from_cortex(cortex)
"""

from .ground import (
    Ground,
    InfrastructureConfig,
    XDGPaths,
    resolve_ground,
)
from .lifecycle import (
    LifecycleManager,
    LifecycleState,
    OperationMode,
    bootstrap,
    quick_bootstrap,
)
from .storage import (
    ProviderConfig,
    RetentionConfig,
    StorageProvider,
)
from .synapse import (
    Signal,
    SignalKind,
    Synapse,
    SynapseConfig,
)

__all__ = [
    # Ground (Bootstrap Agent)
    "Ground",
    "XDGPaths",
    "InfrastructureConfig",
    "resolve_ground",
    # Lifecycle (Fix applied)
    "LifecycleManager",
    "LifecycleState",
    "OperationMode",
    "bootstrap",
    "quick_bootstrap",
    # Storage (Left Hemisphere)
    "StorageProvider",
    "ProviderConfig",
    "RetentionConfig",
    # Synapse (Corpus Callosum)
    "Synapse",
    "Signal",
    "SignalKind",
    "SynapseConfig",
]
