"""
R-gents DSPy Backend - Integration layer for DSPy optimization library.

This module provides the bridge between kgents R-gent abstractions and
DSPy's actual optimization implementations.

Integration Strategy:
  1. Signature -> dspy.Signature conversion
  2. Example -> dspy.Example conversion
  3. Teleprompter wrapper -> dspy optimizers
  4. OptimizationTrace <- dspy optimization history

Note: This module requires DSPy to be installed. The core R-gents types
and interfaces work without DSPy, enabling offline development.

Install DSPy: pip install dspy-ai

See:
  - https://github.com/stanfordnlp/dspy
  - https://dspy.ai/learn/optimization/optimizers/
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, TYPE_CHECKING

from .types import (
    Example,
    FieldSpec,
    OptimizationTrace,
    Signature,
    TeleprompterStrategy,
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

    _dspy_module: Any = field(default=None, init=False)

    def __post_init__(self):
        require_dspy()
        self._build_module()

    def _build_module(self) -> None:
        """Build the DSPy module from signature."""
        dspy_sig = signature_to_dspy(self.signature)

        # Create a ChainOfThought module (most common pattern)
        self._dspy_module = dspy.ChainOfThought(dspy_sig)

    def forward(self, **kwargs) -> Any:
        """Execute the DSPy module."""
        return self._dspy_module(**kwargs)

    @property
    def dspy_module(self) -> Any:
        """Access the underlying DSPy module."""
        return self._dspy_module


# --- DSPy Teleprompter Wrappers ---


@dataclass
class DSPyBootstrapFewShot:
    """
    Wrapper for DSPy BootstrapFewShot optimizer.

    Selects the best examples as few-shot demonstrations.
    """

    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 4

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
        module = DSPyModuleWrapper(signature, None)

        # Convert examples
        dspy_examples = examples_to_dspy(examples)

        # Create metric wrapper
        def dspy_metric(example, pred, trace=None):
            # Extract prediction value
            pred_value = getattr(pred, signature.output_names[0], None)
            # Extract label value
            label_value = example.get(signature.output_names[0])
            return metric(pred_value, label_value)

        # Run optimizer
        optimizer = BootstrapFewShot(
            metric=dspy_metric,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
        )

        try:
            optimized = optimizer.compile(
                module.dspy_module,
                trainset=dspy_examples,
            )

            # Extract optimized prompt (from demos)
            trace.final_prompt = signature.instructions
            trace.converged = True
            trace.convergence_reason = "DSPy BootstrapFewShot completed"

        except Exception as e:
            trace.converged = False
            trace.convergence_reason = f"DSPy error: {str(e)}"

        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace


@dataclass
class DSPyMIPROv2:
    """
    Wrapper for DSPy MIPROv2 optimizer.

    Bayesian optimization over instructions and examples.
    """

    num_candidates: int = 10
    init_temperature: float = 1.0

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

        # Split into train/eval
        split_idx = int(len(dspy_examples) * 0.8)
        trainset = dspy_examples[:split_idx]
        evalset = dspy_examples[split_idx:]

        # Create metric wrapper
        def dspy_metric(example, pred, trace=None):
            pred_value = getattr(pred, signature.output_names[0], None)
            label_value = example.get(signature.output_names[0])
            return metric(pred_value, label_value)

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
                eval_kwargs={"num_threads": 1, "display_progress": False},
            )

            trace.final_prompt = signature.instructions
            trace.converged = True
            trace.convergence_reason = "DSPy MIPROv2 completed"

        except Exception as e:
            trace.converged = False
            trace.convergence_reason = f"DSPy error: {str(e)}"

        trace.completed_at = datetime.now()
        trace.total_examples = len(examples)

        return trace


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


def get_dspy_teleprompter(strategy: TeleprompterStrategy) -> Any:
    """
    Get a DSPy-backed teleprompter implementation.

    Falls back to stub implementations if DSPy is not available.
    """
    if not DSPY_AVAILABLE:
        from .refinery import TeleprompterFactory

        return TeleprompterFactory.get(strategy)

    strategy_map = {
        TeleprompterStrategy.BOOTSTRAP_FEWSHOT: DSPyBootstrapFewShot,
        TeleprompterStrategy.MIPRO_V2: DSPyMIPROv2,
    }

    teleprompter_cls = strategy_map.get(strategy)
    if teleprompter_cls is None:
        # Fall back to stub implementation
        from .refinery import TeleprompterFactory

        return TeleprompterFactory.get(strategy)

    return teleprompter_cls()
