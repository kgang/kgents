"""
LLM Proof Search: The Hallucination-Tolerant Pipeline.

This module implements LLM-assisted proof search with budget management.
The key insight: LLMs can hallucinate freely because the proof checker
is the final arbiter. If the proof verifies, the theorem holds.

Heritage: Kleppmann (§12), Stigmergic Cognition (§13)

    "The LLM can hallucinate all it wants. The proof checker is the gatekeeper."

The Feedback Loop:
    Obligation → Prompt → LLM → Proof Attempt → Checker
                    ↑                              ↓
                    └──────── Failed? ─────────────┘
                              (retry with hints)

Teaching:
    gotcha: Temperature is a hyper-parameter in ProofSearchConfig, not hardcoded.
            Different obligations may benefit from different temperatures.
            (Evidence: test_search.py::test_temperature_configurable)

    gotcha: Failed tactics are tracked SEPARATELY, not in obligation.context.
            This enables cross-attempt learning without bloating obligations.
            (Evidence: test_search.py::test_failed_tactics_not_repeated)

AGENTESE:
    concept.ashc.prove → Attempt to discharge obligation (uses this module)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .checker import ProofChecker
from .contracts import (
    LemmaId,
    ProofAttempt,
    ProofAttemptId,
    ProofObligation,
    ProofSearchConfig,
    ProofSearchResult,
    ProofStatus,
    VerifiedLemma,
)

if TYPE_CHECKING:
    from ..morpheus.gateway import MorpheusGateway
    from ..morpheus.types import ChatMessage, ChatRequest


# =============================================================================
# LemmaDatabase Protocol
# =============================================================================


@runtime_checkable
class LemmaDatabase(Protocol):
    """
    Protocol for lemma database access.

    The lemma database stores verified facts that can be used as hints
    for future proof searches. This protocol enables dependency injection
    for testing.

    Teaching:
        gotcha: Protocol > ABC for interfaces. Enables duck typing without
                inheritance coupling. See meta.md: "Protocol > ABC"
    """

    def find_related(
        self,
        property_stmt: str,
        limit: int = 3,
    ) -> list[VerifiedLemma]:
        """
        Find lemmas related to a property statement.

        Args:
            property_stmt: The property to find related lemmas for
            limit: Maximum number of lemmas to return

        Returns:
            List of related verified lemmas (most relevant first)
        """
        ...

    def store(self, lemma: VerifiedLemma) -> None:
        """Store a newly verified lemma."""
        ...


# =============================================================================
# Stub LemmaDatabase for Initial Implementation
# =============================================================================


@dataclass
class InMemoryLemmaDatabase:
    """
    In-memory stub for lemma database.

    Used for testing and initial development. Will be replaced with
    D-gent persistence in Phase 4.

    Teaching:
        gotcha: This is a STUB, not the final implementation. It stores
                lemmas in memory only—they're lost on restart.
                Phase 4 adds D-gent persistence.
    """

    _lemmas: list[VerifiedLemma] = field(default_factory=list)

    def find_related(
        self,
        property_stmt: str,
        limit: int = 3,
    ) -> list[VerifiedLemma]:
        """
        Find lemmas with overlapping keywords.

        Simple keyword matching for now. Will be replaced with
        semantic search in Phase 4.
        """
        if not self._lemmas:
            return []

        # Extract keywords from property
        keywords = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", property_stmt.lower()))

        # Score lemmas by keyword overlap
        scored: list[tuple[int, VerifiedLemma]] = []
        for lemma in self._lemmas:
            lemma_keywords = set(
                re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", lemma.statement.lower())
            )
            overlap = len(keywords & lemma_keywords)
            if overlap > 0:
                # Bias toward more-used lemmas (stigmergic reinforcement)
                score = overlap * (1 + lemma.usage_count * 0.1)
                scored.append((int(score * 100), lemma))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [lemma for _, lemma in scored[:limit]]

    def store(self, lemma: VerifiedLemma) -> None:
        """Store a newly verified lemma."""
        self._lemmas.append(lemma)

    @property
    def lemma_count(self) -> int:
        """Number of stored lemmas."""
        return len(self._lemmas)


# =============================================================================
# Proof Searcher
# =============================================================================


class ProofSearcher:
    """
    LLM-assisted proof search with budget management.

    Pattern: Signal Aggregation for Decisions (Pattern 4)
    Multiple signals (tactics, hints, failures) contribute to search direction.

    The searcher progresses through three phases:
    - Quick (10 attempts): Simple tactics, catch easy proofs
    - Medium (50 attempts): + hints from failures and lemma DB
    - Deep (200 attempts): + heritage patterns from spec

    Budget is consumed sequentially. If quick phase succeeds, medium and
    deep phases are skipped.

    Teaching:
        gotcha: The searcher is stateless between calls. Each search()
                invocation is independent. Failed tactics are tracked
                PER SEARCH, not across searches.
                (Evidence: test_search.py::test_searcher_stateless)

        gotcha: Budget is ATTEMPTS, not wall time. A slow checker can
                exhaust budget quickly. Monitor avg_attempt_duration_ms.
                (Evidence: test_search.py::test_budget_is_attempt_count)

    Example:
        >>> searcher = ProofSearcher(gateway, checker, lemma_db)
        >>> obl = ProofObligation(property="∀ x. x == x", ...)
        >>> result = await searcher.search(obl)
        >>> if result.succeeded:
        ...     print(f"Proved! Lemma: {result.lemma.statement}")
    """

    def __init__(
        self,
        gateway: "MorpheusGateway",
        checker: ProofChecker,
        lemma_db: LemmaDatabase | None = None,
        config: ProofSearchConfig | None = None,
    ):
        """
        Initialize proof searcher.

        Args:
            gateway: MorpheusGateway for LLM access
            checker: ProofChecker for verifying proofs
            lemma_db: Optional lemma database for hints (default: in-memory stub)
            config: Optional search configuration (default: standard budgets)
        """
        self._gateway = gateway
        self._checker = checker
        self._lemma_db = lemma_db or InMemoryLemmaDatabase()
        self._config = config or ProofSearchConfig()

    @property
    def config(self) -> ProofSearchConfig:
        """Current search configuration."""
        return self._config

    async def search(
        self,
        obligation: ProofObligation,
    ) -> ProofSearchResult:
        """
        Attempt to discharge a proof obligation.

        Progresses through Quick → Medium → Deep phases,
        stopping when proof is found or budget exhausted.

        Args:
            obligation: The proof obligation to discharge

        Returns:
            ProofSearchResult with attempts, success status, and optional lemma

        Example:
            >>> result = await searcher.search(obligation)
            >>> if result.succeeded:
            ...     # Store lemma for future use
            ...     lemma_db.store(result.lemma)
        """
        result = ProofSearchResult(
            obligation=obligation,
            budget_total=self._config.total_budget,
        )

        # Track failed tactics across phases (stigmergic anti-pheromone)
        failed_tactics: set[str] = set()

        # Phase 1: Quick
        if await self._search_phase(
            obligation,
            result,
            budget=self._config.quick_budget,
            tactics=self._config.quick_tactics,
            hints=(),
            failed_tactics=failed_tactics,
            phase_name="quick",
        ):
            return result

        # Phase 2: Medium (add hints from failed attempts + lemma DB)
        hints = self._gather_hints(obligation, result)
        if await self._search_phase(
            obligation,
            result,
            budget=self._config.medium_budget,
            tactics=self._config.medium_tactics,
            hints=hints,
            failed_tactics=failed_tactics,
            phase_name="medium",
        ):
            return result

        # Phase 3: Deep (add heritage patterns)
        heritage_hints = self._heritage_hints(obligation)
        all_hints = hints + heritage_hints
        if await self._search_phase(
            obligation,
            result,
            budget=self._config.deep_budget,
            tactics=self._config.deep_tactics,
            hints=all_hints,
            failed_tactics=failed_tactics,
            phase_name="deep",
        ):
            return result

        return result

    async def _search_phase(
        self,
        obligation: ProofObligation,
        result: ProofSearchResult,
        budget: int,
        tactics: tuple[str, ...],
        hints: tuple[str, ...],
        failed_tactics: set[str],
        phase_name: str,
    ) -> bool:
        """
        Run one phase of proof search.

        Args:
            obligation: The obligation to prove
            result: Accumulated result (mutated in place)
            budget: Maximum attempts for this phase
            tactics: Available tactics for prompting
            hints: Hints from previous phases or lemma DB
            failed_tactics: Set of tactics that have failed (mutated)
            phase_name: Name for logging/debugging

        Returns:
            True if proof found, False otherwise
        """
        for attempt_num in range(budget):
            result.budget_used += 1

            # Build prompt with current hints and failed tactics
            prompt = self._build_prompt(
                obligation,
                tactics,
                hints,
                failed_tactics,
            )

            # Generate proof attempt via LLM
            proof_source = await self._generate_proof(prompt)

            # Check proof
            check_result = await self._checker.check(
                proof_source,
                timeout_ms=self._config.timeout_per_attempt_ms,
            )

            # Extract tactics used from proof source
            tactics_used = self._extract_tactics(proof_source)

            # Record attempt
            attempt = ProofAttempt(
                id=ProofAttemptId(f"att-{phase_name}-{attempt_num:04d}"),
                obligation_id=obligation.id,
                proof_source=proof_source,
                checker=self._checker.name,
                result=ProofStatus.VERIFIED if check_result.success else ProofStatus.FAILED,
                checker_output="\n".join(list(check_result.errors) + list(check_result.warnings)),
                tactics_used=tactics_used,
                duration_ms=check_result.duration_ms,
            )
            result.attempts.append(attempt)

            if check_result.success:
                # Success! Create verified lemma
                result.lemma = VerifiedLemma(
                    id=LemmaId(f"lem-{obligation.id}"),
                    statement=obligation.property,
                    proof=proof_source,
                    checker=self._checker.name,
                    obligation_id=obligation.id,
                )
                return True

            # Track failed tactics for future avoidance
            failed_tactics.update(tactics_used)

        return False

    def _build_prompt(
        self,
        obligation: ProofObligation,
        tactics: tuple[str, ...],
        hints: tuple[str, ...],
        failed_tactics: set[str],
    ) -> str:
        """
        Build LLM prompt for proof generation.

        The prompt is designed to be:
        1. Deterministic (same inputs → same prompt)
        2. Bounded (limited context, limited hints)
        3. Actionable (clear instructions, available tactics)

        Teaching:
            gotcha: Prompt structure is stable for reproducibility.
                    Changes to prompt format affect all future searches.
                    Version the format if making breaking changes.
        """
        prompt_parts = [
            "Generate a Dafny proof for the following property.",
            "",
            f"Property: {obligation.property}",
            f"Source: {obligation.source_location}",
            "",
            "Available tactics: " + ", ".join(tactics),
        ]

        # Add bounded context
        if obligation.context:
            prompt_parts.append("")
            prompt_parts.append("Context:")
            for ctx in obligation.context[:5]:  # Enforce bound
                prompt_parts.append(f"  {ctx}")

        # Add hints (limit to last 5)
        if hints:
            prompt_parts.append("")
            prompt_parts.append("Hints from analysis:")
            for hint in hints[-5:]:
                prompt_parts.append(f"  - {hint}")

        # Add failed tactics to avoid (sorted for determinism)
        if failed_tactics:
            sorted_failed = sorted(failed_tactics)
            prompt_parts.append("")
            prompt_parts.append(f"Avoid these tactics (already tried): {', '.join(sorted_failed)}")

        prompt_parts.append("")
        prompt_parts.append("Respond with ONLY the Dafny proof code, no explanation.")

        return "\n".join(prompt_parts)

    async def _generate_proof(self, prompt: str) -> str:
        """
        Generate proof attempt via LLM.

        Uses MorpheusGateway for LLM access, which handles routing
        to the appropriate provider.
        """
        # Import here to avoid circular imports
        from ..morpheus.types import ChatMessage, ChatRequest

        request = ChatRequest(
            model="claude-sonnet-4-20250514",  # Fast enough for iteration
            messages=[
                ChatMessage(
                    role="system",
                    content="You are a formal verification expert. Generate valid Dafny proofs.",
                ),
                ChatMessage(
                    role="user",
                    content=prompt,
                ),
            ],
            temperature=self._config.temperature,
            max_tokens=2000,
        )

        response = await self._gateway.complete(request, archetype="system")

        # Extract response content
        if response.choices:
            raw_response = response.choices[0].message.content
            return self._extract_code(raw_response)

        return ""

    def _extract_code(self, response: str) -> str:
        """
        Extract Dafny code from LLM response.

        Handles various output formats:
        - ```dafny ... ``` blocks
        - ``` ... ``` generic blocks
        - Plain code (no blocks)

        Teaching:
            gotcha: LLMs are inconsistent with code block formatting.
                    This function handles common variations but may miss
                    exotic formats. The checker will reject invalid syntax.
        """
        response = response.strip()

        # Try to find dafny-specific code blocks
        if "```dafny" in response:
            match = re.search(r"```dafny\s*\n(.*?)\n```", response, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Try generic code blocks
        if "```" in response:
            match = re.search(r"```\s*\n(.*?)\n```", response, re.DOTALL)
            if match:
                return match.group(1).strip()

        # Fallback: assume entire response is code
        # Remove any leading prose (lines without code-like content)
        lines = response.split("\n")
        code_lines: list[str] = []
        in_code = False

        for line in lines:
            # Heuristic: code starts with keywords or braces
            if not in_code:
                stripped = line.strip()
                if stripped.startswith(("lemma", "method", "function", "predicate", "{", "//")):
                    in_code = True
            if in_code:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines).strip()

        # Last resort: return as-is
        return response

    def _extract_tactics(self, proof_source: str) -> tuple[str, ...]:
        """
        Extract tactics used in a Dafny proof.

        Looks for common Dafny/Lean-style tactic keywords.
        """
        tactics: set[str] = set()

        # Dafny tactics/hints
        dafny_patterns = [
            r"\bassert\b",
            r"\bensures\b",
            r"\brequires\b",
            r"\binvariant\b",
            r"\bdecreases\b",
            r"\bmodifies\b",
            r"\breads\b",
            r"\bforall\b",
            r"\bexists\b",
            r"\bcalc\b",
            r"\bby\b",
        ]

        for pattern in dafny_patterns:
            if re.search(pattern, proof_source, re.IGNORECASE):
                # Extract the tactic name
                tactics.add(pattern.replace(r"\b", ""))

        return tuple(sorted(tactics))

    def _gather_hints(
        self,
        obligation: ProofObligation,
        result: ProofSearchResult,
    ) -> tuple[str, ...]:
        """
        Gather hints from lemma DB and failed attempts.

        Combines:
        1. Related lemmas from the database
        2. Patterns from partially successful attempts
        """
        hints: list[str] = []

        # Related lemmas from DB
        related = self._lemma_db.find_related(obligation.property, limit=3)
        for lemma in related:
            hints.append(f"Related lemma: {lemma.statement}")

        # Look for partial success patterns in attempts
        for attempt in result.attempts:
            # If an attempt almost succeeded (few errors), note the pattern
            if attempt.result == ProofStatus.FAILED:
                if "postcondition" in attempt.checker_output.lower():
                    hints.append("Hint: Postcondition proof needed")
                if "precondition" in attempt.checker_output.lower():
                    hints.append("Hint: Strengthen precondition")
                if "invariant" in attempt.checker_output.lower():
                    hints.append("Hint: Loop invariant needed")

        return tuple(hints)

    def _heritage_hints(self, obligation: ProofObligation) -> tuple[str, ...]:
        """
        Add hints from heritage papers (§10, §12).

        These are domain-specific patterns from the kgents spec.
        """
        hints: list[str] = []
        prop_lower = obligation.property.lower()

        # Polynomial functor patterns (§10)
        if "polynomial" in prop_lower:
            hints.append("Pattern: Use polynomial functor composition laws")
            hints.append("Pattern: Check base case and inductive case separately")

        # Type composition (AD-013)
        if ":" in obligation.property and "invoke" in prop_lower:
            hints.append("Pattern: Type-directed proof via substitution")
            hints.append("Pattern: Show input satisfies precondition, output satisfies postcondition")

        # Composition patterns
        if ">>" in obligation.property or "composition" in prop_lower:
            hints.append("Pattern: Prove associativity via unfolding definitions")
            hints.append("Law: (f >> g) >> h ≡ f >> (g >> h)")

        # Identity patterns
        if "identity" in prop_lower or "id" in obligation.property:
            hints.append("Pattern: Identity laws hold by definition")
            hints.append("Law: Id >> f ≡ f ≡ f >> Id")

        return tuple(hints)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Protocol
    "LemmaDatabase",
    # Stub implementation
    "InMemoryLemmaDatabase",
    # Searcher
    "ProofSearcher",
]
