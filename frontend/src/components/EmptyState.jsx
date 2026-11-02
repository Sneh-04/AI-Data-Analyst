import React from 'react'
import { Link } from 'react-router-dom'

export default function EmptyState({ title, description }) {
  return (
    <section className="empty-state">
      <span className="empty-state-icon" aria-hidden="true">
        <svg viewBox="0 0 48 48" fill="none">
          <path d="M8 11.5A3.5 3.5 0 0 1 11.5 8h17L40 19.5v17a3.5 3.5 0 0 1-3.5 3.5h-25A3.5 3.5 0 0 1 8 36.5v-25Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
          <path d="M28 8v12h12M16 28h16M16 34h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <p className="eyebrow">YOUR WORKSPACE</p>
      <h2>{title}</h2>
      <p>{description}</p>
      <Link className="button-link" to="/">Upload a dataset <span aria-hidden="true">→</span></Link>
    </section>
  )
}
