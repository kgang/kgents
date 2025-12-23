/**
 * CodeBlockToken — Syntax-highlighted code display.
 *
 * Renders fenced code blocks with language badge.
 * Shows copy button on hover.
 *
 * "Executable action with sandboxed execution."
 */

import { memo, useCallback, useState } from 'react';

import './tokens.css';

interface CodeBlockTokenProps {
  language: string;
  code: string;
  sourceText: string;
  className?: string;
}

export const CodeBlockToken = memo(function CodeBlockToken({
  language,
  code,
  sourceText: _sourceText,
  className,
}: CodeBlockTokenProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [code]);

  const lineCount = code.split('\n').length;

  return (
    <div className={`code-block-token ${className ?? ''}`} data-language={language || 'text'}>
      {/* INVARIANT: Header has fixed height, copy button always in DOM (CSS controls opacity) */}
      <div className="code-block-token__header">
        <span className="code-block-token__language">{language || 'text'}</span>
        <span className="code-block-token__info">
          {lineCount} {lineCount === 1 ? 'line' : 'lines'}
        </span>
        <button
          type="button"
          className="code-block-token__copy"
          onClick={handleCopy}
          title="Copy to clipboard"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>

      {/* Code content */}
      <pre className="code-block-token__pre">
        <code className="code-block-token__code">{code}</code>
      </pre>
    </div>
  );
});
