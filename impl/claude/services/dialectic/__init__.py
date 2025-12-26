"""
Dialectic Crown Jewel: Thesis-Antithesis-Synthesis for Kent+Claude Fusion.

Theory Basis (Ch 17: Dialectical Fusion):
    Dialectical fusion (Kent + Claude):
      thesis: Kent's view
      antithesis: Claude's view
      synthesis: Cocone construction (REVISED: Heuristic synthesis with preservation)

    The Emerging Constitution (7 articles) governs the fusion:
      I.   Symmetric Agency
      II.  Adversarial Cooperation
      III. Supersession Rights
      IV.  The Disgust Veto (Kent's absolute)
      V.   Trust Accumulation
      VI.  Fusion as Goal
      VII. Amendment

Philosophy:
    "The goal is not Kent's decisions or AI's decisions.
     The goal is fused decisions better than either alone.
     Individual ego is dissolved into shared purpose."

See: docs/theory/17-dialectic.md
See: plans/theory-operationalization/05-co-engineering.md (E3)
"""

from .fusion import (
    DialecticalFusionService,
    Fusion,
    FusionResult,
    FusionStore,
    Position,
    create_position,
    get_fusion_store,
    reset_fusion_store,
)

__all__ = [
    # Core types
    "FusionResult",
    "Position",
    "Fusion",
    # Store
    "FusionStore",
    # Service
    "DialecticalFusionService",
    # Factories
    "create_position",
    # Global store access
    "get_fusion_store",
    "reset_fusion_store",
]
