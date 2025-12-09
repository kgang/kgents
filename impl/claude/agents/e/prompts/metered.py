"""
Metered prompt system for conservative token consumption.

Integrates B-gent Banker concepts (spec/b-gents/banker.md):
- Linear Logic: Tokens are resources that are *consumed*, not copied
- Token Bucket (Hydraulic): Balance refills over time, burst capacity
- Sinking Fund: 1% tax for emergency reserves
- Metered Functor: Agent[A, B] → Agent[A, Receipt[B]]
- Token Futures: Reserve capacity for multi-step jobs

Implements the E-gents Metered Principle (spec/e-gents/README.md #11):
- Start minimal: Default prompts ~30 lines
- Escalate on failure: Rich context is recovery, not default
- Diff over whole: Request changed symbols, not entire files
- Lazy loading: API refs loaded only on hallucination
- Budget awareness: Track tokens, abort if exceeded

Token Budget Levels:
| Level | Prompt Size | Context | Cost Multiplier |
|-------|-------------|---------|-----------------|
| 0 | ~30 lines | Hypothesis + target | 1x |
| 1 | ~80 lines | + function context | 3x |
| 2 | ~250 lines | + API refs, patterns | 10x |
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from .base import PromptContext
    from ..experiment import CodeModule
    from ..ast_analyzer import CodeStructure


# =============================================================================
# Token Economics (from B-gent Banker)
# =============================================================================


class PromptLevel(IntEnum):
    """Prompt verbosity levels, ordered by token cost."""

    MINIMAL = 0  # ~30 lines, hypothesis + target only (1x cost)
    TARGETED = 1  # ~80 lines, + function/class context (3x cost)
    FULL = 2  # ~250 lines, + API refs, patterns (10x cost)

    @property
    def cost_multiplier(self) -> float:
        """Token cost multiplier relative to MINIMAL."""
        return {0: 1.0, 1: 3.0, 2: 10.0}[self.value]


@dataclass
class TokenBudget:
    """
    Token Bucket with Hydraulic Refill (from B-gent Banker).

    Implements the "Leaky Bucket" rate limiter from network engineering.
    Balance refills over time, allowing burst capacity.
    """

    max_balance: int = 10000
    balance: int = 10000
    refill_rate: float = 100.0  # Tokens per second
    last_update: float = field(default_factory=time.time)

    # Tracking
    prompt_tokens: int = 0
    response_tokens: int = 0

    @property
    def used(self) -> int:
        return self.prompt_tokens + self.response_tokens

    @property
    def remaining(self) -> int:
        self._refresh()
        return self.balance

    @property
    def exceeded(self) -> bool:
        return self.balance <= 0

    def _refresh(self) -> None:
        """Hydraulic refill: Time = Money (from Banker spec)."""
        now = time.time()
        delta = now - self.last_update
        inflow = int(delta * self.refill_rate)
        self.balance = min(self.max_balance, self.balance + inflow)
        self.last_update = now

    def can_afford(self, tokens: int) -> bool:
        """Check if we can afford this many tokens."""
        self._refresh()
        return self.balance >= tokens

    def spend(self, prompt_tokens: int, response_tokens: int) -> bool:
        """
        Spend tokens (Linear Logic: consumed, not copied).

        Returns True if successful, False if insufficient balance.
        """
        total = prompt_tokens + response_tokens
        self._refresh()

        if self.balance < total:
            return False

        self.balance -= total
        self.prompt_tokens += prompt_tokens
        self.response_tokens += response_tokens
        return True

    def record(self, prompt_tokens: int, response_tokens: int) -> None:
        """Legacy method for compatibility."""
        self.spend(prompt_tokens, response_tokens)


@dataclass
class SinkingFund:
    """
    Emergency reserve from 1% tax on all transactions (from B-gent Banker).

    Purpose: If a critical evolution job (like fixing a crash) hits 0 budget
    but MUST run, the fund grants an emergency loan.
    """

    reserve: float = 0.0
    tax_rate: float = 0.01  # 1% of all transactions

    def tax(self, amount: int) -> int:
        """Collect tax from transaction, return remaining."""
        tax = int(amount * self.tax_rate)
        self.reserve += tax
        return amount - tax

    def can_loan(self, amount: int) -> bool:
        """Check if emergency loan is possible."""
        return self.reserve >= amount

    def emergency_loan(self, amount: int) -> bool:
        """Grant emergency loan. Returns True if successful."""
        if amount > self.reserve:
            return False
        self.reserve -= amount
        return True


@dataclass
class TokenFuture:
    """
    Reservation of future tokens (from B-gent Banker).

    Like a financial option, this reserves capacity without
    consuming it until needed. Ensures Atomic Economics:
    either you have budget for the whole job, or you don't start.
    """

    reserved_tokens: int
    holder: str  # hypothesis ID or agent ID
    expires_at: datetime
    exercise_price: int = 0  # Premium paid for reservation

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at


B = TypeVar("B")


@dataclass
class Receipt(Generic[B]):
    """
    Receipt from metered execution (from B-gent Metered Functor).

    Type: Agent[A, B] → Agent[A, Receipt[B]]
    """

    value: B
    tokens_estimated: int
    tokens_actual: int
    level: PromptLevel
    duration_ms: float
    from_sinking_fund: bool = False

    @property
    def efficiency(self) -> float:
        """How accurate was our estimate? 1.0 = perfect."""
        if self.tokens_estimated == 0:
            return 0.0
        return min(1.0, self.tokens_estimated / max(1, self.tokens_actual))


@dataclass
class MeteredPromptConfig:
    """Configuration for metered prompt generation."""

    initial_level: PromptLevel = PromptLevel.MINIMAL
    max_level: PromptLevel = PromptLevel.FULL
    failures_before_escalate: int = 1
    budget: TokenBudget = field(default_factory=TokenBudget)
    sinking_fund: SinkingFund = field(default_factory=SinkingFund)
    # Lazy loading flags
    include_api_refs: bool = False  # Only set True after hallucination
    include_patterns: bool = False  # Only set True after style issues
    # Futures
    reserved_futures: list[TokenFuture] = field(default_factory=list)


# =============================================================================
# Level 0: Minimal Prompt (~30 lines)
# =============================================================================


def build_minimal_prompt(
    hypothesis: str,
    module: "CodeModule",
    target_symbol: Optional[str] = None,
) -> str:
    """
    Minimal prompt for simple improvements.

    ~30 lines. Used by default. Demonstrates that E-gents can succeed
    with minimal context before requesting more.

    Args:
        hypothesis: The improvement to make
        module: The module to improve
        target_symbol: Optional specific function/class to target

    Returns:
        Minimal prompt string
    """
    code_lines = module.path.read_text().splitlines()
    line_count = len(code_lines)

    target_hint = ""
    if target_symbol:
        target_hint = f"\nTarget: `{target_symbol}` function/class"

    return f"""# Improve {module.name}

Hypothesis: {hypothesis}{target_hint}

Module: {module.path.name} ({line_count} lines)
Category: {module.category}

## Requirements
1. Return ONLY the changed function/class (not entire file)
2. Maintain existing type signatures
3. Keep imports if adding new ones

## Output Format
```python
# Changed code here
```

Brief explanation of change (1-2 sentences).
"""


# =============================================================================
# Level 1: Targeted Prompt (~80 lines)
# =============================================================================


def build_targeted_prompt(
    hypothesis: str,
    module: "CodeModule",
    target_symbol: str,
    structure: Optional["CodeStructure"] = None,
) -> str:
    """
    Targeted prompt with function/class context.

    ~80 lines. Used after Level 0 fails. Includes the specific
    function/class being modified plus its immediate context.

    Args:
        hypothesis: The improvement to make
        module: The module to improve
        target_symbol: The specific function/class to target
        structure: Optional AST structure for context

    Returns:
        Targeted prompt string
    """
    code = module.path.read_text()

    # Extract the target function/class
    target_code = _extract_symbol(code, target_symbol)
    if not target_code:
        # Fallback: first 100 lines
        target_code = "\n".join(code.splitlines()[:100])

    # Get signature info if available
    sig_info = ""
    if structure:
        for func in structure.functions:
            if func["name"] == target_symbol:
                args = func.get("args", [])
                returns = func.get("returns", "?")
                sig_info = f"\nSignature: ({', '.join(args)}) -> {returns}"
                break
        for cls in structure.classes:
            if cls["name"] == target_symbol:
                bases = cls.get("bases", [])
                sig_info = f"\nClass bases: {', '.join(bases) if bases else 'None'}"
                break

    return f"""# Improve {module.name}::{target_symbol}

Hypothesis: {hypothesis}
Module: {module.path.name}
Category: {module.category}{sig_info}

## Current Implementation
```python
{target_code}
```

## Requirements
1. Return the improved function/class
2. Preserve type signatures (or improve them)
3. Include any new imports needed
4. Explain what changed and why

## Output Format

### CHANGES
```python
# Your improved code
```

### RATIONALE
Brief explanation (2-3 sentences).
"""


def _extract_symbol(code: str, symbol: str) -> Optional[str]:
    """Extract a function or class definition from code."""
    import ast

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == symbol:
                return ast.get_source_segment(code, node)
        elif isinstance(node, ast.ClassDef):
            if node.name == symbol:
                return ast.get_source_segment(code, node)

    return None


# =============================================================================
# Level 2: Full Prompt (~250 lines) - Legacy, use sparingly
# =============================================================================


def build_full_prompt(
    hypothesis: str,
    context: "PromptContext",
    improvement_type: str = "refactor",
    api_hints: Optional[list[str]] = None,
) -> str:
    """
    Full prompt with API references and patterns.

    ~250 lines. Used only after Level 1 fails twice.
    This is the legacy behavior - verbose but comprehensive.

    Args:
        hypothesis: The improvement to make
        context: Rich prompt context
        improvement_type: Type of improvement
        api_hints: Specific APIs to include refs for (lazy loading)

    Returns:
        Full prompt string (delegates to legacy implementation)
    """
    from .improvement import build_improvement_prompt

    return build_improvement_prompt(hypothesis, context, improvement_type)


# =============================================================================
# Metered Prompt Builder
# =============================================================================


@dataclass
class MeteredPromptResult:
    """Result of metered prompt generation."""

    prompt: str
    level: PromptLevel
    estimated_tokens: int
    budget: TokenBudget
    from_sinking_fund: bool = False


class MeteredPromptBuilder:
    """
    Build prompts with progressive escalation and economic metering.

    Integrates B-gent Banker concepts:
    - Token Bucket with hydraulic refill
    - Sinking Fund for emergencies
    - Token Futures for reservations
    - Receipt-based execution tracking

    Usage:
        builder = MeteredPromptBuilder(config)

        # First attempt: minimal prompt
        result = builder.build(hypothesis, module)

        # If that fails, escalate
        result = builder.escalate_and_build(hypothesis, module, structure)

        # For multi-step jobs, reserve capacity upfront
        future = builder.reserve_tokens(5000, "evolution_job_123", hours=2)
    """

    def __init__(self, config: Optional[MeteredPromptConfig] = None):
        self.config = config or MeteredPromptConfig()
        self._current_level = self.config.initial_level
        self._failure_count = 0

    @property
    def current_level(self) -> PromptLevel:
        return self._current_level

    @property
    def budget(self) -> TokenBudget:
        return self.config.budget

    @property
    def sinking_fund(self) -> SinkingFund:
        return self.config.sinking_fund

    def reserve_tokens(
        self,
        tokens: int,
        holder: str,
        hours: float = 1.0,
    ) -> Optional[TokenFuture]:
        """
        Reserve tokens for a multi-step job (Token Futures).

        Ensures Atomic Economics: either you have budget for the whole job,
        or you don't start. Prevents the case where step 49 of 50 fails
        due to budget exhaustion.

        Args:
            tokens: Number of tokens to reserve
            holder: ID of the job/hypothesis reserving
            hours: How long the reservation is valid

        Returns:
            TokenFuture if successful, None if insufficient balance
        """
        if not self.config.budget.can_afford(tokens):
            return None

        future = TokenFuture(
            reserved_tokens=tokens,
            holder=holder,
            expires_at=datetime.now() + timedelta(hours=hours),
        )
        self.config.reserved_futures.append(future)
        return future

    def exercise_future(self, future: TokenFuture) -> bool:
        """
        Exercise a token future to get the reserved tokens.

        Returns True if successful, False if expired or invalid.
        """
        if not future.is_valid:
            return False

        if future not in self.config.reserved_futures:
            return False

        self.config.reserved_futures.remove(future)
        return True

    def build(
        self,
        hypothesis: str,
        module: "CodeModule",
        target_symbol: Optional[str] = None,
        structure: Optional["CodeStructure"] = None,
        context: Optional["PromptContext"] = None,
        critical: bool = False,
    ) -> MeteredPromptResult:
        """
        Build prompt at current level with economic metering.

        Args:
            hypothesis: Improvement hypothesis
            module: Target module
            target_symbol: Specific symbol to target
            structure: AST structure (for Level 1+)
            context: Full context (for Level 2)
            critical: If True, can draw from sinking fund

        Returns:
            MeteredPromptResult with prompt and metadata
        """
        if self._current_level == PromptLevel.MINIMAL:
            prompt = build_minimal_prompt(hypothesis, module, target_symbol)
        elif self._current_level == PromptLevel.TARGETED:
            if not target_symbol:
                # Try to infer target from hypothesis
                target_symbol = _infer_target(hypothesis, structure)
            prompt = build_targeted_prompt(
                hypothesis, module, target_symbol or "", structure
            )
        else:  # FULL
            if context:
                prompt = build_full_prompt(hypothesis, context)
            else:
                # Fallback to targeted if no context
                prompt = build_targeted_prompt(
                    hypothesis, module, target_symbol or "", structure
                )

        estimated_tokens = _estimate_tokens(prompt)
        from_sinking_fund = False

        # Check if we can afford this prompt
        if not self.config.budget.can_afford(estimated_tokens):
            if critical and self.config.sinking_fund.can_loan(estimated_tokens):
                # Emergency loan from sinking fund
                self.config.sinking_fund.emergency_loan(estimated_tokens)
                from_sinking_fund = True
            else:
                # Cannot afford - return empty prompt indicator
                # (caller should handle this)
                pass

        # Apply sinking fund tax (1% to reserve)
        taxed_tokens = self.config.sinking_fund.tax(estimated_tokens)

        return MeteredPromptResult(
            prompt=prompt,
            level=self._current_level,
            estimated_tokens=taxed_tokens,
            budget=self.config.budget,
            from_sinking_fund=from_sinking_fund,
        )

    def record_failure(self) -> bool:
        """
        Record a failure and potentially escalate.

        Returns:
            True if escalated, False if at max level
        """
        self._failure_count += 1

        if self._failure_count >= self.config.failures_before_escalate:
            if self._current_level < self.config.max_level:
                self._current_level = PromptLevel(self._current_level + 1)
                self._failure_count = 0
                return True

        return False

    def record_success(self) -> None:
        """Record success - reset failure count but don't de-escalate."""
        self._failure_count = 0

    def escalate_and_build(
        self,
        hypothesis: str,
        module: "CodeModule",
        target_symbol: Optional[str] = None,
        structure: Optional["CodeStructure"] = None,
        context: Optional["PromptContext"] = None,
        critical: bool = False,
    ) -> MeteredPromptResult:
        """
        Escalate level and build new prompt.

        Convenience method for failure handling.
        """
        self.record_failure()
        return self.build(
            hypothesis, module, target_symbol, structure, context, critical
        )

    def reset(self) -> None:
        """Reset to initial level for new hypothesis."""
        self._current_level = self.config.initial_level
        self._failure_count = 0

    def get_stats(self) -> dict:
        """Get current economic stats for monitoring."""
        return {
            "balance": self.config.budget.balance,
            "max_balance": self.config.budget.max_balance,
            "tokens_used": self.config.budget.used,
            "sinking_fund_reserve": self.config.sinking_fund.reserve,
            "active_futures": len(self.config.reserved_futures),
            "current_level": self._current_level.name,
            "failure_count": self._failure_count,
        }


def _infer_target(
    hypothesis: str, structure: Optional["CodeStructure"]
) -> Optional[str]:
    """Try to infer the target symbol from hypothesis text."""
    if not structure:
        return None

    hypothesis_lower = hypothesis.lower()

    # Check function names
    for func in structure.functions:
        if func["name"].lower() in hypothesis_lower:
            return func["name"]

    # Check class names
    for cls in structure.classes:
        if cls["name"].lower() in hypothesis_lower:
            return cls["name"]

    return None


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars per token average)."""
    return len(text) // 4


# =============================================================================
# Diff-Based Output Parsing
# =============================================================================


def parse_minimal_output(response: str, module: "CodeModule") -> Optional[str]:
    """
    Parse output from minimal prompt.

    Extracts changed code and applies as diff to original module.
    Returns full file content with changes applied.
    """
    # Import P-gent diff parser
    try:
        from agents.p.strategies.diff_based import DiffBasedParser
    except ImportError:
        # Fallback: just extract code block
        return _extract_code_block(response)

    original = module.path.read_text()
    changed = _extract_code_block(response)

    if not changed:
        return None

    # Try to apply as patch
    parser = DiffBasedParser()
    result = parser.parse(changed)

    if result.success and result.value:
        # Apply patch to original
        return _apply_symbol_replacement(original, result.value)

    # Fallback: return raw extraction
    return changed


def _extract_code_block(text: str) -> Optional[str]:
    """Extract first Python code block from text."""
    import re

    pattern = r"```python\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _apply_symbol_replacement(original: str, new_symbol: str) -> Optional[str]:
    """Replace a function/class in original with new version."""
    import ast

    try:
        # Parse new symbol to get its name
        new_tree = ast.parse(new_symbol)
        new_name = None
        for node in ast.walk(new_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                new_name = node.name
                break

        if not new_name:
            return None

        # Find and replace in original
        orig_tree = ast.parse(original)
        lines = original.splitlines(keepends=True)

        for node in ast.walk(orig_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == new_name:
                    # Replace lines
                    start = node.lineno - 1
                    end = node.end_lineno if node.end_lineno else start + 1

                    # Preserve indentation
                    indent = len(lines[start]) - len(lines[start].lstrip())
                    new_lines = [
                        " " * indent + line + "\n" for line in new_symbol.splitlines()
                    ]

                    return "".join(lines[:start] + new_lines + lines[end:])

        return None

    except SyntaxError:
        return None
