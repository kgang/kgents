/**
 * Document Director Components
 *
 * Full-lifecycle document management system.
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → Capture → Verify"
 */

export { DocumentDirector } from './DocumentDirector';
export { DirectorDashboard } from './DirectorDashboard';
export { DocumentTable } from './DocumentTable';
export { DocumentDetail } from './DocumentDetail';
export { DocumentStatusBadge } from './DocumentStatus';
export { PromptDialog } from './PromptDialog';

// New reusable components
export { DirectorStatusBadge } from './DirectorStatusBadge';
export type { DirectorStatusBadgeProps } from './DirectorStatusBadge';

export { AnalysisSummary } from './AnalysisSummary';
export type { AnalysisSummaryProps } from './AnalysisSummary';

export { CaptureDialog } from './CaptureDialog';
