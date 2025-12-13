"""
Synapse CDC Runner - Kubernetes CronJob/Deployment entrypoint.

Polls PostgreSQL outbox, computes embeddings, upserts to Qdrant,
reports metrics to stdout (Prometheus-compatible).

Usage:
    # Single batch (CronJob mode)
    python -m agents.flux.synapse_runner

    # Continuous (Deployment mode)
    python -m agents.flux.synapse_runner --continuous

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    QDRANT_URL: Qdrant HTTP endpoint
    OPENAI_API_KEY: For embeddings (optional if using local model)
    EMBEDDING_PROVIDER: openai, local, or mock
    SYNAPSE_BATCH_SIZE: Events per batch (default: 100)
    SYNAPSE_POLL_INTERVAL_MS: Poll interval in continuous mode (default: 1000)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, AsyncIterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("synapse_runner")


# ===========================================================================
# Configuration
# ===========================================================================


@dataclass
class RunnerConfig:
    """Configuration loaded from environment."""

    database_url: str
    qdrant_url: str
    redis_url: str | None
    openai_api_key: str | None
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    collection: str
    text_field: str
    batch_size: int
    poll_interval_ms: int
    max_retries: int
    use_circuit_breaker: bool
    use_dlq: bool

    @classmethod
    def from_env(cls) -> "RunnerConfig":
        """Load configuration from environment variables."""
        return cls(
            database_url=os.environ.get(
                "DATABASE_URL",
                "postgresql://triad:triad-dev-password@localhost:5432/triad",
            ),
            qdrant_url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
            redis_url=os.environ.get("REDIS_URL"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            embedding_provider=os.environ.get("EMBEDDING_PROVIDER", "mock"),
            embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002"),
            embedding_dimension=int(os.environ.get("EMBEDDING_DIMENSION", "1536")),
            collection=os.environ.get("SYNAPSE_COLLECTION", "memories"),
            text_field=os.environ.get("SYNAPSE_TEXT_FIELD", "content"),
            batch_size=int(os.environ.get("SYNAPSE_BATCH_SIZE", "100")),
            poll_interval_ms=int(os.environ.get("SYNAPSE_POLL_INTERVAL_MS", "1000")),
            max_retries=int(os.environ.get("SYNAPSE_MAX_RETRIES", "5")),
            use_circuit_breaker=os.environ.get(
                "SYNAPSE_USE_CIRCUIT_BREAKER", "true"
            ).lower()
            == "true",
            use_dlq=os.environ.get("SYNAPSE_USE_DLQ", "true").lower() == "true",
        )


# ===========================================================================
# Database Clients
# ===========================================================================


class PostgresClient:
    """PostgreSQL client for outbox polling."""

    def __init__(self, database_url: str) -> None:
        self._url = database_url
        self._pool: Any = None

    async def connect(self) -> None:
        """Connect to PostgreSQL."""
        try:
            import asyncpg

            self._pool = await asyncpg.create_pool(self._url, min_size=1, max_size=5)
            logger.info("Connected to PostgreSQL")
        except ImportError:
            logger.warning("asyncpg not installed, using mock mode")
            self._pool = None

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()

    async def fetch_pending_events(self, batch_size: int) -> list[dict[str, Any]]:
        """Fetch unprocessed outbox events."""
        if self._pool is None:
            return []

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, event_type, table_name, row_id, payload, created_at
                FROM outbox
                WHERE NOT processed
                ORDER BY created_at
                LIMIT $1
                """,
                batch_size,
            )

            return [
                {
                    "id": row["id"],
                    "event_type": row["event_type"],
                    "table_name": row["table_name"],
                    "row_id": row["row_id"],
                    "payload": json.loads(row["payload"])
                    if isinstance(row["payload"], str)
                    else dict(row["payload"]),
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

    async def mark_processed(self, event_ids: list[int]) -> None:
        """Mark events as processed."""
        if self._pool is None or not event_ids:
            return

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE outbox
                SET processed = TRUE, processed_at = NOW()
                WHERE id = ANY($1)
                """,
                event_ids,
            )

    async def get_outbox_stats(self) -> dict[str, Any]:
        """Get outbox statistics for monitoring."""
        if self._pool is None:
            return {"pending_events": 0, "processed_events": 0}

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM outbox_stats")
            return dict(row) if row else {}


class QdrantClient:
    """Qdrant client for vector operations."""

    def __init__(self, url: str, collection: str) -> None:
        self._url = url
        self._collection = collection
        self._client: Any = None

    async def connect(self) -> None:
        """Connect to Qdrant."""
        try:
            from qdrant_client import QdrantClient as QC
            from qdrant_client.models import Distance, VectorParams

            self._client = QC(url=self._url)

            # Ensure collection exists
            collections = self._client.get_collections().collections
            if not any(c.name == self._collection for c in collections):
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
                logger.info(f"Created collection: {self._collection}")

            logger.info(f"Connected to Qdrant at {self._url}")
        except ImportError:
            logger.warning("qdrant-client not installed, using mock mode")
            self._client = None

    async def upsert(
        self, id: str, vector: list[float], payload: dict[str, Any]
    ) -> None:
        """Upsert vector to collection."""
        if self._client is None:
            return

        from qdrant_client.models import PointStruct

        self._client.upsert(
            collection_name=self._collection,
            points=[PointStruct(id=id, vector=vector, payload=payload)],
        )

    async def delete(self, id: str) -> None:
        """Delete vector from collection."""
        if self._client is None:
            return

        from qdrant_client.models import PointIdsList

        self._client.delete(
            collection_name=self._collection,
            points_selector=PointIdsList(points=[id]),
        )

    async def get_collection_info(self) -> dict[str, Any]:
        """Get collection info for monitoring."""
        if self._client is None:
            return {"vectors_count": 0}

        info = self._client.get_collection(self._collection)
        return {
            "vectors_count": info.vectors_count,
            "status": info.status,
        }


class EmbeddingClient:
    """Embedding provider client."""

    def __init__(
        self,
        provider: str,
        model: str,
        dimension: int,
        api_key: str | None,
    ) -> None:
        self._provider = provider
        self._model = model
        self._dimension = dimension
        self._api_key = api_key
        self._client: Any = None

    async def connect(self) -> None:
        """Initialize embedding client."""
        if self._provider == "openai" and self._api_key:
            try:
                import openai

                openai.api_key = self._api_key
                self._client = openai
                logger.info("Using OpenAI embeddings")
            except ImportError:
                logger.warning("openai not installed, using mock embeddings")
                self._provider = "mock"
        else:
            logger.info("Using mock embeddings")
            self._provider = "mock"

    async def embed(self, text: str) -> list[float]:
        """Compute embedding for text."""
        if self._provider == "mock" or self._client is None:
            # Deterministic mock embedding
            seed = hash(text) % 1000
            return [float(seed + i) / 1000 for i in range(self._dimension)]

        # OpenAI embedding
        response = self._client.embeddings.create(
            input=text,
            model=self._model,
        )
        return list(response.data[0].embedding)


# ===========================================================================
# Synapse Runner
# ===========================================================================


class SynapseRunner:
    """Main runner that orchestrates CDC processing."""

    def __init__(self, config: RunnerConfig) -> None:
        self._config = config
        self._postgres = PostgresClient(config.database_url)
        self._qdrant = QdrantClient(config.qdrant_url, config.collection)
        self._embedder = EmbeddingClient(
            config.embedding_provider,
            config.embedding_model,
            config.embedding_dimension,
            config.openai_api_key,
        )

        # Metrics
        self._events_processed = 0
        self._events_failed = 0
        self._total_lag_ms = 0.0

    async def connect(self) -> None:
        """Connect to all services."""
        await self._postgres.connect()
        await self._qdrant.connect()
        await self._embedder.connect()

    async def close(self) -> None:
        """Close all connections."""
        await self._postgres.close()

    async def process_batch(self) -> int:
        """Process a single batch of events. Returns count processed."""
        events = await self._postgres.fetch_pending_events(self._config.batch_size)

        if not events:
            logger.debug("No pending events")
            return 0

        logger.info(f"Processing {len(events)} events")

        processed_ids: list[int] = []
        now = datetime.now(timezone.utc)

        for event in events:
            try:
                await self._process_event(event)
                processed_ids.append(event["id"])
                self._events_processed += 1

                # Calculate lag
                created_at = event["created_at"]
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                lag_ms = (now - created_at).total_seconds() * 1000
                self._total_lag_ms += lag_ms

            except Exception as e:
                logger.error(f"Failed to process event {event['id']}: {e}")
                self._events_failed += 1

        # Mark processed
        if processed_ids:
            await self._postgres.mark_processed(processed_ids)
            logger.info(f"Marked {len(processed_ids)} events as processed")

        return len(processed_ids)

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a single CDC event."""
        event_type = event["event_type"]
        row_id = event["row_id"]
        payload = event["payload"]

        if event_type == "DELETE":
            await self._qdrant.delete(row_id)
            logger.debug(f"Deleted vector: {row_id}")
        else:
            # INSERT or UPDATE
            text = payload.get(self._config.text_field, "")
            if text:
                vector = await self._embedder.embed(text)
                await self._qdrant.upsert(
                    id=row_id,
                    vector=vector,
                    payload={
                        "source": "postgres",
                        "table": event["table_name"],
                        **payload,
                    },
                )
                logger.debug(f"Upserted vector: {row_id}")

    async def run_once(self) -> None:
        """Run a single batch and exit."""
        await self.connect()

        try:
            processed = await self.process_batch()
            logger.info(f"Batch complete: {processed} events processed")
        finally:
            await self.close()
            self._print_metrics()

    async def run_continuous(self) -> None:
        """Run continuously, polling for events."""
        await self.connect()

        try:
            while True:
                processed = await self.process_batch()

                if processed == 0:
                    # No events, wait before next poll
                    await asyncio.sleep(self._config.poll_interval_ms / 1000)
                else:
                    # Events processed, check for more immediately
                    await asyncio.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            await self.close()
            self._print_metrics()

    def _print_metrics(self) -> None:
        """Print Prometheus-compatible metrics to stdout."""
        avg_lag = (
            self._total_lag_ms / self._events_processed
            if self._events_processed > 0
            else 0
        )

        print()
        print("# HELP synapse_events_processed_total Total CDC events processed")
        print("# TYPE synapse_events_processed_total counter")
        print(f"synapse_events_processed_total {self._events_processed}")
        print()
        print("# HELP synapse_events_failed_total Total CDC events that failed")
        print("# TYPE synapse_events_failed_total counter")
        print(f"synapse_events_failed_total {self._events_failed}")
        print()
        print("# HELP synapse_avg_lag_ms Average CDC lag in milliseconds")
        print("# TYPE synapse_avg_lag_ms gauge")
        print(f"synapse_avg_lag_ms {avg_lag:.2f}")
        print()


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Synapse CDC Runner")
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously instead of single batch",
    )
    args = parser.parse_args()

    config = RunnerConfig.from_env()
    runner = SynapseRunner(config)

    logger.info("Starting Synapse CDC Runner")
    logger.info(
        f"  Database: {config.database_url.split('@')[1] if '@' in config.database_url else config.database_url}"
    )
    logger.info(f"  Qdrant: {config.qdrant_url}")
    logger.info(f"  Embeddings: {config.embedding_provider}/{config.embedding_model}")
    logger.info(f"  Mode: {'continuous' if args.continuous else 'batch'}")

    if args.continuous:
        asyncio.run(runner.run_continuous())
    else:
        asyncio.run(runner.run_once())


if __name__ == "__main__":
    main()
