"""
Syntax Tax: Chomsky-Based Pricing for Grammar Complexity

Phase 3 of Structural Economics (B-gent × G-gent Integration).

Core insight: Not all grammars cost the same to parse. Price operations by Chomsky hierarchy.

The Chomsky Price Ladder:
- Type 3 (Regular): Regex, finite automata → Cheap (0.001/token)
- Type 2 (Context-Free): Pushdown automata → Moderate (0.003/token)
- Type 1 (Context-Sensitive): Linear-bounded → Expensive (0.010/token)
- Type 0 (Unrestricted): Turing-complete → Very expensive (0.030/token) + gas limit + escrow

Key features:
1. GrammarClassifier: Analyze grammar to determine Chomsky level
2. SyntaxTaxSchedule: Calculate costs based on complexity
3. SyntaxTaxBudget: Enforce pricing with escrow for Turing-complete
4. Downgrade negotiation: Help agents choose cheaper grammars when budget-constrained

Integration:
- Works with G-gent Tongue for grammar analysis
- Works with B-gent CentralBank for metering
- Works with B-gent ConstitutionalBanker for fiscal safety
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Protocol

from .metered_functor import CentralBank, Gas


if TYPE_CHECKING:
    from agents.g.types import Tongue


# =============================================================================
# Chomsky Hierarchy Types
# =============================================================================


class ChomskyLevel(Enum):
    """
    The four levels of the Chomsky hierarchy.

    Each level corresponds to a class of formal languages and automata:
    - Type 3 (Regular): Recognized by finite automata / regex
    - Type 2 (Context-Free): Recognized by pushdown automata / CFG
    - Type 1 (Context-Sensitive): Recognized by linear-bounded automata
    - Type 0 (Unrestricted): Recognized by Turing machines (halting not guaranteed)
    """

    REGULAR = 3  # Type 3 - Regex, finite automata
    CONTEXT_FREE = 2  # Type 2 - Pushdown automata, BNF
    CONTEXT_SENSITIVE = 1  # Type 1 - Linear-bounded automata
    TURING_COMPLETE = 0  # Type 0 - Turing machines

    @property
    def risk_level(self) -> str:
        """Human-readable risk level."""
        return {
            ChomskyLevel.REGULAR: "low",
            ChomskyLevel.CONTEXT_FREE: "moderate",
            ChomskyLevel.CONTEXT_SENSITIVE: "high",
            ChomskyLevel.TURING_COMPLETE: "critical",
        }[self]

    @property
    def can_halt(self) -> bool:
        """Whether parsing is guaranteed to halt."""
        return self != ChomskyLevel.TURING_COMPLETE

    @property
    def requires_escrow(self) -> bool:
        """Whether this level requires escrow deposit."""
        return self in (ChomskyLevel.CONTEXT_SENSITIVE, ChomskyLevel.TURING_COMPLETE)

    @property
    def requires_gas_limit(self) -> bool:
        """Whether this level requires a gas limit."""
        return self in (ChomskyLevel.CONTEXT_SENSITIVE, ChomskyLevel.TURING_COMPLETE)


class GrammarFeature(Enum):
    """
    Features detected in grammar analysis that indicate complexity.

    Used by GrammarClassifier to determine Chomsky level.
    """

    # Type 3 (Regular) indicators
    SIMPLE_ALTERNATION = auto()  # a | b
    SIMPLE_CONCATENATION = auto()  # a b
    KLEENE_STAR = auto()  # a*
    KLEENE_PLUS = auto()  # a+
    OPTIONAL = auto()  # a?

    # Type 2 (Context-Free) indicators
    RECURSIVE_RULE = auto()  # A ::= ... A ...
    NESTED_STRUCTURE = auto()  # Balanced parens, brackets
    INDIRECT_RECURSION = auto()  # A ::= B; B ::= A

    # Type 1 (Context-Sensitive) indicators
    CONTEXT_DEPENDENT = auto()  # αAβ → αγβ where γ ≠ ε
    LENGTH_DEPENDENT = auto()  # Output depends on input length
    ATTRIBUTE_GRAMMAR = auto()  # Inherited/synthesized attributes

    # Type 0 (Turing-Complete) indicators
    UNBOUNDED_RECURSION = auto()  # No termination guarantee
    ARBITRARY_COMPUTATION = auto()  # eval(), exec(), etc.
    LOOP_CONSTRUCT = auto()  # while, for loops in semantics


@dataclass
class GrammarAnalysis:
    """
    Result of analyzing a grammar for Chomsky classification.

    Contains detected features and the inferred Chomsky level.
    """

    level: ChomskyLevel
    features: set[GrammarFeature] = field(default_factory=set)
    confidence: float = 1.0  # 0.0-1.0, how confident in classification
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def is_high_risk(self) -> bool:
        """Whether this grammar is high risk."""
        return self.level in (
            ChomskyLevel.CONTEXT_SENSITIVE,
            ChomskyLevel.TURING_COMPLETE,
        )

    @property
    def can_run_unbounded(self) -> bool:
        """Whether this grammar can run indefinitely."""
        return self.level == ChomskyLevel.TURING_COMPLETE


# =============================================================================
# Grammar Classifier
# =============================================================================


class GrammarClassifier:
    """
    Classifies grammars by Chomsky hierarchy.

    Uses heuristic analysis of grammar structure to determine complexity:
    - Detects recursion patterns (left, right, indirect)
    - Detects context-sensitive patterns
    - Detects Turing-complete features (loops, eval, unbounded recursion)

    Note: This is a heuristic classifier. Perfect Chomsky classification
    is undecidable in general, but we can detect common patterns.
    """

    # Patterns that indicate recursion
    RECURSION_PATTERNS = [
        r"(\w+)\s*::=.*\1",  # Direct recursion in BNF
        r"(\w+)\s*:\s*.*\1",  # Direct recursion in Lark
        r"def\s+(\w+).*\1\(",  # Recursive function call
    ]

    # Patterns that indicate context-sensitivity
    CONTEXT_SENSITIVE_PATTERNS = [
        r"context",  # Explicit context mention
        r"inherited",  # Inherited attributes
        r"synthesized",  # Synthesized attributes
        r"@\w+",  # Decorator patterns (semantic actions)
    ]

    # Patterns that indicate Turing-completeness
    TURING_COMPLETE_PATTERNS = [
        r"\beval\b",
        r"\bexec\b",
        r"\bwhile\b",
        r"\bfor\b",
        r"loop",
        r"recursive",  # Explicit recursive marker
        r"unbounded",
    ]

    # Patterns that indicate regular expressions
    REGULAR_PATTERNS = [
        r"^[A-Za-z0-9\s\|\*\+\?\(\)]+$",  # Simple regex characters only
    ]

    def classify(self, grammar: str) -> GrammarAnalysis:
        """
        Classify a grammar by Chomsky hierarchy.

        Args:
            grammar: Grammar specification (BNF, EBNF, Lark, regex, etc.)

        Returns:
            GrammarAnalysis with level, features, and confidence
        """
        grammar_lower = grammar.lower()
        features: set[GrammarFeature] = set()
        warnings: list[str] = []
        details: dict[str, Any] = {}

        # Check for Turing-complete features first (highest risk)
        for pattern in self.TURING_COMPLETE_PATTERNS:
            if re.search(pattern, grammar_lower):
                features.add(GrammarFeature.UNBOUNDED_RECURSION)
                if "eval" in grammar_lower or "exec" in grammar_lower:
                    features.add(GrammarFeature.ARBITRARY_COMPUTATION)
                if any(kw in grammar_lower for kw in ["while", "for", "loop"]):
                    features.add(GrammarFeature.LOOP_CONSTRUCT)

        if features & {
            GrammarFeature.UNBOUNDED_RECURSION,
            GrammarFeature.ARBITRARY_COMPUTATION,
            GrammarFeature.LOOP_CONSTRUCT,
        }:
            return GrammarAnalysis(
                level=ChomskyLevel.TURING_COMPLETE,
                features=features,
                confidence=0.9,
                warnings=["Grammar may not terminate on all inputs"],
                details={"detected_turing_features": list(f.name for f in features)},
            )

        # Check for context-sensitive features
        for pattern in self.CONTEXT_SENSITIVE_PATTERNS:
            if re.search(pattern, grammar_lower):
                features.add(GrammarFeature.CONTEXT_DEPENDENT)

        if GrammarFeature.CONTEXT_DEPENDENT in features:
            return GrammarAnalysis(
                level=ChomskyLevel.CONTEXT_SENSITIVE,
                features=features,
                confidence=0.8,
                warnings=["Grammar may have exponential complexity"],
                details={"detected_context_features": True},
            )

        # Check for context-free features (recursion)
        has_recursion = False
        for pattern in self.RECURSION_PATTERNS:
            if re.search(pattern, grammar, re.MULTILINE):
                has_recursion = True
                features.add(GrammarFeature.RECURSIVE_RULE)

        # Check for nested structures
        if any(pair in grammar for pair in ["()", "[]", "{}"]):
            features.add(GrammarFeature.NESTED_STRUCTURE)

        # Check for BNF indicators
        if "::=" in grammar or "|" in grammar:
            # This is a formal grammar, likely context-free
            if has_recursion or GrammarFeature.NESTED_STRUCTURE in features:
                return GrammarAnalysis(
                    level=ChomskyLevel.CONTEXT_FREE,
                    features=features,
                    confidence=0.85,
                    details={"has_bnf": True, "has_recursion": has_recursion},
                )

        # Check for simple regex patterns
        if re.match(r"^[\w\s\|\*\+\?\.\(\)\[\]\^$\\]+$", grammar):
            features.add(GrammarFeature.SIMPLE_ALTERNATION)
            return GrammarAnalysis(
                level=ChomskyLevel.REGULAR,
                features=features,
                confidence=0.95,
                details={"regex_like": True},
            )

        # Default: if has BNF operators, assume context-free
        if any(op in grammar for op in ["::=", "|", "*", "+"]):
            features.add(GrammarFeature.SIMPLE_ALTERNATION)
            return GrammarAnalysis(
                level=ChomskyLevel.CONTEXT_FREE,
                features=features,
                confidence=0.7,
                details={"inferred_from_operators": True},
            )

        # Very simple grammar, treat as regular
        return GrammarAnalysis(
            level=ChomskyLevel.REGULAR,
            features=features,
            confidence=0.6,
            details={"simple_grammar": True},
        )

    def classify_tongue(self, tongue: "Tongue") -> GrammarAnalysis:
        """
        Classify a G-gent Tongue by Chomsky hierarchy.

        Uses both the grammar string and the GrammarLevel hint.
        """
        # Import here to avoid circular dependency
        try:
            from agents.g.types import GrammarLevel
        except ImportError:
            # If G-gent not available, just classify the grammar string
            return self.classify(tongue.grammar)

        analysis = self.classify(tongue.grammar)

        # Use GrammarLevel as a hint to adjust confidence
        if tongue.level == GrammarLevel.RECURSIVE:
            # Recursive level is at least context-free, possibly more
            if analysis.level == ChomskyLevel.REGULAR:
                analysis.level = ChomskyLevel.CONTEXT_FREE
                analysis.confidence *= 0.8
                analysis.details["upgraded_from_level_hint"] = True

        if tongue.level == GrammarLevel.SCHEMA:
            # Schema level is typically regular or simple context-free
            if analysis.level == ChomskyLevel.TURING_COMPLETE:
                analysis.warnings.append(
                    "Schema-level tongue classified as Turing-complete - verify grammar"
                )

        return analysis


# =============================================================================
# Syntax Tax Schedule
# =============================================================================


@dataclass
class SyntaxTaxSchedule:
    """
    Pricing schedule based on grammar complexity.

    Chomsky Hierarchy pricing:
    - Type 3 (Regular): 0.001 / token - Cheap, guaranteed to halt
    - Type 2 (Context-Free): 0.003 / token - Moderate, O(n³) worst case
    - Type 1 (Context-Sensitive): 0.010 / token - Expensive, exponential
    - Type 0 (Turing-Complete): 0.030 / token - Very expensive + gas limit
    """

    # Base costs per token
    regular_cost: float = 0.001  # Type 3
    context_free_cost: float = 0.003  # Type 2
    context_sensitive_cost: float = 0.010  # Type 1
    turing_complete_cost: float = 0.030  # Type 0

    # Gas limits (prevent infinite loops)
    turing_gas_limit: int = 100_000  # Max tokens for Turing-complete
    context_sensitive_gas_limit: int = 500_000  # Max for context-sensitive

    # Escrow multipliers
    turing_escrow_multiplier: float = 2.0  # 2x deposit for Turing-complete
    context_sensitive_escrow_multiplier: float = 1.5  # 1.5x for context-sensitive

    def get_cost_per_token(self, level: ChomskyLevel) -> float:
        """Get cost per token for a Chomsky level."""
        return {
            ChomskyLevel.REGULAR: self.regular_cost,
            ChomskyLevel.CONTEXT_FREE: self.context_free_cost,
            ChomskyLevel.CONTEXT_SENSITIVE: self.context_sensitive_cost,
            ChomskyLevel.TURING_COMPLETE: self.turing_complete_cost,
        }[level]

    def get_gas_limit(self, level: ChomskyLevel) -> int | None:
        """Get gas limit for a Chomsky level (None if no limit)."""
        if level == ChomskyLevel.TURING_COMPLETE:
            return self.turing_gas_limit
        elif level == ChomskyLevel.CONTEXT_SENSITIVE:
            return self.context_sensitive_gas_limit
        return None

    def get_escrow_multiplier(self, level: ChomskyLevel) -> float:
        """Get escrow multiplier for a Chomsky level."""
        if level == ChomskyLevel.TURING_COMPLETE:
            return self.turing_escrow_multiplier
        elif level == ChomskyLevel.CONTEXT_SENSITIVE:
            return self.context_sensitive_escrow_multiplier
        return 1.0

    def calculate_cost(
        self, level: ChomskyLevel, estimated_tokens: int
    ) -> tuple[Gas, int | None, int]:
        """
        Calculate cost based on grammar complexity.

        Args:
            level: Chomsky level of the grammar
            estimated_tokens: Estimated number of tokens to process

        Returns:
            Tuple of (gas_cost, gas_limit, escrow_required)
        """
        cost_per_token = self.get_cost_per_token(level)
        total_cost = estimated_tokens * cost_per_token
        gas_limit = self.get_gas_limit(level)

        # Calculate escrow
        escrow_multiplier = self.get_escrow_multiplier(level)
        escrow_required = (
            int(total_cost * 1000 * escrow_multiplier) if escrow_multiplier > 1.0 else 0
        )

        gas = Gas(
            tokens=int(total_cost * 1000),  # Convert to token units
            time_ms=0,
            model_multiplier=1.0,
        )

        return gas, gas_limit, escrow_required

    def calculate_tongue_cost(
        self,
        tongue: "Tongue",
        estimated_tokens: int,
        classifier: GrammarClassifier | None = None,
    ) -> tuple[Gas, int | None, int, GrammarAnalysis]:
        """
        Calculate cost for a G-gent Tongue.

        Args:
            tongue: The Tongue to price
            estimated_tokens: Estimated number of tokens
            classifier: Optional classifier (creates default if None)

        Returns:
            Tuple of (gas_cost, gas_limit, escrow_required, analysis)
        """
        if classifier is None:
            classifier = GrammarClassifier()

        analysis = classifier.classify_tongue(tongue)
        gas, gas_limit, escrow = self.calculate_cost(analysis.level, estimated_tokens)

        return gas, gas_limit, escrow, analysis


# =============================================================================
# Budget Decision Types
# =============================================================================


@dataclass
class SyntaxTaxDecision:
    """
    Decision from syntax tax budget evaluation.

    Includes approval status, costs, and any required escrow.
    """

    approved: bool
    reason: str
    level: ChomskyLevel
    gas_cost: Gas
    gas_limit: int | None = None
    escrow_required: int = 0
    escrow_lease_id: str | None = None  # ID of held escrow
    downgrade_available: bool = False
    downgrade_level: ChomskyLevel | None = None
    downgrade_savings: float = 0.0


@dataclass
class EscrowLease:
    """
    A held escrow deposit for high-risk grammar execution.

    Escrow is returned if execution completes within gas limit.
    Escrow is forfeited if execution exceeds gas limit.
    """

    id: str
    agent_id: str
    amount: int
    level: ChomskyLevel
    created_at: datetime = field(default_factory=datetime.now)
    released: bool = False
    forfeited: bool = False


# =============================================================================
# Syntax Tax Budget
# =============================================================================


class SyntaxTaxBudget:
    """
    Budget that enforces syntax tax based on Chomsky hierarchy.

    Key behaviors:
    1. Calculate costs based on grammar complexity
    2. Require escrow for high-risk grammars
    3. Enforce gas limits for Turing-complete grammars
    4. Support downgrade negotiation when budget insufficient

    Note: Uses CentralBank's shared token pool. For per-agent budget tracking,
    wrap with agent-specific budget limits.
    """

    def __init__(
        self,
        central_bank: CentralBank | None = None,
        schedule: SyntaxTaxSchedule | None = None,
        classifier: GrammarClassifier | None = None,
    ):
        """
        Initialize syntax tax budget.

        Args:
            central_bank: Bank for authorization (creates default if None)
            schedule: Tax schedule (creates default if None)
            classifier: Grammar classifier (creates default if None)
        """
        self.bank = central_bank or CentralBank()
        self.schedule = schedule or SyntaxTaxSchedule()
        self.classifier = classifier or GrammarClassifier()

        # Track active escrows
        self._escrows: dict[str, EscrowLease] = {}
        self._next_escrow_id = 1

        # Per-agent budget limits (optional)
        self._agent_budgets: dict[str, int] = {}

    def set_agent_budget(self, agent_id: str, budget: int) -> None:
        """Set budget limit for an agent."""
        self._agent_budgets[agent_id] = budget

    def get_agent_budget(self, agent_id: str) -> int:
        """Get budget for agent (defaults to bank balance if not set)."""
        return self._agent_budgets.get(agent_id, self.bank.get_balance())

    def _can_afford(self, agent_id: str, tokens: int) -> bool:
        """Check if agent can afford tokens."""
        # Check agent-specific budget if set
        if agent_id in self._agent_budgets:
            return self._agent_budgets[agent_id] >= tokens
        # Otherwise check shared bank balance
        return self.bank.bucket.can_afford(tokens)

    def evaluate_grammar(
        self, agent_id: str, grammar: str, estimated_tokens: int
    ) -> SyntaxTaxDecision:
        """
        Evaluate a grammar string for syntax tax.

        Args:
            agent_id: Agent requesting the operation
            grammar: Grammar specification string
            estimated_tokens: Estimated tokens to process

        Returns:
            SyntaxTaxDecision with approval status and costs
        """
        analysis = self.classifier.classify(grammar)
        return self._make_decision(agent_id, analysis, estimated_tokens)

    def evaluate_tongue(
        self, agent_id: str, tongue: "Tongue", estimated_tokens: int
    ) -> SyntaxTaxDecision:
        """
        Evaluate a G-gent Tongue for syntax tax.

        Args:
            agent_id: Agent requesting the operation
            tongue: The Tongue to evaluate
            estimated_tokens: Estimated tokens to process

        Returns:
            SyntaxTaxDecision with approval status and costs
        """
        analysis = self.classifier.classify_tongue(tongue)
        return self._make_decision(agent_id, analysis, estimated_tokens)

    def _make_decision(
        self, agent_id: str, analysis: GrammarAnalysis, estimated_tokens: int
    ) -> SyntaxTaxDecision:
        """Internal: Make budget decision based on grammar analysis."""
        level = analysis.level
        gas, gas_limit, escrow = self.schedule.calculate_cost(level, estimated_tokens)

        # Check if agent can afford the base cost
        can_afford_base = self._can_afford(agent_id, gas.tokens)

        if not can_afford_base:
            # Check if downgrade would help
            downgrade_level = self._find_affordable_downgrade(
                agent_id, estimated_tokens
            )
            if downgrade_level:
                downgrade_gas, _, _ = self.schedule.calculate_cost(
                    downgrade_level, estimated_tokens
                )
                return SyntaxTaxDecision(
                    approved=False,
                    reason=f"Insufficient budget for {level.name} grammar ({gas.tokens} tokens)",
                    level=level,
                    gas_cost=gas,
                    gas_limit=gas_limit,
                    escrow_required=escrow,
                    downgrade_available=True,
                    downgrade_level=downgrade_level,
                    downgrade_savings=gas.tokens - downgrade_gas.tokens,
                )
            return SyntaxTaxDecision(
                approved=False,
                reason=f"Insufficient budget for {level.name} grammar ({gas.tokens} tokens)",
                level=level,
                gas_cost=gas,
                gas_limit=gas_limit,
                escrow_required=escrow,
            )

        # Check if agent can afford escrow
        if escrow > 0:
            total_required = gas.tokens + escrow
            if not self._can_afford(agent_id, total_required):
                return SyntaxTaxDecision(
                    approved=False,
                    reason=f"Insufficient escrow for {level.name} grammar "
                    f"(requires {escrow} tokens deposit)",
                    level=level,
                    gas_cost=gas,
                    gas_limit=gas_limit,
                    escrow_required=escrow,
                    downgrade_available=True,
                    downgrade_level=ChomskyLevel.CONTEXT_FREE,
                )

        return SyntaxTaxDecision(
            approved=True,
            reason=f"Syntax tax approved: {level.name} ({gas.tokens} tokens)",
            level=level,
            gas_cost=gas,
            gas_limit=gas_limit,
            escrow_required=escrow,
        )

    def _find_affordable_downgrade(
        self, agent_id: str, estimated_tokens: int
    ) -> ChomskyLevel | None:
        """Find an affordable lower Chomsky level."""
        # Try levels from cheapest to most expensive
        for level in [
            ChomskyLevel.REGULAR,
            ChomskyLevel.CONTEXT_FREE,
            ChomskyLevel.CONTEXT_SENSITIVE,
        ]:
            gas, _, escrow = self.schedule.calculate_cost(level, estimated_tokens)
            total = gas.tokens + escrow
            if self._can_afford(agent_id, total):
                return level
        return None

    async def hold_escrow(
        self, agent_id: str, amount: int, level: ChomskyLevel
    ) -> EscrowLease:
        """
        Hold escrow deposit for high-risk grammar execution.

        Args:
            agent_id: Agent making the deposit
            amount: Amount to hold
            level: Chomsky level requiring escrow

        Returns:
            EscrowLease tracking the held funds
        """
        # Authorize the escrow hold
        await self.bank.authorize(agent_id, amount)

        lease_id = f"ESCROW{self._next_escrow_id:06d}"
        self._next_escrow_id += 1

        lease = EscrowLease(
            id=lease_id,
            agent_id=agent_id,
            amount=amount,
            level=level,
        )
        self._escrows[lease_id] = lease

        return lease

    async def release_escrow(self, lease_id: str) -> bool:
        """
        Release escrow after successful execution.

        Returns True if escrow was released, False if not found.
        """
        lease = self._escrows.get(lease_id)
        if not lease or lease.released or lease.forfeited:
            return False

        # Return funds to agent
        # In a real implementation, this would credit the agent's account
        lease.released = True
        return True

    async def forfeit_escrow(self, lease_id: str) -> bool:
        """
        Forfeit escrow after failed/over-limit execution.

        Returns True if escrow was forfeited, False if not found.
        """
        lease = self._escrows.get(lease_id)
        if not lease or lease.released or lease.forfeited:
            return False

        lease.forfeited = True
        return True

    def get_escrow(self, lease_id: str) -> EscrowLease | None:
        """Get escrow lease by ID."""
        return self._escrows.get(lease_id)

    def get_tier_summary(self) -> dict[str, dict[str, Any]]:
        """Get summary of pricing tiers."""
        return {
            "regular": {
                "level": ChomskyLevel.REGULAR.name,
                "cost_per_token": self.schedule.regular_cost,
                "gas_limit": None,
                "escrow_required": False,
                "risk": "low",
            },
            "context_free": {
                "level": ChomskyLevel.CONTEXT_FREE.name,
                "cost_per_token": self.schedule.context_free_cost,
                "gas_limit": None,
                "escrow_required": False,
                "risk": "moderate",
            },
            "context_sensitive": {
                "level": ChomskyLevel.CONTEXT_SENSITIVE.name,
                "cost_per_token": self.schedule.context_sensitive_cost,
                "gas_limit": self.schedule.context_sensitive_gas_limit,
                "escrow_required": True,
                "risk": "high",
            },
            "turing_complete": {
                "level": ChomskyLevel.TURING_COMPLETE.name,
                "cost_per_token": self.schedule.turing_complete_cost,
                "gas_limit": self.schedule.turing_gas_limit,
                "escrow_required": True,
                "risk": "critical",
            },
        }


# =============================================================================
# Downgrade Negotiation
# =============================================================================


@dataclass
class DowngradeProposal:
    """
    Proposal to downgrade grammar to a cheaper Chomsky level.

    Generated when agent cannot afford requested grammar complexity.
    """

    original_level: ChomskyLevel
    proposed_level: ChomskyLevel
    original_cost: Gas
    proposed_cost: Gas
    savings: float  # Cost savings as ratio
    constraints_to_add: list[str]  # Constraints that enforce downgrade
    capability_loss: list[str]  # Capabilities lost in downgrade


class DowngradeNegotiator:
    """
    Negotiates grammar downgrades when budget is insufficient.

    Works with G-gent to synthesize constrained grammars at lower
    Chomsky levels while preserving as much functionality as possible.
    """

    # Constraints that force downgrade to each level
    DOWNGRADE_CONSTRAINTS = {
        ChomskyLevel.REGULAR: [
            "No recursion",
            "No nesting",
            "Finite state only",
            "Linear patterns only",
        ],
        ChomskyLevel.CONTEXT_FREE: [
            "No context dependence",
            "Bounded recursion",
            "Stack-based only",
            "No side effects",
        ],
        ChomskyLevel.CONTEXT_SENSITIVE: [
            "No arbitrary computation",
            "Bounded memory",
            "Linear time only",
        ],
    }

    # Capabilities lost at each downgrade
    CAPABILITY_LOSS = {
        ChomskyLevel.REGULAR: [
            "Nested structures",
            "Recursive patterns",
            "Tree-structured data",
        ],
        ChomskyLevel.CONTEXT_FREE: [
            "Context-dependent parsing",
            "Cross-references",
            "Semantic conditions",
        ],
        ChomskyLevel.CONTEXT_SENSITIVE: [
            "Arbitrary computation",
            "Unbounded loops",
            "Dynamic evaluation",
        ],
    }

    def __init__(self, budget: SyntaxTaxBudget):
        """Initialize with syntax tax budget."""
        self.budget = budget

    def propose_downgrade(
        self,
        agent_id: str,
        current_level: ChomskyLevel,
        estimated_tokens: int,
        target_level: ChomskyLevel | None = None,
    ) -> DowngradeProposal | None:
        """
        Propose a grammar downgrade.

        Args:
            agent_id: Agent requesting the operation
            current_level: Current Chomsky level
            estimated_tokens: Estimated tokens to process
            target_level: Specific level to downgrade to (finds affordable if None)

        Returns:
            DowngradeProposal if downgrade possible, None otherwise
        """
        if target_level is None:
            target_level = self.budget._find_affordable_downgrade(
                agent_id, estimated_tokens
            )

        if target_level is None:
            return None

        # In Chomsky hierarchy: lower value = more complex
        # A "downgrade" means going to SIMPLER (higher value) grammar
        # TURING_COMPLETE(0) -> REGULAR(3) is a downgrade (0 to 3, 3 > 0)
        if target_level.value <= current_level.value:
            return None  # Not a downgrade (target is same or more complex)

        # Calculate costs
        original_gas, _, _ = self.budget.schedule.calculate_cost(
            current_level, estimated_tokens
        )
        proposed_gas, _, _ = self.budget.schedule.calculate_cost(
            target_level, estimated_tokens
        )

        savings = (original_gas.tokens - proposed_gas.tokens) / max(
            original_gas.tokens, 1
        )

        # Collect constraints and capability loss for all levels between current and target
        # We're downgrading from current (more complex, lower value) to target (simpler, higher value)
        # Need to include all levels we're passing through
        constraints: list[str] = []
        capability_loss: list[str] = []

        for level in ChomskyLevel:
            # Include levels between current (exclusive) and target (inclusive)
            # Example: TURING(0) -> REGULAR(3) includes levels 1, 2, 3
            if current_level.value < level.value <= target_level.value:
                constraints.extend(self.DOWNGRADE_CONSTRAINTS.get(level, []))
                capability_loss.extend(self.CAPABILITY_LOSS.get(level, []))

        return DowngradeProposal(
            original_level=current_level,
            proposed_level=target_level,
            original_cost=original_gas,
            proposed_cost=proposed_gas,
            savings=savings,
            constraints_to_add=constraints,
            capability_loss=capability_loss,
        )

    async def negotiate_downgrade(
        self,
        agent_id: str,
        tongue: "Tongue",
        estimated_tokens: int,
    ) -> tuple["Tongue", DowngradeProposal] | None:
        """
        Negotiate grammar downgrade with G-gent.

        This would integrate with G-gent to synthesize a new tongue
        at a lower Chomsky level.

        Args:
            agent_id: Agent requesting the operation
            tongue: Original tongue
            estimated_tokens: Estimated tokens

        Returns:
            Tuple of (new_tongue, proposal) if successful, None otherwise
        """
        # Classify current tongue
        analysis = self.budget.classifier.classify_tongue(tongue)

        # Propose downgrade
        proposal = self.propose_downgrade(agent_id, analysis.level, estimated_tokens)

        if proposal is None:
            return None

        # In a real implementation, this would call G-gent to synthesize
        # a new tongue with the downgrade constraints
        # For now, return None to indicate manual intervention needed
        return None


# =============================================================================
# Convenience Functions
# =============================================================================


def create_syntax_tax_budget(
    central_bank: CentralBank | None = None,
    schedule: SyntaxTaxSchedule | None = None,
) -> SyntaxTaxBudget:
    """
    Create a SyntaxTaxBudget with default configuration.

    Args:
        central_bank: Optional central bank (creates default if None)
        schedule: Optional tax schedule (creates default if None)

    Returns:
        Configured SyntaxTaxBudget
    """
    return SyntaxTaxBudget(
        central_bank=central_bank,
        schedule=schedule,
    )


def classify_grammar(grammar: str) -> GrammarAnalysis:
    """
    Convenience function to classify a grammar.

    Args:
        grammar: Grammar specification string

    Returns:
        GrammarAnalysis with Chomsky level and features
    """
    classifier = GrammarClassifier()
    return classifier.classify(grammar)


def calculate_syntax_tax(
    grammar: str, estimated_tokens: int, schedule: SyntaxTaxSchedule | None = None
) -> tuple[Gas, ChomskyLevel]:
    """
    Calculate syntax tax for a grammar.

    Args:
        grammar: Grammar specification string
        estimated_tokens: Estimated tokens to process
        schedule: Optional tax schedule (uses default if None)

    Returns:
        Tuple of (gas_cost, chomsky_level)
    """
    if schedule is None:
        schedule = SyntaxTaxSchedule()

    classifier = GrammarClassifier()
    analysis = classifier.classify(grammar)
    gas, _, _ = schedule.calculate_cost(analysis.level, estimated_tokens)

    return gas, analysis.level


def get_tier_costs(schedule: SyntaxTaxSchedule | None = None) -> dict[str, float]:
    """
    Get cost per token for each Chomsky tier.

    Args:
        schedule: Optional tax schedule (uses default if None)

    Returns:
        Dict mapping tier name to cost per token
    """
    if schedule is None:
        schedule = SyntaxTaxSchedule()

    return {
        "regular": schedule.regular_cost,
        "context_free": schedule.context_free_cost,
        "context_sensitive": schedule.context_sensitive_cost,
        "turing_complete": schedule.turing_complete_cost,
    }
