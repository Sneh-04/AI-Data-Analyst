import React, { useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'

export default function Insights() {
  const { records, datasetId } = useDataset()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (records.length === 0) return <p>Upload a dataset first.</p>

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
      <h2>AI insights</h2>
      <div className="card">
        <button onClick={run} disabled={loading}>{loading ? 'Analyzing...' : 'Generate insights'}</button>
        {error && <p style={{ color: '#e06c75' }}>{error}</p>}
      </div>

      {result && (
        <div className="card">
          <h3>Anomalies</h3>
          <ul>{result.insights.anomalies.length ? result.insights.anomalies.map((a,i) => <li key={i}>{a}</li>) : <li>None detected.</li>}</ul>
          <h3>Trends</h3>
          <ul>{result.insights.trends.length ? result.insights.trends.map((t,i) => <li key={i}>{t}</li>) : <li>None detected.</li>}</ul>
          <h3>Correlations</h3>
          <ul>{result.insights.correlations.length ? result.insights.correlations.map((c,i) => <li key={i}>{c}</li>) : <li>None strong enough to flag.</li>}</ul>
        </div>
      )}
    </div>
  )
}
