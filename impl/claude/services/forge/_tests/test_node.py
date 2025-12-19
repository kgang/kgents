"""
Tests for ForgeNode AGENTESE wrapper.

Tests the @node("world.forge") integration:
- Handle and affordances based on observer
- Workshop CRUD operations
- Artisan management
- Contribution submission
- Exhibition lifecycle
- Gallery operations
- Optional: Token economy and festivals (when enabled)

Follows the pattern from services/brain/_tests/test_node.py
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from protocols.agentese.node import BasicRendering, Observer
from services.forge import ForgePersistence
from services.forge.node import (
    ArtisanListRendering,
    ArtisanRendering,
    ContributionListRendering,
    ContributionRendering,
    ExhibitionRendering,
    ForgeManifestRendering,
    ForgeNode,
    GalleryItemRendering,
    GalleryListRendering,
    WorkshopListRendering,
    WorkshopRendering,
)
from services.forge.persistence import (
    ArtisanView,
    ContributionView,
    ExhibitionView,
    ForgeStatus,
    GalleryItemView,
    WorkshopView,
)

# === Fixtures ===


@pytest.fixture
def mock_persistence() -> AsyncMock:
    """Create a mock ForgePersistence."""
    persistence = AsyncMock(spec=ForgePersistence)

    # Default manifest response
    persistence.manifest.return_value = ForgeStatus(
        total_workshops=5,
        active_workshops=2,
        total_artisans=10,
        total_contributions=25,
        total_exhibitions=3,
        open_exhibitions=1,
        storage_backend="sqlite",
    )

    return persistence


@pytest.fixture
def spectator_observer() -> Observer:
    """Create a spectator observer."""
    return Observer.from_archetype("spectator")


@pytest.fixture
def artisan_observer() -> Observer:
    """Create an artisan observer."""
    return Observer.from_archetype("artisan")


@pytest.fixture
def curator_observer() -> Observer:
    """Create a curator observer."""
    return Observer.from_archetype("curator")


@pytest.fixture
def developer_observer() -> Observer:
    """Create a developer observer (full access)."""
    return Observer.from_archetype("developer")


@pytest.fixture
def node(mock_persistence: AsyncMock) -> ForgeNode:
    """Create an ForgeNode with mock persistence."""
    return ForgeNode(forge_persistence=mock_persistence)


# === Handle Tests ===


class TestHandle:
    """Tests for ForgeNode.handle property and get_handle_info()."""

    def test_handle_returns_path(
        self,
        node: ForgeNode,
    ):
        """Handle property returns correct path."""
        assert node.handle == "world.forge"

    @pytest.mark.asyncio
    async def test_get_handle_info_returns_description(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """get_handle_info returns correct info including description."""
        result = await node.get_handle_info(spectator_observer)

        assert result["path"] == "world.forge"
        assert "creative workshop" in result["description"].lower()
        assert result["observer"]["archetype"] == "spectator"

    @pytest.mark.asyncio
    async def test_get_handle_info_shows_feature_availability(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """get_handle_info shows which features are available."""
        result = await node.get_handle_info(spectator_observer)

        assert result["features"]["workshops"] is True
        assert result["features"]["exhibitions"] is True
        assert result["features"]["spectator_economy"] is False  # No token pool
        assert result["features"]["festivals"] is False  # No festival manager


# === Affordances Tests ===


class TestAffordances:
    """Tests for affordances based on observer archetype."""

    def test_spectator_has_read_affordances(
        self,
        node: ForgeNode,
    ):
        """Spectators have read-only affordances."""
        affordances = node._get_affordances_for_archetype("spectator")

        assert "workshop.list" in affordances
        assert "workshop.get" in affordances
        assert "exhibition.view" in affordances
        # Should NOT have write affordances
        assert "workshop.create" not in affordances
        assert "contribute" not in affordances

    def test_artisan_has_create_affordances(
        self,
        node: ForgeNode,
    ):
        """Artisans can join and contribute."""
        affordances = node._get_affordances_for_archetype("artisan")

        assert "workshop.join" in affordances
        assert "contribute" in affordances
        # But not management
        assert "workshop.create" not in affordances

    def test_curator_has_management_affordances(
        self,
        node: ForgeNode,
    ):
        """Curators can manage workshops and exhibitions."""
        affordances = node._get_affordances_for_archetype("curator")

        assert "workshop.create" in affordances
        assert "workshop.end" in affordances
        assert "exhibition.create" in affordances
        assert "exhibition.open" in affordances
        assert "gallery.add" in affordances

    def test_developer_has_all_affordances(
        self,
        node: ForgeNode,
    ):
        """Developers have full access."""
        affordances = node._get_affordances_for_archetype("developer")

        assert "workshop.create" in affordances
        assert "workshop.end" in affordances
        assert "contribute" in affordances
        assert "exhibition.create" in affordances
        assert "gallery.add" in affordances


# === Manifest Tests ===


class TestManifest:
    """Tests for ForgeNode.manifest()."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """Manifest returns forge status."""
        result = await node.manifest(spectator_observer)

        assert isinstance(result, ForgeManifestRendering)
        assert result.status.total_workshops == 5
        assert result.status.active_workshops == 2

    @pytest.mark.asyncio
    async def test_manifest_rendering_to_dict(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """Manifest rendering produces correct dict."""
        result = await node.manifest(spectator_observer)
        data = result.to_dict()

        assert data["type"] == "forge_manifest"
        assert data["total_workshops"] == 5
        assert data["active_workshops"] == 2
        assert data["total_artisans"] == 10

    @pytest.mark.asyncio
    async def test_manifest_rendering_to_text(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """Manifest rendering produces readable text."""
        result = await node.manifest(spectator_observer)
        text = result.to_text()

        assert "Forge Status" in text
        assert "Workshops:" in text
        assert "2/5 active" in text


# === Workshop Tests ===


class TestWorkshopOperations:
    """Tests for workshop CRUD operations."""

    @pytest.mark.asyncio
    async def test_workshop_list(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Workshop list returns workshops."""
        mock_persistence.list_workshops.return_value = [
            WorkshopView(
                id="ws-1",
                name="Poetry Circle",
                description="Haiku workshop",
                theme="nature",
                is_active=True,
                artisan_count=3,
                contribution_count=10,
                started_at="2025-01-01T00:00:00",
                created_at="2025-01-01T00:00:00",
            )
        ]

        result = await node._workshop_list(spectator_observer)

        assert isinstance(result, WorkshopListRendering)
        assert len(result.workshops) == 1
        assert result.workshops[0].name == "Poetry Circle"

    @pytest.mark.asyncio
    async def test_workshop_get_found(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Workshop get returns found workshop."""
        mock_persistence.get_workshop.return_value = WorkshopView(
            id="ws-1",
            name="Poetry Circle",
            description="Haiku workshop",
            theme="nature",
            is_active=True,
            artisan_count=3,
            contribution_count=10,
            started_at="2025-01-01T00:00:00",
            created_at="2025-01-01T00:00:00",
        )

        result = await node._workshop_get(spectator_observer, "ws-1")

        assert isinstance(result, WorkshopRendering)
        assert result.workshop.id == "ws-1"

    @pytest.mark.asyncio
    async def test_workshop_get_not_found(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Workshop get returns error when not found."""
        mock_persistence.get_workshop.return_value = None

        result = await node._workshop_get(spectator_observer, "not-found")

        assert isinstance(result, BasicRendering)
        assert "not found" in result.to_text().lower()

    @pytest.mark.asyncio
    async def test_workshop_create(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        curator_observer: Observer,
    ):
        """Workshop create returns new workshop."""
        mock_persistence.create_workshop.return_value = WorkshopView(
            id="ws-new",
            name="New Workshop",
            description="Test description",
            theme="test",
            is_active=True,
            artisan_count=0,
            contribution_count=0,
            started_at="2025-01-01T00:00:00",
            created_at="2025-01-01T00:00:00",
        )

        result = await node._workshop_create(
            curator_observer,
            name="New Workshop",
            theme="test",
        )

        assert isinstance(result, WorkshopRendering)
        assert result.workshop.id == "ws-new"

    @pytest.mark.asyncio
    async def test_workshop_end(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        curator_observer: Observer,
    ):
        """Workshop end succeeds."""
        mock_persistence.end_workshop.return_value = True

        result = await node._workshop_end(curator_observer, "ws-1")

        assert isinstance(result, BasicRendering)
        assert "ended" in result.to_text().lower()


# === Artisan Tests ===


class TestArtisanOperations:
    """Tests for artisan operations."""

    @pytest.mark.asyncio
    async def test_artisan_list(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Artisan list returns artisans in workshop."""
        mock_persistence.list_artisans.return_value = [
            ArtisanView(
                id="art-1",
                workshop_id="ws-1",
                name="Blake",
                specialty="poet",
                style="romantic",
                is_active=True,
                contribution_count=5,
                created_at="2025-01-01T00:00:00",
            )
        ]

        result = await node._artisan_list(spectator_observer, "ws-1")

        assert isinstance(result, ArtisanListRendering)
        assert len(result.artisans) == 1
        assert result.artisans[0].name == "Blake"

    @pytest.mark.asyncio
    async def test_artisan_join(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        artisan_observer: Observer,
    ):
        """Artisan join adds artisan to workshop."""
        mock_persistence.add_artisan.return_value = ArtisanView(
            id="art-new",
            workshop_id="ws-1",
            name="New Artist",
            specialty="painter",
            style=None,
            is_active=True,
            contribution_count=0,
            created_at="2025-01-01T00:00:00",
        )

        result = await node._artisan_join(
            artisan_observer,
            workshop_id="ws-1",
            name="New Artist",
            specialty="painter",
        )

        assert isinstance(result, ArtisanRendering)
        assert result.artisan.name == "New Artist"


# === Contribution Tests ===


class TestContributionOperations:
    """Tests for contribution operations."""

    @pytest.mark.asyncio
    async def test_contribute(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        artisan_observer: Observer,
    ):
        """Contribute adds contribution to workshop."""
        mock_persistence.contribute.return_value = ContributionView(
            id="contrib-1",
            artisan_id="art-1",
            artisan_name="Blake",
            contribution_type="draft",
            content_type="text",
            content="A haiku about snow...",
            prompt="Write about winter",
            inspiration=None,
            created_at="2025-01-01T00:00:00",
        )

        result = await node._contribute(
            artisan_observer,
            artisan_id="art-1",
            content="A haiku about snow...",
            prompt="Write about winter",
        )

        assert isinstance(result, ContributionRendering)
        assert result.contribution.artisan_name == "Blake"

    @pytest.mark.asyncio
    async def test_contribution_list(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Contribution list returns contributions."""
        mock_persistence.list_contributions.return_value = [
            ContributionView(
                id="contrib-1",
                artisan_id="art-1",
                artisan_name="Blake",
                contribution_type="draft",
                content_type="text",
                content="A haiku about snow...",
                prompt="Write about winter",
                inspiration=None,
                created_at="2025-01-01T00:00:00",
            )
        ]

        result = await node._contribution_list(spectator_observer, workshop_id="ws-1")

        assert isinstance(result, ContributionListRendering)
        assert len(result.contributions) == 1


# === Exhibition Tests ===


class TestExhibitionOperations:
    """Tests for exhibition operations."""

    @pytest.mark.asyncio
    async def test_exhibition_create(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        curator_observer: Observer,
    ):
        """Exhibition create returns new exhibition."""
        mock_persistence.create_exhibition.return_value = ExhibitionView(
            id="exhibit-1",
            workshop_id="ws-1",
            name="Winter Poetry",
            description="Collection of winter haiku",
            curator_notes="Selected best works",
            is_open=False,
            view_count=0,
            item_count=0,
            opened_at=None,
            created_at="2025-01-01T00:00:00",
        )

        result = await node._exhibition_create(
            curator_observer,
            workshop_id="ws-1",
            name="Winter Poetry",
        )

        assert isinstance(result, ExhibitionRendering)
        assert result.exhibition.name == "Winter Poetry"

    @pytest.mark.asyncio
    async def test_exhibition_open(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        curator_observer: Observer,
    ):
        """Exhibition open succeeds."""
        mock_persistence.open_exhibition.return_value = True

        result = await node._exhibition_open(curator_observer, "exhibit-1")

        assert isinstance(result, BasicRendering)
        assert "opened" in result.to_text().lower()

    @pytest.mark.asyncio
    async def test_exhibition_view(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Exhibition view increments count and returns details."""
        mock_persistence.view_exhibition.return_value = ExhibitionView(
            id="exhibit-1",
            workshop_id="ws-1",
            name="Winter Poetry",
            description="Collection of winter haiku",
            curator_notes=None,
            is_open=True,
            view_count=42,
            item_count=5,
            opened_at="2025-01-01T00:00:00",
            created_at="2025-01-01T00:00:00",
        )

        result = await node._exhibition_view(spectator_observer, "exhibit-1")

        assert isinstance(result, ExhibitionRendering)
        assert result.exhibition.view_count == 42


# === Gallery Tests ===


class TestGalleryOperations:
    """Tests for gallery operations."""

    @pytest.mark.asyncio
    async def test_gallery_list(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        spectator_observer: Observer,
    ):
        """Gallery list returns items."""
        mock_persistence.list_gallery_items.return_value = [
            GalleryItemView(
                id="item-1",
                exhibition_id="exhibit-1",
                artifact_type="text",
                artifact_content="A beautiful haiku...",
                title="Winter Snow",
                description="A meditation on snowfall",
                display_order=1,
                artisan_ids=["art-1"],
            )
        ]

        result = await node._gallery_list(spectator_observer, "exhibit-1")

        assert isinstance(result, GalleryListRendering)
        assert len(result.items) == 1
        assert result.items[0].title == "Winter Snow"

    @pytest.mark.asyncio
    async def test_gallery_add(
        self,
        node: ForgeNode,
        mock_persistence: AsyncMock,
        curator_observer: Observer,
    ):
        """Gallery add adds item to exhibition."""
        mock_persistence.add_to_gallery.return_value = GalleryItemView(
            id="item-new",
            exhibition_id="exhibit-1",
            artifact_type="text",
            artifact_content="New content",
            title="New Item",
            description=None,
            display_order=2,
            artisan_ids=[],
        )

        result = await node._gallery_add(
            curator_observer,
            exhibition_id="exhibit-1",
            artifact_content="New content",
            title="New Item",
        )

        assert isinstance(result, GalleryItemRendering)
        assert result.item.title == "New Item"


# === Rendering Tests ===


class TestRenderings:
    """Tests for rendering output formats."""

    def test_workshop_rendering_to_dict(self):
        """WorkshopRendering.to_dict produces correct format."""
        workshop = WorkshopView(
            id="ws-1",
            name="Test",
            description="Desc",
            theme="theme",
            is_active=True,
            artisan_count=2,
            contribution_count=5,
            started_at="2025-01-01T00:00:00",
            created_at="2025-01-01T00:00:00",
        )
        rendering = WorkshopRendering(workshop)
        data = rendering.to_dict()

        assert data["type"] == "workshop"
        assert data["id"] == "ws-1"
        assert data["name"] == "Test"
        assert data["is_active"] is True

    def test_workshop_rendering_to_text(self):
        """WorkshopRendering.to_text produces readable text."""
        workshop = WorkshopView(
            id="ws-1",
            name="Test Workshop",
            description="Desc",
            theme="theme",
            is_active=True,
            artisan_count=2,
            contribution_count=5,
            started_at="2025-01-01T00:00:00",
            created_at="2025-01-01T00:00:00",
        )
        rendering = WorkshopRendering(workshop)
        text = rendering.to_text()

        assert "Test Workshop" in text
        assert "active" in text
        assert "Artisans: 2" in text

    def test_gallery_list_rendering_empty(self):
        """GalleryListRendering handles empty list."""
        rendering = GalleryListRendering([])
        text = rendering.to_text()

        assert "No items" in text


# === Token Economy Tests (Optional Feature) ===


class TestTokenEconomy:
    """Tests for spectator economy when enabled."""

    @pytest.fixture
    def token_pool(self):
        """Create a mock token pool."""
        pool = MagicMock()
        pool._pool = MagicMock()
        return pool

    @pytest.fixture
    def node_with_tokens(
        self,
        mock_persistence: AsyncMock,
        token_pool: MagicMock,
    ) -> ForgeNode:
        """Create node with token pool enabled."""
        return ForgeNode(
            forge_persistence=mock_persistence,
            token_pool=token_pool,
        )

    def test_spectator_gets_token_affordances(
        self,
        node_with_tokens: ForgeNode,
    ):
        """Spectators get token affordances when pool is enabled."""
        affordances = node_with_tokens._get_affordances_for_archetype("spectator")

        assert "tokens.manifest" in affordances
        assert "bid.submit" in affordances

    @pytest.mark.asyncio
    async def test_handle_shows_economy_enabled(
        self,
        node_with_tokens: ForgeNode,
        spectator_observer: Observer,
    ):
        """get_handle_info shows spectator economy as enabled."""
        result = await node_with_tokens.get_handle_info(spectator_observer)

        assert result["features"]["spectator_economy"] is True

    @pytest.mark.asyncio
    async def test_tokens_manifest_without_pool(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """Token manifest returns error when pool not enabled."""
        result = await node._tokens_manifest(spectator_observer)

        assert isinstance(result, BasicRendering)
        assert "not enabled" in result.to_text().lower()


# === Festival Tests (Optional Feature) ===


class TestFestivals:
    """Tests for festivals when enabled."""

    @pytest.fixture
    def festival_manager(self):
        """Create a mock festival manager."""
        return MagicMock()

    @pytest.fixture
    def node_with_festivals(
        self,
        mock_persistence: AsyncMock,
        festival_manager: MagicMock,
    ) -> ForgeNode:
        """Create node with festivals enabled."""
        return ForgeNode(
            forge_persistence=mock_persistence,
            festival_manager=festival_manager,
        )

    @pytest.mark.asyncio
    async def test_handle_shows_festivals_enabled(
        self,
        node_with_festivals: ForgeNode,
        spectator_observer: Observer,
    ):
        """get_handle_info shows festivals as enabled."""
        result = await node_with_festivals.get_handle_info(spectator_observer)

        assert result["features"]["festivals"] is True

    @pytest.mark.asyncio
    async def test_festival_list_without_manager(
        self,
        node: ForgeNode,
        spectator_observer: Observer,
    ):
        """Festival list returns error when not enabled."""
        result = await node._festival_list(spectator_observer)

        assert isinstance(result, BasicRendering)
        assert "not enabled" in result.to_text().lower()
