/**
 * ProjectionError - Error state for AGENTESE projections
 *
 * Shows a helpful error message with recovery suggestions when
 * an AGENTESE path cannot be resolved or invoked.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { motion } from 'framer-motion';
import { AlertCircle, ArrowLeft, Compass, RefreshCw } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import type { ProjectionErrorProps } from './types';
import { formatAgentesePath, getParentPath, AGENTESE_CONTEXTS } from '@/utils/parseAgentesePath';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';

/**
 * Error type classification
 */
type ErrorType = 'not_found' | 'forbidden' | 'refused' | 'server' | 'network' | 'unknown';

function classifyError(error: Error): ErrorType {
  const message = error.message.toLowerCase();
  if (message.includes('404') || message.includes('not found')) return 'not_found';
  if (message.includes('403') || message.includes('forbidden')) return 'forbidden';
  if (message.includes('451') || message.includes('consent')) return 'refused';
  if (message.includes('500') || message.includes('server')) return 'server';
  if (message.includes('network') || message.includes('fetch')) return 'network';
  return 'unknown';
}

const ERROR_TITLES: Record<ErrorType, string> = {
  not_found: 'Path Not Found',
  forbidden: 'Access Denied',
  refused: 'Consent Required',
  server: 'Server Error',
  network: 'Connection Lost',
  unknown: 'Something Went Wrong',
};

const ERROR_DESCRIPTIONS: Record<ErrorType, string> = {
  not_found: "This AGENTESE path doesn't exist in the registry.",
  forbidden: 'You lack the capabilities required to access this path.',
  refused: 'This entity has refused the interaction. Consent is required.',
  server: 'The server encountered an error processing this request.',
  network: 'Unable to connect to the AGENTESE gateway.',
  unknown: 'An unexpected error occurred.',
};

export function ProjectionError({ path, aspect, error, similarPaths }: ProjectionErrorProps) {
  const { shouldAnimate } = useMotionPreferences();
  const navigate = useNavigate();
  const [discoveredPaths, setDiscoveredPaths] = useState<string[]>([]);
  const errorType = classifyError(error);
  const parentPath = getParentPath(path);

  // Fetch similar paths from discovery
  useEffect(() => {
    if (!similarPaths) {
      const context = path.split('.')[0];
      apiClient
        .get<{ paths: string[] }>(`/agentese/discover/${context}`)
        .then((res) => {
          const similar = res.data.paths
            .filter((p) => p !== path && p.startsWith(path.split('.').slice(0, 2).join('.')))
            .slice(0, 5);
          setDiscoveredPaths(similar);
        })
        .catch(() => {
          /* ignore */
        });
    }
  }, [path, similarPaths]);

  const suggestions = similarPaths || discoveredPaths;

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] p-8">
      {/* Error icon with breathing animation */}
      <motion.div
        className="p-4 rounded-full bg-surface-error/10"
        animate={
          shouldAnimate
            ? {
                scale: [1, 1.05, 1],
              }
            : {}
        }
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <AlertCircle className="w-12 h-12 text-content-error" />
      </motion.div>

      {/* Error title */}
      <h1 className="mt-6 text-2xl font-semibold text-content-primary">{ERROR_TITLES[errorType]}</h1>

      {/* Path that failed */}
      <code className="mt-3 px-4 py-2 rounded-md bg-surface-inset font-mono text-sm text-content-secondary">
        {path}
        {aspect !== 'manifest' && `:${aspect}`}
      </code>

      {/* Error description */}
      <p className="mt-4 text-content-secondary max-w-md text-center">
        {ERROR_DESCRIPTIONS[errorType]}
      </p>

      {/* Technical error (collapsed) */}
      <details className="mt-4 text-sm text-content-tertiary">
        <summary className="cursor-pointer hover:text-content-secondary">Technical details</summary>
        <pre className="mt-2 p-3 rounded bg-surface-inset overflow-x-auto max-w-md">
          {error.message}
        </pre>
      </details>

      {/* Recovery actions */}
      <div className="mt-8 flex flex-wrap gap-3 justify-center">
        {/* Go back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-elevated hover:bg-surface-hover text-content-secondary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Go Back
        </button>

        {/* Retry */}
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface-elevated hover:bg-surface-hover text-content-secondary transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>

        {/* Go to parent */}
        {parentPath && (
          <Link
            to={formatAgentesePath(parentPath)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-sage/10 hover:bg-accent-sage/20 text-accent-sage transition-colors"
          >
            <Compass className="w-4 h-4" />
            Go to {parentPath.split('.').pop()}
          </Link>
        )}
      </div>

      {/* Similar paths suggestions */}
      {suggestions.length > 0 && (
        <div className="mt-8 w-full max-w-md">
          <h2 className="text-sm font-medium text-content-tertiary mb-3">Did you mean?</h2>
          <ul className="space-y-2">
            {suggestions.map((suggestedPath) => (
              <li key={suggestedPath}>
                <Link
                  to={formatAgentesePath(suggestedPath)}
                  className="block px-4 py-2 rounded-lg bg-surface-elevated hover:bg-surface-hover text-content-secondary font-mono text-sm transition-colors"
                >
                  {suggestedPath}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Valid contexts hint */}
      {errorType === 'not_found' && (
        <div className="mt-6 text-sm text-content-tertiary">
          <p>
            Valid contexts:{' '}
            {AGENTESE_CONTEXTS.map((ctx, i) => (
              <span key={ctx}>
                <code className="text-accent-sage">{ctx}</code>
                {i < AGENTESE_CONTEXTS.length - 1 && ', '}
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
}

export default ProjectionError;
