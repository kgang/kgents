"""
Dialectic Widget - Three-panel thesis/antithesis/synthesis visualization.

Shows the dialectical process in action:
- Thesis (left): The initial proposition
- Antithesis (middle): The contradiction
- Synthesis (right): The resolved higher truth

Colors follow earth theme; panels animate on state change.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import traitlets

from .base import KgentsWidget

# Path to JS file
_JS_DIR = Path(__file__).parent / "js"


class DialecticWidget(KgentsWidget):
    """
    Three-panel dialectic visualization.

    Features:
    - Animated panel transitions
    - Color-coded phases (thesis=amber, antithesis=rose, synthesis=sage)
    - Progress indicator for synthesis resolution
    - History of previous dialectics (compost heap)
    """

    _esm = _JS_DIR / "dialectic.js"

    # Dialectic content
    thesis = traitlets.Unicode("").tag(sync=True)
    antithesis = traitlets.Unicode("").tag(sync=True)
    synthesis = traitlets.Unicode("").tag(sync=True)

    # Metadata
    thesis_source = traitlets.Unicode("").tag(sync=True)
    antithesis_source = traitlets.Unicode("").tag(sync=True)
    synthesis_confidence = traitlets.Float(0.0).tag(sync=True)  # 0.0-1.0

    # Progress
    synthesis_progress = traitlets.Float(0.0).tag(sync=True)  # 0.0-1.0
    phase = traitlets.Unicode("dormant").tag(sync=True)  # dormant, thesis, antithesis, synthesis

    # History (compost heap)
    history: Any = traitlets.List([]).tag(sync=True)

    def set_thesis(self, content: str, source: str = "") -> None:
        """Set the thesis proposition."""
        self.thesis = content
        self.thesis_source = source
        self.phase = "thesis"
        self.synthesis_progress = 0.0

    def set_antithesis(self, content: str, source: str = "") -> None:
        """Set the antithesis contradiction."""
        self.antithesis = content
        self.antithesis_source = source
        self.phase = "antithesis"
        self.synthesis_progress = 0.33

    def set_synthesis(
        self,
        content: str,
        confidence: float = 1.0,
        archive: bool = True,
    ) -> None:
        """Set the synthesis resolution."""
        # Archive current dialectic before overwriting
        if archive and (self.thesis or self.antithesis):
            self.history = [
                *self.history[-9:],  # Keep last 10
                {
                    "thesis": self.thesis,
                    "antithesis": self.antithesis,
                    "synthesis": content,
                    "confidence": confidence,
                },
            ]

        self.synthesis = content
        self.synthesis_confidence = confidence
        self.phase = "synthesis"
        self.synthesis_progress = 1.0

    def reset(self) -> None:
        """Reset for new dialectic cycle."""
        self.thesis = ""
        self.antithesis = ""
        self.synthesis = ""
        self.thesis_source = ""
        self.antithesis_source = ""
        self.synthesis_confidence = 0.0
        self.synthesis_progress = 0.0
        self.phase = "dormant"
