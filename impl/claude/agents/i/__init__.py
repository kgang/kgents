"""
I-gents: Interface Agents.

I-gent provides multiple visualization modes for the kgents ecosystem:

## v2.5 - The Semantic Flux (NEW)

    "Agents are not rooms to visit—they are currents of cognition."

    >>> from agents.i.app import FluxApp, run_flux
    >>> run_flux(demo=True)  # Launch the Semantic Flux TUI

Features:
- Density field rendering (░▒▓█) - agents as weather, not boxes
- h/j/k/l vim-style navigation
- Flow arrows with throughput-based styling
- Glitch effects for void/error states (Accursed Share made visible)
- Session state persistence

## v1.0 - The Stigmergic Field (Legacy)

Interface agents that render the kgents ecosystem as a stigmergic field:
a shared environment where agents leave traces (pheromones), respond to
traces, and coordinate without explicit communication.

    >>> from agents.i import FieldState, Entity, EntityType, FieldSimulator
    >>> state = create_demo_field()
    >>> simulator = FieldSimulator(state)
    >>> simulator.tick()  # Advance simulation

Legacy types (still available):
- Phase: Moon-cycle lifecycle states
- Glyph: Atomic unit of visualization
- Scale: Fractal zoom levels

See: spec/i-gents/README.md, plans/self/interface.md
"""

# App
from .app import FluxApp, run_flux
from .breath import BreathCycle, BreathManager

# UI Components
from .components import (
    BorderStyle,
    Color,
    DashboardPanel,
    Meter,
    MeterThreshold,
    Panel,
    ProgressBar,
    ProgressBarStyle,
    Spinner,
    SpinnerStyle,
    StatusItem,
    StatusLine,
    Table,
    TableColumn,
    colorize,
    create_dashboard,
    create_panel,
    create_progress_bar,
)
from .core_types import (
    AgentState,
    GardenState,
    Glyph,
    MarginNote,
    NoteSource,
    Phase,
    Scale,
)

# O-gent Polling (Phase 2)
from .data.ogent import (
    HealthLevel,
    OgentPoller,
    XYZHealth,
    create_mock_health,
    render_xyz_bar,
    render_xyz_compact,
    value_to_health_level,
)

# Registry (Phase 2)
from .data.registry import (
    AgentObservable,
    AgentRegistry,
    AgentStatus,
    MemoryRegistry,
    MockObservable,
    RegisteredAgent,
    RegistryCallback,
    RegistryEvent,
    RegistryEventType,
    create_demo_registry,
    create_demo_registry_async,
)

# Data/State
from .data.state import (
    AgentSnapshot,
    FluxState,
    SessionState,
    create_demo_flux_state,
)

# Dream Report Rendering (Instance DB Phase 6)
from .dream_view import (
    DreamPhase,
    MaintenanceChunk,
    MigrationProposal,
    Question,
    SimpleDreamReport,
    create_mock_dream_report,
    create_mock_questions,
    render_briefing_question,
    render_dream_report,
    render_dream_report_compact,
    render_migration_proposals,
    render_migration_sql,
    render_morning_briefing,
    render_phase_bar,
    render_phase_indicator,
)
from .export import MarkdownExporter

# New stigmergic field types
from .field import (
    DialecticPhase,
    Entity,
    EntityType,
    FieldSimulator,
    FieldState,
    Pheromone,
    PheromoneType,
    create_default_field,
    create_demo_field,
)
from .observe import GardenObserver, ObserveAction
from .renderers import (
    CardRenderer,
    GardenRenderer,
    GlyphRenderer,
    LibraryRenderer,
    PageRenderer,
)

# Screens
from .screens.flux import FluxScreen

# =============================================================================
# v2.5 - The Semantic Flux
# =============================================================================
# Theme
from .theme.earth import EARTH_PALETTE, EarthTheme

# Widgets
from .widgets.density_field import DensityField
from .widgets.density_field import Phase as FluxPhase  # Alias to avoid collision
from .widgets.flow_arrow import ConnectionType, Direction, FlowArrow
from .widgets.health_bar import CompactHealthBar, MiniHealthBar, XYZHealthBar

__all__ = [
    # Legacy Types (still supported)
    "Phase",
    "Glyph",
    "Scale",
    "MarginNote",
    "NoteSource",
    "AgentState",
    "GardenState",
    # Legacy Renderers
    "GlyphRenderer",
    "CardRenderer",
    "PageRenderer",
    "GardenRenderer",
    "LibraryRenderer",
    # Export
    "MarkdownExporter",
    # Aesthetics
    "BreathCycle",
    "BreathManager",
    # W-gent Integration
    "ObserveAction",
    "GardenObserver",
    # Stigmergic Field (new)
    "Entity",
    "EntityType",
    "FieldState",
    "FieldSimulator",
    "Pheromone",
    "PheromoneType",
    "DialecticPhase",
    "create_default_field",
    "create_demo_field",
    # UI Components
    "Color",
    "colorize",
    "ProgressBar",
    "ProgressBarStyle",
    "Spinner",
    "SpinnerStyle",
    "BorderStyle",
    "Panel",
    "Meter",
    "MeterThreshold",
    "StatusLine",
    "StatusItem",
    "Table",
    "TableColumn",
    "DashboardPanel",
    "create_progress_bar",
    "create_panel",
    "create_dashboard",
    # Dream Report Rendering (Instance DB Phase 6)
    "DreamPhase",
    "Question",
    "MaintenanceChunk",
    "MigrationProposal",
    "SimpleDreamReport",
    "render_phase_indicator",
    "render_phase_bar",
    "render_dream_report",
    "render_dream_report_compact",
    "render_morning_briefing",
    "render_briefing_question",
    "render_migration_proposals",
    "render_migration_sql",
    "create_mock_dream_report",
    "create_mock_questions",
    # ==========================================================================
    # v2.5 - The Semantic Flux
    # ==========================================================================
    # Theme
    "EARTH_PALETTE",
    "EarthTheme",
    # Widgets
    "DensityField",
    "FluxPhase",
    "FlowArrow",
    "ConnectionType",
    "Direction",
    "XYZHealthBar",
    "CompactHealthBar",
    "MiniHealthBar",
    # Data/State
    "AgentSnapshot",
    "FluxState",
    "SessionState",
    "create_demo_flux_state",
    # Registry (Phase 2)
    "AgentObservable",
    "AgentRegistry",
    "AgentStatus",
    "MemoryRegistry",
    "MockObservable",
    "RegisteredAgent",
    "RegistryCallback",
    "RegistryEvent",
    "RegistryEventType",
    "create_demo_registry",
    "create_demo_registry_async",
    # O-gent Polling (Phase 2)
    "HealthLevel",
    "OgentPoller",
    "XYZHealth",
    "create_mock_health",
    "render_xyz_bar",
    "render_xyz_compact",
    "value_to_health_level",
    # Screens
    "FluxScreen",
    # App
    "FluxApp",
    "run_flux",
]
