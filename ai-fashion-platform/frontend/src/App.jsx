import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Nav from './components/Nav.jsx'
import Login from './pages/Login.jsx'
import Designer from './pages/Designer.jsx'
import Results from './pages/Results.jsx'
import History from './pages/History.jsx'
import Admin from './pages/Admin.jsx'
import Browse from './pages/Browse.jsx'
import { getUser } from './api.js'

/** Role-aware landing page — designers/admins get the workspace,
 *  shoppers get the browse view. Unauth users bounce to /login. */
function RoleHome() {
  const user = getUser()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'shopper') return <Navigate to="/browse" replace />
  return <Navigate to="/designer" replace />
}

function Protected({ children, roles }) {
  const user = getUser()
  const loc = useLocation()
  if (!user) return <Navigate to="/login" replace state={{ from: loc }} />
  if (roles && !roles.includes(user.role)) {
    // Logged in but wrong role — send them to their allowed home.
    return <Navigate to="/" replace />
  }
  return children
}

export default function App() {
  const user = getUser()
  return (
    <>
      {user && <Nav />}
      <Routes>
        <Route path="/" element={<RoleHome />} />
        <Route path="/login" element={<Login />} />

        <Route path="/designer" element={
          <Protected roles={['designer', 'admin']}><Designer /></Protected>
        } />
        <Route path="/browse" element={
          <Protected><Browse /></Protected>
        } />
        <Route path="/results/:id" element={
          <Protected><Results /></Protected>
        } />
        <Route path="/history" element={
          <Protected><History /></Protected>
        } />
        <Route path="/admin" element={
          <Protected roles={['admin']}><Admin /></Protected>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}
