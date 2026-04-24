export default function ConfidenceRing({ value = 0, size = 90 }) {
  const p = Math.max(0, Math.min(1, value))
  const pct = Math.round(p * 100)
  return (
    <div className="confidence-ring" style={{ '--size': `${size}px`, '--p': p }}>
      <span className="confidence-ring-val">{pct}%</span>
    </div>
  )
}
