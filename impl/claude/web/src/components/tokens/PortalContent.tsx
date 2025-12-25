/**
 * PortalContent — Resource-type-aware content renderer
 *
 * Dispatches to appropriate preview component based on resource type.
 * Used when expanding portal tokens to show inline content.
 *
 * See spec/protocols/portal-resource-system.md §6.2
 */

import { FileContent } from './FileContent';
import { ChatSessionPreview } from './ChatSessionPreview';
import { TurnPreview } from './TurnPreview';
import { MarkPreview } from './MarkPreview';
import { ConstitutionalPreview } from './ConstitutionalPreview';
import { GenericContent } from './GenericContent';
import type { ResolvedResource } from './types';
import './tokens.css';

// =============================================================================
// Types
// =============================================================================

export interface PortalContentProps {
  /** Resolved resource to render */
  resource: ResolvedResource;
  /** Compact mode (shorter previews) */
  compact?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * PortalContent — Resource-aware content renderer
 *
 * Dispatches to:
 * - FileContent (file:)
 * - ChatSessionPreview (chat:)
 * - TurnPreview (turn:)
 * - MarkPreview (mark:)
 * - ConstitutionalPreview (constitutional:)
 * - GenericContent (fallback)
 */
export function PortalContent({ resource, compact = false }: PortalContentProps) {
  // Type-safe content casting with proper type guards
  const renderContent = () => {
    switch (resource.resource_type) {
      case 'file':
        return (
          <FileContent
            content={resource.content as string}
            path={resource.metadata.path as string | undefined}
            compact={compact}
          />
        );

      case 'chat':
        return (
          <ChatSessionPreview
            session={resource.content as any}
            compact={compact}
          />
        );

      case 'turn':
        return (
          <TurnPreview
            turn={resource.content as any}
            turnNumber={resource.metadata.turn_number as number | undefined}
            compact={compact}
          />
        );

      case 'mark':
        return (
          <MarkPreview
            mark={resource.content as any}
            turnNumber={resource.metadata.turn_number as number | undefined}
            compact={compact}
          />
        );

      case 'constitutional':
        return (
          <ConstitutionalPreview
            data={resource.content as any}
            compact={compact}
          />
        );

      case 'trace':
        // TODO: Implement TracePreview when ready
        return <GenericContent content={resource.content} compact={compact} />;

      case 'evidence':
        // TODO: Implement EvidencePreview when ready
        return <GenericContent content={resource.content} compact={compact} />;

      case 'crystal':
        // TODO: Implement CrystalPreview when ready
        return <GenericContent content={resource.content} compact={compact} />;

      case 'node':
        // TODO: Implement NodePreview when ready
        return <GenericContent content={resource.content} compact={compact} />;

      default:
        return <GenericContent content={resource.content} compact={compact} />;
    }
  };

  return (
    <div className={`portal-content portal-content--${resource.resource_type}`}>
      {/* Resource header */}
      <div className="portal-content__header">
        <span className="portal-content__title">{resource.title}</span>
        {typeof resource.metadata.session_id === 'string' ? (
          <code className="portal-content__id">
            {resource.metadata.session_id}
          </code>
        ) : null}
      </div>

      {/* Resource-specific content */}
      <div className="portal-content__body">{renderContent() as React.ReactNode}</div>

      {/* Available actions */}
      {resource.actions.length > 0 && !compact && (
        <div className="portal-content__actions">
          {resource.actions.map((action) => (
            <button
              key={action}
              type="button"
              className="portal-content__action"
              title={action}
            >
              {formatActionName(action)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format action name from snake_case to Title Case
 */
function formatActionName(action: string): string {
  return action
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export default PortalContent;
