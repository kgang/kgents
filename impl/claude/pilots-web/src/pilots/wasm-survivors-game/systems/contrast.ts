/**
 * WASM Survivors - Contrast & Arc System
 *
 * Implements the SEVEN CONTRASTS (S4) and ARC GRAMMAR (Part VI) from PROTO_SPEC.
 *
 * The emotional core of the game:
 * - Tracks which contrast poles the player has visited
 * - Manages arc phase transitions (POWER -> FLOW -> CRISIS -> TRAGEDY)
 * - Triggers personality voice lines at key moments
 * - Ensures every run has emotional variety (GD-1: visit 3+ contrasts)
 *
 * Contrast Laws:
 * - GD-1: Every run MUST visit both extremes of at least 3 contrasts
 * - GD-2: Transitions should be *sudden*, not gradual
 * - GD-3: Contrasts compose (you can be "God of Death + Speed + Noise" simultaneously)
 *
 * Arc Validity:
 * - At least ONE peak (moment of highest engagement)
 * - At least ONE valley (moment of lowest engagement)
 * - Definite closure (the arc ENDS, not fades)
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part VI, S4)
 */

import type { GameState } from '../types';

// =============================================================================
// Types - The Seven Contrasts
// =============================================================================

/**
 * The Seven Contrast Poles from S4.
 *
 * Each contrast has two extremes. Quality requires oscillation between them.
 */
export type ContrastPole =
  // Contrast 1: Power
  | 'god_of_death'      // Early game: unstoppable killing machine
  | 'cornered_prey'     // Late game: desperately surviving
  // Contrast 2: Tempo
  | 'speed'             // Combat: constant motion, kills flowing
  | 'stillness'         // Level-up: time frozen, decision pending
  // Contrast 3: Stance
  | 'massacre'          // Early: gleeful destruction
  | 'respect'           // Late: "they earned it"
  // Contrast 4: Humility
  | 'hubris'            // "I am invincible"
  | 'humility'          // "I still lost"
  // Contrast 5: Sound
  | 'noise'             // Combat: chaos, explosions, kills
  | 'silence'           // THE BALL forming: dread, anticipation
  // Contrast 6: Role
  | 'predator'          // Hunting the bees
  | 'prey'              // Being hunted by the swarm
  // Contrast 7: Knowledge
  | 'learning'          // Early runs: discovering patterns
  | 'knowing';          // Later: "ah, I know this one"

/**
 * A contrast dimension with its two poles.
 */
export interface ContrastDimension {
  name: string;
  poleA: ContrastPole;
  poleB: ContrastPole;
  visitedA: boolean;
  visitedB: boolean;
  currentIntensity: number; // -1 (full A) to +1 (full B)
  lastTransition: number;   // gameTime of last pole switch
}

/**
 * Full contrast state tracking.
 */
export interface ContrastState {
  dimensions: Map<string, ContrastDimension>;
  contrastsVisited: number;        // Count of contrasts with both poles visited
  currentDominant: ContrastPole[]; // Currently active poles (can compose)
  transitionHistory: ContrastTransition[];
}

/**
 * A recorded contrast transition (for analysis and voice lines).
 */
export interface ContrastTransition {
  dimension: string;
  from: ContrastPole;
  to: ContrastPole;
  gameTime: number;
  wave: number;
  trigger: string; // What caused the transition
}

// =============================================================================
// Types - Arc Phases
// =============================================================================

/**
 * The four phases of the tragedy arc (Part VI).
 */
export type ArcPhase = 'POWER' | 'FLOW' | 'CRISIS' | 'TRAGEDY';

/**
 * Arc phase configuration.
 */
export interface ArcPhaseConfig {
  phase: ArcPhase;
  description: string;
  waveRange: [number, number]; // Typical wave range
  dominantContrasts: ContrastPole[];
  voiceLines: string[];
}

/**
 * Full arc state tracking.
 */
export interface ArcState {
  currentPhase: ArcPhase;
  phaseStartTime: number;
  phaseStartWave: number;
  phasesVisited: ArcPhase[];
  peakReached: boolean;
  valleyReached: boolean;
  closureType: 'pending' | 'dignity' | 'arbitrary' | null;
}

// =============================================================================
// Types - Personality Voice Lines
// =============================================================================

/**
 * Voice line triggers.
 */
export type VoiceLineTrigger =
  | 'first_kill'
  | 'multi_kill'
  | 'massacre'       // 10+ kills in 3 seconds
  | 'level_up'
  | 'formation_spotted'
  | 'ball_forming'
  | 'ball_escape'
  | 'death'
  | 'contrast_flip'  // Sudden pole reversal
  | 'phase_transition'
  // Kill milestone triggers (CREATIVE-IDENTITY)
  | 'kill_milestone_10'
  | 'kill_milestone_25'
  | 'kill_milestone_50'
  | 'kill_milestone_100'
  | 'kill_milestone_200'
  | 'kill_milestone_300'
  // Situational triggers (CREATIVE-IDENTITY)
  | 'graze'          // Near miss
  | 'low_hp_entered' // First time entering critical health
  | 'survived_ball'; // Escaped THE BALL

/**
 * A voice line with context.
 */
export interface VoiceLine {
  trigger: VoiceLineTrigger;
  text: string;
  phase?: ArcPhase;     // Only show in this phase
  contrast?: string;    // Only show for this contrast flip
  priority: number;     // Higher = more likely to show (0-100)
  cooldownMs: number;   // Minimum time between same line
}

/**
 * Voice line state.
 */
export interface VoiceLineState {
  lastShown: VoiceLine | null;
  lastShownTime: number;
  cooldowns: Map<string, number>; // line text -> last shown time
  queue: VoiceLine[];             // Pending lines to show
}

// =============================================================================
// Constants - The Seven Contrasts
// =============================================================================

/**
 * Initialize the seven contrast dimensions.
 */
export function createContrastDimensions(): Map<string, ContrastDimension> {
  const dimensions = new Map<string, ContrastDimension>();

  const contrasts: Array<{ name: string; poleA: ContrastPole; poleB: ContrastPole }> = [
    { name: 'power', poleA: 'god_of_death', poleB: 'cornered_prey' },
    { name: 'tempo', poleA: 'speed', poleB: 'stillness' },
    { name: 'stance', poleA: 'massacre', poleB: 'respect' },
    { name: 'humility', poleA: 'hubris', poleB: 'humility' },
    { name: 'sound', poleA: 'noise', poleB: 'silence' },
    { name: 'role', poleA: 'predator', poleB: 'prey' },
    { name: 'knowledge', poleA: 'learning', poleB: 'knowing' },
  ];

  for (const { name, poleA, poleB } of contrasts) {
    dimensions.set(name, {
      name,
      poleA,
      poleB,
      visitedA: false,
      visitedB: false,
      currentIntensity: -1, // Start at pole A
      lastTransition: 0,
    });
  }

  return dimensions;
}

// =============================================================================
// Constants - Arc Phases
// =============================================================================

export const ARC_PHASES: ArcPhaseConfig[] = [
  {
    phase: 'POWER',
    description: 'Feeling godlike, kills flowing',
    waveRange: [1, 3],
    dominantContrasts: ['god_of_death', 'speed', 'massacre', 'hubris', 'noise', 'predator', 'learning'],
    voiceLines: [
      '40 per minute. I can do better.',
      'Evolution made me for this.',
      'Pathetic. Is this their defense?',
    ],
  },
  {
    phase: 'FLOW',
    description: 'In the zone, combos chaining',
    waveRange: [4, 6],
    dominantContrasts: ['god_of_death', 'speed', 'massacre', 'hubris', 'noise', 'predator', 'knowing'],
    voiceLines: [
      'Now THIS is hunting.',
      'The rhythm is perfect.',
      'They scatter. They always scatter.',
    ],
  },
  {
    phase: 'CRISIS',
    description: 'THE BALL forming, panic rising',
    waveRange: [7, 9],
    dominantContrasts: ['cornered_prey', 'speed', 'respect', 'hubris', 'silence', 'prey', 'knowing'],
    voiceLines: [
      "They're learning. How adorable.",
      'Interesting formation...',
      'Well. Here we go again.',
    ],
  },
  {
    phase: 'TRAGEDY',
    description: 'Inevitable end, dignity in death',
    waveRange: [10, Infinity],
    dominantContrasts: ['cornered_prey', 'stillness', 'respect', 'humility', 'silence', 'prey', 'knowing'],
    voiceLines: [
      'The colony always wins. ...Respect.',
      'A magnificent end.',
      'Tell the hive I fought well.',
    ],
  },
];

// =============================================================================
// Constants - Voice Lines
// =============================================================================

export const VOICE_LINES: VoiceLine[] = [
  // First kill
  { trigger: 'first_kill', text: '40 per minute. I can do better.', priority: 100, cooldownMs: Infinity },

  // Multi-kills
  { trigger: 'multi_kill', text: 'Evolution made me for this.', priority: 70, cooldownMs: 15000 },
  { trigger: 'multi_kill', text: 'Like cutting through honey.', priority: 60, cooldownMs: 15000 },
  { trigger: 'multi_kill', text: 'Satisfying.', priority: 50, cooldownMs: 10000 },

  // Massacre (10+ kills in 3s)
  { trigger: 'massacre', text: 'THIS is why they fear us.', priority: 90, cooldownMs: 30000 },
  { trigger: 'massacre', text: 'A massacre worthy of song.', priority: 85, cooldownMs: 30000 },
  { trigger: 'massacre', text: 'Beautiful.', priority: 80, cooldownMs: 20000 },

  // Level up
  { trigger: 'level_up', text: 'Ah. More ways to die magnificently.', priority: 60, cooldownMs: 20000 },
  { trigger: 'level_up', text: 'Stronger. Faster. Still doomed.', priority: 55, cooldownMs: 20000 },
  { trigger: 'level_up', text: 'The hive adapts. So do I.', priority: 50, cooldownMs: 20000 },

  // Formation spotted
  { trigger: 'formation_spotted', text: "They're learning. How adorable.", priority: 80, cooldownMs: 30000 },
  { trigger: 'formation_spotted', text: 'Coordination. Impressive.', priority: 70, cooldownMs: 30000 },
  { trigger: 'formation_spotted', text: "Ah. They've been practicing.", priority: 65, cooldownMs: 30000 },

  // THE BALL forming
  { trigger: 'ball_forming', text: 'Well. Here we go again.', priority: 100, cooldownMs: Infinity },
  { trigger: 'ball_forming', text: 'The heat rises. I feel it.', priority: 90, cooldownMs: 60000 },
  { trigger: 'ball_forming', text: 'This is how it ends for most.', priority: 85, cooldownMs: 60000 },

  // Ball escape (if player escapes)
  { trigger: 'ball_escape', text: 'Not today.', priority: 100, cooldownMs: 30000 },
  { trigger: 'ball_escape', text: 'A reprieve. Not a victory.', priority: 90, cooldownMs: 30000 },
  { trigger: 'ball_escape', text: 'They will form again.', priority: 85, cooldownMs: 30000 },

  // Death
  { trigger: 'death', text: 'The colony always wins. ...Respect.', priority: 100, cooldownMs: Infinity },
  { trigger: 'death', text: 'A good death. They earned it.', priority: 95, cooldownMs: Infinity },
  { trigger: 'death', text: 'Tell them I fought well.', priority: 90, cooldownMs: Infinity },

  // Phase transitions
  { trigger: 'phase_transition', text: 'The hunt begins.', phase: 'POWER', priority: 100, cooldownMs: Infinity },
  { trigger: 'phase_transition', text: 'The rhythm settles in.', phase: 'FLOW', priority: 100, cooldownMs: Infinity },
  { trigger: 'phase_transition', text: 'They grow bold.', phase: 'CRISIS', priority: 100, cooldownMs: Infinity },
  { trigger: 'phase_transition', text: 'So. This is the end.', phase: 'TRAGEDY', priority: 100, cooldownMs: Infinity },

  // Contrast flips
  { trigger: 'contrast_flip', text: 'The tables turn.', contrast: 'power', priority: 80, cooldownMs: 30000 },
  { trigger: 'contrast_flip', text: 'From hunter to hunted.', contrast: 'role', priority: 85, cooldownMs: 30000 },
  { trigger: 'contrast_flip', text: 'Now I understand.', contrast: 'knowledge', priority: 75, cooldownMs: 30000 },

  // =============================================================================
  // CREATIVE-IDENTITY: Kill Milestone Lines (Swagger)
  // =============================================================================

  // Kill milestone: 10
  { trigger: 'kill_milestone_10', text: 'Warm-up complete.', priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_10', text: 'Finally getting started.', priority: 90, cooldownMs: Infinity },

  // Kill milestone: 25
  { trigger: 'kill_milestone_25', text: "Now I'm actually trying.", priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_25', text: 'A respectable number.', priority: 90, cooldownMs: Infinity },

  // Kill milestone: 50
  { trigger: 'kill_milestone_50', text: 'This will be remembered.', priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_50', text: 'Half a hundred souls.', priority: 90, cooldownMs: Infinity },

  // Kill milestone: 100
  { trigger: 'kill_milestone_100', text: 'A hundred souls. And counting.', priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_100', text: 'A centuria of corpses.', priority: 90, cooldownMs: Infinity },

  // Kill milestone: 200
  { trigger: 'kill_milestone_200', text: 'They should write songs about this.', priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_200', text: 'Two hundred. Not bad.', priority: 90, cooldownMs: Infinity },

  // Kill milestone: 300
  { trigger: 'kill_milestone_300', text: 'I am become death. And I love it.', priority: 95, cooldownMs: Infinity },
  { trigger: 'kill_milestone_300', text: 'Three hundred. Legendary.', priority: 90, cooldownMs: Infinity },

  // =============================================================================
  // CREATIVE-IDENTITY: Situational Lines (Defiance & Dark Humor)
  // =============================================================================

  // Graze (near miss)
  { trigger: 'graze', text: 'Almost.', priority: 60, cooldownMs: 5000 },
  { trigger: 'graze', text: 'Too slow, little ones.', priority: 55, cooldownMs: 5000 },
  { trigger: 'graze', text: 'That all you got?', priority: 50, cooldownMs: 5000 },
  { trigger: 'graze', text: 'Close. But not close enough.', priority: 45, cooldownMs: 5000 },

  // Low HP entered (defiance, not whining)
  { trigger: 'low_hp_entered', text: 'Getting interesting.', priority: 85, cooldownMs: Infinity },
  { trigger: 'low_hp_entered', text: 'Now they have my attention.', priority: 80, cooldownMs: Infinity },
  { trigger: 'low_hp_entered', text: 'Pain? I call that motivation.', priority: 75, cooldownMs: Infinity },
  { trigger: 'low_hp_entered', text: 'Is that supposed to hurt?', priority: 70, cooldownMs: Infinity },

  // Survived THE BALL (rare achievement, massive swagger)
  { trigger: 'survived_ball', text: 'Not. Today.', priority: 100, cooldownMs: 60000 },
  { trigger: 'survived_ball', text: 'You thought you had me.', priority: 95, cooldownMs: 60000 },
  { trigger: 'survived_ball', text: 'The heat? Refreshing.', priority: 90, cooldownMs: 60000 },
];

// =============================================================================
// Factory Functions
// =============================================================================

/**
 * Create initial contrast state.
 */
export function createContrastState(): ContrastState {
  return {
    dimensions: createContrastDimensions(),
    contrastsVisited: 0,
    currentDominant: ['god_of_death', 'speed', 'massacre', 'hubris', 'noise', 'predator', 'learning'],
    transitionHistory: [],
  };
}

/**
 * Create initial arc state.
 */
export function createArcState(): ArcState {
  return {
    currentPhase: 'POWER',
    phaseStartTime: 0,
    phaseStartWave: 1,
    phasesVisited: ['POWER'],
    peakReached: false,
    valleyReached: false,
    closureType: 'pending',
  };
}

/**
 * Create initial voice line state.
 */
export function createVoiceLineState(): VoiceLineState {
  return {
    lastShown: null,
    lastShownTime: 0,
    cooldowns: new Map(),
    queue: [],
  };
}

// =============================================================================
// Contrast Calculation
// =============================================================================

/**
 * Calculate contrast intensity from game state.
 *
 * Returns -1 to +1 where:
 * - -1 = fully at pole A
 * - +1 = fully at pole B
 * - 0 = neutral/transitioning
 */
export function calculateContrastIntensities(
  gameState: GameState
): Map<string, number> {
  const intensities = new Map<string, number>();
  const { player, wave, enemies } = gameState;

  // Health fraction for calculations
  const healthFrac = player.health / player.maxHealth;

  // Enemy density (normalized 0-1)
  const maxEnemies = 30;
  const enemyDensity = Math.min(enemies.length / maxEnemies, 1);

  // Kill rate (recent kills - would need tracking)
  // For now, approximate from score vs wave
  const killRate = Math.min(gameState.totalEnemiesKilled / (wave * 15), 1);

  // 1. Power: god_of_death (-1) <-> cornered_prey (+1)
  // High health + few enemies = god_of_death
  // Low health + many enemies = cornered_prey
  const powerIntensity = (enemyDensity * 0.6 + (1 - healthFrac) * 0.4) * 2 - 1;
  intensities.set('power', clamp(powerIntensity, -1, 1));

  // 2. Tempo: speed (-1) <-> stillness (+1)
  // In combat = speed, in upgrade/menu = stillness
  const isUpgrading = gameState.status === 'upgrade';
  const tempoIntensity = isUpgrading ? 1 : -1 + killRate * 0.2;
  intensities.set('tempo', clamp(tempoIntensity, -1, 1));

  // 3. Stance: massacre (-1) <-> respect (+1)
  // Early waves = massacre, late waves = respect
  const waveProgress = Math.min(wave / 10, 1);
  const stanceIntensity = waveProgress * 2 - 1;
  intensities.set('stance', clamp(stanceIntensity, -1, 1));

  // 4. Humility: hubris (-1) <-> humility (+1)
  // High health + high kills = hubris, deaths/damage = humility
  const hubrisIntensity = ((1 - healthFrac) + waveProgress * 0.5) - 0.5;
  intensities.set('humility', clamp(hubrisIntensity * 2, -1, 1));

  // 5. Sound: noise (-1) <-> silence (+1)
  // Many enemies dying = noise, few enemies/BALL forming = silence
  // This should be connected to audio system state
  const soundIntensity = enemyDensity > 0.5 ? -1 + (1 - enemyDensity) : 1 - enemyDensity * 2;
  intensities.set('sound', clamp(soundIntensity, -1, 1));

  // 6. Role: predator (-1) <-> prey (+1)
  // Similar to power but more about active state
  const roleIntensity = (enemyDensity * 0.7 + (1 - healthFrac) * 0.3) * 2 - 1;
  intensities.set('role', clamp(roleIntensity, -1, 1));

  // 7. Knowledge: learning (-1) <-> knowing (+1)
  // Increases with wave/experience
  // In real implementation, would track per-run vs cross-run
  const knowledgeIntensity = Math.min(wave / 8, 1) * 2 - 1;
  intensities.set('knowledge', clamp(knowledgeIntensity, -1, 1));

  return intensities;
}

/**
 * Clamp a value to a range.
 */
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

// =============================================================================
// Contrast State Updates
// =============================================================================

/**
 * Update contrast state based on current game state.
 *
 * This is the main update function called each frame (but only processes
 * meaningful changes to avoid performance cost).
 */
export function updateContrastState(
  contrastState: ContrastState,
  gameState: GameState
): { contrastState: ContrastState; transitions: ContrastTransition[] } {
  const intensities = calculateContrastIntensities(gameState);
  const transitions: ContrastTransition[] = [];

  // Threshold for considering a pole "visited"
  const VISIT_THRESHOLD = 0.6;

  // Threshold for triggering a transition event (GD-2: sudden, not gradual)
  const TRANSITION_THRESHOLD = 0.5;

  for (const [name, dimension] of contrastState.dimensions) {
    const newIntensity = intensities.get(name) ?? 0;
    const oldIntensity = dimension.currentIntensity;

    // Check if we've crossed to pole A (intensity <= -VISIT_THRESHOLD)
    if (newIntensity <= -VISIT_THRESHOLD && !dimension.visitedA) {
      dimension.visitedA = true;
    }

    // Check if we've crossed to pole B (intensity >= VISIT_THRESHOLD)
    if (newIntensity >= VISIT_THRESHOLD && !dimension.visitedB) {
      dimension.visitedB = true;
    }

    // Check for significant transition (GD-2: sudden transitions)
    const intensityChange = Math.abs(newIntensity - oldIntensity);
    if (intensityChange >= TRANSITION_THRESHOLD) {
      const from = oldIntensity < 0 ? dimension.poleA : dimension.poleB;
      const to = newIntensity < 0 ? dimension.poleA : dimension.poleB;

      if (from !== to) {
        const transition: ContrastTransition = {
          dimension: name,
          from,
          to,
          gameTime: gameState.gameTime,
          wave: gameState.wave,
          trigger: determineTransitionTrigger(name, gameState),
        };
        transitions.push(transition);
        contrastState.transitionHistory.push(transition);
        dimension.lastTransition = gameState.gameTime;
      }
    }

    dimension.currentIntensity = newIntensity;
  }

  // Count contrasts with both poles visited (GD-1)
  contrastState.contrastsVisited = Array.from(contrastState.dimensions.values())
    .filter(d => d.visitedA && d.visitedB).length;

  // Update current dominant poles
  contrastState.currentDominant = Array.from(contrastState.dimensions.values())
    .map(d => d.currentIntensity < 0 ? d.poleA : d.poleB);

  return { contrastState, transitions };
}

/**
 * Determine what triggered a contrast transition.
 */
function determineTransitionTrigger(dimension: string, gameState: GameState): string {
  const healthFrac = gameState.player.health / gameState.player.maxHealth;

  switch (dimension) {
    case 'power':
      return healthFrac < 0.3 ? 'low_health' : gameState.enemies.length > 20 ? 'swarm_pressure' : 'wave_progression';
    case 'tempo':
      return gameState.status === 'upgrade' ? 'level_up' : 'combat_resumed';
    case 'stance':
      return gameState.wave > 7 ? 'late_game' : 'wave_progression';
    case 'humility':
      return healthFrac < 0.3 ? 'damage_taken' : 'hubris_building';
    case 'sound':
      return gameState.enemies.length < 5 ? 'silence_falls' : 'combat_noise';
    case 'role':
      return gameState.enemies.length > 15 ? 'surrounded' : 'hunting';
    case 'knowledge':
      return 'experience_gained';
    default:
      return 'unknown';
  }
}

// =============================================================================
// Arc Phase Management
// =============================================================================

/**
 * Determine the current arc phase based on game state.
 */
export function calculateArcPhase(gameState: GameState): ArcPhase {
  const { wave } = gameState;
  const healthFrac = gameState.player.health / gameState.player.maxHealth;

  // TRAGEDY: Wave 10+ OR health critical with high enemy count
  if (wave >= 10 || (healthFrac < 0.2 && gameState.enemies.length > 15)) {
    return 'TRAGEDY';
  }

  // CRISIS: Wave 7-9 OR health low with many enemies
  if (wave >= 7 || (healthFrac < 0.4 && gameState.enemies.length > 10)) {
    return 'CRISIS';
  }

  // FLOW: Wave 4-6, player has established rhythm
  if (wave >= 4) {
    return 'FLOW';
  }

  // POWER: Wave 1-3, player is learning but feels powerful
  return 'POWER';
}

/**
 * Update arc state based on game state.
 */
export function updateArcState(
  arcState: ArcState,
  gameState: GameState
): { arcState: ArcState; phaseChanged: boolean; newPhase?: ArcPhase } {
  const newPhase = calculateArcPhase(gameState);
  let phaseChanged = false;

  if (newPhase !== arcState.currentPhase) {
    phaseChanged = true;

    // Record the transition
    if (!arcState.phasesVisited.includes(newPhase)) {
      arcState.phasesVisited.push(newPhase);
    }

    // Update phase tracking
    arcState.currentPhase = newPhase;
    arcState.phaseStartTime = gameState.gameTime;
    arcState.phaseStartWave = gameState.wave;

    // Check for peak (FLOW is the peak of the experience)
    if (newPhase === 'FLOW') {
      arcState.peakReached = true;
    }

    // Check for valley (TRAGEDY is the valley)
    if (newPhase === 'TRAGEDY') {
      arcState.valleyReached = true;
    }
  }

  return { arcState, phaseChanged, newPhase: phaseChanged ? newPhase : undefined };
}

/**
 * Record arc closure (called on death).
 */
export function recordArcClosure(
  arcState: ArcState,
  deathCause: string | null
): ArcState {
  // Determine closure type
  // Dignity: player understands why they died
  // Arbitrary: death felt random/unfair
  const dignifiedCauses = ['ball', 'heat', 'swarm', 'surrounded', 'overwhelmed', 'formation'];
  const hasDignity = deathCause && dignifiedCauses.some(c => deathCause.toLowerCase().includes(c));

  arcState.closureType = hasDignity ? 'dignity' : 'arbitrary';

  return arcState;
}

// =============================================================================
// Voice Line Management
// =============================================================================

/**
 * Get a voice line for a trigger.
 */
export function getVoiceLine(
  voiceLineState: VoiceLineState,
  trigger: VoiceLineTrigger,
  gameTime: number,
  context?: { phase?: ArcPhase; contrast?: string }
): VoiceLine | null {
  // Find matching lines
  const matchingLines = VOICE_LINES.filter(line => {
    if (line.trigger !== trigger) return false;

    // Check phase restriction
    if (line.phase && context?.phase && line.phase !== context.phase) {
      return false;
    }

    // Check contrast restriction
    if (line.contrast && context?.contrast && line.contrast !== context.contrast) {
      return false;
    }

    // Check cooldown
    const lastShown = voiceLineState.cooldowns.get(line.text);
    if (lastShown && gameTime - lastShown < line.cooldownMs) {
      return false;
    }

    return true;
  });

  if (matchingLines.length === 0) return null;

  // Weight by priority
  const totalPriority = matchingLines.reduce((sum, l) => sum + l.priority, 0);
  let random = Math.random() * totalPriority;

  for (const line of matchingLines) {
    random -= line.priority;
    if (random <= 0) {
      // Record cooldown
      voiceLineState.cooldowns.set(line.text, gameTime);
      voiceLineState.lastShown = line;
      voiceLineState.lastShownTime = gameTime;
      return line;
    }
  }

  return matchingLines[0];
}

/**
 * Queue a voice line to be shown.
 */
export function queueVoiceLine(
  voiceLineState: VoiceLineState,
  line: VoiceLine
): void {
  // Don't queue duplicates
  if (voiceLineState.queue.some(l => l.text === line.text)) {
    return;
  }

  // Insert sorted by priority (highest first)
  const insertIndex = voiceLineState.queue.findIndex(l => l.priority < line.priority);
  if (insertIndex === -1) {
    voiceLineState.queue.push(line);
  } else {
    voiceLineState.queue.splice(insertIndex, 0, line);
  }
}

/**
 * Get the next voice line from the queue.
 */
export function dequeueVoiceLine(
  voiceLineState: VoiceLineState,
  gameTime: number
): VoiceLine | null {
  // Minimum time between any voice lines
  const MIN_VOICE_LINE_INTERVAL = 3000; // 3 seconds

  if (gameTime - voiceLineState.lastShownTime < MIN_VOICE_LINE_INTERVAL) {
    return null;
  }

  const line = voiceLineState.queue.shift();
  if (line) {
    voiceLineState.lastShown = line;
    voiceLineState.lastShownTime = gameTime;
    voiceLineState.cooldowns.set(line.text, gameTime);
  }

  return line ?? null;
}

// =============================================================================
// Combined System
// =============================================================================

/**
 * Full emotional state of the game.
 */
export interface EmotionalState {
  contrast: ContrastState;
  arc: ArcState;
  voiceLines: VoiceLineState;
}

/**
 * Create initial emotional state.
 */
export function createEmotionalState(): EmotionalState {
  return {
    contrast: createContrastState(),
    arc: createArcState(),
    voiceLines: createVoiceLineState(),
  };
}

/**
 * Events that the emotional system can emit.
 */
export interface EmotionalEvent {
  type: 'phase_transition' | 'contrast_flip' | 'voice_line' | 'closure';
  data: {
    phase?: ArcPhase;
    transition?: ContrastTransition;
    line?: VoiceLine;
    closureType?: 'dignity' | 'arbitrary';
  };
}

/**
 * Update the full emotional state.
 *
 * This is the main entry point called by the game loop.
 */
export function updateEmotionalState(
  state: EmotionalState,
  gameState: GameState
): { state: EmotionalState; events: EmotionalEvent[] } {
  const events: EmotionalEvent[] = [];

  // Update contrasts
  const { contrastState, transitions } = updateContrastState(state.contrast, gameState);
  state.contrast = contrastState;

  // Emit contrast flip events
  for (const transition of transitions) {
    events.push({
      type: 'contrast_flip',
      data: { transition },
    });

    // Queue voice line for contrast flip
    const line = getVoiceLine(
      state.voiceLines,
      'contrast_flip',
      gameState.gameTime,
      { contrast: transition.dimension }
    );
    if (line) {
      queueVoiceLine(state.voiceLines, line);
    }
  }

  // Update arc
  const { arcState, phaseChanged, newPhase } = updateArcState(state.arc, gameState);
  state.arc = arcState;

  // Emit phase transition event
  if (phaseChanged && newPhase) {
    events.push({
      type: 'phase_transition',
      data: { phase: newPhase },
    });

    // Queue voice line for phase transition
    const line = getVoiceLine(
      state.voiceLines,
      'phase_transition',
      gameState.gameTime,
      { phase: newPhase }
    );
    if (line) {
      queueVoiceLine(state.voiceLines, line);
    }
  }

  // Process voice line queue
  const nextLine = dequeueVoiceLine(state.voiceLines, gameState.gameTime);
  if (nextLine) {
    events.push({
      type: 'voice_line',
      data: { line: nextLine },
    });
  }

  return { state, events };
}

/**
 * Trigger a voice line for a specific event.
 *
 * Called by game systems when specific events occur.
 */
export function triggerVoiceLine(
  state: EmotionalState,
  trigger: VoiceLineTrigger,
  gameTime: number
): VoiceLine | null {
  const line = getVoiceLine(
    state.voiceLines,
    trigger,
    gameTime,
    { phase: state.arc.currentPhase }
  );

  if (line) {
    queueVoiceLine(state.voiceLines, line);
  }

  return line;
}

/**
 * Get quality metrics for the current run.
 *
 * Used to validate the experience quality equation:
 * Q = F x (C x A x V^(1/n))
 */
export function getQualityMetrics(state: EmotionalState): {
  contrastCoverage: number;  // C: fraction of contrasts with both poles visited
  arcCoverage: number;       // A: fraction of arc phases visited
  hasValidArc: boolean;      // Arc validity check (peak + valley + closure)
} {
  // Contrast coverage: how many of the 7 contrasts have both poles visited?
  const contrastCoverage = state.contrast.contrastsVisited / 7;

  // Arc coverage: how many of the 4 phases were visited?
  const arcCoverage = state.arc.phasesVisited.length / 4;

  // Valid arc check
  const hasValidArc =
    state.arc.peakReached &&
    state.arc.valleyReached &&
    state.arc.closureType === 'dignity';

  return {
    contrastCoverage,
    arcCoverage,
    hasValidArc,
  };
}

// =============================================================================
// CREATIVE-SPECTACLE: Phase Transition Visual Effects
// =============================================================================

/**
 * Visual effect configuration for arc phase transitions.
 *
 * These are the "clip-worthy" moments between phases.
 */
export interface PhaseTransitionEffect {
  // Screen effects
  screenFlash?: { color: string; duration: number; opacity: number };
  screenTint?: { color: string; duration: number; opacity: number };
  vignette?: { color: string; intensity: number };

  // Camera effects
  cameraShake?: { intensity: number; duration: number };
  cameraZoom?: { target: number; duration: number };

  // Audio cues
  musicShift?: 'major' | 'minor' | 'silence' | 'heartbeat';
  soundCue?: string;

  // HUD effects
  hudText?: { text: string; color: string; duration: number };
  hudPulse?: { color: string; count: number };

  // Animation
  desaturation?: number; // 0 = full color, 1 = grayscale
}

/**
 * Get visual effects for a phase transition.
 */
export function getPhaseTransitionEffects(
  fromPhase: ArcPhase,
  toPhase: ArcPhase
): PhaseTransitionEffect {
  // POWER -> FLOW: The hunt begins
  if (fromPhase === 'POWER' && toPhase === 'FLOW') {
    return {
      screenFlash: { color: '#FFD700', duration: 200, opacity: 0.3 },
      hudText: { text: 'THE HUNT BEGINS', color: '#FFD700', duration: 2000 },
      hudPulse: { color: '#FFD700', count: 2 },
      musicShift: 'major',
      soundCue: 'phase_flow',
    };
  }

  // FLOW -> CRISIS: They're learning
  if (fromPhase === 'FLOW' && toPhase === 'CRISIS') {
    return {
      screenTint: { color: '#6B2D5B', duration: 500, opacity: 0.15 },
      vignette: { color: '#FF6600', intensity: 0.2 },
      hudText: { text: 'THEY GROW BOLD', color: '#FF6600', duration: 2500 },
      cameraShake: { intensity: 4, duration: 300 },
      musicShift: 'minor',
      soundCue: 'phase_crisis',
    };
  }

  // CRISIS -> TRAGEDY: This is the end
  if (fromPhase === 'CRISIS' && toPhase === 'TRAGEDY') {
    return {
      screenTint: { color: '#000000', duration: 1000, opacity: 0.2 },
      vignette: { color: '#880000', intensity: 0.4 },
      hudText: { text: 'SO. THIS IS THE END.', color: '#888888', duration: 3000 },
      desaturation: 0.3,
      musicShift: 'heartbeat',
      soundCue: 'phase_tragedy',
      cameraZoom: { target: 0.9, duration: 2000 },
    };
  }

  // Any phase -> TRAGEDY (emergency transition)
  if (toPhase === 'TRAGEDY' && fromPhase !== 'CRISIS') {
    return {
      screenFlash: { color: '#FF0000', duration: 150, opacity: 0.4 },
      screenTint: { color: '#000000', duration: 500, opacity: 0.3 },
      vignette: { color: '#880000', intensity: 0.5 },
      cameraShake: { intensity: 8, duration: 400 },
      musicShift: 'silence',
      desaturation: 0.4,
    };
  }

  // Default: subtle transition
  return {
    hudPulse: { color: '#FFFFFF', count: 1 },
  };
}

/**
 * State for tracking active phase transition effects.
 */
export interface PhaseTransitionState {
  active: boolean;
  effect: PhaseTransitionEffect | null;
  startTime: number;
  fromPhase: ArcPhase | null;
  toPhase: ArcPhase | null;
  progress: number; // 0-1
}

/**
 * Create initial phase transition state.
 */
export function createPhaseTransitionState(): PhaseTransitionState {
  return {
    active: false,
    effect: null,
    startTime: 0,
    fromPhase: null,
    toPhase: null,
    progress: 0,
  };
}

/**
 * Start a phase transition effect.
 */
export function startPhaseTransition(
  fromPhase: ArcPhase,
  toPhase: ArcPhase,
  gameTime: number
): PhaseTransitionState {
  const effect = getPhaseTransitionEffects(fromPhase, toPhase);

  return {
    active: true,
    effect,
    startTime: gameTime,
    fromPhase,
    toPhase,
    progress: 0,
  };
}

/**
 * Update phase transition state.
 */
export function updatePhaseTransition(
  state: PhaseTransitionState,
  gameTime: number
): PhaseTransitionState {
  if (!state.active || !state.effect) {
    return state;
  }

  // Calculate max duration from all effects
  const maxDuration = Math.max(
    state.effect.screenFlash?.duration ?? 0,
    state.effect.screenTint?.duration ?? 0,
    state.effect.hudText?.duration ?? 0,
    state.effect.cameraZoom?.duration ?? 0,
    1000 // Minimum 1 second
  );

  const elapsed = gameTime - state.startTime;
  const progress = Math.min(1, elapsed / maxDuration);

  if (progress >= 1) {
    return {
      ...state,
      active: false,
      progress: 1,
    };
  }

  return {
    ...state,
    progress,
  };
}

/**
 * Render phase transition effects to canvas.
 *
 * Call this AFTER game rendering but BEFORE HUD.
 */
export function renderPhaseTransition(
  ctx: CanvasRenderingContext2D,
  state: PhaseTransitionState,
  arenaWidth: number,
  arenaHeight: number
): void {
  if (!state.active || !state.effect) return;

  ctx.save();

  // Screen flash
  if (state.effect.screenFlash) {
    const flashProgress = Math.min(1, state.progress * 3); // Flash is quick
    const opacity = state.effect.screenFlash.opacity * (1 - flashProgress);
    if (opacity > 0) {
      ctx.fillStyle = state.effect.screenFlash.color + Math.floor(opacity * 255).toString(16).padStart(2, '0');
      ctx.fillRect(0, 0, arenaWidth, arenaHeight);
    }
  }

  // Screen tint
  if (state.effect.screenTint) {
    const tintProgress = Math.min(1, state.progress * 2); // Tint fades in then out
    const fadeIn = tintProgress < 0.5;
    const opacity = fadeIn
      ? state.effect.screenTint.opacity * (tintProgress * 2)
      : state.effect.screenTint.opacity * (1 - (tintProgress - 0.5) * 2);
    if (opacity > 0) {
      ctx.fillStyle = state.effect.screenTint.color;
      ctx.globalAlpha = opacity;
      ctx.fillRect(0, 0, arenaWidth, arenaHeight);
      ctx.globalAlpha = 1;
    }
  }

  // Vignette
  if (state.effect.vignette) {
    const vignetteProgress = Math.min(1, state.progress * 1.5);
    const intensity = state.effect.vignette.intensity * (1 - vignetteProgress * 0.5);
    if (intensity > 0) {
      const gradient = ctx.createRadialGradient(
        arenaWidth / 2, arenaHeight / 2, 0,
        arenaWidth / 2, arenaHeight / 2, Math.max(arenaWidth, arenaHeight) * 0.7
      );
      gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
      gradient.addColorStop(1, state.effect.vignette.color);
      ctx.globalAlpha = intensity;
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, arenaWidth, arenaHeight);
      ctx.globalAlpha = 1;
    }
  }

  // Desaturation (grayscale overlay approximation)
  if (state.effect.desaturation && state.effect.desaturation > 0) {
    // This is a CSS-like approximation - true desaturation would need ImageData
    ctx.globalAlpha = state.effect.desaturation * 0.3;
    ctx.fillStyle = '#808080';
    ctx.globalCompositeOperation = 'saturation';
    ctx.fillRect(0, 0, arenaWidth, arenaHeight);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
  }

  ctx.restore();
}

/**
 * Get HUD text to display for phase transition.
 */
export function getPhaseTransitionHudText(
  state: PhaseTransitionState
): { text: string; color: string; opacity: number } | null {
  if (!state.active || !state.effect?.hudText) return null;

  const { text, color, duration } = state.effect.hudText;
  const elapsed = state.progress * duration;

  // Fade in (first 20%), hold, fade out (last 20%)
  let opacity = 1;
  if (elapsed < duration * 0.2) {
    opacity = elapsed / (duration * 0.2);
  } else if (elapsed > duration * 0.8) {
    opacity = 1 - (elapsed - duration * 0.8) / (duration * 0.2);
  }

  return { text, color, opacity };
}
