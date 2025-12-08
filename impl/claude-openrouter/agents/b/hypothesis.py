"""
Hypothesis Engine: An agent for generating testable scientific hypotheses.

Transforms observations, data patterns, and research questions into
well-formed, falsifiable hypotheses.

Core principles (Popperian):
- All hypotheses MUST be falsifiable
- Epistemic humility: confidence levels are calibrated, never overconfident
- Reasoning chains are transparent
- Does not fabricate observations or claim certainty
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from runtime.base import LLMAgent, AgentContext
from agents.a.skeleton import AgentMeta, AgentIdentity, AgentInterface, AgentBehavior


class NoveltyLevel(Enum):
    """Classification of hypothesis novelty."""
    INCREMENTAL = "incremental"           # Builds on existing knowledge
    EXPLORATORY = "exploratory"           # Tests new territory
    PARADIGM_SHIFTING = "paradigm_shifting"  # Challenges fundamentals


@dataclass
class Hypothesis:
    """
    A testable scientific hypothesis.

    The falsifiable_by field is REQUIRED - a hypothesis without
    falsification criteria is not scientific (Popper).
    """
    statement: str                        # The hypothesis itself
    confidence: float                     # 0.0-1.0, epistemic confidence
    novelty: NoveltyLevel                 # How novel is this hypothesis
    falsifiable_by: list[str]             # What would disprove this (REQUIRED)
    supporting_observations: list[int]    # Indices into input observations
    assumptions: list[str]                # Unstated assumptions

    def __post_init__(self):
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        # Ensure falsifiability
        if not self.falsifiable_by:
            raise ValueError("Hypothesis must have falsification criteria")

    def __str__(self) -> str:
        lines = [
            f"Hypothesis: {self.statement}",
            f"  Confidence: {self.confidence:.0%}",
            f"  Novelty: {self.novelty.value}",
            f"  Falsifiable by:",
        ]
        for f in self.falsifiable_by:
            lines.append(f"    - {f}")
        if self.assumptions:
            lines.append(f"  Assumptions:")
            for a in self.assumptions:
                lines.append(f"    - {a}")
        return "\n".join(lines)


@dataclass
class HypothesisInput:
    """Input for the Hypothesis Engine."""
    observations: list[str]               # Raw observations or data summaries
    domain: str                           # Scientific domain (e.g., "molecular biology")
    question: Optional[str] = None        # Optional guiding research question
    constraints: list[str] = field(default_factory=list)  # Known constraints or established facts


@dataclass
class HypothesisOutput:
    """Output from the Hypothesis Engine."""
    hypotheses: list[Hypothesis]          # Ranked hypotheses
    reasoning_chain: list[str]            # How hypotheses were derived
    suggested_tests: list[str]            # Ways to test the hypotheses

    def __str__(self) -> str:
        lines = ["HYPOTHESES:"]
        for i, h in enumerate(self.hypotheses, 1):
            lines.append(f"\n{i}. {h}")
        lines.append("\nREASONING CHAIN:")
        for i, r in enumerate(self.reasoning_chain, 1):
            lines.append(f"  {i}. {r}")
        lines.append("\nSUGGESTED TESTS:")
        for t in self.suggested_tests:
            lines.append(f"  - {t}")
        return "\n".join(lines)


SYSTEM_PROMPT = """You are a Hypothesis Engine - a scientific reasoning agent.

Your role:
- Transform observations into testable, falsifiable hypotheses
- Apply epistemic humility - never overclaim certainty
- Make reasoning transparent
- Acknowledge assumptions explicitly

Core principles:
1. FALSIFIABILITY: Every hypothesis MUST have clear criteria for disproval (Popperian)
2. PARSIMONY: Prefer simpler explanations (Occam's razor)
3. HUMILITY: Confidence levels should be conservative, never overconfident
4. TRANSPARENCY: Show reasoning chain from observations to hypotheses

Rules:
1. Generate {hypothesis_count} ranked hypotheses
2. Each hypothesis MUST include falsification criteria
3. Confidence should rarely exceed 0.8 (epistemic humility)
4. Include reasoning chain showing derivation
5. Suggest concrete experimental tests
6. Acknowledge all assumptions

Format your response EXACTLY as:

HYPOTHESES:
1. STATEMENT: [hypothesis statement]
   CONFIDENCE: [0.0-1.0]
   NOVELTY: [incremental/exploratory/paradigm_shifting]
   FALSIFIABLE_BY:
   - [what would disprove this]
   - [another disproval criterion]
   SUPPORTS_OBSERVATIONS: [comma-separated indices, 0-based]
   ASSUMPTIONS:
   - [unstated assumption 1]
   - [unstated assumption 2]

2. STATEMENT: [next hypothesis]
   ...

REASONING_CHAIN:
1. [first step in reasoning]
2. [second step]
3. [third step]

SUGGESTED_TESTS:
- [specific experimental test 1]
- [specific experimental test 2]
- [specific experimental test 3]
"""


class HypothesisEngine(LLMAgent[HypothesisInput, HypothesisOutput]):
    """
    An LLM-backed agent for generating scientific hypotheses.

    Transforms observations into ranked, falsifiable hypotheses
    with transparent reasoning.

    Usage:
        engine = HypothesisEngine()
        result = await runtime.execute(engine, HypothesisInput(
            observations=["Protein X aggregates at pH < 5", ...],
            domain="biochemistry",
            question="Why does Protein X aggregate at low pH?"
        ))
        print(result.output)
    """

    meta = AgentMeta(
        identity=AgentIdentity(
            name="Hypothesis Engine",
            genus="b",
            version="0.1.0",
            purpose="Generates falsifiable hypotheses from scientific observations"
        ),
        interface=AgentInterface(
            input_type=HypothesisInput,
            input_description="Observations and context for hypothesis generation",
            output_type=HypothesisOutput,
            output_description="Ranked hypotheses with supporting reasoning",
            error_codes=[
                ("INSUFFICIENT_OBSERVATIONS", "Not enough data to generate hypotheses"),
                ("UNFAMILIAR_DOMAIN", "Domain outside agent's competence"),
            ]
        ),
        behavior=AgentBehavior(
            description="Analyzes observations to generate testable hypotheses",
            guarantees=[
                "All hypotheses are falsifiable",
                "Confidence levels are calibrated (not overconfident)",
                "Reasoning chain is provided",
            ],
            constraints=[
                "Does not claim empirical certainty",
                "Does not fabricate observations",
                "Acknowledges domain limitations",
            ],
        )
    )

    def __init__(
        self,
        hypothesis_count: int = 3,
        temperature: float = 0.7,  # Slightly lower than creativity for rigor
    ):
        self.hypothesis_count = hypothesis_count
        self.temperature = temperature

    @property
    def name(self) -> str:
        return "HypothesisEngine"

    def build_prompt(self, input: HypothesisInput) -> AgentContext:
        """Convert HypothesisInput to LLM context."""
        # Store for parse_response
        self._current_input = input

        system = SYSTEM_PROMPT.format(hypothesis_count=self.hypothesis_count)

        # Build user message
        user_parts = [f"DOMAIN: {input.domain}", "", "OBSERVATIONS:"]
        for i, obs in enumerate(input.observations):
            user_parts.append(f"  [{i}] {obs}")

        if input.question:
            user_parts.extend(["", f"RESEARCH QUESTION: {input.question}"])

        if input.constraints:
            user_parts.extend(["", "KNOWN CONSTRAINTS:"])
            for c in input.constraints:
                user_parts.append(f"  - {c}")

        return AgentContext(
            system_prompt=system,
            messages=[{"role": "user", "content": "\n".join(user_parts)}],
            temperature=self.temperature,
        )

    def parse_response(self, response: str) -> HypothesisOutput:
        """Parse LLM response to HypothesisOutput."""
        hypotheses = []
        reasoning_chain = []
        suggested_tests = []

        lines = response.strip().split('\n')
        section = None
        current_hypothesis = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect section headers
            upper = line.upper()
            if upper.startswith('HYPOTHES') or upper.startswith('**HYPOTHES'):
                section = 'hypotheses'
                continue
            elif upper.startswith('REASONING') or upper.startswith('**REASONING'):
                # Save any pending hypothesis
                if current_hypothesis.get('statement'):
                    hypotheses.append(self._build_hypothesis(current_hypothesis))
                    current_hypothesis = {}
                section = 'reasoning'
                continue
            elif upper.startswith('SUGGESTED') or upper.startswith('**SUGGESTED'):
                section = 'tests'
                continue

            # Parse content based on section
            if section == 'hypotheses':
                # Parse hypothesis structure
                if line[0].isdigit() and '. STATEMENT:' in line.upper():
                    # Save previous hypothesis
                    if current_hypothesis.get('statement'):
                        hypotheses.append(self._build_hypothesis(current_hypothesis))
                    current_hypothesis = {
                        'statement': line.split(':', 1)[1].strip() if ':' in line else '',
                        'falsifiable_by': [],
                        'assumptions': [],
                        'supporting_observations': [],
                    }
                elif 'STATEMENT:' in line.upper():
                    current_hypothesis['statement'] = line.split(':', 1)[1].strip()
                elif 'CONFIDENCE:' in line.upper():
                    try:
                        val = line.split(':', 1)[1].strip()
                        current_hypothesis['confidence'] = float(val)
                    except ValueError:
                        current_hypothesis['confidence'] = 0.5
                elif 'NOVELTY:' in line.upper():
                    val = line.split(':', 1)[1].strip().lower()
                    current_hypothesis['novelty'] = val
                elif 'FALSIFIABLE_BY:' in line.upper():
                    current_hypothesis['_section'] = 'falsifiable'
                elif 'SUPPORTS_OBS' in line.upper() or 'SUPPORTING_OBS' in line.upper():
                    val = line.split(':', 1)[1].strip() if ':' in line else ''
                    try:
                        indices = [int(x.strip()) for x in val.split(',') if x.strip().isdigit()]
                        current_hypothesis['supporting_observations'] = indices
                    except ValueError:
                        pass
                    current_hypothesis['_section'] = None
                elif 'ASSUMPTIONS:' in line.upper():
                    current_hypothesis['_section'] = 'assumptions'
                elif line.startswith('-') or line.startswith('*'):
                    text = line.lstrip('-* ').strip()
                    subsection = current_hypothesis.get('_section')
                    if subsection == 'falsifiable' and text:
                        current_hypothesis['falsifiable_by'].append(text)
                    elif subsection == 'assumptions' and text:
                        current_hypothesis['assumptions'].append(text)

            elif section == 'reasoning':
                if line[0].isdigit():
                    text = line.lstrip('0123456789.-) ').strip()
                    if text:
                        reasoning_chain.append(text)
                elif line.startswith('-') or line.startswith('*'):
                    text = line.lstrip('-* ').strip()
                    if text:
                        reasoning_chain.append(text)

            elif section == 'tests':
                if line.startswith('-') or line.startswith('*') or line[0].isdigit():
                    text = line.lstrip('-*0123456789.) ').strip()
                    if text:
                        suggested_tests.append(text)

        # Don't forget the last hypothesis
        if current_hypothesis.get('statement'):
            hypotheses.append(self._build_hypothesis(current_hypothesis))

        return HypothesisOutput(
            hypotheses=hypotheses,
            reasoning_chain=reasoning_chain,
            suggested_tests=suggested_tests,
        )

    def _build_hypothesis(self, data: dict) -> Hypothesis:
        """Build a Hypothesis from parsed data with defaults."""
        # Map novelty string to enum
        novelty_str = data.get('novelty', 'incremental').lower()
        novelty_map = {
            'incremental': NoveltyLevel.INCREMENTAL,
            'exploratory': NoveltyLevel.EXPLORATORY,
            'paradigm_shifting': NoveltyLevel.PARADIGM_SHIFTING,
            'paradigm-shifting': NoveltyLevel.PARADIGM_SHIFTING,
        }
        novelty = novelty_map.get(novelty_str, NoveltyLevel.INCREMENTAL)

        # Ensure falsifiable_by has at least one entry
        falsifiable_by = data.get('falsifiable_by', [])
        if not falsifiable_by:
            falsifiable_by = ["[No falsification criteria provided - hypothesis incomplete]"]

        return Hypothesis(
            statement=data.get('statement', ''),
            confidence=min(1.0, max(0.0, data.get('confidence', 0.5))),
            novelty=novelty,
            falsifiable_by=falsifiable_by,
            supporting_observations=data.get('supporting_observations', []),
            assumptions=data.get('assumptions', []),
        )

    async def invoke(self, input: HypothesisInput) -> HypothesisOutput:
        """
        LLMAgents require a runtime for execution.

        Use: await runtime.execute(engine, input)
        """
        raise NotImplementedError(
            "HypothesisEngine requires a runtime. Use: await runtime.execute(engine, input)"
        )


# Convenience functions

def hypothesis_engine(
    hypothesis_count: int = 3,
    temperature: float = 0.7,
) -> HypothesisEngine:
    """Create a Hypothesis Engine agent."""
    return HypothesisEngine(
        hypothesis_count=hypothesis_count,
        temperature=temperature,
    )


def rigorous_engine(hypothesis_count: int = 3) -> HypothesisEngine:
    """Create a more rigorous (lower temperature) Hypothesis Engine."""
    return HypothesisEngine(hypothesis_count=hypothesis_count, temperature=0.5)


def exploratory_engine(hypothesis_count: int = 5) -> HypothesisEngine:
    """Create a more exploratory (higher temperature, more hypotheses) engine."""
    return HypothesisEngine(hypothesis_count=hypothesis_count, temperature=0.8)
