"""
R-gents DSPy Backend - Full DSPy-backed teleprompter implementations.

Phase 2 Implementation: Production-ready teleprompters with actual LLM calls.

This module provides the bridge between kgents R-gent abstractions and
DSPy's optimization implementations, plus native LLM-backed teleprompters
for TextGrad and OPRO strategies.

Integration Strategy:
  1. Signature <-> dspy.Signature conversion
  2. Example <-> dspy.Example conversion
  3. DSPyBootstrapFewShot: DSPy-backed few-shot optimization
  4. DSPyMIPROv2: DSPy-backed Bayesian instruction optimization
  5. LLMTextGrad: LLM-backed textual gradient descent
  6. LLMOpro: LLM-backed meta-prompt optimization

Note: This module requires DSPy for full functionality. The core R-gents
types and interfaces work without DSPy, enabling offline development.

Install DSPy: pip install dspy-ai

See:
  - https://github.com/stanfordnlp/dspy
  - https://dspy.ai/learn/optimization/optimizers/
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from .types import (
    Example,
    FieldSpec,
    OptimizationTrace,
    Signature,
    TeleprompterStrategy,
    TextualGradient,
)

# Conditional import to avoid hard dependency on DSPy
try:
    import dspy
    from dspy.teleprompt import (
        BootstrapFewShot,
        BootstrapFewShotWithRandomSearch,
        MIPROv2,
    )

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None  # type: ignore


# --- DSPy Availability Check ---


def require_dspy() -> None:
    """Raise ImportError if DSPy is not available."""
    if not DSPY_AVAILABLE:
        raise ImportError(
            "DSPy is required for this feature. Install with: pip install dspy-ai"
        )


def is_dspy_available() -> bool:
    """Check if DSPy is available."""
    return DSPY_AVAILABLE


# --- Signature Conversion ---


def signature_to_dspy(signature: Signature) -> Any:
    """
    Convert kgents Signature to DSPy Signature.

    DSPy signatures are created dynamically using type hints.
    """
    require_dspy()

    # Build input fields
    input_fields = {}
    for field_spec in signature.input_fields:
        input_fields[field_spec.name] = (
            field_spec.field_type,
            dspy.InputField(desc=field_spec.description or "Input"),
        )

    # Build output fields
    output_fields = {}
    for field_spec in signature.output_fields:
        output_fields[field_spec.name] = (
            field_spec.field_type,
            dspy.OutputField(desc=field_spec.description or "Output"),
        )

    # Create DSPy signature class dynamically
    sig_class = type(
        "DynamicSignature",
        (dspy.Signature,),
        {
            "__doc__": signature.instructions,
            "__annotations__": {
                **{k: v[0] for k, v in input_fields.items()},
                **{k: v[0] for k, v in output_fields.items()},
            },
            **{k: v[1] for k, v in input_fields.items()},
            **{k: v[1] for k, v in output_fields.items()},
        },
    )

    return sig_class


def dspy_to_signature(dspy_sig: Any) -> Signature:
    """
    Convert DSPy Signature back to kgents Signature.

    Useful for extracting optimized signatures from DSPy modules.
    """
    require_dspy()

    # Extract fields from DSPy signature
    input_fields = []
    output_fields = []

    for name, field_info in dspy_sig.fields.items():
        field_spec = FieldSpec(
            name=name,
            field_type=field_info.annotation
            if hasattr(field_info, "annotation")
            else str,
            description=field_info.desc if hasattr(field_info, "desc") else "",
        )

        if hasattr(field_info, "input") and field_info.input:
            input_fields.append(field_spec)
        else:
            output_fields.append(field_spec)

    return Signature(
        input_fields=tuple(input_fields),
        output_fields=tuple(output_fields),
        instructions=dspy_sig.__doc__ or "",
    )


# --- Example Conversion ---


def example_to_dspy(example: Example) -> Any:
    """Convert kgents Example to DSPy Example."""
    require_dspy()
    return dspy.Example(**example.inputs, **example.outputs).with_inputs(
        *example.inputs.keys()
    )


def examples_to_dspy(examples: list[Example]) -> list[Any]:
    """Convert list of kgents Examples to DSPy Examples."""
    return [example_to_dspy(ex) for ex in examples]


# --- DSPy Module Wrapper ---


@dataclass
class DSPyModuleWrapper:
    """
    Wraps a kgents Agent as a DSPy module for optimization.

    This enables using DSPy teleprompters on kgents agents.
    """

    signature: Signature
    agent: Any  # The underlying Agent[A, B]
    use_chain_of_thought: bool = True

    _dspy_module: Any = field(default=None, init=False)

    def __post_init__(self):
        require_dspy()
        self._build_module()

    def _build_module(self) -> None:
        """Build the DSPy module from signature."""
        dspy_sig = signature_to_dspy(self.signature)

        if self.use_chain_of_thought:
            self._dspy_module = dspy.ChainOfThought(dspy_sig)
        else:
            self._dspy_module = dspy.Predict(dspy_sig)

    def forward(self, **kwargs) -> Any:
        """Execute the DSPy module."""
        return self._dspy_module(**kwargs)

    @property
    def dspy_module(self) -> Any:
        """Access the underlying DSPy module."""
        return self._dspy_module


# --- DSPy BootstrapFewShot (Full Implementation) ---


@dataclass
class DSPyBootstrapFewShot:
    """
    Full DSPy-backed BootstrapFewShot optimizer.

    Strategy:
    1. Generate demonstrations via teacher model
    2. Select best demos by validation performance
    3. Return optimized module with selected demos

    Complexity: O(N) where N = number of examples
    Cost: ~$0.50-2.00 depending on dataset size
    """

    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 4
    max_rounds: int = 1
    use_chain_of_thought: bool = True

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Run DSPy BootstrapFewShot optimization."""
        require_dspy()

        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method="dspy_bootstrap_fewshot",
        )
        trace.started_at = datetime.now()

        # Create DSPy module
        module = DSPyModuleWrapper(
            signature, None, use_chain_of_thought=self.use_chain_of_thought
        )

        # Convert examples
        dspy_examples = examples_to_dspy(examples)

        # Create metric wrapper
        output_name = signature.output_names[0] if signature.output_names else "output"

        def dspy_metric(example, pred, _trace=None):
            pred_value = getattr(pred, output_name, None)
            label_value = example.get(output_name)
            try:
                return metric(pred_value, label_value)
            except Exception:
                return 0.0

        # Compute baseline score
        try:
            baseline_scores = []
            for ex in dspy_examples[:5]:  # Sample for baseline
                pred = module.forward(**{k: ex[k] for k in signature.input_names})
                baseline_scores.append(dspy_metric(ex, pred))
            baseline_score = (
                sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
            )
        except Exception:
            baseline_score = 0.0

        trace.add_iteration(signature.instructions, baseline_score)

        # Run optimizer
        optimizer = BootstrapFewShot(
            metric=dspy_metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            max_rounds=self.max_rounds,
        )

        try:
            optimized = optimizer.compile(
                module.dspy_module,
                trainset=dspy_examples,
            )

            # Evaluate optimized module
            optimized_scores = []
            for ex in dspy_examples[:5]:
                pred = optimized(**{k: ex[k] for k in signature.input_names})
                optimized_scores.append(dspy_metric(ex, pred))
            final_score = (
                sum(optimized_scores) / len(optimized_scores)
                if optimized_scores
                else baseline_score
            )

            trace.add_iteration(signature.instructions, final_score)
            trace.final_prompt = (
                signature.instructions
            )  # Instructions unchanged, demos optimized
            trace.converged = True
            trace.convergence_reason = "DSPy BootstrapFewShot completed"
            trace.total_llm_calls = len(dspy_examples) * 2  # Estimate

        except Exception as e:
            trace.converged = False
            trace.convergence_reason = f"DSPy error: {str(e)}"
            trace.final_prompt = signature.instructions

        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace


# --- DSPy MIPROv2 (Full Implementation) ---


@dataclass
class DSPyMIPROv2:
    """
    Full DSPy-backed MIPROv2 optimizer.

    Strategy: Bayesian optimization over instructions and examples.
    1. Generate candidate instructions via meta-prompting
    2. Use surrogate model to select promising candidates
    3. Evaluate on validation set
    4. Update surrogate and repeat

    Complexity: O(N) iterations with intelligent sampling
    Cost: ~$5-20 depending on configuration
    """

    num_candidates: int = 10
    init_temperature: float = 1.0
    max_bootstrapped_demos: int = 3
    max_labeled_demos: int = 3
    num_threads: int = 1

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Run DSPy MIPROv2 optimization."""
        require_dspy()

        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method="dspy_mipro_v2",
        )
        trace.started_at = datetime.now()

        # Create DSPy module
        module = DSPyModuleWrapper(signature, None)

        # Convert examples
        dspy_examples = examples_to_dspy(examples)

        # Split into train/eval (80/20)
        split_idx = max(int(len(dspy_examples) * 0.8), 1)
        trainset = dspy_examples[:split_idx]
        evalset = (
            dspy_examples[split_idx:]
            if len(dspy_examples) > split_idx
            else dspy_examples[:1]
        )

        # Create metric wrapper
        output_name = signature.output_names[0] if signature.output_names else "output"

        def dspy_metric(example, pred, _trace=None):
            pred_value = getattr(pred, output_name, None)
            label_value = example.get(output_name)
            try:
                return metric(pred_value, label_value)
            except Exception:
                return 0.0

        # Compute baseline
        try:
            baseline_scores = []
            for ex in evalset[:3]:
                pred = module.forward(**{k: ex[k] for k in signature.input_names})
                baseline_scores.append(dspy_metric(ex, pred))
            baseline_score = (
                sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
            )
        except Exception:
            baseline_score = 0.0

        trace.add_iteration(signature.instructions, baseline_score)

        # Run optimizer
        try:
            optimizer = MIPROv2(
                metric=dspy_metric,
                num_candidates=self.num_candidates,
                init_temperature=self.init_temperature,
            )

            optimized = optimizer.compile(
                module.dspy_module,
                trainset=trainset,
                num_threads=self.num_threads,
                requires_permission_to_run=False,
            )

            # Evaluate optimized
            optimized_scores = []
            for ex in evalset[:3]:
                pred = optimized(**{k: ex[k] for k in signature.input_names})
                optimized_scores.append(dspy_metric(ex, pred))
            final_score = (
                sum(optimized_scores) / len(optimized_scores)
                if optimized_scores
                else baseline_score
            )

            # Try to extract optimized instruction
            final_instruction = signature.instructions
            if (
                hasattr(optimized, "extended_signature")
                and optimized.extended_signature
            ):
                final_instruction = (
                    optimized.extended_signature.__doc__ or signature.instructions
                )

            trace.add_iteration(final_instruction, final_score)
            trace.final_prompt = final_instruction
            trace.converged = True
            trace.convergence_reason = "DSPy MIPROv2 completed"
            trace.total_llm_calls = self.num_candidates * len(trainset)  # Estimate

        except Exception as e:
            trace.converged = False
            trace.convergence_reason = f"DSPy error: {str(e)}"
            trace.final_prompt = signature.instructions

        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace


# --- LLM-backed TextGrad (Full Implementation) ---


@dataclass
class LLMTextGrad:
    """
    LLM-backed TextGrad optimizer.

    TextGrad: Gradient descent in prompt space using textual feedback.

    Strategy:
    1. Evaluate current prompt on examples
    2. For failures, generate textual critiques (gradients)
    3. Aggregate critiques into update direction
    4. Ask LLM to apply gradient to prompt
    5. Repeat until convergence

    Complexity: O(N^2) - N iterations, N examples each
    Cost: ~$5-15 depending on iterations and examples

    Requires: An LLM function (llm_func) that takes a prompt and returns response.
    """

    llm_func: Callable[[str], str] | None = None
    learning_rate: float = 1.0
    convergence_threshold: float = 0.02
    max_failed_examples: int = 5

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Run TextGrad optimization."""
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method="textgrad",
        )
        trace.started_at = datetime.now()

        if self.llm_func is None:
            trace.converged = False
            trace.convergence_reason = "TextGrad requires llm_func to be configured"
            trace.final_prompt = signature.instructions
            trace.completed_at = datetime.now()
            return trace

        current_prompt = signature.instructions
        prev_score = 0.0
        total_llm_calls = 0

        for iteration in range(max_iterations):
            # 1. Evaluate current prompt
            current_score, failed_examples = await self._evaluate_prompt(
                current_prompt, signature, examples, metric
            )
            trace.add_iteration(current_prompt, current_score)

            # 2. Check convergence
            improvement = current_score - prev_score
            if iteration > 0 and abs(improvement) < self.convergence_threshold:
                trace.converged = True
                trace.convergence_reason = f"Converged: improvement {improvement:.4f} < threshold {self.convergence_threshold}"
                break

            if current_score >= 0.95:  # Near-perfect
                trace.converged = True
                trace.convergence_reason = (
                    f"Converged: score {current_score:.2f} >= 0.95"
                )
                break

            if not failed_examples:
                trace.converged = True
                trace.convergence_reason = "No failed examples to learn from"
                break

            # 3. Compute textual gradients
            gradients = await self._compute_gradients(
                current_prompt, failed_examples[: self.max_failed_examples], signature
            )
            total_llm_calls += len(failed_examples[: self.max_failed_examples])

            if not gradients:
                trace.converged = True
                trace.convergence_reason = "No gradients computed"
                break

            # 4. Apply gradients
            new_prompt = await self._apply_gradients(
                current_prompt, gradients, signature
            )
            total_llm_calls += 1

            if new_prompt == current_prompt:
                trace.converged = True
                trace.convergence_reason = "Prompt unchanged after gradient application"
                break

            current_prompt = new_prompt
            prev_score = current_score

        trace.final_prompt = current_prompt
        trace.total_llm_calls = total_llm_calls
        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        if not trace.converged:
            trace.convergence_reason = f"Max iterations ({max_iterations}) reached"

        return trace

    async def _evaluate_prompt(
        self,
        prompt: str,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
    ) -> tuple[float, list[tuple[Example, Any, float]]]:
        """Evaluate prompt on examples, return score and failed examples."""
        if self.llm_func is None:
            return 0.0, []

        scores = []
        failed = []

        for example in examples:
            # Build prompt with example input
            input_str = "\n".join(f"{k}: {v}" for k, v in example.inputs.items())
            full_prompt = f"{prompt}\n\nInput:\n{input_str}\n\nOutput:"

            try:
                # Get LLM response
                response = self.llm_func(full_prompt)

                # Score against expected output
                expected = list(example.outputs.values())[0] if example.outputs else ""
                score = metric(response, expected)
                scores.append(score)

                if score < 0.8:  # Below threshold
                    failed.append((example, response, score))
            except Exception:
                scores.append(0.0)
                failed.append((example, "", 0.0))

        avg_score = sum(scores) / len(scores) if scores else 0.0
        return avg_score, failed

    async def _compute_gradients(
        self,
        prompt: str,
        failed_examples: list[tuple[Example, Any, float]],
        signature: Signature,
    ) -> list[TextualGradient]:
        """Generate textual gradients (critiques) for failed examples."""
        if self.llm_func is None:
            return []

        gradients = []

        for example, actual_output, score in failed_examples:
            expected = list(example.outputs.values())[0] if example.outputs else ""
            input_str = list(example.inputs.values())[0] if example.inputs else ""

            critique_prompt = f"""Analyze why this prompt produced an incorrect output and provide specific improvement suggestions.

Current Prompt:
{prompt}

Input:
{input_str}

Expected Output:
{expected}

Actual Output:
{actual_output}

Score: {score:.2f}

Provide a concise critique (2-3 sentences) explaining:
1. What specifically went wrong
2. How the prompt should be modified to fix this

Critique:"""

            try:
                critique = self.llm_func(critique_prompt)
                gradients.append(
                    TextualGradient(
                        feedback=critique.strip(),
                        source_example=example,
                        magnitude=1.0 - score,  # Higher magnitude for worse failures
                        aspect="accuracy",
                    )
                )
            except Exception:
                pass

        return gradients

    async def _apply_gradients(
        self,
        prompt: str,
        gradients: list[TextualGradient],
        signature: Signature,
    ) -> str:
        """Apply textual gradients to generate improved prompt."""
        if self.llm_func is None:
            return prompt

        # Aggregate critiques
        critiques = "\n\n".join(
            f"- [{g.magnitude:.2f}] {g.feedback}" for g in gradients
        )

        update_prompt = f"""Given the current prompt and aggregated feedback, generate an improved version.

Current Prompt:
{prompt}

Aggregated Feedback (with severity scores):
{critiques}

Requirements:
1. Address the specific issues mentioned in the feedback
2. Preserve any correct behaviors from the original prompt
3. Keep the prompt clear and concise
4. Output ONLY the improved prompt, nothing else

Improved Prompt:"""

        try:
            improved = self.llm_func(update_prompt)
            return improved.strip()
        except Exception:
            return prompt


# --- LLM-backed OPRO (Full Implementation) ---


@dataclass
class LLMOpro:
    """
    LLM-backed OPRO optimizer.

    OPRO: Optimization by PROmpting - uses meta-prompts to ask the
    LLM to propose better prompts directly.

    Strategy:
    1. Show LLM the current prompt and its score
    2. Show history of previous prompts and scores
    3. Ask LLM to propose an improved prompt
    4. Evaluate new prompt
    5. Keep best-so-far, repeat

    Complexity: O(N) iterations
    Cost: ~$2-5, efficient exploration

    Requires: An LLM function (llm_func) that takes a prompt and returns response.
    """

    llm_func: Callable[[str], str] | None = None
    num_candidates_per_iteration: int = 3
    keep_top_k: int = 5

    async def compile(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        max_iterations: int = 10,
        budget_usd: float | None = None,
    ) -> OptimizationTrace:
        """Run OPRO optimization."""
        trace = OptimizationTrace(
            initial_prompt=signature.instructions,
            method="opro",
        )
        trace.started_at = datetime.now()

        if self.llm_func is None:
            trace.converged = False
            trace.convergence_reason = "OPRO requires llm_func to be configured"
            trace.final_prompt = signature.instructions
            trace.completed_at = datetime.now()
            return trace

        # History of (prompt, score) pairs
        history: list[tuple[str, float]] = []
        best_prompt = signature.instructions
        best_score = 0.0
        total_llm_calls = 0

        # Evaluate initial prompt
        initial_score = await self._evaluate_prompt(
            signature.instructions, signature, examples, metric
        )
        total_llm_calls += len(examples)
        history.append((signature.instructions, initial_score))
        best_score = initial_score
        trace.add_iteration(signature.instructions, initial_score)

        for iteration in range(max_iterations):
            # Generate candidate prompts
            candidates = await self._generate_candidates(history, signature, examples)
            total_llm_calls += self.num_candidates_per_iteration

            # Evaluate each candidate
            for candidate in candidates:
                if candidate == best_prompt:  # Skip duplicates
                    continue

                score = await self._evaluate_prompt(
                    candidate, signature, examples, metric
                )
                total_llm_calls += len(examples)
                history.append((candidate, score))

                if score > best_score:
                    best_prompt = candidate
                    best_score = score
                    trace.add_iteration(candidate, score)

            # Prune history to top-k
            history.sort(key=lambda x: x[1], reverse=True)
            history = history[: self.keep_top_k]

            # Check for convergence
            if best_score >= 0.95:
                trace.converged = True
                trace.convergence_reason = f"Converged: score {best_score:.2f} >= 0.95"
                break

            # Check if no improvement in last 3 iterations
            recent_scores = [h[1] for h in history[:3]]
            if (
                len(recent_scores) >= 3
                and max(recent_scores) - min(recent_scores) < 0.01
            ):
                trace.converged = True
                trace.convergence_reason = (
                    "Converged: no improvement in recent iterations"
                )
                break

        trace.final_prompt = best_prompt
        trace.total_llm_calls = total_llm_calls
        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        if not trace.converged:
            trace.convergence_reason = f"Max iterations ({max_iterations}) reached"

        return trace

    async def _evaluate_prompt(
        self,
        prompt: str,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
    ) -> float:
        """Evaluate a prompt on examples."""
        if self.llm_func is None:
            return 0.0

        scores = []
        for example in examples:
            input_str = "\n".join(f"{k}: {v}" for k, v in example.inputs.items())
            full_prompt = f"{prompt}\n\nInput:\n{input_str}\n\nOutput:"

            try:
                response = self.llm_func(full_prompt)
                expected = list(example.outputs.values())[0] if example.outputs else ""
                score = metric(response, expected)
                scores.append(score)
            except Exception:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    async def _generate_candidates(
        self,
        history: list[tuple[str, float]],
        signature: Signature,
        examples: list[Example],
    ) -> list[str]:
        """Generate candidate prompts using meta-prompting."""
        if self.llm_func is None:
            return []

        # Build history string (sorted by score descending)
        sorted_history = sorted(history, key=lambda x: x[1], reverse=True)
        history_str = "\n\n".join(
            f"Prompt (score {score:.2f}):\n{prompt}"
            for prompt, score in sorted_history[:5]
        )

        # Sample examples for context
        example_str = "\n".join(
            f"Input: {list(ex.inputs.values())[0] if ex.inputs else ''}\n"
            f"Expected: {list(ex.outputs.values())[0] if ex.outputs else ''}"
            for ex in examples[:3]
        )

        meta_prompt = f"""You are an expert prompt engineer. Your task is to propose improved prompts.

## Task Description
{signature.instructions}

## Example Input/Output Pairs
{example_str}

## History of Prompts and Scores
{history_str}

## Your Task
Generate {self.num_candidates_per_iteration} new prompt variations that might score higher.
Learn from the patterns in high-scoring prompts.

Output each prompt on a new line, prefixed with "PROMPT: ".
"""

        try:
            response = self.llm_func(meta_prompt)

            # Parse candidates
            candidates = []
            for line in response.split("\n"):
                if line.strip().startswith("PROMPT:"):
                    candidate = line.replace("PROMPT:", "").strip()
                    if candidate:
                        candidates.append(candidate)

            return candidates[: self.num_candidates_per_iteration]
        except Exception:
            return []


# --- LLM Configuration ---


@dataclass
class DSPyLLMConfig:
    """Configuration for DSPy's LLM backend."""

    model: str = "gpt-4"
    api_key: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7

    def configure(self) -> None:
        """Configure DSPy with this LLM backend."""
        require_dspy()

        # Configure DSPy's language model
        lm = dspy.LM(
            model=self.model,
            api_key=self.api_key,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        dspy.configure(lm=lm)


# --- Factory for DSPy-backed Teleprompters ---


def get_dspy_teleprompter(
    strategy: TeleprompterStrategy,
    llm_func: Callable[[str], str] | None = None,
) -> Any:
    """
    Get a DSPy-backed or LLM-backed teleprompter implementation.

    Args:
        strategy: The optimization strategy to use
        llm_func: Optional LLM function for TextGrad/OPRO

    Returns:
        Teleprompter instance appropriate for the strategy

    Falls back to stub implementations if dependencies not available.
    """
    # DSPy-backed strategies
    if strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT:
        if DSPY_AVAILABLE:
            return DSPyBootstrapFewShot()
        else:
            from .refinery import TeleprompterFactory

            return TeleprompterFactory.get(strategy)

    if strategy == TeleprompterStrategy.BOOTSTRAP_FEWSHOT_RANDOM:
        if DSPY_AVAILABLE:
            return DSPyBootstrapFewShot(max_rounds=3)  # More rounds for exploration
        else:
            from .refinery import TeleprompterFactory

            return TeleprompterFactory.get(strategy)

    if strategy == TeleprompterStrategy.MIPRO_V2:
        if DSPY_AVAILABLE:
            return DSPyMIPROv2()
        else:
            from .refinery import TeleprompterFactory

            return TeleprompterFactory.get(strategy)

    # LLM-backed strategies
    if strategy == TeleprompterStrategy.TEXTGRAD:
        return LLMTextGrad(llm_func=llm_func)

    if strategy == TeleprompterStrategy.OPRO:
        return LLMOpro(llm_func=llm_func)

    # Fallback
    from .refinery import TeleprompterFactory

    return TeleprompterFactory.get(strategy)


# --- Utility: Create LLM function from OpenAI/Anthropic ---


def create_openai_llm_func(
    model: str = "gpt-4",
    api_key: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> Callable[[str], str]:
    """
    Create an LLM function using OpenAI's API.

    Requires: openai package installed
    """
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package required. Install with: pip install openai")

    if api_key:
        openai.api_key = api_key

    def llm_func(prompt: str) -> str:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    return llm_func


def create_anthropic_llm_func(
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
    max_tokens: int = 1024,
) -> Callable[[str], str]:
    """
    Create an LLM function using Anthropic's API.

    Requires: anthropic package installed
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "Anthropic package required. Install with: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def llm_func(prompt: str) -> str:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text if response.content else ""

    return llm_func
