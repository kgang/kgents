"""
kgents Reference Implementation - Claude + OpenRouter Runtime

This is the reference implementation of the kgents specification,
using Claude as the primary LLM with OpenRouter as the routing layer.

Structure:
    impl/claude-openrouter/
    ├── bootstrap/      # The 7 irreducible primitives
    ├── agents/         # The 5 genera: A, B, C, H, K
    └── runtime/        # LLM-backed agent execution

Usage:
    from impl.claude_openrouter.bootstrap import (
        Id, Compose, Judge, Ground, Contradict, Sublate, Fix
    )

    # Build pipelines
    pipeline = validate >> transform >> persist

    # Ground facts
    facts = await Ground().invoke(None)

    # Iterate to stability
    result = await fix(transform=step, initial=state)

See spec/ for the conceptual specification.
"""

from .bootstrap import *

__version__ = "0.1.0"
