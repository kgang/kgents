/**
 * Servo Components - SceneGraph → React Projection Layer
 *
 * These components render SceneGraph primitives (from warp_converters.py)
 * to React components using the existing Living Earth palette and
 * animation primitives.
 *
 * Design Philosophy (from WARP spec):
 *   "The webapp is not the UI. The webapp is the composition boundary."
 *
 * @see protocols/agentese/projection/scene.py - SceneGraph definition
 * @see protocols/agentese/projection/warp_converters.py - WARP → SceneGraph
 * @see components/genesis/BreathingContainer.tsx - Animation primitive
 */

export { ServoNodeRenderer, type ServoNodeRendererProps } from './ServoNodeRenderer';
export { ServoEdgeRenderer, type ServoEdgeRendererProps } from './ServoEdgeRenderer';
export { ServoSceneRenderer, type ServoSceneRendererProps } from './ServoSceneRenderer';
export { TraceNodeCard, type TraceNodeCardProps } from './TraceNodeCard';
export { WalkCard, type WalkCardProps } from './WalkCard';
export { LivingEarthTheme, SERVO_PALETTE } from './theme';
