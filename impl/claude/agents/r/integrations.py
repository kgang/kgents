"""
R-gents Phase 3: Cross-Genus Integrations.

This module implements integrations between R-gents and other agent genera:
1. F-gent → R-gent: Post-prototype refinement pipeline
2. T-gent → R-gent: Loss signal adapter (Tool metrics as optimization signals)
3. B-gent → R-gent: Budget grant protocol (ROI-constrained optimization)
4. L-gent → R-gent: Optimization metadata indexing

The integrations enable the full agent lifecycle:
  F-gent (Prototype) → R-gent (Refine) → L-gent (Index)

See spec/r-gents/README.md for full specification.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar
import hashlib
import uuid

from .types import (
    Example,
    OptimizationBudget,
    OptimizationDecision,
    OptimizationTrace,
    ROIEstimate,
    Signature,
    TeleprompterStrategy,
)
from .refinery import RefineryAgent, ROIOptimizer, TeleprompterFactory

# Optional imports - may not be available
try:
    from agents.f.crystallize import Artifact, ArtifactMetadata
    from agents.f.prototype import SourceCode
    from agents.f.intent import Intent
    from agents.f.contract import Contract

    F_GENT_AVAILABLE = True
except ImportError:
    F_GENT_AVAILABLE = False

try:
    from agents.t.tool import Tool, ToolMeta, ToolIdentity
    from agents.t.metrics import MetricObserver

    T_GENT_AVAILABLE = True
except ImportError:
    T_GENT_AVAILABLE = False

try:
    from agents.l.catalog import CatalogEntry, EntityType, Registry, Status

    L_GENT_AVAILABLE = True
except ImportError:
    L_GENT_AVAILABLE = False

try:
    from agents.b.hypothesis import Hypothesis

    B_GENT_AVAILABLE = True
except ImportError:
    B_GENT_AVAILABLE = False


# Type variables
A = TypeVar("A")
B = TypeVar("B")


# =============================================================================
# F-gent → R-gent Integration: Post-Prototype Refinement
# =============================================================================


class RefinePhase(Enum):
    """Phase within the refinement pipeline."""

    PENDING = "pending"
    EXTRACTING = "extracting"  # Extracting signature from prototype
    GENERATING_EXAMPLES = "generating_examples"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    SKIPPED = "skipped"  # ROI check failed
    FAILED = "failed"


@dataclass
class PrototypeRefinementRequest:
    """
    Request to refine an F-gent prototype.

    Encapsulates all inputs needed for the F → R pipeline.
    """

    # The prototype to refine
    source_code: str
    agent_name: str

    # Optional: Pre-existing intent/contract from F-gent
    intent_text: str = ""
    contract_text: str = ""

    # Optimization parameters
    strategy: TeleprompterStrategy = TeleprompterStrategy.BOOTSTRAP_FEWSHOT
    max_iterations: int = 10
    budget_usd: float = 10.0

    # Training data (if available)
    examples: list[Example] = field(default_factory=list)

    # If no examples, generate synthetic ones
    generate_examples: bool = True
    num_synthetic_examples: int = 10

    # ROI parameters
    check_roi: bool = True
    estimated_usage_per_month: int = 1000
    value_per_call_usd: float = 0.10


@dataclass
class PrototypeRefinementResult:
    """
    Result of the F → R refinement pipeline.

    Contains the optimized signature and metadata for crystallization.
    """

    # Status
    phase: RefinePhase
    success: bool

    # Inputs (echoed back)
    request: PrototypeRefinementRequest

    # Outputs
    original_signature: Optional[Signature] = None
    optimized_signature: Optional[Signature] = None
    optimization_trace: Optional[OptimizationTrace] = None

    # ROI decision
    roi_estimate: Optional[ROIEstimate] = None
    roi_decision: Optional[OptimizationDecision] = None

    # Error info
    error_message: str = ""

    @property
    def improvement_percentage(self) -> Optional[float]:
        """Convenience accessor for improvement."""
        if self.optimization_trace:
            return self.optimization_trace.improvement_percentage
        return None


class FGentRefineryBridge:
    """
    Bridge between F-gent Forge Loop and R-gent Refinery.

    Implements Phase 4.5 (Optimize) from spec/f-gents/forge.md:
    - Extract signature from prototype
    - Generate training examples (if needed)
    - Run optimization via R-gent
    - Return refined signature for crystallization

    Category Theory:
        This is a functor F-Prototype → R-Signature that lifts
        untyped source code into typed optimization targets.
    """

    def __init__(
        self,
        refinery: Optional[RefineryAgent] = None,
        roi_optimizer: Optional[ROIOptimizer] = None,
    ):
        """
        Initialize the bridge.

        Args:
            refinery: R-gent instance (created if not provided)
            roi_optimizer: ROI checker (created if not provided)
        """
        self.refinery = refinery or RefineryAgent()
        self.roi_optimizer = roi_optimizer or ROIOptimizer()

    def extract_signature_from_source(
        self,
        source_code: str,
        agent_name: str,
        intent_text: str = "",
    ) -> Signature:
        """
        Extract a Signature from F-gent prototype source code.

        Heuristically parses the source to identify:
        - Input type from first function argument
        - Output type from return annotation
        - Instructions from docstring or intent

        Args:
            source_code: Python source code from F-gent
            agent_name: Name of the agent
            intent_text: Original intent (becomes instructions)

        Returns:
            Signature extracted from source
        """
        import ast
        import re

        # Parse source code
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Fall back to basic signature
            return Signature.simple(
                input_name="input",
                input_type=str,
                output_name="output",
                output_type=str,
                instructions=intent_text or f"Execute {agent_name}",
            )

        # Find main function (async def invoke or similar)
        input_type = str
        output_type = str
        docstring = ""

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) or isinstance(
                node, ast.FunctionDef
            ):
                if node.name in ("invoke", "run", "execute", "__call__"):
                    # Extract docstring
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    ):
                        docstring = node.body[0].value.value

                    # Extract return annotation
                    if node.returns:
                        if isinstance(node.returns, ast.Name):
                            output_type = self._type_from_name(node.returns.id)
                        elif isinstance(node.returns, ast.Subscript):
                            # e.g., Result[str, Error]
                            if isinstance(node.returns.value, ast.Name):
                                if node.returns.value.id == "Result":
                                    # Get first type arg
                                    if isinstance(node.returns.slice, ast.Tuple):
                                        first_elt = node.returns.slice.elts[0]
                                        if isinstance(first_elt, ast.Name):
                                            output_type = self._type_from_name(
                                                first_elt.id
                                            )

                    # Extract first argument type
                    if node.args.args:
                        first_arg = node.args.args[0]
                        if first_arg.annotation and isinstance(
                            first_arg.annotation, ast.Name
                        ):
                            input_type = self._type_from_name(first_arg.annotation.id)

                    break

        # Construct signature
        instructions = intent_text or docstring or f"Execute {agent_name}"
        return Signature.simple(
            input_name="input",
            input_type=input_type,
            output_name="output",
            output_type=output_type,
            instructions=instructions,
        )

    def _type_from_name(self, name: str) -> type:
        """Convert type name string to Python type."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "Any": object,
        }
        return type_map.get(name, str)

    async def generate_synthetic_examples(
        self,
        signature: Signature,
        num_examples: int = 10,
        llm_func: Optional[Callable[[str], str]] = None,
    ) -> list[Example]:
        """
        Generate synthetic training examples for a signature.

        If llm_func is provided, uses LLM to generate realistic examples.
        Otherwise, creates simple placeholder examples.

        Args:
            signature: The signature to generate examples for
            num_examples: Number of examples to generate
            llm_func: Optional LLM function for generation

        Returns:
            List of synthetic Examples
        """
        examples = []

        if llm_func:
            # Use LLM to generate examples
            prompt = f"""Generate {num_examples} diverse input-output examples for this task:

Task: {signature.instructions}
Input fields: {signature.input_names}
Output fields: {signature.output_names}

Format each example as:
Input: <input value>
Output: <expected output>

Generate realistic, diverse examples that cover edge cases."""

            try:
                response = await llm_func(prompt)
                # Parse response into examples
                examples = self._parse_llm_examples(response, signature)
            except Exception:
                pass  # Fall back to synthetic

        # Fill remaining with synthetic examples
        while len(examples) < num_examples:
            example = Example.simple(
                input_value=f"Example input {len(examples) + 1}",
                output_value=f"Example output {len(examples) + 1}",
            )
            examples.append(example)

        return examples[:num_examples]

    def _parse_llm_examples(self, response: str, signature: Signature) -> list[Example]:
        """Parse LLM response into Example objects."""
        examples = []
        import re

        # Simple pattern matching for Input:/Output: format
        pattern = r"Input:\s*(.*?)\nOutput:\s*(.*?)(?=\nInput:|$)"
        matches = re.findall(pattern, response, re.DOTALL)

        for input_val, output_val in matches:
            examples.append(
                Example.simple(
                    input_value=input_val.strip(),
                    output_value=output_val.strip(),
                )
            )

        return examples

    async def refine(
        self,
        request: PrototypeRefinementRequest,
        metric: Optional[Callable[[Any, Any], float]] = None,
        llm_func: Optional[Callable[[str], str]] = None,
    ) -> PrototypeRefinementResult:
        """
        Execute the F → R refinement pipeline.

        Steps:
        1. Extract signature from prototype
        2. Check ROI (if enabled)
        3. Generate examples (if needed)
        4. Run optimization
        5. Return result

        Args:
            request: Refinement request with prototype and parameters
            metric: Metric function (defaults to exact match)
            llm_func: Optional LLM function for example generation

        Returns:
            PrototypeRefinementResult with optimized signature
        """
        result = PrototypeRefinementResult(
            phase=RefinePhase.PENDING,
            success=False,
            request=request,
        )

        # Step 1: Extract signature
        result.phase = RefinePhase.EXTRACTING
        try:
            signature = self.extract_signature_from_source(
                request.source_code,
                request.agent_name,
                request.intent_text,
            )
            result.original_signature = signature
        except Exception as e:
            result.phase = RefinePhase.FAILED
            result.error_message = f"Failed to extract signature: {e}"
            return result

        # Step 2: Check ROI (if enabled)
        if request.check_roi:
            num_examples = len(request.examples) or request.num_synthetic_examples
            decision = self.roi_optimizer.should_optimize(
                usage_per_month=request.estimated_usage_per_month,
                current_performance=0.5,  # Assume 50% baseline
                strategy=request.strategy,
                num_examples=num_examples,
                value_per_call=request.value_per_call_usd,
            )
            result.roi_estimate = decision.roi_estimate
            result.roi_decision = decision

            if not decision.proceed:
                result.phase = RefinePhase.SKIPPED
                result.success = True  # Intentionally skipped is still success
                result.optimized_signature = signature  # Return unchanged
                return result

        # Step 3: Generate examples (if needed)
        result.phase = RefinePhase.GENERATING_EXAMPLES
        examples = request.examples
        if not examples and request.generate_examples:
            examples = await self.generate_synthetic_examples(
                signature=signature,
                num_examples=request.num_synthetic_examples,
                llm_func=llm_func,
            )

        # Step 4: Run optimization
        result.phase = RefinePhase.OPTIMIZING

        # Default metric: exact match
        if metric is None:

            def exact_match(pred: Any, label: Any) -> float:
                return 1.0 if pred == label else 0.0

            metric = exact_match

        try:
            # Use the refinery's refine method
            self.refinery.strategy = request.strategy
            trace = await self.refinery.refine(
                signature=signature,
                examples=examples,
                metric=metric,
                max_iterations=request.max_iterations,
                budget_usd=request.budget_usd,
                check_roi=False,  # ROI already checked above
            )
            result.optimization_trace = trace

            # Build optimized signature with updated demos
            if trace.iterations:
                # Get best prompt from trace
                best_iteration = max(trace.iterations, key=lambda i: i.score)
                optimized_signature = Signature(
                    input_fields=signature.input_fields,
                    output_fields=signature.output_fields,
                    instructions=best_iteration.prompt_text or signature.instructions,
                    demos=signature.demos,  # Could be updated by teleprompter
                    version=f"{signature.version}-optimized",
                    name=signature.name,
                    description=signature.description,
                )
                result.optimized_signature = optimized_signature
            else:
                result.optimized_signature = signature

            result.phase = RefinePhase.COMPLETED
            result.success = True

        except Exception as e:
            result.phase = RefinePhase.FAILED
            result.error_message = f"Optimization failed: {e}"

        return result


# =============================================================================
# T-gent → R-gent Integration: Loss Signal Adapter
# =============================================================================


@dataclass
class MetricSignal:
    """
    A signal from T-gent metrics to R-gent optimization.

    Converts tool execution metrics into optimization gradients.
    """

    # Core metric
    score: float  # 0.0 to 1.0

    # Context
    timestamp: datetime = field(default_factory=datetime.now)
    output_hash: str = ""

    # Source identification
    tool_name: str = ""
    metric_name: str = ""

    # For batching
    batch_id: Optional[str] = None


@dataclass
class TextualLossSignal:
    """
    A textual loss signal for R-gent optimization.

    Combines T-gent metrics with natural language feedback
    to create a gradient for prompt improvement.
    """

    # Numeric signal
    score: float

    # Textual gradient
    feedback: str

    # Source
    prediction: Any
    expected: Any

    # Metadata
    source_example: Optional[Example] = None
    metric_name: str = "accuracy"


class TGentLossAdapter:
    """
    Adapter that converts T-gent Tool outputs into R-gent loss signals.

    Implements the T → R pipeline from spec/r-gents/README.md:
    - Wraps T-gent metrics as optimization signals
    - Converts failures into textual gradients
    - Batches signals for efficient optimization

    Category Theory:
        This is a functor T-Metric → R-Gradient that lifts
        numeric metrics into the tangent space of prompts.
    """

    def __init__(
        self,
        feedback_generator: Optional[Callable[[Any, Any], str]] = None,
    ):
        """
        Initialize the adapter.

        Args:
            feedback_generator: Function to generate textual feedback
                from (prediction, expected) pairs
        """
        self.feedback_generator = feedback_generator or self._default_feedback
        self._signal_batch: list[TextualLossSignal] = []
        self._batch_id: str = ""

    def _default_feedback(self, prediction: Any, expected: Any) -> str:
        """Default feedback generator."""
        return f"Expected: {expected}, Got: {prediction}"

    def compute_loss_signal(
        self,
        prediction: Any,
        expected: Any,
        metric: Callable[[Any, Any], float],
        metric_name: str = "accuracy",
    ) -> TextualLossSignal:
        """
        Compute a loss signal from prediction vs expected.

        Args:
            prediction: Model output
            expected: Ground truth
            metric: Metric function (higher is better)
            metric_name: Name for logging

        Returns:
            TextualLossSignal with score and feedback
        """
        score = metric(prediction, expected)
        feedback = ""

        # Generate feedback for failures
        if score < 1.0:
            feedback = self.feedback_generator(prediction, expected)

        return TextualLossSignal(
            score=score,
            feedback=feedback,
            prediction=prediction,
            expected=expected,
            metric_name=metric_name,
        )

    async def compute_loss_signal_with_llm(
        self,
        prediction: Any,
        expected: Any,
        metric: Callable[[Any, Any], float],
        llm_func: Callable[[str], str],
        metric_name: str = "accuracy",
    ) -> TextualLossSignal:
        """
        Compute loss signal with LLM-generated feedback.

        Uses an LLM to generate rich textual critiques for failures.

        Args:
            prediction: Model output
            expected: Ground truth
            metric: Metric function
            llm_func: LLM for generating feedback
            metric_name: Name for logging

        Returns:
            TextualLossSignal with LLM-generated feedback
        """
        score = metric(prediction, expected)
        feedback = ""

        if score < 1.0:
            # Use LLM to generate detailed critique
            prompt = f"""Analyze why this output is incorrect:

Expected: {expected}
Got: {prediction}

Provide specific, actionable feedback on what went wrong and how to fix it.
Focus on the key differences and what the model should have done differently."""

            try:
                feedback = await llm_func(prompt)
            except Exception:
                feedback = self._default_feedback(prediction, expected)

        return TextualLossSignal(
            score=score,
            feedback=feedback,
            prediction=prediction,
            expected=expected,
            metric_name=metric_name,
        )

    def start_batch(self) -> str:
        """Start a new signal batch. Returns batch ID."""
        self._batch_id = str(uuid.uuid4())[:8]
        self._signal_batch = []
        return self._batch_id

    def add_to_batch(self, signal: TextualLossSignal) -> None:
        """Add a signal to the current batch."""
        self._signal_batch.append(signal)

    def complete_batch(self) -> list[TextualLossSignal]:
        """Complete batch and return all signals."""
        batch = self._signal_batch
        self._signal_batch = []
        return batch

    def aggregate_batch_feedback(self) -> str:
        """
        Aggregate all batch feedback into a single textual gradient.

        This is the "batch normalization" step from TextGrad.
        """
        if not self._signal_batch:
            return ""

        # Filter to failures only
        failures = [s for s in self._signal_batch if s.score < 1.0]
        if not failures:
            return ""

        # Aggregate feedback
        feedback_lines = []
        for i, signal in enumerate(failures, 1):
            feedback_lines.append(f"{i}. {signal.feedback}")

        return "\n".join(feedback_lines)

    @property
    def batch_score(self) -> float:
        """Average score of current batch."""
        if not self._signal_batch:
            return 0.0
        return sum(s.score for s in self._signal_batch) / len(self._signal_batch)


# =============================================================================
# B-gent → R-gent Integration: Budget Grant Protocol
# =============================================================================


class BudgetDenied(Exception):
    """Exception raised when B-gent denies optimization budget."""

    def __init__(self, reason: str, recommendation: str = ""):
        self.reason = reason
        self.recommendation = recommendation
        super().__init__(f"Budget denied: {reason}")


@dataclass
class BudgetGrant:
    """
    A budget grant from B-gent for R-gent optimization.

    Implements the Budget Grant Protocol from spec/r-gents/README.md.
    """

    # Grant status
    approved: bool
    grant_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Amount granted (if approved)
    amount_usd: float = 0.0

    # Constraints
    max_iterations: int = 10
    max_llm_calls: int = 100

    # Strategy recommendation
    recommended_strategy: Optional[TeleprompterStrategy] = None

    # Rejection info (if not approved)
    reason: str = ""
    recommendation: str = ""


@dataclass
class BudgetSpendReport:
    """Report of actual spend after optimization."""

    grant_id: str
    actual_cost_usd: float
    iterations_used: int
    llm_calls_made: int

    # Outcome
    baseline_score: float
    final_score: float
    improvement: float

    # Status
    completed: bool = True
    error: str = ""


class BGentBudgetProtocol:
    """
    Budget grant protocol between B-gent and R-gent.

    Implements economic constraints on optimization:
    1. Request budget before optimization
    2. Run within granted limits
    3. Report actual spend and outcomes

    Category Theory:
        This is a comonad that extracts resources from the
        B-gent economy to fund R-gent optimization.
    """

    def __init__(
        self,
        default_budget_usd: float = 10.0,
        min_roi_threshold: float = 2.0,
    ):
        """
        Initialize the protocol.

        Args:
            default_budget_usd: Default budget if not specified
            min_roi_threshold: Minimum ROI required for approval
        """
        self.default_budget = default_budget_usd
        self.min_roi_threshold = min_roi_threshold
        self._grants: dict[str, BudgetGrant] = {}
        self._spend_reports: dict[str, BudgetSpendReport] = {}

    def request_grant(
        self,
        purpose: str,
        estimated_cost: float,
        expected_roi: float,
        strategy: Optional[TeleprompterStrategy] = None,
    ) -> BudgetGrant:
        """
        Request a budget grant for optimization.

        Args:
            purpose: Description of optimization goal
            estimated_cost: Estimated cost in USD
            expected_roi: Expected return on investment
            strategy: Requested optimization strategy

        Returns:
            BudgetGrant (approved or denied)
        """
        # Check ROI threshold
        if expected_roi < self.min_roi_threshold:
            grant = BudgetGrant(
                approved=False,
                reason=f"ROI ({expected_roi:.2f}) below threshold ({self.min_roi_threshold})",
                recommendation="Use zero-shot or BootstrapFewShot (low cost)",
                recommended_strategy=TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
            )
            self._grants[grant.grant_id] = grant
            return grant

        # Check budget
        granted_amount = min(estimated_cost, self.default_budget)

        # Determine max iterations based on strategy
        if strategy == TeleprompterStrategy.TEXTGRAD:
            max_iterations = 10
            max_llm_calls = 100
        elif strategy == TeleprompterStrategy.MIPRO_V2:
            max_iterations = 50
            max_llm_calls = 200
        elif strategy == TeleprompterStrategy.OPRO:
            max_iterations = 20
            max_llm_calls = 50
        else:
            max_iterations = 10
            max_llm_calls = 30

        grant = BudgetGrant(
            approved=True,
            amount_usd=granted_amount,
            max_iterations=max_iterations,
            max_llm_calls=max_llm_calls,
            recommended_strategy=strategy,
        )

        self._grants[grant.grant_id] = grant
        return grant

    def report_spend(self, report: BudgetSpendReport) -> None:
        """
        Report actual spend after optimization.

        Args:
            report: Spend report with outcomes
        """
        if report.grant_id not in self._grants:
            raise ValueError(f"Unknown grant ID: {report.grant_id}")

        self._spend_reports[report.grant_id] = report

    def get_grant(self, grant_id: str) -> Optional[BudgetGrant]:
        """Get grant by ID."""
        return self._grants.get(grant_id)

    def get_spend_report(self, grant_id: str) -> Optional[BudgetSpendReport]:
        """Get spend report by grant ID."""
        return self._spend_reports.get(grant_id)

    @property
    def total_granted(self) -> float:
        """Total budget granted across all grants."""
        return sum(g.amount_usd for g in self._grants.values() if g.approved)

    @property
    def total_spent(self) -> float:
        """Total budget actually spent."""
        return sum(r.actual_cost_usd for r in self._spend_reports.values())


class BudgetConstrainedRefinery:
    """
    R-gent Refinery with B-gent budget constraints.

    Wraps RefineryAgent with budget protocol:
    1. Request grant before optimizing
    2. Enforce iteration/call limits
    3. Report spend after completion

    Usage:
        refinery = BudgetConstrainedRefinery(budget_protocol)
        result = await refinery.refine_with_budget(signature, examples, metric)
    """

    def __init__(
        self,
        budget_protocol: BGentBudgetProtocol,
        refinery: Optional[RefineryAgent] = None,
    ):
        """
        Initialize the constrained refinery.

        Args:
            budget_protocol: B-gent budget protocol
            refinery: R-gent instance (created if not provided)
        """
        self.budget_protocol = budget_protocol
        self.refinery = refinery or RefineryAgent()

    async def refine_with_budget(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        strategy: TeleprompterStrategy = TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
        estimated_cost: float = 5.0,
        expected_roi: float = 3.0,
    ) -> tuple[OptimizationTrace, BudgetGrant]:
        """
        Run optimization with budget constraints.

        Args:
            signature: Signature to optimize
            examples: Training examples
            metric: Metric function
            strategy: Optimization strategy
            estimated_cost: Estimated cost
            expected_roi: Expected ROI

        Returns:
            Tuple of (optimization trace, budget grant)

        Raises:
            BudgetDenied: If budget request is denied
        """
        # Step 1: Request budget
        grant = self.budget_protocol.request_grant(
            purpose=f"Optimize {signature.name or 'signature'}",
            estimated_cost=estimated_cost,
            expected_roi=expected_roi,
            strategy=strategy,
        )

        if not grant.approved:
            raise BudgetDenied(grant.reason, grant.recommendation)

        # Step 2: Run optimization within limits
        self.refinery.strategy = strategy
        trace = await self.refinery.refine(
            signature=signature,
            examples=examples,
            metric=metric,
            max_iterations=grant.max_iterations,
            budget_usd=grant.amount_usd,
            check_roi=False,  # ROI already checked via grant
        )

        # Step 3: Report spend
        report = BudgetSpendReport(
            grant_id=grant.grant_id,
            actual_cost_usd=trace.cost_usd,
            iterations_used=len(trace.iterations),
            llm_calls_made=trace.total_llm_calls,
            baseline_score=trace.baseline_score or 0.0,
            final_score=trace.final_score or 0.0,
            improvement=trace.improvement or 0.0,
        )
        self.budget_protocol.report_spend(report)

        return trace, grant


# =============================================================================
# L-gent → R-gent Integration: Optimization Metadata Indexing
# =============================================================================


@dataclass
class OptimizationCatalogEntry:
    """
    Extended CatalogEntry with optimization metadata.

    Implements the optimization metadata fields from spec/r-gents/README.md.
    """

    # Core entry fields (from L-gent CatalogEntry)
    entry_id: str
    name: str
    version: str
    description: str

    # Optimization metadata (added by R-gent)
    optimization_method: Optional[str] = None
    optimization_score: Optional[float] = None
    optimization_baseline: Optional[float] = None
    optimization_iterations: Optional[int] = None
    optimization_cost_usd: Optional[float] = None
    optimization_trace_id: Optional[str] = None

    # Signature info
    signature_hash: Optional[str] = None
    demos_count: int = 0

    @property
    def improvement_percentage(self) -> Optional[float]:
        """Relative improvement as percentage."""
        if (
            self.optimization_score is not None
            and self.optimization_baseline is not None
            and self.optimization_baseline != 0
        ):
            return (
                (self.optimization_score - self.optimization_baseline)
                / abs(self.optimization_baseline)
            ) * 100
        return None

    @property
    def is_optimized(self) -> bool:
        """Whether this entry has been optimized."""
        return self.optimization_method is not None


class LGentOptimizationIndex:
    """
    L-gent integration for indexing optimization metadata.

    Extends the L-gent catalog with optimization-aware queries:
    - Find well-optimized agents
    - Find candidates for optimization
    - Track optimization history

    Category Theory:
        This is a functor R-Trace → L-Index that maps
        optimization results into the discovery lattice.
    """

    def __init__(self):
        """Initialize the optimization index."""
        self._entries: dict[str, OptimizationCatalogEntry] = {}
        self._trace_storage: dict[str, OptimizationTrace] = {}

    def index_optimization_result(
        self,
        entry_id: str,
        name: str,
        version: str,
        description: str,
        trace: OptimizationTrace,
        signature: Optional[Signature] = None,
    ) -> OptimizationCatalogEntry:
        """
        Index an optimization result.

        Args:
            entry_id: Unique entry identifier
            name: Agent name
            version: Agent version
            description: Agent description
            trace: Optimization trace from R-gent
            signature: Optional optimized signature

        Returns:
            The indexed OptimizationCatalogEntry
        """
        # Generate trace ID
        trace_id = hashlib.sha256(
            f"{entry_id}:{trace.method}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Store trace
        self._trace_storage[trace_id] = trace

        # Create entry
        entry = OptimizationCatalogEntry(
            entry_id=entry_id,
            name=name,
            version=version,
            description=description,
            optimization_method=trace.method,
            optimization_score=trace.final_score,
            optimization_baseline=trace.baseline_score,
            optimization_iterations=len(trace.iterations),
            optimization_cost_usd=trace.cost_usd,
            optimization_trace_id=trace_id,
            signature_hash=hashlib.sha256(
                (signature.instructions if signature else "").encode()
            ).hexdigest()[:8],
            demos_count=len(signature.demos) if signature else 0,
        )

        self._entries[entry_id] = entry
        return entry

    def find_optimized(
        self,
        min_score: float = 0.0,
        method: Optional[str] = None,
        min_improvement: Optional[float] = None,
    ) -> list[OptimizationCatalogEntry]:
        """
        Find well-optimized agents.

        Args:
            min_score: Minimum optimization score
            method: Filter by optimization method
            min_improvement: Minimum improvement percentage

        Returns:
            List of matching entries
        """
        results = []

        for entry in self._entries.values():
            if not entry.is_optimized:
                continue

            if entry.optimization_score is not None:
                if entry.optimization_score < min_score:
                    continue

            if method and entry.optimization_method != method:
                continue

            if min_improvement is not None:
                if (
                    entry.improvement_percentage is None
                    or entry.improvement_percentage < min_improvement
                ):
                    continue

            results.append(entry)

        # Sort by score descending
        results.sort(
            key=lambda e: e.optimization_score or 0,
            reverse=True,
        )

        return results

    def find_optimization_candidates(
        self,
        min_usage_count: int = 100,
        max_success_rate: float = 0.7,
    ) -> list[OptimizationCatalogEntry]:
        """
        Find agents that could benefit from optimization.

        Args:
            min_usage_count: Minimum usage to be worth optimizing
            max_success_rate: Maximum current success (lower = more room to improve)

        Returns:
            List of candidate entries
        """
        # For this basic implementation, return unoptimized entries
        # In a full implementation, this would query L-gent usage stats
        return [e for e in self._entries.values() if not e.is_optimized]

    def get_trace(self, trace_id: str) -> Optional[OptimizationTrace]:
        """Get stored optimization trace by ID."""
        return self._trace_storage.get(trace_id)

    def get_entry(self, entry_id: str) -> Optional[OptimizationCatalogEntry]:
        """Get entry by ID."""
        return self._entries.get(entry_id)


# =============================================================================
# Unified Integration: The Complete Pipeline
# =============================================================================


@dataclass
class RGentIntegrationConfig:
    """Configuration for R-gent integrations."""

    # F-gent integration
    enable_f_gent: bool = True
    generate_synthetic_examples: bool = True
    num_synthetic_examples: int = 10

    # T-gent integration
    enable_t_gent: bool = True
    use_llm_feedback: bool = False

    # B-gent integration
    enable_b_gent: bool = True
    default_budget_usd: float = 10.0
    min_roi_threshold: float = 2.0

    # L-gent integration
    enable_l_gent: bool = True
    auto_index_results: bool = True


class RGentIntegrationHub:
    """
    Central hub for all R-gent integrations.

    Provides a unified interface for:
    - F-gent → R-gent (prototype refinement)
    - T-gent → R-gent (loss signals)
    - B-gent → R-gent (budget constraints)
    - L-gent → R-gent (indexing)

    Usage:
        hub = RGentIntegrationHub(config)
        result = await hub.refine_prototype(request)
    """

    def __init__(self, config: Optional[RGentIntegrationConfig] = None):
        """Initialize the integration hub."""
        self.config = config or RGentIntegrationConfig()

        # Core refinery
        self.refinery = RefineryAgent()

        # F-gent bridge
        if self.config.enable_f_gent:
            self.f_gent_bridge = FGentRefineryBridge(refinery=self.refinery)
        else:
            self.f_gent_bridge = None

        # T-gent adapter
        if self.config.enable_t_gent:
            self.t_gent_adapter = TGentLossAdapter()
        else:
            self.t_gent_adapter = None

        # B-gent protocol
        if self.config.enable_b_gent:
            self.budget_protocol = BGentBudgetProtocol(
                default_budget_usd=self.config.default_budget_usd,
                min_roi_threshold=self.config.min_roi_threshold,
            )
            self.budget_refinery = BudgetConstrainedRefinery(
                budget_protocol=self.budget_protocol,
                refinery=self.refinery,
            )
        else:
            self.budget_protocol = None
            self.budget_refinery = None

        # L-gent index
        if self.config.enable_l_gent:
            self.optimization_index = LGentOptimizationIndex()
        else:
            self.optimization_index = None

    async def refine_prototype(
        self,
        request: PrototypeRefinementRequest,
        metric: Optional[Callable[[Any, Any], float]] = None,
        llm_func: Optional[Callable[[str], str]] = None,
    ) -> PrototypeRefinementResult:
        """
        Full pipeline: F-gent → R-gent with budget and indexing.

        Args:
            request: Prototype refinement request
            metric: Metric function
            llm_func: LLM function for feedback/examples

        Returns:
            PrototypeRefinementResult
        """
        if not self.f_gent_bridge:
            raise RuntimeError("F-gent integration not enabled")

        result = await self.f_gent_bridge.refine(
            request=request,
            metric=metric,
            llm_func=llm_func,
        )

        # Index result (if enabled and successful)
        if (
            self.config.auto_index_results
            and self.optimization_index
            and result.success
            and result.optimization_trace
        ):
            self.optimization_index.index_optimization_result(
                entry_id=f"{request.agent_name}:{result.optimization_trace.method}",
                name=request.agent_name,
                version="1.0.0",
                description=request.intent_text or f"Optimized {request.agent_name}",
                trace=result.optimization_trace,
                signature=result.optimized_signature,
            )

        return result

    async def refine_with_budget(
        self,
        signature: Signature,
        examples: list[Example],
        metric: Callable[[Any, Any], float],
        strategy: TeleprompterStrategy = TeleprompterStrategy.BOOTSTRAP_FEWSHOT,
        estimated_cost: float = 5.0,
        expected_roi: float = 3.0,
    ) -> tuple[OptimizationTrace, BudgetGrant]:
        """
        Optimize with B-gent budget constraints.

        Args:
            signature: Signature to optimize
            examples: Training examples
            metric: Metric function
            strategy: Optimization strategy
            estimated_cost: Estimated cost
            expected_roi: Expected ROI

        Returns:
            Tuple of (trace, grant)

        Raises:
            BudgetDenied: If budget not approved
        """
        if not self.budget_refinery:
            raise RuntimeError("B-gent integration not enabled")

        return await self.budget_refinery.refine_with_budget(
            signature=signature,
            examples=examples,
            metric=metric,
            strategy=strategy,
            estimated_cost=estimated_cost,
            expected_roi=expected_roi,
        )

    def compute_loss_signal(
        self,
        prediction: Any,
        expected: Any,
        metric: Callable[[Any, Any], float],
    ) -> TextualLossSignal:
        """
        Compute T-gent loss signal.

        Args:
            prediction: Model output
            expected: Ground truth
            metric: Metric function

        Returns:
            TextualLossSignal
        """
        if not self.t_gent_adapter:
            raise RuntimeError("T-gent integration not enabled")

        return self.t_gent_adapter.compute_loss_signal(
            prediction=prediction,
            expected=expected,
            metric=metric,
        )

    def find_optimized_agents(
        self,
        min_score: float = 0.0,
        method: Optional[str] = None,
    ) -> list[OptimizationCatalogEntry]:
        """
        Query L-gent index for optimized agents.

        Args:
            min_score: Minimum optimization score
            method: Filter by method

        Returns:
            List of matching entries
        """
        if not self.optimization_index:
            raise RuntimeError("L-gent integration not enabled")

        return self.optimization_index.find_optimized(
            min_score=min_score,
            method=method,
        )
