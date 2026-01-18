/**
 * ContainerProvider — Context for three-container architecture
 *
 * Grounded in: spec/ui/axioms.md — A1 (Creativity), A2 (Sloppification), A6 (Authority)
 *
 * Three containers:
 * - HUMAN: Full authority, no AI mediation
 * - COLLABORATION: Dialectic visible, fusion tracked
 * - AI: Low intensity, requires review
 */

import { createContext, useContext, useMemo, type ReactNode } from 'react';
import type { ContainerContext, ContainerType, Provenance } from '../../types';
import {
  createHumanContext,
  createCollaborationContext,
  createAIContext,
  getContainerFromProvenance,
  getContainerClass,
} from '../../types';

/**
 * React context for container information.
 */
const ContainerReactContext = createContext<ContainerContext>(createHumanContext());

/**
 * Hook to access current container context.
 */
export function useContainer(): ContainerContext {
  return useContext(ContainerReactContext);
}

/**
 * Provider for container context.
 */
interface ContainerProviderProps {
  /** Container type */
  type: ContainerType;

  /** Whether AI content has been reviewed (for AI container) */
  reviewed?: boolean;

  /** Children to render within container */
  children: ReactNode;
}

export function ContainerProvider({ type, reviewed = false, children }: ContainerProviderProps) {
  const context = useMemo(() => {
    switch (type) {
      case 'human':
        return createHumanContext();
      case 'collaboration':
        return createCollaborationContext();
      case 'ai':
        return createAIContext(reviewed);
    }
  }, [type, reviewed]);

  const className = getContainerClass(context);

  return (
    <ContainerReactContext.Provider value={context}>
      <div className={className} data-container={type}>
        {children}
      </div>
    </ContainerReactContext.Provider>
  );
}

/**
 * Auto-detect container from provenance.
 */
interface ProvenanceContainerProps {
  /** Provenance to derive container from */
  provenance: Provenance;

  /** Children to render */
  children: ReactNode;
}

export function ProvenanceContainer({ provenance, children }: ProvenanceContainerProps) {
  const type = getContainerFromProvenance(provenance.author);
  const reviewed = provenance.reviewed;

  return (
    <ContainerProvider type={type} reviewed={reviewed}>
      {children}
    </ContainerProvider>
  );
}

/**
 * Human container — full authority.
 */
export function HumanContainer({ children }: { children: ReactNode }) {
  return <ContainerProvider type="human">{children}</ContainerProvider>;
}

/**
 * Collaboration container — dialectic visible.
 */
export function CollaborationContainer({ children }: { children: ReactNode }) {
  return <ContainerProvider type="collaboration">{children}</ContainerProvider>;
}

/**
 * AI container — requires review.
 */
export function AIContainer({
  reviewed = false,
  children,
}: {
  reviewed?: boolean;
  children: ReactNode;
}) {
  return (
    <ContainerProvider type="ai" reviewed={reviewed}>
      {children}
    </ContainerProvider>
  );
}

export { ContainerReactContext };
export default ContainerProvider;
