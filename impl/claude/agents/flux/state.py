"""
Flux lifecycle states.

The FluxState enum represents all possible states in a FluxAgent's lifecycle.
State transitions follow a specific machine that ensures proper lifecycle
management and enables the Perturbation Principle.

Teaching:
    gotcha: COLLAPSED is TERMINAL - no transitions out. Unlike STOPPED (which
            allows restart via start()), COLLAPSED requires explicit reset()
            to return to DORMANT. Entropy exhaustion = permanent death.
            (Evidence: can_transition_to returns empty set for COLLAPSED)

    gotcha: allows_perturbation() is only True for FLOWING state. DORMANT uses
            direct invoke (not perturbation), PERTURBED rejects (already handling
            one), and terminal states reject entirely. Check state first.
            (Evidence: Structural - allows_perturbation implementation)

    gotcha: DRAINING is a transient state between source exhaustion and STOPPED.
            is_processing() returns True for DRAINING because output buffer may
            still have items. Wait for STOPPED before assuming completion.
            (Evidence: Structural - is_processing includes DRAINING)
"""

from enum import Enum


class FluxState(Enum):
    """
    Lifecycle states for FluxAgent.

    State machine:
        DORMANT ──start()──→ FLOWING ──source exhausted──→ DRAINING ──→ STOPPED
            │                    │                              │
            │                    │ entropy exhausted            │
            │                    ↓                              │
            │               COLLAPSED                           │
            │                                                   │
            └──────────────────stop()───────────────────────────┘

    Perturbation:
        FLOWING ──invoke()──→ PERTURBED ──processed──→ FLOWING

    Key Insight:
        - DORMANT: invoke() works in discrete mode (like a regular agent)
        - FLOWING: invoke() = perturbation (injected into stream)
        This is the Heterarchical Principle realized.
    """

    DORMANT = "dormant"
    """Created but not started. invoke() works in discrete mode."""

    FLOWING = "flowing"
    """Processing stream. invoke() = perturbation."""

    PERTURBED = "perturbed"
    """Currently handling a perturbation (high-priority event)."""

    DRAINING = "draining"
    """Source exhausted, flushing output buffer."""

    STOPPED = "stopped"
    """Explicitly stopped. Can restart."""

    COLLAPSED = "collapsed"
    """Entropy exhausted. Cannot restart without reset."""

    def can_start(self) -> bool:
        """Check if flux can transition to FLOWING from this state."""
        return self in (FluxState.DORMANT, FluxState.STOPPED)

    def is_processing(self) -> bool:
        """Check if flux is actively processing events."""
        return self in (FluxState.FLOWING, FluxState.PERTURBED, FluxState.DRAINING)

    def is_terminal(self) -> bool:
        """Check if flux is in a terminal state."""
        return self in (FluxState.STOPPED, FluxState.COLLAPSED)

    def allows_perturbation(self) -> bool:
        """
        Check if invoke() can be accepted as a perturbation.

        Only FLOWING state accepts perturbations. In DORMANT, invoke()
        works directly. In other states, invoke() raises an error.
        """
        return self == FluxState.FLOWING

    def can_transition_to(self, target: "FluxState") -> bool:
        """
        Check if transition to target state is valid.

        Valid transitions:
        - DORMANT → FLOWING (start)
        - DORMANT → STOPPED (stop before start)
        - FLOWING → PERTURBED (perturbation received)
        - FLOWING → DRAINING (source exhausted)
        - FLOWING → COLLAPSED (entropy exhausted)
        - FLOWING → STOPPED (explicit stop)
        - PERTURBED → FLOWING (perturbation processed)
        - PERTURBED → STOPPED (explicit stop during perturbation)
        - DRAINING → STOPPED (drain complete)
        - STOPPED → FLOWING (restart)
        """
        valid_transitions = {
            FluxState.DORMANT: {FluxState.FLOWING, FluxState.STOPPED},
            FluxState.FLOWING: {
                FluxState.PERTURBED,
                FluxState.DRAINING,
                FluxState.COLLAPSED,
                FluxState.STOPPED,
            },
            FluxState.PERTURBED: {FluxState.FLOWING, FluxState.STOPPED},
            FluxState.DRAINING: {FluxState.STOPPED},
            FluxState.STOPPED: {FluxState.FLOWING},
            FluxState.COLLAPSED: set(),  # Terminal - no transitions out
        }
        return target in valid_transitions.get(self, set())
