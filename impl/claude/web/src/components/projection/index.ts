/**
 * Projection Component Library
 *
 * Unified rendering components for AGENTESE responses.
 * Provides consistent UI across CLI, Web, and marimo surfaces.
 */

// Status chrome (Error, Refusal, Cache)
export { ErrorPanel } from './ErrorPanel';
export { RefusalPanel } from './RefusalPanel';
export { CachedBadge } from './CachedBadge';

// Widget vocabulary
export { TextWidget } from './TextWidget';
export type { TextVariant, TextWidgetProps } from './TextWidget';

export { SelectWidget } from './SelectWidget';
export type { SelectOption, SelectWidgetProps } from './SelectWidget';

export { ConfirmWidget } from './ConfirmWidget';
export type { ConfirmWidgetProps } from './ConfirmWidget';

export { ProgressWidget } from './ProgressWidget';
export type { ProgressVariant, ProgressStep, ProgressWidgetProps } from './ProgressWidget';

export { TableWidget } from './TableWidget';
export type { TableColumn, TableWidgetProps } from './TableWidget';

export { GraphWidget } from './GraphWidget';
export type { GraphType, GraphDataset, GraphWidgetProps } from './GraphWidget';

export { StreamWidget } from './StreamWidget';
export type { StreamWidgetProps } from './StreamWidget';

// Re-export types from schema for convenience
export type {
  WidgetStatus,
  CacheMeta,
  ErrorInfo,
  RefusalInfo,
  StreamMeta,
  WidgetMeta,
  WidgetEnvelope,
  ErrorCategory,
} from '../../reactive/schema';

export { WidgetMetaFactory } from '../../reactive/schema';

// Gallery components (moved from components/gallery/)
export {
  PilotCard,
  CategoryFilter,
  OverrideControls,
  ProjectionView,
} from './gallery';
