import React from 'react'
import { HashRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import { DatasetProvider, useDataset } from './api/DatasetContext.jsx'
import LogoutControl from './components/LogoutControl.jsx'
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
import Inference from './pages/Inference.jsx'
import Research from './pages/Research.jsx'

const links = [
  { to: '/', label: 'Upload', end: true, icon: 'upload' },
  { to: '/overview', label: 'Overview', icon: 'overview' },
  { to: '/cleaning', label: 'Cleaning', icon: 'cleaning' },
  { to: '/inference', label: 'Inference', icon: 'inference' },
  { to: '/research', label: 'Research', icon: 'research' },
  { to: '/visualization', label: 'Visualization', icon: 'visualization' },
  { to: '/forecasting', label: 'Forecasting', icon: 'forecasting' },
  { to: '/insights', label: 'Insights', icon: 'insights' },
  { to: '/chat', label: 'Chat', icon: 'chat' },
  { to: '/reports', label: 'Reports', icon: 'reports' },
]

function NavIcon({ name }) {
  const paths = {
    upload: <><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M5 14v5h14v-5" /></>,
    overview: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.5" /></>,
    cleaning: <><path d="m4 20 9-9" /><path d="m12 4 8 8" /><path d="m14 2 8 8" /><path d="M3 21h7" /></>,
    inference: <><path d="M4 19V5" /><path d="M4 19h17" /><path d="M8 15v-3m5 3V8m5 7V5" /><path d="m7 9 5-4 5 2 4-4" /></>,
    research: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 5 5M10.8 7v7.6m-3.8-3.8h7.6" /></>,
    visualization: <><path d="M4 19V5" /><path d="M4 19h17" /><path d="m7 15 4-5 3 2 5-7" /></>,
    forecasting: <><path d="M3 17 9 11l4 4 8-9" /><path d="M15 6h6v6" /></>,
    insights: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" /><path d="m19 14 .9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14Z" /></>,
    chat: <><path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-6.5a7.5 7.5 0 1 1 17-3Z" /><path d="M8 11h.01M12 11h.01M16 11h.01" /></>,
    reports: <><path d="M6 3.5h8l4 4V20a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" /><path d="M14 4v4h4M8 12h8M8 16h8" /></>,
  }

  return (
    <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      {paths[name]}
    </svg>
  )
}

function ProtectedRoute({ children }) {
  const location = useLocation()
  return localStorage.getItem('jwt')
    ? children
    : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function Workspace() {
  const location = useLocation()
  const { fileName, datasetId } = useDataset()
  const isAuthRoute = ['/login', '/register'].includes(location.pathname)
  const currentPage = links.find(link => link.to === location.pathname)
  const title = currentPage?.label || (location.pathname === '/register' ? 'Create account' : 'Sign in')

  return (
    <div className={`layout${isAuthRoute ? ' auth-layout' : ''}`}>
      <aside className="sidebar">
        <NavLink className="brand" to="/" aria-label="AI Data Analyst home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none">
              <path d="M7 23V10l9 7 9-7v13" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="7" cy="8" r="2" fill="currentColor" />
              <circle cx="25" cy="8" r="2" fill="currentColor" />
              <circle cx="16" cy="17" r="2" fill="currentColor" />
            </svg>
          </span>
          <span className="brand-copy"><strong>AI Data Analyst</strong><small>DATA WORKSPACE</small></span>
        </NavLink>

        <p className="nav-caption">WORKSPACE</p>
        <nav className="primary-nav" aria-label="Main navigation">
          {links.map(link => (
            <NavLink key={link.to} to={link.to} end={link.end}
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <NavIcon name={link.icon} />
              <span>{link.label}</span>
            </NavLink>
          ))}
          {!isAuthRoute && <LogoutControl />}
        </nav>
        <div className="sidebar-note">
          <span className="sidebar-note-icon" aria-hidden="true">✦</span>
          <p>Turn your data into clearer decisions.</p>
        </div>
      </aside>

      <main className="content">
        {!isAuthRoute && (
          <header className="workspace-header">
            <div className="header-title">
              <span className="header-kicker">AI DATA ANALYST</span>
              <h1>{title}</h1>
            </div>
            <div className={`dataset-status${datasetId ? ' is-ready' : ''}`}>
              <span className="status-indicator" aria-hidden="true" />
              <span className="status-copy">
                <strong>{datasetId ? 'Dataset connected' : 'Workspace ready'}</strong>
                <small>{datasetId ? (fileName || `Dataset #${datasetId}`) : 'Upload a CSV to get started'}</small>
              </span>
            </div>
          </header>
        )}
        <div className="page-content">
          <Routes>
            <Route path="/" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
            <Route path="/overview" element={<ProtectedRoute><Overview /></ProtectedRoute>} />
            <Route path="/cleaning" element={<ProtectedRoute><Cleaning /></ProtectedRoute>} />
            <Route path="/inference" element={<ProtectedRoute><Inference /></ProtectedRoute>} />
            <Route path="/research" element={<ProtectedRoute><Research /></ProtectedRoute>} />
            <Route path="/visualization" element={<ProtectedRoute><Visualization /></ProtectedRoute>} />
            <Route path="/forecasting" element={<ProtectedRoute><Forecasting /></ProtectedRoute>} />
            <Route path="/insights" element={<ProtectedRoute><Insights /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
            <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <DatasetProvider>
      <HashRouter>
        <Workspace />
      </HashRouter>
    </DatasetProvider>
  )
}
