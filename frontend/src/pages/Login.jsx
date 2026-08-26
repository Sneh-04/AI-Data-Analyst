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
        <h2>Sign in</h2>
        <form onSubmit={submit}>
          <label>Email<input name="email" type="email" value={form.email} onChange={updateField} required /></label>
          <label>Password<input name="password" type="password" value={form.password} onChange={updateField} required /></label>
          {error && <p className="auth-error">{error}</p>}
          <button type="submit" disabled={submitting}>{submitting ? 'Signing in...' : 'Sign in'}</button>
        </form>
        <p>New to AI Data Analyst? <Link to="/register">Create an account</Link></p>
      </div>
    </div>
  )
}
