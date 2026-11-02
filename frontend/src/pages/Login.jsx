import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { login } from '../api/auth.js'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const updateField = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(form)
      navigate(location.state?.from || '/', { replace: true })
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to sign in with those details.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <div className="auth-brand"><span className="brand-mark" aria-hidden="true">A</span><strong>AI Data Analyst</strong></div>
        <h2>Sign in</h2>
        <p className="auth-subtitle">Welcome back. Sign in to continue to your data workspace.</p>
        <form onSubmit={submit}>
          <label>Email<input name="email" type="email" value={form.email} onChange={updateField} required /></label>
          <label>Password<input name="password" type="password" value={form.password} onChange={updateField} required /></label>
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button type="submit" disabled={submitting} data-loading={submitting}>{submitting ? 'Signing in...' : 'Sign in'}</button>
        </form>
        <p>New to AI Data Analyst? <Link to="/register">Create an account</Link></p>
      </div>
    </div>
  )
}
