"""
Tests for EmergenceSheaf coherence.

Verifies:
1. Context creation and hierarchy
2. overlap() - shared context between tiles
3. restrict() - extract tile view from gallery state
4. compatible() - check tile views agree
5. glue() - combine tile views into gallery state

Target: 15+ tests for sheaf alone.
"""

import pytest

from agents.emergence import (
    EMERGENCE_SHEAF,
    FAMILY_QUALIA,
    GALLERY_CONTEXT,
    CircadianPhase,
    EmergenceContext,
    # Types
    EmergencePhase,
    # Sheaf
    EmergenceSheaf,
    EmergenceState,
    GluingError,
    PatternConfig,
    PatternFamily,
    QualiaCoords,
    RestrictionError,
    TileView,
    create_emergence_sheaf,
    create_emergence_sheaf_for_families,
    create_tile_context,
)

# =============================================================================
# Context Tests
# =============================================================================


class TestContexts:
    """Test context creation and relationships."""

    def test_gallery_context_exists(self):
        """GALLERY_CONTEXT exists and is gallery level."""
        assert GALLERY_CONTEXT is not None
        assert GALLERY_CONTEXT.level == "gallery"

    def test_create_tile_context(self):
        """create_tile_context creates valid tile context."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)

        assert ctx.level == "tile"
        assert ctx.family == PatternFamily.CHLADNI
        assert ctx.tile_index == (0, 0)
        assert ctx.parent == "gallery"

    def test_tile_context_name_format(self):
        """Tile context name follows pattern: tile_{family}_{row}_{col}."""
        ctx = create_tile_context(PatternFamily.MANDALA, 1, 2)
        assert ctx.name == "tile_mandala_1_2"

    def test_is_sibling_of(self):
        """is_sibling_of returns True for same parent tiles."""
        ctx1 = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        ctx2 = create_tile_context(PatternFamily.MANDALA, 0, 1)

        assert ctx1.is_sibling_of(ctx2)
        assert ctx2.is_sibling_of(ctx1)

    def test_gallery_not_sibling(self):
        """Gallery is not sibling of any tile."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        assert not GALLERY_CONTEXT.is_sibling_of(ctx)

    def test_shares_family(self):
        """shares_family returns True for same family tiles."""
        ctx1 = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        ctx2 = create_tile_context(PatternFamily.CHLADNI, 0, 1)
        ctx3 = create_tile_context(PatternFamily.MANDALA, 0, 0)

        assert ctx1.shares_family(ctx2)
        assert not ctx1.shares_family(ctx3)


# =============================================================================
# Sheaf Factory Tests
# =============================================================================


class TestSheafFactory:
    """Test sheaf creation."""

    def test_empty_sheaf(self):
        """Empty sheaf has just gallery context."""
        sheaf = create_emergence_sheaf()

        assert GALLERY_CONTEXT in sheaf.contexts
        assert len(sheaf.contexts) == 1

    def test_global_instance_exists(self):
        """EMERGENCE_SHEAF global instance exists."""
        assert EMERGENCE_SHEAF is not None

    def test_sheaf_for_families(self):
        """create_emergence_sheaf_for_families creates grid."""
        sheaf = create_emergence_sheaf_for_families(
            families=[PatternFamily.CHLADNI, PatternFamily.MANDALA],
            rows=2,
            cols=2,
        )

        # 2 families * 2 rows * 2 cols = 8 tiles + 1 gallery = 9 contexts
        assert len(sheaf.contexts) == 9

    def test_create_grid(self):
        """create_grid adds tiles to sheaf."""
        sheaf = create_emergence_sheaf()
        tiles = sheaf.create_grid(
            families=[PatternFamily.FLOW],
            rows=3,
            cols=3,
        )

        assert len(tiles) == 9
        # Total: 9 tiles + 1 gallery = 10 contexts
        assert len(sheaf.contexts) == 10


# =============================================================================
# Overlap Tests
# =============================================================================


class TestOverlap:
    """Test overlap() operation."""

    @pytest.fixture
    def sheaf_with_tiles(self):
        """Sheaf with some tiles."""
        return create_emergence_sheaf_for_families(
            families=[PatternFamily.CHLADNI, PatternFamily.MANDALA],
            rows=2,
            cols=2,
        )

    def test_same_context_full_overlap(self, sheaf_with_tiles):
        """Same context has full overlap."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        overlap = sheaf_with_tiles.overlap(ctx, ctx)

        assert "circadian" in overlap
        assert "family" in overlap
        assert "qualia" in overlap
        assert "selection" in overlap

    def test_gallery_tile_overlap_circadian(self, sheaf_with_tiles):
        """Gallery and tile overlap on circadian."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        overlap = sheaf_with_tiles.overlap(GALLERY_CONTEXT, ctx)

        assert "circadian" in overlap

    def test_sibling_tiles_overlap_circadian(self, sheaf_with_tiles):
        """Sibling tiles overlap on circadian."""
        ctx1 = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        ctx2 = create_tile_context(PatternFamily.MANDALA, 0, 1)
        overlap = sheaf_with_tiles.overlap(ctx1, ctx2)

        assert "circadian" in overlap

    def test_same_family_tiles_overlap_qualia(self, sheaf_with_tiles):
        """Same-family tiles overlap on qualia."""
        ctx1 = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        ctx2 = create_tile_context(PatternFamily.CHLADNI, 0, 1)
        overlap = sheaf_with_tiles.overlap(ctx1, ctx2)

        assert "family" in overlap
        assert "qualia" in overlap


# =============================================================================
# Restrict Tests
# =============================================================================


class TestRestrict:
    """Test restrict() operation."""

    @pytest.fixture
    def gallery_state(self):
        """Gallery state with selected family."""
        return EmergenceState(
            phase=EmergencePhase.GALLERY,
            selected_family=PatternFamily.CHLADNI,
            circadian=CircadianPhase.DUSK,
        )

    @pytest.fixture
    def sheaf(self):
        """Sheaf with tiles."""
        return create_emergence_sheaf_for_families(
            families=[PatternFamily.CHLADNI],
            rows=2,
            cols=2,
        )

    def test_restrict_creates_tile_view(self, sheaf, gallery_state):
        """restrict() creates valid TileView."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        sheaf.add_context(ctx)

        view = sheaf.restrict(gallery_state, ctx)

        assert isinstance(view, TileView)
        assert view.tile_id == ctx.name
        assert view.circadian == CircadianPhase.DUSK

    def test_restrict_applies_family_qualia(self, sheaf, gallery_state):
        """restrict() applies family-specific qualia."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        sheaf.add_context(ctx)

        view = sheaf.restrict(gallery_state, ctx)
        base_qualia = FAMILY_QUALIA[PatternFamily.CHLADNI]

        # Qualia should be modified by circadian but based on family
        # CHLADNI base warmth is negative
        assert view.qualia.warmth != 0.0  # Modified from base

    def test_restrict_applies_circadian_modifier(self, sheaf, gallery_state):
        """restrict() applies circadian modifier."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        sheaf.add_context(ctx)

        view = sheaf.restrict(gallery_state, ctx)
        base_qualia = FAMILY_QUALIA[PatternFamily.CHLADNI]

        # DUSK adds warmth, so result should be warmer than base
        assert view.qualia.warmth > base_qualia.warmth

    def test_restrict_marks_selected(self, sheaf, gallery_state):
        """restrict() marks selected family tiles."""
        ctx = create_tile_context(PatternFamily.CHLADNI, 0, 0)
        sheaf.add_context(ctx)

        view = sheaf.restrict(gallery_state, ctx)

        assert view.is_selected is True

    def test_restrict_non_selected_family(self, sheaf, gallery_state):
        """restrict() marks non-selected tiles as not selected."""
        ctx = create_tile_context(PatternFamily.MANDALA, 0, 0)
        sheaf.add_context(ctx)

        view = sheaf.restrict(gallery_state, ctx)

        assert view.is_selected is False

    def test_restrict_non_tile_raises(self, sheaf, gallery_state):
        """restrict() raises for non-tile context."""
        with pytest.raises(RestrictionError):
            sheaf.restrict(gallery_state, GALLERY_CONTEXT)


# =============================================================================
# Compatible Tests
# =============================================================================


class TestCompatible:
    """Test compatible() operation."""

    def test_empty_is_compatible(self):
        """Empty list is compatible."""
        sheaf = create_emergence_sheaf()
        assert sheaf.compatible([])

    def test_single_tile_compatible(self):
        """Single tile is always compatible."""
        view = TileView(
            tile_id="test",
            config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
            qualia=QualiaCoords(),
            circadian=CircadianPhase.NOON,
        )
        sheaf = create_emergence_sheaf()
        assert sheaf.compatible([view])

    def test_same_circadian_compatible(self):
        """Tiles with same circadian are compatible."""
        views = [
            TileView(
                tile_id="a",
                config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.NOON,
            ),
            TileView(
                tile_id="b",
                config=PatternConfig(family=PatternFamily.MANDALA, param1=4, param2=5),
                qualia=QualiaCoords(warmth=0.5),
                circadian=CircadianPhase.NOON,
            ),
        ]
        sheaf = create_emergence_sheaf()
        assert sheaf.compatible(views)

    def test_different_circadian_incompatible(self):
        """Tiles with different circadian are incompatible."""
        views = [
            TileView(
                tile_id="a",
                config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.NOON,
            ),
            TileView(
                tile_id="b",
                config=PatternConfig(family=PatternFamily.MANDALA, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.DUSK,
            ),
        ]
        sheaf = create_emergence_sheaf()
        assert not sheaf.compatible(views)


# =============================================================================
# Glue Tests
# =============================================================================


class TestGlue:
    """Test glue() operation."""

    def test_empty_glues_to_idle(self):
        """Empty tiles glue to IDLE state."""
        sheaf = create_emergence_sheaf()
        state = sheaf.glue([])

        assert state.phase == EmergencePhase.IDLE

    def test_glue_unselected_to_gallery(self):
        """Unselected tiles glue to GALLERY state."""
        views = [
            TileView(
                tile_id="a",
                config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.NOON,
                is_selected=False,
            ),
        ]
        sheaf = create_emergence_sheaf()
        state = sheaf.glue(views)

        assert state.phase == EmergencePhase.GALLERY

    def test_glue_selected_to_exploring(self):
        """Selected tile glues to EXPLORING state."""
        config = PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5)
        views = [
            TileView(
                tile_id="a",
                config=config,
                qualia=QualiaCoords(),
                circadian=CircadianPhase.NOON,
                is_selected=True,
            ),
        ]
        sheaf = create_emergence_sheaf()
        state = sheaf.glue(views)

        assert state.phase == EmergencePhase.EXPLORING
        assert state.pattern_config == config

    def test_glue_preserves_circadian(self):
        """Glue preserves circadian from tiles."""
        views = [
            TileView(
                tile_id="a",
                config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.DUSK,
            ),
        ]
        sheaf = create_emergence_sheaf()
        state = sheaf.glue(views)

        assert state.circadian == CircadianPhase.DUSK

    def test_glue_incompatible_raises(self):
        """Gluing incompatible tiles raises GluingError."""
        views = [
            TileView(
                tile_id="a",
                config=PatternConfig(family=PatternFamily.CHLADNI, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.NOON,
            ),
            TileView(
                tile_id="b",
                config=PatternConfig(family=PatternFamily.MANDALA, param1=4, param2=5),
                qualia=QualiaCoords(),
                circadian=CircadianPhase.MIDNIGHT,  # Different!
            ),
        ]
        sheaf = create_emergence_sheaf()

        with pytest.raises(GluingError):
            sheaf.glue(views)


# =============================================================================
# Full Round-Trip Test
# =============================================================================


class TestRoundTrip:
    """Test restrict → compatible → glue round trip."""

    def test_full_round_trip(self):
        """Can restrict, check compatible, then glue."""
        # Create gallery state
        gallery_state = EmergenceState(
            phase=EmergencePhase.GALLERY,
            selected_family=PatternFamily.CHLADNI,
            circadian=CircadianPhase.NOON,
        )

        # Create sheaf with tiles
        sheaf = create_emergence_sheaf_for_families(
            families=[PatternFamily.CHLADNI, PatternFamily.MANDALA],
            rows=1,
            cols=1,
        )

        # Restrict to all tiles
        tile_views = []
        for ctx in sheaf.contexts:
            if ctx.level == "tile":
                view = sheaf.restrict(gallery_state, ctx)
                tile_views.append(view)

        # Check compatible
        assert sheaf.compatible(tile_views)

        # Glue back
        glued_state = sheaf.glue(tile_views)

        # Verify coherence
        assert glued_state.circadian == CircadianPhase.NOON
        # Selected family should come from selected tile
        assert glued_state.selected_family == PatternFamily.CHLADNI
