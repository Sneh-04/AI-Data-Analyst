import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api/auth.js'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ fullName: '', email: '', password: '' })
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
      await register(form)
      navigate('/', { replace: true })
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to create the account.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <div className="auth-brand"><span className="brand-mark" aria-hidden="true">A</span><strong>AI Data Analyst</strong></div>
        <h2>Create account</h2>
        <p className="auth-subtitle">Create your account and bring your data into focus.</p>
        <form onSubmit={submit}>
          <label>Full name<input name="fullName" value={form.fullName} onChange={updateField} /></label>
          <label>Email<input name="email" type="email" value={form.email} onChange={updateField} required /></label>
          <label>Password<input name="password" type="password" minLength="8" value={form.password} onChange={updateField} required /></label>
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button type="submit" disabled={submitting} data-loading={submitting}>{submitting ? 'Creating account...' : 'Create account'}</button>
        </form>
        <p>Already have an account? <Link to="/login">Sign in</Link></p>
      </div>
    </div>
  )
}
