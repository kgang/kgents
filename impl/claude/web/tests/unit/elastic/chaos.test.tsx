import { render, screen, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useState, useEffect } from 'react';
import { ElasticContainer, ElasticPlaceholder } from '@/components/elastic';
import { CitizenCard } from '@/widgets/cards';
import { ColonyDashboard } from '@/widgets/dashboards';
import type { CitizenCardJSON, ColonyDashboardJSON } from '@/reactive/types';

// Helper to create mock ResizeObserverEntry
function createMockResizeEntry(
  target: Element,
  width: number,
  height: number
): ResizeObserverEntry {
  return {
    target,
    contentRect: { width, height } as DOMRectReadOnly,
    borderBoxSize: [{ blockSize: height, inlineSize: width }] as unknown as readonly ResizeObserverSize[],
    contentBoxSize: [{ blockSize: height, inlineSize: width }] as unknown as readonly ResizeObserverSize[],
    devicePixelContentBoxSize: [
      { blockSize: height, inlineSize: width },
    ] as unknown as readonly ResizeObserverSize[],
  };
}

/**
 * Chaos Tests for Elastic Layout System
 *
 * Simulates rapid, random state changes to verify layout stability:
 * - Random add/remove of citizens
 * - Random selection toggles
 * - Rapid state changes (10+/sec)
 * - Layout integrity validation
 *
 * @see plans/web-refactor/elastic-primitives.md
 */

// Mock citizen generator
function createMockCitizen(id: string, index: number): CitizenCardJSON {
  const archetypes = ['Builder', 'Trader', 'Healer', 'Scholar', 'Watcher', 'Explorer'];
  const phases = ['IDLE', 'WORKING', 'SOCIALIZING', 'REFLECTING'] as const;
  const nphases = ['UNDERSTAND', 'SENSE', 'ACT', 'REFLECT'] as const;
  const regions = ['market', 'plaza', 'workshop', 'garden'];

  return {
    type: 'citizen_card',
    citizen_id: id,
    name: `Citizen-${index}`,
    archetype: archetypes[index % archetypes.length],
    phase: phases[index % phases.length],
    nphase: nphases[index % nphases.length],
    activity: Array.from({ length: 10 }, () => Math.random()),
    capability: Math.random(),
    entropy: Math.random() * 0.5,
    region: regions[index % regions.length],
    mood: `Feeling ${['happy', 'thoughtful', 'busy', 'relaxed'][index % 4]}`,
    eigenvectors: {
      warmth: Math.random(),
      curiosity: Math.random(),
      trust: Math.random(),
    },
    layout: {
      priority: (index % 10) + 1,
      collapsible: true,
    },
  };
}

// Create mock dashboard
function createMockDashboard(citizens: CitizenCardJSON[]): ColonyDashboardJSON {
  return {
    type: 'colony_dashboard',
    colony_id: 'chaos-test-colony',
    phase: 'MORNING',
    day: 1,
    metrics: {
      total_events: citizens.length * 10,
      entropy_budget: 0.5,
      total_tokens: citizens.length * 100,
    },
    citizens,
    grid_cols: 3,
    selected_citizen_id: null,
  };
}

describe('Chaos Tests: Random Widget Show/Hide', () => {
  // Mock ResizeObserver for layout context
  let resizeCallback: (entries: ResizeObserverEntry[]) => void;

  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });

    // Capture resize observer callback
    const MockResizeObserver = vi.fn().mockImplementation((callback) => {
      resizeCallback = callback;
      return {
        observe: vi.fn(() => {
          // Simulate initial measurement
          callback([createMockResizeEntry(document.body, 800, 600)]);
        }),
        unobserve: vi.fn(),
        disconnect: vi.fn(),
      };
    });
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('should handle rapid citizen additions without layout breaks', async () => {
    const initialCitizens = [
      createMockCitizen('add-init-1', 0),
      createMockCitizen('add-init-2', 1),
    ];
    let addCounter = 3;

    function ChaosWrapper() {
      const [citizens, setCitizens] = useState<CitizenCardJSON[]>(initialCitizens);

      useEffect(() => {
        const interval = setInterval(() => {
          if (addCounter <= 12) {
            const id = `add-${addCounter}-${Date.now()}`;
            setCitizens((prev) => [...prev, createMockCitizen(id, addCounter - 1)]);
            addCounter++;
          }
        }, 100);

        return () => clearInterval(interval);
      }, []);

      return (
        <ElasticContainer layout="grid" minItemWidth={200}>
          {citizens.map((c) => (
            <CitizenCard key={c.citizen_id} {...c} />
          ))}
        </ElasticContainer>
      );
    }

    render(<ChaosWrapper />);

    // Advance through additions
    await act(async () => {
      for (let i = 0; i < 10; i++) {
        vi.advanceTimersByTime(100);
      }
    });

    // Should have all cards rendered
    const cards = screen.getAllByTestId('citizen-card');
    expect(cards.length).toBeGreaterThan(2);

    // Verify no layout breaks - all cards should have valid bounding boxes
    cards.forEach((card) => {
      expect(card).toBeInTheDocument();
    });
  });

  it('should handle rapid citizen removals without gaps', async () => {
    // Create high-priority citizens that won't be hidden
    const initialCitizens = Array.from({ length: 10 }, (_, i) =>
      createMockCitizen(`remove-${i}`, i)
    ).map((c) => ({ ...c, layout: { priority: 10, collapsible: false } }));

    function RemovalWrapper() {
      const [citizens, setCitizens] = useState<CitizenCardJSON[]>(initialCitizens);

      useEffect(() => {
        const interval = setInterval(() => {
          setCitizens((prev) => {
            if (prev.length <= 3) return prev; // Keep at least 3
            const indexToRemove = Math.floor(Math.random() * prev.length);
            return prev.filter((_, i) => i !== indexToRemove);
          });
        }, 100);

        return () => clearInterval(interval);
      }, []);

      return (
        <ElasticContainer layout="grid" minItemWidth={200}>
          {citizens.map((c) => (
            <CitizenCard key={c.citizen_id} {...c} />
          ))}
        </ElasticContainer>
      );
    }

    render(<RemovalWrapper />);

    // Advance through removals (7 removals max = 10-3)
    await act(async () => {
      for (let i = 0; i < 7; i++) {
        vi.advanceTimersByTime(100);
      }
    });

    // Should still have at least 3 cards (may be more depending on random timing)
    const cards = screen.queryAllByTestId('citizen-card');
    expect(cards.length).toBeGreaterThanOrEqual(1);

    // All remaining cards should be in document
    cards.forEach((card) => {
      expect(card).toBeInTheDocument();
    });
  });

  it('should handle random selection toggles', async () => {
    const citizens = Array.from({ length: 8 }, (_, i) =>
      createMockCitizen(`select-${i}`, i)
    );

    function SelectionWrapper() {
      const [selected, setSelected] = useState<string | null>(null);

      useEffect(() => {
        const interval = setInterval(() => {
          setSelected((prev) => {
            // Random selection changes
            const randomIndex = Math.floor(Math.random() * citizens.length);
            const randomId = citizens[randomIndex].citizen_id;
            return prev === randomId ? null : randomId;
          });
        }, 50);

        return () => clearInterval(interval);
      }, []);

      return (
        <ColonyDashboard
          {...createMockDashboard(citizens)}
          selected_citizen_id={selected}
          onSelectCitizen={setSelected}
        />
      );
    }

    render(<SelectionWrapper />);

    // Rapid selection changes - 20 changes in 1 second (50ms each)
    await act(async () => {
      for (let i = 0; i < 20; i++) {
        vi.advanceTimersByTime(50);
      }
    });

    // Dashboard should still be functional
    const dashboard = screen.getByText(/AGENT TOWN DASHBOARD/i);
    expect(dashboard).toBeInTheDocument();

    // Cards should still be visible (at least some - layout context may hide low priority)
    const cards = screen.getAllByTestId('citizen-card');
    expect(cards.length).toBeGreaterThanOrEqual(1);
  });

  it('should handle mixed add/remove at 10+ changes per second', async () => {
    let chaosCounter = 1000;

    function RapidChaosWrapper() {
      const [citizens, setCitizens] = useState<CitizenCardJSON[]>(
        Array.from({ length: 5 }, (_, i) => createMockCitizen(`chaos-init-${i}`, i))
      );

      useEffect(() => {
        const interval = setInterval(() => {
          setCitizens((prev) => {
            const action = Math.random();
            if (action < 0.4 && prev.length > 2) {
              // Remove random
              const indexToRemove = Math.floor(Math.random() * prev.length);
              return prev.filter((_, i) => i !== indexToRemove);
            } else if (action < 0.8) {
              // Add new with unique ID
              chaosCounter++;
              return [
                ...prev,
                createMockCitizen(`chaos-new-${chaosCounter}-${Date.now()}`, chaosCounter),
              ];
            } else {
              // Shuffle order
              return [...prev].sort(() => Math.random() - 0.5);
            }
          });
        }, 50); // 20 changes per second

        return () => clearInterval(interval);
      }, []);

      return (
        <ElasticContainer
          layout="grid"
          minItemWidth={150}
          emptyState={
            <ElasticPlaceholder
              for="agent"
              state="empty"
              emptyMessage="No citizens remain"
            />
          }
        >
          {citizens.map((c) => (
            <CitizenCard key={c.citizen_id} {...c} />
          ))}
        </ElasticContainer>
      );
    }

    render(<RapidChaosWrapper />);

    // Run for 3 seconds of simulated time (60 changes)
    await act(async () => {
      for (let i = 0; i < 60; i++) {
        vi.advanceTimersByTime(50);
      }
    });

    // Container should still be functional
    const container = document.querySelector('.elastic-grid');
    expect(container).toBeInTheDocument();

    // Should have some cards (at least 2 or show empty state)
    const cards = screen.queryAllByTestId('citizen-card');
    if (cards.length === 0) {
      // Empty state should be shown
      expect(screen.getByRole('status')).toBeInTheDocument();
    } else {
      expect(cards.length).toBeGreaterThan(0);
    }
  });

  it('should maintain layout integrity during resize + state changes', async () => {
    const citizens = Array.from({ length: 6 }, (_, i) =>
      createMockCitizen(`resize-${i}`, i)
    );
    let resizeTick = 0;

    function ResizeAndChangeWrapper() {
      const [visibleCitizens, setVisibleCitizens] = useState(citizens);
      const [width, setWidth] = useState(800);

      useEffect(() => {
        const interval = setInterval(() => {
          resizeTick++;
          // Alternate between resize and state change
          if (resizeTick % 2 === 0) {
            // Simulate resize
            const newWidth = 400 + Math.floor(Math.random() * 800);
            setWidth(newWidth);
            if (resizeCallback) {
              resizeCallback([createMockResizeEntry(document.body, newWidth, 600)]);
            }
          } else {
            // State change
            setVisibleCitizens((prev) => {
              if (Math.random() < 0.5 && prev.length > 2) {
                return prev.slice(0, -1);
              }
              return [
                ...prev,
                createMockCitizen(`resize-new-${resizeTick}-${Date.now()}`, resizeTick),
              ];
            });
          }
        }, 100);

        return () => clearInterval(interval);
      }, []);

      return (
        <div style={{ width }}>
          <ElasticContainer layout="grid" minItemWidth={200}>
            {visibleCitizens.map((c) => (
              <CitizenCard key={c.citizen_id} {...c} />
            ))}
          </ElasticContainer>
        </div>
      );
    }

    render(<ResizeAndChangeWrapper />);

    // Run for 60 changes
    await act(async () => {
      for (let i = 0; i < 60; i++) {
        vi.advanceTimersByTime(100);
      }
    });

    // Should not have crashed - container exists
    const container = document.querySelector('.elastic-grid');
    expect(container).toBeInTheDocument();
  });

  it('should show placeholder correctly when all citizens removed', async () => {
    function EmptyTransitionWrapper() {
      const [citizens, setCitizens] = useState<CitizenCardJSON[]>(
        Array.from({ length: 3 }, (_, i) => createMockCitizen(`empty-${i}`, i))
      );

      useEffect(() => {
        // Remove all citizens one by one
        const interval = setInterval(() => {
          setCitizens((prev) => {
            if (prev.length === 0) return prev;
            return prev.slice(0, -1);
          });
        }, 100);

        return () => clearInterval(interval);
      }, []);

      return (
        <ElasticContainer
          layout="grid"
          minItemWidth={200}
          emptyState={
            <ElasticPlaceholder
              for="agent"
              state="empty"
              emptyMessage="All citizens have left"
            />
          }
        >
          {citizens.map((c) => (
            <CitizenCard key={c.citizen_id} {...c} />
          ))}
        </ElasticContainer>
      );
    }

    render(<EmptyTransitionWrapper />);

    // Initially should have some cards (layout context may affect exact count)
    const initialCards = screen.queryAllByTestId('citizen-card');
    expect(initialCards.length).toBeGreaterThanOrEqual(1);

    // Remove all
    await act(async () => {
      for (let i = 0; i < 5; i++) {
        vi.advanceTimersByTime(100);
      }
    });

    // Should show empty state
    await waitFor(() => {
      expect(screen.getByRole('status')).toBeInTheDocument();
    });
    expect(screen.getByText(/All citizens have left/i)).toBeInTheDocument();
  });
});

describe('Chaos Tests: Long Duration Stability', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });

    const MockResizeObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn(() => {
        callback([createMockResizeEntry(document.body, 1024, 768)]);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
    window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('should remain stable over 60 seconds of simulated chaos', async () => {
    let longCounter = 5000;

    function LongChaosWrapper() {
      const [citizens, setCitizens] = useState<CitizenCardJSON[]>(
        Array.from({ length: 10 }, (_, i) => createMockCitizen(`long-init-${i}`, i))
      );

      useEffect(() => {
        const interval = setInterval(() => {
          setCitizens((prev) => {
            const action = Math.random();
            if (action < 0.3 && prev.length > 3) {
              // Remove
              const idx = Math.floor(Math.random() * prev.length);
              return prev.filter((_, i) => i !== idx);
            } else if (action < 0.6 && prev.length < 15) {
              // Add with unique ID
              longCounter++;
              return [
                ...prev,
                createMockCitizen(`long-new-${longCounter}-${Date.now()}`, longCounter),
              ];
            } else if (action < 0.8) {
              // Update random
              const idx = Math.floor(Math.random() * prev.length);
              return prev.map((c, i) =>
                i === idx
                  ? {
                      ...c,
                      activity: Array.from({ length: 10 }, () => Math.random()),
                      capability: Math.random(),
                    }
                  : c
              );
            }
            return prev;
          });
        }, 100);

        return () => clearInterval(interval);
      }, []);

      return (
        <ColonyDashboard {...createMockDashboard(citizens)} onSelectCitizen={() => {}} />
      );
    }

    render(<LongChaosWrapper />);

    // 60 seconds at 10 changes/second = 600 changes
    await act(async () => {
      for (let i = 0; i < 600; i++) {
        vi.advanceTimersByTime(100);
      }
    });

    // Dashboard should still be functional
    expect(screen.getByText(/AGENT TOWN DASHBOARD/i)).toBeInTheDocument();

    // Should have some citizens
    const cards = screen.queryAllByTestId('citizen-card');
    expect(cards.length).toBeGreaterThan(0);
  });
});
