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

from .types import (
    Phase,
    Glyph,
    Scale,
    MarginNote,
    NoteSource,
    AgentState,
    GardenState,
)
from .renderers import (
    GlyphRenderer,
    CardRenderer,
    PageRenderer,
    GardenRenderer,
    LibraryRenderer,
)
from .export import MarkdownExporter
from .breath import BreathCycle, BreathManager
from .observe import ObserveAction, GardenObserver

# Forge View (composition mode)
from .forge_view import (
    Archetype,
    ArchetypeLevel,
    Pipeline,
    PipelineSlot,
    ForgeViewState,
    ForgeViewRenderer,
    ForgeViewKeyHandler,
    DEFAULT_ARCHETYPES,
    create_demo_forge_state,
    render_forge_view_once,
    archetype_from_catalog_entry,
    load_archetypes_from_registry,
    create_forge_state_from_registry,
    load_archetypes_from_entries,
)

# New stigmergic field types
from .field import (
    Entity,
    EntityType,
    FieldState,
    FieldSimulator,
    Pheromone,
    PheromoneType,
    DialecticPhase,
    create_default_field,
    create_demo_field,
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
]
