"""
evolve.py - Experimental Improvement Framework

A creative framework for experimentally testing, synthesizing, and
incorporating improvements into kgents.

Philosophy:
- Evolution through dialectic: thesis (current) + antithesis (improvement) → synthesis
- Experiments are cheap, production is sacred
- Fix pattern: iterate until stable (now explicit via bootstrap.Fix)
- Conflicts are data: log tensions, don't hide them

Architecture (Bootstrap-Enhanced):
    EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate

    Bootstrap agents used directly for self-improvement:
    - Judge: Evaluates hypotheses against 7 principles (tasteful→generative)
    - Fix: Convergence-tracked iteration with entropy budgets
    - Contradict: Surfaces tensions between current/improved code
    - Sublate: Synthesizes or holds productive tensions
    - Ground: Injects persona values into prompts

    E-gent agents in agents/e/:
    - ASTAnalyzer: Static analysis for targeted hypotheses
    - MemoryAgent: Track rejected/accepted improvements
    - TestAgent: Validate syntax, types, tests
    - CodeJudge: Domain-specific code evaluation
    - IncorporateAgent: Apply with git safety

Usage (New Default: Test Mode):
    python evolve.py                      # Test mode (fast, safe, single module)
    python evolve.py status               # Check current status (AI agent friendly)
    python evolve.py suggest              # Get improvement suggestions
    python evolve.py meta --auto-apply    # Self-improve evolve.py
    python evolve.py full --auto-apply    # Full codebase evolution

Modes:
    test (default): Fast testing on single module (dry-run, quick, 2 hypotheses)
    status: Show current evolution state and recommendations
    suggest: Analyze and suggest improvements without running experiments
    full: Thorough evolution (all modules, 4 hypotheses, dialectic synthesis)

Flags:
    --dry-run: Preview improvements without applying (default in test mode)
    --auto-apply: Automatically apply improvements that pass tests
    --quick: Skip dialectic synthesis for faster iteration
    --thorough: Use full dialectic synthesis
    --hypotheses=N: Number of hypotheses per module
    --max-improvements=N: Max improvements per module

AI Agent Interface:
    The 'status' and 'suggest' modes are designed for AI agents to query
    the current state and get actionable recommendations without making changes.
    This supports periodic checks via /hydrate command.

Performance:
    Modules are processed in parallel for 2-5x speedup
    Large files (>500 lines) send previews to reduce token usage
    AST analysis is cached to avoid redundant parsing
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

# TYPE_CHECKING: Import types only during type-checking to reduce startup time
if TYPE_CHECKING:
    from agents.b.hypothesis import HypothesisEngine, HypothesisInput
    from agents.h.hegel import HegelAgent, DialecticInput, DialecticOutput
    from bootstrap.sublate import Sublate
    from bootstrap.fix import Fix, FixConfig, FixResult
    from bootstrap.contradict import Contradict, ContradictInput, ContradictResult
    from bootstrap.judge import Judge as BootstrapJudge, JudgeInput as BootstrapJudgeInput
    from bootstrap.ground import Ground
    from runtime.base import LLMAgent, AgentContext, AgentResult

# E-gents: Evolution agents (Phase 1 extraction)
from agents.e import (
    # Core types
    CodeModule,
    CodeImprovement,
    Experiment,
    ExperimentStatus,
    # Agents
    ASTAnalyzer,
    ASTAnalysisInput,
    ImprovementMemory,
    TestAgent,
    TestInput,
    CodeJudge,
    JudgeInput,
    IncorporateAgent,
    IncorporateInput,
    # Utilities
    analyze_module_ast,
    generate_targeted_hypotheses,
    get_code_preview,
    extract_metadata,
    extract_code,
    # Safety (Phase 2)
    SafetyConfig,
    SelfEvolutionAgent,
    SafeEvolutionInput,
    compute_code_similarity,
    # Recovery Layer (Phase 2.5c)
    RetryStrategy,
    RetryConfig,
    FallbackStrategy,
    FallbackConfig,
    ErrorMemory,
    # Status Agents (Phase 2.5e)
    create_status_reporter,
    # Evolution Pipeline (Phase B: Refactored to use agents/e)
    EvolutionPipeline,
    EvolutionConfig,
    EvolutionReport,
)

# Bootstrap imports - the irreducible kernel for self-improvement
from bootstrap import make_default_principles
from bootstrap.types import (
    Agent,
    Verdict,
    VerdictType,
    Synthesis,
    SublateInput,
    Tension,
    TensionMode,
    HoldTension,
    FixConfig,
    FixResult,
    ContradictInput,
    ContradictResult,
    JudgeInput as BootstrapJudgeInputType,
    Facts,
    VOID,
)


# ============================================================================
# Configuration
# ============================================================================

def log(msg: str = "", prefix: str = "", file: Optional[Any] = None) -> None:
    """Print with immediate flush for real-time output."""
    output = f"{prefix} {msg}" if prefix else msg
    print(output, flush=True)
    if file:
        file.write(output + "\n")
        file.flush()


@dataclass
class EvolveCliConfig:
    """
    CLI configuration for evolve.py.

    This extends EvolutionConfig with CLI-specific options like mode and safe_mode.
    Converted to EvolutionConfig via to_evolution_config() for use with agents/e.
    """
    target: str = "meta"  # Default to single module for testing
    mode: str = "test"  # test|status|suggest|full
    dry_run: bool = True  # Safe by default
    auto_apply: bool = False
    max_improvements_per_module: int = 1  # Reduced for testing
    experiment_branch_prefix: str = "evolve"
    require_tests_pass: bool = True
    require_type_check: bool = True
    quick_mode: bool = True  # Fast by default for testing
    hypothesis_count: int = 2  # Reduced for testing
    # Phase 2: Safe self-evolution
    safe_mode: bool = False
    max_iterations: int = 3
    convergence_threshold: float = 0.95
    # Phase 2.5c: Recovery layer
    enable_retry: bool = True
    max_retries: int = 2
    enable_fallback: bool = True
    enable_error_memory: bool = True

    def to_evolution_config(self) -> EvolutionConfig:
        """Convert CLI config to EvolutionConfig for agents/e."""
        return EvolutionConfig(
            target=self.target,
            dry_run=self.dry_run,
            auto_apply=self.auto_apply,
            max_improvements_per_module=self.max_improvements_per_module,
            hypothesis_count=self.hypothesis_count,
            quick_mode=self.quick_mode,
            require_tests_pass=self.require_tests_pass,
            require_type_check=self.require_type_check,
        )


# ============================================================================
# Bootstrap Self-Improvement Helpers
# ============================================================================
# These functions use bootstrap agents DIRECTLY for self-improvement,
# without external coordination. See HYDRATE.md for the full analysis.

def _get_bootstrap_judge() -> "BootstrapJudge":
    """Lazy instantiation of bootstrap Judge for hypothesis evaluation."""
    from bootstrap.judge import Judge
    return Judge()


def _get_bootstrap_fix() -> "Fix":
    """Lazy instantiation of bootstrap Fix for convergence tracking."""
    from bootstrap.fix import Fix
    return Fix


def _get_bootstrap_contradict() -> "Contradict":
    """Lazy instantiation of bootstrap Contradict for tension detection."""
    from bootstrap.contradict import Contradict
    return Contradict()


def _get_bootstrap_ground() -> "Ground":
    """Lazy instantiation of bootstrap Ground for persona/world facts."""
    from bootstrap.ground import Ground
    return Ground()


async def get_grounded_context() -> Facts:
    """
    Get grounded context from bootstrap Ground agent.

    Injects persona values and world state into evolution prompts.
    This ensures improvements align with Kent's preferences (spec/k-gent/persona.md).

    Usage:
        facts = await get_grounded_context()
        # facts.persona.values -> ("intellectual honesty", "ethical technology", ...)
        # facts.persona.communication_style -> "direct but warm"
    """
    ground = _get_bootstrap_ground()
    return await ground.invoke(VOID)


async def detect_code_tension(
    original_code: str,
    improved_code: str,
    context: Optional[dict[str, Any]] = None,
) -> ContradictResult:
    """
    Use bootstrap Contradict to detect tensions between original and improved code.

    This surfaces conflicts that might not be obvious:
    - Logical: API changes that break compatibility
    - Pragmatic: Different recommendations for the same problem
    - Aesthetic: Style conflicts (naming, structure)

    Returns:
        ContradictResult with detected tensions (if any)
    """
    contradict = _get_bootstrap_contradict()
    return await contradict.invoke(ContradictInput(
        a=original_code,
        b=improved_code,
        context=context,
    ))


async def iterate_with_fix(
    transform_fn: Any,
    initial_value: Any,
    max_iterations: int = 10,
    entropy_budget: Optional[float] = 1.0,
) -> FixResult:
    """
    Use bootstrap Fix for convergence-tracked iteration.

    This replaces ad-hoc retry loops with principled fixed-point iteration:
    - Tracks convergence history
    - Respects entropy budgets (diminishes with depth)
    - Returns proximity metric for adaptive strategies

    Args:
        transform_fn: Async function that improves the value
        initial_value: Starting point
        max_iterations: Maximum iterations before stopping
        entropy_budget: J-gents entropy budget (diminishes per iteration)

    Returns:
        FixResult with value, converged status, and history
    """
    from bootstrap.fix import Fix
    config: FixConfig = FixConfig(
        max_iterations=max_iterations,
        entropy_budget=entropy_budget,
    )
    fix = Fix(config)
    return await fix.invoke((transform_fn, initial_value))


class HypothesisWrapper(Agent[str, str]):
    """
    Wrapper to make a hypothesis string into an Agent for Judge evaluation.

    Bootstrap Judge expects an Agent[Any, Any], but we want to evaluate
    hypotheses (strings) against the 7 principles. This wrapper makes
    hypothesis strings behave like agents for judgment.
    """

    def __init__(self, hypothesis: str, module_name: str):
        self._hypothesis = hypothesis
        self._module_name = module_name

    @property
    def name(self) -> str:
        return f"Hypothesis({self._module_name}): {self._hypothesis[:50]}..."

    async def invoke(self, input: str) -> str:
        return self._hypothesis


async def judge_hypothesis_against_principles(
    hypothesis: str,
    module_name: str,
    principles: Optional[tuple[str, ...]] = None,
) -> Verdict:
    """
    Use bootstrap Judge to evaluate a hypothesis against the 7 principles.

    This provides a quality gate BEFORE generating code, filtering out
    hypotheses that violate kgents principles:
    - tasteful: Does this serve a clear purpose?
    - curated: Is this unique/valuable?
    - ethical: Does this respect user agency?
    - joyful: Does this add warmth?
    - composable: Will this compose well?
    - heterarchical: Does this avoid fixed hierarchy?
    - generative: Can this be regenerated from spec?

    Args:
        hypothesis: The improvement hypothesis to evaluate
        module_name: Name of the module being improved
        principles: Specific principles to check (default: all 7)

    Returns:
        Verdict with ACCEPT, REVISE, or REJECT
    """
    from bootstrap.judge import Judge, JudgeInput

    # Wrap hypothesis as an agent for Judge
    hypothesis_agent = HypothesisWrapper(hypothesis, module_name)

    judge = Judge()
    return await judge.invoke(JudgeInput(
        agent=hypothesis_agent,
        principles=principles,
        context={"hypothesis": hypothesis, "module": module_name},
    ))


# ============================================================================
# Module Discovery (extracted from EvolutionPipeline)
# ============================================================================

def discover_modules(target: str) -> list[CodeModule]:
    """
    Discover modules to evolve based on target.

    Args:
        target: One of "runtime", "agents", "bootstrap", "meta", "all"

    Returns:
        List of CodeModule instances to evolve
    """
    base = Path(__file__).parent
    modules = []

    if target in ["runtime", "all"]:
        runtime_dir = base / "runtime"
        for py_file in runtime_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                modules.append(CodeModule(
                    name=py_file.stem,
                    category="runtime",
                    path=py_file
                ))

    if target in ["agents", "all"]:
        agents_dir = base / "agents"
        for letter_dir in agents_dir.iterdir():
            if letter_dir.is_dir() and not letter_dir.name.startswith("_"):
                for py_file in letter_dir.glob("*.py"):
                    if py_file.name != "__init__.py":
                        modules.append(CodeModule(
                            name=py_file.stem,
                            category=f"agents/{letter_dir.name}",
                            path=py_file
                        ))

    if target in ["bootstrap", "all"]:
        bootstrap_dir = base / "bootstrap"
        for py_file in bootstrap_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                modules.append(CodeModule(
                    name=py_file.stem,
                    category="bootstrap",
                    path=py_file
                ))

    if target in ["meta", "all"]:
        modules.append(CodeModule(
            name="evolve",
            category="meta",
            path=base / "evolve.py"
        ))

    return modules


def has_uncommitted_changes() -> bool:
    """Check if there are uncommitted changes in git."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


# ============================================================================
# CLI Wrapper (using agents/e/evolution.py)
# ============================================================================

async def run_evolution_cli(config: EvolveCliConfig) -> EvolutionReport:
    """
    Run evolution with CLI-specific logging and reporting.

    This is a thin wrapper around agents/e/evolution.py that adds:
    - Fancy CLI output with box-drawing
    - Log file creation with timestamps
    - JSON results export
    - Git status checking

    The core pipeline logic is in agents/e/evolution.py.
    """
    log_dir = Path(__file__).parent / ".evolve_logs"
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"evolve_{config.target}_{timestamp}.log"
    log_file = open(log_path, "w")

    log(f"{'='*60}")
    log(f"KGENTS EVOLUTION (Phase 1: Composable Agents)", file=log_file)
    log(f"Target: {config.target}", file=log_file)
    log(f"Dry run: {config.dry_run}", file=log_file)
    log(f"Auto-apply: {config.auto_apply}", file=log_file)
    log(f"Quick mode: {'True ⚡' if config.quick_mode else 'False'}", file=log_file)
    log(f"{'='*60}", file=log_file)
    log(f"⚠️ WARNING: Working tree is not clean." if has_uncommitted_changes() else "✓ Working tree is clean")
    log(f"", file=log_file)

    modules = discover_modules(config.target)
    log(f"Loaded {len(modules)} modules to evolve", file=log_file)
    log(f"📝 Log file: {log_path}")

    log(f"\nDiscovered {len(modules)} modules to evolve")

    # Create pipeline using agents/e
    evolution_config = config.to_evolution_config()
    pipeline = EvolutionPipeline(evolution_config)

    # Run the pipeline
    start_time = time.time()
    report = await pipeline.run(modules, log_fn=log)
    elapsed = time.time() - start_time

    log(f"\nProcessed {len(modules)} modules in {elapsed:.1f}s")

    # CLI-specific output
    log(f"\n{'='*60}", file=log_file)
    log("EVOLUTION SUMMARY", file=log_file)
    log(f"{'='*60}", file=log_file)
    log(f"Experiments run: {len(report.experiments)}", file=log_file)
    log(f"  Passed: {len([e for e in report.experiments if e.status == ExperimentStatus.PASSED])}", file=log_file)
    log(f"  Failed: {len(report.rejected)}", file=log_file)
    log(f"  Held (productive tension): {len(report.held)}", file=log_file)
    log(f"  Incorporated: {len(report.incorporated)}", file=log_file)

    passed = [e for e in report.experiments if e.status == ExperimentStatus.PASSED and e not in report.held]

    if passed and not config.auto_apply:
        log(f"\n{'-'*60}", file=log_file)
        log("READY TO INCORPORATE", file=log_file)
        log(f"{'-'*60}", file=log_file)
        for exp in passed:
            log(f"  [{exp.id}] {exp.improvement.description}", file=log_file)
        log(f"\nRun with --auto-apply to incorporate these improvements.", file=log_file)

    if report.held:
        log(f"\n{'-'*60}", file=log_file)
        log("HELD TENSIONS (require human judgment)", file=log_file)
        log(f"{'-'*60}", file=log_file)
        for exp in report.held:
            log(f"  [{exp.id}] {exp.improvement.description}", file=log_file)

    log(f"\n")
    log(f"╔{'═'*58}╗")
    log(f"║{' '*58}║")
    log(f"║  🎯 EVOLUTION COMPLETE - {config.target.upper():^32}  ║")
    log(f"║{' '*58}║")
    log(f"║  ✓ Passed: {len(passed):3d}   ✗ Failed: {len(report.rejected):3d}   ⏸ Held: {len(report.held):3d}   ✅ Applied: {len(report.incorporated):3d}  ║")
    log(f"║{' '*58}║")
    log(f"║  📝 Full log: {str(log_path)[-42:]:42}  ║")
    log(f"║{' '*58}║")
    log(f"╚{'═'*58}╝")

    # Export JSON results
    results_path = log_path.with_suffix('.json')
    results_data = {
        "timestamp": timestamp,
        "config": {
            "target": config.target,
            "dry_run": config.dry_run,
            "auto_apply": config.auto_apply,
            "quick_mode": config.quick_mode,
        },
        "summary": {
            "total_experiments": len(report.experiments),
            "passed": len(passed),
            "failed": len(report.rejected),
            "held": len(report.held),
            "incorporated": len(report.incorporated),
            "elapsed_seconds": elapsed,
        },
        "passed_experiments": [
            {
                "id": exp.id,
                "module": exp.module.name,
                "category": exp.module.category,
                "improvement": {
                    "type": exp.improvement.improvement_type,
                    "description": exp.improvement.description,
                    "rationale": exp.improvement.rationale,
                    "confidence": exp.improvement.confidence,
                },
                "status": exp.status.value,
            }
            for exp in passed
        ],
        "held_experiments": [
            {
                "id": exp.id,
                "module": exp.module.name,
                "improvement": {
                    "description": exp.improvement.description,
                    "rationale": exp.improvement.rationale,
                },
            }
            for exp in report.held
        ],
        "failed_experiments": [
            {
                "id": exp.id,
                "module": exp.module.name,
                "category": exp.module.category,
                "hypothesis": exp.hypothesis,
                "error": exp.error,
                "improvement": {
                    "type": exp.improvement.improvement_type,
                    "description": exp.improvement.description,
                } if exp.improvement else None,
                "test_results": exp.test_results,
            }
            for exp in report.rejected
        ],
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    log(f"📊 Decision data saved: {results_path}")

    log_file.close()

    return report


# ============================================================================
# DEPRECATED: Old EvolutionPipeline class (to be removed)
# ============================================================================
# The old 826-line EvolutionPipeline class has been replaced with:
# - run_evolution_cli() function (above) for CLI-specific features
# - agents/e/evolution.py for core pipeline logic
#
# TODO: Remove the old class entirely after validating the refactoring works.

# ============================================================================
# Status & Suggestion Modes (for AI agent interface)
# ============================================================================

async def show_status() -> None:
    """
    Show current evolution status - ideal for AI agents checking state.

    Refactored (Phase 2.5e) to use composable status agents:
        StatusReporter = GitStatusAgent >> EvolutionLogAgent >> HydrateStatusAgent >> StatusPresenter

    This demonstrates the morphism principle by decomposing an 83-line monolithic
    function into 4 composable agents with clear input/output types.
    """
    base = Path(__file__).parent
    reporter = create_status_reporter()
    await reporter.invoke(base)


async def show_suggestions(config: EvolveCliConfig) -> None:
    """
    Show improvement suggestions without running experiments.

    Enhanced (Bootstrap Integration):
    - Uses Ground to inject persona context into analysis
    - Uses Judge to evaluate hypotheses against 7 principles
    - Tracks tensions between current state and suggestions
    """
    log("=" * 60)
    log("EVOLUTION SUGGESTIONS (Bootstrap-Enhanced)")
    log("=" * 60)

    # Get grounded context for persona-aware suggestions
    facts = await get_grounded_context()
    log(f"📍 Grounded context: {facts.persona.name}'s preferences loaded")
    log(f"   Values: {', '.join(facts.persona.values[:3])}...")
    log("")

    modules = discover_modules(config.target)

    log(f"Analyzing {len(modules)} modules for improvement opportunities...\n")

    # Create an AST analyzer for quick analysis
    ast_analyzer = ASTAnalyzer(max_hypothesis_targets=3)

    for module in modules[:5]:  # Limit to first 5
        log(f"Module: {module.category}/{module.name}")
        log("-" * 40)

        # Use AST analyzer to get quick insights
        result = await ast_analyzer.invoke(ASTAnalysisInput(path=module.path))
        structure = result.structure
        if structure:
            # Check for missing type annotations
            code = get_code_preview(module.path)

            suggestions = []
            hypotheses_for_judge = []

            # Check complexity
            if structure.complexity_hints:
                hint = f"Reduce complexity: {', '.join(structure.complexity_hints[:2])}"
                suggestions.append(f"  💡 {hint}")
                hypotheses_for_judge.append(hint)

            # Check for long functions (>50 lines)
            for func in structure.functions[:3]:
                if "long" in str(func).lower():
                    hint = f"Refactor long function: {func.get('name', 'unknown')}"
                    suggestions.append(f"  📏 {hint}")
                    hypotheses_for_judge.append(hint)

            # Check for missing docstrings
            if not structure.docstring:
                suggestions.append("  📝 Missing module docstring")
                hypotheses_for_judge.append("Add module docstring")

            # Persona-grounded suggestions
            if "composable" in facts.persona.values or True:  # Always check composability
                if module.category != "bootstrap":
                    suggestions.append(f"  🔗 Check: Does this compose well via >> operator?")

            # Generic suggestions based on category
            if module.category == "runtime":
                suggestions.append("  ⚡ Runtime modules: Focus on performance and error handling")
            elif "agents" in module.category:
                suggestions.append("  🤖 Agent modules: Ensure clear A → B type signatures")

            if suggestions:
                for s in suggestions[:4]:
                    log(s)

                # Judge top hypotheses against 7 principles
                if hypotheses_for_judge and len(hypotheses_for_judge) > 0:
                    log("  ─ Bootstrap Judge Evaluation ─")
                    for hyp in hypotheses_for_judge[:2]:
                        try:
                            verdict = await judge_hypothesis_against_principles(hyp, module.name)
                            verdict_icon = "✓" if verdict.type == VerdictType.ACCEPT else "⚠" if verdict.type == VerdictType.REVISE else "✗"
                            log(f"    {verdict_icon} [{verdict.type.value}] {hyp[:40]}...")
                        except Exception as e:
                            log(f"    ? Could not judge: {str(e)[:30]}...")
            else:
                log("  ✓ No obvious improvements needed")

        log("")

    log(f"{'=' * 60}")
    log("Bootstrap Self-Improvement Patterns Available:")
    log("  • Judge: Evaluate hypotheses against 7 principles")
    log("  • Fix: Convergence-tracked iteration with entropy")
    log("  • Contradict: Detect tensions in code changes")
    log("  • Ground: Inject persona values into prompts")
    log("")
    log("To run experiments, use:")
    log("  python evolve.py meta --auto-apply  (for self-improvement)")
    log("  python evolve.py full --auto-apply  (for full codebase)")
    log("")


# ============================================================================
# Main
# ============================================================================

def parse_args() -> EvolveCliConfig:
    """Parse command line arguments."""
    config = EvolveCliConfig()

    for arg in sys.argv[1:]:
        if arg.startswith("--target="):
            config.target = arg.split("=")[1]
        elif arg in ["runtime", "agents", "bootstrap", "meta", "all"]:
            config.target = arg
        elif arg.startswith("--mode="):
            config.mode = arg.split("=")[1]
        elif arg in ["test", "status", "suggest", "full"]:
            config.mode = arg
        elif arg == "--dry-run":
            config.dry_run = True
        elif arg == "--no-dry-run":
            config.dry_run = False
        elif arg == "--auto-apply":
            config.auto_apply = True
            config.dry_run = False
        elif arg == "--quick":
            config.quick_mode = True
        elif arg == "--thorough":
            config.quick_mode = False
        elif arg.startswith("--hypotheses="):
            config.hypothesis_count = int(arg.split("=")[1])
        elif arg.startswith("--max-improvements="):
            config.max_improvements_per_module = int(arg.split("=")[1])
        elif arg == "--safe-mode":
            config.safe_mode = True
        elif arg.startswith("--max-iterations="):
            config.max_iterations = int(arg.split("=")[1])
        elif arg.startswith("--convergence="):
            config.convergence_threshold = float(arg.split("=")[1])

    # Mode-specific defaults
    if config.mode == "full":
        config.target = config.target if config.target != "meta" else "all"
        config.quick_mode = False
        config.hypothesis_count = 4
        config.max_improvements_per_module = 4
    elif config.mode == "test":
        # Keep test defaults (fast, single module)
        pass

    return config


async def main() -> None:
    config = parse_args()

    # Show help if needed
    if config.target not in ["runtime", "agents", "bootstrap", "meta", "all"]:
        log(f"Unknown target: {config.target}")
        log("Usage: python evolve.py [MODE] [TARGET] [FLAGS]")
        log("")
        log("Modes (default: test):")
        log("  test                   Fast test on single module (dry-run, quick)")
        log("  status                 Show current evolution status (AI agent friendly)")
        log("  suggest                Show improvement suggestions without running")
        log("  full                   Full evolution run (all modules, thorough)")
        log("")
        log("Targets (default: meta):")
        log("  runtime                Runtime modules")
        log("  agents                 All agent modules")
        log("  bootstrap              Bootstrap modules")
        log("  meta                   evolve.py itself")
        log("  all                    All modules")
        log("")
        log("Flags:")
        log("  --dry-run              Preview improvements without applying (default)")
        log("  --no-dry-run           Disable dry-run mode")
        log("  --auto-apply           Automatically apply improvements that pass tests")
        log("  --quick                Skip dialectic synthesis for faster iteration")
        log("  --thorough             Use full dialectic synthesis")
        log("  --hypotheses=N         Number of hypotheses per module (default: 2)")
        log("  --max-improvements=N   Max improvements per module (default: 1)")
        log("")
        log("Safe self-evolution (Phase 2):")
        log("  --safe-mode            Enable safe self-evolution with fixed-point iteration")
        log("  --max-iterations=N     Max fixed-point iterations (default: 3)")
        log("  --convergence=F        Convergence threshold 0.0-1.0 (default: 0.95)")
        log("")
        log("Examples:")
        log("  python evolve.py                        # Test mode (fast, safe)")
        log("  python evolve.py status                 # Check current status")
        log("  python evolve.py suggest                # Get suggestions")
        log("  python evolve.py meta --auto-apply      # Improve evolve.py")
        log("  python evolve.py full --auto-apply      # Full evolution")
        sys.exit(1)

    # Status mode - show current state
    if config.mode == "status":
        await show_status()
        return

    # Suggest mode - show suggestions without running
    if config.mode == "suggest":
        await show_suggestions(config)
        return

    # Phase 2: Safe self-evolution mode
    if config.safe_mode:
        await run_safe_evolution(config)
        return

    # Test or full mode - run the pipeline
    report = await run_evolution_cli(config)
    log(f"\n{report.summary}")


async def run_safe_evolution(config: EvolveCliConfig) -> None:
    """
    Run safe self-evolution using bootstrap Fix for convergence tracking.

    This mode is specifically for evolving evolve.py and related
    infrastructure. It uses multiple safety layers:

    1. Bootstrap Ground: Inject persona values into evolution
    2. Bootstrap Judge: Pre-filter hypotheses against 7 principles
    3. Bootstrap Fix: Convergence-tracked iteration with entropy budgets
    4. Bootstrap Contradict: Detect tensions between old/new code
    5. Sandbox testing (syntax, types, self-test)
    6. Human approval (for meta-changes)

    Usage:
        python evolve.py meta --safe-mode --dry-run
    """
    log("=" * 60)
    log("SAFE SELF-EVOLUTION MODE (Bootstrap-Enhanced)")
    log("=" * 60)
    log(f"Target: {config.target}")
    log(f"Max iterations: {config.max_iterations}")
    log(f"Convergence threshold: {config.convergence_threshold}")
    log(f"Dry run: {config.dry_run}")
    log("")

    # Get grounded context for persona-aware evolution
    facts = await get_grounded_context()
    log(f"📍 Grounded context: {facts.persona.name}'s preferences")
    log(f"   Values: {', '.join(facts.persona.values[:3])}...")
    log(f"   Style: {facts.persona.communication_style}")
    log("")

    # Create safety config
    safety_config = SafetyConfig(
        read_only=config.dry_run,
        require_syntax_valid=True,
        require_mypy_strict=config.require_type_check,
        require_self_test=True,
        max_iterations=config.max_iterations,
        convergence_threshold=config.convergence_threshold,
        require_human_approval=not config.auto_apply,
    )

    # Determine target files
    base = Path(__file__).parent
    if config.target == "meta":
        targets = [base / "evolve.py"]
    elif config.target == "bootstrap":
        targets = list((base / "bootstrap").glob("*.py"))
    elif config.target == "agents":
        targets = []
        for letter_dir in (base / "agents").iterdir():
            if letter_dir.is_dir() and not letter_dir.name.startswith("_"):
                targets.extend(letter_dir.glob("*.py"))
    else:
        targets = [base / "evolve.py"]

    log(f"Targets: {len(targets)} files")
    for t in targets[:5]:
        log(f"  - {t.name}")
    if len(targets) > 5:
        log(f"  ... and {len(targets) - 5} more")
    log("")

    # Run self-evolution agent on each target
    agent = SelfEvolutionAgent(config=safety_config)

    for target in targets:
        log(f"\n{'='*60}")
        log(f"EVOLVING: {target.name}")
        log(f"{'='*60}")

        if not target.exists():
            log(f"  Skip: file not found")
            continue

        original_code = target.read_text()
        log(f"  Original: {len(original_code.splitlines())} lines")

        result = await agent.invoke(SafeEvolutionInput(
            target=target,
            config=safety_config,
        ))

        if result.success:
            log(f"  Status: SUCCESS")
            log(f"  Converged: {result.converged}")
            log(f"  Iterations: {result.iterations}")
            log(f"  Final similarity: {result.final_similarity:.2%}")

            # Use bootstrap Contradict to detect tensions between old/new code
            if result.evolved_code:
                tension_result = await detect_code_tension(
                    original_code,
                    result.evolved_code,
                    context={"target": target.name, "persona": facts.persona.name},
                )
                if not tension_result.no_tension:
                    log(f"  ⚠️ Tensions detected ({len(tension_result.tensions)}):")
                    for tension in tension_result.tensions[:3]:
                        log(f"    • [{tension.mode.value}] {tension.description[:50]}...")
                else:
                    log(f"  ✓ No tensions detected between old/new code")

            if result.evolved_code and not config.dry_run:
                # Apply the evolved code
                target.write_text(result.evolved_code)
                log(f"  Applied: {len(result.evolved_code.splitlines())} lines")
            elif result.evolved_code:
                log(f"  (dry-run) Would write {len(result.evolved_code.splitlines())} lines")
        else:
            log(f"  Status: FAILED")
            log(f"  Error: {result.error}")

        # Show sandbox results
        if result.sandbox_results:
            log(f"  Sandbox tests: {len(result.sandbox_results)}")
            for i, sr in enumerate(result.sandbox_results, 1):
                status = "PASS" if sr.passed else "FAIL"
                log(f"    [{i}] {status}")
                if not sr.passed and sr.error:
                    log(f"        Error: {sr.error[:80]}...")

    log(f"\n{'='*60}")
    log("SAFE SELF-EVOLUTION COMPLETE")
    log(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
