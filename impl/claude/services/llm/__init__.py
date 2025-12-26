"""
LLM Service - Granular LLM Invocation Tracking.

Every LLM call is witnessed with:
- Full request/response
- Causal lineage
- Ripple effects
- Galois loss

See: agents/d/schemas/llm_trace.py
"""

from .tracer import LLMTraceContext, LLMTracer

__all__ = [
    "LLMTracer",
    "LLMTraceContext",
]
