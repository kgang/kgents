/**
 * AGENTESE Router
 *
 * "The route is a lie. There is only the AGENTESE path and its projection."
 *
 * This module exports the radical AGENTESE URL Router that makes
 * URLs semantic AGENTESE invocations rather than traditional routes.
 */

export { AgenteseRouter, getPathMappings, isLegacyRoute, getLegacyRedirect } from './AgenteseRouter';

export {
  parseAgentesePath,
  toUrl,
  buildAgentesePath,
  composePaths,
  isAgentesePath,
  formatPathLabel,
  getEntityType,
  AgentesePathError,
  type AgentesePath,
  type AgenteseContext,
  type AspectCategory,
} from './AgentesePath';

export {
  useAgentesePath,
  useAgenteseNavigate,
  useNavigateTo,
  usePathMatch,
  useAgenteseParams,
  useCurrentAspect,
  useEntityId,
  useNavigateUp,
  useBreadcrumbs,
} from './useAgentesePath';
