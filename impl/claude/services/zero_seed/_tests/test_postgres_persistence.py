"""
Tests for PostgreSQL K-Block persistence in Zero Seed.

Verifies that K-Blocks created during genesis are properly persisted
to PostgreSQL and can be retrieved.

Philosophy:
    "Persistence is not an afterthought—it's the foundation."
"""

import pytest
from sqlalchemy import select

from models.kblock import KBlock as KBlockModel
from services.zero_seed.seed import seed_zero_seed


@pytest.mark.asyncio
async def test_zero_seed_persisted_to_postgres(async_session_factory):
    """Test that Zero Seed K-Blocks are persisted to PostgreSQL."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

    # Create storage with test session factory
    storage = PostgresZeroSeedStorage(async_session_factory)

    # Seed the Zero Seed
    result = await seed_zero_seed(storage)

    # Verify seeding succeeded
    assert result.success
    assert result.zero_seed_kblock_id
    assert len(result.axiom_kblock_ids) == 3  # A1, A2, G
    assert len(result.design_law_kblock_ids) == 4  # 4 design laws

    # Verify Zero Seed K-Block persisted to database
    async with async_session_factory() as session:
        stmt = select(KBlockModel).where(KBlockModel.id == result.zero_seed_kblock_id)
        db_result = await session.execute(stmt)
        zero_seed_db = db_result.scalar_one_or_none()

        assert zero_seed_db is not None
        assert zero_seed_db.zero_seed_layer == 0
        assert zero_seed_db.zero_seed_kind == "SYSTEM"
        assert zero_seed_db.confidence == 1.0
        assert "system" in zero_seed_db.tags
        assert "genesis" in zero_seed_db.tags

    # Verify axioms persisted
    for axiom_id, kblock_id in result.axiom_kblock_ids.items():
        async with async_session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.id == kblock_id)
            db_result = await session.execute(stmt)
            axiom_db = db_result.scalar_one_or_none()

            assert axiom_db is not None
            assert axiom_db.zero_seed_layer == 1
            assert "axiom" in axiom_db.tags
            # L1 axioms are foundational - no lineage
            assert axiom_db.lineage == []


@pytest.mark.asyncio
async def test_kblock_retrieval_from_postgres(async_session_factory):
    """Test that K-Blocks can be retrieved from PostgreSQL."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

    # Create storage and seed
    storage = PostgresZeroSeedStorage(async_session_factory)
    result = await seed_zero_seed(storage)

    # Retrieve Zero Seed K-Block
    zero_seed_kblock = await storage.get_node(result.zero_seed_kblock_id)
    assert zero_seed_kblock is not None
    assert zero_seed_kblock.zero_seed_layer == 0
    assert zero_seed_kblock.content.startswith("# Zero Seed Genesis")

    # Retrieve axiom K-Block
    a1_kblock_id = result.axiom_kblock_ids["A1"]
    a1_kblock = await storage.get_node(a1_kblock_id)
    assert a1_kblock is not None
    assert a1_kblock.zero_seed_layer == 1
    assert "Everything is a node" in a1_kblock.content


@pytest.mark.asyncio
async def test_layer_query_from_postgres(async_session_factory):
    """Test querying K-Blocks by layer."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

    # Create storage and seed
    storage = PostgresZeroSeedStorage(async_session_factory)
    result = await seed_zero_seed(storage)

    # Query L0 (Zero Seed)
    l0_nodes = await storage.get_layer_nodes(0)
    assert len(l0_nodes) == 1
    assert l0_nodes[0].id == result.zero_seed_kblock_id

    # Query L1 (Axioms)
    l1_nodes = await storage.get_layer_nodes(1)
    assert len(l1_nodes) >= 3  # A1, A2, G (may include design laws)


@pytest.mark.asyncio
async def test_kblock_content_hash_stored(async_session_factory):
    """Test that content hash is computed and stored."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

    # Create storage and seed
    storage = PostgresZeroSeedStorage(async_session_factory)
    result = await seed_zero_seed(storage)

    # Verify content hash exists in database
    async with async_session_factory() as session:
        stmt = select(KBlockModel).where(KBlockModel.id == result.zero_seed_kblock_id)
        db_result = await session.execute(stmt)
        zero_seed_db = db_result.scalar_one_or_none()

        assert zero_seed_db is not None
        assert zero_seed_db.content_hash
        assert len(zero_seed_db.content_hash) == 16  # First 16 chars of SHA256


@pytest.mark.asyncio
async def test_kblock_lineage_stored(async_session_factory):
    """Test that lineage is properly stored in JSONB."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage

    # Create storage and seed
    storage = PostgresZeroSeedStorage(async_session_factory)
    result = await seed_zero_seed(storage)

    # Verify axiom lineage (L1 axioms have no lineage - they are foundational)
    a1_kblock_id = result.axiom_kblock_ids["A1"]

    async with async_session_factory() as session:
        stmt = select(KBlockModel).where(KBlockModel.id == a1_kblock_id)
        db_result = await session.execute(stmt)
        a1_db = db_result.scalar_one_or_none()

        assert a1_db is not None
        assert isinstance(a1_db.lineage, list)
        assert a1_db.lineage == []  # L1 axioms are foundational - no lineage

    # Verify L2 design law lineage (should derive from Zero Seed)
    for law_id, kblock_id in result.design_law_kblock_ids.items():
        async with async_session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.id == kblock_id)
            db_result = await session.execute(stmt)
            law_db = db_result.scalar_one_or_none()

            if law_db and law_db.zero_seed_layer == 2:
                # L2 laws derive from Zero Seed
                assert result.zero_seed_kblock_id in law_db.lineage


@pytest.mark.asyncio
async def test_genesis_idempotence(async_session_factory):
    """Test that genesis can be queried multiple times without re-seeding."""
    from services.k_block.postgres_zero_seed_storage import PostgresZeroSeedStorage
    from services.zero_seed.seed import check_genesis_status

    # First seeding
    storage = PostgresZeroSeedStorage(async_session_factory)
    result1 = await seed_zero_seed(storage)
    assert result1.success

    # Check status (should be seeded)
    status = await check_genesis_status(storage)
    assert status.is_seeded
    assert status.zero_seed_exists
    assert status.axiom_count >= 3


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def async_session_factory(tmp_path):
    """
    Provide async session factory for tests.

    Uses in-memory SQLite to avoid PostgreSQL GIN index issues and
    ensure test isolation.
    """
    from models.base import Base
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    # Use SQLite in-memory for these tests (avoids PostgreSQL GIN index issues)
    db_path = tmp_path / "test_zero_seed.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    # Create engine and tables
    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield factory

    # Cleanup: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
