"""
Module dependency manifest for agents.a (A-gent).

A-gents provide abstract architectures and creativity coaching.
They depend on bootstrap for core Agent types.
"""

# kgents modules this module depends on
INTERNAL_DEPS: list[str] = ["bootstrap"]

# External pip packages required at runtime
PIP_DEPS: list[str] = []
