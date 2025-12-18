/**
 * Semantic Icons Constants
 *
 * Per visual-system.md: "kgents uses Lucide icons exclusively for semantic iconography."
 * This file provides icon mappings for all semantic contexts.
 *
 * IMPORTANT: Use these constants instead of emoji in kgents-authored copy.
 *
 * @see docs/creative/visual-system.md
 * @see spec/protocols/os-shell.md
 */

import {
  // Phase/Action icons
  Eye,
  Zap,
  MessageCircle,
  ClipboardList,
  Search,
  Wrench,
  Cog,
  TestTube,
  BarChart3,
  BookOpen,
  Link,
  Target,
  GraduationCap,
  Microscope,
  // Status icons
  AlertTriangle,
  XCircle,
  CheckCircle,
  Info,
  Clock,
  CircleDot,
  // Control icons
  Play,
  Pause,
  RefreshCw,
  User,
  Settings,
  // Park/Archetype icons
  Sparkles,
  Cloud,
  Building2,
  Star,
  Swords,
  Heart,
  Bird, // Using Bird for Sage (Owl not available in Lucide)
  // Builder icons
  Compass,
  Hammer,
  // Infrastructure icons
  Box,
  Monitor,
  Server,
  Database,
  HardDrive,
  Mail,
  Wind,
  Circle,
  // Other semantic icons
  FileText,
  MapPin,
  Lock,
  Wifi,
  HelpCircle,
  // Garden/Season icons
  Moon,
  Sprout,
  Flower2,
  Wheat,
  Leaf,
  // Tending verb icons
  Scissors,
  GitBranch,
  Droplets,
  RotateCw,
  Hourglass,
  // Brain/visualization icons
  Network,
  LayoutGrid,
  type LucideIcon,
} from 'lucide-react';

// =============================================================================
// Phase Icons (Development Lifecycle)
// =============================================================================

/**
 * N-Phase development cycle icons.
 */
export const PHASE_ICONS: Record<string, LucideIcon> = {
  PLAN: ClipboardList,
  RESEARCH: Search,
  DEVELOP: Wrench,
  STRATEGIZE: Target,
  'CROSS-SYNERGIZE': Link,
  IMPLEMENT: Cog,
  QA: Microscope,
  TEST: TestTube,
  EDUCATE: GraduationCap,
  MEASURE: BarChart3,
  REFLECT: BookOpen,
  // Alternative names
  UNDERSTAND: Eye,
  ACT: Zap,
  // Gardener phases
  SENSE: Eye,
} as const;

/**
 * Gardener session phase icons.
 */
export const GARDENER_PHASE_ICONS: Record<string, LucideIcon> = {
  SENSE: Eye,
  ACT: Zap,
  REFLECT: MessageCircle,
} as const;

/**
 * Citizen polynomial phase icons.
 */
export const CITIZEN_PHASE_ICONS: Record<string, LucideIcon> = {
  IDLE: CircleDot,
  SOCIALIZING: MessageCircle,
  WORKING: Wrench,
  REFLECTING: BookOpen,
  RESTING: Cloud,
} as const;

// =============================================================================
// Builder Icons (Workshop)
// =============================================================================

/**
 * Builder archetype icons.
 */
export const BUILDER_ICONS_LUCIDE: Record<string, LucideIcon> = {
  Scout: Compass,
  Sage: GraduationCap,
  Spark: Zap,
  Steady: Hammer,
  Sync: Link,
} as const;

// =============================================================================
// Park Icons (Punchdrunk Park)
// =============================================================================

/**
 * Crisis phase icons.
 */
export const CRISIS_PHASE_ICONS: Record<string, LucideIcon> = {
  NORMAL: CheckCircle,
  INCIDENT: AlertTriangle,
  RESPONSE: Zap,
  RECOVERY: RefreshCw,
} as const;

/**
 * Timer status icons (using text symbols for now since these are badge-like).
 * Consider using Badge components instead.
 */
export const TIMER_STATUS_ICONS: Record<string, LucideIcon> = {
  PENDING: Circle,
  ACTIVE: Play,
  WARNING: AlertTriangle,
  CRITICAL: XCircle,
  EXPIRED: XCircle,
  COMPLETED: CheckCircle,
  PAUSED: Pause,
} as const;

/**
 * Mask archetype icons.
 */
export const MASK_ARCHETYPE_ICONS: Record<string, LucideIcon> = {
  TRICKSTER: Sparkles,
  DREAMER: Cloud,
  SKEPTIC: Search,
  ARCHITECT: Building2,
  CHILD: Star,
  SAGE: Bird,  // Using Bird since Owl not available in Lucide
  WARRIOR: Swords,
  HEALER: Heart,
} as const;

// =============================================================================
// Infrastructure Icons (GestaltLive)
// =============================================================================

/**
 * Infrastructure entity kind icons.
 */
export const INFRA_ENTITY_ICONS: Record<string, LucideIcon> = {
  namespace: Box,
  node: Monitor,
  pod: Server,
  service: Link,
  deployment: Play,
  container: Box,
  nats_subject: Mail,
  nats_stream: Wind,
  database: Database,
  volume: HardDrive,
  custom: Cog,
} as const;

/**
 * Event severity icons.
 */
export const SEVERITY_ICONS: Record<string, LucideIcon> = {
  info: Info,
  warning: AlertTriangle,
  error: XCircle,
  critical: AlertTriangle,
} as const;

// =============================================================================
// Status Icons (General)
// =============================================================================

/**
 * General status icons.
 */
export const STATUS_ICONS = {
  success: CheckCircle,
  warning: AlertTriangle,
  error: XCircle,
  info: Info,
  loading: RefreshCw,
  pending: Clock,
} as const;

/**
 * Error type icons.
 */
export const ERROR_ICONS: Record<string, LucideIcon> = {
  network: Wifi,
  notfound: MapPin,
  permission: Lock,
  timeout: Clock,
  validation: FileText,
  unknown: HelpCircle,
} as const;

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get phase icon by name with fallback.
 */
export function getPhaseIcon(phase: string): LucideIcon {
  return PHASE_ICONS[phase.toUpperCase()] ?? CircleDot;
}

/**
 * Get builder icon by archetype with fallback.
 */
export function getBuilderIcon(archetype: string): LucideIcon {
  return BUILDER_ICONS_LUCIDE[archetype] ?? User;
}

/**
 * Get crisis phase icon with fallback.
 */
export function getCrisisPhaseIcon(phase: string): LucideIcon {
  return CRISIS_PHASE_ICONS[phase.toUpperCase()] ?? CircleDot;
}

/**
 * Get mask archetype icon with fallback.
 */
export function getMaskArchetypeIcon(archetype: string): LucideIcon {
  return MASK_ARCHETYPE_ICONS[archetype.toUpperCase()] ?? Sparkles;
}

/**
 * Get infrastructure entity icon with fallback.
 */
export function getInfraEntityIcon(kind: string): LucideIcon {
  return INFRA_ENTITY_ICONS[kind] ?? Box;
}

/**
 * Get severity icon with fallback.
 */
export function getSeverityIcon(severity: string): LucideIcon {
  return SEVERITY_ICONS[severity] ?? Info;
}

// =============================================================================
// Garden Icons (Seasons and Tending Verbs)
// =============================================================================

/**
 * Garden season icons.
 */
export const SEASON_ICONS: Record<string, LucideIcon> = {
  DORMANT: Moon,
  SPROUTING: Sprout,
  BLOOMING: Flower2,
  HARVEST: Wheat,
  COMPOSTING: Leaf,
} as const;

/**
 * Tending verb icons.
 */
export const VERB_ICONS: Record<string, LucideIcon> = {
  OBSERVE: Eye,
  PRUNE: Scissors,
  GRAFT: GitBranch,
  WATER: Droplets,
  ROTATE: RotateCw,
  WAIT: Hourglass,
} as const;

/**
 * Get season icon with fallback.
 */
export function getSeasonIcon(season: string): LucideIcon {
  return SEASON_ICONS[season.toUpperCase()] ?? Sprout;
}

/**
 * Get tending verb icon with fallback.
 */
export function getVerbIcon(verb: string): LucideIcon {
  return VERB_ICONS[verb.toUpperCase()] ?? Eye;
}

// =============================================================================
// Visualization Action Icons
// =============================================================================

/**
 * Icons for FloatingActions in visualizations.
 * Use these instead of emoji strings.
 */
export const ACTION_ICONS = {
  refresh: RefreshCw,
  settings: Settings,
  capture: Sparkles,
  topology: Network,
  panels: LayoutGrid,
  chart: BarChart3,
} as const;
