"""
Creative Production Studio (S-gent) -- Crown Jewel for Creative Asset Production.

The Studio synthesizes archaeological findings with creative vision to produce
art assets. It absorbs and supersedes the defunct Atelier/Forge concepts.

AGENTESE: world.studio.* (archaeology, vision, production, assets, gallery)

Pipeline:
    RawMaterial -> Archaeology -> Findings -> Synthesis -> Vision -> Production -> Assets

Components:
- StudioPolynomial: State machine for creative production phases (polynomial.py)
- STUDIO_OPERAD: Composition grammar for creative operations (operad.py)

LLM Integration:
    The Studio supports LLM-powered functors for intelligent pattern extraction,
    vision synthesis, and asset production. When LLM credentials are available,
    the service uses:
    - LLMArchaeologyFunctor: Extract patterns with self-feedback
    - LLMVisionFunctor: Synthesize vision with Three Voices critique
    - LLMProductionFunctor: Produce assets with Floor quality checks

    When LLM is unavailable, graceful degradation to scaffold implementations.

    from services.studio.llm import has_llm_credentials
    if has_llm_credentials():
        studio = CreativeStudioService(use_llm=True)  # LLM-powered
    else:
        studio = CreativeStudioService(use_llm=False)  # Scaffold mode

The Two-Functor Insight:
    f(Principles, Archaeology) -> (Vision, Strategy)
    f(Vision | Strategy) -> (Creative Assets | Art Assets)

Teaching:
    gotcha: The Studio follows the Crown Jewel Pattern -- each component is a
            separate file with clear responsibility. If you're adding new
            functionality, determine which component owns it first.

    gotcha: All exports are explicit in __all__. If you add a new type, add it
            to both the import AND the __all__ list. Missing __all__ entries
            break `from services.studio import *` patterns.

    gotcha: The polynomial has 5 phases: ARCHAEOLOGY -> SYNTHESIS -> PRODUCTION
            -> REVIEW -> DELIVERY. Each phase accepts different inputs (mode-dependent).

    gotcha: LLM integration requires credentials (Claude CLI or Morpheus).
            Check studio.use_llm property or use has_llm_credentials() before
            relying on LLM features.

Usage:
    from services.studio import StudioPhase, STUDIO_POLYNOMIAL, STUDIO_OPERAD

    # Check valid inputs for current phase
    valid = STUDIO_POLYNOMIAL.directions(StudioPhase.ARCHAEOLOGY)

    # Get all operad operations
    ops = STUDIO_OPERAD.list_operations()

AGENTESE:
    await logos.invoke("world.studio", umwelt, aspect="manifest")
    await logos.invoke("world.studio.archaeology", umwelt, aspect="excavate", sources=[...])
    await logos.invoke("world.studio.vision", umwelt, aspect="synthesize", findings=findings)
    await logos.invoke("world.studio.production", umwelt, aspect="produce", requirement=req)

See: spec/s-gents/studio.md
"""

# Import contracts (typed BE/FE sync)
from .contracts import (
    ArchaeologicalFindings,
    # Enums
    ArchaeologyFocus,
    Asset,
    AssetType,
    ColorPalette,
    CreativeVision,
    # Vision
    DesignPrinciple,
    # Archaeology
    ExcavateRequest,
    ExportedAsset,
    ExportFormat,
    # Export
    ExportRequest,
    GalleryPlacement,
    MotionSpec,
    Pattern,
    # Gallery
    PlaceRequest,
    # Production
    ProduceRequest,
    # Manifest
    StudioManifestResponse,
    SynthesizeRequest,
    TypographySpec,
)

# Import core service
from .core import (
    CreativeStudioService,
)

# Import node (AGENTESE interface)
from .node import (
    ArchaeologyRendering,
    AssetRendering,
    ExportRendering,
    GalleryRendering,
    StudioManifestRendering,
    StudioNode,
    VisionRendering,
)
from .operad import (
    BRAND_OPERATION,
    CODIFY_OPERATION,
    COMPOSITE_OPERATION,
    EXCAVATE_OPERATION,
    EXPORT_OPERATION,
    GALLERY_OPERATION,
    HANDOFF_OPERATION,
    INTERPRET_OPERATION,
    PRODUCE_OPERATION,
    REFINE_OPERATION,
    STUDIO_OPERAD,
    SYNTHESIZE_OPERATION,
    TRACE_OPERATION,
    StudioLaw,
    StudioLawStatus,
    StudioLawVerification,
    StudioOperad,
    StudioOperation,
    create_studio_operad,
)
from .polynomial import (
    STUDIO_POLYNOMIAL,
    VALID_TRANSITIONS,
    AssetTypeInput,
    DeliveryOutput,
    ExcavateInput,
    ExportInput,
    FeedbackInput,
    FocusInput,
    GalleryInput,
    HandoffInput,
    IterateInput,
    PrincipleInput,
    ProduceInput,
    ReviewInput,
    SourceInput,
    StudioEvent,
    StudioOutput,
    StudioPhase,
    StudioPolynomial,
    StudioStateMachine,
    StudioTransition,
    StyleInput,
    SynthesizeInput,
    VisionInput,
    can_transition,
    get_valid_next_states,
    studio_directions,
    studio_transition,
)

# LLM module (lazy import to avoid import errors if dependencies missing)
# Access via: from services.studio import llm
# or: from services.studio.llm import has_llm_credentials, LLMArchaeologyFunctor, ...

__all__ = [
    # Node (AGENTESE interface)
    "StudioNode",
    # Rendering Classes
    "StudioManifestRendering",
    "ArchaeologyRendering",
    "VisionRendering",
    "AssetRendering",
    "ExportRendering",
    "GalleryRendering",
    # Contracts - Enums
    "ArchaeologyFocus",
    "AssetType",
    "ExportFormat",
    # Contracts - Manifest
    "StudioManifestResponse",
    # Contracts - Archaeology
    "ExcavateRequest",
    "Pattern",
    "ArchaeologicalFindings",
    # Contracts - Vision
    "DesignPrinciple",
    "SynthesizeRequest",
    "ColorPalette",
    "TypographySpec",
    "MotionSpec",
    "CreativeVision",
    # Contracts - Production
    "ProduceRequest",
    "Asset",
    # Contracts - Export
    "ExportRequest",
    "ExportedAsset",
    # Contracts - Gallery
    "PlaceRequest",
    "GalleryPlacement",
    # Core Service
    "CreativeStudioService",
    # Polynomial - Phase/State Types
    "StudioPhase",
    "StudioEvent",
    "StudioTransition",
    "StudioStateMachine",
    "StudioPolynomial",
    "STUDIO_POLYNOMIAL",
    # Polynomial - Transition Helpers
    "can_transition",
    "get_valid_next_states",
    "VALID_TRANSITIONS",
    # Polynomial - Direction/Transition Functions
    "studio_directions",
    "studio_transition",
    # Polynomial - Input Types
    "ExcavateInput",
    "SourceInput",
    "FocusInput",
    "SynthesizeInput",
    "PrincipleInput",
    "VisionInput",
    "ProduceInput",
    "AssetTypeInput",
    "StyleInput",
    "ReviewInput",
    "FeedbackInput",
    "IterateInput",
    "ExportInput",
    "GalleryInput",
    "HandoffInput",
    # Polynomial - Output Types
    "StudioOutput",
    "DeliveryOutput",
    # Operad - Types
    "StudioOperation",
    "StudioLaw",
    "StudioLawStatus",
    "StudioLawVerification",
    "StudioOperad",
    # Operad - Operations
    "EXCAVATE_OPERATION",
    "INTERPRET_OPERATION",
    "TRACE_OPERATION",
    "SYNTHESIZE_OPERATION",
    "CODIFY_OPERATION",
    "BRAND_OPERATION",
    "PRODUCE_OPERATION",
    "REFINE_OPERATION",
    "COMPOSITE_OPERATION",
    "EXPORT_OPERATION",
    "GALLERY_OPERATION",
    "HANDOFF_OPERATION",
    # Operad - Singleton & Factory
    "STUDIO_OPERAD",
    "create_studio_operad",
]
