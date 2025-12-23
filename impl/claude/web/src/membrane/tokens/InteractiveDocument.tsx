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
import { BlockquoteToken } from './BlockquoteToken';
import { CodeBlockToken } from './CodeBlockToken';
import { HorizontalRuleToken } from './HorizontalRuleToken';
import { ImageToken } from './ImageToken';
import { LinkToken } from './LinkToken';
import { MarkdownTableToken } from './MarkdownTableToken';
import { PortalToken } from './PortalToken';
import { PrincipleToken } from './PrincipleToken';
import { TaskCheckboxToken } from './TaskCheckboxToken';
import { TextSpan } from './TextSpan';
import type {
  AGENTESEPathData,
  BlockquoteData,
  CodeBlockData,
  ImageTokenData,
  LinkData,
  MarkdownTableData,
  PortalData,
  PrincipleData,
  SceneGraph,
  SceneNode,
  TaskCheckboxData,
} from './types';
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

    // New token types with full rendering
    case 'CODE_REGION':
    case 'code_block': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<CodeBlockData>(content);
        return (
          <CodeBlockToken
            language={tokenData.language || ''}
            code={tokenData.code || content.source_text}
            sourceText={content.source_text}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    case 'MARKDOWN_TABLE':
    case 'markdown_table': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<MarkdownTableData>(content);
        return (
          <MarkdownTableToken
            columns={tokenData.columns || []}
            rows={tokenData.rows || []}
            sourceText={content.source_text}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    case 'LINK':
    case 'link': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<LinkData>(content);
        return (
          <LinkToken
            text={tokenData.text || content.source_text}
            url={tokenData.url || ''}
            onClick={onNavigate}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    case 'BLOCKQUOTE':
    case 'blockquote': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<BlockquoteData>(content);
        return (
          <BlockquoteToken
            content={tokenData.content || content.source_text}
            attribution={tokenData.attribution}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    case 'HORIZONTAL_RULE':
    case 'horizontal_rule': {
      return <HorizontalRuleToken />;
    }

    // NEW: Portal Token — Expandable hyperedge
    case 'PORTAL':
    case 'portal': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<PortalData>(content);
        return (
          <PortalToken
            edgeType={tokenData.edge_type || 'references'}
            sourcePath={tokenData.source_path}
            destinations={tokenData.destinations || []}
            onNavigate={onNavigate}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    // NEW: Principle Token — Architectural principle reference
    case 'PRINCIPLE':
    case 'principle':
    case 'PRINCIPLE_ANCHOR': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<PrincipleData>(content);
        return (
          <PrincipleToken
            principle={tokenData.principle || content.source_text}
            title={tokenData.title}
            description={tokenData.description}
            category={tokenData.category}
            onClick={onNavigate}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    // NEW: Image Token — Image with AI analysis
    case 'IMAGE':
    case 'image':
    case 'IMAGE_EMBED': {
      if (isMeaningTokenContent(content)) {
        const tokenData = getTokenData<ImageTokenData>(content);
        return (
          <ImageToken
            src={tokenData.src || ''}
            alt={tokenData.alt || ''}
            aiDescription={tokenData.ai_description}
            caption={tokenData.caption}
            onClick={onNavigate}
          />
        );
      }
      return <TextSpan content={String(content)} />;
    }

    // Remaining token types - render as placeholder
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

  const { nodes } = sceneGraph;

  return (
    <div className={`interactive-document ${className ?? ''}`}>
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
