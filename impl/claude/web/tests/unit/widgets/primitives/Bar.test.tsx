import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Bar } from '@/widgets/primitives';

describe('Bar (widget)', () => {
  it('renders with correct fill ratio', () => {
    render(
      <Bar
        value={0.5}
        width={10}
        orientation="horizontal"
        style="solid"
        entropy={0}
      />
    );
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toBeInTheDocument();
    // 5 filled, 5 empty
    expect(bar?.textContent).toContain('█████');
    expect(bar?.textContent).toContain('░░░░░');
  });

  it('renders with dots style', () => {
    render(
      <Bar
        value={0.3}
        width={10}
        orientation="horizontal"
        style="dots"
        entropy={0}
      />
    );
    const bar = document.querySelector('.kgents-bar');
    expect(bar?.textContent).toContain('●●●');
    expect(bar?.textContent).toContain('○○○○○○○');
  });

  it('renders label when provided', () => {
    render(
      <Bar
        value={0.5}
        width={10}
        orientation="horizontal"
        style="solid"
        entropy={0}
        label="CPU"
      />
    );
    expect(screen.getByText('CPU:')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(
      <Bar
        value={0.5}
        width={10}
        orientation="horizontal"
        style="solid"
        entropy={0}
        fg="#00ff00"
      />
    );
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toHaveStyle({ color: '#00ff00' });
  });

  it('renders vertical orientation', () => {
    render(
      <Bar
        value={0.5}
        width={10}
        orientation="vertical"
        style="solid"
        entropy={0}
      />
    );
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toHaveStyle({ flexDirection: 'column' });
  });

  it('applies custom className', () => {
    render(
      <Bar
        value={0.5}
        width={10}
        orientation="horizontal"
        style="solid"
        entropy={0}
        className="custom-class"
      />
    );
    const bar = document.querySelector('.kgents-bar');
    expect(bar).toHaveClass('custom-class');
  });
});
