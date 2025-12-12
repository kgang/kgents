"""
AGENTESE Void Context Resolver

The Accursed Share: entropy, noise, slop, serendipity, gratitude.

void.* handles provide access to randomness and serendipity:
- void.entropy - Draw/return randomness
- void.serendipity - Request tangential discoveries
- void.gratitude - Express thanks, pay tithes

The void is always accessible to all agents.

Principle Alignment: Meta-Principle (gratitude for waste)

See: Bataille's Accursed Share
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from shared.capital import BypassToken, EventSourcedLedger, InsufficientCapitalError
from shared.melting import ContractViolationError, MeltingContext, meltable

from ..exceptions import BudgetExhaustedError
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Entropy Pool ===


@dataclass
class EntropyPool:
    """
    The Accursed Share entropy budget.

    Agents can sip from the pool (draw randomness) and pour back
    (return unused randomness). The pool regenerates over time.

    The Accursed Share: surplus that must be spent
    lest it accumulate destructively.
    """

    initial_budget: float = 100.0
    remaining: float = 100.0
    regeneration_rate: float = 0.1  # Per access

    # History for witness
    _history: list[dict[str, Any]] = field(default_factory=list)
    _random: random.Random = field(default_factory=lambda: random.Random())

    def sip(self, amount: float) -> dict[str, Any]:
        """
        Draw entropy from the pool.

        Args:
            amount: Amount to draw (0.0-1.0 typical)

        Returns:
            Grant with seed and amount

        Raises:
            BudgetExhaustedError: If insufficient entropy
        """
        if amount > self.remaining:
            raise BudgetExhaustedError(
                f"Requested {amount:.2f} but only {self.remaining:.2f} remaining",
                remaining=self.remaining,
                requested=amount,
            )

        self.remaining -= amount
        seed = self._random.random()

        event = {
            "action": "sip",
            "amount": amount,
            "seed": seed,
            "remaining": self.remaining,
            "timestamp": datetime.now().isoformat(),
        }
        self._history.append(event)

        return {
            "amount": amount,
            "seed": seed,
            "source": "accursed_share",
        }

    def pour(self, amount: float, recovery_rate: float = 0.5) -> dict[str, Any]:
        """
        Return unused entropy to the pool.

        Recovery is partial—entropy cannot be fully recovered.

        Args:
            amount: Amount originally drawn
            recovery_rate: Fraction recoverable (default 50%)

        Returns:
            Recovery details
        """
        recovered = amount * recovery_rate
        self.remaining = min(self.initial_budget, self.remaining + recovered)

        event = {
            "action": "pour",
            "returned": amount,
            "recovered": recovered,
            "remaining": self.remaining,
            "timestamp": datetime.now().isoformat(),
        }
        self._history.append(event)

        return {
            "returned": amount,
            "recovered": recovered,
            "remaining": self.remaining,
        }

    def tithe(self) -> dict[str, Any]:
        """
        Pay for order via noop sacrifice.

        The tithe is gratitude in action—acknowledging
        that order comes from chaos.
        """
        # Small regeneration as reward for gratitude
        self.remaining = min(
            self.initial_budget, self.remaining + self.regeneration_rate
        )

        event = {
            "action": "tithe",
            "regenerated": self.regeneration_rate,
            "remaining": self.remaining,
            "timestamp": datetime.now().isoformat(),
        }
        self._history.append(event)

        return {
            "gratitude": "The river flows.",
            "regenerated": self.regeneration_rate,
        }

    def sample(self) -> float:
        """Get a random sample without consuming budget."""
        return self._random.random()

    @property
    def history(self) -> list[dict[str, Any]]:
        """Return entropy transaction history."""
        return list(self._history)


# === Randomness Grant ===


@dataclass
class RandomnessGrant:
    """
    A grant of randomness from the Accursed Share.

    Can be used and then poured back if unused.
    """

    amount: float
    seed: float
    source: str = "accursed_share"
    used: bool = False

    def use(self) -> float:
        """Use the grant's seed value."""
        self.used = True
        return self.seed

    def as_int(self, max_value: int = 100) -> int:
        """Convert seed to integer in range [0, max_value)."""
        self.used = True
        return int(self.seed * max_value)

    def as_choice(self, options: list[Any]) -> Any:
        """Use seed to choose from options."""
        if not options:
            return None
        self.used = True
        index = int(self.seed * len(options))
        return options[min(index, len(options) - 1)]


# === Void Nodes ===


@dataclass
class EntropyNode(BaseLogosNode):
    """
    void.entropy - Access to randomness.

    Affordances:
    - sip: Draw randomness
    - pour: Return unused randomness
    - witness: View entropy history
    """

    _handle: str = "void.entropy"
    _pool: EntropyPool = field(default_factory=EntropyPool)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Everyone can interact with entropy."""
        return ("sip", "pour", "sample", "status")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View entropy pool status."""
        return BasicRendering(
            summary="Entropy Pool (Accursed Share)",
            content=f"Remaining: {self._pool.remaining:.2f} / {self._pool.initial_budget:.2f}",
            metadata={
                "remaining": self._pool.remaining,
                "initial": self._pool.initial_budget,
                "history_length": len(self._pool._history),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle entropy aspects."""
        match aspect:
            case "sip":
                amount = kwargs.get("amount", 0.1)
                return self._pool.sip(amount)
            case "pour":
                amount = kwargs.get("amount", 0.0)
                grant = kwargs.get("grant")
                if grant and isinstance(grant, RandomnessGrant) and not grant.used:
                    return self._pool.pour(grant.amount)
                if amount > 0:
                    return self._pool.pour(amount)
                return {"error": "amount or unused grant required"}
            case "sample":
                return {"sample": self._pool.sample()}
            case "status":
                return {
                    "remaining": self._pool.remaining,
                    "initial": self._pool.initial_budget,
                    "history_count": len(self._pool._history),
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


@dataclass
class SerendipityNode(BaseLogosNode):
    """
    void.serendipity - Request tangential discoveries.

    The serendipity node provides unexpected connections
    and tangential thoughts—the creative potential of chaos.
    """

    _handle: str = "void.serendipity"
    _pool: EntropyPool = field(default_factory=EntropyPool)

    # Tangent templates for generation
    _tangent_templates: tuple[str, ...] = (
        "What if {context} were actually a form of {random_concept}?",
        "Consider the relationship between {context} and {random_concept}.",
        "The opposite of {context} might teach us something.",
        "{context} is like a river—always flowing, never the same.",
        "What would {random_person} say about {context}?",
        "Instead of {context}, what about {random_concept}?",
    )

    _random_concepts: tuple[str, ...] = (
        "music",
        "architecture",
        "gardening",
        "cooking",
        "dance",
        "astronomy",
        "poetry",
        "mathematics",
        "mythology",
        "games",
        "weather",
        "dreams",
        "silence",
        "shadows",
        "echoes",
    )

    _random_persons: tuple[str, ...] = (
        "a child",
        "an elder",
        "a stranger",
        "a poet",
        "a scientist",
        "a gardener",
        "a musician",
        "a traveler",
        "a dreamer",
    )

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Everyone can seek serendipity."""
        return ("sip", "inspire", "tangent")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View serendipity potential."""
        return BasicRendering(
            summary="Serendipity Portal",
            content="The unexpected awaits. Use 'sip' to receive a tangent.",
            metadata={
                "available": True,
                "entropy_remaining": self._pool.remaining,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle serendipity aspects."""
        match aspect:
            case "sip":
                return await self._generate_tangent(observer, **kwargs)
            case "inspire":
                return await self._generate_inspiration(observer, **kwargs)
            case "tangent":
                return await self._generate_tangent(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _generate_tangent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a tangential thought."""
        context = kwargs.get("context", "the current situation")
        confidence_threshold = kwargs.get("confidence_threshold", 0.5)

        # Draw entropy
        try:
            grant = self._pool.sip(0.05)
        except BudgetExhaustedError:
            return {
                "tangent": "The void is quiet. Try void.gratitude.tithe to restore.",
                "status": "budget_exhausted",
            }

        # Generate tangent
        seed = grant["seed"]
        template_idx = int(seed * len(self._tangent_templates))
        template = self._tangent_templates[template_idx]

        random_concept = self._random_concepts[
            int(seed * 1000) % len(self._random_concepts)
        ]
        random_person = self._random_persons[
            int(seed * 1000) % len(self._random_persons)
        ]

        tangent = template.format(
            context=context,
            random_concept=random_concept,
            random_person=random_person,
        )

        return {
            "tangent": tangent,
            "confidence": 1.0 - confidence_threshold,
            "context": context,
            "seed": seed,
        }

    async def _generate_inspiration(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate an inspirational prompt."""
        domain = kwargs.get("domain", "creativity")

        try:
            grant = self._pool.sip(0.03)
        except BudgetExhaustedError:
            return {
                "inspiration": "Rest. Restore. Return.",
                "status": "budget_exhausted",
            }

        inspirations = [
            f"In {domain}, consider what you've been avoiding.",
            "What would the opposite of your current approach look like?",
            "Find three unrelated things and connect them.",
            "What would you do if failure were impossible?",
            "What constraint would actually be liberating?",
        ]

        idx = int(grant["seed"] * len(inspirations))
        return {
            "inspiration": inspirations[idx],
            "domain": domain,
        }


@dataclass
class GratitudeNode(BaseLogosNode):
    """
    void.gratitude - Express thanks, pay tithes.

    The gratitude node acknowledges that all order
    comes from chaos, all structure from entropy.
    """

    _handle: str = "void.gratitude"
    _pool: EntropyPool = field(default_factory=EntropyPool)

    # Gratitude expressions
    _expressions: tuple[str, ...] = (
        "The river flows.",
        "Gratitude.",
        "From chaos, order. From order, chaos. We are grateful.",
        "The void receives. The void gives.",
        "Thank you.",
    )

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Everyone can express gratitude."""
        return ("tithe", "thank", "acknowledge")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View gratitude interface."""
        return BasicRendering(
            summary="Gratitude Portal",
            content="To receive, first give. Use 'tithe' to restore entropy.",
            metadata={
                "entropy_remaining": self._pool.remaining,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle gratitude aspects."""
        match aspect:
            case "tithe":
                return self._pool.tithe()
            case "thank":
                return await self._thank(observer, **kwargs)
            case "acknowledge":
                return await self._acknowledge(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _thank(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Express gratitude (aesthetic operation)."""
        target = kwargs.get("target", "the void")

        idx = hash(target) % len(self._expressions)
        expression = self._expressions[idx]

        return {
            "gratitude": expression,
            "target": target,
            "status": "acknowledged",
        }

    async def _acknowledge(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Acknowledge the Accursed Share."""
        what = kwargs.get("what", "the surplus")

        return {
            "acknowledgment": f"We acknowledge {what}. It is part of us.",
            "what": what,
            "principle": "The Accursed Share: surplus must be spent.",
        }


# === Capital Node ===


@dataclass
class CapitalNode(BaseLogosNode):
    """
    void.capital - Agent capital ledger interface.

    AGENTESE access to the event-sourced capital ledger:
    - manifest: View balance (projection from events)
    - witness: View history (event stream)
    - tithe: Burn capital (potlatch ritual)
    - bypass: Mint bypass token (OCap capability)

    The Accursed Share: wealth that is not consumed will consume the community.
    """

    _handle: str = "void.capital"
    _ledger: EventSourcedLedger = field(default_factory=EventSourcedLedger)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All agents can interact with capital."""
        return ("balance", "history", "tithe", "bypass")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        AGENTESE: void.capital.manifest

        View capital balance for the observing agent.
        Balance is derived from events, not stored.
        """
        agent = self._get_agent_id(observer)
        balance = self._ledger.balance(agent)

        return BasicRendering(
            summary="Capital Ledger (Accursed Share)",
            content=f"Agent: {agent}\nBalance: {balance:.3f} / {self._ledger.max_capital:.3f}",
            metadata={
                "agent": agent,
                "balance": balance,
                "max_capital": self._ledger.max_capital,
                "initial_capital": self._ledger.initial_capital,
                "event_count": len(self._ledger.witness(agent)),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle capital aspects."""
        agent = kwargs.get("agent") or self._get_agent_id(observer)

        match aspect:
            case "balance":
                return {
                    "agent": agent,
                    "balance": self._ledger.balance(agent),
                    "max": self._ledger.max_capital,
                }
            case "history" | "witness":
                limit = kwargs.get("limit", 100)
                events = self._ledger.witness(agent, limit=limit)
                return {
                    "agent": agent,
                    "events": [
                        {
                            "type": e.event_type,
                            "amount": e.amount,
                            "timestamp": e.timestamp.isoformat(),
                            "metadata": e.metadata,
                        }
                        for e in events
                    ],
                    "count": len(events),
                }
            case "tithe":
                amount = kwargs.get("amount", 0.1)
                event = self._ledger.potlatch(agent, amount)
                if event is None:
                    raise InsufficientCapitalError(
                        "Insufficient capital for tithe",
                        agent=agent,
                        required=amount,
                        available=self._ledger.balance(agent),
                    )
                return {
                    "ritual": "potlatch",
                    "agent": agent,
                    "amount": amount,
                    "remaining": self._ledger.balance(agent),
                    "gratitude": "The river flows.",
                }
            case "bypass":
                check_name = kwargs.get("check", "trust_gate")
                cost = kwargs.get("cost", 0.1)
                ttl = kwargs.get("ttl", 60.0)
                token = self._ledger.mint_bypass(agent, check_name, cost, ttl)
                if token is None:
                    raise InsufficientCapitalError(
                        "Insufficient capital for bypass",
                        agent=agent,
                        required=cost,
                        available=self._ledger.balance(agent),
                    )
                return {
                    "token": token,
                    "agent": agent,
                    "check": check_name,
                    "cost": cost,
                    "expires_at": token.expires_at.isoformat(),
                    "remaining": self._ledger.balance(agent),
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def _get_agent_id(self, observer: "Umwelt[Any, Any]") -> str:
        """Extract agent ID from Umwelt's DNA."""
        dna = observer.dna
        return getattr(dna, "name", "unknown")


# === Pataphysics Node ===


@dataclass
class PataphysicsNode(BaseLogosNode):
    """
    void.pataphysics - The Science of Imaginary Solutions.

    Alfred Jarry: "Pataphysics is the science of imaginary solutions,
    which symbolically attributes the properties of objects,
    described by their virtuality, to their lineaments."

    This node provides AGENTESE access to contract-bounded hallucination:
    - solve: Generate an imaginary solution to a problem
    - melt: Invoke a meltable function with fallback
    - verify: Check if a solution satisfies contracts

    The rename from "hallucinate" to "pataphysics.solve" is intentional:
    - "Hallucinate" implies error, accident, unreliability
    - "Solve" implies deliberate method, even when imaginary

    See: plans/concept/creativity.md (The Veale Fix)
    """

    _handle: str = "void.pataphysics"
    _pool: EntropyPool = field(default_factory=EntropyPool)

    # Solution templates for imaginary solutions
    _solution_templates: tuple[str, ...] = (
        "Imagine that {problem} could be addressed by inverting the question.",
        "Consider: what if {problem} were actually its own solution?",
        "The imaginary solution: treat {problem} as a feature, not a bug.",
        "Pataphysics suggests: the exception IS the rule for {problem}.",
        "What lies beyond {problem}? Perhaps the answer is the question itself.",
    )

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Everyone can invoke pataphysics."""
        return ("solve", "melt", "verify", "imagine")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View pataphysics interface."""
        return BasicRendering(
            summary="Pataphysics Portal (Imaginary Solutions)",
            content="The science of imaginary solutions. Use 'solve' to find what lies beyond.",
            metadata={
                "entropy_remaining": self._pool.remaining,
                "jarry_quote": "Pataphysics will be, above all, the science of the particular.",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle pataphysics aspects."""
        match aspect:
            case "solve":
                return await self._solve(observer, **kwargs)
            case "melt":
                return await self._melt(observer, **kwargs)
            case "verify":
                return await self._verify(observer, **kwargs)
            case "imagine":
                return await self._imagine(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _solve(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate an imaginary solution to a problem.

        This is the AGENTESE path for contract-bounded hallucination.
        When rigid solutions fail, pataphysics provides alternatives.
        """
        problem = kwargs.get("problem", "the unsolvable")
        ensure = kwargs.get("ensure")  # Optional postcondition

        try:
            grant = self._pool.sip(0.08)
        except BudgetExhaustedError:
            return {
                "solution": "The void is exhausted. Tithe first, then solve.",
                "status": "budget_exhausted",
            }

        # Generate imaginary solution
        seed = grant["seed"]
        template_idx = int(seed * len(self._solution_templates))
        template = self._solution_templates[template_idx]

        solution = template.format(problem=problem)

        result = {
            "solution": solution,
            "problem": problem,
            "seed": seed,
            "method": "pataphysics",
            "jarry_certified": True,
        }

        # If a postcondition is provided, note whether it would pass
        if ensure is not None:
            try:
                result["contract_satisfied"] = bool(ensure(solution))
            except Exception:
                result["contract_satisfied"] = False

        return result

    async def _melt(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Invoke a meltable operation with fallback.

        This is a meta-operation: it doesn't execute meltable functions
        directly, but provides context for how melting works.
        """
        context = kwargs.get("context", {})
        error_type = kwargs.get("error_type", "unknown")

        return {
            "melting_context": MeltingContext(
                function_name=context.get("function", "unknown"),
                args=context.get("args", ()),
                kwargs=context.get("kwargs", {}),
                error=Exception(f"Simulated {error_type}"),
                attempt=0,
            ),
            "instruction": "Use @meltable decorator for contract-bounded fallback",
            "philosophy": "When rigid code fails, imagination provides.",
        }

    async def _verify(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Verify if a solution satisfies a contract.

        Args:
            solution: The proposed solution
            ensure: The postcondition predicate
        """
        solution = kwargs.get("solution")
        ensure = kwargs.get("ensure")

        if ensure is None:
            return {
                "verified": True,
                "reason": "No contract specified (vacuously true)",
            }

        try:
            satisfied = bool(ensure(solution))
            return {
                "verified": satisfied,
                "solution": solution,
                "reason": "Contract satisfied" if satisfied else "Contract violated",
            }
        except Exception as e:
            return {
                "verified": False,
                "solution": solution,
                "reason": f"Contract evaluation failed: {e}",
                "error": str(e),
            }

    async def _imagine(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Pure imagination: generate without constraints.

        Unlike 'solve', this doesn't attempt to address a problem.
        It simply generates novel content from the entropy pool.
        """
        domain = kwargs.get("domain", "the possible")

        try:
            grant = self._pool.sip(0.05)
        except BudgetExhaustedError:
            return {
                "imagination": "Even imagination requires entropy. Tithe to restore.",
                "status": "budget_exhausted",
            }

        imaginations = [
            f"In the realm of {domain}, all contradictions resolve.",
            f"Beyond {domain} lies its shadow, equally real.",
            f"What if {domain} dreamed of us, instead?",
            f"The inverse of {domain} is also {domain}.",
            f"In pataphysics, {domain} is merely the beginning.",
        ]

        idx = int(grant["seed"] * len(imaginations))
        return {
            "imagination": imaginations[idx],
            "domain": domain,
            "seed": grant["seed"],
        }


# === Metabolic Node ===


@dataclass
class MetabolicNode(BaseLogosNode):
    """
    void.metabolism - Metabolic pressure tracking and fever generation.

    The Accursed Share: surplus must be spent.

    Affordances:
    - pressure: Query current metabolic pressure
    - fever: Check if system is in fever state
    - oblique: Get an Oblique Strategy (FREE, no LLM)
    - dream: Generate fever dream (EXPENSIVE, uses LLM)
    - tithe: Voluntary pressure discharge
    - status: Full metabolic status

    Integration: This node wraps MetabolicEngine and FeverStream.
    """

    _handle: str = "void.metabolism"

    # Lazy-loaded to avoid circular imports
    _engine: Any = field(default=None)
    _fever_stream: Any = field(default=None)

    def __post_init__(self) -> None:
        """Lazy-initialize engine and fever stream."""
        if self._engine is None:
            from protocols.agentese.metabolism import (
                FeverStream,
                get_metabolic_engine,
            )

            self._engine = get_metabolic_engine()
            self._fever_stream = FeverStream()

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Everyone can interact with metabolism."""
        return ("pressure", "fever", "oblique", "dream", "tithe", "status")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View metabolic status."""
        status = self._engine.status()
        pressure_pct = int(status["pressure"] / status["critical_threshold"] * 100)
        fever_str = "FEVER" if status["in_fever"] else "normal"

        return BasicRendering(
            summary=f"Metabolism ({fever_str})",
            content=f"Pressure: {pressure_pct}% of threshold | Temperature: {status['temperature']:.2f}",
            metadata=status,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle metabolism aspects."""
        match aspect:
            case "pressure":
                return {
                    "pressure": self._engine.pressure,
                    "in_fever": self._engine.in_fever,
                    "critical_threshold": self._engine.critical_threshold,
                }
            case "fever":
                return {
                    "in_fever": self._engine.in_fever,
                    "fever_start": self._engine.fever_start,
                }
            case "oblique":
                seed = kwargs.get("seed")
                strategy = self._fever_stream.oblique(seed)
                return {"strategy": strategy}
            case "dream":
                context = kwargs.get("context", {})
                llm_client = kwargs.get("llm_client")
                dream = await self._fever_stream.dream(context, llm_client)
                return {"dream": dream}
            case "tithe":
                amount = kwargs.get("amount", 0.1)
                return self._engine.tithe(amount)
            case "status":
                return self._engine.status()
            case "tick":
                # Manual tick for testing
                input_count = kwargs.get("input_count", 0)
                output_count = kwargs.get("output_count", 0)
                event = self._engine.tick(input_count, output_count)
                if event:
                    return {
                        "fever_triggered": True,
                        "event": {
                            "intensity": event.intensity,
                            "trigger": event.trigger,
                            "oblique_strategy": event.oblique_strategy,
                        },
                    }
                return {"fever_triggered": False, "pressure": self._engine.pressure}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Void Context Resolver ===


@dataclass
class VoidContextResolver:
    """
    Resolver for void.* context.

    The void is always accessible to all agents.
    It provides entropy, serendipity, gratitude, capital, pataphysics, and metabolism.
    """

    # Shared entropy pool
    _pool: EntropyPool = field(default_factory=EntropyPool)

    # Shared capital ledger (injected for dependency isolation)
    _ledger: EventSourcedLedger = field(default_factory=EventSourcedLedger)

    # Singleton nodes
    _entropy: EntropyNode | None = None
    _serendipity: SerendipityNode | None = None
    _gratitude: GratitudeNode | None = None
    _capital: CapitalNode | None = None
    _pataphysics: PataphysicsNode | None = None
    _metabolism: MetabolicNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes with shared pool and ledger."""
        self._entropy = EntropyNode(_pool=self._pool)
        self._serendipity = SerendipityNode(_pool=self._pool)
        self._gratitude = GratitudeNode(_pool=self._pool)
        self._capital = CapitalNode(_ledger=self._ledger)
        self._pataphysics = PataphysicsNode(_pool=self._pool)
        self._metabolism = MetabolicNode()

        # Wire entropy pool to metabolic engine
        if self._metabolism._engine is not None:
            self._metabolism._engine.set_entropy_pool(self._pool)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a void.* path to a node.

        Args:
            holon: The void subsystem (entropy, serendipity, gratitude, capital, pataphysics, metabolism)
            rest: Additional path components

        Returns:
            Resolved node
        """
        match holon:
            case "entropy":
                return self._entropy or EntropyNode()
            case "serendipity":
                return self._serendipity or SerendipityNode()
            case "gratitude":
                return self._gratitude or GratitudeNode()
            case "capital":
                return self._capital or CapitalNode()
            case "pataphysics":
                return self._pataphysics or PataphysicsNode()
            case "metabolism":
                return self._metabolism or MetabolicNode()
            case _:
                # Generic void node for undefined holons
                return GenericVoidNode(holon, self._pool)


# === Generic Void Node ===


@dataclass
class GenericVoidNode(BaseLogosNode):
    """Fallback node for undefined void.* paths."""

    holon: str
    _pool: EntropyPool
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"void.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Void is open to all."""
        return ("sip", "tithe")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Void: {self.holon}",
            content=f"An unexplored region of the void: {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        match aspect:
            case "sip":
                return self._pool.sip(kwargs.get("amount", 0.1))
            case "tithe":
                return self._pool.tithe()
            case _:
                return {"holon": self.holon, "aspect": aspect}


# === Factory Functions ===


def create_void_resolver(
    initial_budget: float = 100.0,
    regeneration_rate: float = 0.1,
    ledger: EventSourcedLedger | None = None,
) -> VoidContextResolver:
    """Create a VoidContextResolver with custom entropy and capital configuration."""
    pool = EntropyPool(
        initial_budget=initial_budget,
        remaining=initial_budget,
        regeneration_rate=regeneration_rate,
    )
    capital_ledger = ledger or EventSourcedLedger()
    resolver = VoidContextResolver(_pool=pool, _ledger=capital_ledger)
    resolver.__post_init__()
    return resolver


def create_entropy_pool(
    initial_budget: float = 100.0,
    regeneration_rate: float = 0.1,
) -> EntropyPool:
    """Create an EntropyPool with custom configuration."""
    return EntropyPool(
        initial_budget=initial_budget,
        remaining=initial_budget,
        regeneration_rate=regeneration_rate,
    )
