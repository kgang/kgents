"""
ASHC - Agentic Self-Hosting Compiler

The compiler is a trace accumulator, not a code generator.
The proof has skin in the game: ASHC bets resources on its confidence.

Phase 1: L0 Kernel
    - Five primitives: compose, apply, match, emit, witness
    - Fail-fast, voice-agnostic, independent from Logos

Phase 2: Evidence Accumulation Engine
    - Run N variations, verify with pytest/mypy/ruff
    - Accumulate evidence, compute equivalence scores
    - "The proof is not formal—it's empirical."

Phase 2.5: Adaptive Bayesian Evidence
    - n_diff stopping rule, Beta-Binomial updating
    - Confidence tiers, LLM pre-verification

Phase 2.75: Economic Accountability
    - ASHC places bets with stakes proportional to confidence
    - Adversary takes the other side, wins on failure
    - Bullshit (high confidence + failure) is severely penalized
    - Causal penalty propagates blame to cited principles

Phase 3: Causal Graph Learning
    - Learn nudge → outcome relationships from evidence
    - Predict outcomes for new nudges based on similarity
    - Verify Causal Monotonicity law
    - "The pattern of nudges IS the proof."

Phase 4: LLM Harness
    - VoidHarness: Isolated Claude CLI execution (no CLAUDE.md)
    - Real LLM generation for testing Bayesian infrastructure
    - Token budget tracking and concurrency control
    - Integration with EvidenceCompiler and AdaptiveCompiler

Phase 5: Bootstrap Regeneration
    - BootstrapRegenerator: Regenerate bootstrap from spec/bootstrap.md
    - IsomorphismChecker: Verify behavioral equivalence
    - SpecParser: Parse markdown into structured agent specs
    - "The kernel that proves itself is the kernel that trusts itself."

Example (L0):
    from protocols.ashc import L0Program

    program = L0Program("my_program")
    x = program.define("x", program.literal(42))
    y = program.define("y", program.call(lambda n: n + 1, n=x))
    program.emit("result", y)
    result = await program.run()
    print(result.artifacts)

Example (Economic Accountability):
    from protocols.ashc import ASHCBet, ASHCCredibility, AdversarialAccountability

    cred = ASHCCredibility()
    adversary = AdversarialAccountability()

    bet = ASHCBet.create(spec="x = 1", confidence=0.9, stake=Decimal("0.10"))
    resolved = bet.resolve(success=False)  # Bullshit!

    cred.record_outcome(resolved)  # Credibility drops
    settlement = adversary.settle_bet(resolved, cred)  # Adversary wins
"""

# Phase 2.5: Adaptive Evidence (Bayesian)
from .adaptive import (
    AdaptiveCompiler,
    AdaptiveEvidence,
    AdaptiveRunResult,
    BetaPrior,
    ConfidenceTier,
    StoppingConfig,
    StoppingDecision,
    StoppingState,
    adaptive_compile,
    expected_samples_for_ndiff,
    reliability_boost_from_voting,
)
from .adversary import (
    AdversarialAccountability,
    BetSettlement,
    create_settlement_report,
)
from .ast import (
    DictPattern,
    L0Call,
    L0Compose,
    L0Define,
    L0Emit,
    L0Expr,
    L0Handle,
    L0Literal,
    L0MatchExpr,
    L0Pattern,
    L0ProgramAST,
    L0Stmt,
    L0Witness,
    ListPattern,
    LiteralPattern,
    WildcardPattern,
)

# Phase 5: Bootstrap Regeneration
from .bootstrap import (
    AGENT_NAMES,
    BehaviorComparison,
    BootstrapAgentSpec,
    BootstrapIsomorphism,
    BootstrapRegenerator,
    RegenerationConfig,
    check_isomorphism,
    parse_bootstrap_spec,
)

# Phase 3: Causal Graph Learning
from .causal_graph import (
    CausalEdge,
    CausalGraph,
    CausalLearner,
    build_graph_from_edges,
    create_edge,
    is_similar_nudge,
    nudge_similarity,
    text_similarity,
)
from .causal_penalty import (
    CausalPenalty,
    PrincipleCredibility,
    PrincipleRegistry,
)

# Phase 2.75: Economic Accountability
from .economy import (
    AllocationStrategy,
    ASHCBet,
    ASHCCredibility,
    ASHCEconomy,
)

# Phase 2: Evidence Accumulation Engine
from .evidence import (
    ASHCOutput,
    Evidence,
    EvidenceCompiler,
    Nudge,
    Run,
    compile_spec,
    quick_verify,
)

# Phase 4: LLM Harness
from .harness import (
    GenerationResult,
    TokenBudget,
    VoidHarness,
    VoidHarnessConfig,
    generate_from_spec,
    generate_n_from_spec,
)
from .llm_compiler import (
    adaptive_compile_with_llm,
    compile_with_llm,
    compile_with_nudges,
    learn_causal_graph,
)
from .patterns import (
    L0MatchError,
    dict_pattern,
    list_pattern,
    literal,
    match,
    wildcard,
)
from .primitives import (
    Artifact,
    ComposedCallable,
    L0Primitives,
    TraceWitnessResult,
    VerificationStatus,
    get_primitives,
)
from .program import L0Program
from .runtime import L0Error, L0Result, run_program
from .stubs import (
    BOOTSTRAP_STUBS,
    contradict_stub,
    get_stub,
    ground_context_stub,
    ground_manifest_stub,
    identity_stub,
    judge_spec_stub,
    sublate_stub,
)
from .verify import (
    LintReport,
    TestReport,
    TypeReport,
    VerificationResult,
    run_mypy,
    run_pytest,
    run_ruff,
    verify_code,
)

__all__ = [
    # Program builder (main entry point)
    "L0Program",
    # Result types
    "L0Result",
    "L0Error",
    "Artifact",
    "TraceWitnessResult",
    "VerificationStatus",
    # AST types
    "L0ProgramAST",
    "L0Expr",
    "L0Stmt",
    "L0Handle",
    "L0Literal",
    "L0Call",
    "L0Compose",
    "L0MatchExpr",
    "L0Define",
    "L0Emit",
    "L0Witness",
    # Pattern types
    "L0Pattern",
    "LiteralPattern",
    "WildcardPattern",
    "DictPattern",
    "ListPattern",
    # Pattern helpers
    "match",
    "literal",
    "wildcard",
    "dict_pattern",
    "list_pattern",
    "L0MatchError",
    # Primitives
    "L0Primitives",
    "ComposedCallable",
    "get_primitives",
    # Runtime
    "run_program",
    # Stubs (pre-Logos)
    "BOOTSTRAP_STUBS",
    "get_stub",
    "ground_manifest_stub",
    "ground_context_stub",
    "judge_spec_stub",
    "contradict_stub",
    "sublate_stub",
    "identity_stub",
    # Phase 2: Evidence Accumulation
    "EvidenceCompiler",
    "Evidence",
    "Run",
    "Nudge",
    "ASHCOutput",
    "compile_spec",
    "quick_verify",
    # Phase 2: Verification Runners
    "TestReport",
    "TypeReport",
    "LintReport",
    "VerificationResult",
    "run_pytest",
    "run_mypy",
    "run_ruff",
    "verify_code",
    # Phase 2.5: Adaptive Evidence (Bayesian)
    "AdaptiveCompiler",
    "AdaptiveEvidence",
    "AdaptiveRunResult",
    "BetaPrior",
    "ConfidenceTier",
    "StoppingConfig",
    "StoppingDecision",
    "StoppingState",
    "adaptive_compile",
    "expected_samples_for_ndiff",
    "reliability_boost_from_voting",
    # Phase 2.75: Economic Accountability
    "ASHCBet",
    "ASHCCredibility",
    "ASHCEconomy",
    "AllocationStrategy",
    "AdversarialAccountability",
    "BetSettlement",
    "create_settlement_report",
    "CausalPenalty",
    "PrincipleCredibility",
    "PrincipleRegistry",
    # Phase 3: Causal Graph Learning
    "CausalEdge",
    "CausalGraph",
    "CausalLearner",
    "build_graph_from_edges",
    "create_edge",
    "is_similar_nudge",
    "nudge_similarity",
    "text_similarity",
    # Phase 4: LLM Harness
    "VoidHarness",
    "VoidHarnessConfig",
    "TokenBudget",
    "GenerationResult",
    "generate_from_spec",
    "generate_n_from_spec",
    "compile_with_llm",
    "adaptive_compile_with_llm",
    "compile_with_nudges",
    "learn_causal_graph",
    # Phase 5: Bootstrap Regeneration
    "AGENT_NAMES",
    "BootstrapAgentSpec",
    "BootstrapRegenerator",
    "RegenerationConfig",
    "BehaviorComparison",
    "BootstrapIsomorphism",
    "parse_bootstrap_spec",
    "check_isomorphism",
]
