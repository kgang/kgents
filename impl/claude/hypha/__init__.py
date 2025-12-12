"""
The Hypha - Agent as Growing Tip with Active Inference.

The Hypha reimagines the agent as a fungal growing tip that forages
through semantic space, driven by Active Inference (Free Energy minimization).

Core Components:
- FreeEnergyState: Variational Free Energy state
- GenerativeModel: Internal predictive model
- ForageAction: Actions based on Free Energy
- Hypha: The agent as growing tip

Mathematical Foundation:
Active Inference: Agent acts to minimize Free Energy F = Complexity + Inaccuracy

This enables:
- Exploration driven by surprise (high prediction error)
- Exploitation when predictions match (low error, high reward)
- Pruning when exploration yields nothing
- Morphic resonance via shared HolographicField

References:
- Friston, "The Free Energy Principle" (2010)
- Friston et al, "Active Inference: A Process Theory" (2017)
"""

from .foraging import ForageAction
from .free_energy import FreeEnergyState, GenerativeModel
from .hypha import Hypha

__all__ = [
    "FreeEnergyState",
    "GenerativeModel",
    "ForageAction",
    "Hypha",
]
