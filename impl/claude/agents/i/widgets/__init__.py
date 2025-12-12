"""I-gent v2.5 Widgets - Density Fields, Flow Arrows, Health Bars, and Overlays."""

from .agentese_hud import (
    AgentContext,
    AgentesePath,
    AgentHUD,
    CompactAgentHUD,
    create_demo_paths,
)
from .density_field import DensityField
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
from .health_bar import CompactHealthBar, MiniHealthBar, XYZHealthBar
from .proprioception import (
    ProprioceptionBar,
    ProprioceptionBars,
    ProprioceptionState,
    ReplicaIndicator,
    TraumaIndicator,
    TraumaLevel,
)
from .waveform import OperationType, ProcessingWaveform, WaveformDisplay

__all__ = [
    # Core widgets
    "DensityField",
    "FlowArrow",
    # Health widgets
    "XYZHealthBar",
    "CompactHealthBar",
    "MiniHealthBar",
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
