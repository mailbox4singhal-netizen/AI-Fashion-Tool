import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, getUser } from '../api.js'

export default function Browse() {
  const user = getUser()
  const [rows, setRows] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    // Shoppers and designers both land here — designers see their own
    // recent work, shoppers see it as a curated feed.
    api.history().then(setRows).catch((e) => setErr(e.message))
  }, [])

  return (
    <div className="container stack-lg">
      <div className="slide-up">
        <div className="eyebrow">Fashion intelligence feed</div>
        <h1 className="gradient-text">Browse trends &amp; designs</h1>
        {user?.role === 'shopper' ? (
          <p className="text-dim">
            You're signed in as a Shopper — this is a read-only feed of recent
            AI-generated collections. Want to create your own designs?{' '}
            <span className="text-neon">Ask your admin to upgrade your role to Designer.</span>
          </p>
        ) : (
          <p className="text-dim">Your most recent AI generations, grouped by request.</p>
        )}
      </div>

      {err && <div className="alert alert-warn">⚠ {err}</div>}

      {rows && rows.length === 0 && (
        <div className="glass padded center">
          <p className="text-dim">No designs yet.</p>
          {(user?.role === 'designer' || user?.role === 'admin') && (
            <Link to="/designer" className="btn btn-primary" style={{ marginTop: 12 }}>
              Create your first →
            </Link>
          )}
        </div>
      )}

      {rows && rows.length > 0 && (
        <div className="grid grid-2">
          {rows.map((r) => (
            <Link key={r.request_id} to={`/results/${r.request_id}`}
                  className="glass padded stack"
                  style={{ textDecoration: 'none', color: 'inherit', transition: 'all .2s ease' }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--pink)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--glass-border)'}
            >
              <div className="row-between">
                <span className="pill pill-violet">{r.region || 'Global'}</span>
                <span className={'pill ' + (r.status === 'complete' ? 'pill-neon' : 'pill-pink')}>
                  {r.status}
                </span>
              </div>
              <h3 style={{ marginTop: 4 }}>{r.prompt || 'Untitled brief'}</h3>
              <div className="text-xs text-mute">
                {new Date(r.created_at).toLocaleString()}
              </div>
              <div className="text-xs text-neon">View details →</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
