import React from 'react'
import { useDataset } from '../api/DatasetContext.jsx'
import api from '../api/client.js'

export default function MyDatasets({ refreshKey }) {
  const { setDatasetId, setFileName, setHeaders, setRecords } = useDataset()
  const [datasets, setDatasets] = React.useState([])
  const [selectedDatasetId, setSelectedDatasetId] = React.useState(null)
  const [loadingDatasetId, setLoadingDatasetId] = React.useState(null)
  const [deletingDatasetId, setDeletingDatasetId] = React.useState(null)
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

  const deleteDataset = async (dataset) => {
    const confirmed = window.confirm(
      `Permanently delete "${dataset.fileName}" and its generated versions and reports? ` +
      'Copies in infrastructure backups may remain until those backups expire.'
    )
    if (!confirmed) return

    setDeletingDatasetId(dataset.datasetId)
    setError('')
    try {
      await api.delete(`/datasets/${dataset.datasetId}`)
      setDatasets(current => current.filter(item => item.datasetId !== dataset.datasetId))
      if (selectedDatasetId === dataset.datasetId) {
        setDatasetId(null)
        setFileName(null)
        setHeaders([])
        setRecords([])
        setSelectedDatasetId(null)
        localStorage.removeItem('selectedDatasetId')
      }
    } catch (requestError) {
      let deleteError = requestError.response?.data?.detail
        || requestError.response?.data?.message
        || 'Dataset deletion is incomplete. Retry the delete action to continue.'
      try {
        const response = await api.get('/datasets')
        setDatasets(response.data)
        const deletedDataset = response.data.find(item => item.datasetId === dataset.datasetId)
        if (deletedDataset?.deletionStatus === 'DELETING' && selectedDatasetId === dataset.datasetId) {
          setDatasetId(null)
          setFileName(null)
          setHeaders([])
          setRecords([])
          setSelectedDatasetId(null)
          localStorage.removeItem('selectedDatasetId')
        }
      } catch (refreshError) {
        const refreshMessage = refreshError.response?.data?.detail
          || refreshError.response?.data?.message
          || 'the status refresh request failed'
        deleteError = `${deleteError} The deletion status could not be refreshed (${refreshMessage}); retry the delete action.`
      }
      setError(deleteError)
    } finally {
      setDeletingDatasetId(null)
    }
  }

  React.useEffect(() => {
    let active = true
    const loadDatasets = async () => {
      try {
        const response = await api.get('/datasets')
        if (!active) return
        const savedDatasets = response.data
        setDatasets(savedDatasets)
        const availableDatasets = savedDatasets.filter(dataset => dataset.deletionStatus !== 'DELETING')
        if (availableDatasets.length === 0) {
          localStorage.removeItem('selectedDatasetId')
          setDatasetId(null)
          setFileName(null)
          setHeaders([])
          setRecords([])
          setSelectedDatasetId(null)
          return
        }
        const previousId = Number(localStorage.getItem('selectedDatasetId'))
        const selected = availableDatasets.find(dataset => dataset.datasetId === previousId) || availableDatasets[0]
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
            <li className="dataset-list-item" key={dataset.datasetId}>
              {dataset.deletionStatus === 'DELETING'
                ? <span>{dataset.fileName} — Deletion pending; retry to continue</span>
                : <button type="button" onClick={() => restoreDataset(dataset)}
                  disabled={loadingDatasetId !== null || deletingDatasetId !== null}
                  aria-current={selectedDatasetId === dataset.datasetId ? 'true' : undefined}>
                  {dataset.fileName} — {dataset.rowCount} rows, {dataset.columnCount} columns
                  {loadingDatasetId === dataset.datasetId ? ' (Loading...)' : ''}
                </button>}
              <button type="button" className="dataset-delete"
                onClick={() => deleteDataset(dataset)}
                disabled={loadingDatasetId !== null || deletingDatasetId !== null}
                aria-label={`Delete ${dataset.fileName}`}>
                {deletingDatasetId === dataset.datasetId
                  ? 'Deleting...'
                  : dataset.deletionStatus === 'DELETING' ? 'Retry deletion' : 'Delete'}
              </button>
            </li>
          ))}
        </ul>}
      {error && <p className="alert alert-error" role="alert">{error}</p>}
    </div>
  )
}
