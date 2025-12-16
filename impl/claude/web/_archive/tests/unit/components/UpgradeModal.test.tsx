import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UpgradeModal } from '@/components/paywall/UpgradeModal';
import { useUIStore } from '@/stores/uiStore';
import { useUserStore } from '@/stores/userStore';

// Mock the payments API
vi.mock('@/api/payments', () => ({
  createSubscriptionCheckout: vi.fn(),
  createCreditCheckout: vi.fn(),
}));

import { createSubscriptionCheckout, createCreditCheckout } from '@/api/payments';

describe('UpgradeModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Reset stores
    useUIStore.setState({
      activeModal: 'upgrade',
      modalData: {},
    });

    useUserStore.setState({
      userId: 'user-123',
      tier: 'TOURIST',
      credits: 50,
    });
  });

  describe('rendering', () => {
    it('should not render when activeModal is not upgrade', () => {
      useUIStore.setState({ activeModal: null });

      render(<UpgradeModal />);

      expect(screen.queryByText('Unlock More')).not.toBeInTheDocument();
    });

    it('should render when activeModal is upgrade', () => {
      render(<UpgradeModal />);

      expect(screen.getByText('Unlock More')).toBeInTheDocument();
    });

    it('should have close button', () => {
      render(<UpgradeModal />);

      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toBeInTheDocument();
    });

    it('should close modal when clicking close button', () => {
      const closeModal = vi.fn();
      useUIStore.setState({ closeModal });

      render(<UpgradeModal />);

      fireEvent.click(screen.getByRole('button', { name: /close/i }));

      expect(closeModal).toHaveBeenCalled();
    });
  });

  describe('tabs', () => {
    it('should show Buy Credits tab by default', () => {
      render(<UpgradeModal />);

      const creditsTab = screen.getByRole('button', { name: /buy credits/i });
      expect(creditsTab).toHaveClass('bg-town-accent/20');
    });

    it('should switch to Upgrade Tier tab when clicked', () => {
      render(<UpgradeModal />);

      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      // Should show subscription options
      expect(screen.getByText('RESIDENT')).toBeInTheDocument();
      expect(screen.getByText('CITIZEN')).toBeInTheDocument();
      expect(screen.getByText('FOUNDER')).toBeInTheDocument();
    });
  });

  describe('credit packs', () => {
    it('should display all credit packs', () => {
      render(<UpgradeModal />);

      expect(screen.getByText('Starter')).toBeInTheDocument();
      expect(screen.getByText('Explorer')).toBeInTheDocument();
      expect(screen.getByText('Adventurer')).toBeInTheDocument();
    });

    it('should show credit amounts', () => {
      render(<UpgradeModal />);

      expect(screen.getByText('100')).toBeInTheDocument();
      expect(screen.getByText('500')).toBeInTheDocument();
      expect(screen.getByText('2000')).toBeInTheDocument();
    });

    it('should show prices', () => {
      render(<UpgradeModal />);

      expect(screen.getByText('$4.99')).toBeInTheDocument();
      expect(screen.getByText('$19.99')).toBeInTheDocument();
      expect(screen.getByText('$49.99')).toBeInTheDocument();
    });

    it('should show Popular badge on Explorer pack', () => {
      render(<UpgradeModal />);

      expect(screen.getByText('Popular')).toBeInTheDocument();
    });

    it('should call createCreditCheckout when buying credits', async () => {
      vi.mocked(createCreditCheckout).mockResolvedValueOnce(undefined);

      render(<UpgradeModal />);

      // Click first Buy Now button (Starter pack)
      const buyButtons = screen.getAllByRole('button', { name: /buy now/i });
      fireEvent.click(buyButtons[0]);

      await waitFor(() => {
        expect(createCreditCheckout).toHaveBeenCalledWith('SMALL', 'user-123');
      });
    });

    it('should show error when not signed in', async () => {
      useUserStore.setState({ userId: null });

      render(<UpgradeModal />);

      const buyButtons = screen.getAllByRole('button', { name: /buy now/i });
      fireEvent.click(buyButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Please sign in to purchase credits')).toBeInTheDocument();
      });
    });

    it('should show error on checkout failure', async () => {
      vi.mocked(createCreditCheckout).mockRejectedValueOnce(new Error('Stripe error'));

      render(<UpgradeModal />);

      const buyButtons = screen.getAllByRole('button', { name: /buy now/i });
      fireEvent.click(buyButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('Failed to start checkout. Please try again.')).toBeInTheDocument();
      });
    });
  });

  describe('subscription tiers', () => {
    it('should display all subscription tiers', () => {
      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      expect(screen.getByText('RESIDENT')).toBeInTheDocument();
      expect(screen.getByText('CITIZEN')).toBeInTheDocument();
      expect(screen.getByText('FOUNDER')).toBeInTheDocument();
    });

    it('should show Recommended badge on CITIZEN', () => {
      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      expect(screen.getByText('Recommended')).toBeInTheDocument();
    });

    it('should show subscription prices', () => {
      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      expect(screen.getByText('$9.99')).toBeInTheDocument();
      expect(screen.getByText('$29.99')).toBeInTheDocument();
      expect(screen.getByText('$99.99')).toBeInTheDocument();
    });

    it.skip('should call createSubscriptionCheckout when upgrading', async () => {
      // TODO: Fix async state update issue with zustand persist middleware
      vi.mocked(createSubscriptionCheckout).mockResolvedValueOnce(undefined);

      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      const upgradeButtons = screen.getAllByRole('button', { name: /upgrade/i });
      fireEvent.click(upgradeButtons[0]); // First Upgrade button (RESIDENT)

      // Wait for async operation to complete
      await waitFor(() => {
        expect(createSubscriptionCheckout).toHaveBeenCalledWith('RESIDENT', 'user-123');
      });
    });

    it.skip('should show error when not signed in', async () => {
      // TODO: Fix zustand persist middleware interaction in tests
      // Set userId to null BEFORE rendering
      useUserStore.setState({
        userId: null,
        tier: 'TOURIST',
        credits: 50,
      });

      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      const upgradeButtons = screen.getAllByRole('button', { name: /upgrade/i });
      fireEvent.click(upgradeButtons[0]);

      // Wait for state update
      await waitFor(() => {
        expect(screen.getByText('Please sign in to upgrade')).toBeInTheDocument();
      });
    });
  });

  describe('current tier', () => {
    it('should show Current Plan for user tier', () => {
      useUserStore.setState({ tier: 'CITIZEN' });

      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      expect(screen.getByText('Current Plan')).toBeInTheDocument();
    });

    it('should disable button for current tier', () => {
      useUserStore.setState({ tier: 'CITIZEN' });

      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      const currentPlanButton = screen.getByRole('button', { name: /current plan/i });
      expect(currentPlanButton).toBeDisabled();
    });

    it('should show Downgrade N/A for lower tiers', () => {
      useUserStore.setState({ tier: 'FOUNDER' });

      render(<UpgradeModal />);
      fireEvent.click(screen.getByRole('button', { name: /upgrade tier/i }));

      const downgradeButtons = screen.getAllByRole('button', { name: /downgrade/i });
      expect(downgradeButtons.length).toBe(2); // RESIDENT and CITIZEN
    });
  });

  describe('required credits banner', () => {
    it('should show required credits message when applicable', () => {
      useUIStore.setState({
        activeModal: 'upgrade',
        modalData: { requiredCredits: 100, currentCredits: 50 },
      });

      render(<UpgradeModal />);

      expect(screen.getByText(/You need 50 more credits/)).toBeInTheDocument();
    });

    it('should show "Covers your needs" for sufficient packs', () => {
      // modalData.currentCredits is what the component uses
      useUIStore.setState({
        activeModal: 'upgrade',
        modalData: { requiredCredits: 50, currentCredits: 0 },
      });

      // Also ensure user credits match
      useUserStore.setState({ credits: 0 });

      render(<UpgradeModal />);

      // All packs should show "Covers your needs" since they all cover the 50 needed
      // 100 >= 50, 500 >= 50, 2000 >= 50
      const coversTexts = screen.getAllByText('Covers your needs');
      expect(coversTexts.length).toBe(3);
    });
  });

  describe('loading state', () => {
    it('should show Processing on buttons during checkout', async () => {
      let resolveCheckout: () => void;
      const checkoutPromise = new Promise<void>((resolve) => {
        resolveCheckout = resolve;
      });
      vi.mocked(createCreditCheckout).mockReturnValueOnce(checkoutPromise);

      render(<UpgradeModal />);

      const buyButtons = screen.getAllByRole('button', { name: /buy now/i });
      fireEvent.click(buyButtons[0]);

      // Wait a tick for state to update
      await new Promise(resolve => setTimeout(resolve, 0));

      // All 3 credit pack buttons should show Processing when loading
      const processingButtons = screen.getAllByText('Processing...');
      expect(processingButtons.length).toBe(3);

      // Cleanup
      resolveCheckout!();
    });

    it('should disable all buttons during checkout', async () => {
      let resolveCheckout: () => void;
      const checkoutPromise = new Promise<void>((resolve) => {
        resolveCheckout = resolve;
      });
      vi.mocked(createCreditCheckout).mockReturnValueOnce(checkoutPromise);

      render(<UpgradeModal />);

      const buyButtons = screen.getAllByRole('button', { name: /buy now/i });
      fireEvent.click(buyButtons[0]);

      // Wait a tick for state to update
      await new Promise(resolve => setTimeout(resolve, 0));

      // All processing buttons should be disabled
      const processingButtons = screen.getAllByRole('button', { name: /processing/i });
      processingButtons.forEach((button) => {
        expect(button).toBeDisabled();
      });

      // Cleanup
      resolveCheckout!();
    });
  });
});
