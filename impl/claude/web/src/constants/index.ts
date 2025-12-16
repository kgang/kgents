/**
 * Design Token Constants
 *
 * Central export for all kgents design tokens.
 * Includes colors, timing, spacing, and lighting.
 *
 * @see docs/creative/visual-system.md
 * @see docs/creative/motion-language.md
 */

// =============================================================================
// Color System
// =============================================================================

export {
  // Jewel colors and types
  JEWEL_COLORS,
  JEWEL_EMOJI,
  JEWEL_TAILWIND_COLORS,
  getJewelColor,
  getJewelEmoji,
  type JewelName,
  type JewelColor,
} from './jewels';

export {
  // Gray scale
  GRAYS,
  type GrayShade,
  // State colors
  STATE_COLORS,
  getStateColor,
  type StateType,
  // Semantic colors
  SEMANTIC_COLORS,
  getSemanticColor,
  type SemanticMeaning,
  // Surface colors
  DARK_SURFACES,
  DARK_TEXT,
  LIGHT_SURFACES,
  LIGHT_TEXT,
  // Domain-specific colors
  ARCHETYPE_COLORS,
  getArchetypeColor,
  type ArchetypeName,
  PHASE_COLORS,
  type PhaseName,
  // Season colors (Garden)
  SEASON_COLORS,
  getSeasonColor,
  type SeasonName,
  // Builder personality colors
  BUILDER_PERSONALITY_COLORS,
  getBuilderColor,
  type BuilderPersonality,
  // Health colors
  HEALTH_COLORS,
  getHealthColor,
  type HealthLevel,
  // Connection status colors
  CONNECTION_STATUS_COLORS,
  getConnectionStatusColor,
  type ConnectionStatus,
  // Tailwind extensions
  COLOR_TAILWIND_EXTENSIONS,
} from './colors';

// =============================================================================
// Motion & Timing
// =============================================================================

export {
  // Timing constants
  TIMING,
  TIMING_CSS,
  type TimingKey,
  // Easing constants
  EASING,
  EASING_CSS,
  type EasingKey,
  // Stagger utilities
  STAGGER,
  getStaggerDelay,
  // Precomposed transitions
  TRANSITIONS,
  // Keyframe definitions
  KEYFRAMES,
  // Tailwind extensions
  ANIMATION_TAILWIND_EXTENSIONS,
} from './timing';

// =============================================================================
// Voice & Tone Messages
// =============================================================================

export {
  // Loading messages
  LOADING_MESSAGES,
  getLoadingMessage,
  GENERIC_LOADING_MESSAGES,
  // Error messages
  ERROR_TITLES,
  ERROR_SUGGESTIONS,
  getErrorMessage,
  // Empty state messages
  EMPTY_STATE_MESSAGES,
  getEmptyState,
  // Success messages
  SUCCESS_MESSAGES,
  // Button labels
  BUTTON_LABELS,
  // Tooltips
  TOOLTIPS,
} from './messages';

// =============================================================================
// 3D Lighting
// =============================================================================

export {
  // Types
  type IlluminationQuality,
  type ShadowBounds,
  // Shadow map constants
  SHADOW_MAP_SIZE,
  SHADOW_BIAS,
  SHADOW_NORMAL_BIAS,
  SHADOW_RADIUS,
  DEFAULT_SHADOW_BOUNDS,
  // Light intensity constants
  AMBIENT_INTENSITY,
  SUN_INTENSITY,
  FILL_INTENSITY,
  // SSAO constants
  SSAO_ENABLED,
  SSAO_SAMPLES,
  SSAO_RADIUS,
  SSAO_INTENSITY,
  SSAO_COLOR,
  // Bloom constants
  BLOOM_ENABLED,
  BLOOM_INTENSITY,
  BLOOM_THRESHOLD,
  BLOOM_SMOOTHING,
  // Canonical positions
  CANONICAL_SUN_POSITION,
  FILL_LIGHT_POSITIONS,
  // Helper functions
  shadowsEnabled,
  ssaoEnabled,
  bloomEnabled,
  getLightingConfig,
  // Quality descriptions
  QUALITY_DESCRIPTIONS,
} from './lighting';

// =============================================================================
// Forest Theme (Gestalt Organic Visualization)
// =============================================================================

export {
  // Ground colors
  FOREST_GROUND,
  // Plant health
  PLANT_HEALTH,
  getPlantHealth,
  type PlantHealthLevel,
  // Vine colors
  VINE_COLORS,
  // Layer rings
  LAYER_RINGS,
  // Sizing
  PLANT_SIZING,
  VINE_SIZING,
  GROWTH_RINGS,
  // Animation
  BREATHE_ANIMATION,
  FLOW_ANIMATION,
  VIOLATION_ANIMATION,
  // Labels
  LABEL_CONFIG,
  LABEL_COLORS,
  // Scene
  FOREST_SCENE,
  // Full theme object
  FOREST_THEME,
} from './forest';
