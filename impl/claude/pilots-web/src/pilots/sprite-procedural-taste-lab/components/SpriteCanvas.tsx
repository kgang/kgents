/**
 * SpriteCanvas - Renders a sprite as actual pixels
 *
 * L1: Visual-First Law - Every UI state shows rendered sprites.
 * "The character is always visible."
 *
 * This component renders pixel art sprites from the data model,
 * NOT placeholder descriptions.
 *
 * Flavor: Foxes, kittens, and seals rendered with playful detail.
 */

import { useRef, useEffect } from 'react';
import type { Sprite } from '@kgents/shared-primitives';

interface SpriteCanvasProps {
  sprite: Sprite;
  scale?: number;
  showGrid?: boolean;
  animating?: boolean;
  className?: string;
}

/**
 * Render a sprite as a canvas element.
 * L1: Visual-First - real pixels, not descriptions.
 */
export function SpriteCanvas({
  sprite,
  scale = 8,
  showGrid = false,
  animating = false,
  className = '',
}: SpriteCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);
  const animationRef = useRef<number>();

  // Compute canvas dimensions
  const canvasWidth = sprite.width * scale;
  const canvasHeight = sprite.height * scale;

  // Render sprite to canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Disable smoothing for crisp pixels
    ctx.imageSmoothingEnabled = false;

    // Draw each pixel
    for (let y = 0; y < sprite.height; y++) {
      for (let x = 0; x < sprite.width; x++) {
        const pixelIndex = y * sprite.width + x;
        const colorIndex = sprite.pixels[pixelIndex];

        // Skip transparent (index 0 often means transparent, but we draw it)
        if (colorIndex >= 0 && colorIndex < sprite.palette.length) {
          ctx.fillStyle = sprite.palette[colorIndex];
          ctx.fillRect(x * scale, y * scale, scale, scale);
        }
      }
    }

    // Draw grid if requested
    if (showGrid) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.lineWidth = 1;

      for (let x = 0; x <= sprite.width; x++) {
        ctx.beginPath();
        ctx.moveTo(x * scale, 0);
        ctx.lineTo(x * scale, canvasHeight);
        ctx.stroke();
      }

      for (let y = 0; y <= sprite.height; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * scale);
        ctx.lineTo(canvasWidth, y * scale);
        ctx.stroke();
      }
    }
  }, [sprite, scale, showGrid, canvasWidth, canvasHeight]);

  // Handle idle animation (L3: Animation-Personality Law)
  useEffect(() => {
    if (!animating) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    const animate = () => {
      frameRef.current++;
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Subtle breathing/idle animation - scale oscillates slightly
      const breathe = Math.sin(frameRef.current * 0.05) * 0.02;

      ctx.save();
      ctx.setTransform(
        1 + breathe,
        0,
        0,
        1 + breathe,
        canvasWidth * -breathe * 0.5,
        canvasHeight * -breathe * 0.5
      );

      // Redraw with transform
      ctx.clearRect(-10, -10, canvasWidth + 20, canvasHeight + 20);
      ctx.imageSmoothingEnabled = false;

      for (let y = 0; y < sprite.height; y++) {
        for (let x = 0; x < sprite.width; x++) {
          const pixelIndex = y * sprite.width + x;
          const colorIndex = sprite.pixels[pixelIndex];

          if (colorIndex >= 0 && colorIndex < sprite.palette.length) {
            ctx.fillStyle = sprite.palette[colorIndex];
            ctx.fillRect(x * scale, y * scale, scale, scale);
          }
        }
      }

      ctx.restore();

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animating, sprite, scale, canvasWidth, canvasHeight]);

  return (
    <canvas
      ref={canvasRef}
      width={canvasWidth}
      height={canvasHeight}
      className={`rounded-lg ${className}`}
      style={{
        imageRendering: 'pixelated',
        background: 'rgba(0, 0, 0, 0.3)',
      }}
    />
  );
}

export default SpriteCanvas;
