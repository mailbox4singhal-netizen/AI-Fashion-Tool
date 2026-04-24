import { useEffect, useState } from 'react'
import { api, downloadAuthed } from '../api.js'

export default function Admin() {
  const [m, setM] = useState(null)
  const [logs, setLogs] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    Promise.all([api.adminMetrics(), api.adminLogs()])
      .then(([metrics, l]) => { setM(metrics); setLogs(l) })
      .catch((e) => setErr(e.message))
  }, [])

  if (err) return <div className="container"><div className="alert alert-warn">⚠ {err}</div></div>
  if (!m) return (
    <div className="container center" style={{ paddingTop: '4rem' }}>
      <div className="spinner" style={{ margin: '0 auto' }} />
    </div>
  )

  const regionMax = Math.max(1, ...Object.values(m.requests_by_region))
  const distMax   = Math.max(1, ...Object.values(m.confidence_distribution))

  return (
    <div className="container stack-lg">
      <div className="slide-up">
        <div className="eyebrow">F9 · Platform Intelligence</div>
        <h1 className="gradient-text">Admin dashboard</h1>
      </div>

      {/* Headline stats */}
      <div className="grid grid-4">
        <StatCard label="Total Requests" value={m.total_requests} />
        <StatCard label="Active Users"   value={m.total_users} />
        <StatCard label="Avg Confidence" value={(m.avg_confidence * 100).toFixed(1) + '%'} />
        <StatCard label="Error Rate"     value={(m.error_rate * 100).toFixed(1) + '%'} />
      </div>

      <div className="grid grid-2">
        {/* Region heatmap */}
        <div className="glass padded stack">
          <div className="eyebrow">Requests by region</div>
          <h3>Global activity</h3>
          <div className="stack">
            {Object.entries(m.requests_by_region).map(([region, count]) => (
              <div key={region}>
                <div className="row-between">
                  <span>{region}</span>
                  <span className="text-neon">{count}</span>
                </div>
                <div className="meter" style={{ marginTop: 6 }}>
                  <div className="meter-fill" style={{ width: `${(count / regionMax) * 100}%` }} />
                </div>
              </div>
            ))}
            {Object.keys(m.requests_by_region).length === 0 && (
              <p className="text-dim text-sm">No requests yet.</p>
            )}
          </div>
        </div>

        {/* Confidence distribution */}
        <div className="glass padded stack">
          <div className="eyebrow">Model health</div>
          <h3>Confidence distribution</h3>
          <div className="stack">
            {Object.entries(m.confidence_distribution).map(([bucket, count]) => (
              <div key={bucket}>
                <div className="row-between">
                  <span>{bucket}</span>
                  <span className="text-neon">{count}</span>
                </div>
                <div className="meter" style={{ marginTop: 6 }}>
                  <div className="meter-fill" style={{ width: `${(count / distMax) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top trends */}
      <div className="glass padded stack">
        <div className="row-between">
          <div>
            <div className="eyebrow">Trend popularity</div>
            <h3>Top 5 predicted trends across all requests</h3>
          </div>
        </div>
        {m.top_trends.length === 0 ? (
          <p className="text-dim text-sm">No trend data yet — run an analysis to populate.</p>
        ) : (
          <div className="grid grid-3">
            {m.top_trends.map((t) => (
              <div key={t.name} className="trend-item">
                <div>
                  <div style={{ fontWeight: 600 }}>{t.name}</div>
                  <div className="text-xs text-dim">{t.count} appearances</div>
                </div>
                <span className="pill pill-neon">{t.count}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Audit logs */}
      <div className="glass padded stack">
        <div className="row-between">
          <div>
            <div className="eyebrow">F10 · Audit trail</div>
            <h3>Recent AI calls</h3>
          </div>
          <button className="btn btn-neon"
            onClick={() => downloadAuthed(api.adminLogsExportUrl(), 'audit_logs.csv')}>
            ⬇ Export CSV
          </button>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>When</th><th>Request</th><th>Model</th><th>Prompt ver.</th><th>Conf.</th>
              </tr>
            </thead>
            <tbody>
              {logs?.slice(0, 20).map((row) => (
                <tr key={row.id}>
                  <td className="mono text-dim text-xs">{new Date(row.created_at).toLocaleString()}</td>
                  <td className="mono text-xs">{row.request_id?.slice(0, 8)}</td>
                  <td className="text-xs">{row.model_version}</td>
                  <td><span className="pill pill-violet text-xs">{row.prompt_version}</span></td>
                  <td className="text-neon">{(row.confidence * 100).toFixed(0)}%</td>
                </tr>
              ))}
              {(!logs || logs.length === 0) && (
                <tr><td colSpan={5} className="text-dim center">No audit entries yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="glass padded stat">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
