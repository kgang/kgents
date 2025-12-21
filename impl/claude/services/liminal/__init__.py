"""
Liminal Transition Protocols: Rituals that honor state changes.

The liminal module provides protocols for transitions between states:
- Morning Coffee: Rest → Work
- Pause: Deep Work → Break (future)
- Evening: Work → Rest (future)
- Return: Away → Back (future)

Each protocol follows a movement-based ritual structure that:
1. Captures the state being left
2. Bridges between states gracefully
3. Prepares the state being entered

See: spec/services/morning-coffee.md
"""

from .coffee import (
    COFFEE_AFFORDANCES,
    # State machine
    COFFEE_POLYNOMIAL,
    MOVEMENTS,
    # Menu types
    ChallengeLevel,
    ChallengeMenu,
    CoffeeMovementCompleted,
    # Node
    CoffeeNode,
    CoffeeOutput,
    CoffeeRitualCompleted,
    CoffeeRitualExited,
    # Events
    CoffeeRitualStarted,
    # Service
    CoffeeService,
    CoffeeState,
    CoffeeVoiceCaptured,
    ConceptualWeather,
    # Garden types
    GardenItem,
    GardenView,
    MenuItem,
    # Voice types
    MorningVoice,
    # Movement types
    Movement,
    # Events and outputs
    RitualEvent,
    WeatherPattern,
    # Weather types
    WeatherType,
    coffee_directions,
    coffee_transition,
    get_coffee_node,
    get_coffee_service,
    reset_coffee_service,
    set_coffee_node,
    set_coffee_service,
)

__all__ = [
    # State machine
    "CoffeeState",
    "COFFEE_POLYNOMIAL",
    "coffee_directions",
    "coffee_transition",
    # Events and outputs
    "RitualEvent",
    "CoffeeOutput",
    # Movement types
    "Movement",
    "MOVEMENTS",
    # Garden types
    "GardenItem",
    "GardenView",
    # Weather types
    "WeatherType",
    "WeatherPattern",
    "ConceptualWeather",
    # Menu types
    "ChallengeLevel",
    "MenuItem",
    "ChallengeMenu",
    # Voice types
    "MorningVoice",
    # Service
    "CoffeeService",
    "get_coffee_service",
    "set_coffee_service",
    "reset_coffee_service",
    # Events
    "CoffeeRitualStarted",
    "CoffeeMovementCompleted",
    "CoffeeVoiceCaptured",
    "CoffeeRitualCompleted",
    "CoffeeRitualExited",
    # Node
    "CoffeeNode",
    "get_coffee_node",
    "set_coffee_node",
    "COFFEE_AFFORDANCES",
]
