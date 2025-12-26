"""
TruthFunctor Probes: Five probe types for testing agent behavior.

The five probe types replace the old T-gent types with a unified TruthFunctor interface:
- NullProbe (was MockAgent, FixtureAgent) - EPISTEMIC mode
- ChaosProbe (was FailingAgent, NoiseAgent, etc.) - DIALECTICAL mode
- WitnessProbe (was SpyAgent, CounterAgent, etc.) - CATEGORICAL mode
- JudgeProbe (was JudgeAgent, OracleAgent) - EPISTEMIC mode
- TrustProbe (was TrustGate) - GENERATIVE mode

All probes:
1. Implement TruthFunctor interface (states, actions, transition, reward, verify)
2. Implement DP semantics with state machines
3. Emit PolicyTrace with constitutional scoring
4. Support verification against categorical laws

Integration:
- Use with existing agents via composition (>>)
- All probes are marked with __is_test__ = True
- Compatible with T-gent test patterns
"""

# Core TruthFunctor types (re-export for convenience)
from ..truth_functor import (
    AnalysisMode,
    ComposedProbe,
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthFunctor,
    TruthVerdict,
)
from .chaos_probe import ChaosConfig, ChaosProbe, ChaosType
from .judge_probe import (
    JudgeConfig,
    JudgePhase,
    JudgeProbe,
    JudgmentCriteria,
    JudgmentResult,
    judge_probe,
)

# Concrete probe implementations
from .null_probe import NullConfig, NullProbe, null_probe
from .trust_probe import Proposal, TrustConfig, TrustDecision, TrustProbe, TrustState, trust_probe
from .witness_probe import (
    ASSOCIATIVITY_LAW,
    IDENTITY_LAW,
    Law,
    WitnessConfig,
    WitnessProbe,
    witness_probe,
)

__all__ = [
    # Core TruthFunctor types
    "AnalysisMode",
    "ConstitutionalScore",
    "TruthVerdict",
    "ProbeState",
    "ProbeAction",
    "TraceEntry",
    "PolicyTrace",
    "TruthFunctor",
    "ComposedProbe",
    # NullProbe (EPISTEMIC)
    "NullProbe",
    "NullConfig",
    "null_probe",
    # WitnessProbe (CATEGORICAL)
    "WitnessProbe",
    "WitnessConfig",
    "Law",
    "IDENTITY_LAW",
    "ASSOCIATIVITY_LAW",
    "witness_probe",
    # JudgeProbe (EPISTEMIC)
    "JudgeProbe",
    "JudgeConfig",
    "JudgmentCriteria",
    "JudgmentResult",
    "JudgePhase",
    "judge_probe",
    # TrustProbe (GENERATIVE)
    "TrustProbe",
    "TrustConfig",
    "TrustState",
    "Proposal",
    "TrustDecision",
    "trust_probe",
    # ChaosProbe (DIALECTICAL)
    "ChaosProbe",
    "ChaosConfig",
    "ChaosType",
]
