/**
 * Easter Eggs
 *
 * Hidden delights that reward exploration.
 * "Easter eggs hidden > announced: discovery is the delight, not the feature list"
 *
 * @see plans/web-refactor/phase5-continuation.md
 * @see meta.md (2025-12-14)
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

interface EasterEggConfig {
  /** Unique identifier */
  id: string;
  /** Whether this egg has been discovered */
  discovered: boolean;
  /** Timestamp of discovery */
  discoveredAt?: number;
}

// =============================================================================
// Storage
// =============================================================================

const STORAGE_KEY = 'kgents_easter_eggs';

/**
 * Get discovered easter eggs from storage.
 */
export function getDiscoveredEggs(): Record<string, EasterEggConfig> {
  if (typeof window === 'undefined') return {};
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

/**
 * Mark an easter egg as discovered.
 */
export function markEggDiscovered(id: string): void {
  if (typeof window === 'undefined') return;
  const eggs = getDiscoveredEggs();
  eggs[id] = {
    id,
    discovered: true,
    discoveredAt: Date.now(),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(eggs));
}

/**
 * Check if an easter egg has been discovered.
 */
export function isEggDiscovered(id: string): boolean {
  const eggs = getDiscoveredEggs();
  return eggs[id]?.discovered ?? false;
}

/**
 * Reset all easter eggs (for testing).
 */
export function resetAllEggs(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(STORAGE_KEY);
  }
}

// =============================================================================
// Konami Code Hook
// =============================================================================

const KONAMI_SEQUENCE = [
  'ArrowUp',
  'ArrowUp',
  'ArrowDown',
  'ArrowDown',
  'ArrowLeft',
  'ArrowRight',
  'ArrowLeft',
  'ArrowRight',
  'KeyB',
  'KeyA',
];

/**
 * Hook that detects the Konami code sequence.
 *
 * @example
 * ```tsx
 * useKonamiCode(() => {
 *   triggerCelebration();
 * });
 * ```
 */
export function useKonamiCode(callback: () => void) {
  const indexRef = useRef(0);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Check if current key matches expected
      if (e.code === KONAMI_SEQUENCE[indexRef.current]) {
        indexRef.current++;

        // Complete sequence
        if (indexRef.current === KONAMI_SEQUENCE.length) {
          markEggDiscovered('konami');
          callback();
          indexRef.current = 0;
        }
      } else {
        // Reset on wrong key
        indexRef.current = 0;
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [callback]);
}

// =============================================================================
// Click Count Hook
// =============================================================================

/**
 * Hook that tracks rapid clicks on an element.
 * Triggers callback when target count is reached.
 *
 * @example
 * ```tsx
 * const { onClick, clickCount } = useClickCounter(7, () => {
 *   console.log('Secret unlocked!');
 * });
 *
 * <div onClick={onClick}>Click me 7 times!</div>
 * ```
 */
export function useClickCounter(targetCount: number, callback: () => void) {
  const [clickCount, setClickCount] = useState(0);
  const timeoutRef = useRef<number | null>(null);

  const onClick = useCallback(() => {
    // Clear existing timeout
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
    }

    setClickCount((prev) => {
      const next = prev + 1;

      if (next >= targetCount) {
        callback();
        return 0;
      }

      return next;
    });

    // Reset count after 2 seconds of no clicks
    timeoutRef.current = window.setTimeout(() => {
      setClickCount(0);
    }, 2000);
  }, [targetCount, callback]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return { onClick, clickCount };
}

// =============================================================================
// Secret Word Hook
// =============================================================================

/**
 * Hook that detects when a secret word is typed.
 *
 * @example
 * ```tsx
 * useSecretWord('coffee', () => {
 *   showCoffeeAnimation();
 * });
 * ```
 */
export function useSecretWord(word: string, callback: () => void) {
  const bufferRef = useRef('');

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Ignore if in input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Add to buffer (lowercase)
      bufferRef.current += e.key.toLowerCase();

      // Keep buffer at reasonable size
      if (bufferRef.current.length > word.length * 2) {
        bufferRef.current = bufferRef.current.slice(-word.length);
      }

      // Check for word
      if (bufferRef.current.includes(word.toLowerCase())) {
        markEggDiscovered(`word_${word}`);
        callback();
        bufferRef.current = '';
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [word, callback]);
}

// =============================================================================
// Double-Click Detection
// =============================================================================

/**
 * Hook for detecting double-click on specific element types.
 *
 * @example
 * ```tsx
 * const handleDoubleClick = useDoubleClickDetector((target) => {
 *   if (target.classList.contains('moon-icon')) {
 *     triggerShootingStar();
 *   }
 * });
 * ```
 */
export function useDoubleClickDetector(callback: (target: HTMLElement) => void) {
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      callback(e.target as HTMLElement);
    };

    document.addEventListener('dblclick', handler);
    return () => document.removeEventListener('dblclick', handler);
  }, [callback]);
}

// =============================================================================
// Celebration Animations
// =============================================================================

/**
 * Trigger a celebration animation.
 * Creates confetti-like particles that burst from center screen.
 */
export function triggerCelebration(): void {
  // Create container
  const container = document.createElement('div');
  container.style.cssText = `
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 9999;
    overflow: hidden;
  `;
  document.body.appendChild(container);

  // Create particles
  const colors = ['#e94560', '#fbbf24', '#34d399', '#60a5fa', '#a78bfa'];
  const particles: HTMLDivElement[] = [];

  for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    const color = colors[Math.floor(Math.random() * colors.length)];
    const size = 8 + Math.random() * 8;
    const angle = (Math.PI * 2 * i) / 50;
    const velocity = 200 + Math.random() * 300;
    const vx = Math.cos(angle) * velocity;
    const vy = Math.sin(angle) * velocity - 200; // Upward bias

    particle.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
    `;

    container.appendChild(particle);
    particles.push(particle);

    // Animate
    const startTime = performance.now();
    const animate = (currentTime: number) => {
      const elapsed = (currentTime - startTime) / 1000;
      const x = vx * elapsed;
      const y = vy * elapsed + 0.5 * 800 * elapsed * elapsed; // Gravity
      const rotation = elapsed * 360;
      const opacity = Math.max(0, 1 - elapsed / 1.5);

      particle.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px)) rotate(${rotation}deg)`;
      particle.style.opacity = String(opacity);

      if (opacity > 0) {
        requestAnimationFrame(animate);
      }
    };
    requestAnimationFrame(animate);
  }

  // Cleanup after animation
  setTimeout(() => {
    container.remove();
  }, 2000);
}

/**
 * Trigger a shooting star animation.
 */
export function triggerShootingStar(): void {
  const star = document.createElement('div');
  star.style.cssText = `
    position: fixed;
    width: 4px;
    height: 4px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 0 10px 2px white, 0 0 20px 4px rgba(255, 255, 255, 0.5);
    top: 20%;
    left: 80%;
    z-index: 9999;
    pointer-events: none;
  `;

  // Trail
  const trail = document.createElement('div');
  trail.style.cssText = `
    position: absolute;
    width: 100px;
    height: 2px;
    background: linear-gradient(to left, white, transparent);
    top: 50%;
    right: 100%;
    transform: translateY(-50%) rotate(-45deg);
    transform-origin: right center;
  `;
  star.appendChild(trail);

  document.body.appendChild(star);

  // Animate
  star.animate(
    [
      { transform: 'translate(0, 0)', opacity: 1 },
      { transform: 'translate(-300px, 300px)', opacity: 0 },
    ],
    {
      duration: 1000,
      easing: 'ease-out',
    }
  ).onfinish = () => {
    star.remove();
  };
}

/**
 * Trigger a coffee animation (for Workshop).
 */
export function triggerCoffeeAnimation(): void {
  const coffee = document.createElement('div');
  coffee.textContent = '☕';
  coffee.style.cssText = `
    position: fixed;
    font-size: 64px;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
    pointer-events: none;
  `;
  document.body.appendChild(coffee);

  // Steam animation
  const steam = document.createElement('div');
  steam.textContent = '~';
  steam.style.cssText = `
    position: absolute;
    font-size: 32px;
    color: rgba(255, 255, 255, 0.6);
    left: 50%;
    top: -20px;
    transform: translateX(-50%);
  `;
  coffee.appendChild(steam);

  // Animate
  coffee.animate(
    [
      { transform: 'translate(-50%, -50%) scale(0)', opacity: 0 },
      { transform: 'translate(-50%, -50%) scale(1.2)', opacity: 1, offset: 0.3 },
      { transform: 'translate(-50%, -50%) scale(1)', opacity: 1, offset: 0.5 },
      { transform: 'translate(-50%, -50%) scale(1)', opacity: 1, offset: 0.8 },
      { transform: 'translate(-50%, -50%) scale(0.8)', opacity: 0 },
    ],
    {
      duration: 2000,
      easing: 'ease-out',
    }
  ).onfinish = () => {
    coffee.remove();
  };

  // Steam float animation
  steam.animate(
    [
      { transform: 'translateX(-50%) translateY(0)', opacity: 0.6 },
      { transform: 'translateX(-50%) translateY(-20px)', opacity: 0 },
    ],
    {
      duration: 1000,
      iterations: 2,
      easing: 'ease-out',
    }
  );
}

// =============================================================================
// Export
// =============================================================================

export const EasterEggs = {
  getDiscovered: getDiscoveredEggs,
  markDiscovered: markEggDiscovered,
  isDiscovered: isEggDiscovered,
  resetAll: resetAllEggs,
  triggerCelebration,
  triggerShootingStar,
  triggerCoffeeAnimation,
};

export default EasterEggs;
