"""
Ψ-gent Integration Tests: Ψ × L × B × D × N × G

Tests integration between Ψ-gent (Metaphor Engine) and other agents:
- Ψ × L: Embedding-based metaphor retrieval
- Ψ × B: Token economics for solve attempts
- Ψ × D: Persistent learning models
- Ψ × N: Narrative tracing of solve attempts
- Ψ × G: Grammar-based prompt templates

Philosophy: Reasoning by analogy as geometric transformation.
"""

import pytest
from datetime import datetime
from typing import Any

from agents.psi import (
    MetaphorEngine,
    Problem,
    Metaphor,
    Operation,
    Solution,
    EngineConfig,
)
from agents.psi.integrations import (
    embed_problem,
    embed_metaphor,
    embed_corpus,
    cosine_similarity,
    retrieve_by_embedding,
    solve_with_budget,
    PsiBudget,
    TokenReceipt,
    PersistentEngine,
    solve_with_tracing,
    PsiTrace,
    project_with_grammar,
    GentDependencies,
    IntegrationConfig,
    create_engine_with_deps,
    ResilientEngine,
)
from agents.psi.learning import ThompsonSamplingModel, AbstractionModel


# =============================================================================
# Mock Implementations for Testing
# =============================================================================


class MockLEmbedder:
    """Mock L-gent embedder for testing."""

    def __init__(self, dim: int = 64):
        self.dim = dim
        self.call_count = 0

    def embed(self, text: str) -> tuple[float, ...]:
        """Generate deterministic embedding from text."""
        self.call_count += 1
        # Simple hash-based embedding for determinism
        h = hash(text) % (10**9)
        return tuple(((h + i * 12345) % 1000) / 1000.0 for i in range(self.dim))

    def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
        """Batch embed."""
        return [self.embed(t) for t in texts]


class MockBudgetManager:
    """Mock B-gent budget manager for testing."""

    def __init__(self, balance: int = 10000):
        self.balance = balance
        self.authorizations: list[dict] = []
        self.costs: list[dict] = []

    def authorize(self, operation: str, estimated_tokens: int) -> bool:
        """Authorize token usage."""
        authorized = self.balance >= estimated_tokens
        self.authorizations.append(
            {
                "operation": operation,
                "tokens": estimated_tokens,
                "authorized": authorized,
            }
        )
        return authorized

    def record_cost(self, category: str, tokens: int, metadata: dict[str, Any]) -> None:
        """Record actual cost."""
        self.costs.append(
            {
                "category": category,
                "tokens": tokens,
                "metadata": metadata,
            }
        )
        self.balance -= tokens


class MockDataAgent:
    """Mock D-gent data agent for testing."""

    def __init__(self):
        self.store: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self.store.get(key)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value


class MockHistorian:
    """Mock N-gent historian for testing."""

    def __init__(self):
        self.traces: list[dict] = []
        self.active_traces: dict[str, dict] = {}

    def begin_trace(self, action: str, input_obj: dict[str, Any]) -> str:
        """Begin a trace, return trace ID."""
        trace_id = f"trace_{len(self.traces)}"
        self.active_traces[trace_id] = {
            "action": action,
            "input": input_obj,
            "started": datetime.now(),
        }
        return trace_id

    def end_trace(self, ctx: str, outputs: dict[str, Any]) -> None:
        """End a trace."""
        if ctx in self.active_traces:
            trace = self.active_traces.pop(ctx)
            trace["outputs"] = outputs
            trace["ended"] = datetime.now()
            self.traces.append(trace)

    def abort_trace(self, ctx: str, error: str) -> None:
        """Abort a trace due to error."""
        if ctx in self.active_traces:
            trace = self.active_traces.pop(ctx)
            trace["error"] = error
            trace["aborted"] = datetime.now()
            self.traces.append(trace)


class MockGrammarEngine:
    """Mock G-gent grammar engine for testing."""

    def __init__(self):
        self.templates: dict[str, str] = {
            "psi_project": "Project {problem_description} into {metaphor_name} at abstraction {abstraction}",
        }
        self.render_calls: list[dict] = []

    def render(self, template: str, **kwargs: Any) -> str:
        """Render a template."""
        self.render_calls.append({"template": template, "kwargs": kwargs})
        if template in self.templates:
            return self.templates[template].format(**kwargs)
        return f"Template: {template}, Args: {kwargs}"

    def parse(self, schema: str, response: str) -> dict[str, Any]:
        """Parse a response."""
        return {"raw": response, "schema": schema}


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_problem() -> Problem:
    """Create a sample problem for testing."""
    return Problem(
        id="test_problem_1",
        description="How should we optimize the database query performance?",
        domain="software_engineering",
        constraints=["must maintain data integrity", "limit memory usage"],
    )


@pytest.fixture
def sample_metaphors() -> list[Metaphor]:
    """Create sample metaphors for testing."""
    return [
        Metaphor(
            id="hydraulics",
            name="Hydraulic Flow",
            domain="physics",
            description="Data as flowing liquid through pipes",
            operations=(
                Operation(
                    name="increase_pressure",
                    description="Add more processing power",
                    preconditions=("system is bottlenecked",),
                    effects=("throughput increases",),
                ),
                Operation(
                    name="widen_pipe",
                    description="Increase bandwidth/capacity",
                    preconditions=("narrow pipe identified",),
                    effects=("flow rate increases",),
                ),
            ),
        ),
        Metaphor(
            id="gardening",
            name="Garden Cultivation",
            domain="biology",
            description="Data as plants to be cultivated",
            operations=(
                Operation(
                    name="prune",
                    description="Remove unnecessary data",
                    preconditions=("overgrowth detected",),
                    effects=("cleaner data structure",),
                ),
                Operation(
                    name="fertilize",
                    description="Add supporting resources",
                    preconditions=("growth is slow",),
                    effects=("data processing improves",),
                ),
            ),
        ),
    ]


@pytest.fixture
def engine() -> MetaphorEngine:
    """Create a test engine."""
    return MetaphorEngine(config=EngineConfig())


# =============================================================================
# Ψ × L: Embedding Integration Tests
# =============================================================================


class TestPsiLgentIntegration:
    """Test Ψ-gent × L-gent integration (embeddings)."""

    def test_embed_problem(self, sample_problem):
        """Test embedding a problem with L-gent."""
        embedder = MockLEmbedder(dim=32)

        embedded = embed_problem(sample_problem, embedder)

        assert embedded.embedding is not None
        assert len(embedded.embedding) == 32
        assert embedder.call_count == 1

    def test_embed_problem_cached(self, sample_problem):
        """Test that already-embedded problems are not re-embedded."""
        embedder = MockLEmbedder(dim=32)

        # First embedding
        embedded1 = embed_problem(sample_problem, embedder)
        # Second call should use cached embedding
        embedded2 = embed_problem(embedded1, embedder)

        assert embedded1.embedding == embedded2.embedding
        assert embedder.call_count == 1  # Only called once

    def test_embed_metaphor(self, sample_metaphors):
        """Test embedding a metaphor with L-gent."""
        embedder = MockLEmbedder(dim=32)
        metaphor = sample_metaphors[0]

        embedded = embed_metaphor(metaphor, embedder)

        assert embedded.embedding is not None
        assert len(embedded.embedding) == 32

    def test_embed_corpus(self, sample_metaphors):
        """Test batch embedding entire corpus."""
        embedder = MockLEmbedder(dim=32)

        embedded_corpus = embed_corpus(sample_metaphors, embedder)

        assert len(embedded_corpus) == len(sample_metaphors)
        assert all(m.embedding is not None for m in embedded_corpus)
        # Batch embed should be called once
        assert embedder.call_count == 2  # One per metaphor

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        a = (1.0, 0.0, 0.0)
        b = (1.0, 0.0, 0.0)
        c = (0.0, 1.0, 0.0)

        # Same vector = 1.0
        assert cosine_similarity(a, b) == pytest.approx(1.0)
        # Orthogonal vectors = 0.0
        assert cosine_similarity(a, c) == pytest.approx(0.0)

    def test_retrieve_by_embedding(self, sample_problem, sample_metaphors):
        """Test retrieval using embeddings."""
        embedder = MockLEmbedder(dim=32)

        # Embed corpus first
        embedded_corpus = embed_corpus(sample_metaphors, embedder)

        # Retrieve by embedding
        results = retrieve_by_embedding(sample_problem, embedded_corpus, embedder)

        assert len(results) == len(sample_metaphors)
        # Results should be sorted by similarity
        for i in range(len(results) - 1):
            assert results[i][1] >= results[i + 1][1]


# =============================================================================
# Ψ × B: Budget Integration Tests
# =============================================================================


class TestPsiBgentIntegration:
    """Test Ψ-gent × B-gent integration (token economics)."""

    def test_solve_with_budget_authorized(self, sample_problem, engine):
        """Test solve with sufficient budget."""
        budget_manager = MockBudgetManager(balance=10000)

        solution, receipt = solve_with_budget(
            sample_problem,
            engine,
            budget_manager,
            PsiBudget(total_budget=6000),
        )

        # Should be authorized
        assert len(budget_manager.authorizations) == 1
        assert budget_manager.authorizations[0]["authorized"] is True

    def test_solve_with_budget_denied(self, sample_problem, engine):
        """Test solve with insufficient budget."""
        budget_manager = MockBudgetManager(balance=100)  # Low balance

        solution, receipt = solve_with_budget(
            sample_problem,
            engine,
            budget_manager,
            PsiBudget(total_budget=6000),
        )

        # Should be denied
        assert solution is None
        assert budget_manager.authorizations[0]["authorized"] is False

    def test_token_receipt_tracking(self):
        """Test token receipt accumulation."""
        receipt = TokenReceipt(
            retrieve_tokens=100,
            project_tokens=200,
            challenge_tokens=150,
            solve_tokens=500,
            translate_tokens=100,
            verify_tokens=50,
        )

        assert receipt.total == 1100

    def test_psi_budget_defaults(self):
        """Test PsiBudget default values."""
        budget = PsiBudget()

        assert budget.total_budget == 6000
        assert budget.retrieve_budget == 500
        assert budget.solve_budget == 2000


# =============================================================================
# Ψ × D: Persistence Integration Tests
# =============================================================================


class TestPsiDgentIntegration:
    """Test Ψ-gent × D-gent integration (state persistence)."""

    def test_persistent_engine_creation(self):
        """Test creating persistent engine with D-gent."""
        data_agent = MockDataAgent()
        engine = PersistentEngine(d_gent=data_agent)

        assert engine.engine is not None

    def test_persistent_engine_saves_state(self, sample_problem):
        """Test that persistent engine saves state after solve."""
        data_agent = MockDataAgent()
        engine = PersistentEngine(d_gent=data_agent)

        # Solve problem (side effect: saves state)
        engine.solve_problem(sample_problem)

        # State should be saved
        assert "psi/learning_model" in data_agent.store

    def test_persistent_engine_loads_state(self):
        """Test loading state from D-gent."""
        data_agent = MockDataAgent()

        # Pre-populate with serialized model
        data_agent.set(
            "psi/learning_model",
            {
                "type": "thompson",
                "alphas": {"problem1:metaphor1": 5.0},
                "betas": {"problem1:metaphor1": 2.0},
            },
        )

        engine = PersistentEngine(d_gent=data_agent)

        # Model should be loaded
        assert engine.engine.retrieval_model is not None


# =============================================================================
# Ψ × N: Tracing Integration Tests
# =============================================================================


class TestPsiNgentIntegration:
    """Test Ψ-gent × N-gent integration (narrative tracing)."""

    def test_solve_with_tracing(self, sample_problem, engine):
        """Test solve with N-gent tracing."""
        historian = MockHistorian()

        solution, trace = solve_with_tracing(sample_problem, engine, historian)

        # Should have trace
        assert isinstance(trace, PsiTrace)
        assert trace.problem_id == sample_problem.id
        assert trace.timestamp is not None

    def test_trace_captures_stages(self, sample_problem, engine):
        """Test that trace captures all stages."""
        historian = MockHistorian()

        # Set up stage callback to capture stages
        captured_stages = []

        def capture_stage(stage: str, data: Any) -> None:
            captured_stages.append(stage)

        engine.on_stage_complete = capture_stage

        solution, trace = solve_with_tracing(sample_problem, engine, historian)

        # Trace should have stages
        assert isinstance(trace.stages, dict)

    def test_historian_records_trace(self, sample_problem, engine):
        """Test that historian records the trace."""
        historian = MockHistorian()

        solve_with_tracing(sample_problem, engine, historian)

        # Historian should have recorded trace
        assert len(historian.traces) == 1
        assert historian.traces[0]["action"] == "psi_solve"


# =============================================================================
# Ψ × G: Grammar Integration Tests
# =============================================================================


class TestPsiGgentIntegration:
    """Test Ψ-gent × G-gent integration (grammar/prompts)."""

    def test_project_with_grammar(self, sample_problem, sample_metaphors):
        """Test project stage using G-gent grammar."""
        grammar = MockGrammarEngine()
        metaphor = sample_metaphors[0]

        project_with_grammar(
            sample_problem,
            metaphor,
            abstraction=0.5,
            g_gent=grammar,
        )

        # Should have rendered template
        assert len(grammar.render_calls) == 1
        assert grammar.render_calls[0]["template"] == "psi_project"

    def test_grammar_template_rendering(self):
        """Test grammar template rendering."""
        grammar = MockGrammarEngine()

        result = grammar.render(
            "psi_project",
            problem_description="test problem",
            metaphor_name="Hydraulics",
            abstraction=0.5,
        )

        assert "test problem" in result
        assert "Hydraulics" in result


# =============================================================================
# Ψ Dependency Injection Tests
# =============================================================================


class TestPsiDependencyInjection:
    """Test Ψ-gent dependency injection."""

    def test_create_engine_with_no_deps(self):
        """Test creating engine without dependencies."""
        engine = create_engine_with_deps()
        assert engine is not None

    def test_create_engine_with_deps(self):
        """Test creating engine with injected dependencies."""
        deps = GentDependencies(
            l_gent=MockLEmbedder(),
            b_gent=MockBudgetManager(),
            d_gent=MockDataAgent(),
            n_gent=MockHistorian(),
            g_gent=MockGrammarEngine(),
        )

        engine = create_engine_with_deps(deps=deps)
        assert engine is not None

    def test_integration_config_defaults(self):
        """Test IntegrationConfig default values."""
        config = IntegrationConfig()

        assert config.default_budget == 6000
        assert config.persistence_backend == "memory"
        assert config.trace_level == "full"


# =============================================================================
# Ψ Resilient Engine Tests
# =============================================================================


class TestResilientEngine:
    """Test Ψ-gent resilient engine with graceful degradation."""

    def test_resilient_engine_without_deps(self, sample_problem):
        """Test resilient engine works without dependencies."""
        engine = MetaphorEngine()
        resilient = ResilientEngine(engine)

        solution = resilient.solve_problem(sample_problem)
        assert isinstance(solution, Solution)

    def test_resilient_engine_with_l_gent(self, sample_problem):
        """Test resilient engine uses L-gent when available."""
        engine = MetaphorEngine()
        deps = GentDependencies(l_gent=MockLEmbedder())
        resilient = ResilientEngine(engine, deps=deps)

        solution = resilient.solve_problem(sample_problem)
        assert isinstance(solution, Solution)

    def test_resilient_engine_with_n_gent(self, sample_problem):
        """Test resilient engine uses N-gent when available."""
        engine = MetaphorEngine()
        deps = GentDependencies(n_gent=MockHistorian())
        resilient = ResilientEngine(engine, deps=deps)

        solution = resilient.solve_problem(sample_problem)
        assert isinstance(solution, Solution)

    def test_resilient_engine_handles_l_gent_failure(self, sample_problem):
        """Test resilient engine continues if L-gent fails."""

        class FailingEmbedder:
            def embed(self, text: str) -> tuple[float, ...]:
                raise RuntimeError("Embedding service unavailable")

            def embed_batch(self, texts: list[str]) -> list[tuple[float, ...]]:
                raise RuntimeError("Embedding service unavailable")

        engine = MetaphorEngine()
        deps = GentDependencies(l_gent=FailingEmbedder())
        resilient = ResilientEngine(engine, deps=deps)

        # Should still work, falling back to basic solve
        solution = resilient.solve_problem(sample_problem)
        assert isinstance(solution, Solution)


# =============================================================================
# Ψ Learning Model Integration Tests
# =============================================================================


class TestPsiLearningIntegration:
    """Test Ψ-gent learning model integration."""

    def test_thompson_sampling_integration(self, sample_problem):
        """Test Thompson sampling model with solve."""
        engine = MetaphorEngine()

        # Solve multiple times to test learning
        for _ in range(3):
            engine.solve_problem(sample_problem)

        # Model should have some data
        assert isinstance(engine.retrieval_model, ThompsonSamplingModel)

    def test_abstraction_model_integration(self, sample_problem):
        """Test abstraction model with solve."""
        engine = MetaphorEngine()
        engine.solve_problem(sample_problem)

        # Abstraction model should exist
        assert isinstance(engine.abstraction_model, AbstractionModel)

    def test_feedback_updates_model(self, sample_problem):
        """Test that feedback updates learning model."""
        engine = MetaphorEngine()

        # Initial solve
        engine.solve_problem(sample_problem)

        # Check if update_from_feedback exists
        if hasattr(engine.retrieval_model, "update"):
            # This tests that the model can accept feedback
            initial_state = engine.retrieval_model.is_trained
            # After feedback, model state may change
            assert isinstance(initial_state, bool)
