"""
Zero Seed LLM Integration: The LLM IS the Galois Adjunction.

> *"The LLM IS the restructurer. The token IS the energy. The loss IS the measure of understanding."*

This module implements the core insight of Zero Seed v2: the LLM literally
instantiates the Galois adjunction (R, C, L) where:

    R: Content -> Modular    (restructure via LLM compression)
    C: Modular -> Content    (reconstitute via LLM generation)
    L: Content x Content -> [0,1]  (loss via LLM semantic comparison)

The LLM's training objective (next-token prediction) IS compression.
Generation IS reconstitution. Comparison IS loss measurement.

Key Concepts:
    - LLMGaloisRestructurer: The (R, C, L) triple via LLM
    - TokenBudget: Thermodynamic energy constraints
    - QualityBudget: Model selection by loss tolerance
    - LatencyBudget: Interactive UX thresholds

Operations:
    - mine_axioms: Extract fixed points (R(C(M)) = M)
    - validate_proof: Check logical coherence via structural loss
    - detect_contradictions: Find super-additive loss
    - synthesize_theorem: Generate low-loss theorems

See: spec/protocols/zero-seed1/llm.md
"""

from __future__ import annotations

from .budgets import (
    LatencyBudget,
    QualityBudget,
    TokenBudget,
    TokenBudgetExceeded,
)
from .operations import (
    AxiomMiner,
    ContradictionDetector,
    ProofValidator,
    TheoremSynthesizer,
)
from .restructurer import LLMGaloisRestructurer
from .types import (
    Alternative,
    Axiom,
    Context,
    Contradiction,
    LossAxis,
    ModularContent,
    Module,
    Proof,
    Style,
    Theorem,
    ValidationResult,
)

__all__ = [
    # Core restructurer
    "LLMGaloisRestructurer",
    # Types
    "Module",
    "ModularContent",
    "Context",
    "Style",
    "LossAxis",
    "Axiom",
    "Proof",
    "Theorem",
    "Contradiction",
    "ValidationResult",
    "Alternative",
    # Budgets
    "TokenBudget",
    "LatencyBudget",
    "QualityBudget",
    "TokenBudgetExceeded",
    # Operations
    "AxiomMiner",
    "ProofValidator",
    "ContradictionDetector",
    "TheoremSynthesizer",
]
