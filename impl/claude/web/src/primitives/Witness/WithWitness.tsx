/**
 * WithWitness HOC
 *
 * Higher-order component that automatically witnesses state changes.
 *
 * "Every state change is a morphism that returns (newState, witnessMark)"
 */

import { ComponentType, useCallback } from 'react';
import type { WitnessConfig } from './types';
import { useWitness } from './useWitness';

// =============================================================================
// HOC Options
// =============================================================================

export interface WithWitnessOptions extends WitnessConfig {
  /** Component display name for debugging */
  displayName?: string;

  /** Whether to inject witness props */
  injectProps?: boolean;
}

// =============================================================================
// Injected Props
// =============================================================================

export interface WitnessInjectedProps {
  /** Witness an action */
  witness: (
    action: string,
    options?: {
      reasoning?: string;
      principles?: string[];
      metadata?: Record<string, unknown>;
      automatic?: boolean;
      fireAndForget?: boolean;
    }
  ) => Promise<string | null>;

  /** Whether currently witnessing */
  isWitnessing: boolean;

  /** Number of pending marks */
  pendingCount: number;
}

// =============================================================================
// HOC Implementation
// =============================================================================

/**
 * HOC that adds automatic witnessing to a component.
 *
 * @example
 * // Basic usage
 * const WitnessedPortal = withWitness(PortalToken, {
 *   action: 'portal-interaction',
 *   principles: ['joy_inducing', 'composable'],
 *   automatic: true,
 * });
 *
 * // With injected props
 * interface MyProps extends WitnessInjectedProps {
 *   value: string;
 * }
 *
 * const WitnessedComponent = withWitness(MyComponent, {
 *   action: 'component-action',
 *   injectProps: true,
 * });
 */
export function withWitness<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: WithWitnessOptions
): ComponentType<Omit<P, keyof WitnessInjectedProps>> {
  const {
    action,
    principles = [],
    automatic = true,
    enabled = true,
    metadata,
    displayName,
    injectProps = false,
  } = options;

  const WithWitnessComponent: ComponentType<Omit<P, keyof WitnessInjectedProps>> = (props) => {
    // Witness hook
    const { witness, isWitnessing, pendingCount } = useWitness({ enabled });

    // Wrapped witness function with defaults
    const wrappedWitness = useCallback(
      async (
        witnessAction: string,
        witnessOptions?: {
          reasoning?: string;
          principles?: string[];
          metadata?: Record<string, unknown>;
          automatic?: boolean;
          fireAndForget?: boolean;
        }
      ) => {
        return witness(witnessAction || action, {
          reasoning: witnessOptions?.reasoning,
          principles: witnessOptions?.principles || principles,
          metadata: {
            ...metadata,
            ...witnessOptions?.metadata,
          },
          automatic: witnessOptions?.automatic ?? automatic,
          fireAndForget: witnessOptions?.fireAndForget ?? true,
        });
      },
      [witness]
    );

    // Build props
    const componentProps = {
      ...props,
      ...(injectProps
        ? {
            witness: wrappedWitness,
            isWitnessing,
            pendingCount,
          }
        : {}),
    } as P;

    return <WrappedComponent {...componentProps} />;
  };

  // Set display name for debugging
  WithWitnessComponent.displayName =
    displayName || `WithWitness(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  return WithWitnessComponent;
}

// =============================================================================
// Convenience Variants
// =============================================================================

/**
 * Convenience HOC for portal components.
 */
export function withPortalWitness<P extends object>(
  WrappedComponent: ComponentType<P>,
  options?: Partial<WithWitnessOptions>
): ComponentType<Omit<P, keyof WitnessInjectedProps>> {
  return withWitness(WrappedComponent, {
    action: 'portal-interaction',
    principles: ['joy_inducing', 'composable'],
    automatic: true,
    ...options,
  });
}

/**
 * Convenience HOC for navigation components.
 */
export function withNavigationWitness<P extends object>(
  WrappedComponent: ComponentType<P>,
  options?: Partial<WithWitnessOptions>
): ComponentType<Omit<P, keyof WitnessInjectedProps>> {
  return withWitness(WrappedComponent, {
    action: 'navigation',
    principles: ['tasteful', 'composable'],
    automatic: true,
    ...options,
  });
}

/**
 * Convenience HOC for edit components.
 */
export function withEditWitness<P extends object>(
  WrappedComponent: ComponentType<P>,
  options?: Partial<WithWitnessOptions>
): ComponentType<Omit<P, keyof WitnessInjectedProps>> {
  return withWitness(WrappedComponent, {
    action: 'edit',
    principles: ['generative', 'composable'],
    automatic: true,
    ...options,
  });
}

/**
 * Convenience HOC for chat components.
 */
export function withChatWitness<P extends object>(
  WrappedComponent: ComponentType<P>,
  options?: Partial<WithWitnessOptions>
): ComponentType<Omit<P, keyof WitnessInjectedProps>> {
  return withWitness(WrappedComponent, {
    action: 'chat',
    principles: ['ethical', 'joy_inducing'],
    automatic: true,
    ...options,
  });
}

export default withWitness;
