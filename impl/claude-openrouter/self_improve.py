"""
Self-Improvement: kgents systematically reviewing and improving itself.

Uses ClaudeCLIRuntime + HypothesisEngine + Judge + Contradict to:
1. Generate improvement hypotheses for each module
2. Judge current implementations against principles
3. Find tensions between spec and impl
4. Synthesize actionable improvements

Usage:
    python self_improve.py [--target runtime|agents|bootstrap|all]
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def log(msg: str = "") -> None:
    """Print with immediate flush for real-time output."""
    print(msg, flush=True)

# Bootstrap imports
from bootstrap import (
    Judge,
    JudgeInput,
    Contradict,
    ContradictInput,
    Sublate,
    make_default_principles,
)
from bootstrap.types import (
    Agent,
    Tension,
    TensionMode,
    Verdict,
    VerdictType,
    HoldTension,
    Synthesis,
)

# Runtime
from runtime import ClaudeCLIRuntime

# Agents
from agents.b.hypothesis import HypothesisEngine, HypothesisInput, HypothesisOutput


# ============================================================================
# Code Analysis Types
# ============================================================================

@dataclass
class CodeModule:
    """A module to analyze."""
    name: str
    path: Path
    content: str
    category: str  # runtime, agents, bootstrap


@dataclass
class ImprovementReport:
    """Report for a single module."""
    module: CodeModule
    hypotheses: HypothesisOutput | None
    verdict: Verdict
    tensions: list[Tension]
    resolutions: list[Synthesis | HoldTension]


# ============================================================================
# Load Modules
# ============================================================================

def load_modules(target: str = "all") -> list[CodeModule]:
    """Load Python modules from impl directory."""
    base = Path(__file__).parent
    modules: list[CodeModule] = []

    targets = {
        "runtime": ["runtime"],
        "agents": ["agents/a", "agents/b", "agents/c", "agents/h", "agents/k"],
        "bootstrap": ["bootstrap"],
        "all": ["runtime", "agents/a", "agents/b", "agents/c", "agents/h", "agents/k", "bootstrap"],
    }

    dirs = targets.get(target, targets["all"])

    for subdir in dirs:
        dir_path = base / subdir
        if not dir_path.exists():
            continue

        for py_file in dir_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            content = py_file.read_text()
            modules.append(CodeModule(
                name=py_file.stem,
                path=py_file,
                content=content,
                category=subdir.split("/")[0],  # runtime, agents, bootstrap
            ))

    return modules


# ============================================================================
# Contradiction Checker for Code Quality
# ============================================================================

def code_quality_check(module: CodeModule, _: Any, mode: TensionMode) -> Tension | None:
    """Check for code quality tensions."""
    content = module.content

    # Tension 1: Missing docstring
    if '"""' not in content and "'''" not in content:
        return Tension(
            mode=TensionMode.AXIOLOGICAL,
            thesis="kgents principle: generative (could be regenerated from spec)",
            antithesis=f"{module.name} has no docstring",
            description=f"Module {module.name} lacks documentation (spec-first violation)",
            severity=0.6,
        )

    # Tension 2: No type hints in function signatures
    import re
    func_pattern = r'def \w+\([^)]*\):'
    typed_pattern = r'def \w+\([^)]*:.*\)'
    funcs = re.findall(func_pattern, content)
    typed = re.findall(typed_pattern, content)

    if funcs and len(typed) < len(funcs) * 0.5:
        return Tension(
            mode=TensionMode.PRAGMATIC,
            thesis="Type hints enable composition",
            antithesis=f"{module.name} has untyped functions",
            description=f"Module {module.name} needs more type annotations for composability",
            severity=0.4,
        )

    # Tension 3: Silent exception handling
    if "except Exception:" in content and "pass" in content:
        return Tension(
            mode=TensionMode.AXIOLOGICAL,
            thesis="Conflicts are data (should be logged)",
            antithesis="Silent exception swallowing found",
            description=f"Module {module.name} has silent exception handling",
            severity=0.7,
        )

    # Tension 4: Long functions (heuristic: >50 lines between def and return)
    lines = content.split("\n")
    in_func = False
    func_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            in_func = True
            func_start = i
        elif in_func and line.strip().startswith("return "):
            if i - func_start > 60:
                return Tension(
                    mode=TensionMode.PRAGMATIC,
                    thesis="Compose, don't concatenate",
                    antithesis=f"Function in {module.name} is >60 lines",
                    description=f"Module {module.name} has a long function (decomposition needed)",
                    severity=0.5,
                )
            in_func = False

    return None


# ============================================================================
# Create Agent Wrapper for Judging
# ============================================================================

@dataclass
class ModuleAgent(Agent[None, None]):
    """Wrap a CodeModule as an Agent for judging."""
    _module: CodeModule

    @property
    def name(self) -> str:
        return self._module.name

    async def invoke(self, _: None) -> None:
        pass


# ============================================================================
# Main Improvement Loop
# ============================================================================

async def analyze_module(
    module: CodeModule,
    runtime: ClaudeCLIRuntime,
    hypothesis_engine: HypothesisEngine,
    judge: Judge,
    contradict: Contradict,
    sublate: Sublate,
    principles,
) -> ImprovementReport:
    """Analyze a single module for improvements."""

    start_time = time.time()
    log(f"\n{'='*60}")
    log(f"ANALYZING: {module.name} ({module.category})")
    log(f"{'='*60}")

    # 1. Generate improvement hypotheses using HypothesisEngine
    log("\n[1] HYPOTHESIS ENGINE: Generating improvement ideas...")
    step_start = time.time()

    # Extract observations from code
    observations = [
        f"Module: {module.name}",
        f"Category: {module.category}",
        f"Lines of code: {len(module.content.split(chr(10)))}",
        f"Has docstring: {'yes' if '\"\"\"' in module.content else 'no'}",
        f"Uses async: {'yes' if 'async def' in module.content else 'no'}",
        f"Has tests: {'no' if 'test_' not in module.name else 'yes'}",
    ]

    # Add specific patterns
    if "# TODO" in module.content or "# FIXME" in module.content:
        observations.append("Contains TODO/FIXME comments (incomplete work)")
    if "raise NotImplementedError" in module.content:
        observations.append("Has NotImplementedError (incomplete implementation)")
    if "import sys" in module.content and "sys.path" in module.content:
        observations.append("Uses sys.path manipulation (packaging issue)")

    hypotheses = None
    try:
        log("      → Calling LLM...")
        result = await runtime.execute(hypothesis_engine, HypothesisInput(
            observations=observations,
            domain="software architecture",
            question=f"What improvements would make {module.name} more robust, composable, and maintainable?",
            constraints=[
                "kgents principles: tasteful, curated, ethical, joy-inducing, composable, heterarchical, generative",
                "Agents are morphisms: A → B",
                "Fix pattern for retries",
                "Conflicts are data (log, don't swallow)",
            ],
        ))
        hypotheses = result.output
        elapsed = time.time() - step_start
        log(f"      ✓ Done in {elapsed:.1f}s")
        log(f"    Generated {len(hypotheses.hypotheses)} hypotheses")
        for i, h in enumerate(hypotheses.hypotheses, 1):
            log(f"    {i}. {h.statement[:80]}...")
    except Exception as e:
        elapsed = time.time() - step_start
        log(f"    ⚠️  Hypothesis generation failed after {elapsed:.1f}s: {e}")

    # 2. Judge the module
    log("\n[2] JUDGE: Evaluating against principles...")
    agent_wrapper = ModuleAgent(_module=module)
    agent_wrapper.__doc__ = module.content[:500]  # First 500 chars as "docs"

    verdict = await judge.invoke(JudgeInput(agent=agent_wrapper, principles=principles))

    if verdict.type == VerdictType.ACCEPT:
        log(f"    ✅ ACCEPT: {verdict.reasons}")
    elif verdict.type == VerdictType.REJECT:
        log(f"    ❌ REJECT: {verdict.reasons}")
    else:
        log(f"    ⚠️  REVISE: {verdict.revisions}")

    # 3. Find tensions
    log("\n[3] CONTRADICT: Finding tensions...")
    tensions: list[Tension] = []

    # Check with our custom code quality checker
    local_contradict = Contradict(checker=code_quality_check)
    tension = await local_contradict.invoke(ContradictInput(a=module, b=None))
    if tension:
        tensions.append(tension)
        log(f"    ⚡ {tension.description} (severity: {tension.severity})")

    if not tensions:
        log("    No tensions found")

    # 4. Resolve tensions
    log("\n[4] SUBLATE: Resolving tensions...")
    resolutions: list[Synthesis | HoldTension] = []

    for t in tensions:
        resolution = await sublate.invoke(t)
        resolutions.append(resolution)

        if isinstance(resolution, HoldTension):
            log(f"    ⏸️  HOLD: {t.description}")
            log(f"       Reason: {resolution.reason}")
        else:
            log(f"    ✅ RESOLVED: {t.description}")
            log(f"       {resolution.resolution_type.value}: {resolution.explanation}")

    total_time = time.time() - start_time
    log(f"\n✓ {module.name} completed in {total_time:.1f}s")

    return ImprovementReport(
        module=module,
        hypotheses=hypotheses,
        verdict=verdict,
        tensions=tensions,
        resolutions=resolutions,
    )


async def run_self_improvement(target: str = "all") -> list[ImprovementReport]:
    """Run the full self-improvement loop."""

    log("="*60)
    log("SELF-IMPROVEMENT: kgents reviewing itself")
    log(f"Target: {target}")
    log("="*60)

    # Initialize
    runtime = ClaudeCLIRuntime(timeout=180.0, max_retries=2)
    hypothesis_engine = HypothesisEngine(hypothesis_count=3, temperature=0.7)
    judge = Judge()
    contradict = Contradict()
    sublate = Sublate()
    principles = make_default_principles()

    # Load modules
    modules = load_modules(target)
    log(f"\nLoaded {len(modules)} modules to analyze")

    # Analyze each module
    reports: list[ImprovementReport] = []
    total = len(modules)

    for i, module in enumerate(modules, 1):
        log(f"\n>>> Progress: {i}/{total} modules <<<")
        try:
            report = await analyze_module(
                module=module,
                runtime=runtime,
                hypothesis_engine=hypothesis_engine,
                judge=judge,
                contradict=contradict,
                sublate=sublate,
                principles=principles,
            )
            reports.append(report)
        except Exception as e:
            log(f"\n⚠️  Error analyzing {module.name}: {e}")

    # Summary
    log("\n" + "="*60)
    log("SELF-IMPROVEMENT SUMMARY")
    log("="*60)

    total_hypotheses = sum(
        len(r.hypotheses.hypotheses) if r.hypotheses else 0
        for r in reports
    )
    total_tensions = sum(len(r.tensions) for r in reports)
    total_held = sum(
        1 for r in reports
        for res in r.resolutions
        if isinstance(res, HoldTension)
    )
    accepts = sum(1 for r in reports if r.verdict.type == VerdictType.ACCEPT)

    log(f"Modules analyzed: {len(reports)}")
    log(f"Hypotheses generated: {total_hypotheses}")
    log(f"Tensions found: {total_tensions}")
    log(f"  - Resolved: {total_tensions - total_held}")
    log(f"  - Held: {total_held}")
    log(f"Verdicts: {accepts}/{len(reports)} ACCEPT")

    # List actionable improvements
    log("\n" + "-"*60)
    log("ACTIONABLE IMPROVEMENTS")
    log("-"*60)

    for report in reports:
        if report.hypotheses and report.hypotheses.hypotheses:
            log(f"\n{report.module.name}:")
            for h in report.hypotheses.hypotheses[:2]:  # Top 2 per module
                log(f"  • {h.statement}")
                if h.falsifiable_by:
                    log(f"    Test: {h.falsifiable_by[0]}")

    # List held tensions requiring human judgment
    held_tensions = [
        (r.module.name, t, res)
        for r in reports
        for t, res in zip(r.tensions, r.resolutions)
        if isinstance(res, HoldTension)
    ]

    if held_tensions:
        log("\n" + "-"*60)
        log("HELD TENSIONS (require human judgment)")
        log("-"*60)
        for name, tension, hold in held_tensions:
            log(f"\n{name}: {tension.description}")
            log(f"  Reason held: {hold.reason}")
            log(f"  Revisit when: {hold.revisit_conditions}")

    return reports


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target.startswith("--target="):
        target = target.split("=")[1]
    elif target.startswith("--"):
        target = target[2:]

    if target not in ["runtime", "agents", "bootstrap", "all"]:
        log(f"Unknown target: {target}")
        log("Usage: python self_improve.py [runtime|agents|bootstrap|all]")
        sys.exit(1)

    asyncio.run(run_self_improvement(target))
