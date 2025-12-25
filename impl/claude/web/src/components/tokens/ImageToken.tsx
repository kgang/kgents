/**
 * ImageToken — Image with AI analysis on hover.
 *
 * Renders images with:
 * - Responsive sizing
 * - Alt text fallback
 * - AI-generated description on hover (lazy loaded)
 * - Click to expand fullscreen
 *
 * "Images are not decoration. They are meaning tokens."
 *
 * @see spec/protocols/interactive-text.md
 */

import { memo, useCallback, useState } from 'react';

import { Breathe } from '../../components/joy/Breathe';

import './tokens.css';

// =============================================================================
// Types
// =============================================================================

interface ImageTokenProps {
  /** Image source path or URL */
  src: string;
  /** Alt text for accessibility */
  alt: string;
  /** AI-generated description (if available) */
  aiDescription?: string;
  /** Called when image is clicked */
  onClick?: (src: string) => void;
  /** Called to request AI analysis (lazy load) */
  onRequestAnalysis?: (src: string) => Promise<string>;
  /** Additional class names */
  className?: string;
  /** Caption below the image */
  caption?: string;
}

// =============================================================================
// Component
// =============================================================================

export const ImageToken = memo(function ImageToken({
  src,
  alt,
  aiDescription,
  onClick,
  onRequestAnalysis,
  className,
  caption,
}: ImageTokenProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [localDescription, setLocalDescription] = useState<string | null>(null);
  const [loadError, setLoadError] = useState(false);

  const displayDescription = aiDescription || localDescription;

  // Lazy load AI analysis on first hover
  const handleMouseEnter = useCallback(async () => {
    setIsHovered(true);

    // If we don't have a description and can request one, do so
    if (!displayDescription && onRequestAnalysis && !isLoading && !loadError) {
      setIsLoading(true);
      try {
        const description = await onRequestAnalysis(src);
        setLocalDescription(description);
      } catch (err) {
        console.error('[ImageToken] Failed to load AI analysis:', err);
        setLoadError(true);
      } finally {
        setIsLoading(false);
      }
    }
  }, [displayDescription, onRequestAnalysis, isLoading, loadError, src]);

  const handleClick = useCallback(() => {
    onClick?.(src);
  }, [src, onClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick?.(src);
      }
    },
    [src, onClick]
  );

  const handleImgError = useCallback(() => {
    setLoadError(true);
  }, []);

  return (
    <figure
      className={`image-token ${className ?? ''}`}
      data-src={src}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Image container */}
      <div className="image-token__container">
        {loadError ? (
          <div className="image-token__error">
            <span className="image-token__error-icon">◇</span>
            <span className="image-token__error-text">Image not found</span>
            <span className="image-token__error-path">{src}</span>
          </div>
        ) : (
          <button
            type="button"
            className="image-token__button"
            onClick={handleClick}
            onKeyDown={handleKeyDown}
            title={alt || 'View image'}
          >
            <img
              src={src}
              alt={alt}
              className="image-token__img"
              onError={handleImgError}
              loading="lazy"
            />
          </button>
        )}

        {/* AI analysis tooltip — INVARIANT: Always in DOM, opacity controlled by CSS */}
        <div
          className="image-token__tooltip"
          style={{ opacity: isHovered && (displayDescription || isLoading) ? 1 : 0 }}
        >
          {isLoading ? (
            <Breathe intensity={0.3}>
              <span className="image-token__tooltip-loading">Analyzing image...</span>
            </Breathe>
          ) : displayDescription ? (
            <>
              <span className="image-token__tooltip-label">AI Analysis</span>
              <span className="image-token__tooltip-text">{displayDescription}</span>
            </>
          ) : null}
        </div>
      </div>

      {/* Caption */}
      {caption && <figcaption className="image-token__caption">{caption}</figcaption>}

      {/* Alt text shown if no caption */}
      {!caption && alt && <figcaption className="image-token__alt">{alt}</figcaption>}
    </figure>
  );
});
