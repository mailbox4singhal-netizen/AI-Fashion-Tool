import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'

const TEMPLATES = [
  { label: 'Streetwear', prompt: 'urban streetwear capsule, oversized silhouettes' },
  { label: 'Ethnic',     prompt: 'festive ethnic wear with contemporary twist' },
  { label: 'Formal',     prompt: 'tailored formal business attire, modern cut' },
  { label: 'Athleisure', prompt: 'athflow layering for commuter lifestyle' },
  { label: 'Y2K',        prompt: 'Y2K nostalgia edit, low-rise, metallic accents' },
  { label: 'Sustainable',prompt: 'sustainable capsule using dead-stock and organic fabrics' },
]

export default function Designer() {
  const [prompt, setPrompt] = useState('summer festive wear')
  const [region, setRegion] = useState('India')
  const [category, setCategory] = useState('women')
  const [season, setSeason] = useState('SS25')
  const [imageUrl, setImageUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const nav = useNavigate()

  async function go(e) {
    e?.preventDefault()
    setBusy(true); setError(null)
    try {
      const res = await api.analyze({
        prompt, region, category, season,
        image_url: imageUrl || undefined,
      })
      nav(`/results/${res.request_id}`, { state: { initial: res } })
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="container stack-lg">
      <div className="slide-up">
        <div className="eyebrow">Design Studio · F5</div>
        <h1 className="gradient-text">Create a design</h1>
        <p className="text-dim">
          Upload inspiration or describe the brief — we'll return regional trends, a trend-aware palette,
          three design concepts, and a full tech pack. <span className="text-neon">Response under 5 seconds.</span>
        </p>
      </div>

      <div className="grid grid-2">
        <form onSubmit={go} className="glass padded stack">
          <div className="field">
            <label>Step 1 · Describe the design</label>
            <textarea className="textarea" value={prompt} rows={3}
                      onChange={(e) => setPrompt(e.target.value)} required
                      placeholder="e.g. 'summer festive wear, lightweight, modern silhouettes'" />
          </div>

          <div>
            <label className="text-xs text-dim" style={{
              textTransform: 'uppercase', letterSpacing: '0.15em', fontWeight: 600
            }}>
              or start from a template
            </label>
            <div className="row" style={{ marginTop: 6, gap: '0.4rem' }}>
              {TEMPLATES.map(t => (
                <button type="button" key={t.label}
                  className="pill pill-violet"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setPrompt(t.prompt)}>
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-3">
            <div className="field">
              <label>Region</label>
              <select className="select" value={region} onChange={(e) => setRegion(e.target.value)}>
                <option>India</option><option>Europe</option><option>USA</option>
                <option>Asia</option><option>Global</option>
              </select>
            </div>
            <div className="field">
              <label>Category</label>
              <select className="select" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option>women</option><option>men</option><option>kids</option><option>unisex</option>
              </select>
            </div>
            <div className="field">
              <label>Season</label>
              <select className="select" value={season} onChange={(e) => setSeason(e.target.value)}>
                <option>SS25</option><option>AW25</option><option>SS26</option><option>Resort</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label>Inspiration URL (optional)</label>
            <input className="input" placeholder="https://…" value={imageUrl}
                   onChange={(e) => setImageUrl(e.target.value)} />
          </div>

          {error && <div className="alert alert-warn text-sm">⚠ {error}</div>}

          <button className="btn btn-primary" disabled={busy} style={{ alignSelf: 'flex-start' }}>
            {busy ? (<><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}/> Analysing…</>)
                  : '✨ Generate'}
          </button>
        </form>

        <div className="glass padded stack">
          <div className="eyebrow">What happens next</div>
          <h2>The AI Orchestrator runs in parallel</h2>
          <p className="text-dim text-sm">
            The orchestrator layer fans out to four specialized engines simultaneously, aggregates
            their outputs with confidence scoring, and applies fallback logic if confidence
            falls below the configured threshold.
          </p>
          <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: '0.6rem' }}>
            {[
              ['🌍', 'Global Trend Intelligence', 'Region + seasonal forecast with growth signals'],
              ['🎨', 'Color Intelligence',        'Culturally tuned, trend-aware palette'],
              ['✏️', 'AI Design Studio',          '3 concept designs · refinable via prompts'],
              ['📋', 'Smart Tech Pack',           'Construction, trims, measurements, care'],
            ].map(([i, t, s]) => (
              <li key={t} className="trend-item">
                <div>
                  <div style={{ fontSize: '1.3rem' }}>{i}</div>
                  <div style={{ fontWeight: 600 }}>{t}</div>
                  <div className="text-xs text-dim">{s}</div>
                </div>
              </li>
            ))}
          </ul>
          <div className="text-xs text-mute">
            Every call is audit-logged with versioned prompts &amp; model version (FRS §F10).
          </div>
        </div>
      </div>
    </div>
  )
}
