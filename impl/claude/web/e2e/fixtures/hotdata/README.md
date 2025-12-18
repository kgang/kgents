# HotData Fixtures (AD-004)

Pre-computed fixtures for deterministic E2E testing. Tests never call the LLM at runtime.

## Purpose

These fixtures provide:
- **Deterministic data** - Same data every test run
- **Fast tests** - No LLM API calls
- **Reproducible failures** - Consistent state for debugging
- **Offline testing** - Works without backend services

## Files

| File | Description |
|------|-------------|
| `citizens.json` | Pre-generated citizen data with all LOD levels |
| `dialogue.json` | Pre-generated dialogue turns between citizens |
| `manifests.json` | AGENTESE manifest responses at various LODs |

## Usage

### In TypeScript tests

```typescript
import { hotdata, setupHotDataMocks } from '../../testing';

test.beforeEach(async ({ page }) => {
  await setupHotDataMocks(page);
});

test('citizen browser shows all citizens', async ({ page }) => {
  await page.goto('/town/demo-town-123');

  // Uses HotData fixtures - no network calls
  for (const citizen of hotdata.citizens) {
    await expect(page.getByText(citizen.name)).toBeVisible();
  }
});
```

### Direct JSON import

```typescript
import citizensData from './hotdata/citizens.json';
import dialogueData from './hotdata/dialogue.json';

const citizens = citizensData.citizens;
const dialogues = dialogueData.dialogues;
```

## Regeneration

To regenerate fixtures (requires backend running):

```bash
# From impl/claude/web
npm run generate-fixtures
```

Or manually:

```bash
# Generate new citizen data
curl http://localhost:8000/v1/town/demo/citizens > e2e/fixtures/hotdata/citizens.json

# Format JSON
npx prettier --write e2e/fixtures/hotdata/*.json
```

## Schema

### Citizen

```typescript
interface HotCitizen {
  id: string;
  name: string;
  archetype: string;
  region: string;
  phase: string;
  is_evolving: boolean;
  mood?: string;
  cosmotechnics?: string;
  metaphor?: string;
  eigenvectors?: Record<string, number>;
  relationships?: Record<string, number>;
}
```

### Dialogue

```typescript
interface HotDialogue {
  id: string;
  participants: string[];
  turns: Array<{
    speaker: string;
    content: string;
    timestamp: number;
    emotion?: string;
  }>;
  topic: string;
  outcome?: string;
}
```

### Manifest

```typescript
interface HotManifest {
  path: string;
  lod: number;
  content: object;
  aspects: string[];
  effects: string[];
}
```

## Versioning

Each fixture file includes metadata:

```json
{
  "metadata": {
    "generated_at": "2025-12-18T00:00:00Z",
    "version": "1.0.0",
    "seed": 42,
    "description": "..."
  }
}
```

Update `version` when making breaking changes to fixture structure.

## Best Practices

1. **Never modify fixtures during tests** - Treat as read-only
2. **Use consistent seeds** - Same seed = same generated content
3. **Document fixture purpose** - What scenario does this test?
4. **Keep fixtures minimal** - Only include necessary data
5. **Validate fixture schema** - CI should catch malformed JSON

## Related

- `plans/playwright-witness-protocol.md` - Testing strategy
- `testing/hotdata.ts` - TypeScript API for fixtures
- `docs/skills/test-patterns.md` - T-gent testing patterns
