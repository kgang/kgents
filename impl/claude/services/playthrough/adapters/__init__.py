"""
Game Adapters: Implementations of GameAdapter protocol for different games.

Each adapter wraps browser automation (Playwright) and game communication,
providing isolated contexts for parallel playthrough execution.

Available Adapters:
- WasmSurvivorsAdapter: WASM Survivors (Vampire Survivors-like)
"""

from .wasm_survivors import WasmSurvivorsAdapter, WasmSurvivorsFactory

__all__ = [
    "WasmSurvivorsAdapter",
    "WasmSurvivorsFactory",
]
