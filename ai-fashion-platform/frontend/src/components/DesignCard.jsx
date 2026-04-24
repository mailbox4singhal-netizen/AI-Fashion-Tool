import { useState } from 'react'
import { api, getUser } from '../api.js'

export default function DesignCard({ design, onModified }) {
  const user = getUser()
  const canModify = user && (user.role === 'designer' || user.role === 'admin')

  const [mod, setMod] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const palette = design.palette && design.palette.length
    ? design.palette
    : ['#FF1493', '#8A2BE2', '#39FF14']

  const gradient = `linear-gradient(135deg, ${palette.join(', ')})`

  async function modify(e) {
    e?.preventDefault()
    if (!mod.trim()) return
    setBusy(true); setError(null)
    try {
      const res = await api.modifyDesign(design.id, mod.trim())
      onModified?.(res)
      setMod('')
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="glass design-card slide-up">
      <div className="design-hero" style={{ background: gradient }} aria-hidden />
      <div>
        <h3 style={{ marginBottom: 6 }}>{design.title}</h3>
        <div className="text-sm text-dim">{design.summary}</div>
      </div>
      <div className="row" style={{ gap: '0.5rem' }}>
        <span className="pill pill-violet">{design.silhouette}</span>
        <span className="pill pill-neon">{design.fabric}</span>
      </div>

      {canModify ? (
        <form onSubmit={modify} className="row" style={{ gap: '0.5rem', marginTop: 'auto' }}>
          <input
            className="input"
            placeholder="Refine e.g. 'more formal' or 'pastel'"
            value={mod}
            onChange={(e) => setMod(e.target.value)}
            style={{ flex: 1, padding: '0.6rem 0.9rem' }}
          />
          <button className="btn btn-neon" disabled={busy || !mod.trim()}>
            {busy ? '…' : 'Modify'}
          </button>
        </form>
      ) : (
        <div className="text-xs text-mute" style={{ marginTop: 'auto' }}>
          Read-only view — sign in as a Designer to refine this design.
        </div>
      )}

      {error && <div className="text-xs" style={{ color: 'var(--pink)' }}>{error}</div>}
    </div>
  )
}
