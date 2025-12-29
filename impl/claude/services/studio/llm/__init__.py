"""
LLM-powered functors for the Creative Studio.

This module contains LLM-backed implementations of the studio functors:
- LLMArchaeologyFunctor: Extract patterns from raw materials
- LLMVisionFunctor: Synthesize creative vision from findings + principles
- LLMProductionFunctor: Create assets from vision + requirements
- StudioFeedbackLoop: Self-feedback and self-improvement for creative production
- Critique: Structured critique from the Three Voices
- ImprovementTracker: Track improvement history for learning

These functors use the LLMClient from agents.k.llm to perform
creative generation with self-feedback and iterative refinement.

The Three Voices pattern for self-critique:
    - Adversarial: Technical coherence check
    - Creative: Novelty and interest assessment
    - Advocate: Would Kent be delighted?

Graceful Degradation:
    Use has_llm_credentials() to check if LLM is available before instantiating.
    If no credentials are available, the CreativeStudioService falls back
    to scaffold implementations.

    from services.studio.llm import has_llm_credentials

    if has_llm_credentials():
        # Use LLM-powered functors
        ...
    else:
        # Fall back to scaffold implementations
        ...

Usage:
    from services.studio.llm import (
        has_llm_credentials,
        LLMArchaeologyFunctor,
        LLMVisionFunctor,
        LLMProductionFunctor,
        StudioFeedbackLoop,
    )
    from agents.k.llm import create_llm_client

    if has_llm_credentials():
        llm = create_llm_client()

        # Pattern extraction (archaeology)
        archaeology_functor = LLMArchaeologyFunctor(llm)
        findings = await archaeology_functor.excavate(sources, ArchaeologyFocus.VISUAL)

        # Vision synthesis
        vision_functor = LLMVisionFunctor(llm)
        vision = await vision_functor.synthesize(findings, principles)

        # Asset production
        production_functor = LLMProductionFunctor(llm)
        asset = await production_functor.produce(vision, requirement)

        # Self-feedback and improvement
        feedback = StudioFeedbackLoop(llm)
        critique = await feedback.critique(asset)
        improved_asset, history = await feedback.improve(asset, critique)

See: spec/s-gents/studio.md
"""

# Re-export has_llm_credentials for graceful degradation checks
from agents.k.llm import create_llm_client, has_llm_credentials

from .archaeology import (
    EXCAVATE_SYSTEM_PROMPT,
    EXCAVATE_USER_PROMPT,
    FOCUS_PROMPTS,
    INTERPRET_SYSTEM_PROMPT,
    INTERPRET_USER_PROMPT,
    LENS_DESCRIPTIONS,
    LLMArchaeologyFunctor,
    LLMClientProtocol,
    QualityAssessment,
    create_archaeology_functor,
)
from .feedback import (
    Critique,
    ImprovementTracker,
    StudioFeedbackLoop,
    critique_artifact,
    improve_artifact,
)
from .production import LLMProductionFunctor
from .vision import LLMVisionFunctor, create_vision_functor

__all__ = [
    # Credential check (for graceful degradation)
    "has_llm_credentials",
    "create_llm_client",
    # Archaeology
    "LLMArchaeologyFunctor",
    "LLMClientProtocol",
    "QualityAssessment",
    "create_archaeology_functor",
    "FOCUS_PROMPTS",
    "EXCAVATE_SYSTEM_PROMPT",
    "EXCAVATE_USER_PROMPT",
    "INTERPRET_SYSTEM_PROMPT",
    "INTERPRET_USER_PROMPT",
    "LENS_DESCRIPTIONS",
    # Vision
    "LLMVisionFunctor",
    "create_vision_functor",
    # Production
    "LLMProductionFunctor",
    # Feedback
    "Critique",
    "ImprovementTracker",
    "StudioFeedbackLoop",
    "critique_artifact",
    "improve_artifact",
]
