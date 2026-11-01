import React from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'

export default function MyDatasets({ refreshKey }) {
  const { setDatasetId, setFileName, setHeaders, setRecords } = useDataset()
  const [datasets, setDatasets] = React.useState([])
  const [selectedDatasetId, setSelectedDatasetId] = React.useState(null)
  const [loadingDatasetId, setLoadingDatasetId] = React.useState(null)
  const [error, setError] = React.useState('')

  const restoreDataset = React.useCallback(async (dataset) => {
    setLoadingDatasetId(dataset.datasetId)
    setError('')
    try {
      const response = await api.get(`/datasets/${dataset.datasetId}/records`)
      const records = response.data
      setDatasetId(dataset.datasetId)
      setFileName(dataset.fileName)
      setRecords(records)
      setHeaders(records.length > 0 ? Object.keys(records[0]) : [])
      setSelectedDatasetId(dataset.datasetId)
      localStorage.setItem('selectedDatasetId', String(dataset.datasetId))
    } catch (requestError) {
      setError(requestError.response?.data?.message || 'Unable to load the selected dataset.')
    } finally {
      setLoadingDatasetId(null)
    }
  }, [setDatasetId, setFileName, setHeaders, setRecords])

  React.useEffect(() => {
    let active = true
    const loadDatasets = async () => {
      try {
        const response = await api.get('/datasets')
        if (!active) return
        const savedDatasets = response.data
        setDatasets(savedDatasets)
        if (savedDatasets.length === 0) {
          localStorage.removeItem('selectedDatasetId')
          return
        }
        const previousId = Number(localStorage.getItem('selectedDatasetId'))
        const selected = savedDatasets.find(dataset => dataset.datasetId === previousId) || savedDatasets[0]
        await restoreDataset(selected)
      } catch (requestError) {
        if (active) setError(requestError.response?.data?.message || 'Unable to load your saved datasets.')
      }
    }
    void loadDatasets()
    return () => { active = false }
  }, [refreshKey, restoreDataset])

  return (
    <div className="card">
      <h2>My datasets</h2>
      {datasets.length === 0
        ? <p>No saved datasets yet.</p>
        : <ul>
          {datasets.map(dataset => (
            <li key={dataset.datasetId}>
              <button type="button" onClick={() => restoreDataset(dataset)}
                disabled={loadingDatasetId !== null}
                aria-current={selectedDatasetId === dataset.datasetId ? 'true' : undefined}>
                {dataset.fileName} — {dataset.rowCount} rows, {dataset.columnCount} columns
                {loadingDatasetId === dataset.datasetId ? ' (Loading...)' : ''}
              </button>
            </li>
          ))}
        </ul>}
      {error && <p className="alert alert-error" role="alert">{error}</p>}
    </div>
  )
}
