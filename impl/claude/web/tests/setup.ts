import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';
import { enableMapSet } from 'immer';

// Enable Immer's MapSet plugin for Map/Set support
enableMapSet();

// =============================================================================
// Heavy Dependency Mocks (Prevent 4GB per worker)
// =============================================================================

// Mock pixi.js - prevents loading 29MB dep for canvas tests
vi.mock('pixi.js', () => ({
  Application: vi.fn(),
  Container: vi.fn(),
  Graphics: vi.fn(),
  Text: vi.fn(),
  TextStyle: vi.fn(),
  Sprite: vi.fn(),
  Texture: vi.fn(),
}));

vi.mock('@pixi/react', () => ({
  Stage: ({ children }: { children?: React.ReactNode }) => children,
  Container: ({ children }: { children?: React.ReactNode }) => children,
  Graphics: () => null,
  Text: () => null,
  Sprite: () => null,
}));

// Mock three.js ecosystem - prevents loading 66MB for 3D tests
vi.mock('three', () => ({}));
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children?: React.ReactNode }) => children,
  useFrame: vi.fn(),
  useThree: vi.fn(() => ({ camera: {}, scene: {}, gl: {} })),
}));
vi.mock('@react-three/drei', () => ({
  OrbitControls: () => null,
  Environment: () => null,
  Text: () => null,
  Html: ({ children }: { children?: React.ReactNode }) => children,
}));
vi.mock('@react-three/postprocessing', () => ({
  EffectComposer: ({ children }: { children?: React.ReactNode }) => children,
  Bloom: () => null,
}));

// Mock useMotionPreferences for animation tests
vi.mock('@/components/joy/useMotionPreferences', () => ({
  useMotionPreferences: () => ({ shouldAnimate: false }),
}));

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Reset mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
// CRITICAL: Must call callback with proper dimensions for layout context to work
// Without this, useLayoutMeasure never updates context, causing layout-dependent
// components (CitizenCard, etc.) to render with default/constrained context.
//
// NOTE: We call the callback SYNCHRONOUSLY to ensure layout context is updated
// before test assertions run. Real ResizeObserver is async, but tests need
// deterministic behavior.
class MockResizeObserver implements ResizeObserver {
  private callback: ResizeObserverCallback;
  private observedElements: Set<Element> = new Set();

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback;
  }

  observe(target: Element) {
    this.observedElements.add(target);
    // Simulate spacious desktop viewport (1280x800) for test stability
    // Tests that need different dimensions can override this mock
    const entry: ResizeObserverEntry = {
      target,
      contentRect: { width: 1280, height: 800 } as DOMRectReadOnly,
      borderBoxSize: [{ blockSize: 800, inlineSize: 1280 }] as unknown as readonly ResizeObserverSize[],
      contentBoxSize: [{ blockSize: 800, inlineSize: 1280 }] as unknown as readonly ResizeObserverSize[],
      devicePixelContentBoxSize: [
        { blockSize: 800, inlineSize: 1280 },
      ] as unknown as readonly ResizeObserverSize[],
    };
    // Call callback SYNCHRONOUSLY for deterministic test behavior
    this.callback([entry], this);
  }

  unobserve(target: Element) {
    this.observedElements.delete(target);
  }

  disconnect() {
    this.observedElements.clear();
  }
}
window.ResizeObserver = MockResizeObserver;

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
window.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;

// Mock crypto.randomUUID
if (!crypto.randomUUID) {
  crypto.randomUUID = vi.fn(
    () =>
      `${Math.random().toString(36).substring(2)}-${Math.random().toString(36).substring(2)}-${Math.random().toString(36).substring(2)}-${Math.random().toString(36).substring(2)}-${Math.random().toString(36).substring(2)}`
  ) as unknown as () => `${string}-${string}-${string}-${string}-${string}`;
}

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock EventSource for SSE tests
class MockEventSource {
  url: string;
  readyState = 0;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSED = 2;

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      this.readyState = 1;
      this.onopen?.(new Event('open'));
    }, 0);
  }

  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  close = vi.fn(() => {
    this.readyState = 2;
  });
  dispatchEvent = vi.fn();
}
window.EventSource = MockEventSource as unknown as typeof EventSource;
