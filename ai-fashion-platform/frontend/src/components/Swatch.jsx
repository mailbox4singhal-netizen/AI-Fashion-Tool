// Pure-luminance contrast pick for legibility on any swatch color.
function readable(hex) {
  const h = hex.replace('#', '')
  const r = parseInt(h.slice(0, 2), 16)
  const g = parseInt(h.slice(2, 4), 16)
  const b = parseInt(h.slice(4, 6), 16)
  const L = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return L > 0.6 ? '#0a0a0f' : '#ffffff'
}

export default function Swatch({ hex, name, weight }) {
  const txt = readable(hex)
  return (
    <div className="swatch" style={{ background: hex, color: txt }}>
      <div>
        <div className="swatch-name">{name}</div>
        <div className="swatch-hex">{hex.toUpperCase()}</div>
      </div>
      {weight != null && (
        <div className="text-xs" style={{ opacity: 0.85 }}>
          {Math.round(weight * 100)}% share
        </div>
      )}
    </div>
  )
}
