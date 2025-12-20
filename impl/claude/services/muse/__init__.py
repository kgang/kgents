"""
The Muse Crown Jewel: Pattern Detection and Contextual Guidance.

The Muse is the oblique Crown Jewel that detects narrative structure
in work sessions and whispers contextual suggestions. It runs passively,
observing Experience Crystals from The Witness.

Philosophy:
    "I see the arc of your work. I know when you're rising, when you're
     stuck, when you're about to break through. I whisper—never shout."

Key Principles:
1. PASSIVE BY DEFAULT: The Muse observes, doesn't demand attention
2. WHISPERS NOT SHOUTS: One suggestion at a time, easily dismissed
3. EARNED ENCOURAGEMENT: Praise only after genuine progress detected
4. AESTHETIC SENSITIVITY: Adapts tone to user's apparent mood

AGENTESE Paths (via @node("self.muse")):
- self.muse.manifest     - Muse state, arc phase, tension
- self.muse.arc          - Current story arc analysis
- self.muse.tension      - Tension level and trend
- self.muse.whisper      - Current suggestion (if any)
- self.muse.encourage    - Request earned encouragement
- self.muse.reframe      - Request perspective shift
- self.muse.summon       - Force suggestions (bypass timing)

Story Arc Phases (Freytag's pyramid for development):
- EXPOSITION: Understanding the problem, reading code
- RISING_ACTION: Building complexity, experiments, attempts
- CLIMAX: The breakthrough (or the wall)
- FALLING_ACTION: Cleanup, refinement, polish
- DENOUEMENT: Reflection, documentation, next steps

See: plans/witness-muse-implementation.md
See: brainstorming/2025-12-19-the-witness-and-the-muse.md
"""

from .arc import ArcPhase, StoryArc, StoryArcDetector
from .contracts import (
    AcceptRequest,
    AcceptResponse,
    ArcRequest,
    ArcResponse,
    DismissRequest,
    DismissResponse,
    EncourageRequest,
    EncourageResponse,
    HistoryRequest,
    HistoryResponse,
    MuseManifestResponse,
    ReframeRequest,
    ReframeResponse,
    SummonRequest,
    SummonResponse,
    TensionRequest,
    TensionResponse,
    WhisperHistoryItem,
    WhisperRequest,
    WhisperResponse,
)
from .node import MuseManifestRendering, MuseNode
from .polynomial import (
    MUSE_POLYNOMIAL,
    MuseContext,
    MuseOutput,
    MusePolynomial,
    MuseState,
    MuseWhisper,
    muse_transition,
)
from .whisper import DismissalMemory, Suggestion, SuggestionCategory, Whisper, WhisperEngine

__all__ = [
    # State machine
    "MuseState",
    "MuseContext",
    "MusePolynomial",
    "MUSE_POLYNOMIAL",
    "muse_transition",
    "MuseOutput",
    "MuseWhisper",
    # Story arc
    "ArcPhase",
    "StoryArc",
    "StoryArcDetector",
    # Whispers
    "Whisper",
    "Suggestion",
    "SuggestionCategory",
    "WhisperEngine",
    "DismissalMemory",
    # AGENTESE Node
    "MuseNode",
    "MuseManifestRendering",
    # Contracts
    "MuseManifestResponse",
    "ArcRequest",
    "ArcResponse",
    "TensionRequest",
    "TensionResponse",
    "WhisperRequest",
    "WhisperResponse",
    "EncourageRequest",
    "EncourageResponse",
    "ReframeRequest",
    "ReframeResponse",
    "SummonRequest",
    "SummonResponse",
    "DismissRequest",
    "DismissResponse",
    "AcceptRequest",
    "AcceptResponse",
    "HistoryRequest",
    "HistoryResponse",
    "WhisperHistoryItem",
]
