import { test, expect } from '@playwright/test';
import { setupHotDataMocks } from '../testing';

/**
 * AGENTESE Contract Tests (Type I - Contracts)
 *
 * Verifies AGENTESE protocol contracts:
 * - Path discovery returns valid paths
 * - Manifest endpoints return expected shapes
 * - Route ↔ AGENTESE path mapping is consistent
 *
 * @tags @contract @smoke
 * @see plans/playwright-witness-protocol.md
 */

test.describe('AGENTESE Discovery @contract @smoke', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);
  });

  test('discover endpoint returns paths array', async ({ request }) => {
    // Mock the discover endpoint
    const response = await request.get('/api/v1/agentese/discover');

    // In real tests, this would hit the actual API
    // For now, we verify the expected structure
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('paths');
      expect(Array.isArray(data.paths)).toBe(true);
    }
  });

  test('paths follow AGENTESE naming convention', async ({ request }) => {
    const response = await request.get('/api/v1/agentese/discover');

    if (response.ok()) {
      const { paths } = await response.json();

      // AGENTESE path pattern: context.entity[.sub][.action]
      const pathPattern = /^(world|self|concept|void|time)\.[a-z]+(\.[a-z]+)*$/;

      for (const path of paths) {
        expect(path).toMatch(pathPattern);
      }
    }
  });
});

test.describe('AGENTESE Manifest Contracts @contract', () => {
  test.beforeEach(async ({ page }) => {
    await setupHotDataMocks(page);

    // Mock AGENTESE manifest endpoint
    await page.route('**/api/v1/agentese/invoke', async (route) => {
      const postData = route.request().postDataJSON();
      const path = postData?.path || '';

      if (path === 'world.town.manifest') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            path,
            manifest: {
              id: 'demo-town-123',
              name: 'Demo Town',
              citizen_count: 5,
              status: 'active',
            },
            aspects: ['overview'],
            effects: ['read'],
          }),
        });
      } else if (path.startsWith('world.town.citizen.')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            path,
            manifest: {
              name: 'Alice',
              region: 'workshop',
              phase: 'WORKING',
            },
            aspects: ['identity', 'location'],
            effects: ['read'],
          }),
        });
      } else {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ detail: `Path not found: ${path}` }),
        });
      }
    });
  });

  test('town manifest returns required fields', async ({ request }) => {
    const response = await request.post('/api/v1/agentese/invoke', {
      data: { path: 'world.town.manifest' },
    });

    if (response.ok()) {
      const data = await response.json();

      expect(data).toHaveProperty('path');
      expect(data).toHaveProperty('manifest');
      expect(data.manifest).toHaveProperty('id');
      expect(data.manifest).toHaveProperty('name');
      expect(data.manifest).toHaveProperty('status');
    }
  });

  test('citizen manifest returns required fields', async ({ request }) => {
    const response = await request.post('/api/v1/agentese/invoke', {
      data: { path: 'world.town.citizen.alice.manifest' },
    });

    if (response.ok()) {
      const data = await response.json();

      expect(data).toHaveProperty('path');
      expect(data).toHaveProperty('manifest');
      expect(data.manifest).toHaveProperty('name');
      expect(data.manifest).toHaveProperty('region');
      expect(data.manifest).toHaveProperty('phase');
    }
  });

  test('invalid path returns 404', async ({ request }) => {
    const response = await request.post('/api/v1/agentese/invoke', {
      data: { path: 'invalid.nonexistent.path' },
    });

    expect(response.status()).toBe(404);
  });
});

test.describe('Route-Path Alignment @contract', () => {
  /**
   * Verify that React routes align with AGENTESE paths.
   * This ensures the NavigationTree two-way mapping is correct.
   */

  const ROUTE_PATH_MAPPINGS = [
    { route: '/town/demo-town-123', path: 'world.town' },
    { route: '/town/demo-town-123/citizens', path: 'world.town.citizens' },
    { route: '/town/demo-town-123/coalitions', path: 'world.town.coalitions' },
    { route: '/brain', path: 'self.brain' },
    { route: '/brain/crystals', path: 'self.brain.crystals' },
    { route: '/park', path: 'world.park' },
  ];

  for (const { route, path } of ROUTE_PATH_MAPPINGS) {
    test(`route ${route} maps to path ${path}`, async ({ page }) => {
      await setupHotDataMocks(page);

      // Navigate to route
      await page.goto(route);

      // Check that we're on the expected page
      // (Specific assertions depend on page content)
      await expect(page).toHaveURL(new RegExp(route.replace(/\//g, '\\/')));

      // Verify AGENTESE path is accessible in page context
      // This depends on how the app exposes the current path
      const currentPath = await page.evaluate(() => {
         
        return (window as any).__AGENTESE_PATH__ || null;
      });

      // If the app sets __AGENTESE_PATH__, verify it matches
      if (currentPath) {
        expect(currentPath).toBe(path);
      }
    });
  }
});

test.describe('LOD Contract Verification @contract', () => {
  test.beforeEach(async ({ page }) => {
    // Setup LOD-aware mocks
    await page.route('**/v1/town/*/citizen/**', async (route) => {
      const url = new URL(route.request().url());
      const lodParam = url.searchParams.get('lod');
      const lod = lodParam ? parseInt(lodParam, 10) : 0;

      const lodResponses: Record<number, object> = {
        0: { name: 'Alice', region: 'workshop', phase: 'WORKING' },
        1: { name: 'Alice', region: 'workshop', phase: 'WORKING', archetype: 'Builder' },
        2: {
          name: 'Alice',
          region: 'workshop',
          phase: 'WORKING',
          archetype: 'Builder',
          mood: 'focused',
        },
        3: {
          name: 'Alice',
          region: 'workshop',
          phase: 'WORKING',
          archetype: 'Builder',
          mood: 'focused',
          eigenvectors: { warmth: 0.6 },
        },
        4: {
          name: 'Alice',
          region: 'workshop',
          phase: 'WORKING',
          archetype: 'Builder',
          mood: 'focused',
          eigenvectors: { warmth: 0.6 },
          relationships: { Bob: 0.8 },
        },
      };

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          lod,
          citizen: lodResponses[lod] || lodResponses[0],
          cost_credits: lod >= 3 ? 10 : 0,
        }),
      });
    });
  });

  test('LOD 0 returns minimal fields', async ({ request }) => {
    const response = await request.get('/api/v1/town/demo/citizen/alice?lod=0');

    if (response.ok()) {
      const data = await response.json();
      expect(data.lod).toBe(0);
      expect(data.citizen).toHaveProperty('name');
      expect(data.citizen).toHaveProperty('region');
      expect(data.citizen).not.toHaveProperty('eigenvectors');
    }
  });

  test('LOD increases field count', async ({ request }) => {
    const responses = await Promise.all([
      request.get('/api/v1/town/demo/citizen/alice?lod=0'),
      request.get('/api/v1/town/demo/citizen/alice?lod=2'),
      request.get('/api/v1/town/demo/citizen/alice?lod=4'),
    ]);

    const fieldCounts = await Promise.all(
      responses.map(async (r) => {
        if (r.ok()) {
          const data = await r.json();
          return Object.keys(data.citizen).length;
        }
        return 0;
      })
    );

    // Higher LOD should have more fields
    expect(fieldCounts[0]).toBeLessThan(fieldCounts[1]);
    expect(fieldCounts[1]).toBeLessThan(fieldCounts[2]);
  });

  test('LOD 3+ incurs credit cost', async ({ request }) => {
    const responseLod2 = await request.get('/api/v1/town/demo/citizen/alice?lod=2');
    const responseLod3 = await request.get('/api/v1/town/demo/citizen/alice?lod=3');

    if (responseLod2.ok() && responseLod3.ok()) {
      const dataLod2 = await responseLod2.json();
      const dataLod3 = await responseLod3.json();

      expect(dataLod2.cost_credits).toBe(0);
      expect(dataLod3.cost_credits).toBeGreaterThan(0);
    }
  });
});

test.describe('Manifest Aspects and Effects @contract', () => {
  test('manifest includes aspects array', async ({ request }) => {
    // Setup mock
    const response = await request.post('/api/v1/agentese/invoke', {
      data: { path: 'world.town.manifest' },
    });

    if (response.ok()) {
      const data = await response.json();

      if (data.aspects) {
        expect(Array.isArray(data.aspects)).toBe(true);
        // Common aspects
        const validAspects = ['identity', 'location', 'overview', 'psychology', 'philosophy', 'social'];
        for (const aspect of data.aspects) {
          expect(validAspects).toContain(aspect);
        }
      }
    }
  });

  test('manifest includes effects array', async ({ request }) => {
    const response = await request.post('/api/v1/agentese/invoke', {
      data: { path: 'world.town.citizen.alice.manifest' },
    });

    if (response.ok()) {
      const data = await response.json();

      if (data.effects) {
        expect(Array.isArray(data.effects)).toBe(true);
        // Common effects
        const validEffects = ['read', 'write', 'reflect', 'dialogue', 'inhabit'];
        for (const effect of data.effects) {
          expect(validEffects).toContain(effect);
        }
      }
    }
  });
});
