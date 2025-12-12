"""
Module dependency manifest for agents.l (L-gent).

L-gents provide semantic registry, knowledge curation, and ecosystem connectivity.
They depend on D-gent for persistence and vector storage.
"""

# kgents modules this module depends on
# Note: agents.d transitively requires bootstrap
INTERNAL_DEPS: list[str] = ["agents.d", "agents.a", "bootstrap"]

# External pip packages required at runtime
# These are the L-gent specific deps (D-gent deps are inherited transitively)
PIP_DEPS: list[str] = [
    "aiosqlite>=0.20.0",  # PersistentRegistry
    "numpy>=1.24.0",  # SemanticBrain, VectorAgent
    "psycopg2-binary>=2.9.0",  # PostgreSQL backend (optional but included for container)
]
