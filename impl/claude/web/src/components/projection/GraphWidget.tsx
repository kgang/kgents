/**
 * GraphWidget: Chart.js wrapper for data visualization.
 *
 * Supports chart types:
 * - line: Time series, trends
 * - bar: Categorical comparisons
 * - pie: Part-of-whole
 * - doughnut: Pie variant
 * - radar: Multi-dimensional comparisons
 *
 * Note: Requires chart.js and react-chartjs-2 dependencies.
 * For now, renders placeholder if Chart.js not available.
 */

export type GraphType = 'line' | 'bar' | 'pie' | 'doughnut' | 'radar';

export interface GraphDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string;
  fill?: boolean;
}

export interface GraphWidgetProps {
  type: GraphType;
  labels: string[];
  datasets: GraphDataset[];
  title?: string;
  stacked?: boolean;
  height?: number;
}

// Default color palette
const COLORS = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#84cc16', // lime
];

/**
 * Placeholder renderer for when Chart.js is not available.
 */
function PlaceholderChart({ type, labels, datasets, title }: GraphWidgetProps) {
  // Find max value for scaling
  const maxValue = Math.max(...datasets.flatMap((ds) => ds.data), 1);

  return (
    <div
      className="kgents-graph-placeholder"
      style={{
        padding: '16px',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        backgroundColor: '#f9fafb',
      }}
    >
      {title && (
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>{title}</h3>
      )}

      {type === 'bar' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {labels.map((label, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ width: '80px', fontSize: '12px', textAlign: 'right' }}>{label}</span>
              <div style={{ flex: 1, display: 'flex', gap: '2px' }}>
                {datasets.map((ds, j) => (
                  <div
                    key={j}
                    style={{
                      height: '24px',
                      width: `${(ds.data[i] / maxValue) * 100}%`,
                      backgroundColor: COLORS[j % COLORS.length],
                      borderRadius: '2px',
                    }}
                    title={`${ds.label}: ${ds.data[i]}`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {type === 'line' && (
        <div style={{ height: '150px', display: 'flex', alignItems: 'flex-end', gap: '4px' }}>
          {labels.map((label, i) => (
            <div
              key={i}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              {datasets.map((ds, j) => (
                <div
                  key={j}
                  style={{
                    width: '8px',
                    height: `${(ds.data[i] / maxValue) * 120}px`,
                    backgroundColor: COLORS[j % COLORS.length],
                    borderRadius: '4px 4px 0 0',
                  }}
                  title={`${ds.label}: ${ds.data[i]}`}
                />
              ))}
              <span style={{ fontSize: '10px', color: '#6b7280' }}>{label}</span>
            </div>
          ))}
        </div>
      )}

      {(type === 'pie' || type === 'doughnut') && (
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div
            style={{
              width: '100px',
              height: '100px',
              borderRadius: '50%',
              background: `conic-gradient(${labels
                .map((_, i) => {
                  const total = datasets[0]?.data.reduce((a, b) => a + b, 0) || 1;
                  const start =
                    datasets[0]?.data.slice(0, i).reduce((a, b) => a + b, 0) || 0;
                  const end = start + (datasets[0]?.data[i] || 0);
                  return `${COLORS[i % COLORS.length]} ${(start / total) * 100}% ${(end / total) * 100}%`;
                })
                .join(', ')})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {type === 'doughnut' && (
              <div
                style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  backgroundColor: 'white',
                }}
              />
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {labels.map((label, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    width: '12px',
                    height: '12px',
                    backgroundColor: COLORS[i % COLORS.length],
                    borderRadius: '2px',
                  }}
                />
                <span style={{ fontSize: '12px' }}>
                  {label}: {datasets[0]?.data[i]}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {type === 'radar' && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <span style={{ fontSize: '12px', color: '#6b7280' }}>[Radar chart placeholder]</span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
            {labels.map((label, i) => (
              <span
                key={i}
                style={{
                  fontSize: '11px',
                  padding: '2px 8px',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '4px',
                }}
              >
                {label}: {datasets[0]?.data[i]}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Legend */}
      {datasets.length > 1 && (
        <div
          style={{
            display: 'flex',
            gap: '16px',
            marginTop: '12px',
            justifyContent: 'center',
          }}
        >
          {datasets.map((ds, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div
                style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: COLORS[i % COLORS.length],
                  borderRadius: '2px',
                }}
              />
              <span style={{ fontSize: '12px' }}>{ds.label}</span>
            </div>
          ))}
        </div>
      )}

      <p
        style={{
          marginTop: '16px',
          fontSize: '11px',
          color: '#9ca3af',
          textAlign: 'center',
        }}
      >
        Install chart.js + react-chartjs-2 for interactive charts
      </p>
    </div>
  );
}

export function GraphWidget(props: GraphWidgetProps) {
  // Try to use Chart.js if available
  // For now, always use placeholder since we haven't confirmed Chart.js is installed
  // In production, this would dynamically import and use react-chartjs-2

  return <PlaceholderChart {...props} />;
}

export default GraphWidget;
