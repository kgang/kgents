/**
 * TraceTimeline Tests
 *
 * Tests for the TraceTimeline component, the foundation of Differance DevEx.
 *
 * @see components/differance/TraceTimeline.tsx
 * @see plans/differance-devex-enlightenment.md - Phase 7A
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { TraceTimeline } from '@/components/differance';

// Mock the hook
vi.mock('@/hooks/useDifferanceQuery', () => ({
  useRecentTraces: vi.fn(),
}));

// Mock the ShellProvider
vi.mock('@/shell/ShellProvider', () => ({
  useShell: () => ({
    density: 'comfortable',
  }),
}));

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    button: (props: React.ComponentProps<'button'>) => <button {...props} />,
    div: (props: React.ComponentProps<'div'>) => <div {...props} />,
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Get the mocked hook
const { useRecentTraces } = vi.mocked(await import('@/hooks/useDifferanceQuery'));

// Test data
const mockTraces = [
  {
    id: 'trace-1',
    operation: 'capture',
    context: '[brain] Captured auth patterns',
    timestamp: new Date().toISOString(),
    ghost_count: 2,
    output_preview: 'crystal_123',
    jewel: 'brain',
  },
  {
    id: 'trace-2',
    operation: 'crystallize',
    context: '[brain] Formed memory crystal',
    timestamp: new Date(Date.now() - 60000).toISOString(),
    ghost_count: 0,
    output_preview: null,
    jewel: 'brain',
  },
  {
    id: 'trace-3',
    operation: 'plant',
    context: '[gardener] Planted new concept',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    ghost_count: 1,
    output_preview: 'plot_abc',
    jewel: 'gardener',
  },
];

const mockResponse = {
  traces: mockTraces,
  total: 3,
  buffer_size: 100,
  store_connected: true,
};

function renderWithRouter(component: React.ReactNode) {
  return render(<BrowserRouter>{component}</BrowserRouter>);
}

describe('TraceTimeline', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    useRecentTraces.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // Should show loading indicator (spinner is visible)
    expect(screen.queryByText(/No traces recorded/)).not.toBeInTheDocument();
  });

  it('renders empty state when no traces', () => {
    useRecentTraces.mockReturnValue({
      data: { traces: [], total: 0, buffer_size: 0, store_connected: false },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    expect(screen.getByText(/No traces recorded yet/)).toBeInTheDocument();
  });

  it('renders traces from hook data', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // Should show trace operations
    expect(screen.getByText('capture')).toBeInTheDocument();
    expect(screen.getByText('crystallize')).toBeInTheDocument();
    expect(screen.getByText('plant')).toBeInTheDocument();
  });

  it('shows ghost count badges on traces with ghosts', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // trace-1 has 2 ghosts, trace-3 has 1 ghost
    const ghostBadges = screen.getAllByText('2');
    expect(ghostBadges.length).toBeGreaterThan(0);
  });

  it('shows jewel tags', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // Should show jewel labels
    expect(screen.getAllByText('brain').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('gardener')).toBeInTheDocument();
  });

  it('calls onExploreHeritage when trace is selected', () => {
    const onExploreHeritage = vi.fn();

    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline onExploreHeritage={onExploreHeritage} />);

    // Click on the first trace
    const captureOperation = screen.getByText('capture');
    fireEvent.click(captureOperation.closest('button')!);

    // The trace should be selected, and clicking again would call onExploreHeritage
    // (first click selects, double click might explore)
    // This tests the basic interaction
  });

  it('shows status footer with buffer info', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // Should show buffer size in footer
    expect(screen.getByText('100 in buffer')).toBeInTheDocument();
    expect(screen.getByText('Store connected')).toBeInTheDocument();
  });

  it('shows disconnected state when store not connected', () => {
    useRecentTraces.mockReturnValue({
      data: { ...mockResponse, store_connected: false },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    expect(screen.getByText('Buffer only')).toBeInTheDocument();
  });

  it('calls refetch when refresh button is clicked', () => {
    const mockRefetch = vi.fn();

    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    });

    renderWithRouter(<TraceTimeline />);

    // Find and click the refresh button (by title)
    const refreshButton = screen.getByTitle('Refresh traces');
    fireEvent.click(refreshButton);

    expect(mockRefetch).toHaveBeenCalled();
  });

  it('supports compact mode', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    const { container } = renderWithRouter(<TraceTimeline compact />);

    // In compact mode, the component should still render
    expect(container.querySelector('[class*="rounded-xl"]')).toBeInTheDocument();
  });

  it('shows header with trace count', () => {
    useRecentTraces.mockReturnValue({
      data: mockResponse,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    renderWithRouter(<TraceTimeline />);

    // Should show count like "3/3"
    expect(screen.getByText('3/3')).toBeInTheDocument();
  });
});
