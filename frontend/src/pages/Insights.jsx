import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

export default function Insights() {
  const { records, datasetId } = useDataset()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (records.length === 0) return <EmptyState title="Find the story in your data" description="Upload a dataset to generate anomaly, trend, and correlation insights." />
  if (!datasetId) return <EmptyState title="Save your dataset to continue" description="Upload this dataset to the platform before generating insights." />

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await datasetApi.insights(datasetId, { records, use_llm: false })
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeading eyebrow="DISCOVER WHAT MATTERS" title="AI insights"
        description="Surface noteworthy patterns and signals across your uploaded dataset." />
      <div className="card">
        <button onClick={run} disabled={loading} data-loading={loading}>{loading ? 'Analyzing...' : 'Generate insights'}</button>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
      </div>

      {result && (
        <div className="insights-grid">
          <div className="card insight-card">
            <span className="insight-icon anomaly-icon" aria-hidden="true">!</span>
            <h3>Anomalies</h3>
            <ul className="insight-list">{result.insights.anomalies.length ? result.insights.anomalies.map((a,i) => <li key={i}>{a}</li>) : <li>None detected.</li>}</ul>
          </div>
          <div className="card insight-card">
            <span className="insight-icon trend-icon" aria-hidden="true">↗</span>
            <h3>Trends</h3>
            <ul className="insight-list">{result.insights.trends.length ? result.insights.trends.map((t,i) => <li key={i}>{t}</li>) : <li>None detected.</li>}</ul>
          </div>
          <div className="card insight-card">
            <span className="insight-icon correlation-icon" aria-hidden="true">⌁</span>
            <h3>Correlations</h3>
            <ul className="insight-list">{result.insights.correlations.length ? result.insights.correlations.map((c,i) => <li key={i}>{c}</li>) : <li>None strong enough to flag.</li>}</ul>
          </div>
        </div>
      )}
    </div>
  )
}
