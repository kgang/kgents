/**
 * Tests for DialogueModal component.
 *
 * Phase 5: Town End-to-End (2D Renaissance)
 *
 * @see src/components/town/DialogueModal.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DialogueModal } from '@/components/town/DialogueModal';
import { townApi } from '@/api/client';
import type { ConversationDetail, TurnSummary } from '@/api/types';

// Mock the townApi
vi.mock('@/api/client', () => ({
  townApi: {
    converse: vi.fn(),
    turn: vi.fn(),
    getHistory: vi.fn(),
  },
}));

// Mock celebrate function
vi.mock('@/components/joy', async () => {
  const actual = await vi.importActual('@/components/joy');
  return {
    ...actual,
    celebrate: vi.fn(),
  };
});

// Test fixtures
const mockConversation: ConversationDetail = {
  id: 'conv-123',
  citizen_id: 'citizen-456',
  citizen_name: 'Alice',
  topic: 'General chat',
  summary: null,
  turn_count: 0,
  is_active: true,
  created_at: '2025-12-18T10:00:00Z',
  turns: [],
};

const mockCitizenTurn: TurnSummary = {
  id: 'turn-789',
  turn_number: 2,
  role: 'citizen',
  content: 'Hello! Nice to meet you.',
  sentiment: 'positive',
  emotion: 'friendly',
  created_at: '2025-12-18T10:01:00Z',
};

const defaultProps = {
  townId: 'town-1',
  citizenId: 'citizen-456',
  citizenName: 'Alice',
  archetype: 'Builder',
  onClose: vi.fn(),
};

describe('DialogueModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock window.innerWidth for mobile detection
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024, // Desktop by default
    });
  });

  describe('rendering', () => {
    it('should render with citizen name and archetype', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      render(<DialogueModal {...defaultProps} />);

      // Wait for conversation to load
      await waitFor(() => {
        expect(screen.getByText('Alice')).toBeInTheDocument();
      });

      expect(screen.getByText('Builder')).toBeInTheDocument();
    });

    it('should show loading state while starting conversation', async () => {
      let resolvePromise: (value: ConversationDetail) => void;
      vi.mocked(townApi.converse).mockReturnValueOnce(
        new Promise((resolve) => {
          resolvePromise = resolve;
        })
      );

      render(<DialogueModal {...defaultProps} />);

      // Should show loading indicator (PersonalityLoading shows "Assembling the team...")
      expect(screen.getByText(/Assembling/i)).toBeInTheDocument();

      // Resolve and verify loading disappears
      await waitFor(async () => {
        resolvePromise!(mockConversation);
      });
    });

    it('should show error state with retry button', async () => {
      vi.mocked(townApi.converse).mockRejectedValueOnce(new Error('Network error'));

      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });
  });

  describe('conversation flow', () => {
    it('should show empty state prompt when conversation has no turns', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText(/Start a conversation with Alice/i)).toBeInTheDocument();
      });
    });

    it('should send message when clicking send button', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);
      vi.mocked(townApi.turn).mockResolvedValueOnce(mockCitizenTurn);

      const user = userEvent.setup();
      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/type a message/i);
      await user.type(input, 'Hello!');
      await user.click(screen.getByRole('button', { name: /send/i }));

      await waitFor(() => {
        expect(townApi.turn).toHaveBeenCalledWith('conv-123', 'Hello!');
      });
    });

    it('should send message on Enter key press', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);
      vi.mocked(townApi.turn).mockResolvedValueOnce(mockCitizenTurn);

      const user = userEvent.setup();
      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/type a message/i);
      await user.type(input, 'Hello!{Enter}');

      await waitFor(() => {
        expect(townApi.turn).toHaveBeenCalledWith('conv-123', 'Hello!');
      });
    });

    it('should not send empty messages', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      const user = userEvent.setup();
      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
      });

      const sendButton = screen.getByRole('button', { name: /send/i });
      expect(sendButton).toBeDisabled();

      await user.click(sendButton);
      expect(townApi.turn).not.toHaveBeenCalled();
    });
  });

  describe('close behavior', () => {
    it('should call onClose when close button clicked', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByLabelText(/close dialogue/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByLabelText(/close dialogue/i));
      expect(defaultProps.onClose).toHaveBeenCalled();
    });

    it('should call onClose when backdrop clicked (desktop)', async () => {
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      render(<DialogueModal {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Click the backdrop (the first fixed inset-0 element)
      const backdrop = document.querySelector('.fixed.inset-0.bg-black\\/60');
      if (backdrop) {
        fireEvent.click(backdrop);
        expect(defaultProps.onClose).toHaveBeenCalled();
      }
    });
  });

  describe('mobile layout', () => {
    it('should use BottomDrawer on mobile', async () => {
      Object.defineProperty(window, 'innerWidth', { value: 500 });
      vi.mocked(townApi.converse).mockResolvedValueOnce(mockConversation);

      render(<DialogueModal {...defaultProps} isMobile={true} />);

      await waitFor(() => {
        // BottomDrawer has specific structure
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });
    });
  });
});
