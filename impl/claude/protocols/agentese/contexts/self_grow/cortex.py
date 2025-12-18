"""
GrowthCortex: Bicameral Persistence Layer for self.grow.

Stores proposals, nursery holons, rollback tokens, and budget state
in the bicameral cortex (Left: relational, Right: vector).

The `why_exists` field is embedded for semantic discovery:
    "Find proposals about botanical exploration"

AGENTESE: self.grow.* persistence
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .schemas import (
    GerminatingHolon,
    GrowthBudget,
    GrowthBudgetConfig,
    HolonProposal,
    RollbackToken,
    ValidationResult,
)

if TYPE_CHECKING:
    from pathlib import Path

    from agents.d.bicameral import BicameralMemory

    from protocols.cli.instance_db.interfaces import IRelationalStore


# === Serialization Helpers ===


def _serialize_proposal(proposal: HolonProposal) -> dict[str, Any]:
    """Serialize HolonProposal to JSON-safe dict."""
    return {
        "proposal_id": proposal.proposal_id,
        "content_hash": proposal.content_hash,
        "entity": proposal.entity,
        "context": proposal.context,
        "version": proposal.version,
        "why_exists": proposal.why_exists,
        "proposed_by": proposal.proposed_by,
        "proposed_at": proposal.proposed_at.isoformat() if proposal.proposed_at else None,
        "affordances": proposal.affordances,
        "manifest": proposal.manifest,
        "relations": proposal.relations,
        "state": proposal.state,
        "behaviors": proposal.behaviors,
        "gap": None,  # Gap is not persisted (too large, ephemeral)
    }


def _deserialize_proposal(data: dict[str, Any]) -> HolonProposal:
    """Deserialize dict to HolonProposal."""
    proposed_at = data.get("proposed_at")
    if isinstance(proposed_at, str):
        proposed_at = datetime.fromisoformat(proposed_at)
    elif proposed_at is None:
        proposed_at = datetime.now()

    return HolonProposal(
        proposal_id=data["proposal_id"],
        content_hash=data.get("content_hash", ""),
        entity=data.get("entity", ""),
        context=data.get("context", ""),
        version=data.get("version", "0.1.0"),
        why_exists=data.get("why_exists", ""),
        proposed_by=data.get("proposed_by", ""),
        proposed_at=proposed_at,
        affordances=data.get("affordances", {}),
        manifest=data.get("manifest", {}),
        relations=data.get("relations", {}),
        state=data.get("state", {}),
        behaviors=data.get("behaviors", {}),
        gap=None,
    )


def _serialize_holon(holon: GerminatingHolon) -> dict[str, Any]:
    """Serialize GerminatingHolon to JSON-safe dict (excluding proposal)."""
    return {
        "germination_id": holon.germination_id,
        "jit_source": holon.jit_source,
        "jit_source_hash": holon.jit_source_hash,
        "usage_count": holon.usage_count,
        "success_count": holon.success_count,
        "failure_patterns": holon.failure_patterns,
        "germinated_at": holon.germinated_at.isoformat(),
        "germinated_by": holon.germinated_by,
        "promoted_at": holon.promoted_at.isoformat() if holon.promoted_at else None,
        "pruned_at": holon.pruned_at.isoformat() if holon.pruned_at else None,
        "rollback_token": holon.rollback_token,
        # Validation result (simplified)
        "validation_passed": holon.validation.passed if holon.validation else True,
        "validation_score": holon.validation.overall_score if holon.validation else 0.0,
    }


def _deserialize_holon(
    data: dict[str, Any],
    proposal: HolonProposal,
    validation: ValidationResult | None = None,
) -> GerminatingHolon:
    """Deserialize dict to GerminatingHolon."""
    germinated_at = data.get("germinated_at")
    if isinstance(germinated_at, str):
        germinated_at = datetime.fromisoformat(germinated_at)
    else:
        germinated_at = datetime.now()

    promoted_at = data.get("promoted_at")
    if isinstance(promoted_at, str):
        promoted_at = datetime.fromisoformat(promoted_at)

    pruned_at = data.get("pruned_at")
    if isinstance(pruned_at, str):
        pruned_at = datetime.fromisoformat(pruned_at)

    # Create minimal validation result if not provided
    if validation is None:
        validation = ValidationResult(
            passed=data.get("validation_passed", True),
            scores={},
        )

    return GerminatingHolon(
        germination_id=data["germination_id"],
        proposal=proposal,
        validation=validation,
        jit_source=data.get("jit_source", ""),
        jit_source_hash=data.get("jit_source_hash", ""),
        usage_count=data.get("usage_count", 0),
        success_count=data.get("success_count", 0),
        failure_patterns=data.get("failure_patterns", []),
        germinated_at=germinated_at,
        germinated_by=data.get("germinated_by", ""),
        promoted_at=promoted_at,
        pruned_at=pruned_at,
        rollback_token=data.get("rollback_token"),
    )


def _serialize_token(token: RollbackToken) -> dict[str, Any]:
    """Serialize RollbackToken to JSON-safe dict."""
    return {
        "token_id": token.token_id,
        "handle": token.handle,
        "promoted_at": token.promoted_at.isoformat(),
        "expires_at": token.expires_at.isoformat(),
        "spec_path": str(token.spec_path) if token.spec_path else None,
        "impl_path": str(token.impl_path) if token.impl_path else None,
        "spec_content": token.spec_content,
        "impl_content": token.impl_content,
    }


def _deserialize_token(data: dict[str, Any]) -> RollbackToken:
    """Deserialize dict to RollbackToken."""
    from pathlib import Path

    return RollbackToken(
        token_id=data["token_id"],
        handle=data["handle"],
        promoted_at=datetime.fromisoformat(data["promoted_at"]),
        expires_at=datetime.fromisoformat(data["expires_at"]),
        spec_path=Path(data["spec_path"]) if data.get("spec_path") else Path("."),
        impl_path=Path(data["impl_path"]) if data.get("impl_path") else Path("."),
        spec_content=data.get("spec_content", ""),
        impl_content=data.get("impl_content", ""),
    )


# === GrowthCortex ===


@dataclass
class GrowthCortex:
    """
    Bicameral persistence layer for self.grow.

    Stores:
    - Proposals (with semantic search on why_exists)
    - Nursery holons (with usage tracking)
    - Rollback tokens (with expiry)
    - Budget state (singleton)

    Integration:
    - Left Hemisphere: SQLite (source of truth)
    - Right Hemisphere: Vector store (semantic search)
    - Coherency: Ghost detection on recall

    Usage:
        cortex = GrowthCortex(bicameral)
        await cortex.init_schema()

        # Store proposal
        await cortex.store_proposal(proposal)

        # Semantic search
        results = await cortex.search_proposals("botanical garden")

        # List all
        proposals = await cortex.list_proposals(status="draft")
    """

    _bicameral: "BicameralMemory | None" = None
    _relational: "IRelationalStore | None" = None
    _embed_field: str = "why_exists"

    # Table names
    _proposals_table: str = "self_grow_proposals"
    _nursery_table: str = "self_grow_nursery"
    _tokens_table: str = "self_grow_rollback_tokens"
    _budget_table: str = "self_grow_budget"

    async def init_schema(self) -> None:
        """
        Initialize database schema via Alembic migrations.

        Ensures all self.grow tables exist before use.
        """
        from system.migrations import ensure_migrations

        await ensure_migrations()

    # === Proposals ===

    async def store_proposal(
        self,
        proposal: HolonProposal,
        status: str = "draft",
    ) -> str:
        """
        Store a proposal in the cortex.

        Args:
            proposal: The HolonProposal to store
            status: Initial status (draft, validated, germinated, promoted, pruned)

        Returns:
            proposal_id

        Side Effects:
            - Stores in relational table
            - Embeds why_exists in vector store (if bicameral configured)
        """
        now = datetime.now().isoformat()
        data = _serialize_proposal(proposal)

        if self._bicameral:
            # Use bicameral for dual-hemisphere storage
            await self._bicameral.store(
                id=proposal.proposal_id,
                data={
                    **data,
                    "status": status,
                    "context": proposal.context,
                    "entity": proposal.entity,
                },
                table=self._proposals_table,
                embed_field=self._embed_field,
            )
        elif self._relational:
            # Fallback to relational-only
            await self._relational.execute(
                f"""
                INSERT INTO {self._proposals_table}
                (id, data, content_hash, context, entity, proposed_by, proposed_at, status, created_at, updated_at)
                VALUES (:id, :data, :content_hash, :context, :entity, :proposed_by, :proposed_at, :status, :created_at, :updated_at)
                ON CONFLICT(id) DO UPDATE SET
                    data = :data,
                    content_hash = :content_hash,
                    status = :status,
                    updated_at = :updated_at
                """,
                {
                    "id": proposal.proposal_id,
                    "data": json.dumps(data),
                    "content_hash": proposal.content_hash,
                    "context": proposal.context,
                    "entity": proposal.entity,
                    "proposed_by": proposal.proposed_by,
                    "proposed_at": proposal.proposed_at.isoformat()
                    if proposal.proposed_at
                    else now,
                    "status": status,
                    "created_at": now,
                    "updated_at": now,
                },
            )

        return proposal.proposal_id

    async def fetch_proposal(self, proposal_id: str) -> HolonProposal | None:
        """
        Fetch a proposal by ID.

        Uses Left Hemisphere (relational) for direct lookup.
        """
        if self._bicameral:
            result = await self._bicameral.fetch(proposal_id, table=self._proposals_table)
            if result:
                return _deserialize_proposal(result)
        elif self._relational:
            row = await self._relational.fetch_one(
                f"SELECT data FROM {self._proposals_table} WHERE id = :id",
                {"id": proposal_id},
            )
            if row:
                data = json.loads(row["data"])
                return _deserialize_proposal(data)

        return None

    async def search_proposals(
        self,
        query: str,
        limit: int = 10,
        status: str | None = None,
    ) -> list[HolonProposal]:
        """
        Semantic search for proposals.

        Searches the why_exists field via Right Hemisphere (vector store).
        Validates results against Left Hemisphere (relational) for coherency.

        Args:
            query: Natural language search query
            limit: Maximum results to return
            status: Optional status filter

        Returns:
            List of matching proposals, sorted by relevance
        """
        if not self._bicameral:
            # Fallback to listing all (no semantic search without vectors)
            return await self.list_proposals(status=status, limit=limit)

        # Build filter
        filter_dict: dict[str, Any] = {"table": self._proposals_table}
        if status:
            filter_dict["status"] = status

        # Semantic search with coherency validation
        results = await self._bicameral.recall(
            query=query,
            limit=limit,
            filter=filter_dict,
        )

        proposals = []
        for result in results:
            if result.data:
                proposal = _deserialize_proposal(result.data)
                proposals.append(proposal)

        return proposals

    async def list_proposals(
        self,
        status: str | None = None,
        context: str | None = None,
        limit: int = 100,
    ) -> list[HolonProposal]:
        """
        List proposals with optional filters.

        Uses Left Hemisphere (relational) for listing.
        """
        conditions = []
        params: dict[str, Any] = {}

        if status:
            conditions.append("status = :status")
            params["status"] = status

        if context:
            conditions.append("context = :context")
            params["context"] = context

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return []

        rows = await store.fetch_all(
            f"""
            SELECT data FROM {self._proposals_table}
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit
            """,
            {**params, "limit": limit},
        )

        proposals = []
        for row in rows:
            data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
            proposals.append(_deserialize_proposal(data))

        return proposals

    async def update_proposal_status(self, proposal_id: str, status: str) -> bool:
        """Update proposal status."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        affected = await store.execute(
            f"""
            UPDATE {self._proposals_table}
            SET status = :status, updated_at = :updated_at
            WHERE id = :id
            """,
            {"id": proposal_id, "status": status, "updated_at": now},
        )
        return affected > 0

    async def delete_proposal(self, proposal_id: str) -> bool:
        """Delete a proposal."""
        if self._bicameral:
            return await self._bicameral.delete(proposal_id, table=self._proposals_table)
        elif self._relational:
            affected = await self._relational.execute(
                f"DELETE FROM {self._proposals_table} WHERE id = :id",
                {"id": proposal_id},
            )
            return affected > 0
        return False

    # === Nursery ===

    async def store_holon(self, holon: GerminatingHolon) -> str:
        """Store a germinating holon."""
        now = datetime.now().isoformat()
        data = _serialize_holon(holon)
        handle = f"{holon.proposal.context}.{holon.proposal.entity}"

        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return holon.germination_id

        await store.execute(
            f"""
            INSERT INTO {self._nursery_table}
            (id, proposal_id, data, handle, usage_count, success_count, failure_patterns,
             germinated_by, germinated_at, promoted_at, pruned_at, rollback_token, created_at, updated_at)
            VALUES (:id, :proposal_id, :data, :handle, :usage_count, :success_count, :failure_patterns,
                    :germinated_by, :germinated_at, :promoted_at, :pruned_at, :rollback_token, :created_at, :updated_at)
            ON CONFLICT(id) DO UPDATE SET
                data = :data,
                usage_count = :usage_count,
                success_count = :success_count,
                failure_patterns = :failure_patterns,
                promoted_at = :promoted_at,
                pruned_at = :pruned_at,
                rollback_token = :rollback_token,
                updated_at = :updated_at
            """,
            {
                "id": holon.germination_id,
                "proposal_id": holon.proposal.proposal_id,
                "data": json.dumps(data),
                "handle": handle,
                "usage_count": holon.usage_count,
                "success_count": holon.success_count,
                "failure_patterns": json.dumps(holon.failure_patterns),
                "germinated_by": holon.germinated_by,
                "germinated_at": holon.germinated_at.isoformat(),
                "promoted_at": holon.promoted_at.isoformat() if holon.promoted_at else None,
                "pruned_at": holon.pruned_at.isoformat() if holon.pruned_at else None,
                "rollback_token": holon.rollback_token,
                "created_at": now,
                "updated_at": now,
            },
        )

        return holon.germination_id

    async def fetch_holon(self, germination_id: str) -> GerminatingHolon | None:
        """Fetch a germinating holon by ID."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return None

        row = await store.fetch_one(
            f"""
            SELECT n.data, n.proposal_id, p.data as proposal_data
            FROM {self._nursery_table} n
            JOIN {self._proposals_table} p ON n.proposal_id = p.id
            WHERE n.id = :id
            """,
            {"id": germination_id},
        )

        if not row:
            return None

        holon_data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
        proposal_data = (
            json.loads(row["proposal_data"])
            if isinstance(row["proposal_data"], str)
            else row["proposal_data"]
        )

        proposal = _deserialize_proposal(proposal_data)
        return _deserialize_holon(holon_data, proposal)

    async def fetch_holon_by_handle(self, handle: str) -> GerminatingHolon | None:
        """Fetch a germinating holon by handle (context.entity)."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return None

        row = await store.fetch_one(
            f"""
            SELECT n.data, n.proposal_id, p.data as proposal_data
            FROM {self._nursery_table} n
            JOIN {self._proposals_table} p ON n.proposal_id = p.id
            WHERE n.handle = :handle AND n.promoted_at IS NULL AND n.pruned_at IS NULL
            """,
            {"handle": handle},
        )

        if not row:
            return None

        holon_data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
        proposal_data = (
            json.loads(row["proposal_data"])
            if isinstance(row["proposal_data"], str)
            else row["proposal_data"]
        )

        proposal = _deserialize_proposal(proposal_data)
        return _deserialize_holon(holon_data, proposal)

    async def list_nursery(
        self,
        active_only: bool = True,
        limit: int = 100,
    ) -> list[GerminatingHolon]:
        """List nursery holons."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return []

        where = "n.promoted_at IS NULL AND n.pruned_at IS NULL" if active_only else "1=1"

        rows = await store.fetch_all(
            f"""
            SELECT n.data, n.proposal_id, p.data as proposal_data
            FROM {self._nursery_table} n
            JOIN {self._proposals_table} p ON n.proposal_id = p.id
            WHERE {where}
            ORDER BY n.created_at DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

        holons = []
        for row in rows:
            holon_data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
            proposal_data = (
                json.loads(row["proposal_data"])
                if isinstance(row["proposal_data"], str)
                else row["proposal_data"]
            )

            proposal = _deserialize_proposal(proposal_data)
            holons.append(_deserialize_holon(holon_data, proposal))

        return holons

    async def update_usage(
        self,
        germination_id: str,
        success: bool,
        failure_pattern: str | None = None,
    ) -> bool:
        """Update usage statistics for a holon."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        # First fetch current state
        row = await store.fetch_one(
            f"SELECT usage_count, success_count, failure_patterns FROM {self._nursery_table} WHERE id = :id",
            {"id": germination_id},
        )

        if not row:
            return False

        usage_count = row["usage_count"] + 1
        success_count = row["success_count"] + (1 if success else 0)

        failure_patterns = json.loads(row["failure_patterns"] or "[]")
        if failure_pattern and not success:
            failure_patterns.append(failure_pattern)

        await store.execute(
            f"""
            UPDATE {self._nursery_table}
            SET usage_count = :usage_count,
                success_count = :success_count,
                failure_patterns = :failure_patterns,
                updated_at = :updated_at
            WHERE id = :id
            """,
            {
                "id": germination_id,
                "usage_count": usage_count,
                "success_count": success_count,
                "failure_patterns": json.dumps(failure_patterns),
                "updated_at": now,
            },
        )

        return True

    async def mark_promoted(self, germination_id: str, rollback_token: str) -> bool:
        """Mark a holon as promoted."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        affected = await store.execute(
            f"""
            UPDATE {self._nursery_table}
            SET promoted_at = :promoted_at, rollback_token = :rollback_token, updated_at = :updated_at
            WHERE id = :id
            """,
            {
                "id": germination_id,
                "promoted_at": now,
                "rollback_token": rollback_token,
                "updated_at": now,
            },
        )

        # Also update proposal status
        row = await store.fetch_one(
            f"SELECT proposal_id FROM {self._nursery_table} WHERE id = :id",
            {"id": germination_id},
        )
        if row:
            await self.update_proposal_status(row["proposal_id"], "promoted")

        return affected > 0

    async def mark_pruned(self, germination_id: str) -> bool:
        """Mark a holon as pruned."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        affected = await store.execute(
            f"""
            UPDATE {self._nursery_table}
            SET pruned_at = :pruned_at, updated_at = :updated_at
            WHERE id = :id
            """,
            {"id": germination_id, "pruned_at": now, "updated_at": now},
        )

        # Also update proposal status
        row = await store.fetch_one(
            f"SELECT proposal_id FROM {self._nursery_table} WHERE id = :id",
            {"id": germination_id},
        )
        if row:
            await self.update_proposal_status(row["proposal_id"], "pruned")

        return affected > 0

    # === Rollback Tokens ===

    async def store_rollback_token(self, token: RollbackToken) -> str:
        """Store a rollback token."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return token.token_id

        await store.execute(
            f"""
            INSERT INTO {self._tokens_table}
            (id, handle, promoted_at, expires_at, spec_path, impl_path, spec_content, impl_content, created_at)
            VALUES (:id, :handle, :promoted_at, :expires_at, :spec_path, :impl_path, :spec_content, :impl_content, :created_at)
            ON CONFLICT(id) DO UPDATE SET
                expires_at = :expires_at,
                spec_content = :spec_content,
                impl_content = :impl_content
            """,
            {
                "id": token.token_id,
                "handle": token.handle,
                "promoted_at": token.promoted_at.isoformat(),
                "expires_at": token.expires_at.isoformat(),
                "spec_path": str(token.spec_path) if token.spec_path else None,
                "impl_path": str(token.impl_path) if token.impl_path else None,
                "spec_content": token.spec_content,
                "impl_content": token.impl_content,
                "created_at": now,
            },
        )

        return token.token_id

    async def fetch_rollback_token(self, handle: str) -> RollbackToken | None:
        """Fetch rollback token by handle."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return None

        row = await store.fetch_one(
            f"SELECT * FROM {self._tokens_table} WHERE handle = :handle ORDER BY created_at DESC LIMIT 1",
            {"handle": handle},
        )

        if not row:
            return None

        return _deserialize_token(dict(row))

    async def delete_rollback_token(self, token_id: str) -> bool:
        """Delete a rollback token."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        affected = await store.execute(
            f"DELETE FROM {self._tokens_table} WHERE id = :id",
            {"id": token_id},
        )
        return affected > 0

    async def cleanup_expired_tokens(self) -> int:
        """Delete expired rollback tokens."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return 0

        affected = await store.execute(
            f"DELETE FROM {self._tokens_table} WHERE expires_at < :now",
            {"now": now},
        )
        return affected

    # === Budget ===

    async def load_budget(self) -> GrowthBudget:
        """Load budget from cortex, or return default if not exists."""
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return GrowthBudget()

        row = await store.fetch_one(
            f"SELECT * FROM {self._budget_table} WHERE id = 'singleton'",
            {},
        )

        if not row:
            return GrowthBudget()

        config_data = json.loads(row["config"]) if row.get("config") else {}
        spent_by_op = json.loads(row["spent_by_operation"]) if row.get("spent_by_operation") else {}

        last_regen = row.get("last_regeneration")
        if isinstance(last_regen, str):
            last_regen = datetime.fromisoformat(last_regen)
        else:
            last_regen = datetime.now()

        budget = GrowthBudget(
            config=GrowthBudgetConfig(**config_data) if config_data else GrowthBudgetConfig(),
            remaining=row.get("remaining", 1.0),
            spent_this_run=row.get("spent_this_run", 0.0),
            last_regeneration=last_regen,
            spent_by_operation=spent_by_op,
        )

        # Apply time-based regeneration
        budget.regenerate()

        return budget

    async def save_budget(self, budget: GrowthBudget) -> bool:
        """Save budget to cortex."""
        now = datetime.now().isoformat()
        store = self._relational or (self._bicameral._left if self._bicameral else None)
        if not store:
            return False

        await store.execute(
            f"""
            INSERT INTO {self._budget_table}
            (id, remaining, spent_this_run, spent_by_operation, last_regeneration, config, updated_at)
            VALUES ('singleton', :remaining, :spent_this_run, :spent_by_operation, :last_regeneration, :config, :updated_at)
            ON CONFLICT(id) DO UPDATE SET
                remaining = :remaining,
                spent_this_run = :spent_this_run,
                spent_by_operation = :spent_by_operation,
                last_regeneration = :last_regeneration,
                config = :config,
                updated_at = :updated_at
            """,
            {
                "remaining": budget.remaining,
                "spent_this_run": budget.spent_this_run,
                "spent_by_operation": json.dumps(budget.spent_by_operation),
                "last_regeneration": budget.last_regeneration.isoformat(),
                "config": json.dumps(
                    {
                        "max_entropy_per_run": budget.config.max_entropy_per_run,
                        "recognize_cost": budget.config.recognize_cost,
                        "propose_cost": budget.config.propose_cost,
                        "validate_cost": budget.config.validate_cost,
                        "germinate_cost": budget.config.germinate_cost,
                        "promote_cost": budget.config.promote_cost,
                        "prune_cost": budget.config.prune_cost,
                        "regeneration_rate_per_hour": budget.config.regeneration_rate_per_hour,
                    }
                ),
                "updated_at": now,
            },
        )

        return True


# === Factory ===


def create_growth_cortex(
    bicameral: "BicameralMemory | None" = None,
    relational: "IRelationalStore | None" = None,
) -> GrowthCortex:
    """
    Create a GrowthCortex instance.

    Args:
        bicameral: BicameralMemory for dual-hemisphere storage (preferred)
        relational: IRelationalStore for relational-only storage (fallback)

    Returns:
        Configured GrowthCortex
    """
    return GrowthCortex(_bicameral=bicameral, _relational=relational)


__all__ = [
    "GrowthCortex",
    "create_growth_cortex",
]
