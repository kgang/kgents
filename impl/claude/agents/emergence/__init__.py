"""
Emergence: Cymatics Design System Crown Jewel.

This module provides the full categorical foundation for the Emergence experience:

1. **Types** (types.py):
   - EmergencePhase: IDLE/LOADING/GALLERY/EXPLORING/EXPORTING
   - PatternFamily: The 9 cymatics pattern families
   - CircadianPhase: dawn/noon/dusk/midnight
   - QualiaCoords: Cross-modal aesthetic coordinates
   - PatternConfig: Complete pattern configuration
   - EmergenceState: Full state for polynomial

2. **Polynomial** (polynomial.py):
   - EMERGENCE_POLYNOMIAL: State machine for emergence experience
   - Inputs: SelectFamily, TuneParam, ApplyConfig, UpdateCircadian, etc.
   - Outputs: PhaseChanged, FamilyChanged, ConfigChanged, CircadianChanged

3. **Operad** (operad.py):
   - EMERGENCE_OPERAD: Grammar for pattern manipulation
   - Pattern operations: select_family, tune_param, apply_preset
   - Qualia operations: modulate_qualia, apply_circadian
   - Entropy operations: inject_entropy (Accursed Share)
   - Inherits from DESIGN_OPERAD

4. **Sheaf** (sheaf.py):
   - EmergenceSheaf: Coherence across pattern tiles
   - Ensures circadian consistency across all tiles
   - Glues tile views into gallery state

The core insight: UI = Phase × Family × Config × Circadian × Qualia

These five dimensions compose orthogonally, enabling the generative
aesthetics described in docs/creative/emergence-principles.md.

IMPLEMENTATION STATUS:
  Layer 1: EmergenceSheaf (complete)
  Layer 2: EMERGENCE_POLYNOMIAL (complete)
  Layer 3: EMERGENCE_OPERAD (complete)
  Layer 4: agents/emergence/ (this module)
  Layer 5: @node decorator (see world_emergence.py)
  Layer 6: Gateway discovery (needs import)
  Layer 7: Web projection (see EmergenceDemo.tsx)

See: plans/structured-greeting-boot.md
"""

# Types
# Operad
from .operad import (
    EMERGENCE_OPERAD,
    create_emergence_operad,
)

# Polynomial
from .polynomial import (
    # Instance
    EMERGENCE_POLYNOMIAL,
    ApplyConfig,
    CancelExport,
    CircadianChanged,
    CompleteExport,
    ConfigChanged,
    EmergenceInput,
    EmergenceOutput,
    EnterExplore,
    EnterGallery,
    ExportReady,
    FamilyChanged,
    LoadingComplete,
    NoChange,
    # Output types
    PhaseChanged,
    Reset,
    ReturnToGallery,
    # Input types
    SelectFamily,
    SelectPreset,
    StartExport,
    StartLoading,
    TuneParam,
    UpdateCircadian,
    create_emergence_polynomial,
    # Functions
    emergence_directions,
    emergence_transition,
)

# Sheaf
from .sheaf import (
    EMERGENCE_SHEAF,
    GALLERY_CONTEXT,
    # Contexts
    EmergenceContext,
    # Sheaf
    EmergenceSheaf,
    # Errors
    GluingError,
    RestrictionError,
    create_emergence_sheaf,
    create_emergence_sheaf_for_families,
    create_tile_context,
)
from .types import (
    CIRCADIAN_MODIFIERS,
    FAMILY_QUALIA,
    # Core Enums
    CircadianPhase,
    CircadianPhaseName,
    EmergencePhase,
    # State
    EmergenceState,
    # Pattern Configuration
    PatternConfig,
    PatternFamily,
    # Qualia Space
    QualiaCoords,
    QualiaModifier,
    # Tile View
    TileView,
)

__all__ = [
    # === Types ===
    # Core Enums
    "EmergencePhase",
    "PatternFamily",
    "CircadianPhase",
    "CircadianPhaseName",
    # Qualia Space
    "QualiaCoords",
    "QualiaModifier",
    "CIRCADIAN_MODIFIERS",
    # Pattern Configuration
    "PatternConfig",
    "FAMILY_QUALIA",
    # State
    "EmergenceState",
    # Tile View
    "TileView",
    # === Polynomial ===
    # Input types
    "SelectFamily",
    "SelectPreset",
    "TuneParam",
    "ApplyConfig",
    "UpdateCircadian",
    "StartLoading",
    "LoadingComplete",
    "EnterGallery",
    "EnterExplore",
    "StartExport",
    "CancelExport",
    "CompleteExport",
    "ReturnToGallery",
    "Reset",
    "EmergenceInput",
    # Output types
    "PhaseChanged",
    "FamilyChanged",
    "ConfigChanged",
    "CircadianChanged",
    "ExportReady",
    "NoChange",
    "EmergenceOutput",
    # Functions
    "emergence_directions",
    "emergence_transition",
    "create_emergence_polynomial",
    # Instance
    "EMERGENCE_POLYNOMIAL",
    # === Operad ===
    "EMERGENCE_OPERAD",
    "create_emergence_operad",
    # === Sheaf ===
    # Contexts
    "EmergenceContext",
    "GALLERY_CONTEXT",
    "create_tile_context",
    # Sheaf
    "EmergenceSheaf",
    "EMERGENCE_SHEAF",
    "create_emergence_sheaf",
    "create_emergence_sheaf_for_families",
    # Errors
    "GluingError",
    "RestrictionError",
]
