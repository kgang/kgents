/**
 * Error Components Stories
 *
 * STARK BIOME: Neutral Error Philosophy
 *
 * These stories showcase error handling components following the
 * "EmpathyError" philosophy: errors should be neutral and actionable,
 * not alarming or condescending.
 *
 * Philosophy:
 * - "Neutral > sympathetic for errors. Poetry belongs in features, not failures."
 * - Errors are opportunities for recovery, not blame
 * - Clear messaging with actionable hints
 * - Lucide icons over emojis for professional tone
 * - Respect user intelligence - no condescending messages
 *
 * Components:
 * - ErrorBoundary: React error boundary for catching render errors
 * - FriendlyError: User-friendly error display with recovery options
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { MemoryRouter } from 'react-router-dom';
import { ErrorBoundary } from './ErrorBoundary';
import { FriendlyError, NetworkError, NotFoundError, PermissionError, TimeoutError, EmptyState } from './FriendlyError';
import type { ErrorType } from './FriendlyError';

// =============================================================================
// Decorator for Router
// =============================================================================

const withRouter = (Story: React.ComponentType) => (
  <MemoryRouter>
    <Story />
  </MemoryRouter>
);

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Components/Error',
  tags: ['autodocs'],
  decorators: [withRouter],
  parameters: {
    docs: {
      description: {
        component: `
## EmpathyError Philosophy

> "Neutral > sympathetic for errors. Poetry belongs in features, not failures."

Error components in kgents follow a distinct philosophy that differs from typical
"friendly" error messaging:

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Neutral Tone** | Professional, not apologetic. No "Oops!" or "Uh oh!" |
| **Actionable** | Every error provides a clear next step |
| **Respectful** | Assume user intelligence, provide technical details when helpful |
| **Non-Alarming** | Slate gray icons, not red warning symbols |
| **Recovery-Focused** | Emphasis on what to do next, not what went wrong |

### Visual Design (STARK BIOME)

- Steel background surfaces (\`#141418\`)
- Neutral gray icons (Lucide, not emoji)
- Subtle borders, not aggressive colors
- Breathing animation only when appropriate (not for errors)

### Error Categories

| Category | Title | Hint |
|----------|-------|------|
| \`network\` | Connection Failed | Check your network connection |
| \`timeout\` | Request Timed Out | Try again in a moment |
| \`notFound\` | Not Found | Use "discover" to see available paths |
| \`permission\` | Access Denied | Check API key or permissions |
| \`unknown\` | Unexpected Error | Try again or refresh the page |

### Philosophy Quote

> "Errors are not failures of the system. They are the system communicating its boundaries."
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// ErrorBoundary Stories
// =============================================================================

/** Component that throws an error for testing ErrorBoundary */
function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Simulated render error for demonstration');
  }
  return (
    <div className="p-4 bg-gray-800 rounded-lg text-gray-200">
      Component rendered successfully
    </div>
  );
}

/**
 * Component that throws after mount.
 * Commented out for lint compliance but available for interactive testing:
 *
 * function _DelayedThrowingComponent() {
 *   const [hasThrown, setHasThrown] = useState(false);
 *   useEffect(() => {
 *     const timer = setTimeout(() => setHasThrown(true), 2000);
 *     return () => clearTimeout(timer);
 *   }, []);
 *   if (hasThrown) throw new Error('Error after 2 seconds');
 *   return <div>This component will error in 2 seconds...</div>;
 * }
 */

export const ErrorBoundaryDefault: StoryObj = {
  name: 'ErrorBoundary - Default Fallback',
  render: () => (
    <ErrorBoundary>
      <ThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Default ErrorBoundary fallback UI. Shows:
- Neutral AlertCircle icon (not alarming red)
- "Component Error" title
- Error message text
- "Try Again" button with sage green accent

The design is professional and recovery-focused, not apologetic.
        `,
      },
    },
  },
};

export const ErrorBoundaryHealthy: StoryObj = {
  name: 'ErrorBoundary - Healthy Component',
  render: () => (
    <ErrorBoundary>
      <ThrowingComponent shouldThrow={false} />
    </ErrorBoundary>
  ),
  parameters: {
    docs: {
      description: {
        story: 'When children render successfully, ErrorBoundary is invisible.',
      },
    },
  },
};

export const ErrorBoundaryCustomFallback: StoryObj = {
  name: 'ErrorBoundary - Custom Fallback',
  render: () => (
    <ErrorBoundary
      fallback={
        <div className="p-8 bg-gray-800 rounded-lg text-center">
          <div className="text-2xl mb-4 text-gray-400">Custom Fallback</div>
          <p className="text-gray-500">
            You can provide any React node as the fallback UI.
          </p>
        </div>
      }
    >
      <ThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Custom fallback UI can be provided via the `fallback` prop.',
      },
    },
  },
};

export const ErrorBoundaryWithCallback: StoryObj = {
  name: 'ErrorBoundary - With onError Callback',
  render: () => {
    const handleError = (error: Error) => {
      console.info('Error caught by boundary:', error.message);
      // In production: send to error tracking service
    };

    return (
      <div>
        <p className="text-gray-400 text-sm mb-4">
          Check console for error callback log.
        </p>
        <ErrorBoundary onError={handleError}>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'The `onError` callback can be used for error logging or telemetry.',
      },
    },
  },
};

// =============================================================================
// FriendlyError Stories
// =============================================================================

export const FriendlyErrorNetwork: StoryObj = {
  name: 'FriendlyError - Network',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError
        type="network"
        onRetry={() => console.info('Retry clicked')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Network error with retry option. Uses Wifi icon.

**Title:** "Connection Failed"
**Hint:** "Check your network connection"
        `,
      },
    },
  },
};

export const FriendlyErrorNotFound: StoryObj = {
  name: 'FriendlyError - Not Found',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError type="notFound" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
404 Not Found error. Uses MapPin icon.

**Title:** "Not Found"
**Hint:** "Use 'discover' to see available paths"

The hint references AGENTESE discovery commands - contextually appropriate.
        `,
      },
    },
  },
};

export const FriendlyErrorPermission: StoryObj = {
  name: 'FriendlyError - Permission',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError type="permission" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Permission denied error. Uses Lock icon.

**Title:** "Access Denied"
**Hint:** "Check API key or permissions"
        `,
      },
    },
  },
};

export const FriendlyErrorTimeout: StoryObj = {
  name: 'FriendlyError - Timeout',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError
        type="timeout"
        onRetry={() => console.info('Retry clicked')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Request timeout error. Uses Clock icon.

**Title:** "Request Timed Out"
**Hint:** "Try again in a moment"
        `,
      },
    },
  },
};

export const FriendlyErrorUnknown: StoryObj = {
  name: 'FriendlyError - Unknown',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError
        type="unknown"
        message="TypeError: Cannot read property 'foo' of undefined"
        onRetry={() => console.info('Retry clicked')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Unknown/unexpected error with technical details. Uses HelpCircle icon.

**Title:** "Unexpected Error"
**Hint:** "Try again or refresh the page"

Technical details are shown in a monospace block for debugging.
        `,
      },
    },
  },
};

export const FriendlyErrorWithMessage: StoryObj = {
  name: 'FriendlyError - With Custom Message',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <FriendlyError
        type="network"
        message="ECONNREFUSED: Connection refused at localhost:8000"
        onRetry={() => console.info('Retry clicked')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Custom technical message is shown in a monospace block below the hint.',
      },
    },
  },
};

// =============================================================================
// Size Variants
// =============================================================================

export const FriendlyErrorSizes: StoryObj = {
  name: 'FriendlyError - Size Variants',
  render: () => (
    <div className="flex flex-col gap-8 bg-gray-900 p-8 rounded-lg">
      <div>
        <h4 className="text-gray-400 text-sm mb-2 uppercase tracking-wide">Small</h4>
        <FriendlyError type="network" size="sm" onRetry={() => {}} />
      </div>
      <div>
        <h4 className="text-gray-400 text-sm mb-2 uppercase tracking-wide">Medium (Default)</h4>
        <FriendlyError type="network" size="md" onRetry={() => {}} />
      </div>
      <div>
        <h4 className="text-gray-400 text-sm mb-2 uppercase tracking-wide">Large</h4>
        <FriendlyError type="network" size="lg" onRetry={() => {}} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Three size variants for different contexts: inline (sm), default (md), and full-page (lg).',
      },
    },
  },
};

// =============================================================================
// All Error Types Gallery
// =============================================================================

export const AllErrorTypes: StoryObj = {
  name: 'All Error Types Gallery',
  render: () => {
    const types: ErrorType[] = ['network', 'notFound', 'permission', 'timeout', 'empty', 'unknown'];

    return (
      <div className="grid grid-cols-2 gap-6 bg-gray-900 p-8 rounded-lg">
        {types.map((type) => (
          <div key={type} className="bg-gray-800/50 rounded-lg p-4">
            <FriendlyError
              type={type}
              size="sm"
              onRetry={type !== 'notFound' && type !== 'permission' && type !== 'empty' ? () => {} : undefined}
            />
          </div>
        ))}
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Gallery of all error types showing icon consistency and neutral messaging.',
      },
    },
  },
};

// =============================================================================
// Specialized Components
// =============================================================================

export const SpecializedErrors: StoryObj = {
  name: 'Specialized Error Components',
  render: () => (
    <div className="flex flex-col gap-8">
      <div className="bg-gray-900 rounded-lg overflow-hidden">
        <NotFoundError />
      </div>
      <div className="bg-gray-900 p-8 rounded-lg">
        <NetworkError onRetry={() => console.info('Retry')} />
      </div>
      <div className="bg-gray-900 p-8 rounded-lg">
        <TimeoutError onRetry={() => console.info('Retry')} />
      </div>
      <div className="bg-gray-900 p-8 rounded-lg">
        <PermissionError />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Pre-configured specialized error components for common scenarios.',
      },
    },
  },
};

// =============================================================================
// Empty State
// =============================================================================

export const EmptyStateDefault: StoryObj = {
  name: 'EmptyState - Default',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <EmptyState />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Empty state is not an error - it's an invitation.

Uses Leaf icon to suggest growth potential. Default message: "Nothing here yet"
        `,
      },
    },
  },
};

export const EmptyStateWithAction: StoryObj = {
  name: 'EmptyState - With Action',
  render: () => (
    <div className="bg-gray-900 p-8 rounded-lg">
      <EmptyState
        message="No witness marks recorded yet"
        actionLabel="Create First Mark"
        onAction={() => console.info('Create mark')}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty state with a call-to-action button for user activation.',
      },
    },
  },
};

// =============================================================================
// Responsive Demo
// =============================================================================

export const ResponsiveError: StoryObj = {
  name: 'Responsive Error Display',
  render: () => (
    <div className="flex flex-col gap-8">
      <div className="text-gray-400 text-sm">
        Resize viewport to see responsive behavior
      </div>

      {/* Constrained width container */}
      <div className="bg-gray-900 rounded-lg p-4" style={{ maxWidth: '320px' }}>
        <h4 className="text-gray-500 text-xs mb-2 uppercase">Mobile (320px)</h4>
        <FriendlyError type="network" size="sm" onRetry={() => {}} />
      </div>

      {/* Medium container */}
      <div className="bg-gray-900 rounded-lg p-6" style={{ maxWidth: '480px' }}>
        <h4 className="text-gray-500 text-xs mb-2 uppercase">Tablet (480px)</h4>
        <FriendlyError type="network" size="md" onRetry={() => {}} />
      </div>

      {/* Full width container */}
      <div className="bg-gray-900 rounded-lg p-8">
        <h4 className="text-gray-500 text-xs mb-2 uppercase">Desktop (Full)</h4>
        <FriendlyError type="network" size="lg" onRetry={() => {}} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Error components adapt to available space using size variants.',
      },
    },
  },
};

// =============================================================================
// Philosophy Documentation
// =============================================================================

export const EmpathyErrorPhilosophy: StoryObj = {
  name: 'EmpathyError Philosophy',
  render: () => (
    <div
      className="p-8 rounded-lg max-w-3xl"
      style={{ background: '#141418', border: '1px solid #28282F' }}
    >
      <h2 className="text-xl font-medium mb-6 text-white">
        The EmpathyError Philosophy
      </h2>

      <div className="space-y-6 text-gray-400">
        <section>
          <h3 className="text-cyan-400 font-medium mb-2">What We Do NOT Do</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>No "Oops!" or "Uh oh!" - not apologetic</li>
            <li>No red warning colors - not alarming</li>
            <li>No sad emoji faces - not condescending</li>
            <li>No "something went wrong" - too vague</li>
            <li>No blame-shifting language - not defensive</li>
          </ul>
        </section>

        <section>
          <h3 className="text-cyan-400 font-medium mb-2">What We DO</h3>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li>State what happened clearly: "Connection Failed"</li>
            <li>Provide actionable hint: "Check your network connection"</li>
            <li>Show technical details when helpful</li>
            <li>Offer recovery action: "Try Again" button</li>
            <li>Use neutral visual design (slate gray icons)</li>
          </ul>
        </section>

        <section>
          <h3 className="text-cyan-400 font-medium mb-2">Design Rationale</h3>
          <p className="text-sm">
            Errors communicate system boundaries. Users encountering errors are already
            frustrated - adding alarm or false sympathy makes it worse. A neutral,
            professional tone respects user intelligence and focuses attention on
            recovery rather than the problem itself.
          </p>
        </section>

        <section className="p-4 rounded-lg bg-gray-800/50 border-l-2 border-cyan-600">
          <p className="text-sm italic">
            "Neutral {'>'}  sympathetic for errors. Poetry belongs in features, not failures."
          </p>
          <p className="text-xs text-gray-500 mt-2">— kgents voice principles</p>
        </section>
      </div>
    </div>
  ),
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        story: `
## The Complete EmpathyError Philosophy

This story documents the reasoning behind kgents error messaging.

Errors in kgents follow a "neutral empathy" approach:
- **Empathy** through actionable hints and recovery options
- **Neutral** through professional tone and visual design

The goal is to help users recover quickly without adding emotional weight
to what is already a frustrating situation.
        `,
      },
    },
  },
};
