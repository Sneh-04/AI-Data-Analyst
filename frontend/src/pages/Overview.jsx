import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import { datasetApi } from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

export default function Overview() {
  const { records, headers, datasetId } = useDataset()
  const [health, setHealth] = useState(null)
  const [scoreHistory, setScoreHistory] = useState([])
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
    setError(null)
    try {
      const result = await datasetApi.healthScore(datasetId, payload)
      setHealth(result)
      setScoreHistory(await datasetApi.healthScoreHistory(datasetId))
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (records.length === 0 || !datasetId) return
    if (useCustomWeights && Math.abs(Object.values(weights).reduce((sum, weight) => sum + weight, 0) - 1) >= 0.001) return
    const payload = { records }
    if (useCustomWeights) payload.weights = weights
    const timer = setTimeout(() => recomputeHealth(payload), 300)
    return () => clearTimeout(timer)
  }, [records, datasetId, useCustomWeights, weights])

  const handleWeightChange = (key, value) => {
    const parsed = parseFloat(value)
    const num = Number.isFinite(parsed) ? parsed : 0
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

  if (records.length === 0) return <EmptyState title="Start with a dataset" description="Upload a CSV to see its structure and assess data quality." />
  if (!datasetId) return <EmptyState title="Save your dataset to continue" description="Upload this dataset to the platform before assessing its health." />

  return (
    <div>
      <PageHeading eyebrow="DATA QUALITY" title="Overview & data quality"
        description="A clear snapshot of your dataset and its quality signals." />
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
          <div className="weight-settings">
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
            {weightError && <p className="alert alert-info" style={{ marginTop: 10 }}>{weightError}</p>}
            {!weightError && <p className="weight-valid">✓ Weights valid</p>}
          </div>
        )}
        {loading && <p className="loading-inline">Scoring...</p>}
        {error && <p className="alert alert-error" role="alert">{error} — is the Spring Boot backend running on :8080?</p>}
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
              <p className="alert alert-info" style={{ marginTop: 12 }}>
                Found {health.sentinel_missing_count} placeholder values (e.g. '-99', 'N/A', 'none') that may represent hidden missing data.
              </p>
            )}
            {health.score_trend && (
              <p className={`trend-note ${health.score_trend === 'declining' ? 'is-declining' : 'is-improving'}`}>
                Quality trend vs. the previous check ({health.previous_score}%): {health.score_trend}.
              </p>
            )}
            {health.mnar_signals?.length > 0 && (
              <ul className="issues" style={{ marginTop: 12 }}>
                {health.mnar_signals.map((signal, i) => <li key={i}>{signal}</li>)}
              </ul>
            )}
            <ul className="issues" style={{ marginTop: 16 }}>
              {(health.issues || []).map((issue, i) => <li key={i}>{issue}</li>)}
            </ul>
          </>
        )}
      </div>
      <div className="card">
        <h3>Health-score history</h3>
        {scoreHistory.length === 0 ? <p>No health assessments recorded yet.</p> : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Assessed</th><th>Score</th><th>Grade</th></tr></thead>
              <tbody>
                {scoreHistory.map(entry => (
                  <tr key={entry.id}>
                    <td>{new Date(entry.assessedAt).toLocaleString()}</td>
                    <td>{entry.score}%</td>
                    <td>{entry.grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
