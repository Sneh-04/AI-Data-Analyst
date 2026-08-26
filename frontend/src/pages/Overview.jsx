import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'

export default function Overview() {
  const { records, headers, datasetId } = useDataset()
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (records.length === 0) return
    setLoading(true)
    datasetApi.healthScore(datasetId, { records })
      .then(setHealth)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [records])

  if (records.length === 0) return <p>Upload a dataset first.</p>

  return (
    <div>
      <h2>Overview & data quality</h2>
      <div className="card">
        <div className="grid">
          <div className="metric"><div className="value">{records.length}</div><div className="label">Rows</div></div>
          <div className="metric"><div className="value">{headers.length}</div><div className="label">Columns</div></div>
        </div>
      </div>

      <div className="card">
        <h3>Health score</h3>
        {loading && <p>Scoring...</p>}
        {error && <p style={{ color: '#e06c75' }}>{error} — is the Spring Boot backend running on :8080?</p>}
        {health && (
          <>
            <div className="grid">
              <div className="metric"><div className="value">{health.score}%</div><div className="label">{health.grade}</div></div>
              <div className="metric"><div className="value">{health.completeness}%</div><div className="label">Completeness</div></div>
              <div className="metric"><div className="value">{health.uniqueness}%</div><div className="label">Uniqueness</div></div>
              <div className="metric"><div className="value">{health.consistency}%</div><div className="label">Consistency</div></div>
              <div className="metric"><div className="value">{health.outliers_score}%</div><div className="label">Outlier score</div></div>
            </div>
            <ul className="issues" style={{ marginTop: 16 }}>
              {health.issues.map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          </>
        )}
      </div>
    </div>
  )
}
