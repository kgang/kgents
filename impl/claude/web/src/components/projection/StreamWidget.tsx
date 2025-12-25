/**
 * StreamWidget: Streaming text display with cursor.
 *
 * Features:
 * - Blinking cursor during streaming
 * - Smooth chunk accumulation
 * - Auto-scroll to bottom
 * - Complete indicator
 */

import { useRef, useEffect } from 'react';

export interface StreamWidgetProps {
  /** Accumulated chunks */
  chunks: string[];
  /** Is stream complete */
  complete?: boolean;
  /** Show blinking cursor */
  showCursor?: boolean;
  /** Auto-scroll to bottom */
  autoScroll?: boolean;
  /** Maximum height (scrollable) */
  maxHeight?: number;
  /** Variant: code or text */
  variant?: 'text' | 'code';
}

export function StreamWidget({
  chunks,
  complete = false,
  showCursor = true,
  autoScroll = true,
  maxHeight = 400,
  variant = 'text',
}: StreamWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new chunks
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [chunks, autoScroll]);

  const content = chunks.join('');

  const isCode = variant === 'code';

  return (
    <div
      ref={containerRef}
      className={`kgents-stream-widget kgents-stream-${variant}`}
      style={{
        maxHeight: `${maxHeight}px`,
        overflowY: 'auto',
        padding: '12px',
        backgroundColor: isCode ? '#1f2937' : '#f9fafb',
        color: isCode ? '#e5e7eb' : '#1f2937',
        borderRadius: '8px',
        fontFamily: isCode ? 'monospace' : 'inherit',
        fontSize: isCode ? '14px' : '15px',
        lineHeight: 1.6,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }}
      aria-live="polite"
      aria-atomic="false"
    >
      {content}

      {/* Cursor */}
      {showCursor && !complete && (
        <span
          className="kgents-stream-cursor"
          style={{
            display: 'inline-block',
            width: '2px',
            height: '1em',
            backgroundColor: isCode ? '#60a5fa' : '#3b82f6',
            marginLeft: '1px',
            animation: 'kgents-cursor-blink 1s step-end infinite',
            verticalAlign: 'text-bottom',
          }}
          aria-hidden="true"
        />
      )}

      {/* Complete indicator */}
      {complete && (
        <span
          style={{
            display: 'inline-block',
            marginLeft: '8px',
            color: '#10b981',
            fontSize: '12px',
          }}
          aria-label="Stream complete"
        >
          ●
        </span>
      )}

      {/* Cursor blink animation */}
      <style>{`
        @keyframes kgents-cursor-blink {
          0%, 50% { opacity: 1; }
          50.01%, 100% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}

export default StreamWidget;
