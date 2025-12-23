/**
 * InteractiveDocument — SceneGraph renderer for Interactive Text.
 *
 * Receives a SceneGraph from self.document.parse and renders it as
 * interactive React components using the SceneNodeRenderer dispatcher.
 *
 * "Specs stop being documentation and become live control surfaces."
 *
 * See: spec/protocols/interactive-text.md
 */

import { memo, useCallback } from 'react';

import { AGENTESEPathToken } from './AGENTESEPathToken';
import { TaskCheckboxToken } from './TaskCheckboxToken';
import { TextSpan } from './TextSpan';
import type { AGENTESEPathData, SceneGraph, SceneNode, TaskCheckboxData } from './types';
import { getTokenData, isMeaningTokenContent, isTextContent } from './types';

import './tokens.css';

// =============================================================================
// Props
// =============================================================================

interface InteractiveDocumentProps {
  sceneGraph: SceneGraph;
  onNavigate?: (path: string) => void;
  onToggle?: (newState: boolean, taskId?: string) => Promise<void>;
  className?: string;
}

interface SceneNodeRendererProps {
  node: SceneNode;
  onNavigate?: (path: string) => void;
  onToggle?: (newState: boolean, taskId?: string) => Promise<void>;
}

// =============================================================================
// Scene Node Renderer (Dispatcher)
// =============================================================================

const SceneNodeRenderer = memo(function SceneNodeRenderer({
  node,
  onNavigate,
  onToggle,
}: SceneNodeRendererProps) {
  const { kind, content, metadata } = node;

  // Get the meaning token kind from metadata (backend stores it there)
  const meaningTokenKind = metadata?.meaning_token_kind as string | undefined;

  // Determine which component to render based on kind or meaning_token_kind
  const effectiveKind = meaningTokenKind || kind;

  switch (effectiveKind) {
    case 'AGENTESE_PORTAL': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<AGENTESEPathData>(content);
        return (
          <AGENTESEPathToken
            path={tokenData.path || content.source_text.replace(/`/g, '')}
            exists={tokenData.exists ?? true}
            onClick={onNavigate}
          />
        );
      }
      // Fallback: treat content as path string
      return <AGENTESEPathToken path={String(content)} exists={true} onClick={onNavigate} />;
    }

    case 'TASK_TOGGLE': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<TaskCheckboxData>(content);
        return (
          <TaskCheckboxToken
            checked={tokenData.checked ?? false}
            description={tokenData.description || content.source_text}
            taskId={content.token_id}
            onToggle={onToggle}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    case 'TEXT':
    case 'PLAIN_TEXT': {
      if (isTextContent(content)) {
        return <TextSpan content={content} />;
      }
      if (isMeaningTokenContent(content)) {
        return <TextSpan content={content.source_text} />;
      }
      return <TextSpan content={String(content)} />;
    }

    // Future token types - render as plain text for now
    case 'CODE_REGION':
    case 'IMAGE_EMBED':
    case 'PRINCIPLE_ANCHOR':
    case 'REQUIREMENT_TRACE': {
      if (isMeaningTokenContent(content)) {
        return (
          <span className={`token-placeholder token-placeholder--${effectiveKind.toLowerCase()}`}>
            {content.source_text}
          </span>
        );
      }
      return <TextSpan content={String(content)} />;
    }

    default: {
      // Unknown kind - render as text
      if (isTextContent(content)) {
        return <TextSpan content={content} />;
      }
      if (isMeaningTokenContent(content)) {
        return <TextSpan content={content.source_text} />;
      }
      return <TextSpan content={String(content)} />;
    }
  }
});

// =============================================================================
// Interactive Document (Container)
// =============================================================================

export const InteractiveDocument = memo(function InteractiveDocument({
  sceneGraph,
  onNavigate,
  onToggle,
  className,
}: InteractiveDocumentProps) {
  // Memoize handlers
  const handleNavigate = useCallback(
    (path: string) => {
      onNavigate?.(path);
    },
    [onNavigate]
  );

  const handleToggle = useCallback(
    async (newState: boolean, taskId?: string) => {
      await onToggle?.(newState, taskId);
    },
    [onToggle]
  );

  const { nodes, layout } = sceneGraph;

  return (
    <div
      className={`interactive-document ${className ?? ''}`}
      style={{
        display: 'flex',
        flexDirection: layout?.direction === 'horizontal' ? 'row' : 'column',
        gap: layout?.gap ? `${layout.gap}rem` : undefined,
      }}
      data-mode={layout?.mode || 'COMFORTABLE'}
    >
      {nodes.map((node) => (
        <SceneNodeRenderer
          key={node.id}
          node={node}
          onNavigate={handleNavigate}
          onToggle={handleToggle}
        />
      ))}
    </div>
  );
});
