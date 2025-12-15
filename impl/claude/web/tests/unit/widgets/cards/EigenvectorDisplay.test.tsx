import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EigenvectorDisplay } from '@/widgets/cards';

describe('EigenvectorDisplay (widget)', () => {
  const eigenvectors = {
    warmth: 0.7,
    curiosity: 0.8,
    trust: 0.6,
  };

  it('renders warmth bar', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} />);
    expect(screen.getByText('W:')).toBeInTheDocument();
  });

  it('renders curiosity bar', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} />);
    expect(screen.getByText('C:')).toBeInTheDocument();
  });

  it('renders trust bar', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} />);
    expect(screen.getByText('T:')).toBeInTheDocument();
  });

  it('shows values in non-compact mode', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} compact={false} />);
    // Values are shown as decimals
    expect(screen.getByText('0.70')).toBeInTheDocument();
    expect(screen.getByText('0.80')).toBeInTheDocument();
    expect(screen.getByText('0.60')).toBeInTheDocument();
  });

  it('hides values in compact mode', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} compact={true} />);
    expect(screen.queryByText('0.70')).not.toBeInTheDocument();
    expect(screen.queryByText('0.80')).not.toBeInTheDocument();
    expect(screen.queryByText('0.60')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<EigenvectorDisplay eigenvectors={eigenvectors} className="custom-class" />);
    const display = document.querySelector('.kgents-eigenvector-display');
    expect(display).toHaveClass('custom-class');
  });
});
