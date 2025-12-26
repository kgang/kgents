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

from dataclasses import dataclass, field
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
    ViewEditTrace,
    WitnessedSheaf,
    generate_kblock_id,
    get_cosmos,
    get_harness,
)
from .views import ViewType

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


@dataclass(frozen=True)
class ViewEditRequest:
    """Request to edit a K-Block via any view (Phase 3 bidirectional)."""

    block_id: str
    source_view: str  # "prose", "graph", "code", "outline"
    content: str  # New content/state
    reasoning: str | None = None


@dataclass(frozen=True)
class ViewEditResponse:
    """Response from view edit operation."""

    success: bool
    block_id: str
    source_view: str
    semantic_deltas: list[dict[str, Any]]
    content_changed: bool
    trace: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class GetRequest:
    """Request to get K-Block content."""

    block_id: str


@dataclass(frozen=True)
class GetResponse:
    """Response with full K-Block content."""

    block_id: str
    path: str
    content: str
    base_content: str
    isolation: str
    is_dirty: bool
    active_views: list[str]
    checkpoints: list[dict[str, Any]]
    # Genesis feed fields
    galois_loss: float = 0.0
    created_by: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReferencesRequest:
    """Request to get K-Block references."""

    block_id: str


@dataclass(frozen=True)
class ReferencesResponse:
    """Response with discovered references."""

    references: list[dict[str, Any]]


@dataclass(frozen=True)
class CreateZeroSeedRequest:
    """Request to create a Zero Seed K-Block."""

    layer: int  # 1-7
    kind: str  # "axiom", "value", "goal", "spec", "action", "reflection", "representation"
    content: str  # Markdown content for the node
    title: str  # Human-readable title
    lineage: list[str] = field(default_factory=list)  # Parent node IDs
    proof: dict[str, Any] | None = None  # Optional Toulmin proof


@dataclass(frozen=True)
class CreateZeroSeedResponse:
    """Response from Zero Seed K-Block creation."""

    success: bool
    block_id: str | None = None
    path: str | None = None  # zeroseed://kind/id path
    error: str | None = None


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
                    # Genesis feed fields
                    "galois_loss": b.galois_loss,
                    "created_by": b.created_by,
                    "tags": b.tags,
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
        # Get full K-Block content
        "get": Contract(GetRequest, GetResponse),
        # Mutations - file K-Blocks
        "create": Contract(CreateRequest, CreateResponse),
        "save": Contract(SaveRequest, SaveResponse),
        # Phase 3: Bidirectional view editing
        "view_edit": Contract(ViewEditRequest, ViewEditResponse),
        # Phase 3: References discovery
        "references": Contract(ReferencesRequest, ReferencesResponse),
        # Mutations - thought K-Blocks (Membrane)
        "thought": Contract(ThoughtRequest, ThoughtResponse),
        # Phase 1: Zero Seed K-Blocks
        "create_zero_seed": Contract(CreateZeroSeedRequest, CreateZeroSeedResponse),
    },
    examples=[
        ("manifest", {}, "Show active K-Blocks"),
        ("create", {"path": "spec/protocols/witness.md"}, "Create K-Block for file"),
        ("save", {"block_id": "kb_abc123"}, "Save K-Block to cosmos"),
        (
            "view_edit",
            {"block_id": "kb_abc123", "source_view": "graph", "content": "..."},
            "Edit via graph view",
        ),
        ("thought", {"content": "What if we...", "session_id": "membrane-1"}, "Append thought"),
        (
            "create_zero_seed",
            {"layer": 1, "kind": "axiom", "content": "# Core Axiom", "title": "Test Axiom"},
            "Create Zero Seed axiom",
        ),
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

            response: dict[str, Any] = {
                "block_id": block.id,
                "path": block.path,
                "isolation": block.isolation.name,
                "content_preview": block.content[:200] if block.content else "",
                "content": block.content,  # Full content for frontend
            }

            # Add not_ingested flag if content wasn't found in cosmos or sovereign store
            # Frontend should show upload UI when this is True
            if block.not_ingested:
                response["not_ingested"] = True
                response["ingest_hint"] = "Upload content via File Picker"

            # Add analysis_required flag for sovereign analysis flow gating
            # Frontend should show analysis gate when this is True
            if block.analysis_required:
                response["analysis_required"] = True

            return response

        elif aspect_name == "get":
            block_id = kwargs.get("block_id", "")

            if not block_id:
                return {"error": "block_id required"}

            get_block = self._harness.get_block(KBlockId(block_id))
            if not get_block:
                # Also check thought blocks
                for tb in _thought_blocks.values():
                    if tb.id == block_id:
                        get_block = tb
                        break

            if not get_block:
                return {"error": f"K-Block not found: {block_id}"}

            get_response = {
                "block_id": get_block.id,
                "path": get_block.path,
                "content": get_block.content,
                "base_content": get_block.base_content,
                "isolation": get_block.isolation.name,
                "is_dirty": get_block.is_dirty,
                "active_views": [vt.value for vt in get_block.active_view_types()],
                "checkpoints": [
                    {
                        "id": cp.id,
                        "name": cp.name,
                        "content_hash": cp.content_hash,
                        "created_at": cp.created_at.isoformat(),
                    }
                    for cp in get_block.checkpoints
                ],
                # Genesis feed fields
                "galois_loss": get_block.galois_loss,
                "created_by": get_block.created_by,
                "tags": get_block.tags,
            }

            # Include analysis_required if set
            if hasattr(get_block, "analysis_required") and get_block.analysis_required:
                get_response["analysis_required"] = True

            return get_response

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

        # === Phase 3: Bidirectional View Editing ===

        elif aspect_name == "view_edit":
            block_id = kwargs.get("block_id", "")
            source_view_str = kwargs.get("source_view", "prose")
            content = kwargs.get("content", "")
            reasoning = kwargs.get("reasoning")

            if not block_id:
                return ViewEditResponse(
                    success=False,
                    block_id="",
                    source_view=source_view_str,
                    semantic_deltas=[],
                    content_changed=False,
                    error="block_id required",
                )

            # Get the K-Block
            edit_block = self._harness.get_block(KBlockId(block_id))
            if not edit_block:
                return ViewEditResponse(
                    success=False,
                    block_id=block_id,
                    source_view=source_view_str,
                    semantic_deltas=[],
                    content_changed=False,
                    error=f"K-Block not found: {block_id}",
                )

            # Parse view type
            try:
                source_view = ViewType(source_view_str)
            except ValueError:
                return ViewEditResponse(
                    success=False,
                    block_id=block_id,
                    source_view=source_view_str,
                    semantic_deltas=[],
                    content_changed=False,
                    error=f"Invalid view type: {source_view_str}",
                )

            # Check if view is editable
            sheaf = WitnessedSheaf(edit_block, actor="membrane")
            if not sheaf.can_edit_view(source_view):
                return ViewEditResponse(
                    success=False,
                    block_id=block_id,
                    source_view=source_view_str,
                    semantic_deltas=[],
                    content_changed=False,
                    error=f"View {source_view_str} is read-only",
                )

            # Activate view if not already active
            if source_view not in edit_block.views:
                edit_block.activate_view(source_view)

            try:
                # Perform witnessed propagation
                old_content = edit_block.content
                changes = sheaf.propagate(
                    source_view,
                    content,
                    reasoning=reasoning,
                )

                # Get trace from changes
                trace = changes.get(source_view, {}).get("trace")
                deltas = changes.get(source_view, {}).get("semantic_deltas", [])

                return ViewEditResponse(
                    success=True,
                    block_id=block_id,
                    source_view=source_view_str,
                    semantic_deltas=deltas,
                    content_changed=old_content != edit_block.content,
                    trace=trace,
                )

            except Exception as e:
                return ViewEditResponse(
                    success=False,
                    block_id=block_id,
                    source_view=source_view_str,
                    semantic_deltas=[],
                    content_changed=False,
                    error=str(e),
                )

        # === Phase 3: References Discovery ===

        elif aspect_name == "references":
            block_id = kwargs.get("block_id", "")

            if not block_id:
                return {"error": "block_id required", "references": []}

            ref_block = self._harness.get_block(KBlockId(block_id))
            if not ref_block:
                return {"error": f"K-Block not found: {block_id}", "references": []}

            # Activate REFERENCES view if not active
            if ViewType.REFERENCES not in ref_block.views:
                ref_block.activate_view(ViewType.REFERENCES)

            # Get references from the view
            refs_view = ref_block.views.get(ViewType.REFERENCES)
            if refs_view and hasattr(refs_view, "references"):
                references = [
                    {
                        "kind": ref.kind,
                        "target": ref.target,
                        "context": ref.context,
                        "line_number": ref.line_number,
                        "confidence": ref.confidence,
                        "stale": ref.stale,
                        "exists": ref.exists,
                    }
                    for ref in refs_view.references
                ]
            else:
                references = []

            return {"references": references}

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

        # === Phase 1: Zero Seed K-Block Creation ===

        elif aspect_name == "create_zero_seed":
            # Create a Zero Seed K-Block (derivation DAG node)
            layer = kwargs.get("layer")
            kind = kwargs.get("kind")
            content = kwargs.get("content", "")
            title = kwargs.get("title", "")
            lineage = kwargs.get("lineage", [])
            proof = kwargs.get("proof")

            # Validate required fields
            if layer is None:
                return CreateZeroSeedResponse(
                    success=False,
                    error="layer required (1-7)",
                )
            if not kind:
                return CreateZeroSeedResponse(
                    success=False,
                    error="kind required (axiom, value, goal, spec, action, reflection, representation)",
                )
            if not title:
                return CreateZeroSeedResponse(
                    success=False,
                    error="title required",
                )

            # Validate layer range
            if not 1 <= layer <= 7:
                return CreateZeroSeedResponse(
                    success=False,
                    error=f"layer must be 1-7, got {layer}",
                )

            # Validate kind
            valid_kinds = {
                "axiom",
                "value",
                "goal",
                "spec",
                "action",
                "reflection",
                "representation",
            }
            if kind not in valid_kinds:
                return CreateZeroSeedResponse(
                    success=False,
                    error=f"Invalid kind '{kind}'. Must be one of: {valid_kinds}",
                )

            try:
                # Create K-Block with Zero Seed metadata
                from uuid import uuid4

                block_id = generate_kblock_id()
                path = f"zeroseed://{kind}/{uuid4().hex[:8]}"

                zero_seed_block = KBlock(
                    id=block_id,
                    path=path,
                    content=content,
                    base_content=content,
                    isolation=IsolationState.PRISTINE,
                    # Zero Seed fields
                    zero_seed_layer=layer,
                    zero_seed_kind=kind,
                    lineage=lineage,
                    has_proof=proof is not None,
                    toulmin_proof=proof,
                )

                # Register with harness (so it appears in manifest)
                self._harness._blocks[block_id] = zero_seed_block

                return CreateZeroSeedResponse(
                    success=True,
                    block_id=block_id,
                    path=path,
                )

            except Exception as e:
                return CreateZeroSeedResponse(
                    success=False,
                    error=str(e),
                )

        else:
            return {"error": f"Unknown aspect: {aspect_name}"}


# === Exports ===

__all__ = [
    "KBlockNode",
    "KBlockManifestRendering",
    # Contracts
    "ViewEditRequest",
    "ViewEditResponse",
    "CreateZeroSeedRequest",
    "CreateZeroSeedResponse",
    # Thought K-Block helpers
    "get_thought_block",
    "create_thought_block",
    "append_thought",
    "crystallize_thoughts",
    "discard_thoughts",
]
