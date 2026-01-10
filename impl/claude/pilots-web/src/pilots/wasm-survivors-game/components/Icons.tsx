/**
 * WASM Survivors - SVG Icon Components
 *
 * Replaces emoji-based icons with clean, geometric SVG icons.
 * All icons are designed to match the "Ukiyo-e meets arcade brutalism" aesthetic.
 *
 * Design principles:
 * - Geometric, angular shapes
 * - Consistent stroke weights
 * - Burnt amber/orange primary color palette
 * - Clean silhouettes at small sizes
 */

import React from 'react';

// =============================================================================
// Types
// =============================================================================

interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

// =============================================================================
// Game Identity Icons
// =============================================================================

/**
 * Hornet icon - the player character
 * A stylized hornet silhouette with angular wings and stinger
 */
export function HornetIcon({ size = 24, color = '#CC5500', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Body */}
      <ellipse cx="12" cy="12" rx="5" ry="6" fill={color} />
      {/* Stripes */}
      <rect x="7" y="10" width="10" height="1.5" fill="#1A1A1A" />
      <rect x="7" y="13" width="10" height="1.5" fill="#1A1A1A" />
      {/* Wings */}
      <ellipse cx="6" cy="9" rx="3" ry="2" fill={color} opacity="0.6" />
      <ellipse cx="18" cy="9" rx="3" ry="2" fill={color} opacity="0.6" />
      {/* Stinger */}
      <polygon points="12,18 10,22 14,22" fill={color} />
      {/* Eyes */}
      <circle cx="10" cy="8" r="1.5" fill="#1A1A1A" />
      <circle cx="14" cy="8" r="1.5" fill="#1A1A1A" />
    </svg>
  );
}

/**
 * Skull icon - death/danger indicator
 */
export function SkullIcon({ size = 24, color = '#FF4444', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Skull shape */}
      <path
        d="M12 2C7 2 4 6 4 10C4 13 5 15 7 16V20H10V18H14V20H17V16C19 15 20 13 20 10C20 6 17 2 12 2Z"
        fill={color}
      />
      {/* Eyes */}
      <circle cx="9" cy="10" r="2" fill="#1A1A1A" />
      <circle cx="15" cy="10" r="2" fill="#1A1A1A" />
      {/* Nose */}
      <polygon points="12,12 10,15 14,15" fill="#1A1A1A" />
    </svg>
  );
}

// =============================================================================
// Action Icons
// =============================================================================

/**
 * Lightning bolt - speed/power/apex strike
 */
export function LightningIcon({ size = 24, color = '#FFD700', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon
        points="13,2 6,14 11,14 11,22 18,10 13,10"
        fill={color}
      />
    </svg>
  );
}

/**
 * Arrow up - level up/upgrade
 */
export function ArrowUpIcon({ size = 24, color = '#00FF88', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,4 4,14 9,14 9,20 15,20 15,14 20,14" fill={color} />
    </svg>
  );
}

/**
 * Gamepad/controller - controls indicator
 */
export function GamepadIcon({ size = 24, color = '#FFFFFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Controller body */}
      <rect x="3" y="7" width="18" height="10" rx="3" fill={color} />
      {/* D-pad */}
      <rect x="6" y="10" width="2" height="4" fill="#1A1A1A" />
      <rect x="5" y="11" width="4" height="2" fill="#1A1A1A" />
      {/* Buttons */}
      <circle cx="16" cy="10" r="1.5" fill="#1A1A1A" />
      <circle cx="18" cy="12" r="1.5" fill="#1A1A1A" />
    </svg>
  );
}

// =============================================================================
// Ability Category Icons
// =============================================================================

/**
 * Sword/blade - damage abilities
 */
export function SwordIcon({ size = 24, color = '#FF3366', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,2 10,4 10,14 8,16 10,18 12,16 14,18 16,16 14,14 14,4" fill={color} />
      <rect x="10" y="18" width="4" height="4" fill={color} />
    </svg>
  );
}

/**
 * Shield - defense abilities
 */
export function ShieldIcon({ size = 24, color = '#4488FF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2L4 6V12C4 17 8 21 12 22C16 21 20 17 20 12V6L12 2Z"
        fill={color}
      />
      <path
        d="M12 5L7 8V12C7 15 9 18 12 19C15 18 17 15 17 12V8L12 5Z"
        fill="#1A1A1A"
        opacity="0.3"
      />
    </svg>
  );
}

/**
 * Running figure - speed abilities
 */
export function SpeedIcon({ size = 24, color = '#00FFFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Speed lines */}
      <line x1="2" y1="8" x2="8" y2="8" stroke={color} strokeWidth="2" />
      <line x1="4" y1="12" x2="10" y2="12" stroke={color} strokeWidth="2" />
      <line x1="2" y1="16" x2="8" y2="16" stroke={color} strokeWidth="2" />
      {/* Arrow */}
      <polygon points="18,12 10,6 10,18" fill={color} />
    </svg>
  );
}

/**
 * Star - special/rare abilities
 */
export function StarIcon({ size = 24, color = '#FFD700', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon
        points="12,2 14.5,9 22,9 16,14 18,22 12,17 6,22 8,14 2,9 9.5,9"
        fill={color}
      />
    </svg>
  );
}

// =============================================================================
// Specific Ability Icons
// =============================================================================

/**
 * Crosshair/target - precision abilities
 */
export function TargetIcon({ size = 24, color = '#FF8800', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="12" cy="12" r="8" stroke={color} strokeWidth="2" fill="none" />
      <circle cx="12" cy="12" r="3" fill={color} />
      <line x1="12" y1="2" x2="12" y2="6" stroke={color} strokeWidth="2" />
      <line x1="12" y1="18" x2="12" y2="22" stroke={color} strokeWidth="2" />
      <line x1="2" y1="12" x2="6" y2="12" stroke={color} strokeWidth="2" />
      <line x1="18" y1="12" x2="22" y2="12" stroke={color} strokeWidth="2" />
    </svg>
  );
}

/**
 * Fire/flame - burn damage
 */
export function FlameIcon({ size = 24, color = '#FF4400', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2C12 2 8 6 8 12C8 16 10 20 12 22C14 20 16 16 16 12C16 6 12 2 12 2Z"
        fill={color}
      />
      <path
        d="M12 8C12 8 10 10 10 13C10 15 11 17 12 18C13 17 14 15 14 13C14 10 12 8 12 8Z"
        fill="#FFD700"
      />
    </svg>
  );
}

/**
 * Heart - health/lifesteal
 */
export function HeartIcon({ size = 24, color = '#00FF88', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 21L10.55 19.7C5.4 15.1 2 12.1 2 8.5C2 5.4 4.4 3 7.5 3C9.2 3 10.9 3.8 12 5.1C13.1 3.8 14.8 3 16.5 3C19.6 3 22 5.4 22 8.5C22 12.1 18.6 15.1 13.45 19.7L12 21Z"
        fill={color}
      />
    </svg>
  );
}

/**
 * Poison drop - poison damage
 */
export function PoisonIcon({ size = 24, color = '#44FF44', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2L6 12C6 17 8.7 22 12 22C15.3 22 18 17 18 12L12 2Z"
        fill={color}
      />
      {/* Skull mark */}
      <circle cx="10" cy="14" r="1.5" fill="#1A1A1A" />
      <circle cx="14" cy="14" r="1.5" fill="#1A1A1A" />
    </svg>
  );
}

/**
 * Chain links - chain abilities
 */
export function ChainIcon({ size = 24, color = '#8888FF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <ellipse cx="8" cy="8" rx="4" ry="3" stroke={color} strokeWidth="2" fill="none" />
      <ellipse cx="16" cy="16" rx="4" ry="3" stroke={color} strokeWidth="2" fill="none" />
      <line x1="11" y1="10" x2="13" y2="14" stroke={color} strokeWidth="2" />
    </svg>
  );
}

/**
 * Diamond - ultimate/rare
 */
export function DiamondIcon({ size = 24, color = '#00FFFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,2 20,8 12,22 4,8" fill={color} />
      <polygon points="12,2 16,8 12,14 8,8" fill="#FFFFFF" opacity="0.3" />
    </svg>
  );
}

/**
 * Explosion/burst - area damage
 */
export function ExplosionIcon({ size = 24, color = '#FF6600', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon
        points="12,2 14,8 20,6 16,12 22,14 16,16 18,22 12,18 6,22 8,16 2,14 8,12 4,6 10,8"
        fill={color}
      />
    </svg>
  );
}

/**
 * Spiral/vortex - AoE/momentum
 */
export function VortexIcon({ size = 24, color = '#9944FF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 4C8 4 4 8 4 12C4 14 5 16 7 17"
        stroke={color}
        strokeWidth="2"
        fill="none"
      />
      <path
        d="M12 8C10 8 8 10 8 12C8 13 8.5 14 9.5 14.5"
        stroke={color}
        strokeWidth="2"
        fill="none"
      />
      <circle cx="12" cy="12" r="2" fill={color} />
      <path
        d="M12 20C16 20 20 16 20 12C20 10 19 8 17 7"
        stroke={color}
        strokeWidth="2"
        fill="none"
      />
    </svg>
  );
}

/**
 * Rocket - momentum/dash
 */
export function RocketIcon({ size = 24, color = '#FF8800', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2L8 8L8 16L12 22L16 16L16 8L12 2Z"
        fill={color}
      />
      {/* Fins */}
      <polygon points="8,12 4,16 8,16" fill={color} />
      <polygon points="16,12 20,16 16,16" fill={color} />
      {/* Window */}
      <circle cx="12" cy="10" r="2" fill="#1A1A1A" />
    </svg>
  );
}

/**
 * Muscle/strength - power abilities
 */
export function StrengthIcon({ size = 24, color = '#FF4444', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Fist shape */}
      <rect x="8" y="6" width="8" height="12" rx="2" fill={color} />
      <rect x="6" y="10" width="3" height="6" rx="1" fill={color} />
      <rect x="15" y="10" width="3" height="6" rx="1" fill={color} />
      {/* Knuckle lines */}
      <line x1="10" y1="8" x2="10" y2="10" stroke="#1A1A1A" strokeWidth="1" />
      <line x1="12" y1="8" x2="12" y2="10" stroke="#1A1A1A" strokeWidth="1" />
      <line x1="14" y1="8" x2="14" y2="10" stroke="#1A1A1A" strokeWidth="1" />
    </svg>
  );
}

/**
 * Timer/clock - cooldown abilities
 */
export function TimerIcon({ size = 24, color = '#FFAA00', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="12" cy="13" r="9" stroke={color} strokeWidth="2" fill="none" />
      <line x1="12" y1="13" x2="12" y2="7" stroke={color} strokeWidth="2" />
      <line x1="12" y1="13" x2="16" y2="13" stroke={color} strokeWidth="2" />
      <rect x="10" y="2" width="4" height="2" fill={color} />
    </svg>
  );
}

/**
 * Butterfly - metamorphosis/transformation
 */
export function ButterflyIcon({ size = 24, color = '#FF88FF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Wings */}
      <ellipse cx="7" cy="10" rx="5" ry="6" fill={color} />
      <ellipse cx="17" cy="10" rx="5" ry="6" fill={color} />
      <ellipse cx="7" cy="16" rx="3" ry="4" fill={color} opacity="0.7" />
      <ellipse cx="17" cy="16" rx="3" ry="4" fill={color} opacity="0.7" />
      {/* Body */}
      <ellipse cx="12" cy="12" rx="1.5" ry="6" fill="#1A1A1A" />
    </svg>
  );
}

/**
 * Coffin - revive/death prevention
 */
export function CoffinIcon({ size = 24, color = '#666666', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,2 8,6 8,20 10,22 14,22 16,20 16,6" fill={color} />
      <line x1="12" y1="8" x2="12" y2="16" stroke="#1A1A1A" strokeWidth="2" />
      <line x1="9" y1="11" x2="15" y2="11" stroke="#1A1A1A" strokeWidth="2" />
    </svg>
  );
}

/**
 * Vampire fangs - lifesteal
 */
export function VampireIcon({ size = 24, color = '#AA0000', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Fangs */}
      <polygon points="8,6 6,16 10,12" fill={color} />
      <polygon points="16,6 18,16 14,12" fill={color} />
      {/* Blood drop */}
      <ellipse cx="12" cy="18" rx="2" ry="3" fill={color} />
    </svg>
  );
}

/**
 * Turtle shell - slow/tank
 */
export function TurtleIcon({ size = 24, color = '#228822', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Shell */}
      <ellipse cx="12" cy="12" rx="9" ry="7" fill={color} />
      {/* Pattern */}
      <line x1="12" y1="5" x2="12" y2="19" stroke="#1A1A1A" strokeWidth="1" />
      <line x1="6" y1="9" x2="18" y2="9" stroke="#1A1A1A" strokeWidth="1" />
      <line x1="6" y1="15" x2="18" y2="15" stroke="#1A1A1A" strokeWidth="1" />
      {/* Head */}
      <ellipse cx="20" cy="12" rx="2" ry="1.5" fill="#448844" />
    </svg>
  );
}

/**
 * Sync/refresh - cooldown reduction
 */
export function RefreshIcon({ size = 24, color = '#00AAFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 4C7.6 4 4 7.6 4 12C4 14.2 4.8 16.2 6.2 17.6"
        stroke={color}
        strokeWidth="2"
        fill="none"
      />
      <path
        d="M12 20C16.4 20 20 16.4 20 12C20 9.8 19.2 7.8 17.8 6.4"
        stroke={color}
        strokeWidth="2"
        fill="none"
      />
      <polygon points="4,8 4,16 8,12" fill={color} />
      <polygon points="20,8 20,16 16,12" fill={color} />
    </svg>
  );
}

/**
 * Wind/dash - movement abilities
 */
export function WindIcon({ size = 24, color = '#88DDFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M4 8H14C16 8 18 6 18 4" stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M4 12H18C20 12 22 14 22 16" stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" />
      <path d="M4 16H12C14 16 16 18 16 20" stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  );
}

/**
 * Sparkle - special effect
 */
export function SparkleIcon({ size = 24, color = '#FFFF00', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,2 13,10 22,12 13,14 12,22 11,14 2,12 11,10" fill={color} />
    </svg>
  );
}

// =============================================================================
// UI Section Icons
// =============================================================================

/**
 * Chart/stats icon
 */
export function ChartIcon({ size = 24, color = '#FFD700', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect x="3" y="14" width="4" height="8" fill={color} />
      <rect x="10" y="8" width="4" height="14" fill={color} />
      <rect x="17" y="4" width="4" height="18" fill={color} />
    </svg>
  );
}

/**
 * Mask/persona icon - build identity
 */
export function MaskIcon({ size = 24, color = '#9944FF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2C6 2 2 8 2 12C2 14 4 16 6 16L8 14C9 15 11 16 12 16C13 16 15 15 16 14L18 16C20 16 22 14 22 12C22 8 18 2 12 2Z"
        fill={color}
      />
      <ellipse cx="8" cy="10" rx="2" ry="3" fill="#1A1A1A" />
      <ellipse cx="16" cy="10" rx="2" ry="3" fill="#1A1A1A" />
    </svg>
  );
}

/**
 * Ghost icon - paths not taken
 */
export function GhostIcon({ size = 24, color = '#88CCFF', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 2C7 2 4 6 4 10V20L6 18L8 20L10 18L12 20L14 18L16 20L18 18L20 20V10C20 6 17 2 12 2Z"
        fill={color}
        opacity="0.7"
      />
      <circle cx="9" cy="10" r="2" fill="#1A1A1A" />
      <circle cx="15" cy="10" r="2" fill="#1A1A1A" />
    </svg>
  );
}

// =============================================================================
// Warning Icons
// =============================================================================

/**
 * Warning triangle
 */
export function WarningIcon({ size = 24, color = '#FFAA00', className = '' }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="12,2 2,22 22,22" fill={color} />
      <rect x="11" y="8" width="2" height="8" fill="#1A1A1A" />
      <rect x="11" y="18" width="2" height="2" fill="#1A1A1A" />
    </svg>
  );
}

// =============================================================================
// Ability Icon Mapping
// =============================================================================

/**
 * Map of ability icon IDs to their SVG components
 * This replaces the emoji-based icons in abilities.ts
 */
export const ABILITY_ICONS: Record<string, React.ComponentType<IconProps>> = {
  // Damage
  strength: StrengthIcon,
  skull: SkullIcon,
  sword: SwordIcon,
  flame: FlameIcon,
  target: TargetIcon,
  lightning: LightningIcon,
  explosion: ExplosionIcon,
  poison: PoisonIcon,
  chain: ChainIcon,

  // Speed
  speed: SpeedIcon,
  wind: WindIcon,
  butterfly: ButterflyIcon,
  rocket: RocketIcon,
  refresh: RefreshIcon,
  timer: TimerIcon,

  // Defense
  shield: ShieldIcon,
  turtle: TurtleIcon,
  heart: HeartIcon,
  vampire: VampireIcon,
  coffin: CoffinIcon,

  // Special
  star: StarIcon,
  sparkle: SparkleIcon,
  diamond: DiamondIcon,
  vortex: VortexIcon,
};

/**
 * Get the icon component for an ability icon ID
 */
export function getAbilityIcon(iconId: string): React.ComponentType<IconProps> {
  return ABILITY_ICONS[iconId] || StarIcon;
}
