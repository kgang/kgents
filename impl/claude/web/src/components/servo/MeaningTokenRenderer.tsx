/**
 * MeaningTokenRenderer - Renders Interactive Text tokens to React
 *
 * This component bridges Interactive Text's MeaningTokens to the Servo rendering layer.
 * It receives token data from SceneNode.content and renders the appropriate visualization.
 *
 * Token Types:
 *   - AGENTESE_PORTAL: Glowing path link with navigate/hover
 *   - TASK_TOGGLE: Checkbox with toggle affordance
 *   - IMAGE_EMBED: Image with expand/analyze
 *   - CODE_REGION: Code block with run/edit
 *   - PRINCIPLE_ANCHOR: Principle reference badge
 *   - REQUIREMENT_TRACE: Requirement reference badge
 *   - PLAIN_TEXT: Non-token markdown prose
 *
 * Design Philosophy:
 *   "The text IS the interface" - Interactive Text manifesto
 *   "Joy-inducing > merely functional" - Constitution
 *
 * @see protocols/agentese/projection/tokens_to_scene.py - Bridge
 * @see services/interactive_text/projectors/web.py - ReactElement specs
 */

import React, { useCallback } from 'react';
import { BreathingContainer } from '@/components/genesis/BreathingContainer';
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from './theme';

// =============================================================================
// Types (matching tokens_to_scene.py MeaningTokenContent)
// =============================================================================

export type MeaningTokenKind =
  | 'AGENTESE_PORTAL'
  | 'TASK_TOGGLE'
  | 'IMAGE_EMBED'
  | 'CODE_REGION'
  | 'PRINCIPLE_ANCHOR'
  | 'REQUIREMENT_TRACE'
  | 'PLAIN_TEXT';

export interface Affordance {
  name: string;
  action: string;
  handler: string;
  enabled: boolean;
  description?: string;
}

export interface MeaningTokenContent {
  token_type: string;
  source_text: string;
  source_position: [number, number];
  token_id: string;
  token_data: Record<string, unknown>;
  affordances: Affordance[];
}

export interface MeaningTokenRendererProps {
  /** The kind of meaning token */
  kind: MeaningTokenKind;
  /** The token content from SceneNode.content */
  content: MeaningTokenContent | string;
  /** Human-readable label */
  label: string;
  /** Whether this token is selected */
  isSelected?: boolean;
  /** Click handler (delegates to affordance) */
  onClick?: () => void;
  /** Hover handler (delegates to affordance) */
  onHover?: (hovering: boolean) => void;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Token-Specific Renderers
// =============================================================================

interface AGENTESEPortalProps {
  content: MeaningTokenContent;
  isSelected: boolean;
  onClick?: () => void;
}

function AGENTESEPortal({ content, isSelected, onClick }: AGENTESEPortalProps) {
  const path = content.token_data?.path as string | undefined;
  const isGhost = content.token_data?.is_ghost as boolean | undefined;

  return (
    <BreathingContainer intensity="subtle">
      <button
        onClick={onClick}
        className={`
          inline-flex items-center gap-1 px-2 py-0.5 rounded
          font-mono text-sm
          transition-all duration-200
          ${
            isGhost
              ? 'text-gray-400/70 italic'
              : 'text-emerald-400 hover:text-emerald-300 hover:bg-emerald-900/30'
          }
          ${isSelected ? 'ring-2 ring-emerald-500/50' : ''}
        `}
      >
        <span className={`${isGhost ? '' : 'animate-pulse'}`}>{isGhost ? '👻' : '🌿'}</span>
        <code>{path ?? content.source_text}</code>
      </button>
    </BreathingContainer>
  );
}

interface TaskToggleProps {
  content: MeaningTokenContent;
  isSelected: boolean;
  onClick?: () => void;
}

function TaskToggle({ content, isSelected, onClick }: TaskToggleProps) {
  const checked = content.token_data?.checked as boolean | undefined;
  const description = content.token_data?.description as string | undefined;

  return (
    <button
      onClick={onClick}
      className={`
        flex items-center gap-2 px-2 py-1 rounded
        ${SERVO_BG_CLASSES.sage}
        ${SERVO_BORDER_CLASSES.sage}
        border transition-all duration-200
        hover:scale-[1.02]
        ${isSelected ? 'ring-2 ring-emerald-500/50' : ''}
      `}
    >
      <span className="text-lg">{checked ? '✅' : '⬜'}</span>
      <span className={`text-sm ${checked ? 'line-through text-gray-400' : 'text-gray-200'}`}>
        {description ?? content.source_text}
      </span>
    </button>
  );
}

interface ImageEmbedProps {
  content: MeaningTokenContent;
  isSelected: boolean;
  onClick?: () => void;
}

function ImageEmbed({ content, isSelected, onClick }: ImageEmbedProps) {
  const src = content.token_data?.src as string | undefined;
  const altText = content.token_data?.alt_text as string | undefined;

  return (
    <button
      onClick={onClick}
      className={`
        relative block rounded overflow-hidden
        border-2 ${SERVO_BORDER_CLASSES.copper}
        transition-all duration-200
        hover:scale-[1.02]
        ${isSelected ? 'ring-2 ring-amber-500/50' : ''}
      `}
    >
      {src ? (
        <img
          src={src}
          alt={altText ?? 'Image'}
          className="max-w-full h-auto max-h-32 object-cover"
        />
      ) : (
        <div className="flex items-center justify-center w-32 h-20 bg-gray-800">
          <span className="text-2xl">🖼️</span>
        </div>
      )}
      {altText && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-xs text-gray-200 px-2 py-1">
          {altText}
        </div>
      )}
    </button>
  );
}

interface CodeRegionProps {
  content: MeaningTokenContent;
  isSelected: boolean;
  onClick?: () => void;
}

function CodeRegion({ content, isSelected, onClick }: CodeRegionProps) {
  const language = content.token_data?.language as string | undefined;
  const code = content.token_data?.code as string | undefined;

  // Truncate long code blocks for preview
  const preview = code?.slice(0, 200) ?? content.source_text.slice(0, 200);
  const isTruncated = (code?.length ?? 0) > 200;

  return (
    <button
      onClick={onClick}
      className={`
        block w-full text-left rounded
        ${SERVO_BG_CLASSES.soil}
        border ${SERVO_BORDER_CLASSES.soil}
        transition-all duration-200
        hover:border-amber-600/70
        ${isSelected ? 'ring-2 ring-amber-500/50' : ''}
      `}
    >
      <div className="flex items-center gap-2 px-3 py-1 border-b border-stone-700/50">
        <span className="text-xs text-amber-400 font-mono">{language || 'code'}</span>
        <span className="flex-1" />
        <span className="text-xs text-gray-500">double-click to run</span>
      </div>
      <pre className="px-3 py-2 text-xs font-mono text-gray-300 overflow-hidden">
        {preview}
        {isTruncated && <span className="text-gray-500">...</span>}
      </pre>
    </button>
  );
}

interface BadgeTokenProps {
  content: MeaningTokenContent;
  kind: 'PRINCIPLE_ANCHOR' | 'REQUIREMENT_TRACE';
  isSelected: boolean;
  onClick?: () => void;
}

function BadgeToken({ content, kind, isSelected, onClick }: BadgeTokenProps) {
  const isPrinciple = kind === 'PRINCIPLE_ANCHOR';
  const number = isPrinciple
    ? (content.token_data?.principle_number as number | undefined)
    : (content.token_data?.requirement_id as string | undefined);

  const bgClass = isPrinciple ? 'bg-amber-700/70' : 'bg-purple-800/70';
  const borderClass = isPrinciple ? 'border-amber-600/50' : 'border-purple-600/50';
  const icon = isPrinciple ? '📜' : '📋';
  const prefix = isPrinciple ? 'P' : 'R';

  return (
    <button
      onClick={onClick}
      className={`
        inline-flex items-center gap-1 px-2 py-0.5 rounded-full
        text-xs font-medium
        ${bgClass} ${borderClass} border
        transition-all duration-200
        hover:scale-105
        ${isSelected ? 'ring-2 ring-white/30' : ''}
      `}
    >
      <span>{icon}</span>
      <span>
        [{prefix}
        {number ?? '?'}]
      </span>
    </button>
  );
}

interface PlainTextProps {
  content: string;
}

function PlainText({ content }: PlainTextProps) {
  return <span className="text-gray-200">{content}</span>;
}

// =============================================================================
// Main Component
// =============================================================================

export function MeaningTokenRenderer({
  kind,
  content,
  label: _label, // Used for future accessibility features
  isSelected = false,
  onClick,
  onHover,
  className = '',
}: MeaningTokenRendererProps) {
  void _label; // Silence unused warning

  // Handler wrappers - must be called unconditionally (React hooks rules)
  const handleClick = useCallback(() => {
    onClick?.();
  }, [onClick]);

  const handleMouseEnter = useCallback(() => {
    onHover?.(true);
  }, [onHover]);

  const handleMouseLeave = useCallback(() => {
    onHover?.(false);
  }, [onHover]);

  // Handle plain text (string content)
  if (typeof content === 'string') {
    return (
      <div className={className}>
        <PlainText content={content} />
      </div>
    );
  }

  // Render based on kind
  let rendered: React.ReactNode;

  switch (kind) {
    case 'AGENTESE_PORTAL':
      rendered = <AGENTESEPortal content={content} isSelected={isSelected} onClick={handleClick} />;
      break;

    case 'TASK_TOGGLE':
      rendered = <TaskToggle content={content} isSelected={isSelected} onClick={handleClick} />;
      break;

    case 'IMAGE_EMBED':
      rendered = <ImageEmbed content={content} isSelected={isSelected} onClick={handleClick} />;
      break;

    case 'CODE_REGION':
      rendered = <CodeRegion content={content} isSelected={isSelected} onClick={handleClick} />;
      break;

    case 'PRINCIPLE_ANCHOR':
    case 'REQUIREMENT_TRACE':
      rendered = (
        <BadgeToken content={content} kind={kind} isSelected={isSelected} onClick={handleClick} />
      );
      break;

    case 'PLAIN_TEXT':
    default:
      rendered = <PlainText content={content.source_text} />;
  }

  return (
    <div
      className={`inline ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {rendered}
    </div>
  );
}

MeaningTokenRenderer.displayName = 'MeaningTokenRenderer';

// =============================================================================
// Exports
// =============================================================================

export { AGENTESEPortal, TaskToggle, ImageEmbed, CodeRegion, BadgeToken, PlainText };
