"""
self.grow.germinate - Holon Germination

Germinates validated proposals into the nursery where they
can be used experimentally before full promotion.

AGENTESE: self.grow.germinate
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode, BasicRendering, Renderable
from .exceptions import AffordanceError, BudgetExhaustedError, ValidationError
from .nursery import NurseryNode
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GerminatingHolon,
    GrowthBudget,
    HolonProposal,
    ValidationResult,
)
from .telemetry import metrics, tracer
from .validate import validate_proposal

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from ...logos import Logos


# === JIT Source Generation ===


def generate_jit_source(
    proposal: HolonProposal,
) -> str:
    """
    Generate JIT source code from a proposal.

    Creates a minimal LogosNode implementation that can be
    loaded at runtime.

    Args:
        proposal: The proposal to generate source from

    Returns:
        Python source code for the node
    """
    handle = f"{proposal.context}.{proposal.entity}"
    class_name = "".join(word.title() for word in proposal.entity.split("_")) + "Node"

    # Generate affordances dict
    affordance_lines = []
    for archetype, verbs in proposal.affordances.items():
        verb_str = ", ".join(f'"{v}"' for v in verbs)
        affordance_lines.append(f'        "{archetype}": ({verb_str}),')
    affordances_dict = "{\n" + "\n".join(affordance_lines) + "\n    }"

    # Generate behavior methods
    behavior_methods = []
    for aspect, description in proposal.behaviors.items():
        method_name = f"_handle_{aspect}"
        behavior_methods.append(
            f'''
    async def {method_name}(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        {description}
        """
        return {{
            "aspect": "{aspect}",
            "handle": self.handle,
            "status": "executed",
        }}'''
        )

    # Generate case statements for behavior dispatch
    case_statements = []
    for aspect in proposal.behaviors:
        method_name = f"_handle_{aspect}"
        case_statements.append(
            f'            case "{aspect}":\n                return await self.{method_name}(observer, **kwargs)'
        )

    case_block = (
        "\n".join(case_statements)
        if case_statements
        else '            case _:\n                return {"aspect": aspect, "status": "not implemented"}'
    )

    source = f'''"""
JIT-generated LogosNode for {handle}

Generated from proposal: {proposal.proposal_id}
Content hash: {proposal.content_hash}

{proposal.why_exists}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


AFFORDANCES = {affordances_dict}


@dataclass
class {class_name}(BaseLogosNode):
    """
    {handle} - JIT generated node.

    {proposal.why_exists}
    """

    _handle: str = "{handle}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return AFFORDANCES.get(archetype, AFFORDANCES.get("default", ()))

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary="{handle}",
            content="{proposal.why_exists}",
            metadata={{"jit_generated": True, "proposal_id": "{proposal.proposal_id}"}},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        match aspect:
{case_block}
            case _:
                return {{"aspect": aspect, "status": "not implemented"}}
{"".join(behavior_methods)}


# Factory function
def create_node() -> {class_name}:
    return {class_name}()
'''

    return source


# === Germinate Node ===


@dataclass
class GerminateNode(BaseLogosNode):
    """
    self.grow.germinate - Holon germination node.

    Germinates validated proposals into the nursery.

    Affordances:
    - manifest: View recent germinations
    - seed: Germinate a validated proposal
    - status: Get germination status

    AGENTESE: self.grow.germinate.*
    """

    _handle: str = "self.grow.germinate"

    # Integration points
    _logos: "Logos | None" = None
    _budget: GrowthBudget | None = None
    _nursery: NurseryNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Germination requires gardener or architect affordance."""
        affordances = SELF_GROW_AFFORDANCES.get(archetype, ())
        if "germinate" in affordances:
            return ("seed", "status")
        return ("status",)  # Read-only for others

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View germination status."""
        if self._nursery is None:
            return BasicRendering(
                summary="Germination (no nursery)",
                content="Nursery not configured",
                metadata={"error": "no_nursery"},
            )

        return BasicRendering(
            summary=f"Germination: {self._nursery.count} active",
            content=f"Nursery: {self._nursery.count}/{self._nursery._config.max_capacity}",
            metadata={
                "nursery_count": self._nursery.count,
                "nursery_capacity": self._nursery._config.max_capacity,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle germination aspects."""
        match aspect:
            case "seed":
                return await self._seed(observer, **kwargs)
            case "status":
                return self._status(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _seed(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Germinate a validated proposal.

        Args:
            proposal: HolonProposal to germinate
            validation: Optional ValidationResult (will validate if not provided)
            skip_validation: If True, skip validation (for testing only)

        Returns:
            Dict with germination details
        """
        meta = self._umwelt_to_meta(observer)

        # Check affordance
        if "germinate" not in SELF_GROW_AFFORDANCES.get(meta.archetype, ()):
            raise AffordanceError(
                f"Archetype '{meta.archetype}' cannot germinate",
                available=SELF_GROW_AFFORDANCES.get(meta.archetype, ()),
            )

        # Check nursery
        if self._nursery is None:
            return {"error": "Nursery not configured"}

        # Get proposal
        proposal = kwargs.get("proposal")
        if proposal is None:
            return {"error": "proposal required"}

        # Check budget
        if self._budget is not None:
            if not self._budget.can_afford("germinate"):
                raise BudgetExhaustedError(
                    "Germination budget exhausted",
                    remaining=self._budget.remaining,
                    requested=self._budget.config.germinate_cost,
                )
            self._budget.spend("germinate")

        # Validate if needed
        validation = kwargs.get("validation")
        if validation is None and not kwargs.get("skip_validation", False):
            validation = await validate_proposal(proposal, logos=self._logos)

        if validation is not None and not validation.passed:
            raise ValidationError(
                "Proposal failed validation",
                blockers=validation.blockers,
            )

        async with tracer.start_span_async("growth.germinate") as span:
            span.set_attribute("growth.phase", "germinate")
            span.set_attribute("growth.proposal.handle", f"{proposal.context}.{proposal.entity}")
            span.set_attribute("growth.proposal.hash", proposal.content_hash)

            # Generate JIT source
            jit_source = generate_jit_source(proposal)
            span.set_attribute("growth.germination.jit_source_len", len(jit_source))

            # Add to nursery
            holon = self._nursery.add(
                proposal=proposal,
                validation=validation or ValidationResult(passed=True),
                germinated_by=meta.name,
                jit_source=jit_source,
            )

            span.set_attribute("growth.germination.id", holon.germination_id)

            # Record metrics
            metrics.counter("growth.germinate.invocations").add(1)
            metrics.gauge("growth.nursery.count").set(self._nursery.count)

        return {
            "status": "germinated",
            "germination_id": holon.germination_id,
            "handle": f"{proposal.context}.{proposal.entity}",
            "nursery_count": self._nursery.count,
            "jit_source_lines": len(jit_source.splitlines()),
        }

    def _status(self, **kwargs: Any) -> dict[str, Any]:
        """Get germination status."""
        if self._nursery is None:
            return {"error": "Nursery not configured"}

        germination_id = kwargs.get("germination_id")
        handle = kwargs.get("handle")

        if germination_id or handle:
            # Get specific holon status
            if germination_id:
                holon = self._nursery.get(germination_id)
            else:
                holon = self._nursery.get_by_handle(handle)

            if holon is None:
                return {"error": "Holon not found"}

            return {
                "germination_id": holon.germination_id,
                "handle": f"{holon.proposal.context}.{holon.proposal.entity}",
                "usage_count": holon.usage_count,
                "success_rate": holon.success_rate,
                "age_days": holon.age_days,
                "should_promote": holon.should_promote(self._nursery._config),
            }

        # General status
        return {
            "nursery_count": self._nursery.count,
            "nursery_capacity": self._nursery._config.max_capacity,
            "ready_for_promotion": len(self._nursery.get_ready_for_promotion()),
            "ready_for_pruning": len(self._nursery.get_ready_for_pruning()),
        }


# === Factory ===


def create_germinate_node(
    logos: "Logos | None" = None,
    budget: GrowthBudget | None = None,
    nursery: NurseryNode | None = None,
) -> GerminateNode:
    """
    Create a GerminateNode with optional configuration.

    Args:
        logos: Logos instance for validation
        budget: Growth budget for entropy tracking
        nursery: NurseryNode for holon storage

    Returns:
        Configured GerminateNode
    """
    return GerminateNode(
        _logos=logos,
        _budget=budget,
        _nursery=nursery,
    )
