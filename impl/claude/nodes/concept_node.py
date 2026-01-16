"""
AGENTESE Node for concept.* - Prompts and Specifications (L3-L4)

The concept namespace represents goals and their formalization. These are
derived artifacts with witnessed proofs, built on top of the void foundation.

L3 (Prompt): Template with parameters, derived from values/specs
L4 (Spec): Formal specification, derived from values and prompts

AGENTESE Paths:
- concept.prompt.list - List prompt templates
- concept.prompt.get - Get prompt by ID
- concept.prompt.create - Create prompt template
- concept.prompt.instantiate - Create invocation from template
- concept.spec.list - List specifications
- concept.spec.get - Get spec by ID
- concept.spec.create - Create specification
- concept.manifest - Show concept layer status

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: spec/protocols/zero-seed.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from agents.d.schemas.prompt import InvocationCrystal, PromptCrystal, PromptParam
from agents.d.schemas.proof import GaloisWitnessedProof
from agents.d.universe.universe import Query, Universe, UniverseStats
from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import BaseLogosNode, BasicRendering, Observer, Renderable
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Concept Response Contracts ===


@dataclass(frozen=True)
class ConceptManifestResponse:
    """Response for concept.manifest."""

    total_prompts: int
    total_specs: int
    total_invocations: int
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_prompts": self.total_prompts,
            "total_specs": self.total_specs,
            "total_invocations": self.total_invocations,
            "backend": self.backend,
        }


@dataclass(frozen=True)
class PromptListRequest:
    """Request for concept.prompt.list."""

    version: int | None = None
    created_by: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class PromptListResponse:
    """Response for concept.prompt.list."""

    prompts: list[PromptCrystal]
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompts": [p.to_dict() for p in self.prompts],
            "count": self.count,
        }


@dataclass(frozen=True)
class PromptGetRequest:
    """Request for concept.prompt.get."""

    id: str


@dataclass(frozen=True)
class PromptGetResponse:
    """Response for concept.prompt.get."""

    prompt: PromptCrystal | None

    def to_dict(self) -> dict[str, Any]:
        return {"prompt": self.prompt.to_dict() if self.prompt else None}


@dataclass(frozen=True)
class PromptCreateRequest:
    """Request for concept.prompt.create."""

    template: str
    parameters: dict[str, dict[str, Any]]
    goal_statement: str
    derived_from: list[str]
    created_by: str


@dataclass(frozen=True)
class PromptCreateResponse:
    """Response for concept.prompt.create."""

    prompt_id: str
    prompt: PromptCrystal

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "prompt": self.prompt.to_dict(),
        }


@dataclass(frozen=True)
class PromptInstantiateRequest:
    """Request for concept.prompt.instantiate."""

    prompt_id: str
    parameters: dict[str, Any]
    executor: str


@dataclass(frozen=True)
class PromptInstantiateResponse:
    """Response for concept.prompt.instantiate."""

    invocation_id: str
    invocation: InvocationCrystal

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "invocation": self.invocation.to_dict(),
        }


# Note: Spec operations would be here for L4, but we don't have SpecCrystal yet.
# For now, we'll focus on prompts (L3) and invocations (L5).


# === Concept Rendering ===


@dataclass(frozen=True)
class ConceptManifestRendering:
    """Rendering for concept.manifest."""

    total_prompts: int
    total_specs: int
    total_invocations: int
    backend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "concept_manifest",
            "total_prompts": self.total_prompts,
            "total_specs": self.total_specs,
            "total_invocations": self.total_invocations,
            "backend": self.backend,
        }

    def to_text(self) -> str:
        lines = [
            "Concept Layer - Goals and Formalization",
            "========================================",
            f"Backend: {self.backend}",
            f"Total Prompts: {self.total_prompts}",
            f"Total Specs: {self.total_specs}",
            f"Total Invocations: {self.total_invocations}",
        ]
        return "\n".join(lines)


# === Concept Affordances ===

CONCEPT_AFFORDANCES: tuple[str, ...] = (
    "prompt.list",  # List prompts
    "prompt.get",  # Get prompt by ID
    "spec.list",  # List specs
    "spec.get",  # Get spec by ID
)

# Developer/operator affordances (creation)
CONCEPT_ADMIN_AFFORDANCES: tuple[str, ...] = CONCEPT_AFFORDANCES + (
    "prompt.create",  # Create prompt
    "prompt.instantiate",  # Instantiate prompt
    "spec.create",  # Create spec
)


# === ConceptNode ===


@node(
    "concept",
    description="Prompts and specifications - goals and their formalization (L3-L4)",
    dependencies=("universe",),
    contracts={
        # Perception aspects
        "manifest": Response(ConceptManifestResponse),
        "prompt.list": Contract(PromptListRequest, PromptListResponse),
        "prompt.get": Contract(PromptGetRequest, PromptGetResponse),
        # Mutation aspects
        "prompt.create": Contract(PromptCreateRequest, PromptCreateResponse),
        "prompt.instantiate": Contract(PromptInstantiateRequest, PromptInstantiateResponse),
    },
    examples=[
        ("manifest", {}, "Show concept layer status"),
        ("prompt.list", {"limit": 10}, "List recent prompts"),
    ],
)
class ConceptNode(BaseLogosNode):
    """
    AGENTESE node for prompts and specifications (L3-L4).

    The concept namespace represents derived goals and formalizations:
    - Prompts: Templates with parameters (L3)
    - Specs: Formal specifications (L4)
    - Invocations: Runtime executions (L5)

    Observer gradation:
    - developer/operator: Full access including creation and instantiation
    - philosopher/scientist: Read and create access
    - guest: Read-only access

    Example:
        # Via AGENTESE gateway
        POST /agentese/concept/prompt/list
        {"limit": 10}

        # Via Logos directly
        await logos.invoke("concept.prompt.list", observer, limit=10)

        # Via CLI
        kgents concept prompt list --limit 10

    Teaching:
        gotcha: ConceptNode REQUIRES universe dependency. Without it,
                instantiation fails with TypeError—this is intentional!
                It enables Logos fallback when DI isn't configured.

        gotcha: Prompt instantiation requires developer/operator archetype.
                This creates invocation records with Galois loss tracking.
                (Evidence: affordances vary by archetype)

        gotcha: Every ConceptNode invocation emits a Mark (WARP Law 3). Don't add
                manual tracing—the gateway handles it at _invoke_path().
    """

    def __init__(self, universe: Universe) -> None:
        """
        Initialize ConceptNode.

        Universe is REQUIRED. When Logos tries to instantiate
        without dependencies, it will fail and fall back to a
        minimal context resolver.

        Args:
            universe: The Universe instance (injected by container)

        Raises:
            TypeError: If universe is not provided (intentional for fallback)
        """
        self._universe = universe

    @property
    def handle(self) -> str:
        return "concept"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Observer gradation:
        - developer/operator: Full access including creation
        - philosopher/scientist: Read and create
        - guest: Read-only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, admins
        if archetype_lower in ("developer", "operator", "admin", "system"):
            return CONCEPT_ADMIN_AFFORDANCES

        # Philosophers/scientists: read and create
        if archetype_lower in ("philosopher", "scientist", "researcher"):
            return CONCEPT_ADMIN_AFFORDANCES

        # Architects: read-only
        if archetype_lower in ("architect", "technical"):
            return CONCEPT_AFFORDANCES

        # Guest (default): read-only
        return CONCEPT_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("universe")],
        help="Display concept layer status (prompts, specs, invocations)",
        examples=["kg concept", "kg concept manifest"],
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest concept layer status to observer.

        AGENTESE: concept.manifest
        """
        if self._universe is None:
            return BasicRendering(
                summary="Concept layer not initialized",
                content="No Universe configured",
                metadata={"error": "no_universe"},
            )

        # Query for prompts, specs, and invocations
        prompt_query = Query(schema="concept.prompt", limit=1000)
        invocation_query = Query(schema="concept.invocation", limit=1000)

        prompts = await self._universe.query(prompt_query)
        invocations = await self._universe.query(invocation_query)

        # Specs not implemented yet (L4)
        total_specs = 0

        stats = await self._universe.stats()

        return ConceptManifestRendering(
            total_prompts=len(prompts),
            total_specs=total_specs,
            total_invocations=len(invocations),
            backend=stats.backend,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to Universe methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._universe is None:
            return {"error": "Universe not configured"}

        # Route to appropriate method
        if aspect == "prompt.list":
            version = kwargs.get("version")
            created_by = kwargs.get("created_by")
            limit = kwargs.get("limit", 100)

            # Build query
            q = Query(schema="concept.prompt", limit=limit)
            results = await self._universe.query(q)

            # Filter by version and created_by
            filtered = results
            if version is not None:
                filtered = [p for p in filtered if p.version == version]
            if created_by:
                filtered = [p for p in filtered if p.created_by == created_by]

            return {"prompts": filtered, "count": len(filtered)}

        elif aspect == "prompt.get":
            prompt_id = kwargs.get("id")
            if not prompt_id:
                return {"error": "id required"}

            prompt = await self._universe.get(prompt_id)
            return {"prompt": prompt}

        elif aspect == "prompt.create":
            template = kwargs.get("template")
            parameters = kwargs.get("parameters", {})
            goal_statement = kwargs.get("goal_statement")
            derived_from = kwargs.get("derived_from", [])
            created_by = kwargs.get("created_by", "system")

            if not template or not goal_statement:
                return {"error": "template and goal_statement required"}

            # Convert parameter dicts to PromptParam objects
            param_objects = {
                name: PromptParam.from_dict(param_dict) for name, param_dict in parameters.items()
            }

            # Create a minimal proof (would be more sophisticated in production)
            proof = GaloisWitnessedProof(
                layers=tuple(derived_from),
                witness_id=f"proof:{created_by}:{datetime.now(UTC).isoformat()}",
                loss=0.0,  # Would be calculated by Zero Seed service
                confidence=1.0,
                timestamp=datetime.now(UTC),
            )

            prompt = PromptCrystal(
                template=template,
                parameters=param_objects,
                goal_statement=goal_statement,
                derived_from=tuple(derived_from),
                version=1,  # Initial version
                created_by=created_by,
                proof=proof,
            )

            prompt_id = await self._universe.store(prompt, "concept.prompt")
            return {"prompt_id": prompt_id, "prompt": prompt}

        elif aspect == "prompt.instantiate":
            prompt_id = kwargs.get("prompt_id")
            parameters = kwargs.get("parameters", {})
            executor = kwargs.get("executor", "system")

            if not prompt_id:
                return {"error": "prompt_id required"}

            # Get the prompt
            prompt = await self._universe.get(prompt_id)
            if not isinstance(prompt, PromptCrystal):
                return {"error": "Prompt not found"}

            # Create invocation record
            # In production, this would actually execute the prompt
            # For now, we just create the record
            proof = GaloisWitnessedProof(
                layers=(prompt_id,),
                witness_id=f"invocation:{executor}:{datetime.now(UTC).isoformat()}",
                loss=0.0,  # Would be calculated during execution
                confidence=1.0,
                timestamp=datetime.now(UTC),
            )

            invocation = InvocationCrystal(
                prompt_id=prompt_id,
                parameters=parameters,
                timestamp=datetime.now(UTC),
                executor=executor,
                output_id=None,  # Would be set if output was generated
                success=True,  # Placeholder
                duration_ms=0,  # Placeholder
                token_count=0,  # Placeholder
                galois_loss_input=0.0,  # Would be calculated
                galois_loss_output=0.0,  # Would be calculated
                proof=proof,
            )

            invocation_id = await self._universe.store(invocation, "concept.invocation")
            return {"invocation_id": invocation_id, "invocation": invocation}

        elif aspect == "spec.list":
            # Placeholder for L4 specs
            return {"specs": [], "count": 0}

        elif aspect == "spec.get":
            # Placeholder for L4 specs
            return {"spec": None}

        elif aspect == "spec.create":
            # Placeholder for L4 specs
            return {"error": "Spec creation not yet implemented"}

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "ConceptNode",
    "ConceptManifestRendering",
    "ConceptManifestResponse",
    "PromptListRequest",
    "PromptListResponse",
    "PromptGetRequest",
    "PromptGetResponse",
    "PromptCreateRequest",
    "PromptCreateResponse",
    "PromptInstantiateRequest",
    "PromptInstantiateResponse",
]
