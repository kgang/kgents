"""
Tests for Schema Neurogenesis: Self-Evolving Database Schema.

Tests cover:
- Type inference from JSON values
- Pattern cluster detection
- Migration proposal generation
- Approval/rejection workflow
- SQL generation
"""

from __future__ import annotations

import pytest

from ..neurogenesis import (
    ColumnType,
    MigrationAction,
    MigrationProposal,
    MockSchemaIntrospector,
    NeurogenesisConfig,
    PatternCluster,
    SchemaNeurogenesis,
    TypeInferrer,
    create_schema_neurogenesis,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def introspector() -> MockSchemaIntrospector:
    """Create a mock introspector for testing."""
    return MockSchemaIntrospector(json_columns=[("events", "data"), ("users", "preferences")])


@pytest.fixture
def neurogenesis(introspector: MockSchemaIntrospector) -> SchemaNeurogenesis:
    """Create a SchemaNeurogenesis for testing."""
    return SchemaNeurogenesis(
        introspector=introspector,
        config=NeurogenesisConfig(
            sample_limit=100,
            min_sample_size=5,
            column_threshold=0.8,
        ),
    )


# =============================================================================
# NeurogenesisConfig Tests
# =============================================================================


class TestNeurogenesisConfig:
    """Tests for NeurogenesisConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = NeurogenesisConfig()
        assert config.sample_limit == 100
        assert config.min_sample_size == 10
        assert config.column_threshold == 0.8
        assert config.max_proposals_per_run == 10

    def test_from_dict(self) -> None:
        """Config can be created from dict."""
        data = {
            "sample_limit": 200,
            "min_sample_size": 5,
            "column_threshold": 0.9,
        }
        config = NeurogenesisConfig.from_dict(data)
        assert config.sample_limit == 200
        assert config.min_sample_size == 5
        assert config.column_threshold == 0.9

    def test_from_dict_uses_defaults(self) -> None:
        """Config uses defaults for missing keys."""
        config = NeurogenesisConfig.from_dict({})
        assert config.sample_limit == 100
        assert config.column_threshold == 0.8


# =============================================================================
# TypeInferrer Tests
# =============================================================================


class TestTypeInferrer:
    """Tests for type inference."""

    def test_infer_integer(self) -> None:
        """Infers INTEGER from int values."""
        values = [1, 2, 3, 4, 5]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.INTEGER
        assert confidence == 1.0

    def test_infer_real(self) -> None:
        """Infers REAL from float values."""
        values = [1.1, 2.2, 3.3, 4.4, 5.5]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.REAL
        assert confidence == 1.0

    def test_infer_text(self) -> None:
        """Infers TEXT from string values."""
        values = ["a", "b", "c", "d", "e"]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.TEXT
        assert confidence == 1.0

    def test_infer_boolean(self) -> None:
        """Infers BOOLEAN from bool values."""
        values = [True, False, True, True, False]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.BOOLEAN
        assert confidence == 1.0

    def test_infer_timestamp(self) -> None:
        """Infers TIMESTAMP from ISO date strings."""
        values = [
            "2024-01-01T00:00:00",
            "2024-01-02T12:00:00",
            "2024-01-03T18:30:00Z",
        ]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.TIMESTAMP
        assert confidence == 1.0

    def test_infer_json(self) -> None:
        """Infers JSON from dict/list values."""
        values = [{"a": 1}, {"b": 2}, [1, 2, 3]]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.JSON
        assert confidence == 1.0

    def test_infer_mixed_types(self) -> None:
        """Handles mixed types with lower confidence."""
        values = [1, "two", 3, "four", 5]
        inferred, confidence = TypeInferrer.infer_type(values)
        # Should pick most common type
        assert inferred in (ColumnType.INTEGER, ColumnType.TEXT)
        assert confidence < 1.0

    def test_infer_empty_list(self) -> None:
        """Handles empty list."""
        inferred, confidence = TypeInferrer.infer_type([])
        assert inferred == ColumnType.UNKNOWN
        assert confidence == 0.0

    def test_infer_all_none(self) -> None:
        """Handles all None values."""
        values = [None, None, None]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.UNKNOWN
        assert confidence == 0.0

    def test_infer_with_nulls(self) -> None:
        """Handles mixed None and real values."""
        values = [1, None, 2, None, 3]
        inferred, confidence = TypeInferrer.infer_type(values)
        assert inferred == ColumnType.INTEGER
        assert confidence == 1.0  # 3/3 non-null are INTEGER


# =============================================================================
# MigrationProposal Tests
# =============================================================================


class TestMigrationProposal:
    """Tests for migration proposals."""

    def test_create_proposal(self) -> None:
        """Can create a migration proposal."""
        proposal = MigrationProposal(
            proposal_id="p-001",
            action=MigrationAction.ADD_COLUMN,
            table_name="events",
            column_name="user_id",
            column_type=ColumnType.TEXT,
            source_column="data",
            confidence=0.95,
            sample_count=100,
            reasoning="Key 'user_id' appears in 95% of samples",
        )
        assert proposal.proposal_id == "p-001"
        assert proposal.approved is False
        assert proposal.executed is False

    def test_to_sql_add_column(self) -> None:
        """Generates SQL for ADD_COLUMN."""
        proposal = MigrationProposal(
            proposal_id="p-001",
            action=MigrationAction.ADD_COLUMN,
            table_name="events",
            column_name="user_id",
            column_type=ColumnType.TEXT,
            source_column=None,
            confidence=0.95,
            sample_count=100,
            reasoning="Test",
        )
        sql = proposal.to_sql()
        assert sql == "ALTER TABLE events ADD COLUMN user_id TEXT"

    def test_to_sql_add_index(self) -> None:
        """Generates SQL for ADD_INDEX."""
        proposal = MigrationProposal(
            proposal_id="p-001",
            action=MigrationAction.ADD_INDEX,
            table_name="events",
            column_name="user_id",
            column_type=None,
            source_column=None,
            confidence=0.95,
            sample_count=100,
            reasoning="Test",
        )
        sql = proposal.to_sql()
        assert sql == "CREATE INDEX idx_events_user_id ON events(user_id)"

    def test_to_sql_unsupported(self) -> None:
        """Returns None for unsupported actions."""
        proposal = MigrationProposal(
            proposal_id="p-001",
            action=MigrationAction.ADD_TABLE,
            table_name="new_table",
            column_name=None,
            column_type=None,
            source_column=None,
            confidence=0.95,
            sample_count=100,
            reasoning="Test",
        )
        assert proposal.to_sql() is None


# =============================================================================
# PatternCluster Tests
# =============================================================================


class TestPatternCluster:
    """Tests for pattern clusters."""

    def test_create_cluster(self) -> None:
        """Can create a pattern cluster."""
        cluster = PatternCluster(
            cluster_id="c-001",
            key_pattern=frozenset(["user_id", "timestamp", "event_type"]),
            occurrence_count=95,
            type_signatures={
                "user_id": ColumnType.TEXT,
                "timestamp": ColumnType.TIMESTAMP,
                "event_type": ColumnType.TEXT,
            },
            sample_values={
                "user_id": ["u1", "u2", "u3"],
                "timestamp": ["2024-01-01T00:00:00"],
            },
            table_source="events.data",
        )
        assert len(cluster.key_pattern) == 3
        assert cluster.occurrence_count == 95


# =============================================================================
# MockSchemaIntrospector Tests
# =============================================================================


class TestMockSchemaIntrospector:
    """Tests for mock introspector."""

    @pytest.mark.asyncio
    async def test_get_json_columns(self) -> None:
        """Returns configured JSON columns."""
        introspector = MockSchemaIntrospector(json_columns=[("t1", "c1"), ("t2", "c2")])
        columns = await introspector.get_json_columns()
        assert len(columns) == 2
        assert ("t1", "c1") in columns

    @pytest.mark.asyncio
    async def test_sample_column(self) -> None:
        """Returns added samples."""
        introspector = MockSchemaIntrospector()
        introspector.add_samples("events", "data", [{"a": 1}, {"a": 2}])
        samples = await introspector.sample_column("events", "data", 10)
        assert len(samples) == 2

    @pytest.mark.asyncio
    async def test_execute_migration(self) -> None:
        """Tracks executed migrations."""
        introspector = MockSchemaIntrospector()
        await introspector.execute_migration("ALTER TABLE x ADD COLUMN y TEXT")
        assert len(introspector.executed_migrations) == 1


# =============================================================================
# SchemaNeurogenesis Basic Tests
# =============================================================================


class TestSchemaNeurogenesisBasic:
    """Basic tests for SchemaNeurogenesis."""

    def test_creates_with_introspector(self, introspector: MockSchemaIntrospector) -> None:
        """Creates with introspector."""
        ng = SchemaNeurogenesis(introspector=introspector)
        assert ng.proposals == []
        assert ng.clusters == []

    def test_factory_function(self, introspector: MockSchemaIntrospector) -> None:
        """Factory function works."""
        ng = create_schema_neurogenesis(
            introspector=introspector,
            config_dict={"sample_limit": 50},
        )
        assert ng._config.sample_limit == 50

    def test_stats(self, neurogenesis: SchemaNeurogenesis) -> None:
        """Stats returns expected structure."""
        stats = neurogenesis.stats()
        assert "total_proposals" in stats
        assert "pending" in stats
        assert "approved" in stats
        assert "clusters_detected" in stats


# =============================================================================
# Analysis Tests
# =============================================================================


class TestAnalysis:
    """Tests for JSON analysis and proposal generation."""

    @pytest.mark.asyncio
    async def test_analyze_finds_patterns(self, introspector: MockSchemaIntrospector) -> None:
        """Analyze finds consistent patterns."""
        # Add samples with consistent keys
        samples = [
            {
                "user_id": f"u{i}",
                "event_type": "click",
                "timestamp": f"2024-01-0{i + 1}T00:00:00",
            }
            for i in range(10)
        ]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        # Should find patterns for user_id, event_type, timestamp
        assert len(proposals) > 0
        column_names = [p.column_name for p in proposals]
        assert "user_id" in column_names

    @pytest.mark.asyncio
    async def test_analyze_skips_sparse_keys(self, introspector: MockSchemaIntrospector) -> None:
        """Analyze skips keys that appear in few samples."""
        samples = [{"user_id": f"u{i}"} for i in range(10)]
        # Add rare key to only 2 samples
        samples[0]["rare_key"] = "value"
        samples[1]["rare_key"] = "value"
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(
                min_sample_size=5,
                column_threshold=0.8,
            ),
        )
        proposals = await ng.analyze()

        # Should not propose rare_key (only 20% occurrence)
        column_names = [p.column_name for p in proposals]
        assert "rare_key" not in column_names

    @pytest.mark.asyncio
    async def test_analyze_insufficient_samples(self, introspector: MockSchemaIntrospector) -> None:
        """Analyze returns empty for insufficient samples."""
        samples = [{"a": 1}, {"a": 2}]  # Only 2 samples
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=10),  # Requires 10
        )
        proposals = await ng.analyze()

        assert len(proposals) == 0

    @pytest.mark.asyncio
    async def test_analyze_skips_complex_blobs(self, introspector: MockSchemaIntrospector) -> None:
        """Analyze skips blobs with too many keys."""
        # Create samples with many keys
        samples = [
            {f"key_{j}": j for j in range(20)}  # 20 keys each
            for _ in range(10)
        ]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(
                min_sample_size=5,
                max_keys_for_column=10,  # Skip if > 10 keys
            ),
        )
        proposals = await ng.analyze()

        # Should skip complex structure
        assert len(proposals) == 0


# =============================================================================
# Approval Workflow Tests
# =============================================================================


class TestApprovalWorkflow:
    """Tests for proposal approval/rejection workflow."""

    @pytest.mark.asyncio
    async def test_approve_proposal(self, introspector: MockSchemaIntrospector) -> None:
        """Can approve a proposal."""
        samples = [{"user_id": f"u{i}"} for i in range(10)]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        if proposals:
            p_id = proposals[0].proposal_id
            assert ng.approve(p_id) is True
            assert proposals[0].approved is True
            assert len(ng.approved) == 1

    @pytest.mark.asyncio
    async def test_reject_proposal(self, introspector: MockSchemaIntrospector) -> None:
        """Can reject a proposal."""
        samples = [{"user_id": f"u{i}"} for i in range(10)]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        if proposals:
            p_id = proposals[0].proposal_id
            assert ng.reject(p_id) is True
            assert proposals[0].rejected is True
            # Rejected not in pending
            assert p_id not in [p.proposal_id for p in ng.proposals]

    def test_approve_nonexistent(self, neurogenesis: SchemaNeurogenesis) -> None:
        """Approving nonexistent returns False."""
        assert neurogenesis.approve("fake-id") is False

    def test_reject_nonexistent(self, neurogenesis: SchemaNeurogenesis) -> None:
        """Rejecting nonexistent returns False."""
        assert neurogenesis.reject("fake-id") is False


# =============================================================================
# Execution Tests
# =============================================================================


class TestExecution:
    """Tests for migration execution."""

    @pytest.mark.asyncio
    async def test_execute_approved(self, introspector: MockSchemaIntrospector) -> None:
        """Executes approved migrations."""
        samples = [{"user_id": f"u{i}"} for i in range(10)]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        if proposals:
            # Change action to ADD_COLUMN for SQL generation
            proposals[0].action = MigrationAction.ADD_COLUMN
            ng.approve(proposals[0].proposal_id)
            executed = await ng.execute_approved()

            assert len(executed) == 1
            assert proposals[0].executed is True
            assert len(introspector.executed_migrations) == 1

    @pytest.mark.asyncio
    async def test_execute_nothing_approved(self, neurogenesis: SchemaNeurogenesis) -> None:
        """Execute with nothing approved returns empty."""
        executed = await neurogenesis.execute_approved()
        assert len(executed) == 0

    @pytest.mark.asyncio
    async def test_get_proposal(self, introspector: MockSchemaIntrospector) -> None:
        """Can retrieve proposal by ID."""
        samples = [{"user_id": f"u{i}"} for i in range(10)]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        if proposals:
            retrieved = ng.get_proposal(proposals[0].proposal_id)
            assert retrieved is not None
            assert retrieved.proposal_id == proposals[0].proposal_id

    def test_get_nonexistent_proposal(self, neurogenesis: SchemaNeurogenesis) -> None:
        """Get nonexistent proposal returns None."""
        assert neurogenesis.get_proposal("fake-id") is None


# =============================================================================
# Integration Tests
# =============================================================================


class TestNeurogenesisIntegration:
    """Integration tests for full workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, introspector: MockSchemaIntrospector) -> None:
        """Full analyze → approve → execute workflow."""
        # Setup realistic data
        samples = [
            {
                "user_id": f"user_{i}",
                "action": "click",
                "timestamp": f"2024-01-{i + 1:02d}T12:00:00",
                "metadata": {"source": "web"},
            }
            for i in range(20)
        ]
        introspector.add_samples("events", "data", samples)

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(
                min_sample_size=10,
                column_threshold=0.8,
            ),
        )

        # Analyze
        proposals = await ng.analyze()
        assert len(proposals) > 0

        # Check clusters were detected
        assert len(ng.clusters) > 0

        # Approve all
        for p in proposals:
            # Make sure we have ADD_COLUMN for SQL
            p.action = MigrationAction.ADD_COLUMN
            ng.approve(p.proposal_id)

        # Execute
        executed = await ng.execute_approved()
        assert len(executed) == len(proposals)

        # Check history
        assert len(ng.history) == len(proposals)

        # Check stats
        stats = ng.stats()
        assert stats["executed"] == len(proposals)

    @pytest.mark.asyncio
    async def test_multiple_tables(self, introspector: MockSchemaIntrospector) -> None:
        """Analyzes multiple tables."""
        # Events table
        introspector.add_samples(
            "events",
            "data",
            [{"event_id": f"e{i}", "type": "click"} for i in range(10)],
        )
        # Users table
        introspector.add_samples(
            "users",
            "preferences",
            [{"theme": "dark", "lang": "en"} for _ in range(10)],
        )

        ng = SchemaNeurogenesis(
            introspector=introspector,
            config=NeurogenesisConfig(min_sample_size=5),
        )
        proposals = await ng.analyze()

        # Should have proposals from both tables
        tables = {p.table_name for p in proposals}
        assert "events" in tables
        assert "users" in tables
