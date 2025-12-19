/**
 * ProjectionError - Canonical error component for AGENTESE projections
 *
 * Design Philosophy: Neutral > sympathetic for errors.
 * - Clear, direct titles
 * - Actionable hints
 * - No poetry, no personality
 *
 * @see spec/protocols/agentese-as-route.md
 * @see constants/messages.ts for centralized error vocabulary
 */

import { motion } from 'framer-motion';
import { AlertCircle, ArrowLeft, Compass, RefreshCw } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import type { ProjectionErrorProps } from './types';
import { formatAgentesePath, getParentPath, AGENTESE_CONTEXTS } from '@/utils/parseAgentesePath';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { ErrorCategory } from '@/constants/messages';

/**
 * Classify an error into a canonical category.
 */
function classifyError(error: Error): ErrorCategory {
  const message = error.message.toLowerCase();
  if (message.includes('404') || message.includes('not found')) return ErrorCategory.NOT_FOUND;
  if (message.includes('403') || message.includes('forbidden')) return ErrorCategory.PERMISSION;
  if (message.includes('451') || message.includes('consent')) return ErrorCategory.CONSENT;
  if (message.includes('500') || message.includes('server') || message.includes('internal'))
    return ErrorCategory.SERVER;
  if (message.includes('network') || message.includes('fetch') || message.includes('econnrefused'))
    return ErrorCategory.NETWORK;
  if (message.includes('timeout')) return ErrorCategory.TIMEOUT;
  if (message.includes('422') || message.includes('validation')) return ErrorCategory.VALIDATION;
  if (message.includes('429') || message.includes('rate')) return ErrorCategory.RATE_LIMITED;
  return ErrorCategory.UNKNOWN;
}

/**
 * Neutral error titles — clear and direct.
 */
const ERROR_TITLES: Record<ErrorCategory, string> = {
  [ErrorCategory.NOT_FOUND]: 'Not Found',
  [ErrorCategory.PERMISSION]: 'Access Denied',
  [ErrorCategory.CONSENT]: 'Consent Required',
  [ErrorCategory.SERVER]: 'Server Error',
  [ErrorCategory.NETWORK]: 'Connection Failed',
  [ErrorCategory.TIMEOUT]: 'Request Timed Out',
  [ErrorCategory.VALIDATION]: 'Invalid Input',
  [ErrorCategory.RATE_LIMITED]: 'Rate Limited',
  [ErrorCategory.UNKNOWN]: 'Unexpected Error',
};

/**
 * Actionable hints — what to do next.
 */
const ERROR_HINTS: Record<ErrorCategory, string> = {
  [ErrorCategory.NOT_FOUND]: 'This path does not exist in the registry.',
  [ErrorCategory.PERMISSION]: 'You do not have access to this path.',
  [ErrorCategory.CONSENT]: 'This entity requires consent to interact.',
  [ErrorCategory.SERVER]: 'An error occurred on the server.',
  [ErrorCategory.NETWORK]: 'Unable to connect to the backend.',
  [ErrorCategory.TIMEOUT]: 'The request took too long.',
  [ErrorCategory.VALIDATION]: 'The request format is invalid.',
  [ErrorCategory.RATE_LIMITED]: 'Too many requests. Wait and retry.',
  [ErrorCategory.UNKNOWN]: 'An unexpected error occurred.',
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
      <h1 className="mt-6 text-2xl font-semibold text-content-primary">
        {ERROR_TITLES[errorType]}
      </h1>

      {/* Path that failed */}
      <code className="mt-3 px-4 py-2 rounded-md bg-surface-inset font-mono text-sm text-content-secondary">
        {path}
        {aspect !== 'manifest' && `:${aspect}`}
      </code>

      {/* Actionable hint */}
      <p className="mt-4 text-content-secondary max-w-md text-center">{ERROR_HINTS[errorType]}</p>

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
      {errorType === ErrorCategory.NOT_FOUND && (
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

// =============================================================================
// Exports for reuse
// =============================================================================

/**
 * Re-export for use by other components.
 */
export { classifyError, ErrorCategory };
export type { ErrorCategory as ErrorType };

export default ProjectionError;
