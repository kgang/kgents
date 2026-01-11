/**
 * Actualize Mode Types
 *
 * Types for pilot actualization, axiom discovery, and witness tracking.
 *
 * @see TangibleSurface.tsx for main component
 */

// =============================================================================
// Pilot Types
// =============================================================================

export type PilotTier = 'core' | 'domain' | 'meta';

export interface PilotMetadata {
  name: string;
  displayName: string;
  tier: PilotTier;
  personalityTag: string;
  description: string;
  icon?: string;
  color?: string;
}

export interface CustomPilot extends PilotMetadata {
  isCustom: true;
  axioms: EndeavorAxioms;
  createdAt: Date;
}

// =============================================================================
// Axiom Discovery Types
// =============================================================================

export type AxiomDiscoveryStep = 'A1' | 'A2' | 'A3' | 'A4' | 'A5';

export interface EndeavorAxioms {
  endeavor: string;
  A1_success: string; // What does success look like?
  A2_feeling: string; // What do you want to feel?
  A3_nonnegotiable: string; // What's non-negotiable?
  A4_validation: string; // How will you know it's working?
  confirmedAt?: Date;
}

export interface AxiomDiscoveryState {
  step: AxiomDiscoveryStep;
  responses: Partial<EndeavorAxioms>;
  isComplete: boolean;
}

// =============================================================================
// Witness Types
// =============================================================================

export interface WitnessMark {
  id: string;
  action: string;
  context: MarkContext;
  timestamp: Date;
  pilotName: string;
}

export interface MarkContext {
  endeavorId?: string;
  axiomReference?: string;
  derivationLink?: string;
  metadata?: Record<string, unknown>;
}

export interface WitnessTrace {
  id: string;
  marks: WitnessMark[];
  pilotName: string;
  createdAt: Date;
  crystallizedAt?: Date;
}

export interface Crystal {
  id: string;
  traceId: string;
  title: string;
  insight: string;
  axiomReference?: string;
  createdAt: Date;
}

// =============================================================================
// Derivation Types
// =============================================================================

export interface DerivationLink {
  sourceId: string;
  targetPrinciple: string;
  strength: number;
  evidence: string;
}

// =============================================================================
// Component Props
// =============================================================================

export interface PilotGalleryProps {
  pilots: PilotMetadata[];
  customPilots?: CustomPilot[];
  selectedPilot: string | null;
  onSelect: (pilotName: string) => void;
  onNewEndeavor: () => void;
  tierFilter: PilotTier | 'all';
  onTierFilterChange: (tier: PilotTier | 'all') => void;
}

export interface AxiomDiscoveryFlowProps {
  endeavor: string;
  onComplete: (axioms: EndeavorAxioms) => void;
  onCancel: () => void;
}

export interface ActivePilotProps {
  pilot: PilotMetadata | CustomPilot;
  marks: WitnessMark[];
  onMark: (action: string, context: MarkContext) => void;
  onDeactivate: () => void;
}

export interface CompositionChainProps {
  trace: WitnessTrace | null;
  crystals: Crystal[];
  derivationLinks: DerivationLink[];
  onCrystallize?: () => void;
}

// =============================================================================
// Pilot Data
// =============================================================================

export const PILOTS: PilotMetadata[] = [
  {
    name: 'trail-to-crystal-daily-lab',
    displayName: 'Trail to Crystal',
    tier: 'core',
    personalityTag: 'Honest gaps over concealment. Witness, not surveillance.',
    description:
      'Daily lab for capturing witness marks and crystallizing insights. The foundation of all reflection.',
    icon: 'gem',
    color: '#c4a77d',
  },
  {
    name: 'zero-seed-personal-governance-lab',
    displayName: 'Zero Seed',
    tier: 'core',
    personalityTag: 'Your axioms are not what you think. Galois loss reveals them.',
    description:
      'Personal governance lab for discovering and refining your axioms through Galois symmetry breaking.',
    icon: 'seedling',
    color: '#22c55e',
  },
  {
    name: 'wasm-survivors-game',
    displayName: 'WASM Survivors',
    tier: 'domain',
    personalityTag: 'Failure is the clearest signal. Chaos is structure when witnessed.',
    description:
      'Roguelike survival game where your gameplay choices reveal your decision-making axioms.',
    icon: 'gamepad-2',
    color: '#ef4444',
  },
  {
    name: 'rap-coach-practice-lab',
    displayName: 'Rap Coach',
    tier: 'domain',
    personalityTag: 'Flow is mathematics made audible. Rhythm reveals cognition.',
    description: 'Freestyle practice lab with beat matching, rhyme analysis, and flow coaching.',
    icon: 'mic',
    color: '#8b5cf6',
  },
  {
    name: 'sprite-lab-animation-studio',
    displayName: 'Sprite Lab',
    tier: 'domain',
    personalityTag: 'Animation is time made visible. Movement encodes intent.',
    description:
      'Sprite animation studio for creating and composing game assets with categorical composition.',
    icon: 'palette',
    color: '#f59e0b',
  },
  {
    name: 'disney-portal-immersive',
    displayName: 'Disney Portal',
    tier: 'domain',
    personalityTag: 'Stories are structured dreams. Narrative is navigation.',
    description:
      'Immersive storytelling portal for exploring Disney narratives through the kgents lens.',
    icon: 'castle',
    color: '#3b82f6',
  },
  {
    name: 'categorical-foundation-meta',
    displayName: 'Categorical Foundation',
    tier: 'meta',
    personalityTag: 'The map is not the territory, but the category might be.',
    description:
      'Meta-pilot for understanding and composing other pilots through categorical lenses.',
    icon: 'git-branch',
    color: '#ec4899',
  },
];

// =============================================================================
// Tier Configuration
// =============================================================================

export const TIER_CONFIG: Record<PilotTier, { label: string; color: string; description: string }> =
  {
    core: {
      label: 'Core',
      color: '#c4a77d',
      description: 'Foundational pilots for witness and governance',
    },
    domain: {
      label: 'Domain',
      color: '#6b8b6b',
      description: 'Domain-specific pilots for practice and play',
    },
    meta: {
      label: 'Meta',
      color: '#8b7355',
      description: 'Meta-pilots for composition and understanding',
    },
  };

// =============================================================================
// Axiom Discovery Steps
// =============================================================================

export const AXIOM_STEPS: Record<AxiomDiscoveryStep, { question: string; placeholder: string }> = {
  A1: {
    question: 'What does success look like?',
    placeholder: 'Describe your ideal outcome in concrete, observable terms...',
  },
  A2: {
    question: 'What do you want to feel?',
    placeholder: 'The emotional state you want to experience when you succeed...',
  },
  A3: {
    question: "What's non-negotiable?",
    placeholder: 'The constraints or principles you will not compromise on...',
  },
  A4: {
    question: "How will you know it's working?",
    placeholder: "The signals that will tell you you're on track...",
  },
  A5: {
    question: 'Confirm your axioms',
    placeholder: 'Review and confirm your axioms to begin...',
  },
};
