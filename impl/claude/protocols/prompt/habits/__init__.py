"""
Habit Encoding: Learn developer patterns from observable signals.

Wave 4 of the Evergreen Prompt System reformation.

Sources (per taste decision):
- Git history: commit patterns, file organization, code style
- Session logs: Claude Code interaction patterns (when available)
- Code patterns: AST analysis of actual code

The HabitEncoder produces a PolicyVector that influences prompt compilation.
"""

from .encoder import HabitEncoder, HabitEncoderConfig, PatternAnalyzer, encode_habits
from .git_analyzer import GitAnalyzerError, GitPattern, GitPatternAnalyzer
from .policy import PolicyVector

# Session and code analyzers are optional imports
try:
    from .session_analyzer import (
        SessionPattern,
        SessionPatternAnalyzer,
        analyze_sessions,
    )
except ImportError:
    SessionPattern = None  # type: ignore
    SessionPatternAnalyzer = None  # type: ignore
    analyze_sessions = None  # type: ignore

try:
    from .code_analyzer import CodePattern, CodePatternAnalyzer, analyze_code
except ImportError:
    CodePattern = None  # type: ignore
    CodePatternAnalyzer = None  # type: ignore
    analyze_code = None  # type: ignore

__all__ = [
    # Core
    "GitPattern",
    "GitPatternAnalyzer",
    "GitAnalyzerError",
    "PolicyVector",
    # Wave 4
    "HabitEncoder",
    "HabitEncoderConfig",
    "PatternAnalyzer",
    "encode_habits",
    # Optional analyzers
    "SessionPattern",
    "SessionPatternAnalyzer",
    "analyze_sessions",
    "CodePattern",
    "CodePatternAnalyzer",
    "analyze_code",
]
