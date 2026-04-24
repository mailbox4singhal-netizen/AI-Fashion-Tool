import { useEffect, useState } from 'react'
import { useLocation, useParams, Link } from 'react-router-dom'
import { api, downloadAuthed } from '../api.js'
import ConfidenceRing from '../components/ConfidenceRing.jsx'
import Swatch from '../components/Swatch.jsx'
import DesignCard from '../components/DesignCard.jsx'

export default function Results() {
  const { id } = useParams()
  const location = useLocation()
  const [data, setData] = useState(location.state?.initial || null)
  const [err, setErr] = useState(null)
  const [modifiedDesigns, setModifiedDesigns] = useState([])

  useEffect(() => {
    if (data) return
    api.results(id).then(setData).catch((e) => setErr(e.message))
  }, [id])

  if (err) return <div className="container"><div className="alert alert-warn">⚠ {err}</div></div>
  if (!data) return (
    <div className="container center" style={{ paddingTop: '6rem' }}>
      <div className="spinner" style={{ margin: '0 auto' }} />
      <p className="text-dim" style={{ marginTop: 16 }}>Running orchestrator…</p>
    </div>
  )

  const allDesigns = [...(data.designs || []), ...modifiedDesigns]

  return (
    <div className="container stack-lg">
      {/* Header */}
      <div className="glass glass-hi padded slide-up">
        <div className="row-between">
          <div>
            <div className="eyebrow">Request · {id.slice(0, 8)}</div>
            <h1 style={{ marginTop: 6 }}>
              <span className="gradient-text">{data.prompt}</span>
            </h1>
            <div className="row" style={{ marginTop: 10 }}>
              <span className="pill pill-pink">🌍 {data.region}</span>
              <span className="pill pill-violet">Status · {data.status}</span>
              <span className="pill pill-neon">Orchestrator v1.0</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ textAlign: 'right' }}>
              <div className="eyebrow" style={{ color: 'var(--pink)' }}>AI Confidence</div>
              <div className="text-xs text-dim">aggregate across all 4 modules</div>
            </div>
            <ConfidenceRing value={data.confidence} />
          </div>
        </div>
        {data.fallback && (
          <div className="alert alert-warn" style={{ marginTop: 16 }}>
            ⚠ <b>Low confidence.</b> {data.fallback}
          </div>
        )}
        {data.explanation && (
          <p className="text-dim text-sm" style={{ marginTop: 14 }}>
            <b className="text-neon">Why these results —</b> {data.explanation}
          </p>
        )}
      </div>

      {/* Trends */}
      <section className="stack">
        <div className="row-between">
          <div>
            <div className="eyebrow">F2 · Global Trend Intelligence</div>
            <h2>Trends for {data.region}</h2>
          </div>
        </div>
        <div className="grid grid-3">
          {data.trends.map((t, i) => (
            <div key={i} className="glass padded stack" style={{ animationDelay: `${i * 80}ms` }}>
              <span className="eyebrow">Trend #{i + 1}</span>
              <h3>{t.name}</h3>
              <p className="text-sm text-dim">{t.forecast}</p>
              <div className="row-between">
                <span className="text-xs text-mute">Predicted growth</span>
                <span className="trend-growth">+{Math.round(t.growth * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Colors */}
      <section className="stack">
        <div>
          <div className="eyebrow">F4 · Color Intelligence</div>
          <h2>Trend-aware palette</h2>
        </div>
        <div className="grid grid-4">
          {data.colors.map((c, i) => <Swatch key={i} {...c} />)}
        </div>
      </section>

      {/* Designs */}
      <section className="stack">
        <div className="row-between">
          <div>
            <div className="eyebrow">F5 · AI Design Studio</div>
            <h2>Design concepts</h2>
          </div>
          <span className="text-xs text-mute">Type a refinement to each card, e.g. "more formal"</span>
        </div>
        <div className="grid grid-3">
          {allDesigns.map((d, i) => (
            <DesignCard key={d.id || i} design={d}
                        onModified={(nd) => setModifiedDesigns((m) => [...m, nd])} />
          ))}
        </div>
      </section>

      {/* Tech pack */}
      {data.tech_pack && (
        <section className="glass padded stack slide-up">
          <div className="row-between">
            <div>
              <div className="eyebrow">F6 · Smart Tech Pack</div>
              <h2>{data.tech_pack.title}</h2>
              <div className="text-sm text-dim">Industry-standard, editable, exportable</div>
            </div>
            <button className="btn btn-neon"
              onClick={() => downloadAuthed(api.techpackExportUrl(id), `techpack_${id.slice(0,8)}.json`)}>
              ⬇ Export JSON
            </button>
          </div>
          <TechPack tp={data.tech_pack} />
        </section>
      )}

      <div className="center" style={{ paddingBottom: '2rem' }}>
        <Link to="/designer" className="btn btn-ghost">← Create another design</Link>
      </div>
    </div>
  )
}

function TechPack({ tp }) {
  return (
    <div>
      <div className="tp-row"><span className="tp-label">Category</span><span className="tp-val">{tp.category}</span></div>
      <div className="tp-row"><span className="tp-label">Fabric</span><span className="tp-val">{tp.fabric}</span></div>
      <div className="tp-row">
        <span className="tp-label">Colors</span>
        <span className="tp-val row" style={{ gap: '0.4rem' }}>
          {tp.colors.map((h, i) => (
            <span key={i} className="pill" style={{
              background: h, color: '#0a0a0f', border: 'none', fontWeight: 700
            }}>{h}</span>
          ))}
        </span>
      </div>
      <div className="tp-row">
        <span className="tp-label">Construction</span>
        <ul className="tp-val" style={{ paddingLeft: '1.2rem' }}>
          {tp.construction.map((c, i) => <li key={i}>{c}</li>)}
        </ul>
      </div>
      <div className="tp-row">
        <span className="tp-label">Trims</span>
        <ul className="tp-val" style={{ paddingLeft: '1.2rem' }}>
          {tp.trims.map((t, i) => <li key={i}>{t}</li>)}
        </ul>
      </div>
      <div className="tp-row">
        <span className="tp-label">Measurements</span>
        <div className="tp-val row" style={{ gap: '0.6rem' }}>
          {Object.entries(tp.measurements).map(([k, v]) => (
            <span key={k} className="pill pill-neon">{k} · {v}</span>
          ))}
        </div>
      </div>
      <div className="tp-row">
        <span className="tp-label">Care</span>
        <ul className="tp-val" style={{ paddingLeft: '1.2rem' }}>
          {tp.care.map((c, i) => <li key={i}>{c}</li>)}
        </ul>
      </div>
    </div>
  )
}
