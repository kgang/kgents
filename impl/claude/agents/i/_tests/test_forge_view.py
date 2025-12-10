"""
Tests for the Forge View (I-gent × F-gent integration).

Tests cover:
- Archetype data structure
- Pipeline composition
- Type checking
- Rendering
- Key handling
"""

import pytest

from agents.i.forge_view import (
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
    load_archetypes_from_entries,
)
from agents.l.catalog import CatalogEntry, EntityType as LEntityType, Status


class TestArchetype:
    """Tests for Archetype data structure."""

    def test_create_archetype(self):
        """Test basic archetype creation."""
        arch = Archetype(
            id="test",
            name="TestAgent",
            symbol="T",
            level=ArchetypeLevel.EXPERT,
        )
        assert arch.id == "test"
        assert arch.name == "TestAgent"
        assert arch.symbol == "T"
        assert arch.level == ArchetypeLevel.EXPERT

    def test_archetype_defaults(self):
        """Test archetype default values."""
        arch = Archetype(id="x", name="X", symbol="X")
        assert arch.level == ArchetypeLevel.JOURNEYMAN
        assert arch.input_type == "Any"
        assert arch.output_type == "Any"
        assert arch.token_cost == 100
        assert arch.entropy_cost == 0.1

    def test_level_display(self):
        """Test level display string."""
        arch = Archetype(
            id="x",
            name="X",
            symbol="X",
            level=ArchetypeLevel.MASTER,
        )
        assert arch.level_display == "lvl.5"

    def test_archetype_levels(self):
        """Test all archetype levels."""
        levels = list(ArchetypeLevel)
        assert len(levels) == 5
        assert ArchetypeLevel.NOVICE.value == 1
        assert ArchetypeLevel.MASTER.value == 5

    def test_default_archetypes(self):
        """Test that default archetypes are valid."""
        assert len(DEFAULT_ARCHETYPES) >= 5
        for arch in DEFAULT_ARCHETYPES:
            assert arch.id
            assert arch.name
            assert arch.symbol
            assert len(arch.symbol) == 1


class TestPipelineSlot:
    """Tests for PipelineSlot."""

    def test_empty_slot(self):
        """Test empty slot."""
        slot = PipelineSlot()
        assert slot.is_empty
        assert slot.symbol == "·"
        assert slot.name == "(empty)"

    def test_slot_with_archetype(self):
        """Test slot with archetype."""
        arch = Archetype(id="x", name="XAgent", symbol="X")
        slot = PipelineSlot(archetype=arch)
        assert not slot.is_empty
        assert slot.symbol == "X"
        assert slot.name == "XAgent"

    def test_slot_rune(self):
        """Test slot rune (placeholder)."""
        slot = PipelineSlot(is_rune=True)
        assert not slot.is_empty
        assert slot.symbol == "+"
        assert slot.name == "+ Slot Rune"


class TestPipeline:
    """Tests for Pipeline composition."""

    def test_empty_pipeline(self):
        """Test empty pipeline."""
        pipe = Pipeline()
        assert len(pipe.slots) == 0
        assert pipe.total_token_cost == 0
        assert pipe.total_entropy_cost == 0
        assert pipe.composition_string == "(empty)"

    def test_add_archetype(self):
        """Test adding archetype to pipeline."""
        pipe = Pipeline()
        arch = Archetype(id="x", name="X", symbol="X", token_cost=150)
        pipe.add(arch)
        assert len(pipe.slots) == 1
        assert pipe.slots[0].archetype == arch
        assert pipe.total_token_cost == 150

    def test_add_rune(self):
        """Test adding slot rune."""
        pipe = Pipeline()
        pipe.add_rune()
        assert len(pipe.slots) == 1
        assert pipe.slots[0].is_rune

    def test_remove_slot(self):
        """Test removing slot."""
        pipe = Pipeline()
        arch = Archetype(id="x", name="X", symbol="X")
        pipe.add(arch)
        pipe.add_rune()

        removed = pipe.remove(0)
        assert removed is not None
        assert removed.archetype == arch
        assert len(pipe.slots) == 1

    def test_remove_invalid_index(self):
        """Test removing from invalid index."""
        pipe = Pipeline()
        assert pipe.remove(0) is None
        assert pipe.remove(-1) is None
        assert pipe.remove(10) is None

    def test_clear_pipeline(self):
        """Test clearing pipeline."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="A", symbol="A"))
        pipe.add(Archetype(id="b", name="B", symbol="B"))
        pipe.clear()
        assert len(pipe.slots) == 0

    def test_composition_string(self):
        """Test composition string generation."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="Foo", symbol="F"))
        pipe.add(Archetype(id="b", name="Bar", symbol="B"))
        pipe.add(Archetype(id="c", name="Baz", symbol="Z"))

        assert pipe.composition_string == "Foo >> Bar >> Baz"

    def test_composition_string_with_runes(self):
        """Test composition string with slot runes."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="Foo", symbol="F"))
        pipe.add_rune()
        pipe.add(Archetype(id="b", name="Bar", symbol="B"))

        assert pipe.composition_string == "Foo >> ? >> Bar"

    def test_total_costs(self):
        """Test total cost calculation."""
        pipe = Pipeline()
        pipe.add(
            Archetype(id="a", name="A", symbol="A", token_cost=100, entropy_cost=0.1)
        )
        pipe.add(
            Archetype(id="b", name="B", symbol="B", token_cost=200, entropy_cost=0.2)
        )
        pipe.add_rune()  # Runes don't add cost

        assert pipe.total_token_cost == 300
        assert pipe.total_entropy_cost == pytest.approx(0.3)


class TestPipelineTypeCheck:
    """Tests for pipeline type checking."""

    def test_type_check_empty(self):
        """Test type checking empty pipeline."""
        pipe = Pipeline()
        errors = pipe.type_check()
        assert errors == []

    def test_type_check_single(self):
        """Test type checking single-slot pipeline."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="A", symbol="A"))
        errors = pipe.type_check()
        assert errors == []

    def test_type_check_any_compatible(self):
        """Test that Any type is compatible with anything."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="A", symbol="A", output_type="Foo"))
        pipe.add(Archetype(id="b", name="B", symbol="B", input_type="Any"))
        errors = pipe.type_check()
        assert errors == []

    def test_type_check_matching_types(self):
        """Test matching types are compatible."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="A", symbol="A", output_type="Data"))
        pipe.add(Archetype(id="b", name="B", symbol="B", input_type="Data"))
        errors = pipe.type_check()
        assert errors == []

    def test_type_check_mismatch(self):
        """Test type mismatch detection."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="Foo", symbol="F", output_type="String"))
        pipe.add(Archetype(id="b", name="Bar", symbol="B", input_type="Number"))
        errors = pipe.type_check()
        assert len(errors) == 1
        assert "Type mismatch" in errors[0]
        assert "Foo" in errors[0]
        assert "Bar" in errors[0]

    def test_type_check_multiple_errors(self):
        """Test multiple type mismatches."""
        pipe = Pipeline()
        pipe.add(Archetype(id="a", name="A", symbol="A", output_type="X"))
        pipe.add(
            Archetype(id="b", name="B", symbol="B", input_type="Y", output_type="Z")
        )
        pipe.add(Archetype(id="c", name="C", symbol="C", input_type="W"))
        errors = pipe.type_check()
        assert len(errors) == 2


class TestForgeViewState:
    """Tests for ForgeViewState."""

    def test_initial_state(self):
        """Test initial state."""
        state = ForgeViewState()
        assert state.inventory == []
        assert len(state.pipeline.slots) == 0
        assert state.inventory_cursor == 0
        assert state.pipeline_cursor == 0
        assert state.active_panel == "inventory"

    def test_state_with_inventory(self):
        """Test state with inventory."""
        archs = [Archetype(id="a", name="A", symbol="A")]
        state = ForgeViewState(inventory=archs)
        assert len(state.inventory) == 1

    def test_move_cursor_inventory(self):
        """Test moving cursor in inventory."""
        archs = [
            Archetype(id="a", name="A", symbol="A"),
            Archetype(id="b", name="B", symbol="B"),
            Archetype(id="c", name="C", symbol="C"),
        ]
        state = ForgeViewState(inventory=archs)

        state.move_cursor(1)
        assert state.inventory_cursor == 1

        state.move_cursor(1)
        assert state.inventory_cursor == 2

        # Should not go past end
        state.move_cursor(1)
        assert state.inventory_cursor == 2

        # Move back up
        state.move_cursor(-1)
        state.move_cursor(-1)
        assert state.inventory_cursor == 0

        # Should not go below 0
        state.move_cursor(-1)
        assert state.inventory_cursor == 0

    def test_move_cursor_pipeline(self):
        """Test moving cursor in pipeline."""
        state = ForgeViewState()
        state.active_panel = "pipeline"
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        state.pipeline.add(Archetype(id="b", name="B", symbol="B"))

        state.move_cursor(1)
        assert state.pipeline_cursor == 1

    def test_switch_panel(self):
        """Test switching between panels."""
        state = ForgeViewState()
        assert state.active_panel == "inventory"

        state.switch_panel()
        assert state.active_panel == "pipeline"

        state.switch_panel()
        assert state.active_panel == "inventory"

    def test_add_selected_to_pipeline(self):
        """Test adding selected archetype to pipeline."""
        archs = [
            Archetype(id="a", name="A", symbol="A"),
            Archetype(id="b", name="B", symbol="B"),
        ]
        state = ForgeViewState(inventory=archs)
        state.inventory_cursor = 1

        result = state.add_selected_to_pipeline()
        assert result is True
        assert len(state.pipeline.slots) == 1
        assert state.pipeline.slots[0].archetype.id == "b"

    def test_add_from_empty_inventory(self):
        """Test adding from empty inventory."""
        state = ForgeViewState()
        result = state.add_selected_to_pipeline()
        assert result is False

    def test_add_from_pipeline_panel(self):
        """Test adding when pipeline panel is active (should fail)."""
        state = ForgeViewState(inventory=[Archetype(id="a", name="A", symbol="A")])
        state.active_panel = "pipeline"
        result = state.add_selected_to_pipeline()
        assert result is False

    def test_remove_from_pipeline(self):
        """Test removing from pipeline."""
        state = ForgeViewState()
        state.active_panel = "pipeline"
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        state.pipeline.add(Archetype(id="b", name="B", symbol="B"))

        result = state.remove_from_pipeline()
        assert result is True
        assert len(state.pipeline.slots) == 1

    def test_remove_updates_cursor(self):
        """Test that removing updates cursor position."""
        state = ForgeViewState()
        state.active_panel = "pipeline"
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        state.pipeline_cursor = 0

        state.remove_from_pipeline()
        assert state.pipeline_cursor == 0


class TestForgeViewRenderer:
    """Tests for ForgeViewRenderer."""

    def test_render_empty_state(self):
        """Test rendering empty state."""
        state = ForgeViewState()
        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        assert "COMPOSITION" in output
        assert "Inventory" in output
        assert "Pipeline" in output

    def test_render_with_inventory(self):
        """Test rendering with inventory."""
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES[:3])
        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        assert "Ground" in output
        assert "Architect" in output
        assert "Builder" in output

    def test_render_with_pipeline(self):
        """Test rendering with pipeline."""
        state = create_demo_forge_state()
        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        # Check budget is shown
        assert "tokens" in output
        assert "Entropy" in output

    def test_render_type_errors(self):
        """Test rendering type errors."""
        state = ForgeViewState()
        state.pipeline.add(Archetype(id="a", name="A", symbol="A", output_type="X"))
        state.pipeline.add(Archetype(id="b", name="B", symbol="B", input_type="Y"))

        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        assert "Type" in output or "mismatch" in output.lower()

    def test_render_valid_pipeline(self):
        """Test rendering valid pipeline shows checkmark."""
        state = ForgeViewState()
        state.pipeline.add(Archetype(id="a", name="A", symbol="A", output_type="Any"))
        state.pipeline.add(Archetype(id="b", name="B", symbol="B", input_type="Any"))

        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        assert "type-checks" in output or "✓" in output

    def test_render_color_disabled(self):
        """Test rendering without color codes."""
        state = create_demo_forge_state()
        renderer = ForgeViewRenderer(state, use_color=False)
        output = renderer.render()

        # Should not contain ANSI escape codes
        assert "\033[" not in output

    def test_render_color_enabled(self):
        """Test rendering with color codes."""
        state = create_demo_forge_state()
        renderer = ForgeViewRenderer(state, use_color=True)
        output = renderer.render()

        # Should contain ANSI escape codes
        assert "\033[" in output


class TestForgeViewKeyHandler:
    """Tests for ForgeViewKeyHandler."""

    def test_move_up(self):
        """Test move up key."""
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES[:3])
        state.inventory_cursor = 1
        handler = ForgeViewKeyHandler(state)

        handled = handler.handle("k")
        assert handled is True
        assert state.inventory_cursor == 0

    def test_move_down(self):
        """Test move down key."""
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES[:3])
        handler = ForgeViewKeyHandler(state)

        handled = handler.handle("j")
        assert handled is True
        assert state.inventory_cursor == 1

    def test_switch_panel(self):
        """Test tab switches panel."""
        state = ForgeViewState()
        handler = ForgeViewKeyHandler(state)

        handled = handler.handle("\t")
        assert handled is True
        assert state.active_panel == "pipeline"

    def test_add_to_pipeline(self):
        """Test enter adds to pipeline."""
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES[:1])
        handler = ForgeViewKeyHandler(state)

        handler.handle("\r")
        assert len(state.pipeline.slots) == 1

    def test_delete_from_pipeline(self):
        """Test d deletes from pipeline."""
        state = ForgeViewState()
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        state.active_panel = "pipeline"
        handler = ForgeViewKeyHandler(state)

        handler.handle("d")
        assert len(state.pipeline.slots) == 0

    def test_add_rune(self):
        """Test + adds rune."""
        state = ForgeViewState()
        handler = ForgeViewKeyHandler(state)

        handler.handle("+")
        assert len(state.pipeline.slots) == 1
        assert state.pipeline.slots[0].is_rune

    def test_clear_pipeline(self):
        """Test c clears pipeline."""
        state = ForgeViewState()
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        state.pipeline.add(Archetype(id="b", name="B", symbol="B"))
        handler = ForgeViewKeyHandler(state)

        handler.handle("c")
        assert len(state.pipeline.slots) == 0

    def test_execute_handler(self):
        """Test execute handler is called."""
        state = ForgeViewState()
        state.pipeline.add(Archetype(id="a", name="A", symbol="A"))
        handler = ForgeViewKeyHandler(state)

        executed_pipeline = None

        def on_execute(p):
            nonlocal executed_pipeline
            executed_pipeline = p

        handler.set_execute_handler(on_execute)
        handler.handle("x")

        assert executed_pipeline is not None
        assert executed_pipeline == state.pipeline

    def test_exit_handler(self):
        """Test exit handler is called."""
        state = ForgeViewState()
        handler = ForgeViewKeyHandler(state)

        exited = False

        def on_exit():
            nonlocal exited
            exited = True

        handler.set_exit_handler(on_exit)
        handler.handle("q")

        assert exited is True

    def test_unknown_key(self):
        """Test unknown key is not handled."""
        state = ForgeViewState()
        handler = ForgeViewKeyHandler(state)

        handled = handler.handle("z")
        assert handled is False


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_demo_forge_state(self):
        """Test demo state creation."""
        state = create_demo_forge_state()

        assert len(state.inventory) > 0
        assert len(state.pipeline.slots) > 0

    def test_render_forge_view_once(self):
        """Test one-shot rendering."""
        state = create_demo_forge_state()
        output = render_forge_view_once(state, use_color=False)

        assert isinstance(output, str)
        assert len(output) > 0
        assert "Inventory" in output

    def test_render_forge_view_with_color(self):
        """Test one-shot rendering with color."""
        state = create_demo_forge_state()
        output = render_forge_view_once(state, use_color=True)

        assert "\033[" in output


class TestIntegrationScenarios:
    """Integration tests for common use cases."""

    def test_build_complete_pipeline(self):
        """Test building a complete pipeline from scratch."""
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES)
        handler = ForgeViewKeyHandler(state)

        # Add Ground
        handler.handle("\r")  # Add first item
        assert len(state.pipeline.slots) == 1

        # Move to K-Gent (index 4)
        for _ in range(4):
            handler.handle("j")
        handler.handle("\r")
        assert len(state.pipeline.slots) == 2

        # Move to Judge (index 5)
        handler.handle("j")
        handler.handle("\r")
        assert len(state.pipeline.slots) == 3

        # Check composition
        assert "Ground" in state.pipeline.composition_string
        assert "Judge" in state.pipeline.composition_string

    def test_edit_pipeline(self):
        """Test editing an existing pipeline."""
        state = create_demo_forge_state()
        original_count = len(state.pipeline.slots)
        handler = ForgeViewKeyHandler(state)

        # Switch to pipeline
        handler.handle("\t")
        assert state.active_panel == "pipeline"

        # Delete first item
        handler.handle("d")
        assert len(state.pipeline.slots) == original_count - 1

        # Add a rune
        handler.handle("+")
        assert state.pipeline.slots[-1].is_rune

    def test_type_safe_pipeline(self):
        """Test building a type-safe pipeline."""
        ground = Archetype(
            id="ground",
            name="Ground",
            symbol="G",
            output_type="GroundedConcept",
        )
        processor = Archetype(
            id="proc",
            name="Processor",
            symbol="P",
            input_type="GroundedConcept",
            output_type="ProcessedData",
        )
        validator = Archetype(
            id="val",
            name="Validator",
            symbol="V",
            input_type="ProcessedData",
        )

        state = ForgeViewState(inventory=[ground, processor, validator])
        handler = ForgeViewKeyHandler(state)

        # Build pipeline
        handler.handle("\r")  # Ground
        handler.handle("j")
        handler.handle("\r")  # Processor
        handler.handle("j")
        handler.handle("\r")  # Validator

        # Should type-check
        errors = state.pipeline.type_check()
        assert errors == []

    def test_type_unsafe_pipeline(self):
        """Test detecting type errors in pipeline."""
        producer = Archetype(
            id="prod",
            name="Producer",
            symbol="P",
            output_type="TypeA",
        )
        consumer = Archetype(
            id="cons",
            name="Consumer",
            symbol="C",
            input_type="TypeB",  # Incompatible!
        )

        state = ForgeViewState(inventory=[producer, consumer])
        handler = ForgeViewKeyHandler(state)

        handler.handle("\r")  # Producer
        handler.handle("j")
        handler.handle("\r")  # Consumer

        errors = state.pipeline.type_check()
        assert len(errors) == 1
        assert "Type mismatch" in errors[0]


class TestLgentIntegration:
    """Tests for L-gent catalog integration."""

    def test_archetype_from_catalog_entry_novice(self):
        """Test converting a new catalog entry (novice level)."""
        entry = CatalogEntry(
            id="test-agent",
            entity_type=LEntityType.AGENT,
            name="TestAgent",
            version="1.0.0",
            description="A test agent",
            keywords=["test", "demo"],
            input_type="String",
            output_type="Number",
            usage_count=0,
            success_rate=1.0,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.id == "test-agent"
        assert arch.name == "TestAgent"
        assert arch.symbol == "T"
        assert arch.level == ArchetypeLevel.NOVICE
        assert arch.input_type == "String"
        assert arch.output_type == "Number"
        assert "test" in arch.tags

    def test_archetype_from_catalog_entry_master(self):
        """Test converting a well-used catalog entry (master level)."""
        entry = CatalogEntry(
            id="master-agent",
            entity_type=LEntityType.AGENT,
            name="MasterAgent",
            version="5.0.0",
            description="A battle-tested agent",
            keywords=["production"],
            usage_count=150,
            success_rate=0.95,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.level == ArchetypeLevel.MASTER

    def test_archetype_from_catalog_entry_expert(self):
        """Test expert level threshold."""
        entry = CatalogEntry(
            id="expert-agent",
            entity_type=LEntityType.AGENT,
            name="Expert",
            version="1.0.0",
            description="",
            keywords=[],
            usage_count=60,
            success_rate=0.85,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.level == ArchetypeLevel.EXPERT

    def test_archetype_from_catalog_entry_journeyman(self):
        """Test journeyman level threshold."""
        entry = CatalogEntry(
            id="journey-agent",
            entity_type=LEntityType.AGENT,
            name="Journey",
            version="1.0.0",
            description="",
            keywords=[],
            usage_count=15,
            success_rate=0.7,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.level == ArchetypeLevel.JOURNEYMAN

    def test_archetype_from_catalog_entry_apprentice(self):
        """Test apprentice level threshold."""
        entry = CatalogEntry(
            id="app-agent",
            entity_type=LEntityType.AGENT,
            name="Apprentice",
            version="1.0.0",
            description="",
            keywords=[],
            usage_count=5,
            success_rate=0.5,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.level == ArchetypeLevel.APPRENTICE

    def test_archetype_default_types(self):
        """Test that missing types default to Any."""
        entry = CatalogEntry(
            id="any-agent",
            entity_type=LEntityType.AGENT,
            name="AnyAgent",
            version="1.0.0",
            description="",
            keywords=[],
            input_type=None,
            output_type=None,
        )

        arch = archetype_from_catalog_entry(entry)

        assert arch.input_type == "Any"
        assert arch.output_type == "Any"

    def test_load_archetypes_from_entries(self):
        """Test loading archetypes from a list of entries (sync)."""
        entries = [
            CatalogEntry(
                id="agent-1",
                entity_type=LEntityType.AGENT,
                name="Agent1",
                version="1.0.0",
                description="First agent",
                keywords=[],
                status=Status.ACTIVE,
            ),
            CatalogEntry(
                id="agent-2",
                entity_type=LEntityType.AGENT,
                name="Agent2",
                version="1.0.0",
                description="Second agent",
                keywords=[],
                status=Status.ACTIVE,
            ),
            # Non-agent (should be filtered out)
            CatalogEntry(
                id="contract-1",
                entity_type=LEntityType.CONTRACT,
                name="Contract1",
                version="1.0.0",
                description="A contract",
                keywords=[],
                status=Status.ACTIVE,
            ),
            # Deprecated agent (should be filtered out)
            CatalogEntry(
                id="old-agent",
                entity_type=LEntityType.AGENT,
                name="OldAgent",
                version="1.0.0",
                description="Deprecated",
                keywords=[],
                status=Status.DEPRECATED,
            ),
        ]

        archetypes = load_archetypes_from_entries(entries)

        assert len(archetypes) == 2
        ids = [a.id for a in archetypes]
        assert "agent-1" in ids
        assert "agent-2" in ids
        assert "contract-1" not in ids
        assert "old-agent" not in ids

    def test_load_archetypes_from_entries_empty(self):
        """Test loading from empty list."""
        archetypes = load_archetypes_from_entries([])
        assert archetypes == []

    def test_create_forge_state_from_entries(self):
        """Test creating ForgeViewState from entries."""
        entries = [
            CatalogEntry(
                id="agent-1",
                entity_type=LEntityType.AGENT,
                name="Agent1",
                version="1.0.0",
                description="Test",
                keywords=[],
                status=Status.ACTIVE,
            )
        ]

        archetypes = load_archetypes_from_entries(entries)
        state = ForgeViewState(inventory=archetypes)

        assert len(state.inventory) == 1
        assert state.inventory[0].id == "agent-1"

    def test_forge_state_empty_entries_with_defaults(self):
        """Test that empty entries can use defaults."""
        archetypes = load_archetypes_from_entries([])

        # If empty, use defaults
        if not archetypes:
            archetypes = DEFAULT_ARCHETYPES.copy()

        state = ForgeViewState(inventory=archetypes)

        # Should use DEFAULT_ARCHETYPES
        assert len(state.inventory) == len(DEFAULT_ARCHETYPES)

    def test_token_cost_by_entity_type(self):
        """Test that different entity types get different token costs."""
        agent_entry = CatalogEntry(
            id="agent",
            entity_type=LEntityType.AGENT,
            name="Agent",
            version="1.0.0",
            description="",
            keywords=[],
        )
        template_entry = CatalogEntry(
            id="template",
            entity_type=LEntityType.TEMPLATE,
            name="Template",
            version="1.0.0",
            description="",
            keywords=[],
        )

        agent_arch = archetype_from_catalog_entry(agent_entry)
        template_arch = archetype_from_catalog_entry(template_entry)

        assert agent_arch.token_cost == 150
        assert template_arch.token_cost == 200

    def test_entropy_cost_scales_with_level(self):
        """Test that entropy cost increases with level."""
        novice_entry = CatalogEntry(
            id="novice",
            entity_type=LEntityType.AGENT,
            name="Novice",
            version="1.0.0",
            description="",
            keywords=[],
            usage_count=0,
        )
        master_entry = CatalogEntry(
            id="master",
            entity_type=LEntityType.AGENT,
            name="Master",
            version="1.0.0",
            description="",
            keywords=[],
            usage_count=200,
            success_rate=0.95,
        )

        novice_arch = archetype_from_catalog_entry(novice_entry)
        master_arch = archetype_from_catalog_entry(master_entry)

        # Master should have higher entropy cost
        assert master_arch.entropy_cost > novice_arch.entropy_cost
