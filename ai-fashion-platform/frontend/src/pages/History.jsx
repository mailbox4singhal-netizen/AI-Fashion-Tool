import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function History() {
  const [rows, setRows] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    api.history().then(setRows).catch((e) => setErr(e.message))
  }, [])

  return (
    <div className="container stack-lg">
      <div className="slide-up">
        <div className="eyebrow">Your activity</div>
        <h1 className="gradient-text">Design history</h1>
      </div>

      {err && <div className="alert alert-warn">⚠ {err}</div>}

      {rows && rows.length === 0 && (
        <div className="glass padded center">
          <p className="text-dim">No designs yet.</p>
          <Link to="/designer" className="btn btn-primary" style={{ marginTop: 12 }}>Create one now</Link>
        </div>
      )}

      {rows && rows.length > 0 && (
        <div className="glass padded">
          <table className="table">
            <thead>
              <tr><th>When</th><th>Prompt</th><th>Region</th><th>Status</th><th></th></tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.request_id}>
                  <td className="mono text-dim">{new Date(r.created_at).toLocaleString()}</td>
                  <td>{r.prompt}</td>
                  <td><span className="pill pill-violet">{r.region}</span></td>
                  <td>
                    <span className={'pill ' + (r.status === 'complete' ? 'pill-neon' : 'pill-pink')}>
                      {r.status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Link to={`/results/${r.request_id}`} className="btn btn-ghost text-sm">View →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
