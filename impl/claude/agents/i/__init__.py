"""
I-gents: The Stigmergic Field.

Interface agents that render the kgents ecosystem as a stigmergic field:
a shared environment where agents leave traces (pheromones), respond to
traces, and coordinate without explicit communication.

Core concepts:
- Field: 2D grid where entities move and interact
- Entity: Bootstrap agents + task attractors
- Pheromone: Invisible environmental traces that affect behavior
- Dialectic Phase: System-wide synthesis state

Three Layers:
1. Physical - Entity positions, phases, events
2. Topological - Composition morphisms, gravity, tension
3. Semantic - Intent, dialectic phase, value alignment

Example:
    >>> from agents.i import FieldState, Entity, EntityType, FieldSimulator
    >>>
    >>> state = create_demo_field()
    >>> simulator = FieldSimulator(state)
    >>> simulator.tick()  # Advance simulation
    >>>
    >>> from agents.i.tui import TUIApplication
    >>> app = TUIApplication(state)
    >>> app.run_sync()  # Launch interactive TUI

Legacy types (still available):
- Phase: Moon-cycle lifecycle states
- Glyph: Atomic unit of visualization
- Scale: Fractal zoom levels

See: spec/i-gents/README.md
"""

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

# Forge View (composition mode)
from .forge_view import (
    DEFAULT_ARCHETYPES,
    Archetype,
    ArchetypeLevel,
    ForgeViewKeyHandler,
    ForgeViewRenderer,
    ForgeViewState,
    Pipeline,
    PipelineSlot,
    archetype_from_catalog_entry,
    create_demo_forge_state,
    create_forge_state_from_registry,
    load_archetypes_from_entries,
    load_archetypes_from_registry,
    render_forge_view_once,
)
from .observe import GardenObserver, ObserveAction
from .renderers import (
    CardRenderer,
    GardenRenderer,
    GlyphRenderer,
    LibraryRenderer,
    PageRenderer,
)
from .types import (
    AgentState,
    GardenState,
    Glyph,
    MarginNote,
    NoteSource,
    Phase,
    Scale,
)

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
    # Forge View (composition mode)
    "Archetype",
    "ArchetypeLevel",
    "Pipeline",
    "PipelineSlot",
    "ForgeViewState",
    "ForgeViewRenderer",
    "ForgeViewKeyHandler",
    "DEFAULT_ARCHETYPES",
    "create_demo_forge_state",
    "render_forge_view_once",
    "archetype_from_catalog_entry",
    "load_archetypes_from_registry",
    "create_forge_state_from_registry",
    "load_archetypes_from_entries",
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
]
