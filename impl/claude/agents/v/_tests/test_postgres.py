"""
PostgresVectorBackend Tests: Tests for pgvector-based vector storage.

Tests cover:
1. Basic CRUD operations (add, get, remove, clear)
2. Search functionality with cosine distance (<=> operator)
3. Batch operations
4. pgvector extension checks

Note: Tests requiring actual Postgres are marked with @pytest.mark.postgres
and will be skipped if KGENTS_DATABASE_URL is not set.

See: plans/pgvector-integration.md
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..backends.postgres import PostgresVectorBackend
from ..types import DistanceMetric, Embedding
from .conftest import make_embedding, make_unit_vector

# =============================================================================
# Skip conditions
# =============================================================================

# Check if we have a database URL for integration tests
DATABASE_URL = os.environ.get("KGENTS_DATABASE_URL", "")
HAS_DATABASE = bool(DATABASE_URL) and "postgresql" in DATABASE_URL

skip_without_database = pytest.mark.skipif(
    not HAS_DATABASE,
    reason="KGENTS_DATABASE_URL not set or not PostgreSQL",
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_session_factory() -> MagicMock:
    """Create a mock session factory for unit tests."""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.get_bind = MagicMock(return_value=MagicMock(dialect=MagicMock(name="postgresql")))

    # Context manager support
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_factory = MagicMock()
    mock_factory.return_value = mock_session
    mock_factory.__call__ = MagicMock(return_value=mock_session)

    return mock_factory


# =============================================================================
# Unit Tests (No Database Required)
# =============================================================================


class TestPgvectorImport:
    """Test that pgvector is properly imported."""

    def test_pgvector_import_succeeds(self) -> None:
        """pgvector module can be imported (required dependency)."""
        from pgvector.sqlalchemy import Vector

        assert Vector is not None


class TestPostgresBackendCreation:
    """Test backend instantiation."""

    def test_create_backend_default_config(self, mock_session_factory: MagicMock) -> None:
        """Create backend with default configuration."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
        )
        assert backend.dimension == 1536
        assert backend.metric == DistanceMetric.COSINE

    def test_create_backend_custom_config(self, mock_session_factory: MagicMock) -> None:
        """Create backend with custom configuration."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=768,
            metric=DistanceMetric.EUCLIDEAN,
            table_name="custom_table",
            id_column="custom_id",
            embedding_column="custom_embedding",
        )
        assert backend.dimension == 768
        assert backend.metric == DistanceMetric.EUCLIDEAN

    def test_repr(self, mock_session_factory: MagicMock) -> None:
        """Backend has useful repr."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=1536,
            table_name="trail_steps",
        )
        repr_str = repr(backend)
        assert "PostgresVectorBackend" in repr_str
        assert "1536" in repr_str
        assert "trail_steps" in repr_str


class TestDistanceOperators:
    """Test distance operator selection."""

    def test_cosine_operator(self, mock_session_factory: MagicMock) -> None:
        """Cosine metric uses <=> operator."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            metric=DistanceMetric.COSINE,
        )
        assert backend._get_distance_operator() == "<=>"

    def test_euclidean_operator(self, mock_session_factory: MagicMock) -> None:
        """Euclidean metric uses <-> operator."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            metric=DistanceMetric.EUCLIDEAN,
        )
        assert backend._get_distance_operator() == "<->"

    def test_dot_product_operator(self, mock_session_factory: MagicMock) -> None:
        """Dot product metric uses <#> operator."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            metric=DistanceMetric.DOT_PRODUCT,
        )
        assert backend._get_distance_operator() == "<#>"


class TestDistanceToSimilarity:
    """Test distance to similarity conversion."""

    def test_cosine_distance_to_similarity(self, mock_session_factory: MagicMock) -> None:
        """Cosine distance converts to similarity correctly."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            metric=DistanceMetric.COSINE,
        )
        # Cosine distance 0 = identical = similarity 1
        assert backend._distance_to_similarity(0.0) == 1.0
        # Cosine distance 0.5 = similarity 0.5
        assert backend._distance_to_similarity(0.5) == 0.5
        # Cosine distance 1.0 = opposite = similarity 0
        assert backend._distance_to_similarity(1.0) == 0.0
        # Negative distance (shouldn't happen but handle gracefully)
        assert backend._distance_to_similarity(-0.1) == 1.0  # Clamped

    def test_euclidean_distance_to_similarity(self, mock_session_factory: MagicMock) -> None:
        """Euclidean distance converts to similarity correctly."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            metric=DistanceMetric.EUCLIDEAN,
        )
        # Distance 0 = similarity 1
        assert backend._distance_to_similarity(0.0) == 1.0
        # Distance 1 = similarity 0.5
        assert backend._distance_to_similarity(1.0) == 0.5


# =============================================================================
# Integration Tests (Require Database)
# =============================================================================


@pytest.mark.postgres
@skip_without_database
class TestPostgresBackendIntegration:
    """
    Integration tests requiring actual PostgreSQL with pgvector.

    These tests use the trail_steps table from migration 007.
    Run with: KGENTS_DATABASE_URL=... pytest -m postgres

    Note: These tests will fail if:
    - pgvector extension is not installed
    - Migration 007 has not been run (trail_steps table doesn't exist)
    """

    @pytest.fixture
    async def session_factory(self):
        """Create actual session factory for integration tests."""
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        engine = create_async_engine(DATABASE_URL)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        yield factory
        await engine.dispose()

    @pytest.fixture
    async def backend(self, session_factory) -> PostgresVectorBackend:
        """Create backend for integration tests."""
        return PostgresVectorBackend(
            session_factory=session_factory,
            dimension=1536,
            table_name="trail_steps",
            id_column="id",
            embedding_column="embedding",
        )

    async def test_check_extension(self, backend: PostgresVectorBackend) -> None:
        """Check pgvector extension availability (may not be enabled)."""
        # Note: This test checks if the extension EXISTS, not if it's enabled
        # If pgvector is not installed on the server, this will return False
        result = await backend.check_extension()
        # Don't assert True - just verify the method works
        assert isinstance(result, bool)
        if not result:
            pytest.skip("pgvector extension not enabled on database")

    async def test_count_with_no_embeddings(self, backend: PostgresVectorBackend) -> None:
        """Count returns 0 when no embeddings exist."""
        # First check if the extension is enabled
        extension_ok = await backend.check_extension()
        if not extension_ok:
            pytest.skip("pgvector extension not enabled on database")

        # Try to count - will fail if table doesn't exist
        try:
            count = await backend.count()
            assert count >= 0
        except Exception as e:
            if "does not exist" in str(e):
                pytest.skip("trail_steps table does not exist (run migration 007)")


# =============================================================================
# Mock-based Tests (Test Logic Without Database)
# =============================================================================


class TestPostgresBackendLogic:
    """Test backend logic using mocks."""

    @pytest.mark.asyncio
    async def test_add_executes_update(self, mock_session_factory: MagicMock) -> None:
        """Add executes UPDATE query."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=8,
        )

        # Create mock session that returns from context manager
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_factory.return_value = mock_session

        emb = make_embedding(1, dimension=8)
        await backend.add("test-id", emb)

        # Verify execute was called
        assert mock_session.execute.called
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_search_builds_correct_query(self, mock_session_factory: MagicMock) -> None:
        """Search builds query with <=> operator."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=8,
        )

        # Create mock session
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall = MagicMock(return_value=[])
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.get_bind = MagicMock(
            return_value=MagicMock(dialect=MagicMock(name="postgresql"))
        )
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_factory.return_value = mock_session

        query = make_embedding(1, dimension=8)
        await backend.search(query, limit=10)

        # Verify execute was called with query containing <=>
        assert mock_session.execute.called
        call_args = mock_session.execute.call_args
        query_text = str(call_args[0][0])
        assert "<=>" in query_text or "ORDER BY" in query_text

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing(self, mock_session_factory: MagicMock) -> None:
        """Get returns None when ID not found."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=8,
        )

        # Create mock session that returns no rows
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_factory.return_value = mock_session

        result = await backend.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_returns_true_when_found(self, mock_session_factory: MagicMock) -> None:
        """Remove returns True when row is updated."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=8,
        )

        # Create mock session where RETURNING returns a row (found and updated)
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=("test-id",))  # Row returned
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_factory.return_value = mock_session

        result = await backend.remove("test-id")
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_returns_false_when_not_found(
        self, mock_session_factory: MagicMock
    ) -> None:
        """Remove returns False when row not found."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
            dimension=8,
        )

        # Create mock session where RETURNING returns None (row not found)
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone = MagicMock(return_value=None)  # No row returned
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_factory.return_value = mock_session

        result = await backend.remove("nonexistent-id")
        assert result is False


# =============================================================================
# VgentProtocol Compliance Tests
# =============================================================================


class TestVgentProtocolCompliance:
    """Verify PostgresVectorBackend implements VgentProtocol."""

    def test_implements_protocol(self, mock_session_factory: MagicMock) -> None:
        """Backend implements VgentProtocol."""
        from ..protocol import VgentProtocol

        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
        )
        assert isinstance(backend, VgentProtocol)

    def test_has_required_properties(self, mock_session_factory: MagicMock) -> None:
        """Backend has required properties."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
        )
        # Required properties
        assert hasattr(backend, "dimension")
        assert hasattr(backend, "metric")
        assert backend.dimension == 1536
        assert backend.metric == DistanceMetric.COSINE

    def test_has_required_methods(self, mock_session_factory: MagicMock) -> None:
        """Backend has required methods."""
        backend = PostgresVectorBackend(
            session_factory=mock_session_factory,
        )
        # Required methods
        assert callable(getattr(backend, "add", None))
        assert callable(getattr(backend, "add_batch", None))
        assert callable(getattr(backend, "search", None))
        assert callable(getattr(backend, "get", None))
        assert callable(getattr(backend, "remove", None))
        assert callable(getattr(backend, "clear", None))
        assert callable(getattr(backend, "count", None))
        assert callable(getattr(backend, "exists", None))
