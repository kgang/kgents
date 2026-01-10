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
      expect(screen.getByText('Path Not Found')).toBeInTheDocument();
    });

    it('should render available paths description', () => {
      renderWithRouter(<NotFound />);
      expect(
        screen.getByText('This AGENTESE path does not exist. Try one of these:')
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
      const homeLink = screen.getByRole('link', { name: /go to home page/i });
      expect(homeLink).toBeInTheDocument();
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('should have a link to chat', () => {
      renderWithRouter(<NotFound />);
      const chatLink = screen.getByRole('link', { name: /chat/i });
      expect(chatLink).toBeInTheDocument();
      expect(chatLink).toHaveAttribute('href', '/self.chat');
    });

    it('should have a link to director', () => {
      renderWithRouter(<NotFound />);
      const directorLink = screen.getByRole('link', { name: /director/i });
      expect(directorLink).toBeInTheDocument();
      expect(directorLink).toHaveAttribute('href', '/self.director');
    });

    it('should have a link to document', () => {
      renderWithRouter(<NotFound />);
      // Use getAllByRole since "document" appears multiple times, then filter by href
      const links = screen.getAllByRole('link');
      const documentLink = links.find((link) => link.getAttribute('href') === '/world.document');
      expect(documentLink).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have heading level 1', () => {
      renderWithRouter(<NotFound />);
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Path Not Found');
    });
  });
});
