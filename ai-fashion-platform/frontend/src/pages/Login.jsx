import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, setToken, setUser } from '../api.js'

const DEMO = {
  designer: { email: 'demo@fashion.ai',     password: 'demo1234' },
  shopper:  { email: 'shopper@fashion.ai',  password: 'shopper1234' },
  admin:    { email: 'admin@fashion.ai',    password: 'admin1234' },
}

export default function Login() {
  const [mode, setMode] = useState('login')           // 'login' | 'register'
  const [email, setEmail] = useState('demo@fashion.ai')
  const [password, setPassword] = useState('demo1234')
  const [name, setName] = useState('')
  const [role, setRole] = useState('designer')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const nav = useNavigate()
  const loc = useLocation()

  function pickDemo(r) {
    setEmail(DEMO[r].email)
    setPassword(DEMO[r].password)
    setError(null)
  }

  function postLoginDest(user) {
    // Respect "from" if the user was redirected to login from a protected page
    const from = loc.state?.from?.pathname
    if (from && from !== '/login') return from
    return user.role === 'shopper' ? '/browse' : '/designer'
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setError(null)
    try {
      const res = mode === 'login'
        ? await api.login(email, password)
        : await api.register(name || email.split('@')[0], email, password, role)
      setToken(res.access_token)
      setUser(res.user)
      nav(postLoginDest(res.user), { replace: true })
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="container" style={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}>
      <div className="glass glass-hi padded slide-up" style={{ width: 'min(520px, 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
          <div className="nav-logo" style={{ width: 52, height: 52, fontSize: '1.4rem' }}>F</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>
              Fashion<span className="text-neon">/AI</span>
            </div>
            <div className="text-xs text-mute">Global Intelligence · Design · Tech Pack</div>
          </div>
        </div>

        <div className="eyebrow">
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </div>
        <h1 className="gradient-text" style={{ marginTop: 8, marginBottom: 6 }}>
          {mode === 'login' ? 'Welcome back' : 'Join the platform'}
        </h1>
        <p className="text-dim text-sm mb-2">
          {mode === 'login'
            ? 'Sign in to access the AI design workspace.'
            : 'Your role decides what you can do — pick carefully.'}
        </p>

        <form onSubmit={submit} className="stack">
          {mode === 'register' && (
            <>
              <div className="field">
                <label>Full name</label>
                <input className="input" value={name}
                       onChange={(e) => setName(e.target.value)}
                       placeholder="e.g. Maya Rodriguez" />
              </div>
              <div className="field">
                <label>Role</label>
                <div className="row" style={{ gap: '.5rem' }}>
                  {[
                    { key: 'designer', desc: 'Create & refine designs' },
                    { key: 'shopper',  desc: 'Browse trends (read-only)' },
                    { key: 'admin',    desc: 'Full platform access' },
                  ].map(({ key, desc }) => (
                    <button
                      type="button"
                      key={key}
                      onClick={() => setRole(key)}
                      className={'glass padded-sm'}
                      style={{
                        flex: 1, minWidth: 130, cursor: 'pointer',
                        border: '1px solid ' + (role === key ? 'var(--neon)' : 'var(--glass-border)'),
                        background: role === key ? 'rgba(57,255,20,.08)' : 'var(--glass-bg)',
                        textAlign: 'left',
                      }}
                    >
                      <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        {key} {role === key && <span className="text-neon">✓</span>}
                      </div>
                      <div className="text-xs text-dim" style={{ marginTop: 4 }}>{desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          <div className="field">
            <label>Email</label>
            <input className="input" type="email" required autoComplete="username"
                   value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="field">
            <label>Password</label>
            <input className="input" type="password" required minLength={4}
                   autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                   value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          {error && <div className="alert alert-warn text-sm">⚠ {error}</div>}

          <button className="btn btn-primary" disabled={busy}>
            {busy ? 'Working…' : (mode === 'login' ? 'Sign in →' : 'Create account →')}
          </button>
        </form>

        {mode === 'login' && (
          <div style={{ marginTop: '1.4rem' }}>
            <div className="eyebrow" style={{ marginBottom: 8 }}>Try a demo account</div>
            <div className="row" style={{ gap: '.5rem' }}>
              <button onClick={() => pickDemo('designer')} className="pill pill-violet" style={{ cursor: 'pointer' }}>
                Designer
              </button>
              <button onClick={() => pickDemo('shopper')} className="pill pill-neon" style={{ cursor: 'pointer' }}>
                Shopper
              </button>
              <button onClick={() => pickDemo('admin')} className="pill pill-pink" style={{ cursor: 'pointer' }}>
                Admin
              </button>
            </div>
          </div>
        )}

        <div className="row-between" style={{ marginTop: '1.4rem' }}>
          <button className="btn btn-ghost text-sm" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
            {mode === 'login' ? 'Need an account? Register →' : '← Back to sign in'}
          </button>
        </div>
      </div>
    </div>
  )
}
