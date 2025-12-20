/**
 * RequestPreview - Shows the full HTTP request with syntax highlighting
 *
 * Displays the exact request that will be made, styled like a code editor.
 * Features:
 * - Method badge with color coding
 * - Full URL
 * - All headers in key: value format
 * - Body with JSON syntax highlighting
 * - Copy entire request button
 */

import { useState, useMemo } from 'react';
import { Copy, Check } from 'lucide-react';
import type { RequestPreviewProps } from './types';

// =============================================================================
// Syntax Highlighting Colors
// =============================================================================

const COLORS = {
  method: {
    GET: 'text-green-400',
    POST: 'text-amber-400',
    PUT: 'text-blue-400',
    DELETE: 'text-red-400',
    PATCH: 'text-violet-400',
  } as const,
  url: 'text-cyan-300',
  headerKey: 'text-pink-400',
  headerValue: 'text-gray-300',
  punctuation: 'text-gray-500',
};

// =============================================================================
// JSON Formatting
// =============================================================================

/**
 * Format JSON value for display.
 * Returns a formatted string with proper indentation.
 */
function formatJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

// =============================================================================
// Component
// =============================================================================

export function RequestPreview({ config, onCopy }: RequestPreviewProps) {
  const [copied, setCopied] = useState(false);

  // Build the full request text for copying
  const fullRequestText = useMemo(() => {
    const lines: string[] = [];

    // Request line
    lines.push(`${config.method} ${config.url}`);

    // Headers
    for (const header of config.headers) {
      if (header.enabled && header.key) {
        lines.push(`${header.key}: ${header.value}`);
      }
    }

    // Body
    if (config.body && config.method !== 'GET') {
      lines.push('');
      lines.push(JSON.stringify(config.body, null, 2));
    }

    return lines.join('\n');
  }, [config]);

  // Handle copy
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullRequestText);
      setCopied(true);
      onCopy();
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  };

  // Method color
  const methodColor = COLORS.method[config.method as keyof typeof COLORS.method] || 'text-gray-400';

  // Filter enabled headers for rendering
  const enabledHeaders = config.headers.filter(
    (h): h is { key: string; value: string; enabled: true } => h.enabled && Boolean(h.key)
  );

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/50 bg-gray-900/50">
        <span className="text-sm text-gray-400">HTTP Request Preview</span>
        <button
          onClick={handleCopy}
          className="
            flex items-center gap-1.5 px-2 py-1 rounded text-sm
            text-gray-400 hover:text-white hover:bg-gray-700/50
            transition-colors
          "
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 font-mono text-sm leading-relaxed">
        <div className="mb-4">
          <span className={`font-bold ${methodColor}`}>{config.method}</span>
          <span className="text-gray-400"> </span>
          <span className={COLORS.url}>{config.url}</span>
        </div>

        <div className="mb-4 space-y-0.5">
          {enabledHeaders.map((header, i) => (
            <div key={i}>
              <span className={COLORS.headerKey}>{header.key}</span>
              <span className={COLORS.punctuation}>: </span>
              <span className={COLORS.headerValue}>{header.value}</span>
            </div>
          ))}
        </div>

        {config.body !== undefined && config.body !== null && config.method !== 'GET' ? (
          <>
            <div className="border-t border-gray-700/50 my-4" />
            <pre className="whitespace-pre-wrap">
              <code className="text-gray-200">{formatJson(config.body)}</code>
            </pre>
          </>
        ) : null}

        {config.method === 'GET' && (
          <div className="text-gray-500 italic">(GET requests do not include a body)</div>
        )}
      </div>
    </div>
  );
}

export default RequestPreview;
