"""
Contradiction Service: Detection, Classification, and Resolution.

The Contradiction Engine is ONE OF THE MOST IMPORTANT PARTS of the Zero Seed system.

Core Components:
1. Detection (detection.py): Super-additive loss analysis
2. Classification (classification.py): Strength-based taxonomy
3. Resolution (resolution.py): Five resolution strategies
4. UI Generation (ui.py): Backend-driven presentation state

Philosophy:
    "Surfacing, interrogating, and systematically interacting with
     personal beliefs, values, and contradictions is ONE OF THE MOST
     IMPORTANT PARTS of the system."
    - Zero Seed Grand Strategy, LAW 4

Quick Start:
    ```python
    from services.contradiction import (
        detect_contradiction,
        classify_contradiction,
        create_resolution_prompt,
        generate_contradiction_card,
    )

    # Detect
    pair = await detect_contradiction(kblock_a, kblock_b, galois)
    if pair is None:
        return  # No contradiction

    # Classify
    classification = classify_contradiction(pair.strength)

    # Create resolution prompt
    prompt = create_resolution_prompt(pair, classification)

    # Generate UI
    card = generate_contradiction_card(pair, classification, prompt)
    ```

See: plans/zero-seed-genesis-grand-strategy.md (Phase 4)
"""

from __future__ import annotations

# Detection
from .detection import (
    CONTRADICTION_THRESHOLD,
    ContradictionDetector,
    ContradictionPair,
    default_detector,
    detect_contradiction,
)

# Classification
from .classification import (
    APPARENT_MAX,
    ClassificationResult,
    ContradictionClassifier,
    ContradictionType,
    PRODUCTIVE_MAX,
    TENSION_MAX,
    classify_contradiction,
    default_classifier,
)

# Resolution
from .resolution import (
    ResolutionEngine,
    ResolutionOutcome,
    ResolutionPrompt,
    ResolutionStrategy,
    create_resolution_prompt,
    default_engine,
)

# UI Generation
from .ui import (
    ContradictionCardUI,
    ContradictionUIGenerator,
    ResolutionDialogUI,
    default_generator,
    generate_contradiction_card,
    generate_resolution_dialog,
)

__all__ = [
    # === Detection ===
    "CONTRADICTION_THRESHOLD",
    "ContradictionPair",
    "ContradictionDetector",
    "detect_contradiction",
    "default_detector",
    # === Classification ===
    "ContradictionType",
    "APPARENT_MAX",
    "PRODUCTIVE_MAX",
    "TENSION_MAX",
    "ClassificationResult",
    "ContradictionClassifier",
    "classify_contradiction",
    "default_classifier",
    # === Resolution ===
    "ResolutionStrategy",
    "ResolutionOutcome",
    "ResolutionPrompt",
    "ResolutionEngine",
    "create_resolution_prompt",
    "default_engine",
    # === UI Generation ===
    "ContradictionCardUI",
    "ResolutionDialogUI",
    "ContradictionUIGenerator",
    "generate_contradiction_card",
    "generate_resolution_dialog",
    "default_generator",
]
