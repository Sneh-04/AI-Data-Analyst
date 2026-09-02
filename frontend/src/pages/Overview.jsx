import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'

export default function Overview() {
  const { records, headers, datasetId } = useDataset()
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [useCustomWeights, setUseCustomWeights] = useState(false)
  const [weights, setWeights] = useState({
    completeness: 0.35,
    uniqueness: 0.25,
    consistency: 0.20,
    outliers: 0.20,
  })
  const [weightError, setWeightError] = useState(null)

  const recomputeHealth = async (payload) => {
    setLoading(true)
    datasetApi.healthScore(datasetId, payload)
      .then(setHealth)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (records.length === 0) return
    const payload = { records }
    if (useCustomWeights) payload.weights = weights
    recomputeHealth(payload)
  }, [records, useCustomWeights, weights])

  const handleWeightChange = (key, value) => {
    const num = parseFloat(value) || 0
    const newWeights = { ...weights, [key]: num }
    setWeights(newWeights)
    const sum = Object.values(newWeights).reduce((a, b) => a + b, 0)
    if (Math.abs(sum - 1.0) < 0.001) {
      setWeightError(null)
    } else {
      setWeightError(`Weights sum to ${sum.toFixed(3)}, must equal 1.0`)
    }
  }

  const toggleCustomWeights = () => {
    setWeightError(null)
    setUseCustomWeights(!useCustomWeights)
  }

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
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input type="checkbox" checked={useCustomWeights} onChange={toggleCustomWeights} />
            Use custom weights
          </label>
        </div>
        {useCustomWeights && (
          <div style={{ background: '#1d2130', padding: 14, borderRadius: 6, marginBottom: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
              <div>
                <label>Completeness</label>
                <input type="number" min="0" max="1" step="0.01" value={weights.completeness}
                  onChange={e => handleWeightChange('completeness', e.target.value)}
                  style={{ width: '100%', marginTop: 4 }} />
              </div>
              <div>
                <label>Uniqueness</label>
                <input type="number" min="0" max="1" step="0.01" value={weights.uniqueness}
                  onChange={e => handleWeightChange('uniqueness', e.target.value)}
                  style={{ width: '100%', marginTop: 4 }} />
              </div>
              <div>
                <label>Consistency</label>
                <input type="number" min="0" max="1" step="0.01" value={weights.consistency}
                  onChange={e => handleWeightChange('consistency', e.target.value)}
                  style={{ width: '100%', marginTop: 4 }} />
              </div>
              <div>
                <label>Outliers</label>
                <input type="number" min="0" max="1" step="0.01" value={weights.outliers}
                  onChange={e => handleWeightChange('outliers', e.target.value)}
                  style={{ width: '100%', marginTop: 4 }} />
              </div>
            </div>
            {weightError && <p style={{ color: '#d4a04f', marginTop: 8, fontSize: 12 }}>{weightError}</p>}
            {!weightError && <p style={{ color: '#52b788', marginTop: 8, fontSize: 12 }}>✓ Weights valid</p>}
          </div>
        )}
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
            {health.sentinel_missing_count > 0 && (
              <p style={{ background: '#1d2130', padding: 10, borderRadius: 6, marginTop: 12, fontSize: 12, color: '#d4a04f' }}>
                Found {health.sentinel_missing_count} placeholder values (e.g. '-99', 'N/A', 'none') that may represent hidden missing data.
              </p>
            )}
            <ul className="issues" style={{ marginTop: 16 }}>
              {health.issues.map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          </>
        )}
      </div>
    </div>
  )
}
