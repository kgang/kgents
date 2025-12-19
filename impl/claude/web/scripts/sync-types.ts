#!/usr/bin/env npx tsx
/**
 * AGENTESE Contract Type Synchronization Script
 *
 * Fetches contract schemas from BE and generates TypeScript types.
 *
 * Usage:
 *   npx tsx scripts/sync-types.ts                    # Generate types
 *   npx tsx scripts/sync-types.ts --check            # Check for drift (CI mode)
 *   npx tsx scripts/sync-types.ts --url http://...   # Custom backend URL
 *
 * Phase 7: AGENTESE Contract Protocol (autopoietic-architecture.md)
 */

import * as fs from 'fs';
import * as path from 'path';

// === Configuration ===

const DEFAULT_BACKEND_URL = 'http://localhost:8000';
const DISCOVER_PATH = '/agentese/discover';
const OUTPUT_DIR = 'src/api/types/_generated';
const INDEX_FILE = 'index.ts';

// === Types ===

interface JsonSchemaProperty {
  type?: string;
  items?: JsonSchemaProperty;
  additionalProperties?: JsonSchemaProperty;
  properties?: Record<string, JsonSchemaProperty>;
  required?: string[];
  enum?: (string | number)[];
  oneOf?: JsonSchemaProperty[];
  nullable?: boolean;
  default?: unknown;
  description?: string;
  title?: string;
}

interface AspectSchema {
  request?: JsonSchemaProperty;
  response?: JsonSchemaProperty;
  error?: string;
}

interface DiscoveryResponse {
  paths: string[];
  stats: {
    registered_nodes: number;
    paths_with_contracts: number;
  };
  schemas?: Record<string, Record<string, AspectSchema>>;
  contract_coverage?: {
    paths_with_contracts: number;
    total_paths: number;
    coverage_pct: number;
  };
}

// === JSON Schema to TypeScript ===

function jsonSchemaToTypeScript(schema: JsonSchemaProperty, indent: number = 0): string {
  const pad = '  '.repeat(indent);

  // Handle nullable
  const nullable = schema.nullable ? ' | null' : '';

  // Handle enum
  if (schema.enum) {
    const enumValues = schema.enum
      .map((v) => (typeof v === 'string' ? `'${v}'` : String(v)))
      .join(' | ');
    return enumValues + nullable;
  }

  // Handle oneOf (union types)
  if (schema.oneOf) {
    const types = schema.oneOf.map((s) => jsonSchemaToTypeScript(s, indent));
    return types.join(' | ') + nullable;
  }

  // Handle by type
  switch (schema.type) {
    case 'string':
      return 'string' + nullable;

    case 'integer':
    case 'number':
      return 'number' + nullable;

    case 'boolean':
      return 'boolean' + nullable;

    case 'null':
      return 'null';

    case 'array':
      if (schema.items) {
        const itemType = jsonSchemaToTypeScript(schema.items, indent);
        return `${itemType}[]` + nullable;
      }
      return 'unknown[]' + nullable;

    case 'object':
      if (schema.properties) {
        const props = Object.entries(schema.properties)
          .map(([key, prop]) => {
            const required = schema.required?.includes(key);
            const propType = jsonSchemaToTypeScript(prop, indent + 1);
            const comment = prop.description ? `  /** ${prop.description} */\n${pad}` : '';
            return `${comment}  ${key}${required ? '' : '?'}: ${propType};`;
          })
          .join('\n' + pad);
        return `{\n${pad}${props}\n${pad}}` + nullable;
      }
      if (schema.additionalProperties) {
        const valueType = jsonSchemaToTypeScript(schema.additionalProperties, indent);
        return `Record<string, ${valueType}>` + nullable;
      }
      return 'Record<string, unknown>' + nullable;

    default:
      return 'unknown';
  }
}

function generateInterface(name: string, schema: JsonSchemaProperty): string {
  const description = schema.description ? `/**\n * ${schema.description}\n */\n` : '';

  if (schema.type !== 'object' || !schema.properties) {
    // Not an object, generate type alias
    const tsType = jsonSchemaToTypeScript(schema);
    return `${description}export type ${name} = ${tsType};\n`;
  }

  const properties = Object.entries(schema.properties)
    .map(([key, prop]) => {
      const required = schema.required?.includes(key);
      const propType = jsonSchemaToTypeScript(prop, 1);
      const comment = prop.description ? `  /** ${prop.description} */\n` : '';
      return `${comment}  ${key}${required ? '' : '?'}: ${propType};`;
    })
    .join('\n');

  return `${description}export interface ${name} {\n${properties}\n}\n`;
}

// === Path Processing ===

function pathToModuleName(agentesePath: string): string {
  // world.town -> WorldTown
  return agentesePath
    .split('.')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
}

function pathToFileName(agentesePath: string): string {
  // world.town -> world-town.ts
  return agentesePath.replace(/\./g, '-') + '.ts';
}

function aspectToTypeName(
  moduleName: string,
  aspect: string,
  kind: 'Request' | 'Response'
): string {
  // WorldTown + manifest + Response -> WorldTownManifestResponse
  const aspectName = aspect
    .split('.')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join('');
  return `${moduleName}${aspectName}${kind}`;
}

// === File Generation ===

/**
 * Global registry of generated type names to their owning path.
 * Used to detect and resolve collisions (child paths win).
 */
const generatedTypes = new Map<string, string>();

/**
 * Check if a child path should own a type over a parent path.
 *
 * The principle: "Child paths own their types."
 * - world.town.citizen.list → WorldTownCitizenListResponse (child owns)
 * - world.town.citizen.list → WorldTownCitizenListResponse (parent should NOT duplicate)
 *
 * A path P is a child of path Q if P starts with Q + "."
 */
function isChildPath(path: string, otherPath: string): boolean {
  return path.startsWith(otherPath + '.');
}

/**
 * Check if this path should claim a type name.
 *
 * Returns:
 * - 'claim': This path should generate the type
 * - 'skip': Another path already claimed it and should keep it
 * - 'replace': This path should claim it (it's more specific)
 */
function shouldClaimType(typeName: string, currentPath: string): 'claim' | 'skip' | 'replace' {
  const existingPath = generatedTypes.get(typeName);

  if (!existingPath) {
    return 'claim';
  }

  // If current path is a child of the existing path, current wins (more specific)
  if (isChildPath(currentPath, existingPath)) {
    return 'replace';
  }

  // If existing path is a child of current path, existing wins
  if (isChildPath(existingPath, currentPath)) {
    return 'skip';
  }

  // Unrelated paths with same type name - this shouldn't happen with proper
  // AGENTESE path design, but if it does, first one wins
  return 'skip';
}

function generatePathFile(
  agentesePath: string,
  aspects: Record<string, AspectSchema>
): { content: string; skippedTypes: string[] } {
  const moduleName = pathToModuleName(agentesePath);
  const lines: string[] = [
    `/**`,
    ` * Generated types for AGENTESE path: ${agentesePath}`,
    ` * DO NOT EDIT - regenerate with: npm run sync-types`,
    ` */`,
    ``,
  ];

  const skippedTypes: string[] = [];

  for (const [aspect, schema] of Object.entries(aspects)) {
    if (schema.error) {
      lines.push(`// Error generating ${aspect}: ${schema.error}`);
      continue;
    }

    if (schema.request) {
      const typeName = aspectToTypeName(moduleName, aspect, 'Request');
      const decision = shouldClaimType(typeName, agentesePath);

      if (decision === 'claim' || decision === 'replace') {
        generatedTypes.set(typeName, agentesePath);
        lines.push(generateInterface(typeName, schema.request));
      } else {
        skippedTypes.push(typeName);
        lines.push(`// ${typeName} defined in ${generatedTypes.get(typeName)}`);
      }
    }

    if (schema.response) {
      const typeName = aspectToTypeName(moduleName, aspect, 'Response');
      const decision = shouldClaimType(typeName, agentesePath);

      if (decision === 'claim' || decision === 'replace') {
        generatedTypes.set(typeName, agentesePath);
        lines.push(generateInterface(typeName, schema.response));
      } else {
        skippedTypes.push(typeName);
        lines.push(`// ${typeName} defined in ${generatedTypes.get(typeName)}`);
      }
    }
  }

  return { content: lines.join('\n'), skippedTypes };
}

function generateIndexFile(paths: string[]): string {
  const exports = paths
    .map((p) => {
      const fileName = pathToFileName(p).replace('.ts', '');
      return `export * from './${fileName}';`;
    })
    .join('\n');

  return [
    '/**',
    ' * Generated AGENTESE contract types index',
    ' * DO NOT EDIT - regenerate with: npm run sync-types',
    ' */',
    '',
    exports,
    '',
  ].join('\n');
}

// === Main ===

async function fetchDiscovery(backendUrl: string): Promise<DiscoveryResponse> {
  const url = `${backendUrl}${DISCOVER_PATH}?include_schemas=true`;
  console.log(`Fetching discovery from: ${url}`);

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch discovery: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

async function main() {
  const args = process.argv.slice(2);
  const checkMode = args.includes('--check');
  const urlIndex = args.indexOf('--url');
  const backendUrl = urlIndex >= 0 ? args[urlIndex + 1] : DEFAULT_BACKEND_URL;

  console.log('AGENTESE Contract Type Sync');
  console.log('===========================');
  console.log(`Backend: ${backendUrl}`);
  console.log(`Mode: ${checkMode ? 'Check (CI)' : 'Generate'}`);
  console.log('');

  // Fetch discovery
  let discovery: DiscoveryResponse;
  try {
    discovery = await fetchDiscovery(backendUrl);
  } catch (error) {
    console.error('Failed to connect to backend:', error);
    console.error('');
    console.error('Make sure the backend is running:');
    console.error(
      '  cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000'
    );
    process.exit(1);
  }

  // Check coverage
  const coverage = discovery.contract_coverage;
  if (coverage) {
    console.log(`Contract Coverage: ${coverage.coverage_pct}%`);
    console.log(`  Paths with contracts: ${coverage.paths_with_contracts}/${coverage.total_paths}`);
    console.log('');
  }

  // Check if any schemas
  const schemas = discovery.schemas || {};
  const pathsWithSchemas = Object.keys(schemas);

  if (pathsWithSchemas.length === 0) {
    console.log('No contracts found. Add contracts to @node decorators to generate types.');
    console.log('');
    console.log('Example:');
    console.log('  @node(');
    console.log('      "world.town",');
    console.log('      contracts={');
    console.log('          "manifest": Response(TownManifestResponse),');
    console.log('      }');
    console.log('  )');
    process.exit(0);
  }

  // Sort paths so child paths come FIRST (more specific paths claim types first)
  // This ensures world.town.citizen claims "WorldTownCitizenListResponse" before world.town tries
  const sortedPaths = pathsWithSchemas.sort((a, b) => {
    // Longer paths (more specific) come first
    if (a.length !== b.length) return b.length - a.length;
    // Alphabetical for same length
    return a.localeCompare(b);
  });

  console.log(`Found ${sortedPaths.length} paths with contracts:`);
  sortedPaths.forEach((p) => console.log(`  - ${p}`));
  console.log('');

  // Reset the global type registry for this run
  generatedTypes.clear();

  // Ensure output directory exists
  const outputPath = path.resolve(OUTPUT_DIR);
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
    console.log(`Created directory: ${outputPath}`);
  }

  // Generate files - process in sorted order (child paths first)
  const generatedFiles: string[] = [];
  let hasChanges = false;
  let totalSkipped = 0;

  for (const agentesePath of sortedPaths) {
    const aspects = schemas[agentesePath];
    const fileName = pathToFileName(agentesePath);
    const filePath = path.join(outputPath, fileName);
    const { content, skippedTypes } = generatePathFile(agentesePath, aspects);

    if (skippedTypes.length > 0) {
      totalSkipped += skippedTypes.length;
    }

    // Check for drift
    if (checkMode && fs.existsSync(filePath)) {
      const existing = fs.readFileSync(filePath, 'utf-8');
      if (existing !== content) {
        console.error(`DRIFT: ${fileName} has changed`);
        hasChanges = true;
      }
    }

    if (!checkMode) {
      fs.writeFileSync(filePath, content);
      const skipNote = skippedTypes.length > 0 ? ` (${skippedTypes.length} deduped)` : '';
      console.log(`Generated: ${fileName}${skipNote}`);
    }

    generatedFiles.push(agentesePath);
  }

  if (totalSkipped > 0 && !checkMode) {
    console.log(`\nDeduplicated ${totalSkipped} types (child paths own their types)`);
  }

  // Generate index file
  const indexPath = path.join(outputPath, INDEX_FILE);
  const indexContent = generateIndexFile(generatedFiles);

  if (checkMode && fs.existsSync(indexPath)) {
    const existing = fs.readFileSync(indexPath, 'utf-8');
    if (existing !== indexContent) {
      console.error(`DRIFT: ${INDEX_FILE} has changed`);
      hasChanges = true;
    }
  }

  if (!checkMode) {
    fs.writeFileSync(indexPath, indexContent);
    console.log(`Generated: ${INDEX_FILE}`);
  }

  console.log('');

  if (checkMode) {
    if (hasChanges) {
      console.error('Contract types are out of sync!');
      console.error('Run `npm run sync-types` to regenerate.');
      process.exit(1);
    } else {
      console.log('All contract types are in sync.');
    }
  } else {
    console.log('Done! Generated types are in:', OUTPUT_DIR);
    console.log('');
    console.log('Import in your code:');
    console.log(`  import { WorldTownManifestResponse } from '@/api/types/_generated';`);
  }
}

main().catch((error) => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
