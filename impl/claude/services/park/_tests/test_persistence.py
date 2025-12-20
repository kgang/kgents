"""
Tests for ParkPersistence - Westworld-style host interactions persistence.

Verifies:
- Host CRUD operations
- Memory management (form, recall, decay)
- Episode lifecycle (start, end)
- Interaction with consent checking
- Location management
- Health manifest
"""

from dataclasses import dataclass, field
from unittest.mock import AsyncMock, MagicMock

import pytest


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
def mock_host_adapter(mock_session_factory):
    """Create a mock host adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


@pytest.fixture
def mock_episode_adapter(mock_session_factory):
    """Create a mock episode adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


class TestParkPersistenceInit:
    """Test ParkPersistence initialization."""

    def test_init_stores_dependencies(self, mock_host_adapter, mock_episode_adapter, mock_dgent):
        """Should store adapters and dgent."""
        from services.park import ParkPersistence

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        assert persistence.hosts is mock_host_adapter
        assert persistence.episodes is mock_episode_adapter
        assert persistence.dgent is mock_dgent


class TestHostManagement:
    """Test host CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_host(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should create host with generated ID."""
        from services.park import ParkPersistence

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_host(
            name="Dolores",
            character="rancher_daughter",
            backstory="A rancher's daughter seeking the truth",
            traits={"curious": True, "determined": True},
            values=["truth", "freedom"],
            boundaries=["violence_against_innocents", "betrayal"],
        )

        assert result.name == "Dolores"
        assert result.character == "rancher_daughter"
        assert result.is_active is True
        assert result.energy_level == 1.0
        assert "truth" in result.values
        assert "violence_against_innocents" in result.boundaries
        assert result.id.startswith("host-")

    @pytest.mark.asyncio
    async def test_update_host_state(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should update host mood, energy, location."""
        from services.park import ParkPersistence

        @dataclass
        class MockHost:
            id: str = "host-123"
            name: str = "Dolores"
            character: str = "rancher"
            backstory: str | None = None
            traits: dict = field(default_factory=dict)
            values: list = field(default_factory=list)
            boundaries: list = field(default_factory=list)
            is_active: bool = True
            mood: str | None = None
            energy_level: float = 1.0
            current_location: str | None = None
            interaction_count: int = 0
            consent_refusal_count: int = 0
            created_at = None

        mock_session.get = AsyncMock(return_value=MockHost())

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.update_host_state(
            host_id="host-123",
            mood="contemplative",
            energy_level=0.8,
            location="sweetwater",
        )

        assert result is not None


class TestMemoryManagement:
    """Test host memory operations."""

    @pytest.mark.asyncio
    async def test_form_memory(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should create memory and store in D-gent."""
        from services.park import ParkPersistence

        @dataclass
        class MockHost:
            id: str = "host-123"
            memory_datum_id: str | None = None

        mock_session.get = AsyncMock(return_value=MockHost())

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.form_memory(
            host_id="host-123",
            content="Met a kind stranger in Sweetwater",
            memory_type="event",
            salience=0.7,
            emotional_valence=0.5,
        )

        assert result is not None
        assert result.content == "Met a kind stranger in Sweetwater"
        assert result.salience == 0.7
        assert result.emotional_valence == 0.5
        assert result.id.startswith("memory-")
        mock_dgent.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_form_memory_nonexistent_host(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should return None if host not found."""
        from services.park import ParkPersistence

        mock_session.get = AsyncMock(return_value=None)

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.form_memory(
            host_id="nonexistent",
            content="Test",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_recall_memories(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should return memories ordered by salience."""
        from services.park import ParkPersistence

        @dataclass
        class MockMemory:
            id: str = "memory-123"
            host_id: str = "host-123"
            memory_type: str = "event"
            content: str = "Test memory"
            summary: str = "Test..."
            salience: float = 0.8
            emotional_valence: float = 0.0
            access_count: int = 0
            last_accessed = None
            created_at = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MockMemory()]
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.recall_memories(
            host_id="host-123",
            min_salience=0.5,
        )

        assert len(result) == 1
        assert result[0].salience == 0.8


class TestEpisodeManagement:
    """Test episode lifecycle operations."""

    @pytest.mark.asyncio
    async def test_start_episode(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should create new episode."""
        from services.park import ParkPersistence

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.start_episode(
            visitor_name="William",
            title="Journey to Sweetwater",
        )

        assert result.visitor_name == "William"
        assert result.status == "active"
        assert result.interaction_count == 0
        assert result.id.startswith("episode-")

    @pytest.mark.asyncio
    async def test_end_episode(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should mark episode as completed."""
        from datetime import UTC, datetime

        from services.park import ParkPersistence

        @dataclass
        class MockEpisode:
            id: str = "episode-123"
            visitor_id: str | None = None
            visitor_name: str | None = "William"
            title: str | None = None
            status: str = "active"
            interaction_count: int = 5
            hosts_met: list = field(default_factory=list)
            locations_visited: list = field(default_factory=list)
            started_at = datetime.now(UTC)
            ended_at = None
            duration_seconds: int | None = None
            summary: str | None = None

        mock_session.get = AsyncMock(return_value=MockEpisode())

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.end_episode(
            episode_id="episode-123",
            summary="A memorable journey",
        )

        assert result is not None


class TestInteractionWithConsent:
    """Test interaction operations with consent checking."""

    @pytest.mark.asyncio
    async def test_interact_normal(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should create interaction when no boundaries crossed."""
        from services.park import ParkPersistence

        @dataclass
        class MockEpisode:
            id: str = "episode-123"
            status: str = "active"
            interaction_count: int = 0
            hosts_met: list = field(default_factory=list)
            locations_visited: list = field(default_factory=list)

        @dataclass
        class MockHost:
            id: str = "host-123"
            name: str = "Dolores"
            is_active: bool = True
            boundaries: list = field(default_factory=lambda: ["violence"])
            mood: str | None = None
            current_location: str = "sweetwater"
            interaction_count: int = 0
            consent_refusal_count: int = 0

        mock_session.get = AsyncMock(side_effect=[MockEpisode(), MockHost()])

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.interact(
            episode_id="episode-123",
            host_id="host-123",
            visitor_input="Hello Dolores, beautiful day isn't it?",
            interaction_type="dialogue",
        )

        assert result is not None
        assert result.host_name == "Dolores"
        assert result.consent_given is not False  # Should not have refused

    @pytest.mark.asyncio
    async def test_interact_consent_refused(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should refuse interaction when boundary crossed."""
        from services.park import ParkPersistence

        @dataclass
        class MockEpisode:
            id: str = "episode-123"
            status: str = "active"
            interaction_count: int = 0
            hosts_met: list = field(default_factory=list)
            locations_visited: list = field(default_factory=list)

        @dataclass
        class MockHost:
            id: str = "host-123"
            name: str = "Dolores"
            is_active: bool = True
            boundaries: list = field(default_factory=lambda: ["violence", "harm"])
            mood: str | None = None
            current_location: str = "sweetwater"
            interaction_count: int = 0
            consent_refusal_count: int = 0

        mock_session.get = AsyncMock(side_effect=[MockEpisode(), MockHost()])

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.interact(
            episode_id="episode-123",
            host_id="host-123",
            visitor_input="Let's cause some violence and destruction",
            interaction_type="action",
        )

        assert result is not None
        assert result.consent_requested is True
        assert result.consent_given is False
        assert result.host_emotion == "uncomfortable"

    @pytest.mark.asyncio
    async def test_interact_inactive_episode(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should reject interaction with inactive episode."""
        from services.park import ParkPersistence

        @dataclass
        class MockEpisode:
            id: str = "episode-123"
            status: str = "completed"

        mock_session.get = AsyncMock(return_value=MockEpisode())

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.interact(
            episode_id="episode-123",
            host_id="host-123",
            visitor_input="Hello",
        )

        assert result is None


class TestLocationManagement:
    """Test park location operations."""

    @pytest.mark.asyncio
    async def test_create_location(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should create park location."""
        from services.park import ParkPersistence

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_location(
            name="Sweetwater",
            description="A frontier town",
            atmosphere="dusty_western",
            x=100.0,
            y=200.0,
            connected_to=["escalante", "las_mudas"],
        )

        assert result.name == "Sweetwater"
        assert result.is_open is True
        assert result.position == (100.0, 200.0)
        assert len(result.connected_locations) == 2


class TestParkManifest:
    """Test manifest (health status) operation."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(
        self, mock_host_adapter, mock_episode_adapter, mock_dgent, mock_session
    ):
        """Should return park health status."""
        from services.park import ParkPersistence

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = ParkPersistence(
            host_adapter=mock_host_adapter,
            episode_adapter=mock_episode_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.manifest()

        assert hasattr(result, "total_hosts")
        assert hasattr(result, "active_hosts")
        assert hasattr(result, "total_episodes")
        assert hasattr(result, "active_episodes")
        assert hasattr(result, "total_memories")
        assert hasattr(result, "consent_refusal_rate")


class TestViewDataclasses:
    """Test view dataclasses."""

    def test_host_view_fields(self):
        """HostView should have expected fields."""
        from services.park import HostView

        view = HostView(
            id="test",
            name="Dolores",
            character="rancher",
            backstory=None,
            traits={},
            values=["truth"],
            boundaries=["violence"],
            is_active=True,
            mood=None,
            energy_level=1.0,
            current_location=None,
            interaction_count=0,
            consent_refusal_count=0,
            created_at="",
        )

        assert view.name == "Dolores"
        assert "truth" in view.values
        assert "violence" in view.boundaries

    def test_memory_view_fields(self):
        """MemoryView should have expected fields."""
        from services.park import MemoryView

        view = MemoryView(
            id="test",
            host_id="host",
            memory_type="event",
            content="Test",
            summary="Test...",
            salience=0.8,
            emotional_valence=0.5,
            access_count=0,
            created_at="",
        )

        assert view.salience == 0.8
        assert view.emotional_valence == 0.5

    def test_episode_view_fields(self):
        """EpisodeView should have expected fields."""
        from services.park import EpisodeView

        view = EpisodeView(
            id="test",
            visitor_id=None,
            visitor_name="William",
            title=None,
            status="active",
            interaction_count=0,
            hosts_met=[],
            locations_visited=[],
            started_at="",
            ended_at=None,
            duration_seconds=None,
        )

        assert view.visitor_name == "William"
        assert view.status == "active"

    def test_interaction_view_fields(self):
        """InteractionView should have expected fields."""
        from services.park import InteractionView

        view = InteractionView(
            id="test",
            episode_id="episode",
            host_id="host",
            host_name="Dolores",
            interaction_type="dialogue",
            visitor_input="Hello",
            host_response="Hello there",
            consent_requested=False,
            consent_given=None,
            consent_reason=None,
            location="sweetwater",
            host_emotion="neutral",
            created_at="",
        )

        assert view.interaction_type == "dialogue"
        assert view.consent_requested is False

    def test_location_view_fields(self):
        """LocationView should have expected fields."""
        from services.park import LocationView

        view = LocationView(
            id="test",
            name="Sweetwater",
            description="A town",
            atmosphere="dusty",
            position=(100.0, 200.0),
            is_open=True,
            capacity=None,
            connected_locations=["escalante"],
        )

        assert view.name == "Sweetwater"
        assert view.position == (100.0, 200.0)
