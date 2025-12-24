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
  MeaningTokenContent,
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
// Token Renderer Context (shared by all renderers)
// =============================================================================

interface TokenRenderContext {
  content: SceneNode['content'];
  onNavigate?: (path: string) => void;
  onToggle?: (newState: boolean, taskId?: string) => Promise<void>;
  effectiveKind: string;
}

type TokenRenderer = (ctx: TokenRenderContext) => React.ReactElement;

// =============================================================================
// Individual Token Renderers
// =============================================================================

function renderAGENTESEPortal(ctx: TokenRenderContext): React.ReactElement {
  const { content, onNavigate } = ctx;
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
  return <AGENTESEPathToken path={String(content)} exists={true} onClick={onNavigate} />;
}

function renderTaskToggle(ctx: TokenRenderContext): React.ReactElement {
  const { content, onToggle } = ctx;
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

function renderPlainText(ctx: TokenRenderContext): React.ReactElement {
  const { content } = ctx;
  if (isTextContent(content)) {
    return <TextSpan content={content} />;
  }
  if (isMeaningTokenContent(content)) {
    return <TextSpan content={content.source_text} />;
  }
  return <TextSpan content={String(content)} />;
}

function renderCodeBlock(ctx: TokenRenderContext): React.ReactElement {
  const { content } = ctx;
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

function renderMarkdownTable(ctx: TokenRenderContext): React.ReactElement {
  const { content } = ctx;
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

function renderLink(ctx: TokenRenderContext): React.ReactElement {
  const { content, onNavigate } = ctx;
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

function renderBlockquote(ctx: TokenRenderContext): React.ReactElement {
  const { content } = ctx;
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

function renderHorizontalRule(): React.ReactElement {
  return <HorizontalRuleToken />;
}

function renderPortal(ctx: TokenRenderContext): React.ReactElement {
  const { content, onNavigate } = ctx;
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

function renderPrinciple(ctx: TokenRenderContext): React.ReactElement {
  const { content, onNavigate } = ctx;
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

function renderImage(ctx: TokenRenderContext): React.ReactElement {
  const { content, onNavigate } = ctx;
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

function renderRequirementTrace(ctx: TokenRenderContext): React.ReactElement {
  const { content, effectiveKind } = ctx;
  if (isMeaningTokenContent(content)) {
    return (
      <span className={`token-placeholder token-placeholder--${effectiveKind.toLowerCase()}`}>
        {(content as MeaningTokenContent).source_text}
      </span>
    );
  }
  return <TextSpan content={String(content)} />;
}

function renderDefault(ctx: TokenRenderContext): React.ReactElement {
  const { content } = ctx;
  if (isTextContent(content)) {
    return <TextSpan content={content} />;
  }
  if (isMeaningTokenContent(content)) {
    return <TextSpan content={content.source_text} />;
  }
  return <TextSpan content={String(content)} />;
}

// =============================================================================
// Token Renderer Registry
// =============================================================================

const TOKEN_RENDERERS: Record<string, TokenRenderer> = {
  // AGENTESE Portal
  AGENTESE_PORTAL: renderAGENTESEPortal,

  // Task Toggle
  TASK_TOGGLE: renderTaskToggle,

  // Plain Text
  TEXT: renderPlainText,
  PLAIN_TEXT: renderPlainText,

  // Code Block
  CODE_REGION: renderCodeBlock,
  code_block: renderCodeBlock,

  // Markdown Table
  MARKDOWN_TABLE: renderMarkdownTable,
  markdown_table: renderMarkdownTable,

  // Link
  LINK: renderLink,
  link: renderLink,

  // Blockquote
  BLOCKQUOTE: renderBlockquote,
  blockquote: renderBlockquote,

  // Horizontal Rule
  HORIZONTAL_RULE: renderHorizontalRule,
  horizontal_rule: renderHorizontalRule,

  // Portal
  PORTAL: renderPortal,
  portal: renderPortal,

  // Principle
  PRINCIPLE: renderPrinciple,
  principle: renderPrinciple,
  PRINCIPLE_ANCHOR: renderPrinciple,

  // Image
  IMAGE: renderImage,
  image: renderImage,
  IMAGE_EMBED: renderImage,

  // Requirement Trace
  REQUIREMENT_TRACE: renderRequirementTrace,
};

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

  // Build render context
  const ctx: TokenRenderContext = { content, onNavigate, onToggle, effectiveKind };

  // Look up renderer in registry, fall back to default
  const renderer = TOKEN_RENDERERS[effectiveKind] ?? renderDefault;
  return renderer(ctx);
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
