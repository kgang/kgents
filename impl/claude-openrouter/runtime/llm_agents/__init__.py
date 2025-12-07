"""
LLM-Backed Agent Implementations

These agents use LLM reasoning instead of heuristics.
"""

from .judge import LLMJudge
from .sublate import LLMSublate
from .contradict import LLMContradict

__all__ = ["LLMJudge", "LLMSublate", "LLMContradict"]
