import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Glyph } from '@/widgets/primitives';

describe('Glyph (widget)', () => {
  it('renders the character', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="none" />);
    expect(screen.getByText('◉')).toBeInTheDocument();
  });

  it('applies foreground color', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="none" fg="#ff0000" />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveStyle({ color: '#ff0000' });
  });

  it('applies background color', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="none" bg="#0000ff" />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveStyle({ backgroundColor: '#0000ff' });
  });

  it('applies animation class when animate is not none', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="pulse" />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveClass('animate-pulse');
  });

  it('does not apply animation class when animate is none', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="none" />);
    const glyph = screen.getByText('◉');
    expect(glyph).not.toHaveClass('animate-pulse');
    expect(glyph).not.toHaveClass('animate-blink');
  });

  it('applies distortion transform (skew)', () => {
    render(
      <Glyph
        char="◉"
        phase="active"
        entropy={0}
        animate="none"
        distortion={{
          blur: 0,
          skew: 5,
          jitter_x: 0,
          jitter_y: 0,
          pulse: 1,
        }}
      />
    );
    const glyph = screen.getByText('◉');
    expect(glyph.style.transform).toContain('skewX(5deg)');
  });

  it('applies distortion transform (jitter)', () => {
    render(
      <Glyph
        char="◉"
        phase="active"
        entropy={0}
        animate="none"
        distortion={{
          blur: 0,
          skew: 0,
          jitter_x: 2,
          jitter_y: 3,
          pulse: 1,
        }}
      />
    );
    const glyph = screen.getByText('◉');
    expect(glyph.style.transform).toContain('translate(2px, 3px)');
  });

  it('applies blur filter when distortion.blur > 0', () => {
    render(
      <Glyph
        char="◉"
        phase="active"
        entropy={0}
        animate="none"
        distortion={{
          blur: 2,
          skew: 0,
          jitter_x: 0,
          jitter_y: 0,
          pulse: 1,
        }}
      />
    );
    const glyph = screen.getByText('◉');
    expect(glyph.style.filter).toBe('blur(2px)');
  });

  it('sets data-phase attribute', () => {
    render(<Glyph char="◉" phase="thinking" entropy={0} animate="none" />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveAttribute('data-phase', 'thinking');
  });

  it('applies custom className', () => {
    render(<Glyph char="◉" phase="active" entropy={0} animate="none" className="custom-class" />);
    const glyph = screen.getByText('◉');
    expect(glyph).toHaveClass('custom-class');
  });
});
