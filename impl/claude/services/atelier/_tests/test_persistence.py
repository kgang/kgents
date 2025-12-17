"""
Tests for AtelierPersistence - Creative workshop fishbowl persistence.

Verifies:
- Workshop CRUD operations
- Artisan management
- Contribution tracking
- Exhibition and gallery management
- Health manifest
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.get = AsyncMock(return_value=None)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_session_factory(mock_session):
    """Create a mock session factory."""
    factory = AsyncMock()
    factory.__aenter__ = AsyncMock(return_value=mock_session)
    factory.__aexit__ = AsyncMock(return_value=None)
    return MagicMock(return_value=factory)


@pytest.fixture
def mock_dgent():
    """Create a mock D-gent."""
    dgent = AsyncMock()
    dgent.put = AsyncMock(return_value="datum-123")
    dgent.get = AsyncMock(return_value=None)
    return dgent


@pytest.fixture
def mock_workshop_adapter(mock_session_factory):
    """Create a mock workshop adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


@pytest.fixture
def mock_artisan_adapter(mock_session_factory):
    """Create a mock artisan adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


class TestAtelierPersistenceInit:
    """Test AtelierPersistence initialization."""

    def test_init_stores_dependencies(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent
    ):
        """Should store adapters and dgent."""
        from services.atelier import AtelierPersistence

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        assert persistence.workshops is mock_workshop_adapter
        assert persistence.artisans is mock_artisan_adapter
        assert persistence.dgent is mock_dgent


class TestWorkshopManagement:
    """Test workshop CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_workshop(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should create workshop with generated ID."""
        from services.atelier import AtelierPersistence

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_workshop(
            name="Poetry Circle",
            description="Collaborative poetry",
            theme="nature",
        )

        assert result.name == "Poetry Circle"
        assert result.theme == "nature"
        assert result.is_active is True
        assert result.id.startswith("workshop-")

    @pytest.mark.asyncio
    async def test_end_workshop(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should mark workshop as inactive."""
        from services.atelier import AtelierPersistence

        @dataclass
        class MockWorkshop:
            id: str = "workshop-123"
            is_active: bool = True
            ended_at = None

        mock_session.get = AsyncMock(return_value=MockWorkshop())

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.end_workshop("workshop-123")

        assert result is True


class TestArtisanManagement:
    """Test artisan operations."""

    @pytest.mark.asyncio
    async def test_add_artisan_to_workshop(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should add artisan to active workshop."""
        from services.atelier import AtelierPersistence

        @dataclass
        class MockWorkshop:
            id: str = "workshop-123"
            is_active: bool = True

        mock_session.get = AsyncMock(return_value=MockWorkshop())

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.add_artisan(
            workshop_id="workshop-123",
            name="Blake",
            specialty="poet",
            style="romantic",
        )

        assert result is not None
        assert result.name == "Blake"
        assert result.specialty == "poet"
        assert result.id.startswith("artisan-")

    @pytest.mark.asyncio
    async def test_add_artisan_to_inactive_workshop(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should reject artisan to inactive workshop."""
        from services.atelier import AtelierPersistence

        @dataclass
        class MockWorkshop:
            id: str = "workshop-123"
            is_active: bool = False

        mock_session.get = AsyncMock(return_value=MockWorkshop())

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.add_artisan(
            workshop_id="workshop-123",
            name="Blake",
            specialty="poet",
        )

        assert result is None


class TestContributions:
    """Test contribution operations."""

    @pytest.mark.asyncio
    async def test_contribute_stores_in_dgent(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should store contribution content in D-gent."""
        from services.atelier import AtelierPersistence

        @dataclass
        class MockArtisan:
            id: str = "artisan-123"
            name: str = "Blake"
            is_active: bool = True
            contribution_count: int = 0

        mock_session.get = AsyncMock(return_value=MockArtisan())

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.contribute(
            artisan_id="artisan-123",
            content="A poem about nature",
            content_type="text",
            contribution_type="draft",
        )

        assert result is not None
        assert result.content == "A poem about nature"
        mock_dgent.put.assert_called_once()


class TestExhibitions:
    """Test exhibition management."""

    @pytest.mark.asyncio
    async def test_create_exhibition(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should create exhibition for workshop."""
        from services.atelier import AtelierPersistence

        @dataclass
        class MockWorkshop:
            id: str = "workshop-123"

        mock_session.get = AsyncMock(return_value=MockWorkshop())

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_exhibition(
            workshop_id="workshop-123",
            name="Nature's Voice",
            description="Poems inspired by nature",
        )

        assert result is not None
        assert result.name == "Nature's Voice"
        assert result.is_open is False


class TestAtelierManifest:
    """Test manifest (health status) operation."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(
        self, mock_workshop_adapter, mock_artisan_adapter, mock_dgent, mock_session
    ):
        """Should return atelier health status."""
        from services.atelier import AtelierPersistence

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = AtelierPersistence(
            workshop_adapter=mock_workshop_adapter,
            artisan_adapter=mock_artisan_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.manifest()

        assert hasattr(result, "total_workshops")
        assert hasattr(result, "active_workshops")
        assert hasattr(result, "total_artisans")
        assert hasattr(result, "total_contributions")


class TestViewDataclasses:
    """Test view dataclasses."""

    def test_workshop_view_fields(self):
        """WorkshopView should have expected fields."""
        from services.atelier import WorkshopView

        view = WorkshopView(
            id="test",
            name="Test",
            description=None,
            theme=None,
            is_active=True,
            artisan_count=0,
            contribution_count=0,
            started_at=None,
            created_at="",
        )

        assert view.is_active is True

    def test_artisan_view_fields(self):
        """ArtisanView should have expected fields."""
        from services.atelier import ArtisanView

        view = ArtisanView(
            id="test",
            workshop_id="ws",
            name="Test",
            specialty="poet",
            style=None,
            is_active=True,
            contribution_count=0,
            created_at="",
        )

        assert view.specialty == "poet"
