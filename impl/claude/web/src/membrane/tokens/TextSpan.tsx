/**
 * TextSpan — Plain text renderer for non-token content.
 *
 * This is the fallback renderer for text that isn't a meaning token.
 * It preserves whitespace and renders inline.
 */

import { memo } from 'react';

interface TextSpanProps {
  content: string;
  className?: string;
}

export const TextSpan = memo(function TextSpan({ content, className }: TextSpanProps) {
  // Preserve whitespace, including newlines
  return (
    <span className={`text-span ${className ?? ''}`} style={{ whiteSpace: 'pre-wrap' }}>
      {content}
    </span>
  );
});
