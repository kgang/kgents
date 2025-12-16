"""
Artisans: The craftspeople of Tiny Atelier.

Each artisan has a unique specialty and personality.
All share the streaming-first architecture.
"""

from agents.atelier.artisans.archivist import Archivist
from agents.atelier.artisans.calligrapher import Calligrapher
from agents.atelier.artisans.cartographer import Cartographer

# Registry for CLI lookup
ARTISAN_REGISTRY: dict[str, type] = {
    "calligrapher": Calligrapher,
    "cartographer": Cartographer,
    "archivist": Archivist,
}


def get_artisan(name: str) -> type | None:
    """Get artisan class by name."""
    return ARTISAN_REGISTRY.get(name.lower())


def list_artisans() -> list[str]:
    """List all available artisan names."""
    return list(ARTISAN_REGISTRY.keys())


__all__ = [
    "Calligrapher",
    "Cartographer",
    "Archivist",
    "ARTISAN_REGISTRY",
    "get_artisan",
    "list_artisans",
]
