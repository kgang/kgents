"""
Morning Coffee: Liminal Transition Protocol from Rest to Work.

"The musician doesn't start with the hardest passage.
 She tunes, breathes, plays a scale, feels the instrument respond."

The Morning Coffee ritual honors the precious liminal state between
rest and work through four movements:

1. Garden View - "What grew while I slept?"
2. Conceptual Weather - "What's shifting in the atmosphere?"
3. Menu - "What suits my taste this morning?"
4. Fresh Capture - "What's Kent saying before code takes over?"

AGENTESE Path: time.coffee
CLI: kg coffee

See: spec/services/morning-coffee.md
"""

from .capture import (
    CAPTURE_QUESTIONS,
    CaptureQuestion,
    CaptureSession,
    extract_voice_patterns,
    load_recent_voices,
    load_voice,
    save_voice,
    voice_to_anchor,
)
from .circadian import (
    ArchaeologicalVoice,
    CircadianContext,
    CircadianResonance,
    PatternOccurrence,
    ResonanceMatch,
    SerendipityWisdom,
    StratigraphyLayer,
    get_circadian_resonance,
    reset_circadian_resonance,
    set_circadian_resonance,
)
from .core import (
    CoffeeMovementCompleted,
    CoffeeRitualCompleted,
    CoffeeRitualExited,
    CoffeeRitualStarted,
    CoffeeService,
    CoffeeVoiceCaptured,
    get_coffee_service,
    reset_coffee_service,
    set_coffee_service,
)
from .garden import (
    generate_garden_view,
    generate_garden_view_async,
    parse_git_stat,
    parse_now_md,
)
from .menu import (
    classify_challenge,
    extract_todos_from_now,
    extract_todos_from_plans,
    generate_menu,
    generate_menu_async,
)
from .node import (
    COFFEE_AFFORDANCES,
    CoffeeNode,
    get_coffee_node,
    set_coffee_node,
)
from .polynomial import (
    COFFEE_POLYNOMIAL,
    coffee_directions,
    coffee_transition,
)
from .stigmergy import (
    ACCOMPLISHED_REINFORCEMENT,
    PARTIAL_REINFORCEMENT,
    PheromoneDeposit,
    VoiceStigmergy,
    get_voice_stigmergy,
    reset_voice_stigmergy,
    set_voice_stigmergy,
)
from .types import (
    MOVEMENTS,
    ChallengeLevel,
    ChallengeMenu,
    CoffeeOutput,
    CoffeeState,
    ConceptualWeather,
    GardenItem,
    GardenView,
    MenuItem,
    MorningVoice,
    Movement,
    RitualEvent,
    WeatherPattern,
    WeatherType,
)
from .weather import (
    detect_emerging,
    detect_refactoring,
    detect_scaffolding,
    detect_tension,
    generate_weather,
    generate_weather_async,
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
    # Garden generators
    "generate_garden_view",
    "generate_garden_view_async",
    "parse_git_stat",
    "parse_now_md",
    # Weather generators
    "generate_weather",
    "generate_weather_async",
    "detect_refactoring",
    "detect_emerging",
    "detect_scaffolding",
    "detect_tension",
    # Menu generators
    "generate_menu",
    "generate_menu_async",
    "classify_challenge",
    "extract_todos_from_plans",
    "extract_todos_from_now",
    # Capture
    "CaptureSession",
    "CaptureQuestion",
    "CAPTURE_QUESTIONS",
    "save_voice",
    "load_voice",
    "load_recent_voices",
    "voice_to_anchor",
    "extract_voice_patterns",
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
    # Stigmergy
    "VoiceStigmergy",
    "PheromoneDeposit",
    "get_voice_stigmergy",
    "set_voice_stigmergy",
    "reset_voice_stigmergy",
    "ACCOMPLISHED_REINFORCEMENT",
    "PARTIAL_REINFORCEMENT",
    # Circadian (Phase 1 Metabolic)
    "StratigraphyLayer",
    "ArchaeologicalVoice",
    "ResonanceMatch",
    "PatternOccurrence",
    "SerendipityWisdom",
    "CircadianContext",
    "CircadianResonance",
    "get_circadian_resonance",
    "set_circadian_resonance",
    "reset_circadian_resonance",
]
