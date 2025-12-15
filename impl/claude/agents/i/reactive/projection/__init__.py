"""
Projection Protocol: Batteries-included rendering for all targets.

The Projection Protocol formalizes how widgets render to different targets.
Developers design state, projections are batteries included.

Architecture:
    ProjectionRegistry - Central registry of target-specific projectors
    ExtendedTarget - Extended RenderTarget with SSE, VR placeholders
    verify_* - Functor law verification utilities

Key Insight (from spec):
    project : State × Target → Output

    This is a natural transformation—the same state, projected through
    different functors, produces semantically equivalent views (modulo fidelity).

Usage:
    from agents.i.reactive.projection import (
        ProjectionRegistry,
        ExtendedTarget,
        verify_identity_law,
        verify_composition_law,
    )

    # Register a new target
    @ProjectionRegistry.register("webgl")
    def webgl_projector(widget: KgentsWidget, **opts) -> Any:
        return ...  # Three.js scene

    # Verify functor laws
    assert verify_identity_law(my_widget, ExtendedTarget.CLI)
"""

from agents.i.reactive.projection.laws import (
    LawVerificationResult,
    ProjectionLawError,
    verify_all_laws,
    verify_composition_law,
    verify_determinism,
    verify_identity_law,
)
from agents.i.reactive.projection.registry import (
    FidelityLevel,
    ProjectionRegistry,
    Projector,
    ProjectorFn,
)
from agents.i.reactive.projection.targets import (
    ExtendedTarget,
    TargetCapability,
    target_capabilities,
    target_fidelity,
)

__all__ = [
    # Registry
    "ProjectionRegistry",
    "Projector",
    "ProjectorFn",
    "FidelityLevel",
    # Targets
    "ExtendedTarget",
    "TargetCapability",
    "target_fidelity",
    "target_capabilities",
    # Law verification
    "verify_identity_law",
    "verify_composition_law",
    "verify_determinism",
    "verify_all_laws",
    "LawVerificationResult",
    "ProjectionLawError",
]
