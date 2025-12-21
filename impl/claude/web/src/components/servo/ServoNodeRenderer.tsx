/**
 * ServoNodeRenderer - Renders any SceneNode to React
 *
 * This is the core projection layer that maps SceneNodeKind to React components.
 * Each kind has a dedicated component; unknown kinds fall back to a generic panel.
 *
 * Design Philosophy (from Constitution):
 *   Composable: ServoScene.compose() follows category laws
 *   Joy-Inducing: Breathing surfaces, organic unfurling
 *   Tasteful: 9 SceneNodeKinds, not kitchen-sink sprawl
 *
 * @see protocols/agentese/projection/scene.py - SceneGraph definition
 * @see protocols/agentese/projection/warp_converters.py - WARP → SceneGraph
 */

import React from 'react';
import { BreathingContainer } from '@/components/genesis/BreathingContainer';
import { TraceNodeCard, type TraceNodeContent } from './TraceNodeCard';
import { WalkCard, type WalkContent } from './WalkCard';
import {
  MeaningTokenRenderer,
  type MeaningTokenKind,
  type MeaningTokenContent,
} from './MeaningTokenRenderer';
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from './theme';

// =============================================================================
// Types (matching SceneNode from scene.py)
// =============================================================================

/** SceneNodeKind enum values (from Python) */
export type SceneNodeKind =
  | 'PANEL'
  | 'TRACE'
  | 'INTENT'
  | 'OFFERING'
  | 'COVENANT'
  | 'WALK'
  | 'RITUAL'
  | 'TEXT'
  | 'GROUP';

/** NodeStyle from Python (optional fields) */
export interface NodeStyle {
  background?: string;
  foreground?: string;
  border?: string;
  breathing?: boolean;
  unfurling?: boolean;
  paper_grain?: boolean;
  opacity?: number;
}

/** Interaction from Python */
export interface Interaction {
  kind: string;
  action: string;
  requires_trust: number;
  metadata?: Record<string, unknown>;
}

/** SceneNode from Python (serialized via to_dict()) */
export interface SceneNode {
  id: string;
  kind: SceneNodeKind;
  content: unknown;
  label: string;
  style: NodeStyle;
  flex: number;
  min_width: number | null;
  min_height: number | null;
  interactions: Interaction[];
  metadata: Record<string, unknown>;
}

export interface ServoNodeRendererProps {
  /** The SceneNode to render */
  node: SceneNode;
  /** Whether this node is selected */
  isSelected?: boolean;
  /** Click handler */
  onClick?: (node: SceneNode) => void;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Generic Fallback Components
// =============================================================================

interface GenericPanelProps {
  label: string;
  content: unknown;
  style: NodeStyle;
  isSelected: boolean;
  onClick?: () => void;
}

function GenericPanel({ label, content, style, isSelected, onClick }: GenericPanelProps) {
  const bgClass = style.background
    ? (SERVO_BG_CLASSES[style.background] ?? `bg-[${style.background}]`)
    : SERVO_BG_CLASSES.paper;

  return (
    <div
      className={`
        rounded-lg border-2 p-3
        ${bgClass}
        ${SERVO_BORDER_CLASSES[style.background ?? 'paper'] ?? 'border-gray-700/50'}
        ${isSelected ? 'ring-2 ring-white/50' : ''}
        ${onClick ? 'cursor-pointer hover:scale-[1.02]' : ''}
        transition-all duration-200
      `}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="font-medium text-sm text-white">{label}</div>
      {typeof content === 'string' && <div className="text-xs text-gray-300 mt-1">{content}</div>}
    </div>
  );
}

function TextNode({ label, content }: { label: string; content: unknown }) {
  const text = typeof content === 'string' ? content : JSON.stringify(content);
  return (
    <div className="text-sm text-gray-200">
      {label && <span className="font-medium">{label}: </span>}
      {text}
    </div>
  );
}

function GroupNode({ children }: { children: React.ReactNode }) {
  return <div className="flex flex-col gap-2">{children}</div>;
}

// =============================================================================
// Intent/Offering/Covenant/Ritual Components
// =============================================================================

interface BadgeNodeProps {
  label: string;
  kind: 'INTENT' | 'OFFERING' | 'COVENANT' | 'RITUAL';
  content: unknown;
  style: NodeStyle;
  onClick?: () => void;
}

function BadgeNode({ label, kind, content, onClick }: BadgeNodeProps) {
  const kindStyles: Record<string, string> = {
    INTENT: 'bg-amber-700/70 border-amber-600/50 text-amber-100',
    OFFERING: 'bg-yellow-600/70 border-yellow-500/50 text-yellow-100',
    COVENANT: 'bg-purple-800/70 border-purple-600/50 text-purple-100',
    RITUAL: 'bg-amber-800/70 border-amber-600/50 text-amber-100',
  };

  const kindIcons: Record<string, string> = {
    INTENT: '🎯',
    OFFERING: '🎁',
    COVENANT: '🤝',
    RITUAL: '🔮',
  };

  const metadata = typeof content === 'object' && content !== null ? content : {};

  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full
        border text-sm font-medium
        ${kindStyles[kind]}
        ${onClick ? 'cursor-pointer hover:scale-105' : ''}
        transition-all duration-200
      `}
      onClick={onClick}
    >
      <span>{kindIcons[kind]}</span>
      <span className="truncate max-w-[150px]">{label}</span>
      {kind === 'COVENANT' && 'trust_level' in (metadata as Record<string, unknown>) && (
        <span className="text-xs opacity-75">
          L{(metadata as Record<string, number>).trust_level}
        </span>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ServoNodeRenderer({
  node,
  isSelected = false,
  onClick,
  className = '',
}: ServoNodeRendererProps) {
  // Graceful degradation: handle missing/malformed node
  if (!node) {
    return <div className="p-2 text-gray-500 text-sm">[Empty node]</div>;
  }

  const kind = node.kind ?? 'PANEL';
  const content = node.content ?? {};
  const label = node.label ?? '';
  const style = node.style ?? {};
  const breathing = style?.breathing ?? false;

  // Handler wrapper
  const handleClick = onClick ? () => onClick(node) : undefined;

  // Render based on kind
  let rendered: React.ReactNode;

  switch (kind) {
    case 'TRACE':
      rendered = (
        <TraceNodeCard
          content={content as TraceNodeContent}
          label={label}
          breathing={breathing}
          isSelected={isSelected}
          onClick={handleClick}
          className={className}
        />
      );
      break;

    case 'WALK':
      rendered = (
        <WalkCard
          content={content as WalkContent}
          label={label}
          isSelected={isSelected}
          onClick={handleClick}
          className={className}
        />
      );
      break;

    case 'INTENT':
    case 'OFFERING':
    case 'COVENANT':
    case 'RITUAL':
      rendered = (
        <BadgeNode
          kind={kind}
          label={label}
          content={content}
          style={style}
          onClick={handleClick}
        />
      );
      break;

    case 'TEXT':
      // Check if this is a meaning token (has meaning_token_kind in metadata)
      if (node.metadata?.meaning_token_kind) {
        const tokenKind = node.metadata.meaning_token_kind as MeaningTokenKind;
        rendered = (
          <MeaningTokenRenderer
            kind={tokenKind}
            content={content as MeaningTokenContent | string}
            label={label}
            isSelected={isSelected}
            onClick={handleClick}
            className={className}
          />
        );
        break;
      }
      rendered = <TextNode label={label} content={content} />;
      break;

    case 'GROUP':
      rendered = <GroupNode>{label}</GroupNode>;
      break;

    case 'PANEL':
    default:
      rendered = (
        <GenericPanel
          label={label}
          content={content}
          style={style}
          isSelected={isSelected}
          onClick={handleClick}
        />
      );
  }

  // Wrap with breathing if needed and not already wrapped (TRACE/WALK handle their own)
  if (breathing && kind !== 'TRACE' && kind !== 'WALK') {
    return (
      <BreathingContainer intensity="subtle" className={className}>
        {rendered}
      </BreathingContainer>
    );
  }

  return <>{rendered}</>;
}

ServoNodeRenderer.displayName = 'ServoNodeRenderer';
