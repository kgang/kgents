"""
B-gents: Bio/Scientific Discovery

Agents for biological and scientific research—hypothesis generation,
experimental design, and scientific reasoning.

B for Bio, Biology, and Breakthrough.

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
"""

from .hypothesis_engine import (
    HypothesisEngine,
    hypothesis_engine,
    generate_hypotheses,
    quick_hypothesis,
)

from ..types import (
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    Novelty,
)

__all__ = [
    # Agent
    'HypothesisEngine',
    'hypothesis_engine',

    # Convenience functions
    'generate_hypotheses',
    'quick_hypothesis',

    # Types
    'HypothesisInput',
    'HypothesisOutput',
    'Hypothesis',
    'Novelty',
]

# B-gents genus marker
GENUS = 'b'
