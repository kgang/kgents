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
  JEWEL_ICONS,
  JEWEL_TAILWIND_COLORS,
  getJewelColor,
  getJewelIcon,
  type JewelName,
  type JewelColor,
  // @deprecated - use JEWEL_ICONS instead
  JEWEL_EMOJI,
  getJewelEmoji,
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
  // Phase glow effects (park-town-design-overhaul)
  PHASE_GLOW,
  getPhaseGlow,
  type PhaseGlowType,
  // Teaching gradient backgrounds (park-town-design-overhaul)
  TEACHING_GRADIENT,
  getTeachingGradient,
  type TeachingCategory,
  // Edge animation configuration
  EDGE_ANIMATION,
  // Tailwind extensions
  COLOR_TAILWIND_EXTENSIONS,
  // Living Earth palette (Crown Jewels Genesis) - legacy exports from colors.ts
  LIVING_EARTH,
  getLivingEarthColor,
  type LivingEarthColor,
  JEWEL_IDENTITY_COLORS,
} from './colors';

// =============================================================================
// Living Earth Palette (Crown Jewels Genesis) - Full Implementation
// =============================================================================

export {
  // Earth tones
  EARTH,
  type EarthShade,
  getEarthColor,
  getEarthColorByMode,
  // Living greens
  GREEN,
  type GreenShade,
  getGreenColor,
  getGreenColorByMode,
  // Ghibli glow
  GLOW,
  type GlowShade,
  getGlowColor,
  // Dark mode variants
  DARK_EARTH,
  type DarkEarthShade,
  getDarkEarthColor,
  DARK_GREEN,
  type DarkGreenShade,
  getDarkGreenColor,
  // Jewel identity colors
  JEWEL_IDENTITY,
  type JewelName as LivingEarthJewelName,
  getJewelIdentityColor,
  // Semantic mappings
  SEMANTIC_MAPPINGS,
  type SemanticMapping,
  getSemanticMapping,
  // Full palette exports
  LIVING_EARTH_PALETTE,
  LIVING_EARTH_FLAT,
} from './livingEarth';

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
// Semantic Icons
// =============================================================================

export {
  // Phase icons
  PHASE_ICONS,
  GARDENER_PHASE_ICONS,
  CITIZEN_PHASE_ICONS,
  getPhaseIcon,
  // Builder icons
  BUILDER_ICONS_LUCIDE,
  getBuilderIcon,
  // Park icons
  CRISIS_PHASE_ICONS,
  TIMER_STATUS_ICONS,
  MASK_ARCHETYPE_ICONS,
  getCrisisPhaseIcon,
  getMaskArchetypeIcon,
  // Infrastructure icons
  INFRA_ENTITY_ICONS,
  SEVERITY_ICONS,
  getInfraEntityIcon,
  getSeverityIcon,
  // Status icons
  STATUS_ICONS,
  ERROR_ICONS,
  // Garden icons
  SEASON_ICONS,
  VERB_ICONS,
  getSeasonIcon,
  getVerbIcon,
  // Action icons (for FloatingActions)
  ACTION_ICONS,
} from './icons';

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

// =============================================================================
// Town Theme (Agent Town Visualization)
// =============================================================================

export {
  // Colors
  TOWN_COLORS,
  CITIZEN_PHASE_COLORS,
  TOWN_PHASE_COLORS,
  REGION_COLORS,
  type CitizenPhaseName,
  type TownPhaseName,
  type RegionName,
  // Animation
  BREATHING_ANIMATION,
  GROWING_ANIMATION,
  FLOWING_ANIMATION,
  UNFURLING_ANIMATION,
  // Density-aware
  NODE_RADIUS,
  LABEL_SIZE,
  MAX_CITIZENS_VISIBLE,
  EDGE_THICKNESS,
  // 3D theme
  TOWN_THEME_3D,
  // Archetype config
  ARCHETYPE_CONFIG,
  type ArchetypeKey,
  // Full theme
  TOWN_THEME,
  // Helper functions
  getCitizenPhaseColor,
  getTownPhaseColor,
  getRegionColor,
  getArchetypeConfig,
  getBreathingScale,
} from './town';
