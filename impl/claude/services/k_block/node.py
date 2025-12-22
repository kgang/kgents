"""
K-Block AGENTESE Node: @node("self.kblock")

Wraps K-Block harness operations as an AGENTESE node.
Every dialogue session IS a K-Block. Crystallize = harness.save().

AGENTESE Paths:
- self.kblock.manifest   - Active K-Blocks and their isolation states
- self.kblock.create     - Create K-Block (lift content into isolation)
- self.kblock.save       - Commit K-Block to cosmos (escape isolation)
- self.kblock.discard    - Abandon K-Block (no cosmic effects)
- self.kblock.fork       - Create parallel editing universe
- self.kblock.merge      - Combine two K-Blocks
- self.kblock.checkpoint - Create named restore point
- self.kblock.rewind     - Restore to checkpoint
- self.kblock.thought    - Create thought K-Block (for Membrane)

The Radical Insight (Option C):
    "Every dialogue session is a K-Block.
     You edit a possible world until you crystallize.
     Crystallize = harness.save() = thoughts escape to cosmos."

Philosophy:
    "The K-Block is not where you edit a document.
     It's where you edit a possible world."

See: spec/protocols/k-block.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .core import (
    ContentDelta,
    Cosmos,
    FileOperadHarness,
    IsolationState,
    KBlock,
    KBlockId,
    generate_kblock_id,
    get_cosmos,
    get_harness,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Contracts ===


@dataclass(frozen=True)
class KBlockManifestResponse:
    """Response for K-Block manifest."""

    active_blocks: int
    blocks: list[dict[str, Any]]


@dataclass(frozen=True)
class CreateRequest:
    """Request to create a K-Block."""

    path: str


@dataclass(frozen=True)
class CreateResponse:
    """Response from K-Block creation."""

    block_id: str
    path: str
    isolation: str


@dataclass(frozen=True)
class SaveRequest:
    """Request to save a K-Block."""

    block_id: str
    reasoning: str | None = None


@dataclass(frozen=True)
class SaveResponse:
    """Response from K-Block save."""

    success: bool
    path: str
    version_id: str | None = None
    no_changes: bool = False
    error: str | None = None


@dataclass(frozen=True)
class ThoughtRequest:
    """Request to create a thought K-Block (for Membrane)."""

    content: str
    session_id: str | None = None


@dataclass(frozen=True)
class ThoughtResponse:
    """Response from thought K-Block operations."""

    block_id: str
    content: str
    isolation: str
    message_count: int


# === Rendering ===


@dataclass(frozen=True)
class KBlockManifestRendering:
    """Rendering for K-Block status."""

    blocks: list[KBlock]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kblock_manifest",
            "active_blocks": len(self.blocks),
            "blocks": [
                {
                    "id": b.id,
                    "path": b.path,
                    "isolation": b.isolation.name,
                    "is_dirty": b.is_dirty,
                    "checkpoints": len(b.checkpoints),
                    "created_at": b.created_at.isoformat(),
                    "modified_at": b.modified_at.isoformat(),
                }
                for b in self.blocks
            ],
        }

    def to_text(self) -> str:
        if not self.blocks:
            return "No active K-Blocks."
        lines = [f"Active K-Blocks ({len(self.blocks)})", ""]
        for b in self.blocks:
            state = "DIRTY" if b.is_dirty else b.isolation.name
            lines.append(f"  [{state}] {b.path} (id={b.id[:12]}...)")
        return "\n".join(lines)


# === Thought K-Block (Membrane Integration) ===


# In-memory store for thought K-Blocks (session-scoped)
# Key: session_id, Value: KBlock containing dialogue
_thought_blocks: dict[str, KBlock] = {}


def get_thought_block(session_id: str) -> KBlock | None:
    """Get thought K-Block for session."""
    return _thought_blocks.get(session_id)


def create_thought_block(session_id: str) -> KBlock:
    """Create or get thought K-Block for session.

    Every dialogue session IS a K-Block.
    Thoughts are isolated until crystallized.
    """
    if session_id in _thought_blocks:
        return _thought_blocks[session_id]

    # Create K-Block for thoughts (path is virtual)
    block = KBlock(
        id=generate_kblock_id(),
        path=f"membrane://thoughts/{session_id}",
        content="",  # Will accumulate dialogue
        base_content="",
        isolation=IsolationState.PRISTINE,
    )

    _thought_blocks[session_id] = block
    return block


def append_thought(session_id: str, role: str, content: str) -> KBlock:
    """Append a thought to the session's K-Block.

    Each message becomes part of the K-Block's content.
    The K-Block stays DIRTY until crystallized.
    """
    block = create_thought_block(session_id)

    # Format message
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"\n\n[{timestamp}] {role.upper()}: {content}"

    # Append to K-Block content
    block.set_content(block.content + formatted)

    return block


def crystallize_thoughts(session_id: str, reasoning: str | None = None) -> dict[str, Any]:
    """Crystallize thought K-Block = harness.save() for thoughts.

    This is the moment thoughts escape isolation and become
    part of the cosmos (witnessed reality).

    Returns information for Witness crystal creation.
    """
    block = _thought_blocks.get(session_id)
    if not block:
        return {"error": "No thoughts to crystallize", "success": False}

    if not block.is_dirty:
        return {"success": True, "no_changes": True}

    # Extract crystallization data
    result = {
        "success": True,
        "block_id": block.id,
        "path": block.path,
        "content": block.content,
        "content_hash": block.content_hash,
        "message_count": block.content.count("[") // 2,  # Rough count
        "created_at": block.created_at.isoformat(),
        "crystallized_at": datetime.now(UTC).isoformat(),
        "reasoning": reasoning,
    }

    # Reset the block (thoughts now in cosmos)
    block.base_content = block.content
    block.isolation = IsolationState.PRISTINE
    block.checkpoints.clear()

    return result


def discard_thoughts(session_id: str) -> bool:
    """Discard thought K-Block without crystallizing.

    All thoughts are lost. The session starts fresh.
    """
    if session_id in _thought_blocks:
        del _thought_blocks[session_id]
        return True
    return False


# === KBlockNode ===


@node(
    "self.kblock",
    description="K-Block Crown Jewel - Transactional hyperdimensional editing",
    dependencies=("harness", "cosmos"),
    contracts={
        # Perception
        "manifest": Response(KBlockManifestResponse),
        # Mutations - file K-Blocks
        "create": Contract(CreateRequest, CreateResponse),
        "save": Contract(SaveRequest, SaveResponse),
        # Mutations - thought K-Blocks (Membrane)
        "thought": Contract(ThoughtRequest, ThoughtResponse),
    },
    examples=[
        ("manifest", {}, "Show active K-Blocks"),
        ("create", {"path": "spec/protocols/witness.md"}, "Create K-Block for file"),
        ("save", {"block_id": "kb_abc123"}, "Save K-Block to cosmos"),
        ("thought", {"content": "What if we...", "session_id": "membrane-1"}, "Append thought"),
    ],
)
class KBlockNode(BaseLogosNode):
    """
    AGENTESE node for K-Block Crown Jewel.

    The K-Block is a transactional boundary around edits.
    Everything inside is isolated until committed (save) or abandoned (discard).

    The Membrane Integration (Option C):
        Every dialogue session IS a K-Block for thoughts.
        Messages accumulate in isolation.
        Crystallize = save = thoughts escape to cosmos.

    Philosophy:
        "The K-Block is not where you edit a document.
         It's where you edit a possible world."
    """

    def __init__(
        self,
        harness: FileOperadHarness | None = None,
        cosmos: Cosmos | None = None,
    ) -> None:
        """Initialize KBlockNode with optional DI."""
        self._harness = harness or get_harness()
        self._cosmos = cosmos or get_cosmos()

    @property
    def handle(self) -> str:
        return "self.kblock"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return (
                "manifest",
                "create",
                "save",
                "discard",
                "fork",
                "merge",
                "checkpoint",
                "rewind",
                "thought",  # Membrane integration
                "crystallize",  # Membrane: save thoughts
            )

        # Architects: can create and view, limited mutations
        if archetype_lower in ("architect", "artist", "researcher"):
            return (
                "manifest",
                "create",
                "save",
                "thought",
                "crystallize",
            )

        # Newcomers: read-only
        if archetype_lower in ("newcomer", "casual"):
            return ("manifest",)

        # Guest: minimal
        return ("manifest",)

    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest active K-Blocks."""
        blocks = self._harness.list_blocks()

        # Also include thought K-Blocks
        thought_block_list = list(_thought_blocks.values())

        all_blocks = blocks + thought_block_list

        return KBlockManifestRendering(blocks=all_blocks)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        aspect_name = aspect  # Avoid shadowing imported `aspect` decorator

        if aspect_name == "create":
            path = kwargs.get("path", "")
            if not path:
                return {"error": "path required"}

            block = await self._harness.create(path)
            return {
                "block_id": block.id,
                "path": block.path,
                "isolation": block.isolation.name,
                "content_preview": block.content[:200] if block.content else "",
            }

        elif aspect_name == "save":
            block_id = kwargs.get("block_id", "")
            reasoning = kwargs.get("reasoning")

            if not block_id:
                return {"error": "block_id required"}

            save_block = self._harness.get_block(KBlockId(block_id))
            if not save_block:
                return {"error": f"K-Block not found: {block_id}"}

            save_result = await self._harness.save(
                save_block,
                actor="membrane",
                reasoning=reasoning,
            )

            return {
                "success": save_result.success,
                "path": save_result.path,
                "version_id": save_result.version_id,
                "no_changes": save_result.no_changes,
                "error": save_result.error,
            }

        elif aspect_name == "discard":
            block_id = kwargs.get("block_id", "")

            if not block_id:
                return {"error": "block_id required"}

            discard_block = self._harness.get_block(KBlockId(block_id))
            if not discard_block:
                return {"error": f"K-Block not found: {block_id}"}

            await self._harness.discard(discard_block)
            return {"success": True, "discarded": block_id}

        elif aspect_name == "fork":
            block_id = kwargs.get("block_id", "")

            if not block_id:
                return {"error": "block_id required"}

            fork_block = self._harness.get_block(KBlockId(block_id))
            if not fork_block:
                return {"error": f"K-Block not found: {block_id}"}

            left, right = await self._harness.fork(fork_block)
            return {
                "left_id": left.id,
                "right_id": right.id,
                "path": left.path,
            }

        elif aspect_name == "merge":
            block_id_1 = kwargs.get("block_id_1", "")
            block_id_2 = kwargs.get("block_id_2", "")

            if not block_id_1 or not block_id_2:
                return {"error": "block_id_1 and block_id_2 required"}

            kb1 = self._harness.get_block(KBlockId(block_id_1))
            kb2 = self._harness.get_block(KBlockId(block_id_2))

            if not kb1:
                return {"error": f"K-Block not found: {block_id_1}"}
            if not kb2:
                return {"error": f"K-Block not found: {block_id_2}"}

            merge_result = await self._harness.merge(kb1, kb2)
            return {
                "success": merge_result.success,
                "block_id": merge_result.block_id,
                "has_conflicts": merge_result.has_conflicts,
                "conflict_count": merge_result.conflict_count,
                "error": merge_result.error,
            }

        elif aspect_name == "checkpoint":
            block_id = kwargs.get("block_id", "")
            name = kwargs.get("name", f"checkpoint-{datetime.now(UTC).timestamp():.0f}")

            if not block_id:
                return {"error": "block_id required"}

            cp_block = self._harness.get_block(KBlockId(block_id))
            if not cp_block:
                return {"error": f"K-Block not found: {block_id}"}

            cp_id = await self._harness.checkpoint(cp_block, name)
            return {
                "checkpoint_id": cp_id,
                "name": name,
                "block_id": block_id,
            }

        elif aspect_name == "rewind":
            block_id = kwargs.get("block_id", "")
            checkpoint_id = kwargs.get("checkpoint_id", "")

            if not block_id or not checkpoint_id:
                return {"error": "block_id and checkpoint_id required"}

            rewind_block = self._harness.get_block(KBlockId(block_id))
            if not rewind_block:
                return {"error": f"K-Block not found: {block_id}"}

            await self._harness.rewind(rewind_block, checkpoint_id)
            return {
                "success": True,
                "block_id": block_id,
                "rewound_to": checkpoint_id,
            }

        # === Thought K-Block Operations (Membrane) ===

        elif aspect_name == "thought":
            # Append thought to session's K-Block
            content = kwargs.get("content", "")
            session_id = kwargs.get("session_id", "default")
            role = kwargs.get("role", "user")

            if not content:
                return {"error": "content required"}

            thought_block = append_thought(session_id, role, content)

            return {
                "block_id": thought_block.id,
                "session_id": session_id,
                "content_length": len(thought_block.content),
                "isolation": thought_block.isolation.name,
                "is_dirty": thought_block.is_dirty,
            }

        elif aspect_name == "crystallize":
            # Crystallize = harness.save() for thoughts
            session_id = kwargs.get("session_id", "default")
            reasoning = kwargs.get("reasoning")

            crystallize_result = crystallize_thoughts(session_id, reasoning)

            # If successful, emit to Witness (will be wired later)
            if crystallize_result.get("success") and not crystallize_result.get("no_changes"):
                # TODO: Wire to Witness for actual crystal creation
                # await witness.crystallize(crystallize_result["content"], ...)
                pass

            return crystallize_result

        elif aspect_name == "discard_thoughts":
            session_id = kwargs.get("session_id", "default")
            success = discard_thoughts(session_id)
            return {"success": success, "session_id": session_id}

        else:
            return {"error": f"Unknown aspect: {aspect_name}"}


# === Exports ===

__all__ = [
    "KBlockNode",
    "KBlockManifestRendering",
    "get_thought_block",
    "create_thought_block",
    "append_thought",
    "crystallize_thoughts",
    "discard_thoughts",
]
