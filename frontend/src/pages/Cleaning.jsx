import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useDataset } from '../api/DatasetContext.jsx'
import api, { datasetApi } from '../api/client.js'
import EmptyState from '../components/EmptyState.jsx'
import PageHeading from '../components/PageHeading.jsx'

export default function Cleaning() {
  const { records, setRecords, datasetId } = useDataset()
  const [strategy, setStrategy] = useState('auto')
  const [outlierMethod, setOutlierMethod] = useState('iqr')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [versions, setVersions] = useState([])
  const [restoring, setRestoring] = useState(null)
  const [repairLog, setRepairLog] = useState([])
  const [repairTruncated, setRepairTruncated] = useState(false)

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

  if (records.length === 0) return <EmptyState title="Bring in data to clean" description="Upload a CSV dataset to explore missing values, duplicates, and repair options." />
  if (!datasetId) return <EmptyState title="Save your dataset to continue" description="Upload this dataset to the platform before cleaning it." />

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
      setRepairLog(result.repair_log || [])
      setRepairTruncated(Boolean(result.repair_log_truncated))
      await loadVersions()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeading eyebrow="PREPARE YOUR DATA" title="Cleaning studio"
        description="Choose a strategy, review the changes, and restore an earlier version whenever you need." />
      <div className="card control-panel cleaning-controls">
        <label>Missing value strategy: </label>
        <select value={strategy} onChange={e => setStrategy(e.target.value)} style={{ marginRight: 16 }}>
          <option value="auto">Auto (median / mode)</option>
          <option value="knn">KNN imputation</option>
          <option value="multiple">Multiple imputation (point fill only - not valid for inference)</option>
        </select>
        <p className="muted-copy cleaning-inference-link">
          For inferential intervals, use <Link to="/inference">Inference</Link>.
        </p>

        <label>Outlier handling: </label>
        <select value={outlierMethod} onChange={e => setOutlierMethod(e.target.value)}>
          <option value="iqr">IQR capping</option>
          <option value="isolation_forest">Isolation Forest</option>
          <option value="none">None</option>
        </select>

        <div style={{ marginTop: 16 }}>
          <button onClick={runCleaning} disabled={loading} data-loading={loading}>{loading ? 'Cleaning...' : 'Run cleaning'}</button>
        </div>
        {error && <p className="alert alert-error" role="alert">{error}</p>}
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

      {repairLog.length > 0 && (
        <div className="card">
          <h3>Repair log ({repairLog.length}{repairTruncated ? '+' : ''} automated changes)</h3>
          <p className="muted-copy">
            The cleaner records each repair. Multiple-imputation uncertainty is the spread across imputations,
            not a calibrated prediction interval.
          </p>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Row</th><th>Column</th><th>Method</th><th>New value</th><th>Uncertainty</th></tr></thead>
              <tbody>
                {repairLog.slice(0, 15).map((entry, i) => (
                  <tr key={i}>
                    <td>{entry.row_index}</td>
                    <td>{entry.column ?? (entry.columns_affected || []).join(', ')}</td>
                    <td>{entry.strategy_used === 'multiple_imputation'
                      ? 'Point fill only - not valid for inference'
                      : entry.strategy_used ?? entry.reason}</td>
                    <td>{entry.imputed_value ?? entry.capped_value ?? '—'}</td>
                    <td>{entry.imputation_uncertainty != null ? `± ${entry.imputation_uncertainty}` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {(repairLog.length > 15 || repairTruncated) && <p className="muted-copy">Showing the first 15 entries.</p>}
        </div>
      )}

      <div className="card">
        <h3>Version history</h3>
        {!datasetId && <p>Upload this dataset to the platform to enable version history.</p>}
        {datasetId && versions.length === 0 && <p>No cleaning versions yet.</p>}
        {versions.map(version => (
          <div key={version.versionNumber} className="version-row">
            <div>
              <strong>Version {version.versionNumber}</strong>
              <div className="muted-copy">{version.operation} · {new Date(version.createdAt).toLocaleString()}</div>
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
            }} disabled={restoring !== null} data-loading={restoring === version.versionNumber}>
              {restoring === version.versionNumber ? 'Restoring...' : 'Restore'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
