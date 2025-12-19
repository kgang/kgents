import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind classes with clsx.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format credits with thousands separator.
 */
export function formatCredits(credits: number): string {
  return credits.toLocaleString();
}

/**
 * Format time in MM:SS format.
 */
export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format price in USD.
 */
export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(price);
}

/**
 * Get archetype color class.
 */
export function getArchetypeColor(archetype: string): string {
  const colors: Record<string, string> = {
    Builder: 'text-archetype-builder',
    Trader: 'text-archetype-trader',
    Healer: 'text-archetype-healer',
    Scholar: 'text-archetype-scholar',
    Watcher: 'text-archetype-watcher',
  };
  return colors[archetype] || 'text-gray-400';
}

/**
 * Get archetype background color class.
 */
export function getArchetypeBgColor(archetype: string): string {
  const colors: Record<string, string> = {
    Builder: 'bg-archetype-builder',
    Trader: 'bg-archetype-trader',
    Healer: 'bg-archetype-healer',
    Scholar: 'bg-archetype-scholar',
    Watcher: 'bg-archetype-watcher',
  };
  return colors[archetype] || 'bg-gray-400';
}

/**
 * Get phase color class.
 */
export function getPhaseColor(phase: string): string {
  const colors: Record<string, string> = {
    MORNING: 'text-phase-morning',
    AFTERNOON: 'text-phase-afternoon',
    EVENING: 'text-phase-evening',
    NIGHT: 'text-phase-night',
  };
  return colors[phase] || 'text-gray-400';
}

/**
 * Get consent debt status.
 */
export function getConsentStatus(debt: number): {
  label: string;
  color: string;
} {
  if (debt >= 1.0) {
    return { label: 'RUPTURED', color: 'text-red-500' };
  }
  if (debt >= 0.8) {
    return { label: 'CRITICAL', color: 'text-red-400' };
  }
  if (debt >= 0.5) {
    return { label: 'STRAINED', color: 'text-yellow-500' };
  }
  if (debt >= 0.2) {
    return { label: 'TENSE', color: 'text-yellow-400' };
  }
  return { label: 'HARMONIOUS', color: 'text-green-500' };
}

/**
 * Debounce function.
 */
export function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Throttle function.
 */
export function throttle<T extends (...args: unknown[]) => void>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
