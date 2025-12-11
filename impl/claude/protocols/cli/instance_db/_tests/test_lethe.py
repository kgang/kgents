"""
Tests for LetheStore cryptographic amnesia.

These tests verify:
- Forget proofs creation and verification
- Retention policy checking
- Composting before forgetting
- Audit logging
- LetheGardener operations
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pytest

from ..hippocampus import LetheEpoch
from ..lethe import (
    ForgetProof,
    LetheGardener,
    LetheStore,
    NullStorageBackend,
    RetentionConfig,
    RetentionPolicy,
    create_lethe_gardener,
    create_lethe_store,
)

# === Test Fixtures ===


@dataclass
class MockSignal:
    """Mock signal for testing."""

    signal_type: str
    data: dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


def create_test_epoch(
    epoch_id: str = "test-epoch",
    days_ago: int = 0,
) -> LetheEpoch:
    """Create a test epoch."""
    sealed_at = datetime.now() - timedelta(days=days_ago)
    return LetheEpoch(
        epoch_id=epoch_id,
        created_at=sealed_at.isoformat(),
        sealed_at=sealed_at.isoformat(),
        signal_count=100,
        signal_types={"test"},
    )


def create_test_signals(count: int = 10) -> list[MockSignal]:
    """Create test signals."""
    return [
        MockSignal(
            signal_type=f"type_{i % 3}",
            data={"value": i, "instance_id": f"inst_{i % 5}"},
        )
        for i in range(count)
    ]


# === ForgetProof Tests ===


class TestForgetProof:
    """Tests for ForgetProof."""

    def test_proof_creation(self):
        """Test creating a forget proof."""
        proof = ForgetProof(
            epoch_id="test-epoch",
            content_hash="abc123",
            deletion_timestamp=datetime.now().isoformat(),
            signature="sig123",
        )
        assert proof.epoch_id == "test-epoch"
        assert proof.content_hash == "abc123"
        assert proof.algorithm == "sha256"

    @pytest.mark.asyncio
    async def test_proof_verification_valid(self):
        """Test verifying a valid proof."""
        secret_key = secrets.token_bytes(32)
        store = LetheStore(secret_key=secret_key)

        # Create a real proof through the store
        epoch = create_test_epoch()

        proof = await store.forget(epoch)

        # Verify with same key
        assert proof.verify(secret_key)

    @pytest.mark.asyncio
    async def test_proof_verification_invalid(self):
        """Test that wrong key fails verification."""
        secret_key = secrets.token_bytes(32)
        wrong_key = secrets.token_bytes(32)

        store = LetheStore(secret_key=secret_key)
        epoch = create_test_epoch()

        proof = await store.forget(epoch)

        # Verify with wrong key should fail
        assert not proof.verify(wrong_key)

    def test_proof_serialization(self):
        """Test proof dict serialization."""
        proof = ForgetProof(
            epoch_id="test",
            content_hash="abc",
            deletion_timestamp="2025-01-01T00:00:00",
            signature="sig",
            witness_ids=["w1", "w2"],
        )

        data = proof.to_dict()
        restored = ForgetProof.from_dict(data)

        assert restored.epoch_id == proof.epoch_id
        assert restored.content_hash == proof.content_hash
        assert restored.witness_ids == proof.witness_ids


# === RetentionPolicy Tests ===


class TestRetentionPolicy:
    """Tests for retention policy checking."""

    def test_hot_tier(self):
        """Test that recent epochs are HOT."""
        store = LetheStore(retention_config=RetentionConfig(hot_days=30))

        epoch = create_test_epoch(days_ago=5)
        policy = store.check_retention(epoch)

        assert policy == RetentionPolicy.HOT

    def test_warm_tier(self):
        """Test that older epochs are WARM."""
        store = LetheStore(retention_config=RetentionConfig(hot_days=30, warm_days=365))

        epoch = create_test_epoch(days_ago=60)
        policy = store.check_retention(epoch)

        assert policy == RetentionPolicy.WARM

    def test_compost_tier(self):
        """Test that old epochs are COMPOST."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=30,
                warm_days=365,
                compost_days=730,
            )
        )

        epoch = create_test_epoch(days_ago=400)
        policy = store.check_retention(epoch)

        assert policy == RetentionPolicy.COMPOST

    def test_forget_tier(self):
        """Test that very old epochs are FORGET."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=30,
                warm_days=365,
                compost_days=730,
            )
        )

        epoch = create_test_epoch(days_ago=800)
        policy = store.check_retention(epoch)

        assert policy == RetentionPolicy.FORGET


# === LetheStore Tests ===


class TestLetheStore:
    """Tests for LetheStore operations."""

    @pytest.mark.asyncio
    async def test_forget_creates_proof(self):
        """Test that forget creates a valid proof."""
        store = LetheStore()
        epoch = create_test_epoch()

        proof = await store.forget(epoch)

        assert proof.epoch_id == epoch.epoch_id
        assert proof.content_hash is not None
        assert proof.signature is not None
        assert store.verify_proof(proof)

    @pytest.mark.asyncio
    async def test_forget_records_operation(self):
        """Test that forget records the operation."""
        store = LetheStore()
        epoch = create_test_epoch()

        await store.forget(epoch, reason="test_deletion")

        record = store.get_record(epoch.epoch_id)
        assert record is not None
        assert record.operation == "forget"
        assert record.proof is not None

    @pytest.mark.asyncio
    async def test_compost_creates_block(self):
        """Test that compost creates a nutrient block."""
        store = LetheStore()
        epoch = create_test_epoch()
        signals = create_test_signals(50)

        block = await store.compost(epoch, signals)

        assert block.epoch_id == epoch.epoch_id
        assert block.source_signal_count == 50
        assert store.get_nutrient_block(epoch.epoch_id) is not None

    @pytest.mark.asyncio
    async def test_compost_then_forget(self):
        """Test composting then forgetting."""
        store = LetheStore()
        epoch = create_test_epoch()
        signals = create_test_signals(50)

        block, proof = await store.compost_then_forget(epoch, signals)

        # Both should exist
        assert block.source_signal_count == 50
        assert store.verify_proof(proof)

        # Should have both records
        records = store.records
        assert len(records) == 2
        assert records[0].operation == "compost"
        assert records[1].operation == "forget"

    @pytest.mark.asyncio
    async def test_retain_records_operation(self):
        """Test that retain records the operation."""
        store = LetheStore()
        epoch = create_test_epoch()

        record = await store.retain(epoch, reason="manual_keep")

        assert record.operation == "retain"
        assert record.metadata["reason"] == "manual_keep"

    @pytest.mark.asyncio
    async def test_audit_log(self):
        """Test audit logging."""
        store = LetheStore(retention_config=RetentionConfig(audit_log=True))
        epoch = create_test_epoch()

        await store.forget(epoch)

        log = store.get_audit_log()
        assert len(log) == 1
        assert log[0]["operation"] == "forget"
        assert log[0]["epoch_id"] == epoch.epoch_id

    @pytest.mark.asyncio
    async def test_audit_log_filtering(self):
        """Test audit log filtering."""
        store = LetheStore()

        # Multiple operations
        await store.retain(create_test_epoch("e1"))
        await store.forget(create_test_epoch("e2"))
        await store.retain(create_test_epoch("e3"))

        # Filter by operation
        retains = store.get_audit_log(operation="retain")
        assert len(retains) == 2

        forgets = store.get_audit_log(operation="forget")
        assert len(forgets) == 1

    def test_stats(self):
        """Test statistics reporting."""
        store = LetheStore()

        stats = store.stats()

        assert "total_records" in stats
        assert "nutrient_blocks" in stats
        assert "operations" in stats
        assert "retention_config" in stats


# === Storage Backend Tests ===


class TestNullStorageBackend:
    """Tests for NullStorageBackend."""

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        """Test storing and retrieving content."""
        backend = NullStorageBackend()

        await backend.store_epoch("epoch-1", b"test content")

        content = await backend.get_epoch_content("epoch-1")
        assert content == b"test content"

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deletion."""
        backend = NullStorageBackend()
        await backend.store_epoch("epoch-1", b"test")

        result = await backend.delete_epoch("epoch-1")
        assert result is True

        exists = await backend.epoch_exists("epoch-1")
        assert exists is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        """Test deleting nonexistent epoch."""
        backend = NullStorageBackend()

        result = await backend.delete_epoch("nonexistent")
        assert result is False


# === Retention Policy Application Tests ===


class TestRetentionPolicyApplication:
    """Tests for applying retention policies."""

    @pytest.mark.asyncio
    async def test_apply_policy_hot(self):
        """Test that HOT epochs are not processed."""
        store = LetheStore()

        epochs = [create_test_epoch("e1", days_ago=1)]
        records = await store.apply_retention_policy(epochs)

        # HOT epochs should not generate records
        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_apply_policy_warm(self):
        """Test that WARM epochs are retained."""
        store = LetheStore(retention_config=RetentionConfig(hot_days=30))

        epochs = [create_test_epoch("e1", days_ago=60)]
        records = await store.apply_retention_policy(epochs)

        assert len(records) == 1
        assert records[0].operation == "retain"

    @pytest.mark.asyncio
    async def test_apply_policy_compost(self):
        """Test that COMPOST epochs are composted."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=30,
                warm_days=100,
            )
        )

        epoch = create_test_epoch("e1", days_ago=200)
        signals = create_test_signals(20)

        records = await store.apply_retention_policy(
            [epoch],
            signals_by_epoch={"e1": signals},
        )

        assert len(records) == 1
        assert records[0].operation == "compost"

    @pytest.mark.asyncio
    async def test_apply_policy_forget(self):
        """Test that FORGET epochs are deleted."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=30,
                warm_days=100,
                compost_days=200,
            )
        )

        epoch = create_test_epoch("e1", days_ago=300)

        records = await store.apply_retention_policy([epoch])

        assert len(records) == 1
        # Should be forget (no signals provided for compost)
        assert records[0].operation == "forget"


# === LetheGardener Tests ===


class TestLetheGardener:
    """Tests for LetheGardener."""

    @pytest.mark.asyncio
    async def test_run_once(self):
        """Test running the gardener once."""
        store = LetheStore()
        gardener = LetheGardener(store)

        epochs = [
            create_test_epoch("e1", days_ago=60),  # WARM
            create_test_epoch("e2", days_ago=5),  # HOT
        ]

        records = await gardener.run_once(epochs)

        # Only WARM epoch should be processed
        assert len(records) == 1
        assert gardener.last_run is not None

    def test_gardener_stats(self):
        """Test gardener statistics."""
        store = LetheStore()
        gardener = LetheGardener(store)

        stats = gardener.stats()

        assert "is_running" in stats
        assert "last_run" in stats
        assert "config" in stats


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_lethe_store(self):
        """Test create_lethe_store factory."""
        store = create_lethe_store()
        assert store is not None
        assert store.secret_key is not None

    def test_create_lethe_store_with_config(self):
        """Test create_lethe_store with config."""
        store = create_lethe_store(
            retention_config={
                "hot_days": 7,
                "warm_days": 30,
            }
        )
        assert store.retention_config.hot_days == 7
        assert store.retention_config.warm_days == 30

    def test_create_lethe_gardener(self):
        """Test create_lethe_gardener factory."""
        store = create_lethe_store()
        gardener = create_lethe_gardener(store)

        assert gardener is not None

    def test_create_lethe_gardener_with_config(self):
        """Test create_lethe_gardener with config."""
        store = create_lethe_store()
        gardener = create_lethe_gardener(
            store,
            {
                "batch_size": 50,
                "check_interval_seconds": 1800,
            },
        )

        assert gardener._config.batch_size == 50
        assert gardener._config.check_interval_seconds == 1800


# === Integration Tests ===


class TestLetheIntegration:
    """Integration tests for Lethe workflow."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        """Test full data lifecycle through Lethe."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=0,  # Immediate transition for testing
                warm_days=0,
                compost_days=0,
            )
        )

        # Create epoch with content
        backend = NullStorageBackend()
        await backend.store_epoch("epoch-1", b"sensitive data")

        store._backend = backend
        epoch = create_test_epoch("epoch-1")
        signals = create_test_signals(100)

        # Compost then forget
        block, proof = await store.compost_then_forget(epoch, signals)

        # Verify:
        # 1. Proof is valid
        assert store.verify_proof(proof)

        # 2. Nutrient block preserved
        assert store.get_nutrient_block("epoch-1") is not None

        # 3. Raw data deleted
        exists = await backend.epoch_exists("epoch-1")
        assert exists is False

        # 4. Audit log complete
        log = store.get_audit_log()
        assert len(log) == 2  # compost + forget

    @pytest.mark.asyncio
    async def test_multiple_epochs_lifecycle(self):
        """Test processing multiple epochs."""
        store = LetheStore(
            retention_config=RetentionConfig(
                hot_days=10,
                warm_days=50,
                compost_days=100,
            )
        )

        epochs = [
            create_test_epoch("hot-1", days_ago=5),
            create_test_epoch("warm-1", days_ago=30),
            create_test_epoch("compost-1", days_ago=70),
            create_test_epoch("forget-1", days_ago=150),
        ]

        signals = {
            "compost-1": create_test_signals(20),
            "forget-1": create_test_signals(10),
        }

        records = await store.apply_retention_policy(epochs, signals)

        # Hot should not be processed
        hot_records = [r for r in records if r.epoch_id == "hot-1"]
        assert len(hot_records) == 0

        # Warm should be retained
        warm_records = [r for r in records if r.epoch_id == "warm-1"]
        assert len(warm_records) == 1
        assert warm_records[0].operation == "retain"

        # Compost should have nutrient block
        assert store.get_nutrient_block("compost-1") is not None

        # Forget should have proof
        forget_record = store.get_record("forget-1")
        assert forget_record is not None
        # With signals, it should compost then forget
        assert forget_record.operation == "forget"
