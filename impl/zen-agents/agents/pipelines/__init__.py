"""
Pipelines: Composed agents for session lifecycle operations.

Every multi-step operation is a pipeline of agents.

IDIOM: Compose, Don't Concatenate
> If a function does A then B then C, it should BE `A >> B >> C`.
"""

from .create import (
    CreateSessionPipeline,
    ValidateConfig,
    SpawnTmux,
    create_session_pipeline,
)
from .revive import (
    ReviveSessionPipeline,
    ValidateSession,
    revive_session_pipeline,
)
from .clean import (
    CleanSessionPipeline,
    KillTmux,
    CleanupSession,
    clean_session_pipeline,
)

__all__ = [
    # Create
    "CreateSessionPipeline",
    "ValidateConfig",
    "SpawnTmux",
    "create_session_pipeline",
    # Revive
    "ReviveSessionPipeline",
    "ValidateSession",
    "revive_session_pipeline",
    # Clean
    "CleanSessionPipeline",
    "KillTmux",
    "CleanupSession",
    "clean_session_pipeline",
]
