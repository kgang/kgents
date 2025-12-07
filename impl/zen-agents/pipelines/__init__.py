"""
zen-agents Pipelines

Composed agent pipelines for common workflows.
These demonstrate the core kgents insight:
    "Services are Agents; composition is primary"

Key pipelines:
    - new_session: Full session creation flow
    - session_tick: Per-tick state update
    - config_cascade: 3-tier config resolution
"""

from .new_session import NewSessionPipeline, create_session_pipeline
from .session_tick import SessionTickPipeline, session_tick

__all__ = [
    'NewSessionPipeline', 'create_session_pipeline',
    'SessionTickPipeline', 'session_tick',
]
