"""
Schema Neurogenesis: Self-Evolving Database Schema for the Bicameral Engine.

The Schema Neurogenesis module proposes schema migrations based on
detected patterns in the data. It provides:
- JSON blob analysis to detect recurring structures
- Migration proposals with confidence scores
- Pattern clustering to identify schema candidates
- Migration history tracking

Design rationale:
- Databases often evolve from unstructured to structured data
- JSON blobs with recurring keys should become columns
- Schema changes should be proposed, not automatic
- Human approval required before migration

From the implementation plan:
> "The cortex learns new structures from experience."

This implements "Schema Neurogenesis" - the database schema grows new
columns/tables based on observed patterns, like neurons forming new
connections.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4


class MigrationAction(Enum):
    """Types of migration actions."""

    ADD_COLUMN = "add_column"
    ADD_INDEX = "add_index"
    ADD_TABLE = "add_table"
    EXTRACT_JSON = "extract_json"
    CREATE_FOREIGN_KEY = "create_foreign_key"
    ADD_COMPUTED = "add_computed"


class ColumnType(Enum):
    """Detected column types from JSON analysis."""

    TEXT = "TEXT"
    INTEGER = "INTEGER"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    JSON = "JSON"
    UNKNOWN = "UNKNOWN"


@dataclass
class MigrationProposal:
    """A proposed schema migration."""

    proposal_id: str
    action: MigrationAction
    table_name: str
    column_name: str | None
    column_type: ColumnType | None
    source_column: str | None  # For extract_json migrations
    confidence: float  # 0.0 to 1.0
    sample_count: int  # Number of samples analyzed
    reasoning: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    rejected: bool = False
    executed: bool = False

    def to_sql(self) -> str | None:
        """Generate SQL for this migration (if applicable)."""
        if self.action == MigrationAction.ADD_COLUMN:
            return f"ALTER TABLE {self.table_name} ADD COLUMN {self.column_name} {self.column_type.value if self.column_type else 'TEXT'}"
        elif self.action == MigrationAction.ADD_INDEX:
            idx_name = f"idx_{self.table_name}_{self.column_name}"
            return f"CREATE INDEX {idx_name} ON {self.table_name}({self.column_name})"
        return None


@dataclass
class PatternCluster:
    """A cluster of similar JSON structures."""

    cluster_id: str
    key_pattern: frozenset[str]  # Set of keys that appear together
    occurrence_count: int
    type_signatures: dict[str, ColumnType]  # Inferred types per key
    sample_values: dict[str, list[Any]]  # Sample values per key
    table_source: str  # Which table/column these came from


@dataclass
class NeurogenesisConfig:
    """Configuration for Schema Neurogenesis."""

    # Sampling
    sample_limit: int = 100  # Max rows to sample per table
    min_sample_size: int = 10  # Min rows needed for analysis

    # Confidence thresholds
    column_threshold: float = 0.8  # Key appears in 80%+ samples → propose column
    index_threshold: float = 0.5  # Cardinality suggests index benefit

    # Pattern detection
    max_keys_for_column: int = 10  # Don't analyze blobs with too many keys
    type_consistency_threshold: float = 0.9  # 90%+ same type → confident

    # Migration limits
    max_proposals_per_run: int = 10  # Limit proposals per analysis

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NeurogenesisConfig":
        """Create from configuration dict."""
        return cls(
            sample_limit=data.get("sample_limit", 100),
            min_sample_size=data.get("min_sample_size", 10),
            column_threshold=data.get("column_threshold", 0.8),
            index_threshold=data.get("index_threshold", 0.5),
            max_keys_for_column=data.get("max_keys_for_column", 10),
            type_consistency_threshold=data.get("type_consistency_threshold", 0.9),
            max_proposals_per_run=data.get("max_proposals_per_run", 10),
        )


@runtime_checkable
class ISchemaIntrospector(Protocol):
    """Protocol for schema introspection."""

    async def get_json_columns(self) -> list[tuple[str, str]]:
        """Get list of (table, column) pairs that contain JSON."""
        ...

    async def sample_column(
        self, table: str, column: str, limit: int
    ) -> list[dict[str, Any]]:
        """Sample JSON values from a column."""
        ...

    async def execute_migration(self, sql: str) -> bool:
        """Execute a migration SQL statement."""
        ...


class MockSchemaIntrospector:
    """Mock introspector for testing."""

    def __init__(self, json_columns: list[tuple[str, str]] | None = None):
        self._json_columns = json_columns or []
        self._samples: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._executed_migrations: list[str] = []

    def add_samples(
        self, table: str, column: str, samples: list[dict[str, Any]]
    ) -> None:
        """Add sample data for a column."""
        self._samples[(table, column)] = samples

    async def get_json_columns(self) -> list[tuple[str, str]]:
        return self._json_columns

    async def sample_column(
        self, table: str, column: str, limit: int
    ) -> list[dict[str, Any]]:
        return self._samples.get((table, column), [])[:limit]

    async def execute_migration(self, sql: str) -> bool:
        self._executed_migrations.append(sql)
        return True

    @property
    def executed_migrations(self) -> list[str]:
        return self._executed_migrations


class TypeInferrer:
    """Infers column types from sample values."""

    @staticmethod
    def infer_type(values: list[Any]) -> tuple[ColumnType, float]:
        """
        Infer the most likely type for a list of values.

        Returns:
            Tuple of (type, confidence)
        """
        if not values:
            return ColumnType.UNKNOWN, 0.0

        # Filter None values
        non_null = [v for v in values if v is not None]
        if not non_null:
            return ColumnType.UNKNOWN, 0.0

        type_counts: Counter[ColumnType] = Counter()

        for value in non_null:
            detected = TypeInferrer._detect_value_type(value)
            type_counts[detected] += 1

        # Find most common type
        most_common = type_counts.most_common(1)[0]
        best_type = most_common[0]
        confidence = most_common[1] / len(non_null)

        return best_type, confidence

    @staticmethod
    def _detect_value_type(value: Any) -> ColumnType:
        """Detect type of a single value."""
        if isinstance(value, bool):
            return ColumnType.BOOLEAN
        if isinstance(value, int):
            return ColumnType.INTEGER
        if isinstance(value, float):
            return ColumnType.REAL
        if isinstance(value, str):
            # Check for timestamp patterns
            if TypeInferrer._looks_like_timestamp(value):
                return ColumnType.TIMESTAMP
            return ColumnType.TEXT
        if isinstance(value, dict) or isinstance(value, list):
            return ColumnType.JSON
        return ColumnType.UNKNOWN

    @staticmethod
    def _looks_like_timestamp(value: str) -> bool:
        """Check if a string looks like a timestamp."""
        # ISO format check
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            pass
        # Other common patterns
        timestamp_indicators = ["-", "T", ":", "Z", "UTC"]
        return (
            len(value) >= 10
            and sum(1 for ind in timestamp_indicators if ind in value) >= 2
        )


class SchemaNeurogenesis:
    """
    Proposes schema migrations based on detected patterns.

    Analyzes JSON columns to find:
    - Recurring keys that should become columns
    - High-cardinality fields that need indexes
    - Patterns suggesting new tables

    Usage:
        neurogenesis = SchemaNeurogenesis(introspector)

        # Analyze and get proposals
        proposals = await neurogenesis.analyze()

        # Review proposals
        for proposal in proposals:
            print(f"{proposal.action}: {proposal.column_name}")
            print(f"  Confidence: {proposal.confidence:.1%}")
            print(f"  SQL: {proposal.to_sql()}")

        # Approve and execute
        neurogenesis.approve(proposal.proposal_id)
        await neurogenesis.execute_approved()
    """

    def __init__(
        self,
        introspector: ISchemaIntrospector,
        config: NeurogenesisConfig | None = None,
    ):
        """
        Initialize Schema Neurogenesis.

        Args:
            introspector: Database introspection interface
            config: Configuration options
        """
        self._introspector = introspector
        self._config = config or NeurogenesisConfig()
        self._proposals: list[MigrationProposal] = []
        self._clusters: list[PatternCluster] = []
        self._history: list[MigrationProposal] = []

    @property
    def proposals(self) -> list[MigrationProposal]:
        """Current pending proposals."""
        return [p for p in self._proposals if not p.rejected and not p.executed]

    @property
    def approved(self) -> list[MigrationProposal]:
        """Approved but not yet executed proposals."""
        return [
            p
            for p in self._proposals
            if p.approved and not p.executed and not p.rejected
        ]

    @property
    def history(self) -> list[MigrationProposal]:
        """All historical proposals."""
        return self._history.copy()

    @property
    def clusters(self) -> list[PatternCluster]:
        """Detected pattern clusters."""
        return self._clusters.copy()

    async def analyze(self) -> list[MigrationProposal]:
        """
        Analyze JSON columns and propose migrations.

        Returns:
            List of migration proposals
        """
        self._proposals = []
        self._clusters = []

        # Get all JSON columns
        json_columns = await self._introspector.get_json_columns()

        for table, column in json_columns:
            # Sample the column
            samples = await self._introspector.sample_column(
                table, column, self._config.sample_limit
            )

            if len(samples) < self._config.min_sample_size:
                continue

            # Analyze patterns
            patterns = self._analyze_json_patterns(table, column, samples)
            self._clusters.extend(patterns)

            # Generate proposals from patterns
            for cluster in patterns:
                proposals = self._proposals_from_cluster(
                    cluster, table, column, len(samples)
                )
                self._proposals.extend(proposals)

        # Limit proposals
        self._proposals = self._proposals[: self._config.max_proposals_per_run]

        return self._proposals

    def _analyze_json_patterns(
        self, table: str, column: str, samples: list[dict[str, Any]]
    ) -> list[PatternCluster]:
        """Analyze JSON samples to find patterns."""
        clusters = []

        # Count key occurrences
        key_counts: Counter[str] = Counter()
        key_values: dict[str, list[Any]] = {}

        for sample in samples:
            if not isinstance(sample, dict):
                continue

            for key, value in sample.items():
                key_counts[key] += 1
                if key not in key_values:
                    key_values[key] = []
                key_values[key].append(value)

        # Skip if too many keys (probably complex structure)
        if len(key_counts) > self._config.max_keys_for_column:
            return clusters

        # Find keys that appear consistently
        consistent_keys = {
            key
            for key, count in key_counts.items()
            if count / len(samples) >= self._config.column_threshold
        }

        if not consistent_keys:
            return clusters

        # Infer types for consistent keys
        type_signatures = {}
        sample_values = {}
        for key in consistent_keys:
            values = key_values.get(key, [])
            inferred_type, confidence = TypeInferrer.infer_type(values)
            if confidence >= self._config.type_consistency_threshold:
                type_signatures[key] = inferred_type
                sample_values[key] = values[:5]  # Keep first 5 samples

        # Create cluster
        if type_signatures:
            cluster = PatternCluster(
                cluster_id=str(uuid4()),
                key_pattern=frozenset(type_signatures.keys()),
                occurrence_count=len(samples),
                type_signatures=type_signatures,
                sample_values=sample_values,
                table_source=f"{table}.{column}",
            )
            clusters.append(cluster)

        return clusters

    def _proposals_from_cluster(
        self,
        cluster: PatternCluster,
        table: str,
        source_column: str,
        sample_count: int,
    ) -> list[MigrationProposal]:
        """Generate migration proposals from a pattern cluster."""
        proposals = []

        for key, col_type in cluster.type_signatures.items():
            # Propose column extraction
            proposal = MigrationProposal(
                proposal_id=str(uuid4()),
                action=MigrationAction.EXTRACT_JSON,
                table_name=table,
                column_name=key,
                column_type=col_type,
                source_column=source_column,
                confidence=cluster.occurrence_count / sample_count,
                sample_count=sample_count,
                reasoning=f"Key '{key}' appears in {cluster.occurrence_count}/{sample_count} samples with type {col_type.value}",
            )
            proposals.append(proposal)

        return proposals

    def approve(self, proposal_id: str) -> bool:
        """
        Approve a migration proposal.

        Args:
            proposal_id: ID of the proposal to approve

        Returns:
            True if approved, False if not found
        """
        for proposal in self._proposals:
            if proposal.proposal_id == proposal_id:
                proposal.approved = True
                return True
        return False

    def reject(self, proposal_id: str) -> bool:
        """
        Reject a migration proposal.

        Args:
            proposal_id: ID of the proposal to reject

        Returns:
            True if rejected, False if not found
        """
        for proposal in self._proposals:
            if proposal.proposal_id == proposal_id:
                proposal.rejected = True
                return True
        return False

    async def execute_approved(self) -> list[MigrationProposal]:
        """
        Execute all approved migrations.

        Returns:
            List of executed proposals
        """
        executed = []

        for proposal in self.approved:
            sql = proposal.to_sql()
            if sql:
                try:
                    success = await self._introspector.execute_migration(sql)
                    if success:
                        proposal.executed = True
                        executed.append(proposal)
                        self._history.append(proposal)
                except Exception:
                    pass  # Log but don't fail

        return executed

    def get_proposal(self, proposal_id: str) -> MigrationProposal | None:
        """Get a proposal by ID."""
        for proposal in self._proposals:
            if proposal.proposal_id == proposal_id:
                return proposal
        return None

    def stats(self) -> dict[str, Any]:
        """Get neurogenesis statistics."""
        return {
            "total_proposals": len(self._proposals),
            "pending": len(self.proposals),
            "approved": len(self.approved),
            "executed": len([p for p in self._proposals if p.executed]),
            "rejected": len([p for p in self._proposals if p.rejected]),
            "clusters_detected": len(self._clusters),
            "history_size": len(self._history),
        }


# Factory function
def create_schema_neurogenesis(
    introspector: ISchemaIntrospector,
    config_dict: dict[str, Any] | None = None,
) -> SchemaNeurogenesis:
    """
    Create a Schema Neurogenesis instance.

    Args:
        introspector: Database introspection interface
        config_dict: Configuration dict (from YAML)

    Returns:
        Configured SchemaNeurogenesis
    """
    config = (
        NeurogenesisConfig.from_dict(config_dict)
        if config_dict
        else NeurogenesisConfig()
    )
    return SchemaNeurogenesis(introspector=introspector, config=config)
