/**
 * Atelier Components
 *
 * UI components for Tiny Atelier - a demo app showcasing the kgents ecosystem.
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 *
 * Projection-First Pattern:
 * - AtelierVisualization: Main canvas (receives data from PathProjection)
 * - Individual components: Building blocks for the visualization
 */

// Main visualization (for projection-first pages)
export { AtelierVisualization } from './AtelierVisualization';
export type { AtelierVisualizationProps, AtelierStatusData } from './AtelierVisualization';

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

// Phase 2: FishbowlCanvas (Crown Jewels Genesis)
export { FishbowlCanvas } from './FishbowlCanvas';
export type { FishbowlCanvasProps, SpectatorCursor as FishbowlSpectatorCursor } from './FishbowlCanvas';
export { SpectatorOverlay, eigenvectorToColor, getColorForId } from './SpectatorOverlay';
export type { SpectatorOverlayProps, SpectatorCursor } from './SpectatorOverlay';

// Phase 2: BidQueue (Crown Jewels Genesis - Chunk 2)
export { BidQueuePanel } from './BidQueuePanel';
export type { BidQueuePanelProps, Bid, BidType, BidStatus } from './BidQueuePanel';
export { BidSubmitModal } from './BidSubmitModal';
export type { BidSubmitModalProps, NewBid } from './BidSubmitModal';

// Phase 2: Token Visualization (Crown Jewels Genesis - Chunk 3)
export { TokenBalanceWidget } from './TokenBalanceWidget';
export type { TokenBalanceWidgetProps } from './TokenBalanceWidget';
export { TokenFlowIndicator } from './TokenFlowIndicator';
export type { TokenFlowIndicatorProps, TokenFlowEvent } from './TokenFlowIndicator';
export { SpendHistoryPanel } from './SpendHistoryPanel';
export type { SpendHistoryPanelProps } from './SpendHistoryPanel';
