import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Sparkline } from '@/widgets/primitives';

describe('Sparkline (widget)', () => {
  it('renders sparkline characters', () => {
    render(
      <Sparkline
        values={[0.2, 0.4, 0.6, 0.8, 1.0]}
        max_length={20}
        entropy={0}
      />
    );
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toBeInTheDocument();
    // Should contain vertical bar characters
    expect(sparkline?.textContent).toMatch(/[▁▂▃▄▅▆▇█]+/);
  });

  it('renders label when provided', () => {
    render(
      <Sparkline
        values={[0.5, 0.6, 0.7]}
        max_length={20}
        entropy={0}
        label="Activity"
      />
    );
    expect(screen.getByText('Activity:')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(
      <Sparkline
        values={[0.5]}
        max_length={20}
        entropy={0}
        fg="#ff00ff"
      />
    );
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toHaveStyle({ color: '#ff00ff' });
  });

  it('applies default green color when fg not provided', () => {
    render(
      <Sparkline
        values={[0.5]}
        max_length={20}
        entropy={0}
      />
    );
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toHaveStyle({ color: '#28a745' });
  });

  it('applies custom className', () => {
    render(
      <Sparkline
        values={[0.5]}
        max_length={20}
        entropy={0}
        className="custom-class"
      />
    );
    const sparkline = document.querySelector('.kgents-sparkline');
    expect(sparkline).toHaveClass('custom-class');
  });
});
