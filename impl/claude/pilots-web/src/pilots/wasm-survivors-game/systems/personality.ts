/**
 * WASM Survivors - Hornet Personality System
 *
 * The hornet is a MAGNIFICENT BASTARD who KNOWS the score and hunts anyway.
 *
 * From PROTO_SPEC Part VII (The Hornet's Personality):
 * - Never begs, never whines, never seems unfairly treated
 * - KNOWS what this is and does it anyway
 * - Swagger before the fall
 * - Respect for the colony in death
 *
 * This system provides:
 * 1. Animation state machine with personality-aware transitions
 * 2. Kill milestone tracking for voice lines
 * 3. Personality rendering parameters (swagger glow, defiant stance)
 * 4. Witness integration for personality-flavored summaries
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VII)
 * @see systems/contrast.ts (voice lines)
 */

// =============================================================================
// Types - Animation States
// =============================================================================

/**
 * Hornet animation states.
 *
 * Each state has a distinct personality expression:
 * - IDLE_EARLY: Alert, aggressive, hungry
 * - IDLE_LATE: Confident swagger, surveying kills
 * - IDLE_LOW_HP: Still defiant, NOT cowering
 * - HUNTING: Predatory stance, ready to kill
 * - KILL: Satisfying snap
 * - MULTI_KILL: Brief pause, savoring
 * - MASSIVE_KILL: Head tilt, admiring carnage
 * - HIT_REACT: "Really?" shrug, not flinch
 * - DEATH: Acceptance, not despair
 */
export type AnimationState =
  | 'idle_early'     // Waves 1-3: Alert, aggressive
  | 'idle_late'      // Waves 7+: Confident swagger
  | 'idle_low_hp'    // <25% HP: Defiant, not cowering
  | 'hunting'        // Active movement: Predatory
  | 'kill'           // Single kill: Satisfying snap
  | 'multi_kill'     // 3+ kills: Savoring
  | 'massive_kill'   // 6+ kills: Admiring carnage
  | 'hit_react'      // Taking damage: Shrug
  | 'graze'          // Near miss: Brush off
  | 'death';         // Final: Acceptance

/**
 * Animation state configuration.
 */
export interface AnimationConfig {
  state: AnimationState;
  durationMs: number;       // How long state lasts (-1 for indefinite)
  priority: number;         // Higher = harder to interrupt
  nextState: AnimationState | null;  // Auto-transition to this state
  canInterrupt: boolean;    // Can be interrupted by higher priority
}

/**
 * Full personality state.
 */
export interface PersonalityState {
  // Animation
  currentAnimation: AnimationState;
  animationStartTime: number;
  animationQueue: AnimationState[];

  // Kill tracking
  totalKills: number;
  killsThisSecond: number;
  lastKillTime: number;
  killStreak: number;
  maxKillStreak: number;
  killMilestones: number[];  // Reached milestones (10, 25, 50, 100, 200, 300)

  // Graze tracking
  grazeCount: number;
  consecutiveGrazes: number;
  lastGrazeTime: number;

  // Swagger state
  swaggerLevel: number;     // 0-1, builds over time during dominance
  defiance: number;         // 0-1, builds during low HP survival
  acceptance: number;       // 0-1, builds during death sequence

  // Personality moments (for witness)
  quotableLines: string[];  // Lines that were displayed
  personalityMoments: PersonalityMoment[];
}

/**
 * A personality moment for witness system.
 */
export interface PersonalityMoment {
  type: 'swagger' | 'defiance' | 'humor' | 'respect' | 'kill_milestone';
  gameTime: number;
  description: string;
  voiceLine?: string;
}

// =============================================================================
// Constants - Animation Configurations
// =============================================================================

export const ANIMATION_CONFIGS: Record<AnimationState, AnimationConfig> = {
  idle_early: {
    state: 'idle_early',
    durationMs: -1,           // Indefinite
    priority: 10,
    nextState: null,
    canInterrupt: true,
  },
  idle_late: {
    state: 'idle_late',
    durationMs: -1,
    priority: 10,
    nextState: null,
    canInterrupt: true,
  },
  idle_low_hp: {
    state: 'idle_low_hp',
    durationMs: -1,
    priority: 15,             // Slightly higher - low HP is important
    nextState: null,
    canInterrupt: true,
  },
  hunting: {
    state: 'hunting',
    durationMs: -1,
    priority: 20,
    nextState: null,
    canInterrupt: true,
  },
  kill: {
    state: 'kill',
    durationMs: 100,
    priority: 50,
    nextState: 'hunting',
    canInterrupt: true,
  },
  multi_kill: {
    state: 'multi_kill',
    durationMs: 300,
    priority: 60,
    nextState: 'hunting',
    canInterrupt: false,      // Let them savor
  },
  massive_kill: {
    state: 'massive_kill',
    durationMs: 500,
    priority: 70,
    nextState: 'hunting',
    canInterrupt: false,
  },
  hit_react: {
    state: 'hit_react',
    durationMs: 150,
    priority: 40,
    nextState: 'hunting',
    canInterrupt: true,
  },
  graze: {
    state: 'graze',
    durationMs: 200,
    priority: 35,
    nextState: 'hunting',
    canInterrupt: true,
  },
  death: {
    state: 'death',
    durationMs: -1,
    priority: 100,            // Cannot be interrupted
    nextState: null,
    canInterrupt: false,
  },
};

/**
 * Kill milestones that trigger voice lines.
 */
export const KILL_MILESTONES = [10, 25, 50, 100, 200, 300] as const;

/**
 * Kill milestone voice lines.
 */
export const KILL_MILESTONE_LINES: Record<number, string[]> = {
  10: ['Warm-up complete.', 'Finally getting started.'],
  25: ["Now I'm actually trying.", 'A respectable number.'],
  50: ['This will be remembered.', 'Half a hundred souls.'],
  100: ['A hundred souls. And counting.', 'A centuria of corpses.'],
  200: ['They should write songs about this.', 'Two hundred. Not bad.'],
  300: ['I am become death. And I love it.', 'Three hundred. Legendary.'],
};

/**
 * Graze voice lines.
 */
export const GRAZE_LINES = [
  'Almost.',
  'Too slow, little ones.',
  'That all you got?',
  'Close. But not close enough.',
  'Nice try.',
];

/**
 * Low HP voice lines (defiance).
 */
export const LOW_HP_LINES = [
  'Getting interesting.',
  'Now they have my attention.',
  'Pain? I call that motivation.',
  'Is that supposed to hurt?',
  "You'll need more than that.",
];

// =============================================================================
// Factory Functions
// =============================================================================

/**
 * Create initial personality state.
 */
export function createPersonalityState(): PersonalityState {
  return {
    // Animation
    currentAnimation: 'idle_early',
    animationStartTime: 0,
    animationQueue: [],

    // Kill tracking
    totalKills: 0,
    killsThisSecond: 0,
    lastKillTime: 0,
    killStreak: 0,
    maxKillStreak: 0,
    killMilestones: [],

    // Graze tracking
    grazeCount: 0,
    consecutiveGrazes: 0,
    lastGrazeTime: 0,

    // Swagger state
    swaggerLevel: 0,
    defiance: 0,
    acceptance: 0,

    // Personality moments
    quotableLines: [],
    personalityMoments: [],
  };
}

// =============================================================================
// Animation State Machine
// =============================================================================

/**
 * Transition to a new animation state.
 *
 * Respects priority and interruptibility rules.
 */
export function transitionAnimation(
  state: PersonalityState,
  newAnimation: AnimationState,
  gameTime: number
): { state: PersonalityState; transitioned: boolean } {
  const currentConfig = ANIMATION_CONFIGS[state.currentAnimation];
  const newConfig = ANIMATION_CONFIGS[newAnimation];

  // Check if current animation is finished
  const elapsed = gameTime - state.animationStartTime;
  const isFinished = currentConfig.durationMs !== -1 && elapsed >= currentConfig.durationMs;

  // Determine if we can transition
  const canTransition =
    isFinished ||
    (currentConfig.canInterrupt && newConfig.priority >= currentConfig.priority);

  if (!canTransition) {
    return { state, transitioned: false };
  }

  // Transition
  state.currentAnimation = newAnimation;
  state.animationStartTime = gameTime;

  return { state, transitioned: true };
}

/**
 * Update animation state (called each frame).
 *
 * Handles auto-transitions when animations complete.
 */
export function updateAnimationState(
  state: PersonalityState,
  gameTime: number,
  context: {
    wave: number;
    healthFraction: number;
    isMoving: boolean;
  }
): PersonalityState {
  const currentConfig = ANIMATION_CONFIGS[state.currentAnimation];

  // Check if current animation is finished
  const elapsed = gameTime - state.animationStartTime;
  const isFinished = currentConfig.durationMs !== -1 && elapsed >= currentConfig.durationMs;

  // Handle auto-transition
  if (isFinished && currentConfig.nextState) {
    state.currentAnimation = currentConfig.nextState;
    state.animationStartTime = gameTime;
  }

  // Handle idle state selection based on context
  if (
    state.currentAnimation === 'hunting' ||
    state.currentAnimation.startsWith('idle')
  ) {
    const targetIdle = selectIdleState(context);

    // Only transition if not actively moving
    if (!context.isMoving && state.currentAnimation !== targetIdle) {
      transitionAnimation(state, targetIdle, gameTime);
    } else if (context.isMoving && state.currentAnimation !== 'hunting') {
      transitionAnimation(state, 'hunting', gameTime);
    }
  }

  // Update swagger level
  if (context.healthFraction > 0.5 && context.wave >= 4) {
    state.swaggerLevel = Math.min(1, state.swaggerLevel + 0.001);
  }

  // Update defiance
  if (context.healthFraction < 0.25 && context.healthFraction > 0) {
    state.defiance = Math.min(1, state.defiance + 0.002);
  }

  return state;
}

/**
 * Select the appropriate idle state based on context.
 */
function selectIdleState(context: {
  wave: number;
  healthFraction: number;
}): AnimationState {
  // Low HP always takes priority (but still defiant!)
  if (context.healthFraction < 0.25) {
    return 'idle_low_hp';
  }

  // Late game swagger
  if (context.wave >= 7) {
    return 'idle_late';
  }

  // Early game aggressive
  return 'idle_early';
}

// =============================================================================
// Event Handlers
// =============================================================================

/**
 * Handle a kill event.
 *
 * Tracks kill streaks, milestones, and triggers appropriate animations.
 */
export function handleKill(
  state: PersonalityState,
  gameTime: number,
  killCount: number = 1
): { state: PersonalityState; voiceLine?: string; milestone?: number } {
  // Update kill tracking
  state.totalKills += killCount;

  // Track kills per second (for streaks)
  if (gameTime - state.lastKillTime < 1000) {
    state.killsThisSecond += killCount;
    state.killStreak += killCount;
  } else {
    state.killsThisSecond = killCount;
    state.killStreak = killCount;
  }

  state.lastKillTime = gameTime;
  state.maxKillStreak = Math.max(state.maxKillStreak, state.killStreak);

  // Determine animation based on kill count
  let animationToTrigger: AnimationState;
  if (killCount >= 6) {
    animationToTrigger = 'massive_kill';
  } else if (killCount >= 3) {
    animationToTrigger = 'multi_kill';
  } else {
    animationToTrigger = 'kill';
  }

  transitionAnimation(state, animationToTrigger, gameTime);

  // Check for milestones
  let voiceLine: string | undefined;
  let milestone: number | undefined;

  for (const m of KILL_MILESTONES) {
    if (state.totalKills >= m && !state.killMilestones.includes(m)) {
      state.killMilestones.push(m);
      milestone = m;

      // Pick a random line for this milestone
      const lines = KILL_MILESTONE_LINES[m];
      if (lines) {
        voiceLine = lines[Math.floor(Math.random() * lines.length)];
        state.quotableLines.push(voiceLine);
        state.personalityMoments.push({
          type: 'kill_milestone',
          gameTime,
          description: `Reached ${m} kills`,
          voiceLine,
        });
      }
      break; // Only one milestone at a time
    }
  }

  return { state, voiceLine, milestone };
}

/**
 * Handle a graze event (near miss).
 */
export function handleGraze(
  state: PersonalityState,
  gameTime: number
): { state: PersonalityState; voiceLine?: string } {
  state.grazeCount++;

  // Track consecutive grazes
  if (gameTime - state.lastGrazeTime < 2000) {
    state.consecutiveGrazes++;
  } else {
    state.consecutiveGrazes = 1;
  }

  state.lastGrazeTime = gameTime;

  // Trigger graze animation
  transitionAnimation(state, 'graze', gameTime);

  // Voice line on 5+ consecutive grazes
  let voiceLine: string | undefined;
  if (state.consecutiveGrazes >= 5 && state.consecutiveGrazes % 5 === 0) {
    voiceLine = GRAZE_LINES[Math.floor(Math.random() * GRAZE_LINES.length)];
    state.quotableLines.push(voiceLine);
    state.personalityMoments.push({
      type: 'swagger',
      gameTime,
      description: `${state.consecutiveGrazes} consecutive near-misses`,
      voiceLine,
    });
  }

  return { state, voiceLine };
}

/**
 * Handle taking damage.
 */
export function handleDamage(
  state: PersonalityState,
  gameTime: number,
  _damage: number,
  healthAfter: number,
  maxHealth: number
): { state: PersonalityState; voiceLine?: string } {
  // Trigger hit react animation (shrug, not flinch)
  transitionAnimation(state, 'hit_react', gameTime);

  // Reset consecutive grazes
  state.consecutiveGrazes = 0;

  // Voice line if entering low HP for the first time
  let voiceLine: string | undefined;
  const healthFraction = healthAfter / maxHealth;
  const wasHealthy = state.defiance === 0;

  if (healthFraction < 0.25 && wasHealthy) {
    voiceLine = LOW_HP_LINES[Math.floor(Math.random() * LOW_HP_LINES.length)];
    state.quotableLines.push(voiceLine);
    state.personalityMoments.push({
      type: 'defiance',
      gameTime,
      description: 'Entered critical health with defiance',
      voiceLine,
    });
  }

  return { state, voiceLine };
}

/**
 * Handle death.
 */
export function handleDeath(
  state: PersonalityState,
  gameTime: number
): PersonalityState {
  // Trigger death animation (acceptance, not despair)
  transitionAnimation(state, 'death', gameTime);

  // Set acceptance to 1
  state.acceptance = 1;

  // Record the moment
  state.personalityMoments.push({
    type: 'respect',
    gameTime,
    description: 'Faced THE BALL with dignity',
  });

  return state;
}

// =============================================================================
// Rendering Parameters
// =============================================================================

/**
 * Get rendering parameters based on personality state.
 *
 * These affect how the player is drawn in GameCanvas.
 */
export function getPersonalityRenderParams(
  state: PersonalityState,
  gameTime: number
): PersonalityRenderParams {
  const config = ANIMATION_CONFIGS[state.currentAnimation];
  const elapsed = gameTime - state.animationStartTime;
  const progress = config.durationMs > 0 ? Math.min(elapsed / config.durationMs, 1) : 0;

  // Base parameters
  const params: PersonalityRenderParams = {
    // Scale effects
    scale: 1.0,
    scaleX: 1.0,
    scaleY: 1.0,

    // Color effects
    glowColor: '#00D4FF',
    glowIntensity: 0.3,
    colorOverlay: null,
    colorOverlayAlpha: 0,

    // Animation specifics
    rotation: 0,
    bobOffset: 0,
    breathingIntensity: 1.0,

    // Swagger effects
    swaggerGlow: state.swaggerLevel > 0.5,
    defianceFlare: state.defiance > 0.5,
  };

  // Modify based on animation state
  switch (state.currentAnimation) {
    case 'idle_early':
      // Alert, aggressive - subtle forward lean
      params.bobOffset = Math.sin(gameTime / 150) * 2;
      params.breathingIntensity = 1.2;
      break;

    case 'idle_late':
      // Confident swagger - slow sway
      params.bobOffset = Math.sin(gameTime / 400) * 3;
      params.glowIntensity = 0.4 + state.swaggerLevel * 0.2;
      if (state.swaggerLevel > 0.5) {
        params.glowColor = '#FFD700'; // Golden swagger glow
      }
      break;

    case 'idle_low_hp':
      // Defiant - faster breathing but UPRIGHT
      params.breathingIntensity = 1.5;
      params.glowIntensity = 0.5;
      if (state.defiance > 0.5) {
        params.glowColor = '#FF8800'; // Orange defiance glow
      }
      break;

    case 'hunting':
      // Predatory - smooth, focused
      params.breathingIntensity = 1.0;
      break;

    case 'kill':
      // Satisfying snap
      params.scale = 1.0 + (1 - progress) * 0.1;
      params.glowIntensity = 0.5;
      break;

    case 'multi_kill':
      // Savoring - brief pause
      params.scale = 1.05;
      params.glowIntensity = 0.6;
      params.glowColor = '#FFD700';
      break;

    case 'massive_kill':
      // Head tilt, admiring carnage
      params.scale = 1.08;
      params.rotation = Math.sin(progress * Math.PI) * 5 * (Math.PI / 180);
      params.glowIntensity = 0.8;
      params.glowColor = '#FFD700';
      break;

    case 'hit_react':
      // "Really?" shrug - NOT a flinch
      // Brief scale up (surprised) then normal
      params.scale = 1.0 + (1 - progress) * 0.05;
      params.rotation = (1 - progress) * 3 * (Math.PI / 180); // Slight tilt
      break;

    case 'graze':
      // Brush off - casual
      params.glowIntensity = 0.4;
      break;

    case 'death':
      // Acceptance - dignified fade
      params.acceptance = state.acceptance;
      params.glowIntensity = 0.3 * (1 - progress * 0.5);
      params.glowColor = '#CC3333'; // Deep red acceptance
      break;
  }

  return params;
}

/**
 * Rendering parameters for the player sprite.
 */
export interface PersonalityRenderParams {
  // Scale effects
  scale: number;
  scaleX: number;
  scaleY: number;

  // Color effects
  glowColor: string;
  glowIntensity: number;
  colorOverlay: string | null;
  colorOverlayAlpha: number;

  // Animation specifics
  rotation: number;
  bobOffset: number;
  breathingIntensity: number;

  // Special effects
  swaggerGlow?: boolean;
  defianceFlare?: boolean;
  acceptance?: number;
}

// =============================================================================
// Witness Integration
// =============================================================================

/**
 * Generate a personality-flavored run summary for witness.
 *
 * This replaces generic descriptions with personality-aware language.
 */
export function generatePersonalitySummary(state: PersonalityState): string {
  const { totalKills, maxKillStreak, quotableLines, personalityMoments } = state;

  // Build the summary
  const parts: string[] = [];

  // Opening based on kill count
  if (totalKills >= 200) {
    parts.push('A legendary hunt.');
  } else if (totalKills >= 100) {
    parts.push('A hunt worthy of song.');
  } else if (totalKills >= 50) {
    parts.push('A respectable hunt.');
  } else {
    parts.push('A brief hunt.');
  }

  // Kill streak mention
  if (maxKillStreak >= 10) {
    parts.push(`Peak massacre: ${maxKillStreak} kills in rapid succession.`);
  }

  // Personality moments
  const swaggerMoments = personalityMoments.filter(m => m.type === 'swagger').length;
  const defianceMoments = personalityMoments.filter(m => m.type === 'defiance').length;
  const respectMoments = personalityMoments.filter(m => m.type === 'respect').length;

  if (swaggerMoments > 0) {
    parts.push('Swagger was maintained.');
  }
  if (defianceMoments > 0) {
    parts.push('Defiance was shown.');
  }
  if (respectMoments > 0) {
    parts.push('The colony earned respect.');
  }

  // Quotable line if any
  if (quotableLines.length > 0) {
    const randomLine = quotableLines[Math.floor(Math.random() * quotableLines.length)];
    parts.push(`"${randomLine}"`);
  }

  return parts.join(' ');
}

/**
 * Generate death screen flavor text.
 *
 * This replaces the generic "KILLED BY" text with personality-aware language.
 */
export function generateDeathFlavorText(
  state: PersonalityState,
  deathCause: string,
  wave: number
): { title: string; subtitle: string; quote: string } {
  // Title based on wave reached
  let title: string;
  if (wave >= 10) {
    title = 'A MAGNIFICENT END';
  } else if (wave >= 7) {
    title = 'THE HUNT CONCLUDES';
  } else if (wave >= 4) {
    title = 'THE COLONY PREVAILS';
  } else {
    title = 'CUT SHORT';
  }

  // Subtitle based on death cause
  let subtitle: string;
  if (deathCause.includes('ball') || deathCause.includes('BALL')) {
    subtitle = 'The heat claimed its hunter.';
  } else if (deathCause.includes('swarm') || deathCause.includes('SWARM')) {
    subtitle = 'Overwhelmed by coordination.';
  } else {
    subtitle = 'The colony always wins.';
  }

  // Quote - prefer the last quotable line, or use a death line
  let quote: string;
  if (state.quotableLines.length > 0) {
    quote = state.quotableLines[state.quotableLines.length - 1];
  } else if (wave >= 7) {
    quote = 'The colony always wins. ...Respect.';
  } else {
    quote = 'Next time.';
  }

  return { title, subtitle, quote };
}

// =============================================================================
// Exports for External Use
// =============================================================================

export type {
  AnimationState as HornetAnimationState,
  PersonalityState as HornetPersonalityState,
  PersonalityMoment as HornetPersonalityMoment,
  PersonalityRenderParams as HornetRenderParams,
};
