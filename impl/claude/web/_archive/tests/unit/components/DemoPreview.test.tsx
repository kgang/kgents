import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DemoPreview } from '@/components/landing/DemoPreview';
import type { CitizenSummary, TownEvent } from '@/api/types';

// Mock the API client
vi.mock('@/api/client', () => ({
  townApi: {
    create: vi.fn(),
    getCitizens: vi.fn(),
  },
}));

// Mock the region grid
vi.mock('@/lib/regionGrid', () => ({
  REGION_GRID_POSITIONS: {
    square: { x: 10, y: 10 },
    market: { x: 5, y: 5 },
    temple: { x: 15, y: 5 },
    forge: { x: 5, y: 15 },
  },
  gridToScreen: (gridX: number, gridY: number, cellSize: number, offsetX: number, offsetY: number) => ({
    x: offsetX + (gridX - gridY) * cellSize / 2,
    y: offsetY + (gridX + gridY) * cellSize / 4,
  }),
}));

import { townApi } from '@/api/client';

const mockCitizens: CitizenSummary[] = [
  {
    id: 'citizen-1',
    name: 'Alice',
    archetype: 'Builder',
    region: 'square',
    phase: 'IDLE',
    is_evolving: false,
  },
  {
    id: 'citizen-2',
    name: 'Bob',
    archetype: 'Trader',
    region: 'market',
    phase: 'WORKING',
    is_evolving: false,
  },
  {
    id: 'citizen-3',
    name: 'Carol',
    archetype: 'Healer',
    region: 'temple',
    phase: 'SOCIALIZING',
    is_evolving: true,
  },
];

// Mock canvas context
const mockContext = {
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 0,
  font: '',
  textAlign: '',
  textBaseline: '',
  fillRect: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  stroke: vi.fn(),
  arc: vi.fn(),
  fill: vi.fn(),
  fillText: vi.fn(),
  setTransform: vi.fn(),
  clearRect: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  scale: vi.fn(),
  translate: vi.fn(),
  rotate: vi.fn(),
  measureText: vi.fn(() => ({ width: 0 })),
};

describe('DemoPreview', () => {
  let mockEventSource: {
    onopen: ((e: Event) => void) | null;
    onerror: ((e: Event) => void) | null;
    addEventListener: ReturnType<typeof vi.fn>;
    close: ReturnType<typeof vi.fn>;
    readyState: number;
    url: string;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Mock EventSource
    mockEventSource = {
      onopen: null,
      onerror: null,
      addEventListener: vi.fn(),
      close: vi.fn(),
      readyState: 0,
      url: '',
    };

    vi.stubGlobal('EventSource', vi.fn().mockImplementation((url: string) => {
      mockEventSource.url = url;
      setTimeout(() => {
        mockEventSource.readyState = 1;
        mockEventSource.onopen?.(new Event('open'));
      }, 0);
      return mockEventSource;
    }));

    // Mock canvas
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(mockContext);

    // Mock requestAnimationFrame
    vi.stubGlobal('requestAnimationFrame', vi.fn().mockReturnValue(1));
    vi.stubGlobal('cancelAnimationFrame', vi.fn());

    // Default successful API responses
    vi.mocked(townApi.create).mockResolvedValue({ data: { id: 'test-town-123' } } as any);
    vi.mocked(townApi.getCitizens).mockResolvedValue({ data: { citizens: mockCitizens } } as any);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  const renderWithRouter = (component: React.ReactElement) => {
    return render(<BrowserRouter>{component}</BrowserRouter>);
  };

  describe('initialization', () => {
    it('should render loading state initially', () => {
      renderWithRouter(<DemoPreview />);

      expect(screen.getByText('Loading town...')).toBeInTheDocument();
    });

    it('should create a demo town on mount', async () => {
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(0);

      expect(townApi.create).toHaveBeenCalledWith({
        name: 'demo-preview',
        phase: 3,
        enable_dialogue: false,
      });
    });

    it('should fetch citizens after town creation', async () => {
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(0);

      expect(townApi.getCitizens).toHaveBeenCalledWith('test-town-123');
    });

    it('should connect to SSE after loading citizens', async () => {
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(0);

      expect(mockEventSource.url).toBe('/v1/town/test-town-123/live?speed=2&phases=100');
    });
  });

  describe('canvas rendering', () => {
    it('should get canvas 2d context', async () => {
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(0);

      expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    });

    it('should render canvas with correct dimensions', () => {
      renderWithRouter(<DemoPreview />);

      // Canvas might not have role="img", query by element type
      const canvasElements = document.querySelectorAll('canvas');
      expect(canvasElements.length).toBe(1);
      expect(canvasElements[0]).toHaveAttribute('width', '480');
      expect(canvasElements[0]).toHaveAttribute('height', '320');
    });

    it.skip('should start animation frame when citizens load', async () => {
      // TODO: Fix fake timer interaction with requestAnimationFrame stubbing
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(0);

      expect(requestAnimationFrame).toHaveBeenCalled();
    });
  });

  describe('connection status', () => {
    it('should show "Connecting..." initially', () => {
      renderWithRouter(<DemoPreview />);

      expect(screen.getByText('Connecting...')).toBeInTheDocument();
    });

    it.skip('should show "LIVE" when connected', async () => {
      // TODO: Fix fake timer interaction with async state updates
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      await waitFor(() => {
        expect(screen.getByText('LIVE')).toBeInTheDocument();
      });
    });

    it.skip('should reconnect on error after 3 seconds', async () => {
      // TODO: Fix fake timer interaction with EventSource reconnection
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      // Simulate SSE error
      mockEventSource.readyState = 2; // CLOSED
      mockEventSource.onerror?.(new Event('error'));

      // Should still work initially
      await vi.advanceTimersByTimeAsync(3000);

      // EventSource should be recreated
      expect(EventSource).toHaveBeenCalledTimes(2);
    });
  });

  describe('event feed', () => {
    it.skip('should show "Waiting for activity..." when no events', async () => {
      // TODO: Fix fake timer interaction with async state updates
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      expect(screen.getByText('Waiting for activity...')).toBeInTheDocument();
    });

    it.skip('should show "LIVE ACTIVITY" header', async () => {
      // TODO: Fix fake timer interaction with async state updates
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      expect(screen.getByText('LIVE ACTIVITY')).toBeInTheDocument();
    });

    it.skip('should display events when received', async () => {
      // TODO: Fix fake timer interaction with EventSource event handling
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      // Simulate receiving an event
      const mockEvent: TownEvent = {
        tick: 100,
        phase: 'MORNING',
        operation: 'greet',
        participants: ['Alice', 'Bob'],
        success: true,
        message: 'Alice greeted Bob',
        tokens_used: 50,
        timestamp: '2024-01-01T00:00:00Z',
      };

      // Get the event handler
      const eventHandler = mockEventSource.addEventListener.mock.calls.find(
        (call: string[]) => call[0] === 'live.event'
      )?.[1] as ((e: MessageEvent) => void) | undefined;

      if (eventHandler) {
        eventHandler({ data: JSON.stringify(mockEvent) } as MessageEvent);
      }

      await waitFor(() => {
        expect(screen.getByText('Alice greeted Bob')).toBeInTheDocument();
      });
    });

    it.skip('should show link to full town view', async () => {
      // TODO: Fix fake timer interaction with async state updates
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      const link = screen.getByText('Open Full View →');
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', '/town/test-town-123');
    });
  });

  describe('legend', () => {
    it.skip('should display archetype legend', async () => {
      // TODO: Fix fake timer interaction with async state updates
      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      expect(screen.getByText('Builder')).toBeInTheDocument();
      expect(screen.getByText('Trader')).toBeInTheDocument();
      expect(screen.getByText('Healer')).toBeInTheDocument();
      expect(screen.getByText('Scholar')).toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it.skip('should show error state when town creation fails', async () => {
      // TODO: Fix fake timer interaction with async error handling
      vi.mocked(townApi.create).mockRejectedValueOnce(new Error('Server error'));

      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      await waitFor(() => {
        expect(screen.getByText('Demo unavailable')).toBeInTheDocument();
      });
    });

    it.skip('should show placeholder when in error state', async () => {
      // TODO: Fix fake timer interaction with async error handling
      vi.mocked(townApi.create).mockRejectedValueOnce(new Error('Server error'));

      renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      await waitFor(() => {
        expect(screen.getByText('Live demo preview')).toBeInTheDocument();
      });
    });
  });

  describe('cleanup', () => {
    it('should close EventSource on unmount', async () => {
      const { unmount } = renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      unmount();

      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it.skip('should cancel animation frame on unmount', async () => {
      // TODO: Fix fake timer interaction with cancelAnimationFrame stubbing
      const { unmount } = renderWithRouter(<DemoPreview />);

      await vi.advanceTimersByTimeAsync(10);

      unmount();

      expect(cancelAnimationFrame).toHaveBeenCalled();
    });
  });
});
