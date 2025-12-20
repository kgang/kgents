/**
 * Tests for NotFound (404) page.
 *
 * @see src/pages/NotFound.tsx
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NotFound from '@/pages/NotFound';

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('NotFound', () => {
  describe('content', () => {
    it('should render the MapPin icon', () => {
      renderWithRouter(<NotFound />);
      // Uses Lucide MapPin icon (rendered as SVG) instead of emoji
      expect(document.querySelector('svg')).toBeInTheDocument();
    });

    it('should render the title', () => {
      renderWithRouter(<NotFound />);
      expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    });

    it('should render the description', () => {
      renderWithRouter(<NotFound />);
      expect(
        screen.getByText('This page does not exist. Check the URL or navigate home.')
      ).toBeInTheDocument();
    });

    it('should render the error code', () => {
      renderWithRouter(<NotFound />);
      expect(screen.getByText(/404/)).toBeInTheDocument();
    });
  });

  describe('navigation links', () => {
    it('should have a link to home', () => {
      renderWithRouter(<NotFound />);
      const homeLink = screen.getByRole('link', { name: /go home/i });
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should have a link to cockpit', () => {
      renderWithRouter(<NotFound />);
      const cockpitLink = screen.getByRole('link', { name: /open cockpit/i });
      expect(cockpitLink).toBeInTheDocument();
      expect(cockpitLink).toHaveAttribute('href', '/concept.cockpit');
    });
  });

  describe('accessibility', () => {
    it('should have heading level 1', () => {
      renderWithRouter(<NotFound />);
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Page Not Found');
    });
  });
});
