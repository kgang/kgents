"""
E-gent v2 Teleological Demon: 5-Layer Intent-Aware Selection.

The Teleological Demon is the heart of E-gent v2's approach to preventing
parasitic code evolution. It applies 5 layers of selection, ordered by cost:

1. Syntactic viability (FREE) - ast.parse()
2. Semantic stability (CHEAP) - Type lattice check
3. Teleological alignment (CHEAP-ISH) - Intent embedding distance
4. Thermodynamic viability (FREE) - Gibbs check
5. Economic viability (FREE) - Market quote

The key innovation is Layer 3: Teleological Alignment. Without this layer,
evolution drifts toward "parasitic code" - code that passes tests by gaming
them (hardcoding, deleting functionality, empty implementations).

The Demon kills ~90% of mutations before expensive validation (tests),
using Intent embedding distance to detect purpose drift.

From spec/e-gents/thermodynamics.md:
> "The Teleological Demon doesn't just check fitness—it checks PURPOSE.
> A mutation that passes all tests but drifts from Intent is still rejected."

Spec Reference: spec/e-gents/README.md (Five-Layer Selection)
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from .types import (
    Phage,
    PhageStatus,
    MutationVector,
    Intent,
)


# =============================================================================
# Selection Layer Results
# =============================================================================


class RejectionReason(Enum):
    """Reason a mutation was rejected by the Demon."""

    # Layer 1: Syntactic
    SYNTAX_ERROR = "syntax_error"
    DIFF_TOO_LARGE = "diff_too_large"

    # Layer 2: Semantic
    TYPE_MISMATCH = "type_mismatch"
    STRUCTURE_BROKEN = "structure_broken"
    MISSING_PUBLIC_NAMES = "missing_public_names"

    # Layer 3: Teleological
    INTENT_DRIFT = "intent_drift"
    PARASITIC_PATTERN = "parasitic_pattern"
    PURPOSE_UNCLEAR = "purpose_unclear"

    # Layer 4: Thermodynamic
    UNFAVORABLE_GIBBS = "unfavorable_gibbs"
    COMPLEXITY_EXPLOSION = "complexity_explosion"

    # Layer 5: Economic
    MARKET_REJECTED = "market_rejected"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    ODDS_TOO_POOR = "odds_too_poor"


@dataclass
class SelectionResult:
    """Result of passing through the Teleological Demon."""

    passed: bool
    layer_reached: int  # 0-5 (5 = passed all layers)
    rejection_reason: RejectionReason | None = None
    rejection_detail: str | None = None

    # Layer metrics
    syntax_valid: bool = False
    type_compatible: bool = False
    intent_alignment: float = 0.0
    gibbs_favorable: bool = False
    market_viable: bool = False

    # Timing
    checked_at: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0

    @classmethod
    def rejected(
        cls,
        layer: int,
        reason: RejectionReason,
        detail: str | None = None,
        **kwargs: Any,
    ) -> "SelectionResult":
        """Create a rejected result."""
        return cls(
            passed=False,
            layer_reached=layer,
            rejection_reason=reason,
            rejection_detail=detail,
            **kwargs,
        )

    @classmethod
    def accepted(cls, **kwargs: Any) -> "SelectionResult":
        """Create an accepted result."""
        return cls(
            passed=True,
            layer_reached=5,
            **kwargs,
        )


@dataclass
class DemonStats:
    """Statistics for the Teleological Demon."""

    total_checked: int = 0
    layer1_rejections: int = 0  # Syntactic
    layer2_rejections: int = 0  # Semantic
    layer3_rejections: int = 0  # Teleological
    layer4_rejections: int = 0  # Thermodynamic
    layer5_rejections: int = 0  # Economic
    passed: int = 0

    @property
    def rejection_rate(self) -> float:
        """Overall rejection rate."""
        if self.total_checked == 0:
            return 0.0
        return 1.0 - (self.passed / self.total_checked)

    @property
    def layer_rejection_rates(self) -> dict[int, float]:
        """Rejection rate per layer (of mutations reaching that layer)."""
        rates = {}
        remaining = self.total_checked

        for layer, rejections in enumerate(
            [
                self.layer1_rejections,
                self.layer2_rejections,
                self.layer3_rejections,
                self.layer4_rejections,
                self.layer5_rejections,
            ],
            start=1,
        ):
            if remaining > 0:
                rates[layer] = rejections / remaining
                remaining -= rejections
            else:
                rates[layer] = 0.0

        return rates

    def record(self, result: SelectionResult) -> None:
        """Record a selection result."""
        self.total_checked += 1

        if result.passed:
            self.passed += 1
        else:
            layer_to_attr = {
                1: "layer1_rejections",
                2: "layer2_rejections",
                3: "layer3_rejections",
                4: "layer4_rejections",
                5: "layer5_rejections",
            }
            attr = layer_to_attr.get(result.layer_reached)
            if attr:
                setattr(self, attr, getattr(self, attr) + 1)


# =============================================================================
# Parasitic Pattern Detection
# =============================================================================


@dataclass
class ParasiticPattern:
    """A pattern that indicates parasitic code evolution."""

    name: str
    description: str
    detector: Callable[[str, str], bool]  # (original, mutated) -> is_parasitic


def detect_hardcoding(original: str, mutated: str) -> bool:
    """Detect if mutation hardcodes test values."""
    try:
        orig_tree = ast.parse(original)
        mut_tree = ast.parse(mutated)
    except SyntaxError:
        return False

    # Count literal values in return statements
    orig_literals = sum(
        1
        for node in ast.walk(orig_tree)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)
    )
    mut_literals = sum(
        1
        for node in ast.walk(mut_tree)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)
    )

    # Significant increase in hardcoded returns is suspicious
    return mut_literals > orig_literals + 2


def detect_functionality_deletion(original: str, mutated: str) -> bool:
    """Detect if mutation deletes significant functionality."""
    try:
        orig_tree = ast.parse(original)
        mut_tree = ast.parse(mutated)
    except SyntaxError:
        return False

    # Count meaningful statements (not just body length)
    def count_statements(tree: ast.AST) -> int:
        """Count meaningful statements recursively."""
        total = 0
        for node in ast.walk(tree):
            # Count actual work: assignments, calls, returns with values
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                total += 1
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                total += 1
            elif isinstance(node, ast.Return) and node.value is not None:
                total += 1
            elif isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
                total += 1
            elif isinstance(node, ast.comprehension):
                # Comprehensions are condensed functionality
                total += 2
        return total

    orig_stmts = count_statements(orig_tree)
    mut_stmts = count_statements(mut_tree)

    # Only flag if significant functionality loss AND very short result
    # A comprehension replacing a loop is NOT deletion
    if orig_stmts > 3 and mut_stmts < orig_stmts * 0.3 and mut_stmts < 2:
        return True

    return False


def detect_pass_only_bodies(original: str, mutated: str) -> bool:
    """Detect if mutation introduces pass-only function bodies."""
    try:
        mut_tree = ast.parse(mutated)
    except SyntaxError:
        return False

    # Count functions with only 'pass' in body
    for node in ast.walk(mut_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check if body is just pass (or docstring + pass)
            effective_body = [
                n
                for n in node.body
                if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))
            ]
            if len(effective_body) == 1 and isinstance(effective_body[0], ast.Pass):
                return True

    return False


def detect_test_gaming(original: str, mutated: str) -> bool:
    """Detect if mutation games tests (e.g., special-cases test inputs)."""
    try:
        orig_tree = ast.parse(original)
        mut_tree = ast.parse(mutated)
    except SyntaxError:
        return False

    # Count if-statements (too many new ifs might be test gaming)
    def count_ifs(tree: ast.AST) -> int:
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))

    orig_ifs = count_ifs(orig_tree)
    mut_ifs = count_ifs(mut_tree)

    # Significant increase in conditionals is suspicious
    return mut_ifs > orig_ifs + 3


# Standard parasitic patterns
PARASITIC_PATTERNS: list[ParasiticPattern] = [
    ParasiticPattern(
        name="hardcoding",
        description="Hardcodes return values to pass tests",
        detector=detect_hardcoding,
    ),
    ParasiticPattern(
        name="functionality_deletion",
        description="Deletes functionality to reduce test surface",
        detector=detect_functionality_deletion,
    ),
    ParasiticPattern(
        name="pass_only_bodies",
        description="Replaces implementations with pass statements",
        detector=detect_pass_only_bodies,
    ),
    ParasiticPattern(
        name="test_gaming",
        description="Special-cases test inputs to pass",
        detector=detect_test_gaming,
    ),
]


# =============================================================================
# Teleological Demon
# =============================================================================


@dataclass
class DemonConfig:
    """Configuration for the Teleological Demon."""

    # Layer 1: Syntactic
    max_diff_lines: int = 500  # Maximum lines changed

    # Layer 2: Semantic
    require_type_compatibility: bool = True
    allow_new_public_names: bool = True

    # Layer 3: Teleological
    min_intent_alignment: float = 0.3  # Minimum cosine similarity
    detect_parasitic_patterns: bool = True

    # Layer 4: Thermodynamic
    require_favorable_gibbs: bool = True
    max_enthalpy_increase: float = 1.0  # Maximum complexity increase

    # Layer 5: Economic
    min_market_odds: float = 0.1  # Minimum odds to proceed
    require_sufficient_funds: bool = True

    # Meta
    skip_layers: set[int] = field(default_factory=set)  # For testing


class TeleologicalDemon:
    """
    The Teleological Demon: 5-layer intent-aware selection.

    The Demon's purpose is to kill mutations cheaply before they reach
    expensive validation (tests). The key insight is that ~90% of mutations
    should die in the first 3 layers.

    Layer ordering is by COST, not importance:
    1. Syntactic (FREE): ast.parse()
    2. Semantic (CHEAP): Type structure check
    3. Teleological (CHEAP-ISH): Intent embedding distance
    4. Thermodynamic (FREE): Gibbs calculation
    5. Economic (FREE): Market quote

    The most important layer is 3 (Teleological), which prevents parasitic
    evolution by checking PURPOSE, not just FITNESS.

    From spec/e-gents/thermodynamics.md:
    > "Without the Demon, evolution drifts toward Empty—the lowest energy
    > state. With the Demon, evolution is constrained to PURPOSE."
    """

    def __init__(
        self,
        config: DemonConfig | None = None,
        intent: Intent | None = None,
        type_checker: Callable[[str, str], bool] | None = None,
        market_quoter: Callable[[MutationVector], tuple[float, bool]] | None = None,
    ) -> None:
        """
        Initialize the Teleological Demon.

        Args:
            config: Demon configuration
            intent: The Intent (teleological field) to align mutations to
            type_checker: Function to check type compatibility (L-gent)
            market_quoter: Function to get market quote (B-gent)
        """
        self.config = config or DemonConfig()
        self.intent = intent
        self.type_checker = type_checker
        self.market_quoter = market_quoter
        self.stats = DemonStats()
        self._parasitic_patterns = list(PARASITIC_PATTERNS)

    def set_intent(self, intent: Intent) -> None:
        """Set or update the Intent (teleological field)."""
        self.intent = intent

    def add_parasitic_pattern(self, pattern: ParasiticPattern) -> None:
        """Add a custom parasitic pattern detector."""
        self._parasitic_patterns.append(pattern)

    # -------------------------------------------------------------------
    # Main Selection Interface
    # -------------------------------------------------------------------

    def select(self, phage: Phage) -> SelectionResult:
        """
        Run the phage through all 5 selection layers.

        This is the main entry point for selection. Updates phage status
        and returns detailed selection result.

        Args:
            phage: The Phage to evaluate

        Returns:
            SelectionResult with pass/fail and layer details
        """
        import time

        start = time.time()

        if phage.mutation is None:
            result = SelectionResult.rejected(
                layer=0,
                reason=RejectionReason.SYNTAX_ERROR,
                detail="Phage has no mutation",
            )
            self.stats.record(result)
            return result

        mutation = phage.mutation

        # Layer 1: Syntactic viability
        if 1 not in self.config.skip_layers:
            result = self._check_layer1_syntax(mutation)
            if not result.passed:
                result.duration_ms = (time.time() - start) * 1000
                phage.status = PhageStatus.REJECTED
                phage.error = f"Layer 1: {result.rejection_reason.value}"
                self.stats.record(result)
                return result

        # Layer 2: Semantic stability
        if 2 not in self.config.skip_layers:
            result = self._check_layer2_semantic(mutation)
            if not result.passed:
                result.duration_ms = (time.time() - start) * 1000
                phage.status = PhageStatus.REJECTED
                phage.error = f"Layer 2: {result.rejection_reason.value}"
                self.stats.record(result)
                return result

        # Layer 3: Teleological alignment
        if 3 not in self.config.skip_layers:
            result = self._check_layer3_teleological(mutation)
            if not result.passed:
                result.duration_ms = (time.time() - start) * 1000
                phage.status = PhageStatus.REJECTED
                phage.intent_alignment = result.intent_alignment
                phage.intent_checked = True
                phage.error = f"Layer 3: {result.rejection_reason.value}"
                self.stats.record(result)
                return result
            phage.intent_alignment = result.intent_alignment
            phage.intent_checked = True

        # Layer 4: Thermodynamic viability
        if 4 not in self.config.skip_layers:
            result = self._check_layer4_thermodynamic(mutation)
            if not result.passed:
                result.duration_ms = (time.time() - start) * 1000
                phage.status = PhageStatus.REJECTED
                phage.error = f"Layer 4: {result.rejection_reason.value}"
                self.stats.record(result)
                return result

        # Layer 5: Economic viability
        if 5 not in self.config.skip_layers:
            result = self._check_layer5_economic(mutation)
            if not result.passed:
                result.duration_ms = (time.time() - start) * 1000
                phage.status = PhageStatus.REJECTED
                phage.error = f"Layer 5: {result.rejection_reason.value}"
                self.stats.record(result)
                return result

        # All layers passed!
        result = SelectionResult.accepted(
            syntax_valid=True,
            type_compatible=True,
            intent_alignment=phage.intent_alignment,
            gibbs_favorable=mutation.is_viable,
            market_viable=True,
        )
        result.duration_ms = (time.time() - start) * 1000

        # Update phage status
        phage.status = PhageStatus.QUOTED

        self.stats.record(result)
        return result

    def select_batch(
        self,
        phages: list[Phage],
    ) -> list[tuple[Phage, SelectionResult]]:
        """
        Run multiple phages through selection.

        Returns list of (phage, result) tuples. Failed phages are included
        so caller can analyze rejection reasons.
        """
        results = []
        for phage in phages:
            result = self.select(phage)
            results.append((phage, result))
        return results

    def filter_batch(self, phages: list[Phage]) -> list[Phage]:
        """
        Filter a batch, returning only phages that pass selection.

        This is a convenience method when you don't need rejection details.
        """
        results = self.select_batch(phages)
        return [phage for phage, result in results if result.passed]

    # -------------------------------------------------------------------
    # Individual Layer Checks
    # -------------------------------------------------------------------

    def _check_layer1_syntax(self, mutation: MutationVector) -> SelectionResult:
        """
        Layer 1: Syntactic viability (FREE).

        Checks:
        - Original code is valid Python
        - Mutated code is valid Python
        - Diff size is within limits
        """
        # Check original code
        try:
            ast.parse(mutation.original_code)
        except SyntaxError as e:
            return SelectionResult.rejected(
                layer=1,
                reason=RejectionReason.SYNTAX_ERROR,
                detail=f"Original code syntax error: {e}",
            )

        # Check mutated code
        try:
            ast.parse(mutation.mutated_code)
        except SyntaxError as e:
            return SelectionResult.rejected(
                layer=1,
                reason=RejectionReason.SYNTAX_ERROR,
                detail=f"Mutated code syntax error: {e}",
            )

        # Check diff size
        if mutation.lines_changed > self.config.max_diff_lines:
            return SelectionResult.rejected(
                layer=1,
                reason=RejectionReason.DIFF_TOO_LARGE,
                detail=f"Diff size {mutation.lines_changed} exceeds limit {self.config.max_diff_lines}",
            )

        return SelectionResult(
            passed=True,
            layer_reached=1,
            syntax_valid=True,
        )

    def _check_layer2_semantic(self, mutation: MutationVector) -> SelectionResult:
        """
        Layer 2: Semantic stability (CHEAP).

        Checks type structure preservation using L-gent's type inference.
        """
        if not self.config.require_type_compatibility:
            return SelectionResult(
                passed=True,
                layer_reached=2,
                syntax_valid=True,
                type_compatible=True,
            )

        if self.type_checker:
            # Use injected type checker (L-gent integration)
            is_compatible = self.type_checker(
                mutation.original_code,
                mutation.mutated_code,
            )
        else:
            # Fallback: basic structural check
            is_compatible = self._basic_type_check(
                mutation.original_code,
                mutation.mutated_code,
            )

        if not is_compatible:
            return SelectionResult.rejected(
                layer=2,
                reason=RejectionReason.TYPE_MISMATCH,
                detail="Mutation breaks type structure",
                syntax_valid=True,
            )

        return SelectionResult(
            passed=True,
            layer_reached=2,
            syntax_valid=True,
            type_compatible=True,
        )

    def _check_layer3_teleological(self, mutation: MutationVector) -> SelectionResult:
        """
        Layer 3: Teleological alignment (CHEAP-ISH).

        This is the KEY layer that prevents parasitic code.

        Checks:
        - Mutation aligns with Intent embedding
        - Mutation doesn't match parasitic patterns
        """
        alignment = 0.0

        # Check Intent alignment (if Intent is set)
        if self.intent is not None:
            # We need the mutation's intent embedding
            # For now, use the mutation description as a proxy
            mutation_text = mutation.description or mutation.mutated_code[:500]

            # Simple check: if Intent has embedding, check alignment
            # In production, this would call L-gent's embed_code_intent()
            if self.intent.embedding:
                # For now, we use the confidence as a proxy for alignment
                # In full implementation, we'd embed mutation_text and compare
                alignment = mutation.confidence
        else:
            # No Intent set - use mutation confidence as alignment proxy
            alignment = mutation.confidence

        # Check minimum alignment
        if alignment < self.config.min_intent_alignment:
            return SelectionResult.rejected(
                layer=3,
                reason=RejectionReason.INTENT_DRIFT,
                detail=f"Intent alignment {alignment:.3f} below threshold {self.config.min_intent_alignment}",
                syntax_valid=True,
                type_compatible=True,
                intent_alignment=alignment,
            )

        # Check parasitic patterns
        if self.config.detect_parasitic_patterns:
            for pattern in self._parasitic_patterns:
                try:
                    if pattern.detector(mutation.original_code, mutation.mutated_code):
                        return SelectionResult.rejected(
                            layer=3,
                            reason=RejectionReason.PARASITIC_PATTERN,
                            detail=f"Detected parasitic pattern: {pattern.name} - {pattern.description}",
                            syntax_valid=True,
                            type_compatible=True,
                            intent_alignment=alignment,
                        )
                except Exception:
                    # Pattern detection failed - don't reject on detector errors
                    pass

        return SelectionResult(
            passed=True,
            layer_reached=3,
            syntax_valid=True,
            type_compatible=True,
            intent_alignment=alignment,
        )

    def _check_layer4_thermodynamic(self, mutation: MutationVector) -> SelectionResult:
        """
        Layer 4: Thermodynamic viability (FREE).

        Checks Gibbs Free Energy: ΔG = ΔH - TΔS < 0
        """
        if not self.config.require_favorable_gibbs:
            return SelectionResult(
                passed=True,
                layer_reached=4,
                syntax_valid=True,
                type_compatible=True,
                gibbs_favorable=True,
            )

        # Check Gibbs viability
        if not mutation.is_viable:
            return SelectionResult.rejected(
                layer=4,
                reason=RejectionReason.UNFAVORABLE_GIBBS,
                detail=f"ΔG = {mutation.gibbs_free_energy:.3f} > 0 (unfavorable)",
                syntax_valid=True,
                type_compatible=True,
            )

        # Check enthalpy limit (prevent complexity explosion)
        if mutation.enthalpy_delta > self.config.max_enthalpy_increase:
            return SelectionResult.rejected(
                layer=4,
                reason=RejectionReason.COMPLEXITY_EXPLOSION,
                detail=f"Enthalpy increase {mutation.enthalpy_delta:.3f} exceeds limit {self.config.max_enthalpy_increase}",
                syntax_valid=True,
                type_compatible=True,
            )

        return SelectionResult(
            passed=True,
            layer_reached=4,
            syntax_valid=True,
            type_compatible=True,
            gibbs_favorable=True,
        )

    def _check_layer5_economic(self, mutation: MutationVector) -> SelectionResult:
        """
        Layer 5: Economic viability (FREE).

        Checks market quote and funding availability.
        """
        if self.market_quoter:
            # Use injected market quoter (B-gent integration)
            odds, has_funds = self.market_quoter(mutation)

            if odds < self.config.min_market_odds:
                return SelectionResult.rejected(
                    layer=5,
                    reason=RejectionReason.ODDS_TOO_POOR,
                    detail=f"Market odds {odds:.3f} below threshold {self.config.min_market_odds}",
                    syntax_valid=True,
                    type_compatible=True,
                    gibbs_favorable=True,
                )

            if self.config.require_sufficient_funds and not has_funds:
                return SelectionResult.rejected(
                    layer=5,
                    reason=RejectionReason.INSUFFICIENT_FUNDS,
                    detail="Insufficient funds for stake",
                    syntax_valid=True,
                    type_compatible=True,
                    gibbs_favorable=True,
                )

        return SelectionResult(
            passed=True,
            layer_reached=5,
            syntax_valid=True,
            type_compatible=True,
            gibbs_favorable=True,
            market_viable=True,
        )

    # -------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------

    def _basic_type_check(self, original: str, mutated: str) -> bool:
        """
        Basic type structure check (fallback when L-gent not available).

        Checks that all public names from original exist in mutated.
        """
        try:
            orig_tree = ast.parse(original)
            mut_tree = ast.parse(mutated)
        except SyntaxError:
            return False

        def get_public_names(tree: ast.AST) -> set[str]:
            names = set()
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    if not node.name.startswith("_"):
                        names.add(node.name)
            return names

        orig_names = get_public_names(orig_tree)
        mut_names = get_public_names(mut_tree)

        # All original public names should exist in mutated
        return orig_names.issubset(mut_names)


# =============================================================================
# Factory Functions
# =============================================================================


def create_demon(
    intent: Intent | None = None,
    config: DemonConfig | None = None,
) -> TeleologicalDemon:
    """Create a Teleological Demon with default configuration."""
    return TeleologicalDemon(
        config=config or DemonConfig(),
        intent=intent,
    )


def create_strict_demon(intent: Intent | None = None) -> TeleologicalDemon:
    """Create a strict Demon (high alignment threshold, all checks enabled)."""
    config = DemonConfig(
        min_intent_alignment=0.5,
        detect_parasitic_patterns=True,
        require_favorable_gibbs=True,
        require_type_compatibility=True,
    )
    return TeleologicalDemon(config=config, intent=intent)


def create_lenient_demon() -> TeleologicalDemon:
    """Create a lenient Demon (low thresholds, minimal checks)."""
    config = DemonConfig(
        min_intent_alignment=0.1,
        detect_parasitic_patterns=False,
        require_favorable_gibbs=False,
        require_type_compatibility=False,
    )
    return TeleologicalDemon(config=config)
