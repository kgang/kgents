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
    it('should render the 404 emoji', () => {
      renderWithRouter(<NotFound />);
      expect(screen.getByText('🏚️')).toBeInTheDocument();
    });

    it('should render the title', () => {
      renderWithRouter(<NotFound />);
      expect(screen.getByText('Lost in the Wilderness')).toBeInTheDocument();
    });

    it('should render the description', () => {
      renderWithRouter(<NotFound />);
      expect(
        screen.getByText('This path leads nowhere. The town you seek lies elsewhere.')
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
      const homeLink = screen.getByRole('link', { name: /return home/i });
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should have a link to demo town', () => {
      renderWithRouter(<NotFound />);
      const demoLink = screen.getByRole('link', { name: /visit demo town/i });
      expect(demoLink).toBeInTheDocument();
      expect(demoLink).toHaveAttribute('href', '/town/demo');
    });
  });

  describe('accessibility', () => {
    it('should have heading level 1', () => {
      renderWithRouter(<NotFound />);
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Lost in the Wilderness');
    });
  });
});
