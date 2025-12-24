"""
Witness Crown Jewel as DP Formulation.

The Witness witnesses itself via DP: every tracing decision is itself traced.

This module defines:
- WitnessState: States in the witnessing process
- WitnessAction: Actions the Witness can take
- WitnessFormulation: MDP formulation for optimal tracing

The reward function is based on the 7 principles:
- GENERATIVE: compression_ratio (fewer marks, more value)
- ETHICAL: auditability_score (can we explain decisions?)
- JOY_INDUCING: discovery_potential (interesting patterns)
- COMPOSABLE: trace coherence (marks compose well)
- TASTEFUL: signal-to-noise ratio
- CURATED: intentional selection
- HETERARCHICAL: no fixed hierarchy in marks

See: spec/protocols/witness-primitives.md
See: dp/core/value_agent.py
"""

from dp.jewels.witness.formulation import (
    WitnessAction,
    WitnessContext,
    WitnessFormulation,
    WitnessState,
    create_witness_agent,
    witness_available_actions,
    witness_reward,
    witness_transition,
)

__all__ = [
    "WitnessState",
    "WitnessAction",
    "WitnessContext",
    "WitnessFormulation",
    "create_witness_agent",
    "witness_available_actions",
    "witness_reward",
    "witness_transition",
]
