"""
Domain-specific quality algebras.

Each pilot should define its algebra in this package.
Import them here to register at startup.
"""

# Import domain algebras to trigger registration
from .wasm_survivors import register_wasm_algebra

# Auto-register on import
register_wasm_algebra(overwrite=True)
