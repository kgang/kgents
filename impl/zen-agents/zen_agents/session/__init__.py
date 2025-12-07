"""
Session Lifecycle Agents

Session agents form the core of zen-agents, managing the full lifecycle:
    create → running → (pause/resume) → completed/failed

Key mappings from research plan:
    - create: SessionConfig → Session
    - detect_state: Session → SessionState (Fix-based polling)
    - pause: Session → PausedSession
    - kill: Session → Killed
"""

from .create import SessionCreate, create_session
from .detect import SessionDetect, detect_state
from .lifecycle import (
    SessionPause, SessionKill, SessionRevive, SessionResume,
    pause_session, kill_session, revive_session, resume_session
)

__all__ = [
    'SessionCreate', 'create_session',
    'SessionDetect', 'detect_state',
    'SessionPause', 'SessionKill', 'SessionRevive', 'SessionResume',
    'pause_session', 'kill_session', 'revive_session', 'resume_session',
]
