"""
Module dependency manifest for agents.d (D-gent).

D-gents provide data/state management with various backends.
They depend on bootstrap for core Agent types.
"""

# kgents modules this module depends on
INTERNAL_DEPS: list[str] = ["bootstrap"]

# External pip packages required at runtime
# Note: numpy is optional (for VectorAgent/SemanticManifold)
# Note: aiosqlite is optional (for SQLiteBackend)
# Note: psycopg2-binary is optional (for PostgreSQLBackend)
# Note: redis is optional (for RedisAgent)
PIP_DEPS: list[str] = [
    "numpy>=1.24.0",  # VectorAgent, SemanticManifold
    "aiosqlite>=0.20.0",  # SQLiteBackend
]
