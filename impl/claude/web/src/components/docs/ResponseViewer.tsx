/**
 * ResponseViewer - The middle pane showing invocation results.
 *
 * Features:
 * - Observer-colored syntax highlighting
 * - Response time with contextual loading messages
 * - Success shimmer celebration
 * - Empathetic error states ("Lost in the Ether" not "500")
 */

import React, { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Check, Copy, Download } from 'lucide-react';
import type { Observer } from './ObserverPicker';

// =============================================================================
// Types
// =============================================================================

interface ResponseViewerProps {
  response: {
    data: unknown;
    elapsed: number;
    status: 'idle' | 'loading' | 'success' | 'error';
    error?: string;
  };
  path: string | null;
  aspect: string;
  observer: Observer;
}

// =============================================================================
// Loading Messages (Joy-Inducing)
// =============================================================================

const LOADING_MESSAGES = [
  'Traversing the ontology...',
  'Consulting the sheaf...',
  'Composing morphisms...',
  'Observing through your lens...',
  'Gluing local patches...',
  'Asking the void nicely...',
  'Following the path...',
  'Projecting reality...',
];

function getLoadingMessage(): string {
  return LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)];
}

// =============================================================================
// Observer Colors
// =============================================================================

const OBSERVER_COLORS: Record<string, { accent: string; bg: string }> = {
  guest: { accent: '#9CA3AF', bg: 'from-gray-900 to-gray-800' },
  user: { accent: '#06B6D4', bg: 'from-cyan-900/20 to-gray-900' },
  developer: { accent: '#22C55E', bg: 'from-green-900/20 to-gray-900' },
  mayor: { accent: '#F59E0B', bg: 'from-amber-900/20 to-gray-900' },
  coalition: { accent: '#8B5CF6', bg: 'from-violet-900/20 to-gray-900' },
  void: { accent: '#EC4899', bg: 'from-pink-900/20 to-gray-900' },
};

// =============================================================================
// Component
// =============================================================================

export function ResponseViewer({ response, path, aspect, observer }: ResponseViewerProps) {
  const [loadingMessage, setLoadingMessage] = useState(getLoadingMessage);
  const [copied, setCopied] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  // Rotate loading messages
  useEffect(() => {
    if (response.status !== 'loading') return;
    const interval = setInterval(() => {
      setLoadingMessage(getLoadingMessage());
    }, 2000);
    return () => clearInterval(interval);
  }, [response.status]);

  // Success celebration
  useEffect(() => {
    if (response.status === 'success') {
      setShowCelebration(true);
      const timer = setTimeout(() => setShowCelebration(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [response.status, response.elapsed]);

  // Observer styling
  const observerStyle = OBSERVER_COLORS[observer.archetype] || OBSERVER_COLORS.guest;

  // Format JSON with syntax highlighting
  const formattedJson = useMemo(() => {
    if (!response.data) return '';
    try {
      return JSON.stringify(response.data, null, 2);
    } catch {
      return String(response.data);
    }
  }, [response.data]);

  // Copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formattedJson);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  };

  // Download as JSON
  const handleDownload = () => {
    const blob = new Blob([formattedJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${path?.replace(/\./g, '-')}-${aspect}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Idle state
  if (response.status === 'idle' && !path) {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <motion.div
            className="text-6xl mb-6"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            🌐
          </motion.div>
          <h2 className="text-xl font-semibold text-white mb-2">AGENTESE Explorer</h2>
          <p className="text-gray-400">
            Select a path to begin exploring. The universe of AGENTESE awaits.
          </p>
        </div>
      </div>
    );
  }

  // Loading state
  if (response.status === 'loading') {
    return (
      <div
        className={`h-full flex items-center justify-center bg-gradient-to-br ${observerStyle.bg}`}
      >
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <motion.div
            className="w-16 h-16 mx-auto mb-6 rounded-full border-4"
            style={{
              borderColor: `${observerStyle.accent}30`,
              borderTopColor: observerStyle.accent,
            }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          <p className="text-gray-300 font-medium">{loadingMessage}</p>
          <p className="text-gray-500 text-sm mt-2">
            {path}:{aspect}
          </p>
        </motion.div>
      </div>
    );
  }

  // Error state (empathetic, not robotic)
  if (response.status === 'error') {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-gradient-to-br from-red-900/10 to-gray-900">
        <motion.div
          className="text-center max-w-md"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="text-6xl mb-6">🌑</div>
          <h2 className="text-xl font-semibold text-pink-400 mb-2">Lost in the Ether</h2>
          <p className="text-gray-400 mb-4">{response.error}</p>
          <div className="text-xs text-gray-500">
            <span className="font-mono">
              {path}:{aspect}
            </span>
            <span className="mx-2">•</span>
            <span>{response.elapsed.toFixed(0)}ms</span>
          </div>
        </motion.div>
      </div>
    );
  }

  // Success state
  return (
    <div className={`h-full flex flex-col bg-gradient-to-br ${observerStyle.bg}`}>
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/50">
        <div className="flex items-center gap-3">
          {/* Path and aspect */}
          <span className="font-mono text-sm text-gray-300">
            {path}
            <span className="text-gray-500">:</span>
            <span style={{ color: observerStyle.accent }}>{aspect}</span>
          </span>

          {/* Observer badge */}
          <span
            className="px-2 py-0.5 rounded text-xs font-medium"
            style={{
              backgroundColor: `${observerStyle.accent}20`,
              color: observerStyle.accent,
            }}
          >
            {observer.archetype}
          </span>
        </div>

        {/* Meta info and actions */}
        <div className="flex items-center gap-4">
          {/* Response time */}
          <div className="flex items-center gap-1 text-sm text-gray-400">
            <Clock className="w-4 h-4" />
            <span>{response.elapsed.toFixed(0)}ms</span>
          </div>

          {/* Success indicator */}
          <AnimatePresence>
            {showCelebration && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                className="flex items-center gap-1 text-green-400"
              >
                <Check className="w-4 h-4" />
                <span className="text-sm">Success</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Actions */}
          <div className="flex items-center gap-1">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded hover:bg-gray-700/50 transition-colors text-gray-400 hover:text-white"
              title="Copy to clipboard"
            >
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            </button>
            <button
              onClick={handleDownload}
              className="p-1.5 rounded hover:bg-gray-700/50 transition-colors text-gray-400 hover:text-white"
              title="Download JSON"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* JSON Content */}
      <div className="flex-1 overflow-auto relative">
        {/* Success shimmer overlay */}
        <AnimatePresence>
          {showCelebration && (
            <motion.div
              className="absolute inset-0 pointer-events-none"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{
                background: `linear-gradient(45deg, transparent 30%, ${observerStyle.accent}10 50%, transparent 70%)`,
                backgroundSize: '200% 200%',
              }}
            >
              <motion.div
                className="w-full h-full"
                style={{
                  background: `linear-gradient(90deg, transparent 0%, ${observerStyle.accent}20 50%, transparent 100%)`,
                }}
                initial={{ x: '-100%' }}
                animate={{ x: '100%' }}
                transition={{ duration: 0.6 }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Code block */}
        <pre className="p-4 text-sm font-mono leading-relaxed" style={{ color: '#E5E7EB' }}>
          <SyntaxHighlightedJson json={formattedJson} accentColor={observerStyle.accent} />
        </pre>
      </div>
    </div>
  );
}

// =============================================================================
// Syntax Highlighting
// =============================================================================

interface SyntaxHighlightedJsonProps {
  json: string;
  accentColor: string;
}

/**
 * Token-based JSON syntax highlighter.
 *
 * This replaces the previous regex-based approach which was fragile:
 * - Regex couldn't handle nested quotes or special characters
 * - dangerouslySetInnerHTML + React element extraction caused hydration issues
 *
 * Now we tokenize properly and render React elements directly.
 */
function SyntaxHighlightedJson({ json, accentColor }: SyntaxHighlightedJsonProps) {
  const elements = useMemo(() => {
    if (!json)
      return [
        <span key="empty" className="text-gray-500 italic">
          Empty response
        </span>,
      ];

    // Parse JSON to re-serialize with highlighting
    // This is safer than regex because we know the structure
    try {
      const parsed = JSON.parse(json);
      return renderValue(parsed, accentColor, 0);
    } catch {
      // Fallback to plain text if JSON is invalid
      return [<span key="raw">{json}</span>];
    }
  }, [json, accentColor]);

  return <code className="block">{elements}</code>;
}

/**
 * Recursively render JSON value with syntax highlighting.
 */
function renderValue(
  value: unknown,
  accentColor: string,
  depth: number,
  isLast: boolean = true
): React.ReactNode[] {
  const indent = '  '.repeat(depth);
  const comma = isLast ? '' : ',';

  if (value === null) {
    return [
      <span key="null" style={{ color: '#EF9A9A' }}>
        null{comma}
      </span>,
    ];
  }

  if (typeof value === 'boolean') {
    return [
      <span key="bool" style={{ color: '#FFB74D' }}>
        {value.toString()}
        {comma}
      </span>,
    ];
  }

  if (typeof value === 'number') {
    return [
      <span key="num" style={{ color: '#90CAF9' }}>
        {value}
        {comma}
      </span>,
    ];
  }

  if (typeof value === 'string') {
    // Escape string for display
    const escaped = JSON.stringify(value);
    return [
      <span key="str" style={{ color: '#A5D6A7' }}>
        {escaped}
        {comma}
      </span>,
    ];
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return [<span key="empty-arr">[]{comma}</span>];
    }

    const elements: React.ReactNode[] = [];
    elements.push(<span key="open">[</span>);
    elements.push(<br key="br-open" />);

    value.forEach((item, i) => {
      elements.push(<span key={`indent-${i}`}>{indent} </span>);
      elements.push(...renderValue(item, accentColor, depth + 1, i === value.length - 1));
      elements.push(<br key={`br-${i}`} />);
    });

    elements.push(<span key="close-indent">{indent}</span>);
    elements.push(<span key="close">]{comma}</span>);
    return elements;
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) {
      return [
        <span key="empty-obj">
          {'{}'}
          {comma}
        </span>,
      ];
    }

    const elements: React.ReactNode[] = [];
    elements.push(<span key="open">{'{'}</span>);
    elements.push(<br key="br-open" />);

    entries.forEach(([key, val], i) => {
      elements.push(<span key={`indent-${i}`}>{indent} </span>);
      elements.push(
        <span key={`key-${i}`} style={{ color: accentColor }}>
          "{key}"
        </span>
      );
      elements.push(<span key={`colon-${i}`}>: </span>);
      elements.push(...renderValue(val, accentColor, depth + 1, i === entries.length - 1));
      elements.push(<br key={`br-${i}`} />);
    });

    elements.push(<span key="close-indent">{indent}</span>);
    elements.push(
      <span key="close">
        {'}'}
        {comma}
      </span>
    );
    return elements;
  }

  // Fallback for unknown types
  return [
    <span key="unknown">
      {String(value)}
      {comma}
    </span>,
  ];
}

export default ResponseViewer;
