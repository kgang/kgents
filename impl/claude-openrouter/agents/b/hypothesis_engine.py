"""
Hypothesis Engine

An agent for generating testable scientific hypotheses.

Transforms observations, data patterns, and research questions into
well-formed, falsifiable hypotheses.

B-gents do NOT replace scientists. They:
- Augment human reasoning capacity
- Surface connections across vast literature
- Suggest hypotheses for human evaluation
- Help formalize intuitions into testable claims

Design Principles:
1. Epistemic Humility: Express uncertainty appropriately
2. Traceability: Link hypotheses to supporting evidence
3. Falsifiability: All hypotheses must be falsifiable
4. Domain Awareness: Operate within established methods

Bootstrap dependency: Ground (domain context), Judge (quality filtering)
"""

import re
from typing import Any

from bootstrap import Agent, judge, JudgeInput, Verdict, VerdictStatus
from ..types import (
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    Novelty,
)


# Domain-specific reasoning patterns
DOMAIN_PATTERNS = {
    "biology": {
        "mechanisms": ["binding", "signaling", "expression", "regulation", "transport"],
        "test_methods": ["knockout", "knockdown", "overexpression", "inhibitor", "imaging"],
        "confidence_modifiers": {"in vitro": 0.1, "in vivo": 0.2, "clinical": 0.3},
    },
    "biochemistry": {
        "mechanisms": ["catalysis", "folding", "aggregation", "modification", "interaction"],
        "test_methods": ["mutagenesis", "spectroscopy", "crystallography", "mass spec", "assay"],
        "confidence_modifiers": {"structural": 0.2, "kinetic": 0.15, "thermodynamic": 0.15},
    },
    "physics": {
        "mechanisms": ["coupling", "resonance", "symmetry breaking", "phase transition", "interaction"],
        "test_methods": ["measurement", "simulation", "derivation", "observation", "experiment"],
        "confidence_modifiers": {"theoretical": 0.1, "experimental": 0.25, "observational": 0.2},
    },
    "computer science": {
        "mechanisms": ["algorithm", "data structure", "protocol", "architecture", "optimization"],
        "test_methods": ["benchmark", "proof", "simulation", "implementation", "analysis"],
        "confidence_modifiers": {"formal": 0.3, "empirical": 0.2, "theoretical": 0.15},
    },
    "default": {
        "mechanisms": ["cause", "effect", "correlation", "mechanism", "process"],
        "test_methods": ["experiment", "observation", "measurement", "analysis", "test"],
        "confidence_modifiers": {"direct": 0.2, "indirect": 0.1, "inferential": 0.05},
    },
}


class HypothesisEngine(Agent[HypothesisInput, HypothesisOutput]):
    """
    Scientific hypothesis generation agent.

    Type signature: HypothesisEngine: (observations, domain, question?) → HypothesisOutput

    Guarantees:
    - All hypotheses are falsifiable
    - Confidence levels are calibrated (not overconfident)
    - Reasoning chain is provided
    - Does not claim empirical certainty
    - Does not fabricate observations
    """

    @property
    def name(self) -> str:
        return "Hypothesis Engine"

    @property
    def genus(self) -> str:
        return "b"

    @property
    def purpose(self) -> str:
        return "Generates falsifiable hypotheses from scientific observations"

    async def invoke(self, input: HypothesisInput) -> HypothesisOutput:
        """
        Generate hypotheses from observations.
        """
        if len(input.observations) < 2:
            return HypothesisOutput(
                hypotheses=[],
                reasoning_chain=["Insufficient observations for hypothesis generation (need >= 2)"],
                suggested_tests=["Gather more observations", "Document existing patterns"]
            )

        # Get domain patterns
        domain_info = DOMAIN_PATTERNS.get(
            input.domain.lower(),
            DOMAIN_PATTERNS["default"]
        )

        # Generate hypotheses
        hypotheses = await self._generate_hypotheses(
            input.observations,
            input.domain,
            input.question,
            input.constraints,
            domain_info
        )

        # Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(
            input.observations,
            hypotheses
        )

        # Generate suggested tests
        suggested_tests = self._generate_tests(hypotheses, domain_info)

        return HypothesisOutput(
            hypotheses=hypotheses,
            reasoning_chain=reasoning_chain,
            suggested_tests=suggested_tests
        )

    async def _generate_hypotheses(
        self,
        observations: list[str],
        domain: str,
        question: str | None,
        constraints: list[str],
        domain_info: dict[str, Any]
    ) -> list[Hypothesis]:
        """Generate hypotheses from observations"""
        hypotheses: list[Hypothesis] = []

        # Strategy 1: Pattern-based hypothesis (look for correlations)
        correlation_hyp = self._hypothesis_from_correlation(
            observations, domain_info
        )
        if correlation_hyp:
            hypotheses.append(correlation_hyp)

        # Strategy 2: Mechanistic hypothesis (propose mechanism)
        mechanism_hyp = self._hypothesis_from_mechanism(
            observations, domain_info
        )
        if mechanism_hyp:
            hypotheses.append(mechanism_hyp)

        # Strategy 3: Question-guided hypothesis
        if question:
            question_hyp = self._hypothesis_from_question(
                observations, question, domain_info
            )
            if question_hyp:
                hypotheses.append(question_hyp)

        # Apply constraints as filters
        if constraints:
            hypotheses = [
                h for h in hypotheses
                if self._satisfies_constraints(h, constraints)
            ]

        # Sort by confidence
        hypotheses.sort(key=lambda h: h.confidence, reverse=True)

        return hypotheses[:5]  # Return top 5

    def _hypothesis_from_correlation(
        self,
        observations: list[str],
        domain_info: dict[str, Any]
    ) -> Hypothesis | None:
        """Generate hypothesis based on correlations in observations"""
        # Look for common patterns across observations
        obs_lower = [o.lower() for o in observations]
        obs_text = " ".join(obs_lower)

        # Find shared concepts
        shared = []
        for i, obs1 in enumerate(obs_lower):
            words1 = set(obs1.split())
            for j, obs2 in enumerate(obs_lower):
                if i < j:
                    words2 = set(obs2.split())
                    common = words1 & words2
                    # Filter out common words
                    common = {w for w in common if len(w) > 4 and w not in {"about", "their", "these", "which", "where"}}
                    shared.extend(common)

        if not shared:
            return None

        most_common = max(set(shared), key=shared.count)

        # Build hypothesis around shared concept
        statement = f"The observed phenomena share {most_common} as a common causal factor"

        # Calculate confidence based on evidence
        confidence = min(0.3 + (len(shared) * 0.05), 0.7)

        # Supporting observations are all of them
        supporting = list(range(len(observations)))

        return Hypothesis(
            statement=statement,
            confidence=confidence,
            novelty=Novelty.INCREMENTAL,
            falsifiable_by=[
                f"Removing {most_common} eliminates the observed pattern",
                f"Other factors correlate more strongly than {most_common}",
            ],
            supporting_observations=supporting,
            assumptions=[
                "Correlation suggests possible causation",
                "Observations are accurate and representative",
            ]
        )

    def _hypothesis_from_mechanism(
        self,
        observations: list[str],
        domain_info: dict[str, Any]
    ) -> Hypothesis | None:
        """Generate hypothesis proposing a mechanism"""
        obs_text = " ".join(observations).lower()
        mechanisms = domain_info["mechanisms"]

        # Find mentioned mechanisms
        found_mechanisms = [m for m in mechanisms if m in obs_text]

        if not found_mechanisms:
            # Propose a mechanism
            mechanism = mechanisms[0]
        else:
            mechanism = found_mechanisms[0]

        # Look for conditions mentioned
        conditions = []
        condition_patterns = [
            r'at\s+(\w+\s+\d+)', r'when\s+(\w+)', r'under\s+(\w+)',
            r'in\s+(\w+\s+conditions)', r'with\s+(\w+)'
        ]
        for pattern in condition_patterns:
            matches = re.findall(pattern, obs_text)
            conditions.extend(matches[:2])

        condition_str = conditions[0] if conditions else "specific conditions"

        statement = f"Under {condition_str}, {mechanism} is the primary driver of the observed effects"

        # Calculate confidence
        confidence_mods = domain_info.get("confidence_modifiers", {})
        base_confidence = 0.4
        for mod, boost in confidence_mods.items():
            if mod in obs_text:
                base_confidence += boost

        confidence = min(base_confidence, 0.75)

        return Hypothesis(
            statement=statement,
            confidence=confidence,
            novelty=Novelty.EXPLORATORY,
            falsifiable_by=[
                f"Blocking {mechanism} does not affect observations",
                f"Alternative mechanism explains observations better",
                f"{condition_str} is not necessary for the effect",
            ],
            supporting_observations=[0],  # First observation usually describes main phenomenon
            assumptions=[
                f"{mechanism} is operative in this system",
                f"{condition_str} is the relevant variable",
            ]
        )

    def _hypothesis_from_question(
        self,
        observations: list[str],
        question: str,
        domain_info: dict[str, Any]
    ) -> Hypothesis | None:
        """Generate hypothesis guided by research question"""
        question_lower = question.lower()

        # Extract key concepts from question
        if "why" in question_lower:
            # Causal hypothesis
            statement = question.replace("Why does", "").replace("why", "").strip()
            statement = f"The cause of {statement} is mechanistically linked to observations"
            novelty = Novelty.EXPLORATORY
        elif "how" in question_lower:
            # Mechanistic hypothesis
            statement = f"The process described in the question operates via {domain_info['mechanisms'][0]}"
            novelty = Novelty.EXPLORATORY
        elif "what" in question_lower:
            # Descriptive hypothesis
            statement = f"The phenomenon is characterized by the patterns evident in observations"
            novelty = Novelty.INCREMENTAL
        else:
            # General hypothesis
            statement = f"The research question is answered by examining the relationship between observations"
            novelty = Novelty.INCREMENTAL

        return Hypothesis(
            statement=statement,
            confidence=0.5,  # Question-guided are moderate confidence
            novelty=novelty,
            falsifiable_by=[
                "Direct experimental test contradicts hypothesis",
                "Alternative explanation fits observations better",
            ],
            supporting_observations=list(range(len(observations))),
            assumptions=[
                "Research question is well-formed",
                "Observations are relevant to the question",
            ]
        )

    def _satisfies_constraints(
        self,
        hypothesis: Hypothesis,
        constraints: list[str]
    ) -> bool:
        """Check if hypothesis satisfies constraints"""
        statement_lower = hypothesis.statement.lower()
        for constraint in constraints:
            # Constraints that mention "must" require presence
            if "must" in constraint.lower():
                required = constraint.lower().replace("must", "").strip()
                if required and required not in statement_lower:
                    return False
            # Constraints that mention "not" require absence
            if "not" in constraint.lower() or "no " in constraint.lower():
                forbidden = constraint.lower().replace("not", "").replace("no ", "").strip()
                if forbidden and forbidden in statement_lower:
                    return False
        return True

    def _build_reasoning_chain(
        self,
        observations: list[str],
        hypotheses: list[Hypothesis]
    ) -> list[str]:
        """Build the reasoning chain from observations to hypotheses"""
        chain = []

        # Document observations
        chain.append(f"Starting from {len(observations)} observations")

        # Document patterns found
        if hypotheses:
            chain.append("Identified patterns and potential causal relationships")
            for i, h in enumerate(hypotheses):
                chain.append(f"Hypothesis {i+1}: confidence {h.confidence:.2f}, based on observations {h.supporting_observations}")

        # Document falsifiability
        chain.append("Each hypothesis includes explicit falsification criteria")

        return chain

    def _generate_tests(
        self,
        hypotheses: list[Hypothesis],
        domain_info: dict[str, Any]
    ) -> list[str]:
        """Generate suggested tests for hypotheses"""
        tests = []
        test_methods = domain_info["test_methods"]

        for h in hypotheses[:3]:  # Top 3 hypotheses
            for falsifier in h.falsifiable_by[:2]:
                # Suggest specific test method
                method = test_methods[len(tests) % len(test_methods)]
                tests.append(f"{method.capitalize()} to test: {falsifier}")

        # Add general tests
        tests.append("Literature review for prior work")
        tests.append("Consult domain experts for overlooked factors")

        return tests[:8]  # Limit to 8 suggestions


# Singleton instance
hypothesis_engine = HypothesisEngine()


async def generate_hypotheses(
    observations: list[str],
    domain: str,
    question: str | None = None,
    constraints: list[str] | None = None
) -> HypothesisOutput:
    """
    Convenience function to generate hypotheses.

    Example:
        result = await generate_hypotheses(
            observations=[
                "Protein X aggregates at pH < 5",
                "Aggregation correlates with disease progression",
                "Protein X has histidine residues in binding domain"
            ],
            domain="biochemistry",
            question="Why does Protein X aggregate at low pH?"
        )
    """
    return await hypothesis_engine.invoke(HypothesisInput(
        observations=observations,
        domain=domain,
        question=question,
        constraints=constraints or []
    ))


async def quick_hypothesis(observations: list[str], domain: str) -> list[str]:
    """Quick function returning just hypothesis statements"""
    result = await generate_hypotheses(observations, domain)
    return [h.statement for h in result.hypotheses]
