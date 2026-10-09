import React, { useEffect, useState } from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import api, { datasetApi } from '../api/client.js'

export default function Cleaning() {
  const { records, setRecords, datasetId } = useDataset()
  const [strategy, setStrategy] = useState('auto')
  const [outlierMethod, setOutlierMethod] = useState('iqr')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [versions, setVersions] = useState([])
  const [restoring, setRestoring] = useState(null)

  const loadVersions = async () => {
    if (!datasetId) return
    try {
      const result = await api.get(`/datasets/${datasetId}/versions`)
      setVersions(result.data)
    } catch (e) {
      setError(e.message)
    }
  }

  useEffect(() => {
    loadVersions()
  }, [datasetId])

  if (records.length === 0) return <p>Upload a dataset first.</p>

  const runCleaning = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await datasetApi.clean(datasetId, {
        records,
        strategy,
        remove_duplicates: true,
        outlier_method: outlierMethod,
      })
      setRecords(result.cleaned_records)
      setSummary(result.summary)
      await loadVersions()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Cleaning studio</h2>
      <div className="card">
        <label>Missing value strategy: </label>
        <select value={strategy} onChange={e => setStrategy(e.target.value)} style={{ marginRight: 16 }}>
          <option value="auto">Auto (median / mode)</option>
          <option value="knn">KNN imputation</option>
          <option value="multiple">Iterative Bayesian imputation (experimental)</option>
        </select>

        <label>Outlier handling: </label>
        <select value={outlierMethod} onChange={e => setOutlierMethod(e.target.value)}>
          <option value="iqr">IQR capping</option>
          <option value="isolation_forest">Isolation Forest</option>
          <option value="none">None</option>
        </select>

        <div style={{ marginTop: 16 }}>
          <button onClick={runCleaning} disabled={loading}>{loading ? 'Cleaning...' : 'Run cleaning'}</button>
        </div>
        {error && <p style={{ color: '#e06c75' }}>{error}</p>}
      </div>

      {summary && (
        <div className="card">
          <h3>Cleaning summary</h3>
          <div className="grid">
            <div className="metric"><div className="value">{summary.rows_removed}</div><div className="label">Duplicate rows removed</div></div>
            <div className="metric"><div className="value">{summary.nulls_fixed}</div><div className="label">Nulls fixed</div></div>
            <div className="metric"><div className="value">{summary.cleaned_rows}</div><div className="label">Rows remaining</div></div>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Version history</h3>
        {!datasetId && <p>Upload this dataset to the platform to enable version history.</p>}
        {datasetId && versions.length === 0 && <p>No cleaning versions yet.</p>}
        {versions.map(version => (
          <div key={version.versionNumber} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #262b3a' }}>
            <div>
              <strong>Version {version.versionNumber}</strong>
              <div style={{ color: '#a9adba', fontSize: 12 }}>{version.operation} · {new Date(version.createdAt).toLocaleString()}</div>
            </div>
            <button onClick={async () => {
              setRestoring(version.versionNumber)
              setError(null)
              try {
                const result = await api.post(`/datasets/${datasetId}/versions/${version.versionNumber}/restore`)
                setRecords(result.data.records)
                setSummary(null)
              } catch (e) {
                setError(e.message)
              } finally {
                setRestoring(null)
              }
            }} disabled={restoring !== null}>
              {restoring === version.versionNumber ? 'Restoring...' : 'Restore'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
