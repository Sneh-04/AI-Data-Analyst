import React from 'react'
import { HashRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import { DatasetProvider } from './api/DatasetContext.jsx'
import Upload from './pages/Upload.jsx'
import Overview from './pages/Overview.jsx'
import Cleaning from './pages/Cleaning.jsx'
import Visualization from './pages/Visualization.jsx'
import Forecasting from './pages/Forecasting.jsx'
import Insights from './pages/Insights.jsx'
import Chat from './pages/Chat.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Reports from './pages/Reports.jsx'

const links = [
  { to: '/', label: 'Upload', end: true },
  { to: '/overview', label: 'Overview' },
  { to: '/cleaning', label: 'Cleaning' },
  { to: '/visualization', label: 'Visualization' },
  { to: '/forecasting', label: 'Forecasting' },
  { to: '/insights', label: 'Insights' },
  { to: '/chat', label: 'Chat' },
  { to: '/reports', label: 'Reports' },
]

function ProtectedRoute({ children }) {
  const location = useLocation()
  return localStorage.getItem('jwt')
    ? children
    : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

export default function App() {
  return (
    <DatasetProvider>
      <HashRouter>
        <div className="layout">
          <aside className="sidebar">
            <h1>AI Data Analyst</h1>
            <nav>
              {links.map(l => (
                <NavLink key={l.to} to={l.to} end={l.end} className={({isActive}) => isActive ? 'active' : ''}>
                  {l.label}
                </NavLink>
              ))}
            </nav>
          </aside>
          <main className="content">
            <Routes>
              <Route path="/" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/overview" element={<ProtectedRoute><Overview /></ProtectedRoute>} />
              <Route path="/cleaning" element={<ProtectedRoute><Cleaning /></ProtectedRoute>} />
              <Route path="/visualization" element={<ProtectedRoute><Visualization /></ProtectedRoute>} />
              <Route path="/forecasting" element={<ProtectedRoute><Forecasting /></ProtectedRoute>} />
              <Route path="/insights" element={<ProtectedRoute><Insights /></ProtectedRoute>} />
              <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
              <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
        </div>
      </HashRouter>
    </DatasetProvider>
  )
}
