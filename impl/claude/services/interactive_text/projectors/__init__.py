"""
Projection functor implementations.

This module contains projection functors that transform meaning tokens
to target-specific renderings:
- CLIProjectionFunctor: Projects to Rich terminal markup
- WebProjectionFunctor: Projects to React element specifications
- JSONProjectionFunctor: Projects to API-friendly JSON structures

Each projector implements the ProjectionFunctor protocol and satisfies
the naturality condition: projecting before state change then applying
target's update equals applying change then projecting.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 2.1, 2.2, 2.4, 2.6
"""

from services.interactive_text.projectors.base import (
    DENSITY_PARAMS,
    CompositionResult,
    DensityParams,
    ProjectionFunctor,
    ProjectionResult,
)
from services.interactive_text.projectors.cli import (
    CLIProjectionFunctor,
    RichMarkup,
)
from services.interactive_text.projectors.json import (
    JSONDocument,
    JSONProjectionFunctor,
    JSONToken,
)
from services.interactive_text.projectors.web import (
    ReactElement,
    WebProjectionFunctor,
)

__all__ = [
    # Base
    "ProjectionFunctor",
    "ProjectionResult",
    "CompositionResult",
    "DensityParams",
    "DENSITY_PARAMS",
    # CLI
    "CLIProjectionFunctor",
    "RichMarkup",
    # Web
    "WebProjectionFunctor",
    "ReactElement",
    # JSON
    "JSONProjectionFunctor",
    "JSONToken",
    "JSONDocument",
]
