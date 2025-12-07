"""
tmux Wrapper Agents

Low-level tmux operations wrapped as agents.
Maps zenportal's TmuxService methods to kgents morphisms.

Key agents:
    - TmuxSpawn: Command → TmuxSession
    - TmuxCapture: TmuxSession → OutputLines
    - TmuxSendKeys: (TmuxSession, Keys) → Sent
    - TmuxList: Void → [TmuxSession]
    - TmuxKill: TmuxSession → Killed
"""

from .spawn import TmuxSpawn, spawn_tmux
from .capture import TmuxCapture, capture_output
from .send import TmuxSendKeys, send_keys
from .query import TmuxList, TmuxExists, list_sessions, session_exists

__all__ = [
    'TmuxSpawn', 'spawn_tmux',
    'TmuxCapture', 'capture_output',
    'TmuxSendKeys', 'send_keys',
    'TmuxList', 'TmuxExists', 'list_sessions', 'session_exists',
]
