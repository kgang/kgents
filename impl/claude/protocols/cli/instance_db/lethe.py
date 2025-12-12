"""
LetheStore: Cryptographic Amnesia for Secure Memory Deletion.

Named after the river Lethe in Greek mythology - drinking from it
caused complete forgetfulness. This module provides cryptographic
deletion with proof of forgetting.

Components:
- LetheStore: Manages cryptographic deletion of epochs
- ForgetProof: Cryptographic proof that data was deleted
- LethePolicy: Configurable retention and deletion policies

Design Philosophy:
- True deletion requires cryptographic proof
- Data cannot be recovered after proper Lethe treatment
- Audit trail for compliance (GDPR "right to be forgotten")
- Graceful degradation when crypto is unavailable

From the implementation plan:
> "Lethe epochs mark boundaries for memory retention policies.
>  Once an epoch is sealed, its memories can be:
>  - Retained (consolidated to long-term)
>  - Composted (compressed to statistics)
>  - Forgotten (deleted with cryptographic proof)"
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .compost import CompostBin, CompostConfig, NutrientBlock
from .hippocampus import LetheEpoch


class LetheError(Exception):
    """Error during Lethe operation."""


class ForgetError(LetheError):
    """Failed to forget data."""


class ProofVerificationError(LetheError):
    """Failed to verify forget proof."""


class RetentionPolicy(Enum):
    """Data retention policies."""

    HOT = "hot"  # Keep fully accessible (< 30 days)
    WARM = "warm"  # Keep accessible, may be slower (30-365 days)
    COMPOST = "compost"  # Compress to statistics only
    FORGET = "forget"  # Cryptographically delete


@dataclass
class RetentionConfig:
    """Configuration for data retention."""

    # Days in each tier
    hot_days: int = 30
    warm_days: int = 365
    compost_days: int = 730  # After this, forget completely

    # What to do when thresholds are reached
    hot_to_warm_action: str = "archive"  # Move to slower storage
    warm_to_compost_action: str = "compress"  # Keep only statistics
    compost_to_forget_action: str = "delete"  # Cryptographic deletion

    # Compliance
    require_forget_proof: bool = True  # Require cryptographic proof
    audit_log: bool = True  # Log all retention actions

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetentionConfig":
        """Create from dict."""
        return cls(
            hot_days=data.get("hot_days", 30),
            warm_days=data.get("warm_days", 365),
            compost_days=data.get("compost_days", 730),
            hot_to_warm_action=data.get("hot_to_warm_action", "archive"),
            warm_to_compost_action=data.get("warm_to_compost_action", "compress"),
            compost_to_forget_action=data.get("compost_to_forget_action", "delete"),
            require_forget_proof=data.get("require_forget_proof", True),
            audit_log=data.get("audit_log", True),
        )


@dataclass
class ForgetProof:
    """
    Cryptographic proof that data was forgotten.

    This proof can be used to demonstrate compliance with
    data deletion requirements (e.g., GDPR Article 17).

    The proof contains:
    - Epoch ID that was deleted
    - Hash of deleted content (proves what was deleted)
    - Deletion timestamp
    - HMAC signature (proves deletion was authorized)
    """

    epoch_id: str
    content_hash: str  # SHA-256 of deleted content
    deletion_timestamp: str
    signature: str  # HMAC signature
    algorithm: str = "sha256"
    witness_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "epoch_id": self.epoch_id,
            "content_hash": self.content_hash,
            "deletion_timestamp": self.deletion_timestamp,
            "signature": self.signature,
            "algorithm": self.algorithm,
            "witness_ids": self.witness_ids,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ForgetProof":
        """Deserialize from dict."""
        return cls(
            epoch_id=data["epoch_id"],
            content_hash=data["content_hash"],
            deletion_timestamp=data["deletion_timestamp"],
            signature=data["signature"],
            algorithm=data.get("algorithm", "sha256"),
            witness_ids=data.get("witness_ids", []),
            metadata=data.get("metadata", {}),
        )

    def verify(self, secret_key: bytes) -> bool:
        """
        Verify the proof signature.

        Args:
            secret_key: The secret key used for signing

        Returns:
            True if signature is valid
        """
        message = f"{self.epoch_id}:{self.content_hash}:{self.deletion_timestamp}"
        expected = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.signature, expected)


@dataclass
class LetheRecord:
    """Record of a Lethe operation."""

    epoch_id: str
    operation: str  # "retain", "compost", "forget"
    timestamp: str
    proof: ForgetProof | None = None
    nutrient_block: NutrientBlock | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "epoch_id": self.epoch_id,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "proof": self.proof.to_dict() if self.proof else None,
            "nutrient_block": self.nutrient_block.to_dict()
            if self.nutrient_block
            else None,
            "metadata": self.metadata,
        }


@runtime_checkable
class IStorageBackend(Protocol):
    """Protocol for storage backend that supports deletion."""

    async def delete_epoch(self, epoch_id: str) -> bool:
        """Delete all data for an epoch."""
        ...

    async def get_epoch_content(self, epoch_id: str) -> bytes | None:
        """Get raw content for an epoch (for hashing before deletion)."""
        ...

    async def epoch_exists(self, epoch_id: str) -> bool:
        """Check if epoch exists."""
        ...


class NullStorageBackend:
    """Null storage backend for testing."""

    def __init__(self) -> None:
        self._epochs: dict[str, bytes] = {}

    async def store_epoch(self, epoch_id: str, content: bytes) -> None:
        """Store epoch content (for testing)."""
        self._epochs[epoch_id] = content

    async def delete_epoch(self, epoch_id: str) -> bool:
        """Delete epoch."""
        if epoch_id in self._epochs:
            del self._epochs[epoch_id]
            return True
        return False

    async def get_epoch_content(self, epoch_id: str) -> bytes | None:
        """Get epoch content."""
        return self._epochs.get(epoch_id)

    async def epoch_exists(self, epoch_id: str) -> bool:
        """Check if epoch exists."""
        return epoch_id in self._epochs


class LetheStore:
    """
    Cryptographic Amnesia Store.

    Manages the forgetting of data with cryptographic proofs.
    This enables:
    - Verifiable deletion (GDPR compliance)
    - Audit trail of what was deleted
    - Graceful degradation when crypto unavailable
    - Integration with composting for partial retention

    Usage:
        store = LetheStore(secret_key=os.urandom(32))

        # Forget an epoch completely
        proof = await store.forget(epoch)
        assert proof.verify(store.secret_key)

        # Compost before forgetting (keep statistics)
        nutrients = await store.compost_then_forget(epoch, signals)

        # Check retention policy
        action = store.check_retention(epoch)
        # → RetentionPolicy.WARM, RetentionPolicy.COMPOST, etc.
    """

    def __init__(
        self,
        secret_key: bytes | None = None,
        storage_backend: IStorageBackend | None = None,
        retention_config: RetentionConfig | None = None,
        compost_config: CompostConfig | None = None,
    ):
        """
        Initialize LetheStore.

        Args:
            secret_key: Secret key for signing proofs (generated if None)
            storage_backend: Backend for actual data storage
            retention_config: Data retention configuration
            compost_config: Composting configuration
        """
        self._secret_key = secret_key or secrets.token_bytes(32)
        self._backend = storage_backend or NullStorageBackend()
        self._retention_config = retention_config or RetentionConfig()
        self._compost_config = compost_config or CompostConfig()

        # Records of Lethe operations
        self._records: list[LetheRecord] = []
        self._nutrient_blocks: dict[str, NutrientBlock] = {}

        # Audit log
        self._audit_log: list[dict[str, Any]] = []

    @property
    def secret_key(self) -> bytes:
        """Get the secret key (for verification)."""
        return self._secret_key

    @property
    def retention_config(self) -> RetentionConfig:
        """Get retention configuration."""
        return self._retention_config

    @property
    def records(self) -> list[LetheRecord]:
        """Get all Lethe records."""
        return self._records.copy()

    @property
    def nutrient_blocks(self) -> dict[str, NutrientBlock]:
        """Get all nutrient blocks."""
        return self._nutrient_blocks.copy()

    def check_retention(self, epoch: LetheEpoch) -> RetentionPolicy:
        """
        Determine retention policy for an epoch based on age.

        Args:
            epoch: Epoch to check

        Returns:
            Appropriate RetentionPolicy
        """
        sealed_at = datetime.fromisoformat(epoch.sealed_at)
        age = datetime.now() - sealed_at
        age_days = age.total_seconds() / 86400

        if age_days < self._retention_config.hot_days:
            return RetentionPolicy.HOT
        elif age_days < self._retention_config.warm_days:
            return RetentionPolicy.WARM
        elif age_days < self._retention_config.compost_days:
            return RetentionPolicy.COMPOST
        else:
            return RetentionPolicy.FORGET

    async def forget(
        self,
        epoch: LetheEpoch,
        reason: str = "retention_policy",
    ) -> ForgetProof:
        """
        Cryptographically forget an epoch.

        This:
        1. Gets the content hash (before deletion)
        2. Deletes all data for the epoch
        3. Creates a cryptographic proof of deletion
        4. Records the operation in the audit log

        Args:
            epoch: Epoch to forget
            reason: Reason for forgetting (for audit)

        Returns:
            ForgetProof that can be used to verify deletion

        Raises:
            ForgetError: If deletion fails
        """
        now = datetime.now().isoformat()

        # Get content for hashing
        content = await self._backend.get_epoch_content(epoch.epoch_id)
        if content is None:
            # Epoch may already be deleted or never stored
            content = b""

        # Compute content hash
        content_hash = hashlib.sha256(content).hexdigest()

        # Delete the epoch
        deleted = await self._backend.delete_epoch(epoch.epoch_id)

        if not deleted and await self._backend.epoch_exists(epoch.epoch_id):
            raise ForgetError(f"Failed to delete epoch {epoch.epoch_id}")

        # Create signature
        message = f"{epoch.epoch_id}:{content_hash}:{now}"
        signature = hmac.new(
            self._secret_key, message.encode(), hashlib.sha256
        ).hexdigest()

        # Create proof
        proof = ForgetProof(
            epoch_id=epoch.epoch_id,
            content_hash=content_hash,
            deletion_timestamp=now,
            signature=signature,
            metadata={"reason": reason},
        )

        # Record the operation
        record = LetheRecord(
            epoch_id=epoch.epoch_id,
            operation="forget",
            timestamp=now,
            proof=proof,
            metadata={"reason": reason},
        )
        self._records.append(record)

        # Audit log
        if self._retention_config.audit_log:
            self._log_audit(
                "forget",
                epoch.epoch_id,
                {
                    "reason": reason,
                    "content_hash": content_hash,
                    "proof_signature": signature[:16] + "...",
                },
            )

        return proof

    async def compost(
        self,
        epoch: LetheEpoch,
        signals: list[Any],
    ) -> NutrientBlock:
        """
        Compost an epoch (compress to statistics only).

        Args:
            epoch: Epoch to compost
            signals: Signals from the epoch to extract statistics from

        Returns:
            NutrientBlock containing compressed statistics
        """
        now = datetime.now().isoformat()

        # Create compost bin and add signals
        bin = CompostBin(config=self._compost_config)
        for signal in signals:
            bin.add(signal)

        # Seal to create nutrient block
        block = bin.seal(epoch.epoch_id)

        # Store the nutrient block
        self._nutrient_blocks[epoch.epoch_id] = block

        # Record the operation
        record = LetheRecord(
            epoch_id=epoch.epoch_id,
            operation="compost",
            timestamp=now,
            nutrient_block=block,
        )
        self._records.append(record)

        # Audit log
        if self._retention_config.audit_log:
            self._log_audit(
                "compost",
                epoch.epoch_id,
                {
                    "signal_count": len(signals),
                    "compression_ratio": block.compression_ratio,
                },
            )

        return block

    async def compost_then_forget(
        self,
        epoch: LetheEpoch,
        signals: list[Any],
        reason: str = "retention_policy",
    ) -> tuple[NutrientBlock, ForgetProof]:
        """
        Compost an epoch and then forget the raw data.

        This is the recommended path for data past the warm tier:
        1. Extract statistics into NutrientBlock
        2. Delete raw data with cryptographic proof
        3. Keep nutrients for historical queries

        Args:
            epoch: Epoch to process
            signals: Signals to extract statistics from
            reason: Reason for the operation

        Returns:
            Tuple of (NutrientBlock, ForgetProof)
        """
        # First compost
        block = await self.compost(epoch, signals)

        # Then forget the raw data
        proof = await self.forget(epoch, reason)

        return block, proof

    async def retain(
        self,
        epoch: LetheEpoch,
        reason: str = "manual_retention",
    ) -> LetheRecord:
        """
        Explicitly mark an epoch for retention (prevent deletion).

        Args:
            epoch: Epoch to retain
            reason: Reason for retention

        Returns:
            LetheRecord documenting the retention
        """
        now = datetime.now().isoformat()

        record = LetheRecord(
            epoch_id=epoch.epoch_id,
            operation="retain",
            timestamp=now,
            metadata={"reason": reason},
        )
        self._records.append(record)

        if self._retention_config.audit_log:
            self._log_audit("retain", epoch.epoch_id, {"reason": reason})

        return record

    def verify_proof(self, proof: ForgetProof) -> bool:
        """
        Verify a forget proof.

        Args:
            proof: Proof to verify

        Returns:
            True if proof is valid
        """
        return proof.verify(self._secret_key)

    def get_record(self, epoch_id: str) -> LetheRecord | None:
        """Get the most recent record for an epoch."""
        for record in reversed(self._records):
            if record.epoch_id == epoch_id:
                return record
        return None

    def get_nutrient_block(self, epoch_id: str) -> NutrientBlock | None:
        """Get nutrient block for an epoch (if composted)."""
        return self._nutrient_blocks.get(epoch_id)

    async def apply_retention_policy(
        self,
        epochs: list[LetheEpoch],
        signals_by_epoch: dict[str, list[Any]] | None = None,
    ) -> list[LetheRecord]:
        """
        Apply retention policy to a list of epochs.

        This is the main entry point for automated retention management.
        It checks each epoch's age and applies the appropriate action.

        Args:
            epochs: Epochs to process
            signals_by_epoch: Signals for each epoch (for composting)

        Returns:
            List of records for actions taken
        """
        signals_by_epoch = signals_by_epoch or {}
        records = []

        for epoch in epochs:
            policy = self.check_retention(epoch)

            if policy == RetentionPolicy.HOT:
                # Keep as-is
                continue

            elif policy == RetentionPolicy.WARM:
                # Archive action - just record
                record = await self.retain(epoch, reason="warm_tier")
                records.append(record)

            elif policy == RetentionPolicy.COMPOST:
                # Compress to statistics
                signals = signals_by_epoch.get(epoch.epoch_id, [])
                if signals:
                    await self.compost(epoch, signals)
                    records.append(self.get_record(epoch.epoch_id))  # type: ignore

            elif policy == RetentionPolicy.FORGET:
                # Cryptographic deletion
                signals = signals_by_epoch.get(epoch.epoch_id, [])
                if signals:
                    # Compost first to preserve some information
                    _, _ = await self.compost_then_forget(epoch, signals)
                else:
                    # Just forget
                    await self.forget(epoch, reason="retention_policy_forget")
                records.append(self.get_record(epoch.epoch_id))  # type: ignore

        return [r for r in records if r is not None]

    def _log_audit(
        self, operation: str, epoch_id: str, details: dict[str, Any]
    ) -> None:
        """Add entry to audit log."""
        self._audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "epoch_id": epoch_id,
                "details": details,
            }
        )

    def get_audit_log(
        self,
        since: str | None = None,
        operation: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            since: Only entries after this timestamp
            operation: Filter by operation type

        Returns:
            List of audit log entries
        """
        entries = self._audit_log

        if since:
            entries = [e for e in entries if e["timestamp"] >= since]

        if operation:
            entries = [e for e in entries if e["operation"] == operation]

        return entries

    def stats(self) -> dict[str, Any]:
        """Get Lethe store statistics."""
        operations = {"forget": 0, "compost": 0, "retain": 0}
        for record in self._records:
            if record.operation in operations:
                operations[record.operation] += 1

        return {
            "total_records": len(self._records),
            "nutrient_blocks": len(self._nutrient_blocks),
            "operations": operations,
            "audit_log_entries": len(self._audit_log),
            "retention_config": {
                "hot_days": self._retention_config.hot_days,
                "warm_days": self._retention_config.warm_days,
                "compost_days": self._retention_config.compost_days,
            },
        }


@dataclass
class LetheGardenerConfig:
    """Configuration for the Lethe Gardener."""

    # How often to run retention checks (seconds)
    check_interval_seconds: int = 3600  # 1 hour

    # Batch size for retention operations
    batch_size: int = 100

    # Whether to run automatically
    auto_run: bool = True

    # Grace period before first run (seconds)
    grace_period_seconds: int = 300  # 5 minutes

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LetheGardenerConfig":
        return cls(
            check_interval_seconds=data.get("check_interval_seconds", 3600),
            batch_size=data.get("batch_size", 100),
            auto_run=data.get("auto_run", True),
            grace_period_seconds=data.get("grace_period_seconds", 300),
        )


class LetheGardener:
    """
    Background worker that applies retention policies.

    The Gardener periodically checks epochs and applies
    the appropriate retention policy (archive, compost, forget).

    Usage:
        gardener = LetheGardener(
            lethe_store=store,
            epoch_provider=hippocampus,
        )
        await gardener.run_once()  # Manual run
        # or
        await gardener.start()  # Background loop
    """

    def __init__(
        self,
        lethe_store: LetheStore,
        config: LetheGardenerConfig | None = None,
    ):
        """
        Initialize the Gardener.

        Args:
            lethe_store: LetheStore for retention operations
            config: Gardener configuration
        """
        self._store = lethe_store
        self._config = config or LetheGardenerConfig()
        self._running = False
        self._last_run: datetime | None = None

    @property
    def is_running(self) -> bool:
        """Check if gardener is running."""
        return self._running

    @property
    def last_run(self) -> datetime | None:
        """Get time of last run."""
        return self._last_run

    async def run_once(
        self,
        epochs: list[LetheEpoch],
        signals_by_epoch: dict[str, list[Any]] | None = None,
    ) -> list[LetheRecord]:
        """
        Run retention check once.

        Args:
            epochs: Epochs to check
            signals_by_epoch: Signals for composting

        Returns:
            Records of actions taken
        """
        records = await self._store.apply_retention_policy(epochs, signals_by_epoch)
        self._last_run = datetime.now()
        return records

    def stats(self) -> dict[str, Any]:
        """Get gardener statistics."""
        return {
            "is_running": self._running,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "config": {
                "check_interval_seconds": self._config.check_interval_seconds,
                "batch_size": self._config.batch_size,
                "auto_run": self._config.auto_run,
            },
        }


# Factory functions


def create_lethe_store(
    secret_key: bytes | None = None,
    storage_backend: IStorageBackend | None = None,
    retention_config: dict[str, Any] | None = None,
    compost_config: dict[str, Any] | None = None,
) -> LetheStore:
    """
    Create a LetheStore with optional configuration.

    Args:
        secret_key: Secret key for signing proofs
        storage_backend: Storage backend
        retention_config: Retention configuration dict
        compost_config: Composting configuration dict

    Returns:
        Configured LetheStore
    """
    ret_config = (
        RetentionConfig.from_dict(retention_config) if retention_config else None
    )
    comp_config = CompostConfig.from_dict(compost_config) if compost_config else None

    return LetheStore(
        secret_key=secret_key,
        storage_backend=storage_backend,
        retention_config=ret_config,
        compost_config=comp_config,
    )


def create_lethe_gardener(
    lethe_store: LetheStore,
    config_dict: dict[str, Any] | None = None,
) -> LetheGardener:
    """
    Create a LetheGardener with optional configuration.

    Args:
        lethe_store: LetheStore for retention operations
        config_dict: Gardener configuration dict

    Returns:
        Configured LetheGardener
    """
    config = LetheGardenerConfig.from_dict(config_dict) if config_dict else None
    return LetheGardener(lethe_store=lethe_store, config=config)
