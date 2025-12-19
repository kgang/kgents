/**
 * GenericProjection - Fallback JSON viewer for AGENTESE responses
 *
 * When no specific projection is registered for a response type,
 * this component renders the raw data in a readable format with
 * teaching callouts.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight, Copy, Check, Code, FileJson } from 'lucide-react';
import type { ProjectionProps } from './types';
import { formatPathLabel } from '@/utils/parseAgentesePath';

/**
 * Recursively render JSON with collapsible nodes
 */
function JsonValue({
  value,
  depth = 0,
}: {
  value: unknown;
  depth?: number;
  keyName?: string;
}) {
  const [expanded, setExpanded] = useState(depth < 2);

  if (value === null) {
    return <span className="text-content-tertiary italic">null</span>;
  }

  if (value === undefined) {
    return <span className="text-content-tertiary italic">undefined</span>;
  }

  if (typeof value === 'boolean') {
    return <span className="text-accent-amber">{value ? 'true' : 'false'}</span>;
  }

  if (typeof value === 'number') {
    return <span className="text-accent-sage">{value}</span>;
  }

  if (typeof value === 'string') {
    // Truncate long strings
    const display = value.length > 100 ? value.slice(0, 100) + '...' : value;
    return <span className="text-accent-honey">"{display}"</span>;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-content-tertiary">[]</span>;
    }

    return (
      <div className="inline">
        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-content-secondary hover:text-content-primary"
        >
          {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          <span className="text-content-tertiary">[{value.length}]</span>
        </button>
        {expanded && (
          <div className="ml-4 border-l border-border-subtle pl-3">
            {value.map((item, i) => (
              <div key={i} className="py-0.5">
                <span className="text-content-tertiary mr-2">{i}:</span>
                <JsonValue value={item} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value);
    if (entries.length === 0) {
      return <span className="text-content-tertiary">{'{}'}</span>;
    }

    return (
      <div className="inline">
        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 text-content-secondary hover:text-content-primary"
        >
          {expanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          <span className="text-content-tertiary">
            {'{'}
            {entries.length}
            {'}'}
          </span>
        </button>
        {expanded && (
          <div className="ml-4 border-l border-border-subtle pl-3">
            {entries.map(([k, v]) => (
              <div key={k} className="py-0.5">
                <span className="text-content-primary font-medium mr-2">{k}:</span>
                <JsonValue value={v} depth={depth + 1} keyName={k} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return <span className="text-content-secondary">{String(value)}</span>;
}

export function GenericProjection({ context }: ProjectionProps) {
  const [copied, setCopied] = useState(false);
  const { path, aspect, responseType, response } = context;
  const label = formatPathLabel(path);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(response, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-content-primary flex items-center gap-2">
            <FileJson className="w-6 h-6 text-accent-sage" />
            {label}
          </h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <code className="px-2 py-1 text-xs rounded bg-surface-inset text-content-secondary font-mono">
              {path}
            </code>
            {aspect !== 'manifest' && (
              <code className="px-2 py-1 text-xs rounded bg-accent-sage/10 text-accent-sage font-mono">
                :{aspect}
              </code>
            )}
            {responseType && (
              <code className="px-2 py-1 text-xs rounded bg-accent-amber/10 text-accent-amber font-mono">
                {responseType}
              </code>
            )}
          </div>
        </div>

        {/* Copy button */}
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-elevated hover:bg-surface-hover text-content-secondary transition-colors"
        >
          {copied ? <Check className="w-4 h-4 text-accent-sage" /> : <Copy className="w-4 h-4" />}
          <span className="text-sm">{copied ? 'Copied!' : 'Copy JSON'}</span>
        </button>
      </div>

      {/* Teaching callout */}
      <motion.div
        className="mb-6 p-4 rounded-lg bg-accent-sage/5 border border-accent-sage/20"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start gap-3">
          <Code className="w-5 h-5 text-accent-sage flex-shrink-0 mt-0.5" />
          <div className="text-sm text-content-secondary">
            <p className="font-medium text-content-primary">Generic Projection</p>
            <p className="mt-1">
              No specific projection is registered for response type{' '}
              <code className="text-accent-amber">{responseType || 'unknown'}</code>. Showing raw
              JSON data.
            </p>
            <p className="mt-1 text-content-tertiary">
              To create a custom projection, add an entry to{' '}
              <code>shell/projections/registry.ts</code>.
            </p>
          </div>
        </div>
      </motion.div>

      {/* JSON viewer */}
      <div className="rounded-lg bg-surface-inset border border-border-subtle overflow-hidden">
        <div className="px-4 py-2 border-b border-border-subtle bg-surface-elevated flex items-center justify-between">
          <span className="text-sm font-medium text-content-secondary">Response Data</span>
          <span className="text-xs text-content-tertiary">
            {typeof response === 'object' && response !== null
              ? `${Object.keys(response).length} keys`
              : typeof response}
          </span>
        </div>
        <div className="p-4 font-mono text-sm overflow-x-auto">
          <JsonValue value={response} />
        </div>
      </div>

      {/* Query params if present */}
      {Object.keys(context.params).length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-medium text-content-secondary mb-2">Query Parameters</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(context.params).map(([key, value]) => (
              <span
                key={key}
                className="px-2 py-1 text-xs rounded bg-surface-inset text-content-secondary font-mono"
              >
                {key}={value}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default GenericProjection;
