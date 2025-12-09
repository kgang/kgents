"""
P-gents Parsing Strategies

Organized along the Prevention ← → Correction ← → Novel spectrum:

Phase 1: Prevention (Logit-Level Constraint)
- CFGConstrainedParser: Context-free grammar logit masking
- FIMSandwichParser: Fill-in-the-middle sandwich
- TypeGuidedParser: Pydantic type-guided generation

Phase 2: Correction (Stream-Repair & Partial Parsing)
- StackBalancingParser: Stack-balancing stream processor
- StructuralDecouplingParser: Decouple structure from content
- IncrementalParser: Build AST as tokens arrive
- LazyValidationParser: Defer validation until access

Phase 3: Code-as-Schema (Hybrid Prevention + Correction)
- ExecutableCoercionParser: Pydantic with reflection loops
- GraduatedPromptParser: Start strict, relax on failure

Phase 4: Novel / First-Principles Techniques
- DiffBasedParser: Differential diffing (patch strategy)
- AnchorBasedParser: Islands of stability
- VisualValidationParser: Multimodal validation
- ProbabilisticASTParser: Confidence-scored tree nodes
- EvolvingParser: Schema evolution tracking
- EnsembleParser: Multi-model structure + content specialists
"""

from agents.p.strategies.anchor import AnchorBasedParser

__all__ = [
    "AnchorBasedParser",
]
