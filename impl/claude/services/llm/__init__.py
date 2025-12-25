"""
LLM Service - Granular LLM Invocation Tracking.

Every LLM call is witnessed with:
- Full request/response
- Causal lineage
- Ripple effects
- Galois loss

See: agents/d/schemas/llm_trace.py
"""

from .tracer import LLMTracer, LLMTraceContext

__all__ = [
    "LLMTracer",
    "LLMTraceContext",
]
