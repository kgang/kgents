/**
 * ValueCompass Test Page
 *
 * Quick visual test of the ValueCompass primitive
 */

import { ValueCompassExample } from '@/primitives/ValueCompass/ValueCompassExample';

export function ValueCompassTestPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--surface-0)',
      padding: '2rem',
    }}>
      <ValueCompassExample />
    </div>
  );
}

export default ValueCompassTestPage;
