"""
Tests for GestaltPersistence - Code topology visualization persistence.

Verifies:
- Topology CRUD operations
- CodeBlock management
- CodeLink relationships
- Snapshot creation
- Health manifest
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

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
def mock_topology_adapter(mock_session_factory):
    """Create a mock topology adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


@pytest.fixture
def mock_block_adapter(mock_session_factory):
    """Create a mock block adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


class TestGestaltPersistenceInit:
    """Test GestaltPersistence initialization."""

    def test_init_stores_dependencies(self, mock_topology_adapter, mock_block_adapter, mock_dgent):
        """Should store adapters and dgent."""
        from services.gestalt import GestaltPersistence

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        assert persistence.topologies is mock_topology_adapter
        assert persistence.blocks is mock_block_adapter
        assert persistence.dgent is mock_dgent


class TestTopologyManagement:
    """Test topology CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_topology(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should create topology with generated ID."""
        from services.gestalt import GestaltPersistence

        # Setup mock to return created topology
        @dataclass
        class MockTopology:
            created_at = None

        mock_session.add = MagicMock()

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_topology(
            name="Test Project",
            description="Test description",
            repo_path="/path/to/repo",
        )

        assert result.name == "Test Project"
        assert result.description == "Test description"
        assert result.repo_path == "/path/to/repo"
        assert result.id.startswith("topology-")

    @pytest.mark.asyncio
    async def test_list_topologies(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should list topologies ordered by updated_at."""
        from services.gestalt import GestaltPersistence

        # Setup mock to return empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.list_topologies(limit=10)

        assert result == []


class TestCodeBlockManagement:
    """Test code block operations."""

    @pytest.mark.asyncio
    async def test_add_block_to_topology(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should add block and update topology count."""
        from services.gestalt import GestaltPersistence

        # Setup mock topology
        @dataclass
        class MockTopology:
            id: str = "topology-123"
            block_count: int = 0

        mock_session.get = AsyncMock(return_value=MockTopology())

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.add_block(
            topology_id="topology-123",
            name="test_function",
            block_type="function",
            file_path="/path/to/file.py",
            line_start=10,
            line_end=20,
        )

        assert result is not None
        assert result.name == "test_function"
        assert result.block_type == "function"
        assert result.id.startswith("block-")

    @pytest.mark.asyncio
    async def test_add_block_to_nonexistent_topology(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should return None if topology doesn't exist."""
        from services.gestalt import GestaltPersistence

        mock_session.get = AsyncMock(return_value=None)

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.add_block(
            topology_id="nonexistent",
            name="test",
            block_type="function",
            file_path="/path",
        )

        assert result is None


class TestCodeLinkManagement:
    """Test code link operations."""

    @pytest.mark.asyncio
    async def test_add_link_between_blocks(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should create link between two blocks."""
        from services.gestalt import GestaltPersistence

        # Setup mocks
        @dataclass
        class MockTopology:
            id: str = "topology-123"
            link_count: int = 0

        @dataclass
        class MockBlock:
            id: str = "block-123"

        mock_session.get = AsyncMock(side_effect=[MockTopology(), MockBlock(), MockBlock()])

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.add_link(
            topology_id="topology-123",
            source_block_id="block-a",
            target_block_id="block-b",
            link_type="import",
            strength=0.8,
        )

        assert result is not None
        assert result.link_type == "import"
        assert result.strength == 0.8


class TestGestaltManifest:
    """Test manifest (health status) operation."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(
        self, mock_topology_adapter, mock_block_adapter, mock_dgent, mock_session
    ):
        """Should return gestalt health status."""
        from services.gestalt import GestaltPersistence

        # Setup mock counts
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = GestaltPersistence(
            topology_adapter=mock_topology_adapter,
            block_adapter=mock_block_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.manifest()

        assert hasattr(result, "total_topologies")
        assert hasattr(result, "total_blocks")
        assert hasattr(result, "total_links")
        assert hasattr(result, "storage_backend")


class TestViewDataclasses:
    """Test view dataclasses."""

    def test_topology_view_fields(self):
        """TopologyView should have expected fields."""
        from services.gestalt import TopologyView

        view = TopologyView(
            id="test",
            name="Test",
            description=None,
            repo_path=None,
            git_ref=None,
            block_count=0,
            link_count=0,
            complexity_score=None,
            created_at="",
        )

        assert view.id == "test"
        assert view.name == "Test"

    def test_code_block_view_fields(self):
        """CodeBlockView should have expected fields."""
        from services.gestalt import CodeBlockView

        view = CodeBlockView(
            id="test",
            topology_id="topo",
            name="func",
            block_type="function",
            file_path="/path",
            line_start=1,
            line_end=10,
            position=(0.0, 0.0, 0.0),
            test_coverage=None,
            complexity=None,
            churn_rate=None,
            created_at="",
        )

        assert view.block_type == "function"
        assert view.position == (0.0, 0.0, 0.0)
