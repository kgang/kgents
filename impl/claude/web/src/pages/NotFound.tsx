/**
 * NotFound: 404 page.
 *
 * Displayed when user navigates to a non-existent route.
 * Provides helpful AGENTESE path suggestions.
 *
 * @see spec/protocols/projection-web.md
 */

import { Link, useLocation } from 'react-router-dom';
import { MapPin, ArrowRight } from 'lucide-react';

/**
 * Available AGENTESE paths with descriptions.
 */
const AGENTESE_PATHS = [
  { path: '/self.chat', label: 'Chat', description: 'Conversational interface with branching' },
  { path: '/self.memory', label: 'Memory', description: 'Explore crystals, marks, and wisdom' },
  { path: '/self.director', label: 'Director', description: 'Living document canvas' },
  { path: '/world.document', label: 'Document', description: 'Hypergraph spec editor' },
  { path: '/world.chart', label: 'Chart', description: 'Astronomical visualization' },
  { path: '/void.telescope', label: 'Telescope', description: 'Epistemic graph navigation' },
];

/**
 * Legacy path mapping for suggestions.
 */
const LEGACY_SUGGESTIONS: Record<string, string> = {
  '/brain': '/self.memory',
  '/chat': '/self.chat',
  '/director': '/self.director',
  '/editor': '/world.document',
  '/hypergraph-editor': '/world.document',
  '/chart': '/world.chart',
  '/feed': '/self.memory',
  '/proof-engine': '/void.telescope',
  '/zero-seed': '/void.telescope',
};

/**
 * 404 Not Found page with AGENTESE path suggestions.
 */
export default function NotFound() {
  const location = useLocation();
  const pathname = location.pathname;

  // Check if this looks like a legacy path
  const suggestion = LEGACY_SUGGESTIONS[pathname];

  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-surface-canvas">
      <div className="text-center max-w-2xl px-4">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          <MapPin className="w-16 h-16 text-text-tertiary" strokeWidth={1.5} />
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold mb-3 text-text-primary">Path Not Found</h1>

        {/* Current path */}
        <code className="inline-block bg-surface-overlay px-4 py-2 rounded text-sm text-text-secondary mb-4">
          {pathname}
        </code>

        {/* Suggestion for legacy paths */}
        {suggestion && (
          <div className="mb-8 p-4 bg-surface-overlay rounded-lg border border-border-subtle">
            <p className="text-text-secondary mb-3">
              This looks like a legacy route. Try the AGENTESE path instead:
            </p>
            <Link
              to={suggestion}
              className="inline-flex items-center gap-2 px-6 py-3 bg-accent-primary hover:bg-accent-primary/80 rounded-lg font-medium transition-colors text-white"
            >
              Go to {suggestion}
              <ArrowRight size={18} />
            </Link>
          </div>
        )}

        {/* Description */}
        <p className="text-text-secondary mb-8 text-lg">
          {suggestion
            ? 'Or explore other available paths:'
            : 'This AGENTESE path does not exist. Try one of these:'}
        </p>

        {/* Available paths grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
          {AGENTESE_PATHS.map(({ path, label, description }) => (
            <Link
              key={path}
              to={path}
              className="p-4 bg-surface-overlay hover:bg-surface-raised rounded-lg border border-border-subtle hover:border-accent-primary transition-all text-left group"
            >
              <div className="flex items-start justify-between mb-1">
                <span className="font-medium text-text-primary group-hover:text-accent-primary transition-colors">
                  {label}
                </span>
                <ArrowRight size={16} className="text-text-tertiary group-hover:text-accent-primary transition-colors" />
              </div>
              <code className="text-xs text-text-tertiary block mb-2">{path}</code>
              <p className="text-sm text-text-secondary">{description}</p>
            </Link>
          ))}
        </div>

        {/* Home link */}
        <Link
          to="/"
          className="inline-block text-text-secondary hover:text-accent-primary transition-colors text-sm"
        >
          Or go to home page
        </Link>

        {/* Error code */}
        <p className="text-text-tertiary text-sm mt-8">404</p>
      </div>
    </div>
  );
}
