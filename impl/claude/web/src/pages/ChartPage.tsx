/**
 * ChartPage — Astronomical visualization (placeholder)
 *
 * Note: The old Spec Ledger visualization has been removed.
 * The Document Director (/director) is the canonical documents view.
 *
 * Future: This page will show astronomical constellation charts.
 */

export function ChartPage() {
  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--color-steel-950)',
        color: 'var(--color-steel-200)',
        flexDirection: 'column',
        gap: '1rem',
        padding: '2rem',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '3rem' }}>✦</div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600, margin: 0 }}>Chart View</h1>
      <p style={{ maxWidth: '600px', opacity: 0.7, margin: 0 }}>
        The old Spec Ledger visualization has been removed. Use the <strong>Documents</strong> tab (Shift+D) to
        view and manage documents.
      </p>
      <p style={{ fontSize: '0.875rem', opacity: 0.5, margin: 0 }}>
        Future: Astronomical constellation charts will appear here.
      </p>
    </div>
  );
}

export default ChartPage;
