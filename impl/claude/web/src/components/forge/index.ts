/**
 * Forge Components
 *
 * UI components for the Metaphysical Forge - where agents are built.
 * Theme: Clean, minimal, purposeful.
 *
 * Projection-First Pattern:
 * - ForgeVisualization: Main canvas (receives data from PathProjection)
 * - Individual components: Building blocks for the visualization
 */

// Main visualization (for projection-first pages)
export { ForgeVisualization } from './ForgeVisualization';
export type { ForgeVisualizationProps, ForgeStatusData } from './ForgeVisualization';

// Building blocks
export { ArtisanCard } from './ArtisanCard';
export { ArtisanGrid } from './ArtisanGrid';
export { CommissionForm } from './CommissionForm';
export { StreamingProgress } from './StreamingProgress';
export { PieceCard } from './PieceCard';
export { PieceDetail } from './PieceDetail';
export { GalleryGrid } from './GalleryGrid';
export { LineageTree } from './LineageTree';
export { CollaborationBuilder } from './CollaborationBuilder';
export { ErrorPanel } from './ErrorPanel';
export { LoadingPanel } from './LoadingPanel';

// K-gent Soul Presence (Phase 2: K-gent Integration)
export { SoulPresence, SoulIndicator } from './SoulPresence';

// Commission Workflow (Phase 2.5: Commission Workflow)
export { CommissionPanel } from './CommissionPanel';
