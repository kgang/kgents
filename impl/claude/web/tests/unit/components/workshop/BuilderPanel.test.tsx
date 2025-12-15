import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BuilderPanel } from '@/components/workshop/BuilderPanel';
import { useWorkshopStore } from '@/stores/workshopStore';
import { useUserStore } from '@/stores/userStore';
import { workshopApi } from '@/api/client';
import type { BuilderSummary } from '@/api/types';

// Mock API client
vi.mock('@/api/client', () => ({
  workshopApi: {
    whisper: vi.fn(),
  },
}));

// Helper to create mock builder
const createMockBuilder = (
  archetype: string,
  overrides: Partial<BuilderSummary> = {}
): BuilderSummary => ({
  archetype: archetype as BuilderSummary['archetype'],
  name: archetype,
  phase: 'IDLE' as BuilderSummary['phase'],
  is_active: false,
  is_in_specialty: false,
  ...overrides,
});

describe('BuilderPanel', () => {
  beforeEach(() => {
    // Reset stores
    useWorkshopStore.setState({
      builders: [
        createMockBuilder('Scout'),
        createMockBuilder('Sage'),
        createMockBuilder('Spark'),
        createMockBuilder('Steady'),
        createMockBuilder('Sync'),
      ],
      selectedBuilder: null,
    });

    useUserStore.setState({
      tier: 'RESIDENT',
    });

    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('without selection', () => {
    it('should show placeholder when no builder selected', () => {
      render(<BuilderPanel />);
      expect(screen.getByText(/click a builder on the canvas/i)).toBeInTheDocument();
    });

    it('should show available builders list', () => {
      render(<BuilderPanel />);
      // Text includes icon + name, use regex for flexible matching
      expect(screen.getByText(/Scout/)).toBeInTheDocument();
      expect(screen.getByText(/Sage/)).toBeInTheDocument();
      expect(screen.getByText(/Spark/)).toBeInTheDocument();
      expect(screen.getByText(/Steady/)).toBeInTheDocument();
      expect(screen.getByText(/Sync/)).toBeInTheDocument();
    });

    it('should allow selecting builder from list', async () => {
      render(<BuilderPanel />);
      // Click the button containing "Scout"
      fireEvent.click(screen.getByText(/Scout/));

      await waitFor(() => {
        expect(useWorkshopStore.getState().selectedBuilder).toBe('Scout');
      });
    });
  });

  describe('with selection', () => {
    beforeEach(() => {
      useWorkshopStore.setState({
        selectedBuilder: 'Scout',
      });
    });

    it('should show builder name and archetype', () => {
      render(<BuilderPanel />);
      // Multiple elements may have "Scout" - check at least one exists
      expect(screen.getAllByText('Scout').length).toBeGreaterThan(0);
      expect(screen.getByText('🔍')).toBeInTheDocument(); // Scout icon
    });

    it('should show status section', () => {
      render(<BuilderPanel />);
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Phase')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('In Specialty')).toBeInTheDocument();
    });

    it('should show specialty description', () => {
      render(<BuilderPanel />);
      expect(screen.getByText('Specialty')).toBeInTheDocument();
      expect(screen.getByText(/exploration.*research/i)).toBeInTheDocument();
    });

    it('should have whisper input', () => {
      render(<BuilderPanel />);
      expect(screen.getByPlaceholderText(/say something/i)).toBeInTheDocument();
    });

    it('should allow deselecting builder', () => {
      render(<BuilderPanel />);
      fireEvent.click(screen.getByText('✕'));

      expect(useWorkshopStore.getState().selectedBuilder).toBeNull();
    });

    it('should send whisper on button click', async () => {
      (workshopApi.whisper as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: {
          success: true,
          builder: 'Scout',
          response: '*Scout acknowledges*',
        },
      });

      render(<BuilderPanel />);

      const input = screen.getByPlaceholderText(/say something/i);
      fireEvent.change(input, { target: { value: 'Hello Scout!' } });

      const whisperButton = screen.getByText('💬');
      fireEvent.click(whisperButton);

      await waitFor(() => {
        expect(workshopApi.whisper).toHaveBeenCalledWith('Scout', 'Hello Scout!');
      });
    });

    it('should send whisper on enter key', async () => {
      (workshopApi.whisper as ReturnType<typeof vi.fn>).mockResolvedValue({
        data: {
          success: true,
          builder: 'Scout',
          response: '*Scout acknowledges*',
        },
      });

      render(<BuilderPanel />);

      const input = screen.getByPlaceholderText(/say something/i);
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyDown(input, { key: 'Enter' });

      await waitFor(() => {
        expect(workshopApi.whisper).toHaveBeenCalledWith('Scout', 'Test message');
      });
    });
  });

  describe('builder states', () => {
    it('should show active state', () => {
      useWorkshopStore.setState({
        selectedBuilder: 'Scout',
        builders: [
          createMockBuilder('Scout', { is_active: true }),
          createMockBuilder('Sage'),
          createMockBuilder('Spark'),
          createMockBuilder('Steady'),
          createMockBuilder('Sync'),
        ],
      });

      render(<BuilderPanel />);
      expect(screen.getByText('Yes')).toBeInTheDocument();
    });

    it('should show in-specialty state', () => {
      useWorkshopStore.setState({
        selectedBuilder: 'Scout',
        builders: [
          createMockBuilder('Scout', { is_in_specialty: true }),
          createMockBuilder('Sage'),
          createMockBuilder('Spark'),
          createMockBuilder('Steady'),
          createMockBuilder('Sync'),
        ],
      });

      render(<BuilderPanel />);
      // Find all "Yes" texts - one should be for in_specialty
      const yesTexts = screen.getAllByText('Yes');
      expect(yesTexts.length).toBeGreaterThan(0);
    });

    it('should show builder phase', () => {
      useWorkshopStore.setState({
        selectedBuilder: 'Scout',
        builders: [
          createMockBuilder('Scout', { phase: 'EXPLORING' }),
          createMockBuilder('Sage'),
          createMockBuilder('Spark'),
          createMockBuilder('Steady'),
          createMockBuilder('Sync'),
        ],
      });

      render(<BuilderPanel />);
      expect(screen.getByText('EXPLORING')).toBeInTheDocument();
    });
  });

  describe('different archetypes', () => {
    const archetypes = [
      { name: 'Scout', specialty: /exploration/i },
      { name: 'Sage', specialty: /architecture/i },
      { name: 'Spark', specialty: /prototyping/i },
      { name: 'Steady', specialty: /refinement/i },
      { name: 'Sync', specialty: /integration/i },
    ];

    archetypes.forEach(({ name, specialty }) => {
      it(`should show ${name} specialty`, () => {
        useWorkshopStore.setState({
          selectedBuilder: name,
        });

        render(<BuilderPanel />);
        expect(screen.getByText(specialty)).toBeInTheDocument();
      });
    });
  });
});
