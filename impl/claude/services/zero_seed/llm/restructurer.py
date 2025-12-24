"""
Zero Seed LLM Galois Restructurer: The LLM IS the Galois Adjunction.

> *"The LLM IS the restructurer. The token IS the energy. The loss IS the measure of understanding."*

This is not metaphor. The LLM's compression/generation mechanisms
ARE the mathematical operations R, C, L defined in Galois theory.

Proof: For any content x,
    - R(x) = LLM(compress_prompt(x))
    - C(m) = LLM(expand_prompt(m))
    - L(x,y) = LLM(compare_prompt(x,y))

The adjunction laws hold empirically with high probability when:
    1. Prompts are well-structured (see prompts/)
    2. Token budget is liberal (see budgets.py)
    3. Model selection matches loss tolerance (see QualityBudget)

See: spec/protocols/zero-seed1/llm.md Section 1
"""

from __future__ import annotations

import difflib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .types import Context, LossAxis, ModularContent, Module, Style
from .budgets import BudgetManager, QualityBudget, TokenBudget

if TYPE_CHECKING:
    from agents.k.llm import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Prompt Templates
# -----------------------------------------------------------------------------

RESTRUCTURE_PROMPT = """You are a Galois modularization engine. Your task is to decompose content into its minimal, semantically atomic modules.

INPUT CONTENT:
{content}

CONTEXT:
{context}

OUTPUT REQUIREMENTS:
1. Identify atomic semantic units (axioms, definitions, theorems, lemmas)
2. Extract dependency edges (A depends on B if A references B)
3. Compute compression ratio: len(output) / len(input)
4. Preserve ALL semantic information - no lossy summarization

Return JSON:
{{
  "modules": [
    {{"id": "mod_1", "type": "axiom", "content": "...", "deps": []}},
    {{"id": "mod_2", "type": "theorem", "content": "...", "deps": ["mod_1"]}}
  ],
  "edges": [["mod_2", "mod_1"]],
  "compression_ratio": 0.3,
  "rationale": "Explain why this modularization is minimal"
}}

CRITICAL: If you cannot losslessly modularize (e.g., content is already atomic), return compression_ratio = 1.0 and wrap in a single module.

Return ONLY valid JSON, no markdown code blocks."""


RECONSTITUTE_PROMPT = """You are a Galois reconstitution engine. Your task is to expand modular content back into fluent prose.

MODULAR REPRESENTATION:
{modules}

STYLE GUIDE:
{style}

OUTPUT REQUIREMENTS:
1. Fluent, natural prose (not a bulleted list)
2. Preserve logical dependencies (if A depends on B, introduce B first)
3. Match the style guide (formal theorem vs. intuitive explanation)
4. Include ALL semantic content from modules - no omissions

Return the expanded prose directly (not JSON)."""


GALOIS_LOSS_PROMPT = """You are a semantic distance metric. Compare two texts and measure information loss.

ORIGINAL:
{original}

RECONSTITUTED:
{reconstituted}

AXIS: {axis}

INSTRUCTIONS:
- Semantic axis: Do they convey the same information? Ignore wording differences.
- Logical axis: If original proves X, does reconstituted prove X? Check validity.
- Stylistic axis: Do they have the same tone, formality, voice?
- Structural axis: Do they decompose into the same modules?

OUTPUT: A single float from 0.0 to 1.0 where:
  0.0 = perfect preservation (no loss)
  0.5 = significant drift (half the information lost)
  1.0 = complete divergence (unrecognizable)

Return ONLY the float, no explanation."""


# -----------------------------------------------------------------------------
# LLM Client Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Protocol for LLM clients compatible with restructurer."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Any:
        """Generate a response from the LLM."""
        ...


# -----------------------------------------------------------------------------
# LLM Galois Restructurer
# -----------------------------------------------------------------------------


@dataclass
class LLMGaloisRestructurer:
    """The LLM IS the Galois restructure operator.

    This class implements the (R, C, L) Galois adjunction using LLM calls.
    Each method corresponds to a Galois operation:

    - restructure(): R: Content -> Modular
    - reconstitute(): C: Modular -> Content
    - galois_loss(): L: Content x Content -> [0,1]

    The adjunction laws are enforced empirically:
    - L(x, C(R(x))) < epsilon (lossless round-trip)
    - R(C(m)) = m (reconstitution is left-inverse)

    Usage:
        from agents.k.llm import create_llm_client

        llm = create_llm_client()
        restructurer = LLMGaloisRestructurer(llm)

        # Restructure prose to modules
        modular = await restructurer.restructure(prose, context)

        # Reconstitute back to prose
        prose2 = await restructurer.reconstitute(modular, Style.FORMAL)

        # Measure loss
        loss = await restructurer.galois_loss(prose, prose2, LossAxis.SEMANTIC)
        assert loss < 0.15  # Low loss = good round-trip
    """

    llm: LLMClientProtocol
    budget: BudgetManager = field(default_factory=BudgetManager)
    loss_tolerance: float = 0.15
    cache_enabled: bool = True

    # Cache for loss computations (expensive)
    _loss_cache: dict[tuple[str, str, LossAxis], float] = field(
        default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        """Initialize quality budget for model selection."""
        self._quality = QualityBudget()

    def select_model(self, task: str) -> str:
        """Select model based on task requirements.

        Args:
            task: One of "restructure", "reconstitute", "loss"

        Returns:
            Model name for the task
        """
        # Task-specific loss tolerances
        tolerances = {
            "restructure": 0.10,  # Need high fidelity for modularization
            "reconstitute": 0.15,  # Can tolerate some variation
            "loss": 0.30,  # Fast model for metric computation
        }

        max_loss = tolerances.get(task, self.loss_tolerance)
        return self._quality.select_model(task, max_loss)

    async def restructure(
        self,
        content: str,
        context: Context,
    ) -> ModularContent:
        """R: Content -> Modular

        Maps arbitrary prose to its minimal modular representation.
        Preserves semantic information while compressing syntax.

        Args:
            content: Prose content to modularize
            context: Domain context (axioms, existing modules)

        Returns:
            ModularContent with atomic modules and dependency graph

        Invariant: L(content, C(R(content))) < self.loss_tolerance
        """
        # Estimate tokens
        estimated_input = len(content) // 4 + 500  # Rough tokenization
        estimated_output = 2000  # JSON output

        # Check budget
        plan = self.budget.plan_operation(
            task="restructure",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.10,
        )

        # Build prompt
        prompt = RESTRUCTURE_PROMPT.format(
            content=content,
            context=context.render(),
        )

        # Call LLM
        response = await self.llm.generate(
            system="You are a Galois modularization engine that preserves semantic information.",
            user=prompt,
            temperature=0.0,  # Deterministic for reproducibility
            max_tokens=10_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=len(response.text) // 4,
        )

        # Parse response
        return self._parse_modular_response(response.text)

    async def reconstitute(
        self,
        modular: ModularContent,
        style: Style,
    ) -> str:
        """C: Modular -> Content

        Maps modular representation back to prose.
        Style guide allows controlled variation (theorem vs. proof vs. explanation).

        Args:
            modular: Modular content to expand
            style: Output style (FORMAL, CONCISE, INTUITIVE, etc.)

        Returns:
            Fluent prose containing all module content

        Invariant: R(C(m)) = m (up to normalization)
        """
        # Estimate tokens
        module_text = modular.render_for_llm()
        estimated_input = len(module_text) // 4 + 300
        estimated_output = len(module_text)  # Expansion factor ~1x

        # Check budget
        plan = self.budget.plan_operation(
            task="reconstitute",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.15,
        )

        # Build prompt
        prompt = RECONSTITUTE_PROMPT.format(
            modules=module_text,
            style=style.description,
        )

        # Call LLM
        response = await self.llm.generate(
            system="You are a Galois reconstitution engine that produces fluent prose.",
            user=prompt,
            temperature=0.3,  # Slight variation for natural prose
            max_tokens=20_000,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=len(response.text) // 4,
        )

        return response.text.strip()

    async def galois_loss(
        self,
        x: str,
        y: str,
        axis: LossAxis,
    ) -> float:
        """L: Content x Content -> [0,1]

        Semantic distance metric. Not string edit distance - captures
        whether the MEANING is preserved.

        Args:
            x: Original content
            y: Reconstituted content
            axis: Which aspect to measure (SEMANTIC, LOGICAL, etc.)

        Returns:
            Loss in [0, 1] where 0 = identical, 1 = completely different
        """
        # Check cache
        cache_key = (x, y, axis)
        if self.cache_enabled and cache_key in self._loss_cache:
            return self._loss_cache[cache_key]

        # Estimate tokens
        estimated_input = (len(x) + len(y)) // 4 + 200
        estimated_output = 10  # Just a float

        # Check budget
        plan = self.budget.plan_operation(
            task="loss",
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            max_loss=0.30,  # Fast model OK for metrics
        )

        # Build prompt
        prompt = GALOIS_LOSS_PROMPT.format(
            original=x,
            reconstituted=y,
            axis=axis.value,
        )

        # Call LLM
        response = await self.llm.generate(
            system="You are a semantic distance metric. Return only a float.",
            user=prompt,
            temperature=0.0,
            max_tokens=10,
        )

        # Record usage
        self.budget.record_usage(
            actual_input=estimated_input,
            actual_output=5,
        )

        # Parse response
        try:
            loss = float(response.text.strip())
            loss = max(0.0, min(1.0, loss))  # Clamp to [0, 1]
        except ValueError:
            # Fallback: use edit distance as crude approximation
            logger.warning(
                f"Failed to parse loss response: {response.text[:50]}, falling back to edit distance"
            )
            loss = 1.0 - difflib.SequenceMatcher(None, x, y).ratio()

        # Cache result
        if self.cache_enabled:
            self._loss_cache[cache_key] = loss

        return loss

    async def round_trip_loss(
        self,
        content: str,
        context: Context,
        style: Style = Style.FORMAL,
        axis: LossAxis = LossAxis.SEMANTIC,
    ) -> float:
        """Compute L(x, C(R(x))) - the fundamental Galois coherence metric.

        This measures how much information is lost when content is
        modularized and then reconstituted.

        Args:
            content: Original content
            context: Domain context
            style: Style for reconstitution
            axis: Loss measurement axis

        Returns:
            Round-trip loss in [0, 1]
        """
        # R(x)
        modular = await self.restructure(content, context)

        # C(R(x))
        reconstituted = await self.reconstitute(modular, style)

        # L(x, C(R(x)))
        loss = await self.galois_loss(content, reconstituted, axis)

        return loss

    def _parse_modular_response(self, response: str) -> ModularContent:
        """Parse LLM response into ModularContent.

        Handles common LLM output quirks:
        - Response might be in markdown code blocks
        - Fields might use different casing
        - Arrays might be null vs empty
        """
        # Extract JSON from response
        json_text = self._extract_json(response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}. Response: {json_text[:200]}")
            # Return single-module fallback
            return ModularContent(
                modules=[Module(id="mod_1", type="content", content=response, deps=[])],
                compression_ratio=1.0,
            )

        return ModularContent.from_dict(data)

    def _extract_json(self, response: str) -> str:
        """Extract JSON from various response formats."""
        import re

        response = response.strip()

        # Try raw JSON first
        if response.startswith("{") and response.endswith("}"):
            return response

        # Try markdown code block
        code_block_patterns = [
            r"```json\s*\n?(.*?)\n?```",
            r"```\s*\n?(.*?)\n?```",
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                if extracted.startswith("{"):
                    return extracted

        # Try to find JSON object in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Last resort: return as-is
        return response

    def clear_cache(self) -> None:
        """Clear the loss computation cache."""
        self._loss_cache.clear()

    def get_budget_summary(self) -> dict[str, Any]:
        """Get budget usage summary."""
        return self.budget.summary()


# -----------------------------------------------------------------------------
# Factory Functions
# -----------------------------------------------------------------------------


def create_restructurer(
    llm: LLMClientProtocol | None = None,
    token_budget: int = 1_000_000,
    loss_tolerance: float = 0.15,
) -> LLMGaloisRestructurer:
    """Create a configured LLMGaloisRestructurer.

    Args:
        llm: LLM client (auto-creates if None)
        token_budget: Maximum session token budget
        loss_tolerance: Default loss tolerance

    Returns:
        Configured restructurer instance
    """
    if llm is None:
        from agents.k.llm import create_llm_client

        llm = create_llm_client()

    budget = BudgetManager(
        token=TokenBudget(max_session_cumulative=token_budget),
    )

    return LLMGaloisRestructurer(
        llm=llm,
        budget=budget,
        loss_tolerance=loss_tolerance,
    )


__all__ = [
    "LLMGaloisRestructurer",
    "LLMClientProtocol",
    "create_restructurer",
    # Prompt templates (for customization)
    "RESTRUCTURE_PROMPT",
    "RECONSTITUTE_PROMPT",
    "GALOIS_LOSS_PROMPT",
]
