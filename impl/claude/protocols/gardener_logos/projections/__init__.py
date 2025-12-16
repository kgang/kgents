"""
Projections for Gardener-Logos.

Multiple views of the garden state:
- ASCII (CLI)
- JSON (API)
- Three.js config (Web 3D)
"""

from .ascii import project_garden_to_ascii, project_plot_to_ascii
from .json import project_garden_to_json

__all__ = [
    "project_garden_to_ascii",
    "project_plot_to_ascii",
    "project_garden_to_json",
]
