"""
Flux Functor: Lifting agents from Discrete State to Continuous Flow.

The Flux Functor transforms agents that process single inputs into
agents that process and produce streams:

    Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]

Key Insight:
    "The noun is a lie. There is only the rate of change."

    Static:  Agent: A → B           (a point transformation)
    Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)

The Four Critiques Addressed:
1. Polling Fallacy → Event-driven (no asyncio.sleep in core)
2. Sink Problem → start() returns AsyncIterator[B]
3. Bypass Problem → invoke() on FLOWING = Perturbation
4. Recurrence Gap → Ouroboric feedback via feedback_fraction

Usage:
    >>> from agents.flux import Flux, FluxConfig
    >>> from agents.flux.sources import from_iterable
    >>>
    >>> # Lift a discrete agent to flux domain
    >>> flux_agent = Flux.lift(my_agent)
    >>>
    >>> # Process a stream
    >>> async for result in flux_agent.start(from_iterable([1, 2, 3])):
    ...     print(result)
    >>>
    >>> # Create living pipelines
    >>> pipeline = flux_a | flux_b | flux_c
    >>> async for result in pipeline.start(source):
    ...     process(result)
"""

# Core types
from .agent import FluxAgent
from .config import FluxConfig
from .errors import (
    FluxBackpressureError,
    FluxEntropyError,
    FluxError,
    FluxPerturbationError,
    FluxPipelineError,
    FluxSourceError,
    FluxStateError,
)
from .functor import Flux, FluxFunctor, FluxLifter, is_flux, lift, unlift
from .metabolism import FluxMetabolism, create_flux_metabolism
from .perturbation import (
    Perturbation,
    await_perturbation,
    create_perturbation,
    is_perturbation,
    unwrap_perturbation,
)
from .pipeline import FluxPipeline, pipeline
from .state import FluxState

__all__ = [
    # State
    "FluxState",
    # Errors
    "FluxError",
    "FluxStateError",
    "FluxEntropyError",
    "FluxBackpressureError",
    "FluxPerturbationError",
    "FluxPipelineError",
    "FluxSourceError",
    # Config
    "FluxConfig",
    # Perturbation
    "Perturbation",
    "is_perturbation",
    "unwrap_perturbation",
    "create_perturbation",
    "await_perturbation",
    # Agent
    "FluxAgent",
    # Functor
    "Flux",
    "FluxFunctor",
    "FluxLifter",
    "lift",
    "unlift",
    "is_flux",
    # Pipeline
    "FluxPipeline",
    "pipeline",
    # Metabolism
    "FluxMetabolism",
    "create_flux_metabolism",
]
