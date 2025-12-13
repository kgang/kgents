"""I-gent v2.5 Widgets - Density Fields, Flow Arrows, Health Bars, Overlays, and Cognitive Loom."""

from .agentese_hud import (
    AgentContext,
    AgentesePath,
    AgentHUD,
    CompactAgentHUD,
    create_demo_paths,
)
from .branch_tree import BranchTree
from .density_field import DensityField
from .entropy import EntropyParams, entropy_to_border_style, entropy_to_params
from .event_stream import AgentEvent, EventStream, EventStreamDisplay, EventType
from .flow_arrow import FlowArrow
from .glitch import (
    GlitchConfig,
    GlitchController,
    GlitchEvent,
    GlitchIndicator,
    GlitchType,
    add_zalgo,
    apply_glitch,
    get_glitch_controller,
    glitch_message,
)
from .graph_layout import (
    SEMANTIC_POSITIONS,
    GraphLayout,
    LayoutAlgorithm,
    NodePosition,
)
from .health_bar import CompactHealthBar, MiniHealthBar, XYZHealthBar
from .hint_container import HintContainer
from .metrics_panel import MetricsPanel, MultiMetricsPanel
from .proprioception import (
    ProprioceptionBar,
    ProprioceptionBars,
    ProprioceptionState,
    ReplicaIndicator,
    TraumaIndicator,
    TraumaLevel,
)
from .slider import SLIDER_CHARS, Slider, clamp, generate_slider_track
from .sparkline import Sparkline, generate_sparkline
from .timeline import Timeline
from .waveform import OperationType, ProcessingWaveform, WaveformDisplay

__all__ = [
    # Core widgets
    "DensityField",
    "FlowArrow",
    # Entropy system (Phase 5: Generative TUI)
    "EntropyParams",
    "entropy_to_params",
    "entropy_to_border_style",
    # Sparkline widget (Phase 5: Generative TUI)
    "Sparkline",
    "generate_sparkline",
    # Hint Container (Track C: Heterarchical UI)
    "HintContainer",
    # Cognitive Loom widgets (Track B: Temporal Topology)
    "BranchTree",
    "Timeline",
    # Graph Layout (P5: Garden View)
    "GraphLayout",
    "LayoutAlgorithm",
    "NodePosition",
    "SEMANTIC_POSITIONS",
    # Slider (P11: Direct Manipulation)
    "Slider",
    "generate_slider_track",
    "clamp",
    "SLIDER_CHARS",
    # Health widgets
    "XYZHealthBar",
    "CompactHealthBar",
    "MiniHealthBar",
    # Metrics widgets (Terrarium Phase 3)
    "MetricsPanel",
    "MultiMetricsPanel",
    # Waveform widgets (Phase 3)
    "ProcessingWaveform",
    "WaveformDisplay",
    "OperationType",
    # Event stream widgets (Phase 3)
    "EventStream",
    "EventStreamDisplay",
    "AgentEvent",
    "EventType",
    # Proprioception widgets (Phase 3)
    "ProprioceptionBar",
    "ProprioceptionBars",
    "ProprioceptionState",
    "ReplicaIndicator",
    "TraumaIndicator",
    "TraumaLevel",
    # Glitch system (Phase 4)
    "GlitchController",
    "GlitchConfig",
    "GlitchEvent",
    "GlitchType",
    "GlitchIndicator",
    "add_zalgo",
    "apply_glitch",
    "glitch_message",
    "get_glitch_controller",
    # AGENTESE HUD (Phase 4)
    "AgentHUD",
    "CompactAgentHUD",
    "AgentesePath",
    "AgentContext",
    "create_demo_paths",
]
