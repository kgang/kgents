"""
Genesis Services — File and K-Block integration for genesis.

Philosophy: "Files are sovereign territory. K-Blocks are rich indexes."

This package provides:
- GenesisPathResolver: Bidirectional path conversion
- Integration with clean_slate_genesis for file writing

See: services/zero_seed/clean_slate_genesis.py
"""

from .path_resolver import GenesisPathResolver

__all__ = ["GenesisPathResolver"]
