"""
Evolution Pipeline Stages: Composable agents for each pipeline phase.

Decomposes the monolithic EvolutionPipeline into composable stages:
    EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Incorporate

Each stage is an Agent[I, O] that can be tested and composed independently.

Architecture:
- GroundStage: CodeModule → CodeStructure (AST analysis)
- HypothesisStage: HypothesisInput → list[Hypothesis] (idea generation + filtering)
- ExperimentStage: ExperimentInput → Experiment (code generation + testing)
- JudgeStage: Already exists as CodeJudge
- IncorporateStage: Already exists as IncorporateAgent

This enables composition:
    module >> ground >> hypothesis >> experiment >> judge >> incorporate
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bootstrap.types import Agent

from .ast_analyzer import (
    ASTAnalyzer,
    ASTAnalysisInput,
    CodeStructure,
    generate_targeted_hypotheses,
)
from .experiment import CodeModule, CodeImprovement, Experiment, get_code_preview
from .memory import ImprovementMemory
from .prompts import build_prompt_context, build_improvement_prompt


# ============================================================================
# Stage 1: Ground (AST Analysis)
# ============================================================================


@dataclass(frozen=True)
class GroundInput:
    """Input for ground stage: module to analyze."""

    module: CodeModule


@dataclass(frozen=True)
class GroundOutput:
    """Output from ground stage: AST structure."""

    module: CodeModule
    structure: Optional[CodeStructure]


class GroundStage(Agent[GroundInput, GroundOutput]):
    """
    Ground stage: Analyze module AST structure.

    Morphism: GroundInput → GroundOutput

    Extracts code structure facts (classes, functions, imports) for
    hypothesis generation.
    """

    def __init__(self, max_hypothesis_targets: int = 3):
        self._analyzer = ASTAnalyzer(max_hypothesis_targets=max_hypothesis_targets)
        self._cache: dict[str, Optional[CodeStructure]] = {}

    @property
    def name(self) -> str:
        return "GroundStage"

    async def invoke(self, input: GroundInput) -> GroundOutput:
        """Analyze module AST structure with caching."""
        key = str(input.module.path)

        if key not in self._cache:
            result = await self._analyzer.invoke(
                ASTAnalysisInput(path=input.module.path)
            )
            self._cache[key] = result.structure

        return GroundOutput(module=input.module, structure=self._cache[key])


# ============================================================================
# Stage 2: Hypothesis Generation
# ============================================================================


@dataclass(frozen=True)
class HypothesisStageInput:
    """Input for hypothesis stage: module + AST structure."""

    module: CodeModule
    structure: Optional[CodeStructure]
    hypothesis_count: int = 4
    runtime: Optional[Any] = None  # Optional: for LLM-based hypothesis generation


@dataclass(frozen=True)
class HypothesisStageOutput:
    """Output from hypothesis stage: filtered hypotheses."""

    module: CodeModule
    hypotheses: tuple[str, ...]  # Filtered, ready to experiment
    ast_hypotheses: tuple[str, ...]  # AST-derived
    llm_hypotheses: tuple[str, ...]  # LLM-derived
    filtered_count: int  # How many were filtered by memory


class HypothesisStage(Agent[HypothesisStageInput, HypothesisStageOutput]):
    """
    Hypothesis stage: Generate improvement ideas.

    Morphism: (CodeModule, CodeStructure) → list[Hypothesis]

    Combines:
    1. AST-based hypotheses (fast, deterministic)
    2. LLM-based hypotheses (creative, context-aware)
    3. Memory filtering (avoid rejected ideas)
    """

    def __init__(self, memory: Optional[ImprovementMemory] = None):
        self._memory = memory or ImprovementMemory()
        self._hypothesis_engine: Optional[Any] = None

    @property
    def name(self) -> str:
        return "HypothesisStage"

    def _get_hypothesis_engine(self) -> Any:
        """Lazy instantiation of hypothesis engine."""
        if self._hypothesis_engine is None:
            from agents.b.hypothesis import HypothesisEngine

            self._hypothesis_engine = HypothesisEngine()
        return self._hypothesis_engine

    async def invoke(self, input: HypothesisStageInput) -> HypothesisStageOutput:
        """Generate and filter hypotheses."""
        # Phase 1: AST-based hypotheses (deterministic)
        ast_hypotheses: list[str] = []
        if input.structure:
            ast_hypotheses = generate_targeted_hypotheses(
                input.structure, max_targets=max(2, input.hypothesis_count // 2)
            )

        # Phase 2: LLM-based hypotheses (creative)
        llm_hypotheses: list[str] = []
        if input.runtime:
            llm_hypotheses = await self._generate_llm_hypotheses(
                input.module, input.structure, input.hypothesis_count, input.runtime
            )

        # Phase 3: Memory filtering
        all_hypotheses = ast_hypotheses + llm_hypotheses
        filtered: list[str] = []
        filtered_count = 0

        for h in all_hypotheses:
            # Check if rejected
            rejection = self._memory.was_rejected(input.module.name, h)
            if rejection:
                filtered_count += 1
                continue

            # Check if recently accepted
            if self._memory.was_recently_accepted(input.module.name, h):
                filtered_count += 1
                continue

            filtered.append(h)

        return HypothesisStageOutput(
            module=input.module,
            hypotheses=tuple(filtered),
            ast_hypotheses=tuple(ast_hypotheses),
            llm_hypotheses=tuple(llm_hypotheses),
            filtered_count=filtered_count,
        )

    async def _generate_llm_hypotheses(
        self,
        module: CodeModule,
        structure: Optional[CodeStructure],
        count: int,
        runtime: Any,
    ) -> list[str]:
        """Generate hypotheses using LLM."""
        try:
            from agents.b.hypothesis import HypothesisInput

            code_content = get_code_preview(module.path)
            ast_context = ""
            if structure:
                ast_context = f"""
AST ANALYSIS:
- Classes: {", ".join(c["name"] for c in structure.classes) or "None"}
- Functions: {", ".join(f["name"] for f in structure.functions[:10]) or "None"}
- Imports: {len(structure.imports)} total
"""

            hypothesis_input = HypothesisInput(
                observations=[
                    f"Module: {module.name}",
                    f"Category: {module.category}",
                    ast_context,
                    f"Code preview:\n{code_content}",
                ],
                domain=f"Code improvement for {module.category}/{module.name}",
                question=f"What are {count} specific improvements?",
                constraints=[
                    "Agents are morphisms with clear A → B types",
                    "Composable via >> operator",
                    "Use Fix pattern for iteration/retry",
                    "Tasteful: less is more",
                ],
            )

            engine = self._get_hypothesis_engine()
            result = await runtime.execute(engine, hypothesis_input)

            if hasattr(result.output, "hypotheses"):
                return [h.statement for h in result.output.hypotheses]
        except Exception:
            pass

        return []


# ============================================================================
# Stage 3: Experiment (Code Generation + Testing)
# ============================================================================


@dataclass(frozen=True)
class ExperimentStageInput:
    """Input for experiment stage: module + hypothesis."""

    module: CodeModule
    hypothesis: str
    structure: Optional[CodeStructure]  # For prompt context
    runtime: Any  # Required for LLM code generation
    require_tests_pass: bool = True
    require_type_check: bool = True


@dataclass(frozen=True)
class ExperimentStageOutput:
    """Output from experiment stage: completed experiment."""

    experiment: Optional[Experiment]  # None if generation failed
    generation_error: Optional[str] = None


class ExperimentStage(Agent[ExperimentStageInput, ExperimentStageOutput]):
    """
    Experiment stage: Generate code improvement and test it.

    Morphism: (CodeModule, Hypothesis) → Experiment

    Steps:
    1. Generate code improvement using LLM
    2. Test improvement (syntax, types, tests)
    3. Return experiment with results
    """

    def __init__(self):
        from .experiment import TestAgent

        self._test_agent = TestAgent()

    @property
    def name(self) -> str:
        return "ExperimentStage"

    async def invoke(self, input: ExperimentStageInput) -> ExperimentStageOutput:
        """Run experiment: generate + test improvement."""
        # Generate improvement
        improvement = await self._generate_improvement(
            input.module, input.hypothesis, input.structure, input.runtime
        )

        if not improvement:
            return ExperimentStageOutput(
                experiment=None, generation_error="Failed to generate improvement"
            )

        # Create experiment
        exp_id = f"{input.module.name}_{hash(input.hypothesis) & 0xFFFF:04x}"
        experiment = Experiment(
            id=exp_id,
            module=input.module,
            improvement=improvement,
            hypothesis=input.hypothesis,
        )

        # Test improvement
        from .experiment import TestInput

        test_result = await self._test_agent.invoke(
            TestInput(
                experiment=experiment,
                require_type_check=input.require_type_check,
                require_tests_pass=input.require_tests_pass,
            )
        )

        return ExperimentStageOutput(experiment=test_result.experiment)

    async def _generate_improvement(
        self,
        module: CodeModule,
        hypothesis: str,
        structure: Optional[CodeStructure],
        runtime: Any,
    ) -> Optional[CodeImprovement]:
        """Generate code improvement using LLM with rich prompt context."""
        from runtime.base import AgentContext
        from .experiment import extract_metadata, extract_code

        # Build rich prompt context
        prompt_context = build_prompt_context(module, structure)

        # Use prompt system with error-aware context
        prompt = build_improvement_prompt(
            hypothesis, prompt_context, improvement_type="refactor"
        )

        try:
            agent_context = AgentContext(
                system_prompt="You are a code improvement agent for kgents.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=16000,
            )

            response_text, _ = await runtime.raw_completion(agent_context)
            response = response_text.strip()

            metadata = extract_metadata(response, module.name)
            if metadata is None:
                return None

            code = extract_code(response, module.name)
            if code is None:
                return None

            return CodeImprovement(
                description=metadata.get("description", "No description"),
                rationale=metadata.get("rationale", "No rationale"),
                improvement_type=metadata.get("improvement_type", "refactor"),
                code=code,
                confidence=metadata.get("confidence", 0.5),
                metadata=metadata,
            )

        except Exception:
            return None


# ============================================================================
# Convenience Factories
# ============================================================================


def ground_stage(max_hypothesis_targets: int = 3) -> GroundStage:
    """Create a ground stage agent."""
    return GroundStage(max_hypothesis_targets)


def hypothesis_stage(memory: Optional[ImprovementMemory] = None) -> HypothesisStage:
    """Create a hypothesis stage agent."""
    return HypothesisStage(memory)


def experiment_stage() -> ExperimentStage:
    """Create an experiment stage agent."""
    return ExperimentStage()
