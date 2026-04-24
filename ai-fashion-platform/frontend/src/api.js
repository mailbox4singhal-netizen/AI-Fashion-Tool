// Thin fetch wrapper — talks to FastAPI backend.
// In dev it goes through Vite's /api proxy to http://localhost:8000

const BASE = '/api'

function getToken() {
  return localStorage.getItem('token')
}
export function setToken(t) {
  if (t) localStorage.setItem('token', t)
  else   localStorage.removeItem('token')
}
export function getUser() {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
}
export function setUser(u) {
  if (u) localStorage.setItem('user', JSON.stringify(u))
  else   localStorage.removeItem('user')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const t = getToken()
    if (t) headers['Authorization'] = `Bearer ${t}`
  }
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try { const j = await res.json(); detail = j.detail || detail } catch {}
    throw new Error(detail)
  }
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return res.json()
  return res.text()
}

export const api = {
  login:    (email, password) => request('/auth/login', { method: 'POST', body: { email, password }, auth: false }),
  register: (name, email, password, role = 'designer') =>
              request('/auth/register', { method: 'POST', body: { name, email, password, role }, auth: false }),
  me:       () => request('/auth/me'),

  analyze:  (payload) => request('/analyze', { method: 'POST', body: payload }),
  results:  (id)      => request(`/results/${id}`),
  history:  ()        => request('/my/history'),

  modifyDesign: (baseId, modifier) =>
    request('/generate-design/modify', { method: 'POST', body: { base_design_id: baseId, modifier } }),

  techpack: (id) => request(`/generate-techpack/${id}`),
  techpackExportUrl: (id) =>
    `${BASE}/generate-techpack/${id}/export`,

  adminMetrics: () => request('/admin/metrics'),
  adminLogs:    () => request('/admin/audit-logs'),
  adminLogsExportUrl: () => `${BASE}/admin/audit-logs/export`,
}

/** Download a URL while preserving the bearer token. */
export async function downloadAuthed(url, filename) {
  const res = await fetch(url, { headers: { Authorization: `Bearer ${getToken()}` } })
  const blob = await res.blob()
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}
