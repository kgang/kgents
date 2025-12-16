/**
 * Orchestration: Pipeline building and execution flow.
 *
 * Wraps the pipeline components with:
 * - Full-screen canvas mode
 * - Pre-built templates
 * - Execution monitoring
 * - Result visualization
 *
 * Flow: Enter Build Mode → Drag Agents → Connect Ports → Execute
 *
 * @see plans/web-refactor/user-flows.md
 */

export {
  OrchestrationCanvas,
  type OrchestrationCanvasProps,
} from './OrchestrationCanvas';

export {
  ExecutionMonitor,
  type ExecutionMonitorProps,
  type ExecutionStatus,
  type NodeExecution,
  type MonitorNodeInfo,
} from './ExecutionMonitor';

export {
  PipelineTemplates,
  type PipelineTemplatesProps,
  type PipelineTemplate,
} from './PipelineTemplates';
