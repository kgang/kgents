"""
Psi-gent v3.0 Integration Adapters.

Clean integration with L/B/D/N/G-gents.
Graceful degradation when integrations are unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Any
from datetime import datetime

from .types import (
    Problem,
    Metaphor,
    Solution,
    Distortion,
    Outcome,
)
from .engine import MetaphorEngine


# =============================================================================
# L-gent Integration (Embeddings)
# =============================================================================


class LEmbedder(Protocol):
    """Protocol for L-gent embedding interface."""

    def embed(self, text: str) -> tuple[float, ...]:
        """Embed a single text."""
        ...

    def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Embed multiple texts efficiently."""
        ...


def embed_problem(problem: Problem, l_gent: LEmbedder) -> Problem:
    """Add embedding to problem using L-gent."""
    if problem.embedding:
        return problem

    embedding = l_gent.embed(problem.description)
    return problem.with_embedding(tuple(embedding))


def embed_metaphor(metaphor: Metaphor, l_gent: LEmbedder) -> Metaphor:
    """Add embedding to metaphor using L-gent."""
    if metaphor.embedding:
        return metaphor

    # Embed description + operation names
    text = (
        f"{metaphor.description} Operations: {[op.name for op in metaphor.operations]}"
    )
    embedding = l_gent.embed(text)
    return metaphor.with_embedding(tuple(embedding))


def embed_corpus(corpus: list[Metaphor], l_gent: LEmbedder) -> list[Metaphor]:
    """Batch embed entire corpus."""
    texts = [
        f"{m.description} Operations: {[op.name for op in m.operations]}"
        for m in corpus
    ]
    embeddings = l_gent.embed_batch(texts)

    return [m.with_embedding(tuple(e)) for m, e in zip(corpus, embeddings)]


def cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute cosine similarity between two embeddings."""
    if len(a) != len(b) or not a:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def retrieve_by_embedding(
    problem: Problem,
    corpus: list[Metaphor],
    l_gent: LEmbedder,
) -> list[tuple[Metaphor, float]]:
    """Retrieve metaphors by embedding similarity."""
    if not problem.embedding:
        problem = embed_problem(problem, l_gent)

    scored: list[tuple[Metaphor, float]] = []
    for metaphor in corpus:
        if not metaphor.embedding:
            metaphor = embed_metaphor(metaphor, l_gent)

        similarity = cosine_similarity(problem.embedding, metaphor.embedding)  # type: ignore
        scored.append((metaphor, similarity))

    return sorted(scored, key=lambda x: x[1], reverse=True)


# =============================================================================
# B-gent Integration (Token Economics)
# =============================================================================


class BudgetManager(Protocol):
    """Protocol for B-gent budget interface."""

    def authorize(self, operation: str, estimated_tokens: int) -> Any:
        """Request authorization for token usage."""
        ...

    def record_cost(self, category: str, tokens: int, metadata: dict[str, Any]) -> None:
        """Record actual token usage."""
        ...


@dataclass
class TokenReceipt:
    """Receipt for token usage in a solve attempt."""

    retrieve_tokens: int = 0
    project_tokens: int = 0
    challenge_tokens: int = 0
    solve_tokens: int = 0
    translate_tokens: int = 0
    verify_tokens: int = 0

    @property
    def total(self) -> int:
        return (
            self.retrieve_tokens
            + self.project_tokens
            + self.challenge_tokens
            + self.solve_tokens
            + self.translate_tokens
            + self.verify_tokens
        )


@dataclass(frozen=True)
class PsiBudget:
    """Token budget for a solve attempt."""

    retrieve_budget: int = 500
    project_budget: int = 1000
    challenge_budget: int = 800
    solve_budget: int = 2000
    translate_budget: int = 800
    verify_budget: int = 600
    total_budget: int = 6000


class BudgetExhausted(Exception):
    """Raised when token budget is exhausted."""

    pass


def solve_with_budget(
    problem: Problem,
    engine: MetaphorEngine,
    b_gent: BudgetManager,
    budget: PsiBudget | None = None,
) -> tuple[Solution | None, TokenReceipt]:
    """Execute solve with B-gent budget control."""
    budget = budget or PsiBudget()
    receipt = TokenReceipt()

    # Authorize budget
    authorization = b_gent.authorize("psi_solve", budget.total_budget)

    if not authorization:
        return None, receipt

    try:
        solution = engine.solve_problem(problem)

        # Record costs (in production, would track actual LLM calls)
        b_gent.record_cost(
            "psi_solve",
            receipt.total,
            {"problem_id": problem.id, "success": solution.success},
        )

        return solution, receipt

    except BudgetExhausted:
        return None, receipt


# =============================================================================
# D-gent Integration (State Persistence)
# =============================================================================


class DataAgent(Protocol):
    """Protocol for D-gent data interface."""

    def get(self, key: str) -> Any | None:
        """Get value by key."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Set value by key."""
        ...


def serialize_model(model: Any) -> dict[str, Any]:
    """Serialize a learning model to dict."""
    if hasattr(model, "alphas") and hasattr(model, "betas"):
        # ThompsonSamplingModel
        return {
            "type": "thompson",
            "alphas": {f"{k[0]}:{k[1]}": v for k, v in model.alphas.items()},
            "betas": {f"{k[0]}:{k[1]}": v for k, v in model.betas.items()},
        }
    elif hasattr(model, "counts"):
        # FrequencyModel
        return {
            "type": "frequency",
            "counts": {f"{k[0]}:{k[1]}": v for k, v in model.counts.items()},
        }
    return {}


def deserialize_model(data: dict[str, Any], model_type: type) -> Any:
    """Deserialize a learning model from dict."""
    model = model_type()

    if data.get("type") == "thompson":
        for key, val in data.get("alphas", {}).items():
            parts = key.split(":", 1)
            if len(parts) == 2:
                model.alphas[(parts[0], parts[1])] = val
        for key, val in data.get("betas", {}).items():
            parts = key.split(":", 1)
            if len(parts) == 2:
                model.betas[(parts[0], parts[1])] = val

    elif data.get("type") == "frequency":
        for key, val in data.get("counts", {}).items():
            parts = key.split(":", 1)
            if len(parts) == 2:
                model.counts[(parts[0], parts[1])] = tuple(val)

    return model


class PersistentEngine:
    """MetaphorEngine with D-gent persistence."""

    def __init__(self, d_gent: DataAgent, engine: MetaphorEngine | None = None):
        self.d_gent = d_gent
        self.engine = engine or MetaphorEngine()
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted state."""
        from .learning import ThompsonSamplingModel, AbstractionModel

        # Learning model
        learning_state = self.d_gent.get("psi/learning_model")
        if learning_state:
            self.engine.retrieval_model = deserialize_model(
                learning_state, ThompsonSamplingModel
            )

        # Abstraction model
        abstraction_state = self.d_gent.get("psi/abstraction_model")
        if abstraction_state and isinstance(abstraction_state, dict):
            model = AbstractionModel()
            for key, val in abstraction_state.items():
                parts = key.split(":", 1)
                if len(parts) == 2:
                    model.history[(int(parts[0]), int(parts[1]))] = list(val)
            self.engine.abstraction_model = model

    def _save_state(self) -> None:
        """Save state to D-gent."""
        self.d_gent.set(
            "psi/learning_model", serialize_model(self.engine.retrieval_model)
        )

        # Save abstraction model
        abstraction_data = {
            f"{k[0]}:{k[1]}": v
            for k, v in self.engine.abstraction_model.history.items()
        }
        self.d_gent.set("psi/abstraction_model", abstraction_data)

    def solve_problem(self, problem: Problem) -> Solution:
        """Solve with automatic state persistence."""
        solution = self.engine.solve_problem(problem)
        self._save_state()
        return solution


# =============================================================================
# N-gent Integration (Tracing)
# =============================================================================


class Historian(Protocol):
    """Protocol for N-gent tracing interface."""

    def begin_trace(self, action: str, input_obj: dict[str, Any]) -> Any:
        """Begin a trace context."""
        ...

    def end_trace(self, ctx: Any, outputs: dict[str, Any]) -> None:
        """End a trace context."""
        ...

    def abort_trace(self, ctx: Any, error: str) -> None:
        """Abort a trace due to error."""
        ...


@dataclass
class PsiTrace:
    """Complete trace of a solve attempt."""

    trace_id: str
    problem_id: str
    timestamp: datetime
    stages: dict[str, dict[str, Any]] = field(default_factory=dict)
    outcome: Outcome | None = None
    distortion: Distortion | None = None
    backtracks: list[str] = field(default_factory=list)


def solve_with_tracing(
    problem: Problem,
    engine: MetaphorEngine,
    n_gent: Historian,
) -> tuple[Solution, PsiTrace]:
    """Solve with full N-gent tracing."""
    from uuid import uuid4

    trace = PsiTrace(
        trace_id=str(uuid4()),
        problem_id=problem.id,
        timestamp=datetime.now(),
    )

    ctx = n_gent.begin_trace("psi_solve", {"problem_id": problem.id})

    # Install trace callback
    def on_stage(stage: str, data: dict[str, Any]) -> None:
        trace.stages[stage] = data

    old_callback = engine.on_stage_complete
    engine.on_stage_complete = on_stage

    try:
        solution = engine.solve_problem(problem)
        trace.outcome = Outcome.SUCCESS if solution.success else Outcome.VERIFY_FAILED
        trace.distortion = solution.distortion

        n_gent.end_trace(ctx, {"trace_id": trace.trace_id, "success": solution.success})
        return solution, trace

    except Exception as e:
        n_gent.abort_trace(ctx, str(e))
        raise

    finally:
        engine.on_stage_complete = old_callback


# =============================================================================
# G-gent Integration (Grammar/Prompts)
# =============================================================================


class GrammarEngine(Protocol):
    """Protocol for G-gent grammar interface."""

    def render(self, template: str, **kwargs: Any) -> str:
        """Render a prompt template."""
        ...

    def parse(self, schema: str, response: str) -> dict[str, Any]:
        """Parse a response according to schema."""
        ...


# Prompt templates for Psi-gent stages
PSI_TEMPLATES = {
    "project": """
Given this problem: {problem_description}
Domain: {domain}

And this metaphor framework: {metaphor_name}
Description: {metaphor_description}
Available operations: {operations}

Map the problem concepts to metaphor concepts at abstraction level {abstraction:.1f}.
(0.0 = very concrete/specific, 1.0 = very abstract/general)

For each mapping provide:
- source: The problem concept
- target: The metaphor equivalent
- confidence: How good is this mapping? (0.0 to 1.0)

Also list any concepts that don't map well as "gaps".
""",
    "challenge": """
Projection: {mapped_description}
Metaphor: {metaphor_name}

Consider these adversarial questions:
1. What if the opposite were true?
2. What about extreme values (zero, very large)?
3. What problem aspects have no metaphor equivalent?
4. What does the metaphor predict that might be wrong?

Does the metaphor survive these challenges?
""",
    "solve": """
Current state in {metaphor_name} terms:
{current_state}

Available operations:
{operations}

Apply the most relevant operation. Show your reasoning step by step.
What operation applies? What is the result?
""",
    "translate": """
The metaphor-space conclusion was: {conclusion}
The original problem was: {problem_description}
The mapping was: {mappings}

Translate the conclusion into concrete terms for the original problem.
What specific actions does this imply?
""",
}


def project_with_grammar(
    problem: Problem,
    metaphor: Metaphor,
    abstraction: float,
    g_gent: GrammarEngine,
) -> str:
    """Generate projection prompt using G-gent."""
    return g_gent.render(
        "psi_project",
        problem_description=problem.description,
        domain=problem.domain,
        metaphor_name=metaphor.name,
        metaphor_description=metaphor.description,
        operations=[op.name for op in metaphor.operations],
        abstraction=abstraction,
    )


# =============================================================================
# Dependency Injection
# =============================================================================


@dataclass
class GentDependencies:
    """Injected gent dependencies for MetaphorEngine."""

    l_gent: LEmbedder | None = None
    b_gent: BudgetManager | None = None
    d_gent: DataAgent | None = None
    n_gent: Historian | None = None
    g_gent: GrammarEngine | None = None


@dataclass(frozen=True)
class IntegrationConfig:
    """Configuration for gent integrations."""

    # L-gent
    l_gent_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_size: int = 10000

    # B-gent
    default_budget: int = 6000
    budget_strategy: str = "metered"  # or "fixed" or "unlimited"

    # D-gent
    persistence_backend: str = "memory"  # or "sqlite" or "redis"
    state_path: str = "./psi_state"

    # N-gent
    trace_level: str = "full"  # or "summary" or "none"
    trace_retention_days: int = 30

    # G-gent
    grammar_validation: bool = True
    strict_parsing: bool = False


def create_engine_with_deps(
    deps: GentDependencies | None = None,
    config: IntegrationConfig | None = None,
) -> MetaphorEngine:
    """Create MetaphorEngine with optional dependencies."""
    engine = MetaphorEngine()

    if deps:
        # Wire up integrations as available
        # In production, would configure engine.llm_call with actual LLM
        pass

    return engine


# =============================================================================
# Graceful Degradation
# =============================================================================


class ResilientEngine:
    """MetaphorEngine wrapper that degrades gracefully."""

    def __init__(
        self,
        engine: MetaphorEngine,
        deps: GentDependencies | None = None,
    ):
        self.engine = engine
        self.deps = deps or GentDependencies()

    def solve_problem(self, problem: Problem) -> Solution:
        """Solve with graceful degradation."""
        # Try with full integrations
        if self.deps.l_gent:
            try:
                problem = embed_problem(problem, self.deps.l_gent)
            except Exception:
                pass  # Fall back to non-embedded retrieval

        if self.deps.n_gent:
            try:
                solution, trace = solve_with_tracing(
                    problem, self.engine, self.deps.n_gent
                )
                return solution
            except Exception:
                pass  # Fall back to non-traced solve

        # Basic solve
        return self.engine.solve_problem(problem)
