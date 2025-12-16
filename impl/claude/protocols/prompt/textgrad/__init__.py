"""
TextGRAD: Textual Gradient-based Self-Improvement.

Wave 4 of the Evergreen Prompt System reformation.

Based on the TextGRAD paper: treats natural language feedback as
"textual gradients" that guide prompt improvement.

See: spec/heritage.md Part II, Section 9 (TextGRAD)
See: plans/_continuations/evergreen-wave3-reformation-continuation.md
"""

from .feedback_parser import FeedbackParser, FeedbackTarget, ParsedFeedback
from .gradient import GradientStep, TextualGradient
from .improver import ImprovementResult, TextGRADImprover

__all__ = [
    "TextGRADImprover",
    "ImprovementResult",
    "FeedbackParser",
    "ParsedFeedback",
    "FeedbackTarget",
    "TextualGradient",
    "GradientStep",
]
